#stats.py


from datetime import datetime, timedelta

from proton_autogen.loader import save_game_config, load_game_config


BADGE_TYPE_PROFILE = [

    {
        "type": "favorite",
        "label": "❤️",
        "condition": lambda g: g.get("favorite", False),
        "text": lambda g: "Favorite"
    },

    # ------------------------------------------
    # TYPE
    # ------------------------------------------

    {
        "type": "legacy",
        "label": "🕰️",
        "condition": lambda g: g.get("exe_type") == "legacy",
        "text": lambda g: "Legacy profile"
    },

    {
        "type": "launcher",
        "label": "🚀",
        "condition": lambda g: g.get("exe_type") == "launcher",
        "text": lambda g: "Launcher profile"
    },

    {
        "type": "dx11",
        "label": "🎮",
        "condition": lambda g: g.get("exe_type") == "dx11",
        "text": lambda g: "DirectX 11"
    },

    {
        "type": "dx11Bnet",
        "label": "🎮",
        "condition": lambda g: g.get("exe_type") == "dx11Bnet",
        "text": lambda g: "DirectX 11 (Battle.net)"
    },

    {
        "type": "dx12",
        "label": "⚡",
        "condition": lambda g: g.get("exe_type") == "dx12",
        "text": lambda g: "DirectX 12"
    },

    {
        "type": "dx9",
        "label": "🎲",
        "condition": lambda g: g.get("exe_type") == "dx9",
        "text": lambda g: "DirectX 9"
    },

    {
        "type": "dx9dg",
        "label": "🧩",
        "condition": lambda g: g.get("exe_type") == "dx9dg",
        "text": lambda g: "DirectX 9 + dgVoodoo"
    },

    {
        "type": "dx8dg",
        "label": "🧩",
        "condition": lambda g: g.get("exe_type") == "dx8dg",
        "text": lambda g: "DirectX 8 + dgVoodoo"
    },

    {
        "type": "dx9opengl",
        "label": "🌐",
        "condition": lambda g: g.get("exe_type") == "dx9opengl",
        "text": lambda g: "DirectX 9 + OpenGL"
    },

    {
        "type": "install",
        "label": "📦",
        "condition": lambda g: g.get("exe_type") == "install",
        "text": lambda g: "Installer"
    },

    {
        "type": "oldgame",
        "label": "🕹️",
        "condition": lambda g: g.get("exe_type") == "oldgame",
        "text": lambda g: "Old game compatibility"
    },

    {
        "type": "ut99",
        "label": "💥",
        "condition": lambda g: g.get("exe_type") == "ut99",
        "text": lambda g: "Unreal Tournament 99"
    },

    {
        "type": "ut3",
        "label": "🔫",
        "condition": lambda g: g.get("exe_type") == "ut3",
        "text": lambda g: "Unreal Tournament 3"
    },

    {
        "type": "quake",
        "label": "☄️",
        "condition": lambda g: g.get("exe_type") == "quake",
        "text": lambda g: "Quake"
    },

    {
        "type": "valve",
        "label": "🔧",
        "condition": lambda g: g.get("exe_type") == "valve",
        "text": lambda g: "GoldSrc engine"
    },

    {
        "type": "win95",
        "label": "💾",
        "condition": lambda g: g.get("exe_type") == "win95",
        "text": lambda g: "Windows 95 compatibility"
    },

    {
        "type": "desktop",
        "label": "🖥️",
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
        "condition": lambda g: "battle.net" in g.get("path", "").lower(),
        "text": lambda g: "Battle.net game"
    },


    {
        "type": "steam",
        "label": "🚂",
        "condition": lambda g: "steam" in g.get("path", "").lower(),
        "text": lambda g: "Steam game"
    },

    {
        "type": "epic",
        "label": "🟦",
        "condition": lambda g: "epic games" in g.get("path", "").lower(),
        "text": lambda g: "Epic Games"
    },

    {
        "type": "gog",
        "label": "🟣",
        "condition": lambda g: "gog" in g.get("path", "").lower(),
        "text": lambda g: "GOG game"
    },


    {
        "type": "ubisoft",
        "label": "🌀",
        "condition": lambda g: "ubisoft" in g.get("path", "").lower(),
        "text": lambda g: "Ubisoft Connect"
    },

    {
        "type": "ea",
        "label": "⚽",
        "condition": lambda g: "ea app" in g.get("path", "").lower(),
        "text": lambda g: "EA App"
    },


    {
        "type": "rockstar",
        "label": "⭐",
        "condition": lambda g: "rockstar games" in g.get("path", "").lower(),
        "text": lambda g: "Rockstar Games Launcher"
    },

]


BADGE_DEFINITIONS_FR = [
    # -------------------------
    # CLASSIQUES
    # -------------------------
    {
        "type": "favorite",
        "label": "⭐",
        "condition": lambda g: g.get("favorite"),
        "text": lambda g: "Favori"
    },
    {
        "type": "recent",
        "label": "🔥",
        "condition": lambda g: is_recent_launch(g.get("playtime", {}), 7),
        "text": lambda g: "Récemment joué"
    },
    {
        "type": "time",
        "label": "⏱",
        "condition": lambda g: g.get("playtime", {}).get("seconds", 0) >= 3600,
        "text": lambda g: format_playtime(g.get("playtime", {}).get("seconds", 0))
    },

    # -------------------------
    # MODE JOUEUR
    # -------------------------
    {
        "type": "gamemode",
        "label": "🚀",
        "condition": lambda g: g.get("features", {}).get("gamemode", False),
        "text": lambda g: "GameMode activé"
    },
    {
        "type": "mangohud",
        "label": "📊",
        "condition": lambda g: g.get("features", {}).get("mangohud", False),
        "text": lambda g: "MangoHud activé"
    },



    # -------------------------
    # HUMOUR / RANGS JOUEUR
    # -------------------------

    # 👶 Débutant total
    {
        "type": "rookie",
        "label": "🐣",
        "condition": lambda g: 0 < g.get("playtime", {}).get("seconds", 0) < 3600,
        "text": lambda g: "Débutant (on commence doucement)"
    },

    # 🧑 joueur occasionnel
    {
        "type": "casual",
        "label": "🙂",
        "condition": lambda g: 3600 <= g.get("playtime", {}).get("seconds", 0) < 10 * 3600,
        "text": lambda g: "Casual gamer"
    },

    # 🎮 vrai joueur
    {
        "type": "gamer",
        "label": "🎮",
        "condition": lambda g: 10 * 3600 <= g.get("playtime", {}).get("seconds", 0) < 50 * 3600,
        "text": lambda g: "Gamer confirmé"
    },

    # 🏆 tryhard
    {
        "type": "heavy",
        "label": "🏆",
        "condition": lambda g: g.get("playtime", {}).get("seconds", 0) >= 50 * 3600,
        "text": lambda g: "Tryhard détecté"
    },

    # 💀 addiction douce (humour)
    {
        "type": "addict",
        "label": "💀",
        "condition": lambda g: g.get("playtime", {}).get("seconds", 0) >= 150 * 3600,
        "text": lambda g: "Send help"
    },

    # 🌙 session récente
    {
        "type": "night_owl",
        "label": "🌙",
        "condition": lambda g: is_recent_launch(g.get("playtime", {}), 1),
        "text": lambda g: "Actif récemment (nocturne ?)"
    },

    # 💾 old school / nostalgie
    {
        "type": "veteran",
        "label": "🧓",
        "condition": lambda g: g.get("playtime", {}).get("seconds", 0) >= 300 * 3600,
        "text": lambda g: "Vétéran légendaire"
    },
]


BADGE_DEFINITIONS_EN = [
    # -------------------------
    # CLASSIC
    # -------------------------
    {
        "type": "favorite",
        "label": "⭐",
        "condition": lambda g: g.get("favorite"),
        "text": lambda g: "Favorite"
    },
    {
        "type": "recent",
        "label": "🔥",
        "condition": lambda g: is_recent_launch(g.get("playtime", {}), 7),
        "text": lambda g: "Recently played"
    },
    {
        "type": "time",
        "label": "⏱",
        "condition": lambda g: g.get("playtime", {}).get("seconds", 0) >= 3600,
        "text": lambda g: format_playtime(g.get("playtime", {}).get("seconds", 0))
    },

    # -------------------------
    # PLAYER MODE
    # -------------------------
    {
        "type": "gamemode",
        "label": "🚀",
        "condition": lambda g: g.get("features", {}).get("gamemode", False),
        "text": lambda g: "GameMode enabled"
    },
    {
        "type": "mangohud",
        "label": "📊",
        "condition": lambda g: g.get("features", {}).get("mangohud", False),
        "text": lambda g: "MangoHud enabled"
    },

    # -------------------------
    # PLAYER RANKS / HUMOR
    # -------------------------

    # 👶 Beginner
    {
        "type": "rookie",
        "label": "🐣",
        "condition": lambda g: 0 < g.get("playtime", {}).get("seconds", 0) < 3600,
        "text": lambda g: "Beginner (just getting started)"
    },

    # 🧑 Casual player
    {
        "type": "casual",
        "label": "🙂",
        "condition": lambda g: 3600 <= g.get("playtime", {}).get("seconds", 0) < 10 * 3600,
        "text": lambda g: "Casual gamer"
    },

    # 🎮 Regular gamer
    {
        "type": "gamer",
        "label": "🎮",
        "condition": lambda g: 10 * 3600 <= g.get("playtime", {}).get("seconds", 0) < 50 * 3600,
        "text": lambda g: "Experienced gamer"
    },

    # 🏆 Hardcore
    {
        "type": "heavy",
        "label": "🏆",
        "condition": lambda g: g.get("playtime", {}).get("seconds", 0) >= 50 * 3600,
        "text": lambda g: "Tryhard detected"
    },

    # 💀 Addiction joke
    {
        "type": "addict",
        "label": "💀",
        "condition": lambda g: g.get("playtime", {}).get("seconds", 0) >= 150 * 3600,
        "text": lambda g: "Send help"
    },

    # 🌙 Night activity
    {
        "type": "night_owl",
        "label": "🌙",
        "condition": lambda g: is_recent_launch(g.get("playtime", {}), 1),
        "text": lambda g: "Recently active (night owl?)"
    },

    # 🧓 Veteran
    {
        "type": "veteran",
        "label": "🧓",
        "condition": lambda g: g.get("playtime", {}).get("seconds", 0) >= 300 * 3600,
        "text": lambda g: "Legendary veteran"
    },
]

BADGE_DEFINITIONS_ZH = [
    # -------------------------
    # 经典
    # -------------------------
    {
        "type": "favorite",
        "label": "⭐",
        "condition": lambda g: g.get("favorite"),
        "text": lambda g: "收藏"
    },
    {
        "type": "recent",
        "label": "🔥",
        "condition": lambda g: is_recent_launch(g.get("playtime", {}), 7),
        "text": lambda g: "最近游玩"
    },
    {
        "type": "time",
        "label": "⏱",
        "condition": lambda g: g.get("playtime", {}).get("seconds", 0) >= 3600,
        "text": lambda g: format_playtime(g.get("playtime", {}).get("seconds", 0))
    },

    # -------------------------
    # 玩家模式
    # -------------------------
    {
        "type": "gamemode",
        "label": "🚀",
        "condition": lambda g: g.get("features", {}).get("mangohud", False),
        "text": lambda g: "已启用 GameMode"
    },
    {
        "type": "mangohud",
        "label": "📊",
        "condition": lambda g: g.get("features", {}).get("mangohud", False),
        "text": lambda g: "已启用 MangoHud"
    },

    # -------------------------
    # 玩家等级 / 幽默
    # -------------------------

    # 👶 新手
    {
        "type": "rookie",
        "label": "🐣",
        "condition": lambda g: 0 < g.get("playtime", {}).get("seconds", 0) < 3600,
        "text": lambda g: "新手（刚刚开始）"
    },

    # 🧑 休闲玩家
    {
        "type": "casual",
        "label": "🙂",
        "condition": lambda g: 3600 <= g.get("playtime", {}).get("seconds", 0) < 10 * 3600,
        "text": lambda g: "休闲玩家"
    },

    # 🎮 资深玩家
    {
        "type": "gamer",
        "label": "🎮",
        "condition": lambda g: 10 * 3600 <= g.get("playtime", {}).get("seconds", 0) < 50 * 3600,
        "text": lambda g: "经验丰富的玩家"
    },

    # 🏆 硬核玩家
    {
        "type": "heavy",
        "label": "🏆",
        "condition": lambda g: g.get("playtime", {}).get("seconds", 0) >= 50 * 3600,
        "text": lambda g: "硬核玩家"
    },

    # 💀 上瘾（玩笑）
    {
        "type": "addict",
        "label": "💀",
        "condition": lambda g: g.get("playtime", {}).get("seconds", 0) >= 150 * 3600,
        "text": lambda g: "需要救援"
    },

    # 🌙 夜猫子
    {
        "type": "night_owl",
        "label": "🌙",
        "condition": lambda g: is_recent_launch(g.get("playtime", {}), 1),
        "text": lambda g: "最近活跃（夜猫子？）"
    },

    # 🧓 老玩家
    {
        "type": "veteran",
        "label": "🧓",
        "condition": lambda g: g.get("playtime", {}).get("seconds", 0) >= 300 * 3600,
        "text": lambda g: "传奇老玩家"
    },
]



BADGE_DEFINITIONS = {
    "fr": BADGE_TYPE_PROFILE + BADGE_TYPE_GAME + BADGE_DEFINITIONS_FR,
    "en": BADGE_TYPE_PROFILE + BADGE_TYPE_GAME + BADGE_DEFINITIONS_EN,
    "zh": BADGE_TYPE_PROFILE + BADGE_TYPE_GAME + BADGE_DEFINITIONS_ZH,
}

def get_game_badges(game: dict, lang: str = "en"):
    badges = []

    definitions = BADGE_DEFINITIONS.get(lang, BADGE_DEFINITIONS_EN)

    for badge in definitions:
        try:
            if badge["condition"](game):
                b = {
                    "type": badge["type"],
                    "label": badge["label"],
                }

                if "text" in badge:
                    val = badge["text"]
                    b["text"] = val(game) if callable(val) else val

                badges.append(b)

        except Exception as e:
            # évite crash UI si donnée game corrompue
            print(f"[badges] error in {badge.get('type')}: {e}")

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
