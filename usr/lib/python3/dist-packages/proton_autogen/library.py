#!/usr/bin/env python3
# library.py
"""
Règles de présentation de la bibliothèque de jeux — SANS GTK.

Ce module ne contient que des fonctions pures : elles prennent des listes de
dictionnaires `game` (le format produit par backend.list_programs_ux) et
retournent de nouvelles listes, sans toucher à aucun widget, ni au disque, ni
à `self`. Il peut donc être testé par pytest sans serveur graphique et réutilisé
par la CLI ou par une future autre interface.

Extrait de ux/dashboard.py (Dashboard.get_recent_games, get_favorite_games et
le filtre « favoris » de _set_game_views). Les méthodes du Dashboard existent
toujours, avec la même signature : elles délèguent simplement ici.
"""

from datetime import datetime


# Valeurs par défaut d'un jeu pour l'interface. Les valeurs modifiables
# (dict, list) sont des fabriques : chaque jeu reçoit SON objet, jamais un
# objet partagé entre plusieurs jeux.
_GAME_DEFAULTS = {
    "name": lambda: "Unknown",
    "path": lambda: None,
    "config_path": lambda: None,
    "exe_type": lambda: "dx11",
    "proton": lambda: "",
    "prefix": dict,
    "features": dict,
    "env": dict,
    "favorite": lambda: False,
    "playtime": dict,
    "badges": list,
    "app_id": lambda: None,
    "protondb": lambda: None,
    "cover_image": lambda: None,
}


def normalize_game(game):
    """Copie d'un jeu venant de backend.list_programs_ux, prête pour l'UI.

    - TOUTES les clés fournies par le backend sont conservées : ajouter un
      champ côté backend suffit pour qu'il atteigne les vues (il n'y a plus
      de seconde liste de champs à maintenir dans le Dashboard, cause du
      bug « cover_image perdu »).
    - Les clés absentes reçoivent leur valeur par défaut ; une clé présente
      avec la valeur None est laissée telle quelle (même sémantique que
      l'ancien `g.get(clé, défaut)`).
    - La copie est superficielle : les sous-objets (features, env,
      playtime...) restent partagés avec l'original, comme avant.
    """
    normalized = dict(game)

    for key, make_default in _GAME_DEFAULTS.items():
        if key not in normalized:
            normalized[key] = make_default()

    return normalized


def normalize_games(games):
    """normalize_game() pour chaque élément qui est un dict (les autres
    éléments sont ignorés, comme avant)."""
    return [normalize_game(g) for g in games if isinstance(g, dict)]


def only_favorites(games):
    """Jeux marqués favoris, dans l'ordre d'origine."""
    return [g for g in games if g.get("favorite")]


def visible_games(games, favorites_only=False):
    """Jeux à afficher dans la grille / bibliothèque selon le filtre ★.

    Sans filtre, retourne `games` lui-même (pas une copie) : comportement
    identique à l'ancien code, qui passait la liste telle quelle aux vues.
    """
    return only_favorites(games) if favorites_only else games


def get_favorite_games(games, limit=6):
    """Les `limit` premiers favoris (carrousel « Favoris »)."""
    return only_favorites(games)[:limit]


def _last_launch(game):
    """Date du dernier lancement, ou None si absente / illisible."""
    raw = (game.get("playtime") or {}).get("last_launch")
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw)
    except Exception:
        return None


def get_recent_games(games, limit=6):
    """Les `limit` jeux lancés le plus récemment (carrousel « Récents »).

    Les jeux jamais lancés (ou dont la date est illisible) sont exclus.
    """
    played = [(g, _last_launch(g)) for g in games]
    played = [(g, dt) for g, dt in played if dt is not None]
    played.sort(key=lambda pair: pair[1], reverse=True)
    return [g for g, _ in played][:limit]
