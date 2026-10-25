"""Tests de library.normalize_game(s) — purs, sans GTK.

`_old_normalize` est l'ancienne liste de champs de
ux/dashboard.py::_on_games_loaded, recopiée telle quelle : le test
d'équivalence prouve que les 14 champs historiques sont inchangés.
"""

import random

import pytest

from proton_autogen import library

pytestmark = pytest.mark.unit

OLD_KEYS = (
    "name", "path", "config_path", "exe_type", "proton", "prefix", "features",
    "env", "favorite", "playtime", "badges", "app_id", "protondb", "cover_image",
)


def _old_normalize(games):
    return [
        {
            "name": g.get("name", "Unknown"),
            "path": g.get("path"),
            "config_path": g.get("config_path"),
            "exe_type": g.get("exe_type", "dx11"),
            "proton": g.get("proton", ""),
            "prefix": g.get("prefix", {}),
            "features": g.get("features", {}),
            "env": g.get("env", {}),
            "favorite": g.get("favorite", False),
            "playtime": g.get("playtime", {}),
            "badges": g.get("badges", []),
            "app_id": g.get("app_id"),
            "protondb": g.get("protondb"),
            "cover_image": g.get("cover_image"),
        }
        for g in games
        if isinstance(g, dict)
    ]


def _random_game(rng):
    values = {
        "name": "Jeu", "path": "/g/a.exe", "config_path": "/c/a.json",
        "exe_type": "dx12", "proton": "/p/GE", "prefix": {"name": "main"},
        "features": {"mangohud": True}, "env": {"A": "1"}, "favorite": True,
        "playtime": {"seconds": 5}, "badges": [{"type": "x"}], "app_id": "42",
        "protondb": object(), "cover_image": "/c/img.png",
    }
    game = {}
    for key in OLD_KEYS:
        roll = rng.random()
        if roll < 0.5:
            game[key] = values[key]          # présente avec une valeur
        elif roll < 0.65:
            game[key] = None                 # présente mais None
        # sinon : absente
    return game


@pytest.mark.parametrize("seed", range(30))
def test_equivalence_des_14_champs_historiques(seed):
    rng = random.Random(seed)
    games = [_random_game(rng) for _ in range(rng.randint(0, 25))]
    games.insert(rng.randint(0, len(games)), "pas un dict")   # élément ignoré
    games.append(None)

    new = library.normalize_games(games)
    old = _old_normalize(games)

    assert len(new) == len(old)
    for n, o in zip(new, old):
        assert {k: n[k] for k in OLD_KEYS} == o


def test_entree_complete_identique_a_l_ancien_resultat():
    game = _random_game(random.Random(1))
    full = {k: game.get(k) for k in OLD_KEYS}
    assert library.normalize_games([full]) == _old_normalize([full])


def test_une_cle_inconnue_traverse():
    # C'est le correctif du bug « cover_image perdu » : un champ ajouté
    # côté backend atteint l'UI sans modifier le Dashboard.
    game = {"name": "x", "nouveau_champ": 123}
    assert library.normalize_game(game)["nouveau_champ"] == 123


def test_valeur_none_presente_est_conservee():
    assert library.normalize_game({"prefix": None})["prefix"] is None


def test_defauts_modifiables_jamais_partages():
    a = library.normalize_game({})
    b = library.normalize_game({})
    a["env"]["X"] = "1"
    a["badges"].append("b")
    assert b["env"] == {} and b["badges"] == []


def test_l_original_n_est_pas_modifie():
    original = {"name": "x"}
    library.normalize_game(original)
    assert original == {"name": "x"}
