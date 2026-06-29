#stats.py


from datetime import datetime, timedelta


# ------------------------------------------
# BADGE GAMES
# ------------------------------------------
BADGE_DEFINITIONS = [
    {
        "type": "favorite",
        "label": "⭐",
        "condition": lambda g: g.get("favorite")
    },
    {
        "type": "recent",
        "label": "🔥",
        "condition": lambda g: is_recent_launch(g.get("playtime", {}), 7)
    },
    {
        "type": "time",
        "label": "⏱",
        "condition": lambda g: g.get("playtime", {}).get("seconds", 0) >= 3600,
        "text": lambda g: format_playtime(g.get("playtime", {}).get("seconds", 0))
    },
    {
        "type": "heavy",
        "label": "🏆",
        "condition": lambda g: g.get("playtime", {}).get("seconds", 0) >= 3600 * 50,
        "text": lambda g: "Gros joueur"
    },
]

def get_game_badges(game: dict):
    badges = []

    for badge in BADGE_DEFINITIONS:
        if badge["condition"](game):
            b = {
                "type": badge["type"],
                "label": badge["label"],
            }

            if "text" in badge:
                val = badge["text"]
                b["text"] = val(game) if callable(val) else val

            badges.append(b)

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
    if not last_launch:
        return False

    try:
        dt = datetime.fromisoformat(last_launch)
    except Exception:
        return False

    return datetime.now() - dt <= timedelta(days=days)





def format_playtime(seconds: int):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{hours}h {minutes}m"


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

def get_stats(exe_path):
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
