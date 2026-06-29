LANG = {
    "en": {
        "favorite": "Favorite",
        "favorites": "Favorites",
        "playtime": "Play time",
        "last_session": "Last session",
        "last_launch": "Last launch",
        "launch_count": "Launches",
        "never": "Never",
    },

    "fr": {
        "favorite": "Favori",
        "favorites": "Favoris",
        "playtime": "Temps de jeu",
        "last_session": "Dernière session",
        "last_launch": "Dernier lancement",
        "launch_count": "Lancements",
        "never": "Jamais",
    },

    "zh": {
        "favorite": "收藏",
        "favorites": "收藏夹",
        "playtime": "游戏时间",
        "last_session": "最近游戏时长",
        "last_launch": "最近启动",
        "launch_count": "启动次数",
        "never": "从未",
    },
}


def tr(key, lang="en"):
    return LANG.get(lang, LANG["en"]).get(key, key)
