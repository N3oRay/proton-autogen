#loader.py
import os
import json
import hashlib
import re
import sys
import shutil
import subprocess
import uuid
import time
from pathlib import Path
from shutil import which
import configparser

from proton_autogen.config import VERSION, CONFIG_FILE, CONFIG_DIR

def normalize_game_config(config: dict):
    return {
        **config,
        "favorite": config.get("favorite", False),
        "playtime": {
            "seconds": config.get("playtime", {}).get("seconds", 0),
            "launch_count": config.get("playtime", {}).get("launch_count", 0),
            "last_session": config.get("playtime", {}).get("last_session", 0),
            "last_launch": config.get("playtime", {}).get("last_launch", None),
        }
    }

def _game_id(exe_path: str):
    return hashlib.md5(os.path.abspath(exe_path).encode()).hexdigest()


def get_game_config_path(exe_path: str):
    gid = _game_id(exe_path)
    return os.path.join(CONFIG_DIR, f"{gid}.json"), gid

# -- Save game for UX
def deep_merge(base: dict, updates: dict):
    for k, v in updates.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            deep_merge(base[k], v)
        else:
            base[k] = v
    return base

def load_game_config(exe_path):
    game_id = _game_id(exe_path)
    path = os.path.expanduser(f"~/.config/proton-autogen/games/{game_id}.json")

    if os.path.exists(path):
        with open(path, "r") as f:
            config = json.load(f)

        return normalize_game_config(config)

    return None


def save_game_config(data: dict):
    exe_path = data.get("path")
    if not exe_path:
        raise ValueError("Missing path in data")

    config_path, gid = get_game_config_path(exe_path)

    # load existing config
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            base = json.load(f)
    else:
        base = {}

    # ensure id always stable
    base["id"] = gid

    # merge safely
    merged = deep_merge(base, data)

    # IMPORTANT: ensure required fields exist
    merged.setdefault("features", {})
    merged.setdefault("prefix", {"name": "main", "path": ""})
    merged.setdefault("env", {})
    # ADD STATS AND FAV
    merged = normalize_game_config(merged)

    with open(config_path, "w") as f:
        json.dump(merged, f, indent=2)

    return merged

def save_game_config_v1(data: dict):
    if not isinstance(data, dict):
        return

    exe_path = data.get("path")
    if not exe_path:
        return

    config_path, gid = get_game_config_path(exe_path)

    data["id"] = gid

    os.makedirs(CONFIG_DIR, exist_ok=True)

    with open(config_path, "w") as f:
        json.dump(data, f, indent=2)

    print("[proton-autogen] Saved:", config_path)
