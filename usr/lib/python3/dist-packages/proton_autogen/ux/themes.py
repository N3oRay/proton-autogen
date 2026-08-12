import os
from pathlib import Path
import configparser

CONFIG_PATH = Path.home() / ".config" / "proton-autogen-ux.conf"
DEFAULT_THEME = "fluent"
AVAILABLE_THEMES = ["fluent", "gta", "adwaita", "hellokit", "cute", "dark", "sky", "Breeze"]

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
