from pathlib import Path
import configparser

CONFIG_PATH = Path.home() / ".config" / "proton-autogen-ux.conf"
DEFAULT_THEME = "fluent"
AVAILABLE_THEMES = ["fluent", "adwaita", "hellokit"]

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
