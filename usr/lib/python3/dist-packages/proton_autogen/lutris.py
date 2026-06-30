from __future__ import annotations

import os
import copy
import yaml
import logging
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

from proton_autogen.lutris_validate import validate_lutris_export, LutrisValidationError
# ============================================================
# Utils
# ============================================================

from pathlib import Path
import os


def resolve_game_path(exe_path: str, base_dir: str | None = None) -> str:
    """
    Resolve exe path for Lutris export.

    Strategy:
    1. absolute path -> keep
    2. relative path -> resolve against base_dir
    3. fallback -> search in base_dir recursively
    """

    if not exe_path:
        return ""

    p = Path(exe_path)

    # -------------------------
    # 1. Already absolute
    # -------------------------
    if p.is_absolute() and p.exists():
        return str(p)

    # -------------------------
    # 2. Relative path resolution
    # -------------------------
    if base_dir:
        candidate = Path(base_dir) / exe_path
        if candidate.exists():
            return str(candidate.resolve())

    # -------------------------
    # 3. Try current working dir
    # -------------------------
    cwd_candidate = Path.cwd() / exe_path
    if cwd_candidate.exists():
        return str(cwd_candidate.resolve())

    # -------------------------
    # 4. Deep search fallback (safe, limited depth)
    # -------------------------
    if base_dir and Path(base_dir).exists():
        base = Path(base_dir)

        for p in base.rglob(exe_path):
            if p.is_file():
                return str(p.resolve())

    # -------------------------
    # 5. Last fallback (return original)
    # -------------------------
    return str(p)

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
    game_config = copy.deepcopy(game_config)

    name = game_config.get("name", "Unknown Game")

    # 🔥 SAFE SLUG (TOUJOURS DÉFINI)
    slug = game_config.get("id") or name
    slug = slug.lower().strip()
    slug = slug.replace(" ", "-").replace(".exe", "")

    exe_path = game_config.get("path") or ""

    # 🔥 AUTO-FIX CONTEXT
    base_dir = os.path.dirname(exe_path) if exe_path else None
    fixed_exe = resolve_game_path(exe_path, base_dir)

    workdir, exe = _split_exe_path(fixed_exe)

    prefix = _ensure_dict(game_config.get("prefix"))
    env = _ensure_dict(game_config.get("env"))

    lutris_data = {
        # 🔥 IMPORTANT: runner ici uniquement
        "runner": "wine",
        "name": name,
        "game_slug": slug,
        "slug": slug,
        "version": "proton-autogen-1",

        "script": {
            "game": {
                "exe": exe_path,  # ⚠️ FULL PATH (plus robuste)
                "working_dir": workdir,
                "prefix": prefix.get("path", "$GAMEDIR"),
            },

            "env": env,

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
    data = yaml.safe_load(yaml_text)

    if not isinstance(data, dict):
        raise ValueError("Invalid YAML root")

    script = data.get("script", {})
    game = script.get("game", {})

    name = data.get("name", "Imported Game")

    exe = game.get("exe")
    workdir = game.get("working_dir")

    env = _ensure_dict(script.get("env"))
    prefix = game.get("prefix")

    exe_path = os.path.join(workdir, exe) if exe and workdir else None

    return {
        "id": data.get("game_slug"),
        "name": name,
        "path": exe_path,

        "prefix": {
            "path": prefix
        },

        "env": {
            k: v for k, v in env.items()
        },

        "features": {
            "mangohud": env.get("MANGOHUD") == "1",
            "gamemode": env.get("GAMEMODE") == "1",
        },

        "meta": {
            "imported_from": "lutris"
        }
    }


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
