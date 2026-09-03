import os
import shutil
from pathlib import Path
from typing import Optional
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
AVAILABLE_THEMES = ["fluent", "gta", "adwaita", "hellokit", "cute", "dark", "sky", "Breeze", "ironman", "ironpro", "ironwood"]

# Taille par défaut de la fenêtre principale au tout premier lancement
# (avant toute sauvegarde), ou quand remember_window_size = false.
DEFAULT_WINDOW_WIDTH = 1120
DEFAULT_WINDOW_HEIGHT = 800

# Taille minimale absolue, appliquée quel que soit remember_window_size :
# protège contre une valeur corrompue ou aberrante dans le fichier de
# config (ex. édition manuelle malheureuse, largeur négative ou nulle)
# qui rendrait sinon la fenêtre inutilisable au prochain lancement.
MIN_WINDOW_WIDTH = 800
MIN_WINDOW_HEIGHT = 600


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

    if "window" not in cfg:
        cfg["window"] = {}

    if "remember_window_size" not in cfg["window"]:
        cfg["window"]["remember_window_size"] = "true"

    if "width" not in cfg["window"]:
        cfg["window"]["width"] = str(DEFAULT_WINDOW_WIDTH)

    if "height" not in cfg["window"]:
        cfg["window"]["height"] = str(DEFAULT_WINDOW_HEIGHT)

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
            "ironman": "logo-ironman.jpg",
            "ironpro": "logo-ironpro.jpg",
            "ironwood": "logo-ironman2.jpg",

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
            "ironman": os.path.join(base, "assets", "style-ironman.css"),
            "ironpro": os.path.join(base, "assets", "style-bios.css"),
            "ironwood": os.path.join(base, "assets", "style-ironman.css"),
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


# ------------------------------------------------------------------------------------
# LANGUE
# ------------------------------------------------------------------------------------

def load_saved_language() -> Optional[str]:
    """Retourne la langue explicitement choisie via le panneau de
    réglages, ou None si l'utilisateur n'a jamais rien sauvegardé — dans
    ce cas l'appelant doit retomber sur la détection CLI/environnement
    habituelle (detect_help_env_lang() dans i18n.py)."""
    cfg = configparser.ConfigParser()
    if CONFIG_PATH.exists():
        try:
            cfg.read(CONFIG_PATH)
            value = cfg.get("ui", "language", fallback="").strip()
            return value or None
        except Exception:
            return None
    return None


def save_language(lang: str):
    cfg = configparser.ConfigParser()
    if CONFIG_PATH.exists():
        try:
            cfg.read(CONFIG_PATH)
        except Exception:
            pass
    if "ui" not in cfg:
        cfg["ui"] = {}
    cfg["ui"]["language"] = lang
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        cfg.write(f)


# ------------------------------------------------------------------------------------
# TAILLE DE FENÊTRE
# ------------------------------------------------------------------------------------

def load_remember_window_size(default: bool = True) -> bool:
    cfg = configparser.ConfigParser()
    if CONFIG_PATH.exists():
        try:
            cfg.read(CONFIG_PATH)
            return cfg.getboolean("window", "remember_window_size", fallback=default)
        except Exception:
            return default
    return default


def save_remember_window_size(enabled: bool):
    cfg = configparser.ConfigParser()
    if CONFIG_PATH.exists():
        try:
            cfg.read(CONFIG_PATH)
        except Exception:
            pass
    if "window" not in cfg:
        cfg["window"] = {}
    cfg["window"]["remember_window_size"] = "true" if enabled else "false"
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        cfg.write(f)


def load_window_size() -> tuple[int, int]:
    """Retourne (largeur, hauteur) sauvegardées, avec repli sur
    DEFAULT_WINDOW_WIDTH/HEIGHT si absentes ou illisibles. Les valeurs
    lues sont toujours bornées à MIN_WINDOW_WIDTH/MIN_WINDOW_HEIGHT :
    protège contre un fichier de config corrompu ou édité à la main
    avec des valeurs aberrantes (0, négatives...), qui rendrait sinon
    la fenêtre inutilisable au prochain lancement plutôt que de simplement
    ignorer la préférence invalide."""
    cfg = configparser.ConfigParser()
    width, height = DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT

    if CONFIG_PATH.exists():
        try:
            cfg.read(CONFIG_PATH)
            width = cfg.getint("window", "width", fallback=DEFAULT_WINDOW_WIDTH)
            height = cfg.getint("window", "height", fallback=DEFAULT_WINDOW_HEIGHT)
        except Exception:
            width, height = DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT

    width = max(width, MIN_WINDOW_WIDTH)
    height = max(height, MIN_WINDOW_HEIGHT)

    return width, height


def save_window_size(width: int, height: int):
    # Ne jamais persister une taille invalide (ex. lue pendant un état
    # transitoire de la fenêtre, avant sa première allocation réelle).
    if width <= 0 or height <= 0:
        return

    cfg = configparser.ConfigParser()
    if CONFIG_PATH.exists():
        try:
            cfg.read(CONFIG_PATH)
        except Exception:
            pass
    if "window" not in cfg:
        cfg["window"] = {}
    cfg["window"]["width"] = str(width)
    cfg["window"]["height"] = str(height)
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        cfg.write(f)
