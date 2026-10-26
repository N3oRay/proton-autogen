"""Cache d'index des manifestes Steam (utils/steam_appid) — sans GTK."""

from pathlib import Path

import pytest

from proton_autogen.utils import steam_appid
from proton_autogen.utils.steam_appid import detect_steam_appid

pytestmark = pytest.mark.unit

_ENV = ("STEAM_COMPAT_APP_ID", "SteamAppId", "SteamGameId")


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    for key in _ENV:
        monkeypatch.delenv(key, raising=False)


def _manifest(steamapps, appid, installdir, filename=None, body=None):
    name = filename or f"appmanifest_{appid}.acf"
    content = body if body is not None else (
        '"AppState"\n{\n\t"appid"\t"%s"\n\t"installdir"\t"%s"\n}\n' % (appid, installdir)
    )
    (steamapps / name).write_text(content, encoding="utf-8")


@pytest.fixture
def library(tmp_path):
    """Bibliothèque Steam factice avec des cas tordus."""
    steamapps = tmp_path / "SteamLibrary" / "steamapps"
    (steamapps / "common").mkdir(parents=True)

    for i in range(20):
        _manifest(steamapps, 1000 + i, f"Game{i}")

    _manifest(steamapps, 2001, "Dup")                       # deux manifestes,
    _manifest(steamapps, 2002, "Dup")                       # même installdir
    _manifest(steamapps, 0, "", filename="appmanifest_abc.acf")        # nom invalide
    _manifest(steamapps, 3001, "", body='"AppState"\n{\n"appid" "3001"\n}\n')  # sans installdir
    _manifest(steamapps, 3002, "Spaced Name")
    return steamapps


def _exe(steamapps, game_dir):
    # Nom d'exécutable volontairement improbable : "game.exe" figure dans
    # KNOWN_APPIDS et serait résolu par la détection « exécutable connu ».
    return str(steamapps / "common" / game_dir / "bin" / "zz_unit_test_game.exe")


def _all_cases(steamapps, tmp_path):
    cases = [_exe(steamapps, f"Game{i}") for i in range(20)]
    cases += [
        _exe(steamapps, "Dup"),             # doublon : même gagnant des deux côtés
        _exe(steamapps, "Spaced Name"),
        _exe(steamapps, "Inconnu"),         # dossier sans manifeste
        str(tmp_path / "Jeux" / "other.exe"),                    # hors Steam
        str(steamapps / "common"),                               # 'common' en fin de chemin
        str(tmp_path / "nowhere" / "steamapps" / "common" / "X" / "x.exe"),  # steamapps absent
    ]
    return cases


def test_resultats_identiques_avec_et_sans_cache(library, tmp_path):
    cache = {}

    for exe in _all_cases(library, tmp_path):
        expected = detect_steam_appid(exe, fallback=False)
        assert detect_steam_appid(exe, fallback=False, manifest_cache=cache) == expected, exe


def test_resultats_attendus(library):
    cache = {}
    assert detect_steam_appid(_exe(library, "Game7"), fallback=False, manifest_cache=cache) == "1007"
    assert detect_steam_appid(_exe(library, "Spaced Name"), fallback=False, manifest_cache=cache) == "3002"
    assert detect_steam_appid(_exe(library, "Inconnu"), fallback=False, manifest_cache=cache) is None
    # nom de fichier invalide / installdir absent : jamais retournés
    assert detect_steam_appid(_exe(library, ""), fallback=False, manifest_cache=cache) is None


def test_chaque_dossier_steamapps_n_est_lu_qu_une_fois(library, monkeypatch):
    reads = []
    original = Path.read_text

    def counting(self, *a, **kw):
        if self.name.endswith(".acf"):
            reads.append(self.name)
        return original(self, *a, **kw)

    monkeypatch.setattr(Path, "read_text", counting)

    n_manifests = len(list(library.glob("appmanifest_*.acf")))
    cache = {}
    for i in range(20):
        detect_steam_appid(_exe(library, f"Game{i}"), fallback=False, manifest_cache=cache)

    assert len(reads) <= n_manifests          # une lecture par manifeste, au plus

    reads.clear()
    for i in range(20):
        detect_steam_appid(_exe(library, f"Game{i}"), fallback=False)   # sans cache

    assert len(reads) > n_manifests           # comportement d'origine : bien plus


def test_un_nouveau_cache_voit_les_manifestes_ajoutes(library):
    cache = {}
    exe = _exe(library, "NouveauJeu")
    assert detect_steam_appid(exe, fallback=False, manifest_cache=cache) is None

    _manifest(library, 4001, "NouveauJeu")

    # même cache : index déjà lu (le cache vit le temps d'UN traitement groupé)
    assert detect_steam_appid(exe, fallback=False, manifest_cache=cache) is None
    # nouveau traitement = nouveau dict = données fraîches
    assert detect_steam_appid(exe, fallback=False, manifest_cache={}) == "4001"


def test_sans_cache_le_comportement_d_origine_est_conserve(library):
    assert detect_steam_appid(_exe(library, "Game3"), fallback=False) == "1003"
    assert detect_steam_appid(_exe(library, "Inconnu"), fallback=True) == steam_appid._FALLBACK_APPID


def test_l_environnement_reste_prioritaire(library, monkeypatch):
    monkeypatch.setenv("SteamAppId", "999")
    assert detect_steam_appid(_exe(library, "Game3"), fallback=False, manifest_cache={}) == "999"
