#!/usr/bin/env python3
# ux/settings_scan.py

import configparser
import re
from typing import Iterable, List

from proton_autogen.ux.themes import CONFIG_PATH

# ---------------------------------------------------------------------------
# Préférence [ui] scan_options (proton-autogen-ux.conf)
# ---------------------------------------------------------------------------

def load_scan_options(default: bool = True) -> bool:
    cfg = configparser.ConfigParser()

    if not CONFIG_PATH.exists():
        return default

    try:
        cfg.read(CONFIG_PATH)
        return cfg.getboolean("ui", "scan_options", fallback=default)
    except Exception:
        return default


def save_scan_options(enabled: bool) -> None:
    cfg = configparser.ConfigParser()

    if CONFIG_PATH.exists():
        try:
            cfg.read(CONFIG_PATH)
        except Exception:
            pass

    if "ui" not in cfg:
        cfg["ui"] = {}

    cfg["ui"]["scan_options"] = "true" if enabled else "false"

    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        cfg.write(f)
