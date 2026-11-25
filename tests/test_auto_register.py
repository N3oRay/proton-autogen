"""`proton-autogen game.exe` crée la config du programme si elle n'existe pas.

Ces tests n'écrivent que dans un dossier temporaire : aucune config, aucun
préfixe ni aucun Proton réels ne sont utilisés.
"""

import json
import os

import pytest

from proton_autogen import auto_register, backend, core, editor, loader

pytestmark = pytest.mark.unit


@pytest.fixture
def env(tmp_path, monkeypatch):
    games = tmp_path / "games"
    prefixes = tmp_path / "env"

    for module in (loader, editor):
        monkeypatch.setattr(module, "CONFIG_DIR", str(games))
    for module in (core, editor):
        monkeypatch.setattr(module, "load_prefix_dir", lambda: str(prefixes))
    monkeypatch.setattr(editor, "find_proton", lambda: {"path": "/fake/GE-Proton"})
    monkeypatch.setattr(editor, "detect_exe_type", lambda _p: "dx11")

    exe = tmp_path / "Mon Jeu" / "Game.exe"
    exe.parent.mkdir()
    exe.write_bytes(b"MZ")
    return {"exe": str(exe), "games": games, "prefixes": prefixes}


def _configs(env):
    return sorted(env["games"].glob("*.json")) if env["games"].exists() else []


def test_cree_la_config_au_premier_lancement(env):
    config = auto_register.ensure_game_config(env["exe"], "main")

    assert config is not None
    files = _configs(env)
    assert len(files) == 1
    saved = json.loads(files[0].read_text())
    assert saved["path"] == env["exe"]
    assert saved["name"] == "Game.exe"
    assert saved["proton"] == "/fake/GE-Proton"
    assert saved["id"] == files[0].stem


def test_le_prefixe_enregistre_est_celui_du_lancement(env):
    config = auto_register.ensure_game_config(env["exe"], "main")
    assert config["prefix"] == {"name": "main", "path": str(env["prefixes"] / "main")}


@pytest.mark.parametrize("mode, name", [("shared", "shared"), ("custom", "custom")])
def test_prefixes_nommes(env, mode, name):
    config = auto_register.ensure_game_config(env["exe"], mode)
    assert config["prefix"]["name"] == name
    assert config["prefix"]["path"] == str(env["prefixes"] / name)


def test_prefixe_automatique_par_jeu(env):
    config = auto_register.ensure_game_config(env["exe"], "auto")
    name = config["prefix"]["name"]
    assert name.startswith("Game-")
    assert config["prefix"]["path"] == str(env["prefixes"] / name)
    # le nom enregistré redonne le même dossier au lancement suivant
    assert core.get_prefix_path(name, env["exe"]) == config["prefix"]["path"]


def test_une_config_existante_n_est_jamais_reecrite(env):
    path, _gid = loader.get_game_config_path(env["exe"])
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps({"id": "x", "path": env["exe"], "name": "Perso",
                                "prefix": {"name": "mon-prefixe"}}))
    before = path.read_text()

    config = auto_register.ensure_game_config(env["exe"], "main")

    assert config["name"] == "Perso"
    assert path.read_text() == before


@pytest.mark.parametrize("name", ["setup.msi", "run.bat", "Raccourci.lnk", "UPPER.EXE"])
def test_enregistre_exe_msi_bat_lnk(env, tmp_path, name):
    other = tmp_path / name
    other.write_bytes(b"x")
    assert auto_register.ensure_game_config(str(other), "main") is not None
    assert len(_configs(env)) == 1


def test_ignore_les_autres_types_et_les_fichiers_absents(env, tmp_path):
    other = tmp_path / "notes.txt"
    other.write_bytes(b"x")
    assert auto_register.ensure_game_config(str(other), "main") is None
    assert auto_register.ensure_game_config(str(tmp_path / "absent.exe"), "main") is None
    assert _configs(env) == []


def test_un_echec_de_l_ajout_ne_leve_pas(env, monkeypatch):
    def boom(*_a, **_k):
        raise RuntimeError("disque plein")

    monkeypatch.setattr(editor, "add_game_ux", boom)
    assert auto_register.ensure_game_config(env["exe"], "main") is None


# --- branchement dans backend.run ------------------------------------------

class _Stop(Exception):
    """Interrompt run() juste après l'étape de configuration."""


@pytest.fixture
def run_probe(monkeypatch):
    calls = []

    def fake_ensure(exe, prefix_mode):
        calls.append((exe, prefix_mode))
        return None

    def stop(*_a, **_k):
        raise _Stop

    monkeypatch.setattr(backend, "ensure_game_config", fake_ensure)
    monkeypatch.setattr(backend, "has_mangohud", lambda: False)
    monkeypatch.setattr(backend, "detect_system_info", stop)
    return calls


def test_run_sans_config_appelle_l_enregistrement(env, monkeypatch, run_probe):
    monkeypatch.setattr(backend, "load_game_config", lambda _p: None)
    with pytest.raises(_Stop):
        backend.run(env["exe"], "proton", "shared")
    assert run_probe == [(os.path.abspath(env["exe"]), "shared")]


def test_run_avec_config_n_enregistre_rien(env, monkeypatch, run_probe):
    monkeypatch.setattr(backend, "load_game_config", lambda _p: {"name": "x"})
    with pytest.raises(_Stop):
        backend.run(env["exe"])
    assert run_probe == []
