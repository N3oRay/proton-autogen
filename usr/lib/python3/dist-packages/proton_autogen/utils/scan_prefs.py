#!/usr/bin/env python3
# utils/scan_prefs.py
"""
Préférence « scan automatique des nouvelles applications » — SANS GTK.

[ui] scan_options = true|false   (proton-autogen-ux.conf, true par défaut)

  true  : au chargement, proton-autogen parcourt ~/Bureau, ~/Downloads, ~/Jeux et
          ~/Téléchargements à la recherche de nouveaux .exe (comportement historique)
  false : seules les applications déjà enregistrées sont chargées (démarrage plus
          rapide : aucune arborescence n'est parcourue)

Ce module vit dans utils/ (et non dans ux/) parce que la couche métier
(backend.find_windows_programs_ux) le consulte : elle ne doit jamais importer ux/.
Il n'importe volontairement PAS ux.themes, dont l'import crée / migre le fichier
de configuration de l'interface (effet de bord indésirable pour la CLI et les tests).
ux/settings_scan.py le ré-exporte pour les anciens imports.
"""

import configparser
from pathlib import Path

# Même fichier que ux.themes.CONFIG_PATH (un test vérifie que les deux restent égaux).
CONFIG_PATH = Path.home() / ".config" / "proton-autogen" / "proton-autogen-ux.conf"


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
