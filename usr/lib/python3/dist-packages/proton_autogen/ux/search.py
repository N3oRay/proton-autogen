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

        if features.get("gamemode"):
            fields.append("gamemode")

        if features.get("gamescope"):
            fields.append("gamescope")

        searchable = " ".join(fields).lower()

        if text in searchable:
            results.append(game)

    return results
