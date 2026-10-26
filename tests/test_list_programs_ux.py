"""list_programs_ux : n'analyser que ce qui est nécessaire — sans GTK."""

import pytest

from proton_autogen import backend

pytestmark = pytest.mark.unit


@pytest.fixture
def harness(monkeypatch):
    """Remplace tout ce qui touche au disque / à l'exécutable par des doubles
    qui comptent leurs appels."""
    state = {"configs": {}, "exe_type_calls": [], "appid_calls": []}

    monkeypatch.setattr(backend, "find_windows_programs_ux", lambda *a, **k: list(state["configs"]))
    monkeypatch.setattr(backend, "load_game_config", lambda exe: state["configs"].get(exe))

    def fake_exe_type(exe):
        state["exe_type_calls"].append(exe)
        return "detected"

    def fake_appid(exe, fallback=True, manifest_cache=None):
        state["appid_calls"].append((exe, manifest_cache))
        return None

    monkeypatch.setattr(backend, "detect_exe_type", fake_exe_type)
    monkeypatch.setattr(backend, "detect_steam_appid", fake_appid)
    return state


def test_exe_type_present_dans_la_config_n_est_pas_re_detecte(harness):
    harness["configs"]["/g/a.exe"] = {"exe_type": "dx12"}

    result = backend.list_programs_ux()

    assert result[0]["exe_type"] == "dx12"
    assert harness["exe_type_calls"] == []


def test_exe_type_absent_est_detecte_une_fois(harness):
    harness["configs"]["/g/a.exe"] = {}

    result = backend.list_programs_ux()

    assert result[0]["exe_type"] == "detected"
    assert harness["exe_type_calls"] == ["/g/a.exe"]


def test_exe_type_present_mais_none_est_conserve_comme_avant(harness):
    # Ancienne sémantique de dict.get(clé, défaut) : clé présente => valeur
    # présente, même None. Pas de redétection.
    harness["configs"]["/g/a.exe"] = {"exe_type": None}

    assert backend.list_programs_ux()[0]["exe_type"] is None
    assert harness["exe_type_calls"] == []


def test_jeu_sans_config_est_detecte(harness, monkeypatch):
    monkeypatch.setattr(backend, "find_windows_programs_ux", lambda *a, **k: ["/g/new.exe"])

    result = backend.list_programs_ux()

    assert result[0]["exe_type"] == "detected"


def test_detection_par_jeu_selon_la_config(harness):
    harness["configs"].update({
        "/g/a.exe": {"exe_type": "dx11"},
        "/g/b.exe": {},
        "/g/c.exe": {"exe_type": "legacy"},
        "/g/d.exe": {},
    })

    backend.list_programs_ux()

    assert sorted(harness["exe_type_calls"]) == ["/g/b.exe", "/g/d.exe"]


def test_app_id_en_config_evite_la_detection_steam(harness):
    harness["configs"]["/g/a.exe"] = {"app_id": "42"}

    assert backend.list_programs_ux()[0]["app_id"] == "42"
    assert harness["appid_calls"] == []


def test_un_seul_cache_de_manifestes_partage_entre_les_jeux(harness):
    harness["configs"].update({f"/g/{i}.exe": {} for i in range(5)})

    backend.list_programs_ux()

    caches = [cache for _, cache in harness["appid_calls"]]
    assert len(caches) == 5
    assert all(c is caches[0] and c is not None for c in caches)


def test_chaque_appel_recree_un_cache_neuf(harness):
    harness["configs"]["/g/a.exe"] = {}

    backend.list_programs_ux()
    backend.list_programs_ux()

    first, second = harness["appid_calls"][0][1], harness["appid_calls"][1][1]
    assert first is not second


def test_champs_du_resultat_inchanges(harness):
    harness["configs"]["/g/a.exe"] = {"name": "A", "exe_type": "dx11", "cover_image": "/c/x.png"}

    game = backend.list_programs_ux()[0]

    assert set(game) == {
        "name", "path", "config_path", "exe_type", "proton", "prefix", "features",
        "env", "favorite", "cover_image", "playtime", "badges", "app_id", "protondb",
    }
    assert game["cover_image"] == "/c/x.png"
