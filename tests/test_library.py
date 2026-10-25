"""Tests de proton_autogen.library — purs, sans GTK, sans disque.

Les fonctions `_old_*` sont les implémentations d'origine de
ux/dashboard.py, recopiées telles quelles : les tests d'équivalence prouvent
que l'extraction ne change aucun résultat.
"""

import random
from datetime import datetime, timedelta

import pytest

from proton_autogen import library

pytestmark = pytest.mark.unit


# --- implémentations d'origine (ux/dashboard.py, avant extraction) ---------

def _old_get_recent_games(games, limit=6):
    def last_launch_dt(g):
        raw = g.get("playtime", {}).get("last_launch")
        if not raw:
            return None
        try:
            return datetime.fromisoformat(raw)
        except Exception:
            return None

    played = [(g, last_launch_dt(g)) for g in games]
    played = [(g, dt) for g, dt in played if dt is not None]
    played.sort(key=lambda pair: pair[1], reverse=True)
    return [g for g, _ in played][:limit]


def _old_get_favorite_games(games, limit=6):
    return [g for g in games if g.get("favorite", False)][:limit]


def _old_shown(games, favorites_only):
    return [g for g in games if g.get("favorite")] if favorites_only else games


# --- jeu de données aléatoire mais reproductible ---------------------------

def _random_games(rng, n):
    base = datetime(2026, 1, 1)
    games = []
    for i in range(n):
        g = {"name": f"game{i}", "path": f"/g/{i}.exe"}
        if rng.random() < 0.9:
            g["favorite"] = rng.random() < 0.4
        kind = rng.random()
        if kind < 0.6:
            dt = base + timedelta(minutes=rng.randint(0, 100000))
            g["playtime"] = {"last_launch": dt.isoformat()}
        elif kind < 0.7:
            g["playtime"] = {"last_launch": "pas-une-date"}
        elif kind < 0.8:
            g["playtime"] = {"last_launch": None}
        elif kind < 0.9:
            g["playtime"] = {}
        # sinon : clé "playtime" absente
        games.append(g)
    return games


@pytest.mark.parametrize("seed", range(25))
def test_equivalence_avec_ancien_code(seed):
    rng = random.Random(seed)
    games = _random_games(rng, rng.randint(0, 40))

    for limit in (0, 1, 6, 20, 1000):
        assert library.get_recent_games(games, limit) == _old_get_recent_games(games, limit)
        assert library.get_favorite_games(games, limit) == _old_get_favorite_games(games, limit)

    for favorites_only in (False, True):
        assert library.visible_games(games, favorites_only) == _old_shown(games, favorites_only)


def test_visible_games_sans_filtre_renvoie_la_meme_liste():
    games = [{"favorite": True}, {"favorite": False}]
    assert library.visible_games(games, False) is games


def test_recents_tries_du_plus_recent_au_plus_ancien():
    games = [
        {"name": "a", "playtime": {"last_launch": "2026-01-01T10:00:00"}},
        {"name": "b", "playtime": {"last_launch": "2026-03-01T10:00:00"}},
        {"name": "c", "playtime": {"last_launch": "2026-02-01T10:00:00"}},
        {"name": "jamais", "playtime": {}},
    ]
    assert [g["name"] for g in library.get_recent_games(games)] == ["b", "c", "a"]


def test_favoris_gardent_l_ordre_et_respectent_la_limite():
    games = [{"name": str(i), "favorite": i % 2 == 0} for i in range(10)]
    assert [g["name"] for g in library.get_favorite_games(games, 3)] == ["0", "2", "4"]


def test_playtime_none_ne_plante_plus():
    # Seule différence volontaire avec l'ancien code, qui levait
    # AttributeError si une config contenait "playtime": null.
    games = [{"name": "x", "playtime": None}]
    assert library.get_recent_games(games) == []
