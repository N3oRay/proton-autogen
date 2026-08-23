import os
import shutil
from pathlib import Path
import configparser

CONFIG_PATH = Path.home() / ".config" / "proton-autogen" / "proton-autogen-ux.conf"

# Ancien emplacement (avant regroupement sous ~/.config/proton-autogen/).
_LEGACY_CONFIG_PATH = Path.home() / ".config" / "proton-autogen-ux.conf"


def _migrate_legacy_config():
    """Déplace l'ancien ~/.config/proton-autogen-ux.conf vers le nouvel
    emplacement ~/.config/proton-autogen/proton-autogen-ux.conf, une seule
    fois, sans jamais écraser un fichier déjà présent au nouvel endroit.
    Échec silencieux : ne doit jamais empêcher le démarrage de l'appli."""
    if CONFIG_PATH.exists():
        return  # déjà migré, ou déjà (re)créé au nouvel emplacement

    if not _LEGACY_CONFIG_PATH.exists():
        return  # rien à migrer (nouvelle installation)

    try:
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(_LEGACY_CONFIG_PATH), str(CONFIG_PATH))
    except Exception:
        pass


_migrate_legacy_config()

DEFAULT_THEME = "fluent"
AVAILABLE_THEMES = ["fluent", "gta", "adwaita", "hellokit", "cute", "dark", "sky", "Breeze"]


def _ensure_default_config():
    """Crée le fichier de configuration et ajoute les valeurs par défaut
    manquantes, sans écraser les préférences existantes."""
    cfg = configparser.ConfigParser()

    if CONFIG_PATH.exists():
        try:
            cfg.read(CONFIG_PATH)
        except Exception:
            pass

    if "ui" not in cfg:
        cfg["ui"] = {}

    if "theme" not in cfg["ui"]:
        cfg["ui"]["theme"] = DEFAULT_THEME

    if "mini" not in cfg:
        cfg["mini"] = {}

    if "mini_mode" not in cfg["mini"]:
        cfg["mini"]["mini_mode"] = "true"

    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        cfg.write(f)


_ensure_default_config()

BACKGROUND_THEMES = {
            "fluent": "logo-pa.jpg",
            "gta": "logo-gta.jpg",
            "adwaita": "logo-adwaita.jpg",
            "hellokit": "logo-hellokit.jpg",
            "cute": "logo-cute.jpg",
            "dark": "logo-dark.jpg",
            "sky": "logo-sky.jpg",
            "Breeze": "logo-kde.jpg",
        }
base = os.path.dirname(__file__)

STYLE_CSS = {
            "fluent": os.path.join(base, "assets", "style.css"),
            "gta": os.path.join(base, "assets", "style.css"),
            "adwaita": os.path.join(base, "assets", "style_adwaita.css"),
            "hellokit": os.path.join(base, "assets", "hello-kit.css"),
            "cute": os.path.join(base, "assets", "style-cute.css"),
            "dark": os.path.join(base, "assets", "style-dark.css"),
            "sky": os.path.join(base, "assets", "style-dark.css"),
            "Breeze": os.path.join(base, "assets", "style-kde.css"),
        }

def load_saved_theme() -> str:
    cfg = configparser.ConfigParser()
    if CONFIG_PATH.exists():
        try:
            cfg.read(CONFIG_PATH)
            return cfg.get("ui", "theme", fallback=DEFAULT_THEME)
        except Exception:
            return DEFAULT_THEME
    return DEFAULT_THEME

def save_theme(theme: str):
    cfg = configparser.ConfigParser()
    if CONFIG_PATH.exists():
        try:
            cfg.read(CONFIG_PATH)
        except Exception:
            pass
    if "ui" not in cfg:
        cfg["ui"] = {}
    cfg["ui"]["theme"] = theme
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        cfg.write(f)
