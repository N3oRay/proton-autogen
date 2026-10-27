#!/usr/bin/env python3
# ux/settings_scan.py
"""Compatibilité : la préférence de scan vit désormais dans
proton_autogen.utils.scan_prefs (sans GTK, importable par la couche métier).
Ce relais ré-exporte les mêmes objets sous les mêmes noms."""

from proton_autogen.utils.scan_prefs import (  # noqa: F401
    CONFIG_PATH,
    load_scan_options,
    save_scan_options,
)
