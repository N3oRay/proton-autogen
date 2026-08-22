#core.py proton-autogen
import os
import re
import shutil
import configparser
from pathlib import Path

from proton_autogen.detection.proton import DEFAULT_PROTON_PATHS


VERSION = "3.3.0"

CONFIG_FILE = os.path.expanduser("~/.config/proton-autogen/proton-autogen.conf")
CONFIG_DIR = os.path.expanduser("~/.config/proton-autogen/games")

PREFIX_DIR = "~/Documents/Proton/env"
PREFIX_DIR_PATH = os.path.expanduser(PREFIX_DIR)

# Old location (before consolidation under ~/.config/proton-autogen/).
# Retained solely for the automatic migration below.

# Ancien emplacement (avant regroupement sous ~/.config/proton-autogen/).
# Conservé uniquement pour la migration automatique ci-dessous.
_LEGACY_CONFIG_FILE = os.path.expanduser("~/.config/proton-autogen.conf")


# Moves the old ~/.config/proton-autogen.conf to the new
# location ~/.config/proton-autogen/proton-autogen.conf—once only—
# without ever overwriting a file already present at the new location.
# Silent failure: must never prevent the app from starting.
def _migrate_legacy_config():
    """Déplace l'ancien ~/.config/proton-autogen.conf vers le nouvel
    emplacement ~/.config/proton-autogen/proton-autogen.conf, une seule
    fois, sans jamais écraser un fichier déjà présent au nouvel endroit.
    Échec silencieux : ne doit jamais empêcher le démarrage de l'appli."""
    if os.path.isfile(CONFIG_FILE):
        return  # déjà migré, ou déjà (re)créé au nouvel emplacement

    if not os.path.isfile(_LEGACY_CONFIG_FILE):
        return  # rien à migrer (nouvelle installation)

    try:
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        shutil.move(_LEGACY_CONFIG_FILE, CONFIG_FILE)
    except Exception:
        pass


_migrate_legacy_config()


def load_proton_paths():
    def create_default_config():
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)

        sample = """[proton]
# Flatpak Steam in ~/.config/proton-autogen.conf by default
# Add custom Proton locations here
# You can separate paths with newlines, ":" or ";"
paths = ~/.var/app/com.valvesoftware.Steam/.local/share/Steam/compatibilitytools.d;~/.var/app/com.valvesoftware.Steam/.steam/root/compatibilitytools.d

# Directory where Proton/Wine prefixes are stored.
# Defaults to ~/Documents/Proton/env if left empty or removed.
prefix_dir = ~/Documents/Proton/env
"""

        try:
            with open(CONFIG_FILE, "w") as f:
                f.write(sample)
        except Exception:
            pass

    # ----------------------------
    # base paths (always safe)
    # ----------------------------
    base_paths = [os.path.expanduser(p) for p in DEFAULT_PROTON_PATHS]

    # ----------------------------
    # auto-create config if missing
    # ----------------------------
    if not os.path.isfile(CONFIG_FILE):
        create_default_config()
        return base_paths

    config = configparser.ConfigParser()

    try:
        config.read(CONFIG_FILE)

        if config.has_section("proton") and config.has_option("proton", "paths"):
            raw = config["proton"]["paths"]

            for p in re.split(r"[;:\n]", raw):
                p = os.path.expanduser(p.strip())
                if p:
                    base_paths.append(p)

    except Exception:
        # fail-safe: never break proton detection
        return base_paths

    # ------------------------------------
    # normalization + deduplication (SAFE)
    # ------------------------------------
    cleaned = []
    seen = set()

    for p in base_paths:
        if not p:
            continue

        # keep symlinks safe (Steam/Flatpak compatibility)
        p = os.path.expanduser(p)
        p = os.path.normpath(p)

        # stable dedup key
        key = p.lower()

        if key in seen:
            continue

        seen.add(key)
        cleaned.append(p)

    return cleaned


def load_prefix_dir() -> str:
    """
    Retourne le dossier racine des préfixes Proton/Wine (~expanded, normalisé).

    Priorité :
      1. clé `prefix_dir` de la section [proton] du fichier de config
      2. valeur par défaut PREFIX_DIR_PATH (~/Documents/Proton/env)

    Ne crée jamais le fichier de config elle-même (c'est le rôle de
    load_proton_paths()) — si le fichier n'existe pas encore, ou si la clé
    est absente/vide/invalide, on replie silencieusement sur la valeur par
    défaut, comme pour load_proton_paths().
    """
    if not os.path.isfile(CONFIG_FILE):
        return PREFIX_DIR_PATH

    config = configparser.ConfigParser()

    try:
        config.read(CONFIG_FILE)

        if config.has_section("proton") and config.has_option("proton", "prefix_dir"):
            raw = config["proton"]["prefix_dir"].strip()
            if raw:
                return os.path.normpath(os.path.expanduser(raw))

    except Exception:
        # fail-safe: ne jamais casser la résolution du dossier de préfixes
        return PREFIX_DIR_PATH

    return PREFIX_DIR_PATH
