#stats.py

import os
import json

from proton_autogen.utils.logger import StructuredLogger
from datetime import datetime, timedelta

from proton_autogen.loader import save_game_config, load_game_config
from proton_autogen.notify import notifications

#-------------------------- Init Log -------------------
logger = StructuredLogger("proton-autogen.stats")


BADGE_TYPE_PROFILE = [

    # ------------------------------------------
    # TYPE
    # ------------------------------------------

    {
        "type": "legacy",
        "label": "🕰️",
        "css": "profile",
        "condition": lambda g: g.get("exe_type") == "legacy",
        "text": lambda g: "Legacy profile"
    },

    {
        "type": "launcher",
        "label": "🚀",
        "css": "profile",
        "condition": lambda g: g.get("exe_type") == "launcher",
        "text": lambda g: "Launcher profile"
    },

    {
        "type": "dx11",
        "label": "🎮",
        "css": "profile",
        "condition": lambda g: g.get("exe_type") == "dx11",
        "text": lambda g: "DirectX 11"
    },

    {
        "type": "dx11Bnet",
        "label": "🎮",
        "css": "profile",
        "condition": lambda g: g.get("exe_type") == "dx11Bnet",
        "text": lambda g: "DirectX 11 (Battle.net)"
    },

    {
        "type": "dx12",
        "label": "⚡",
        "css": "profile",
        "condition": lambda g: g.get("exe_type") == "dx12",
        "text": lambda g: "DirectX 12"
    },

    {
        "type": "dx9",
        "label": "🎲",
        "css": "profile",
        "condition": lambda g: g.get("exe_type") == "dx9",
        "text": lambda g: "DirectX 9"
    },

    {
        "type": "dx9dg",
        "label": "🧩",
        "css": "profile",
        "condition": lambda g: g.get("exe_type") == "dx9dg",
        "text": lambda g: "DirectX 9 + dgVoodoo"
    },

    {
        "type": "dx8dg",
        "label": "🧩",
        "css": "profile",
        "condition": lambda g: g.get("exe_type") == "dx8dg",
        "text": lambda g: "DirectX 8 + dgVoodoo"
    },

    {
        "type": "dx9opengl",
        "label": "🌐",
        "css": "profile",
        "condition": lambda g: g.get("exe_type") == "dx9opengl",
        "text": lambda g: "DirectX 9 + OpenGL"
    },

    {
        "type": "install",
        "label": "📦",
        "css": "profile",
        "condition": lambda g: g.get("exe_type") == "install",
        "text": lambda g: "Installer"
    },

    {
        "type": "oldgame",
        "label": "🕹️",
        "css": "profile",
        "condition": lambda g: g.get("exe_type") == "oldgame",
        "text": lambda g: "Old game compatibility"
    },

    {
        "type": "ut99",
        "label": "💥",
        "css": "profile",
        "condition": lambda g: g.get("exe_type") == "ut99",
        "text": lambda g: "Unreal Tournament 99"
    },

    {
        "type": "ut3",
        "label": "🔫",
        "css": "profile",
        "condition": lambda g: g.get("exe_type") == "ut3",
        "text": lambda g: "Unreal Tournament 3"
    },

    {
        "type": "quake",
        "label": "☄️",
        "css": "profile",
        "condition": lambda g: g.get("exe_type") == "quake",
        "text": lambda g: "Quake"
    },

    {
        "type": "valve",
        "label": "🔧",
        "css": "profile",
        "condition": lambda g: g.get("exe_type") == "valve",
        "text": lambda g: "GoldSrc engine"
    },

    {
        "type": "win95",
        "label": "💾",
        "css": "profile",
        "condition": lambda g: g.get("exe_type") == "win95",
        "text": lambda g: "Windows 95 compatibility"
    },

    {
        "type": "desktop",
        "label": "🖥️",
        "css": "profile",
        "condition": lambda g: g.get("exe_type") == "desktop",
        "text": lambda g: "Windows desktop"
    },

]

# ------------------------------------------
# BADGE GAMES
# ------------------------------------------

BADGE_TYPE_GAME = [
    # -------------------------
    # TYPE GAME
    # -------------------------

    {
        "type": "battlenet",
        "label": "⚔️",
        "css": "platform",
        "condition": lambda g: "battle.net" in g.get("path", "").lower(),
        "text": lambda g: "Battle.net game"
    },


    {
        "type": "steam",
        "label": "🚂",
        "css": "platform",
        "condition": lambda g: "steam" in g.get("path", "").lower(),
        "text": lambda g: "Steam game"
    },

    {
        "type": "epic",
        "label": "🟦",
        "css": "platform",
        "condition": lambda g: "epic games" in g.get("path", "").lower(),
        "text": lambda g: "Epic Games"
    },

    {
        "type": "gog",
        "label": "🟣",
        "css": "platform",
        "condition": lambda g: "gog" in g.get("path", "").lower(),
        "text": lambda g: "GOG game"
    },


    {
        "type": "ubisoft",
        "label": "🌀",
        "css": "platform",
        "condition": lambda g: "ubisoft" in g.get("path", "").lower(),
        "text": lambda g: "Ubisoft Connect"
    },

    {
        "type": "ea",
        "label": "⚽",
        "css": "platform",
        "condition": lambda g: "ea app" in g.get("path", "").lower(),
        "text": lambda g: "EA App"
    },


    {
        "type": "rockstar",
        "label": "⭐",
        "css": "platform",
        "condition": lambda g: "rockstar games" in g.get("path", "").lower(),
        "text": lambda g: "Rockstar Games Launcher"
    },

]


# ------------------------------------------
# BADGES JOUEUR (traduits)
#
# Une seule définition canonique par type — plus de duplication d'un bloc
# BADGE_DEFINITIONS_XX entier par langue. label/css/condition sont
# strictement identiques quelle que soit la langue (vérifié à l'extraction) ;
# seul le texte affiché change, et il est chargé à la demande depuis
# locales/stats_<code>.json (voir plus bas).
#
# "time" est un cas particulier : son texte est calculé dynamiquement
# (format_playtime) et n'a jamais été traduit — il garde donc son lambda
# "text" ici plutôt que de passer par les fichiers de traduction.
# ------------------------------------------

BADGE_PLAYER_RULES = [
    # -------------------------
    # CLASSIQUES
    # -------------------------
    {
        "type": "favorite",
        "label": "⭐",
        "css": "favorite",
        "condition": lambda g: g.get("favorite"),
    },
    {
        "type": "recent",
        "label": "🔥",
        "css": "favorite",
        "condition": lambda g: is_recent_launch(g.get("playtime", {}), 7),
    },
    {
        "type": "time",
        "label": "⏱",
        "css": "favorite",
        "condition": lambda g: g.get("playtime", {}).get("seconds", 0) >= 3600,
        "text": lambda g: format_playtime(g.get("playtime", {}).get("seconds", 0)),
    },

    # -------------------------
    # MODE JOUEUR
    # -------------------------
    {
        "type": "gamemode",
        "label": "🚀",
        "css": "feature",
        "condition": lambda g: g.get("features", {}).get("gamemode", False),
    },
    {
        "type": "gamescope",
        "label": "🖥️",
        "css": "feature",
        "condition": lambda g: g.get("features", {}).get("gamescope", False),
    },
    {
        "type": "mangohud",
        "label": "📊",
        "css": "feature",
        "condition": lambda g: g.get("features", {}).get("mangohud", False),
    },

    # -------------------------
    # HUMOUR / RANGS JOUEUR
    # -------------------------
    {
        "type": "rookie",
        "label": "🐣",
        "css": "rookie",
        "condition": lambda g: 0 < g.get("playtime", {}).get("seconds", 0) < 3600,
    },
    {
        "type": "casual",
        "label": "🙂",
        "css": "casual",
        "condition": lambda g: 3600 <= g.get("playtime", {}).get("seconds", 0) < 10 * 3600,
    },
    {
        "type": "gamer",
        "label": "🎮",
        "css": "gamer",
        "condition": lambda g: 10 * 3600 <= g.get("playtime", {}).get("seconds", 0) < 50 * 3600,
    },
    {
        "type": "heavy",
        "label": "🏆",
        "css": "heavy",
        "condition": lambda g: g.get("playtime", {}).get("seconds", 0) >= 50 * 3600,
    },
    {
        "type": "addict",
        "label": "💀",
        "css": "addict",
        "condition": lambda g: g.get("playtime", {}).get("seconds", 0) >= 150 * 3600,
    },
    {
        "type": "night_owl",
        "label": "🌙",
        "css": "night_owl",
        "condition": lambda g: is_recent_launch(g.get("playtime", {}), 1),
    },
    {
        "type": "veteran",
        "label": "🧓",
        "css": "veteran",
        "condition": lambda g: g.get("playtime", {}).get("seconds", 0) >= 300 * 3600,
    },
]

_ALL_BADGE_RULES = BADGE_TYPE_PROFILE + BADGE_TYPE_GAME + BADGE_PLAYER_RULES


# ------------------------------------------------------------------------------------
# TEXTES DE BADGES : chargement paresseux
#
# Même stratégie que i18n.py / desc.py : un fichier locales/stats_<code>.json
# par langue, chargé et mis en cache uniquement à la première utilisation.
# Préfixe "stats_" pour cohabiter dans locales/ avec les fichiers de i18n.py
# (fr.json, en.json...) et de desc.py (desc_fr.json...).
# ------------------------------------------------------------------------------------

_LOCALES_DIR = os.path.join(os.path.dirname(__file__), "locales")
_STATS_PREFIX = "stats_"

# Cache des langues déjà chargées : {code: {type_or_key: text}}
_STATS_CACHE: dict[str, dict] = {}


def _discover_available_stats_langs() -> set[str]:
    try:
        return {
            fname[len(_STATS_PREFIX):-5]  # retire "stats_" et ".json"
            for fname in os.listdir(_LOCALES_DIR)
            if fname.startswith(_STATS_PREFIX) and fname.endswith(".json")
        }
    except OSError:
        return {"en"}


AVAILABLE_STATS_LANGS = _discover_available_stats_langs()


def _load_stats_file(code: str) -> dict:
    path = os.path.join(_LOCALES_DIR, f"{_STATS_PREFIX}{code}.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _get_stats_table(code: str) -> dict:
    """Retourne la table de textes de badges d'une langue, en la chargeant et
    la mettant en cache au besoin."""
    if code in _STATS_CACHE:
        return _STATS_CACHE[code]

    try:
        table = _load_stats_file(code)
    except (OSError, json.JSONDecodeError) as e:
        print(f"[stats] WARNING: échec du chargement de '{code}' ({e}), repli sur 'en'")
        if code == "en":
            table = {}
        else:
            return _get_stats_table("en")

    _STATS_CACHE[code] = table
    return table


def _get_badge_text(lang: str, badge_type: str) -> str:
    """Texte traduit d'un badge, avec repli par clé sur 'en' si absent
    (ex: 'hi' n'a pas de textes de badges traduits -> repli sur 'en' pour
    chaque type, comme avant ce refacto)."""
    table = _get_stats_table(lang) if lang in AVAILABLE_STATS_LANGS else {}
    text = table.get(badge_type)
    if text is None:
        text = _get_stats_table("en").get(badge_type, badge_type)
    return text


def _get_badge_error_strings(lang: str) -> tuple:
    """Titre/message de la notification d'erreur d'actualisation des badges,
    avec repli sur 'en'."""
    table = _get_stats_table(lang) if lang in AVAILABLE_STATS_LANGS else {}
    en_table = _get_stats_table("en")
    title = table.get("_error_title", en_table.get("_error_title", "WARNING"))
    message = table.get("_error_message", en_table.get("_error_message", "Badge Updates"))
    return title, message


def get_game_badges(game: dict, lang: str = "en"):

    badges = []

    for badge in _ALL_BADGE_RULES:
        try:
            if badge["condition"](game):
                b = {
                    "type": badge["type"],
                    "label": badge["label"],
                }

                # 👇 AJOUT CSS CLASS
                b["css"] = badge.get("css", badge["type"])

                if "text" in badge:
                    # Cas non traduits (profil/plateforme) ou dynamiques (time)
                    val = badge["text"]
                    b["text"] = val(game) if callable(val) else val
                else:
                    b["text"] = _get_badge_text(lang, badge["type"])

                badges.append(b)

        except Exception as e:
            title, message = _get_badge_error_strings(lang)
            notifications.notify("error", title, message)
            logger.error(f"[badges] error in {badge.get('type')}: {e}")

    return badges

# ------------------------------------------
# FONCTIONS PRINCIPALES
# ------------------------------------------

def _parse_date(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except Exception:
        return None


def is_recent_launch(playtime, days=7):
    dt = _parse_date(playtime.get("last_launch"))
    if not dt:
        return False
    return datetime.now() - dt < timedelta(days=days)


def format_hours(seconds: int):
    hours = seconds // 3600
    if hours < 1:
        return "<1h"
    if hours < 10:
        return f"{hours}h"
    return f"{hours}h+"


def is_recent(last_launch, days=3):
    dt = _parse_date(last_launch)
    if not dt:
        return False
    return datetime.now() - dt <= timedelta(days=days)


def format_playtime(seconds: int):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{hours}h {minutes}m"


def get_playtime_stats(exe_path):
    stats = get_stats(exe_path)

    if not stats:
        return {}

    return stats.get("playtime", {})

def get_stats(exe_path):
    config = load_game_config(exe_path)

    if not config:
        return None

    return {
        **config,
        "playtime": _get_playtime(config),
    }


def get_stats_and_fav(exe_path):
    config = load_game_config(exe_path)
    if not config:
        return None

    return {
        "favorite": config.get("favorite", False),
        "playtime": _get_playtime(config),
    }

def reset_playtime(exe_path):
    config = load_game_config(exe_path)
    if not config:
        return False

    config["playtime"] = {
        "seconds": 0,
        "launch_count": 0,
        "last_session": 0,
        "last_launch": None,
    }

    save_game_config(config)
    return True

def get_favorite_games(games):
    return [g for g in games if g.get("favorite", False)]

def _get_playtime(config):
    """Retourne la section playtime en garantissant tous les champs."""

    playtime = config.setdefault("playtime", {})

    playtime.setdefault("seconds", 0)
    playtime.setdefault("launch_count", 0)
    playtime.setdefault("last_session", 0)
    playtime.setdefault("last_launch", None)

    return playtime


def update_playtime(exe_path, session_seconds):
    """Met à jour les statistiques après fermeture du jeu."""

    config = load_game_config(exe_path)
    if not config:
        return False

    playtime = _get_playtime(config)

    session_seconds = max(0, int(session_seconds))

    playtime["seconds"] += session_seconds
    playtime["launch_count"] += 1
    playtime["last_session"] = session_seconds
    playtime["last_launch"] = datetime.now().isoformat(timespec="seconds")

    save_game_config(config)

    return True

def get_playtime(exe_path):
    """Retourne les statistiques d'un jeu."""

    config = load_game_config(exe_path)
    if not config:
        return None

    return _get_playtime(config)


def set_favorite(exe_path, value=True):
    config = load_game_config(exe_path)
    if not config:
        return False

    config["favorite"] = bool(value)

    save_game_config(config)

    return True


def toggle_favorite(exe_path):
    config = load_game_config(exe_path)
    if not config:
        return False

    config["favorite"] = not config.get("favorite", False)

    save_game_config(config)

    return config["favorite"]


def is_favorite(exe_path):
    config = load_game_config(exe_path)
    if not config:
        return False

    return config.get("favorite", False)

# ---------------------------------------------------------------------------------------------------
def log_game_stats(exe_path):
    playtime = get_playtime_stats(exe_path) or {}

    logger.info(
        "Statistics:"
        "\n  launches : %d"
        "\n  playtime : %s",
        playtime.get("launch_count", 0),
        format_playtime(playtime.get("seconds", 0)),
    )
