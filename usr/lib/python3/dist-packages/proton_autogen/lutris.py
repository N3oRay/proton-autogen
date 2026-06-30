from __future__ import annotations

import os
import copy
import yaml
import logging
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)


# ============================================================
# Utils
# ============================================================

def _split_exe_path(exe_path: str) -> Tuple[str, str]:
    """
    Split absolute exe path into (workdir, exe_name)
    """
    if not exe_path:
        return "", ""

    workdir = os.path.dirname(exe_path)
    exe = os.path.basename(exe_path)
    return workdir, exe


def _safe_get(d: Dict[str, Any], path: str, default=None):
    """
    Safe nested getter: "a.b.c"
    """
    keys = path.split(".")
    cur = d
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur


def _ensure_dict(value):
    return value if isinstance(value, dict) else {}


# ============================================================
# EXPORT: Proton-autogen -> Lutris YAML
# ============================================================

def export_game_to_lutris_yaml(game_config: Dict[str, Any]) -> str:
    import copy
    import yaml

    game_config = copy.deepcopy(game_config)

    name = game_config.get("name", "Unknown Game")

    # slug = Lutris "safe identifier"
    slug = (game_config.get("id") or name).lower().replace(" ", "-")
    game_slug = slug

    exe_path = game_config.get("path") or ""

    prefix = _ensure_dict(game_config.get("prefix"))

    workdir, exe = _split_exe_path(exe_path)

    lutris_data = {
        # 🔥 REQUIRED ROOT FIELDS
        "name": name,
        "slug": slug,
        "game_slug": game_slug,
        "version": "proton-autogen-1",
        "runner": "wine",

        # 🔥 SCRIPT BLOCK
        "script": {
            "game": {
                "exe": f"{workdir}/{exe}" if exe else "",
                "working_dir": workdir,
                "prefix": prefix.get("path") or "$GAMEDIR",
            },

            "installer": [
                {
                    "task": {
                        "name": "wineexec",
                        "executable": exe
                    }
                }
            ]
        }
    }

    def prune(o):
        if isinstance(o, dict):
            return {k: prune(v) for k, v in o.items() if v is not None}
        if isinstance(o, list):
            return [prune(v) for v in o if v is not None]
        return o

    return yaml.safe_dump(prune(lutris_data), sort_keys=False, allow_unicode=True)


# ============================================================
# IMPORT: Lutris YAML -> Proton-autogen config
# ============================================================

def import_lutris_yaml_to_game_config(yaml_text: str) -> Dict[str, Any]:
    """
    Convert Lutris YAML -> proton-autogen game config (best-effort reversible mapping)
    """

    try:
        data = yaml.safe_load(yaml_text)
    except Exception as e:
        raise ValueError(f"Invalid YAML: {e}")

    if not isinstance(data, dict):
        raise ValueError("YAML root must be a dict")

    game = data.get("game", {})

    name = game.get("name", "Imported Game")
    game_id = game.get("id")

    exe = game.get("exe")
    workdir = game.get("workdir")

    wine = _ensure_dict(game.get("wine"))
    env = _ensure_dict(game.get("env"))
    meta = _ensure_dict(game.get("meta"))

    prefix_path = wine.get("prefix")

    # ----------------------------
    # Reverse feature mapping
    # ----------------------------
    features = {
        "mangohud": env.get("MANGOHUD") == "1",
        "gamemode": env.get("GAMEMODE") == "1",
    }

    # sync inference
    sync = {
        "esync": "auto" if env.get("WINEESYNC") == "1" else "off",
        "fsync": "auto" if env.get("WINEFSYNC") == "1" else "off",
    }

    # reconstruct exe path (best effort)
    if exe and workdir:
        exe_path = os.path.join(workdir, exe)
    else:
        exe_path = None

    proton_path = meta.get("proton_path")

    game_config = {
        "id": game_id,
        "name": name,
        "path": exe_path,
        "proton": proton_path,
        "prefix": {
            "name": None,
            "path": prefix_path,
        },
        "features": features,
        "env": {
            k: v for k, v in env.items()
            if k not in {"MANGOHUD", "MANGOHUD_DLSYM", "GAMEMODE"}
        },
        "sync": sync,
        "meta": {
            "imported_from": "lutris",
            "raw_meta": meta,
        },
    }

    # mark missing exe explicitly (important UX behavior)
    if not exe_path:
        logger.warning("Executable path missing or incomplete in YAML import")

    return game_config


# ============================================================
# Validation helpers
# ============================================================

def validate_game_config(game_config: Dict[str, Any]) -> None:
    """
    Minimal validation for proton-autogen schema stability
    """
    if not isinstance(game_config, dict):
        raise ValueError("game_config must be dict")

    if not game_config.get("name"):
        raise ValueError("Missing required field: name")

    env = game_config.get("env", {})
    if not isinstance(env, dict):
        raise ValueError("env must be a dict")

    prefix = game_config.get("prefix", {})
    if prefix and not isinstance(prefix, dict):
        raise ValueError("prefix must be a dict if present")
