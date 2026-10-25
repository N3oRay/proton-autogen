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
