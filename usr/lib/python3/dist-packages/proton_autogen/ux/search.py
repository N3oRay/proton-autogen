def filter_games(games, text):
    """
    Recherche dans toutes les informations utiles d'un jeu.
    """

    text = text.lower().strip()

    if not text:
        return games

    results = []

    for game in games:

        fields = [
            game.get("name", ""),
            game.get("path", ""),
            game.get("exe_type", ""),
            game.get("proton", ""),
            game.get("prefix", {}).get("name", "")
        ]

        features = game.get("features", {})

        if features.get("mangohud"):
            fields.append("mangohud")

            fps_limit = features.get("fps_limit")
            if fps_limit:
                fields.append(str(fps_limit))
                fields.append(f"fps:{fps_limit}")

        if features.get("gamemode"):
            fields.append("gamemode")

        if features.get("gamescope"):
            fields.append("gamescope")

        # Variables d'environnement personnalisées : on rend à la fois
        # les noms et les valeurs cherchables (ex: "DXVK_ASYNC" ou "0")
        env = game.get("env", {}) or {}
        for key, value in env.items():
            fields.append(str(key))
            fields.append(str(value))

        searchable = " ".join(fields).lower()

        if text in searchable:
            results.append(game)

    return results
