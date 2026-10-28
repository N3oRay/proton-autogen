"""Mode PRO : `proton-autogen game.exe --profile NOM` — sans lancer de jeu.

Avant correctif, la CLI plantait avec un NameError (le module `core` n'était pas
importé), et même après l'affectation le backend n'aurait pas vu le profil :
il en avait une copie figée à None.
"""

import json
import os
import runpy
import shutil
import subprocess
import sys

import pytest

from proton_autogen import backend, core

pytestmark = pytest.mark.unit

CLI = shutil.which("proton-autogen")
needs_cli = pytest.mark.skipif(CLI is None, reason="commande proton-autogen non installée")

PROFILE = {"name": "dx9dg", "base": "dx9dg", "env": {"PA_TEST_VAR": "1"}, "remove": ["PA_REMOVED"]}


@pytest.fixture
def home_with_profile(tmp_path, monkeypatch):
    profiles = tmp_path / ".config" / "proton-autogen" / "profiles"
    profiles.mkdir(parents=True)
    (profiles / "dx9dg.json").write_text(json.dumps(PROFILE), encoding="utf-8")
    monkeypatch.setenv("HOME", str(tmp_path))
    # Enregistre la valeur actuelle pour la restaurer après le test.
    monkeypatch.setattr(core, "USER_PROFILE", None)
    monkeypatch.setattr(core, "USER_PROFILE_DATA", None)
    return tmp_path


def _load_cli_namespace():
    """Exécute le script CLI sans déclencher main() (run_name != "__main__")."""
    return runpy.run_path(CLI, run_name="proton_autogen_cli")


def _run_main(monkeypatch, argv):
    namespace = _load_cli_namespace()
    calls = []

    def fake_run(exe, launch_mode, prefix_mode, *a, **k):
        calls.append({
            "exe": exe, "launch_mode": launch_mode, "prefix_mode": prefix_mode,
            "profile": core.USER_PROFILE, "data": core.USER_PROFILE_DATA,
            "backend_exe_type": backend._apply_profile_exe_type("detected"),
        })

    # run_path() renvoie une COPIE des globales : main() continue de lire les
    # siennes (main.__globals__), c'est donc là qu'il faut remplacer `run`.
    main = namespace["main"]
    monkeypatch.setitem(main.__globals__, "run", fake_run)
    monkeypatch.setattr(sys, "argv", ["proton-autogen", *argv])
    main()
    return calls


# --- le backend lit le profil À L'APPEL ------------------------------------

def test_sans_profil_le_type_detecte_est_conserve(monkeypatch):
    monkeypatch.setattr(core, "USER_PROFILE_DATA", None)
    assert backend._apply_profile_exe_type("dx11") == "dx11"


@pytest.mark.parametrize("data,expected", [
    ({"base": "dx9dg", "name": "autre"}, "dx9dg"),     # base prioritaire
    ({"name": "mon-profil"}, "mon-profil"),
    ({}, "dx11"),                                       # profil vide = pas de profil
])
def test_le_profil_impose_remplace_le_type_detecte(monkeypatch, data, expected):
    monkeypatch.setattr(core, "USER_PROFILE_DATA", data)
    assert backend._apply_profile_exe_type("dx11") == expected


def test_le_backend_voit_une_affectation_posterieure_a_son_import(monkeypatch):
    # Garde-fou : si quelqu'un réintroduit `from proton_autogen.core import
    # USER_PROFILE_DATA` dans backend, la valeur affectée après l'import par la
    # CLI redevient invisible.
    monkeypatch.setattr(core, "USER_PROFILE_DATA", None)
    assert backend._apply_profile_exe_type("dx11") == "dx11"

    core.USER_PROFILE_DATA = {"base": "dx9dg"}          # affectation tardive, comme la CLI

    assert backend._apply_profile_exe_type("dx11") == "dx9dg"


def test_backend_n_expose_plus_de_copie_figee_du_profil():
    assert not hasattr(backend, "USER_PROFILE")
    assert not hasattr(backend, "USER_PROFILE_DATA")


# --- la CLI affecte core ------------------------------------------------------

@needs_cli
def test_cli_affecte_le_profil_sur_core_puis_lance(home_with_profile, monkeypatch):
    calls = _run_main(monkeypatch, ["game.exe", "--profile", "dx9dg"])

    assert len(calls) == 1
    assert calls[0]["exe"] == "game.exe"
    assert calls[0]["profile"] == "dx9dg"
    assert calls[0]["data"] == PROFILE
    assert calls[0]["backend_exe_type"] == "dx9dg"      # le backend le voit aussi


@needs_cli
def test_cli_sans_profil_ne_touche_pas_a_core(home_with_profile, monkeypatch):
    calls = _run_main(monkeypatch, ["game.exe"])

    assert calls[0]["profile"] is None
    assert calls[0]["data"] is None
    assert calls[0]["backend_exe_type"] == "detected"


@needs_cli
def test_cli_options_de_lancement_conservees_avec_profil(home_with_profile, monkeypatch):
    calls = _run_main(monkeypatch, ["game.exe", "--profile", "dx9dg", "--call", "--ps"])

    assert calls[0]["launch_mode"] == "proton-call"
    assert calls[0]["prefix_mode"] == "shared"


@needs_cli
def test_cli_profil_introuvable_sort_proprement(home_with_profile, monkeypatch):
    with pytest.raises(SystemExit) as exc:
        _run_main(monkeypatch, ["game.exe", "--profile", "inexistant"])

    assert exc.value.code == 1


@needs_cli
def test_cli_profil_sans_nom_sort_proprement(home_with_profile, monkeypatch):
    with pytest.raises(SystemExit) as exc:
        _run_main(monkeypatch, ["game.exe", "--profile"])

    assert exc.value.code == 1


# --- le profil est réellement appliqué à l'environnement du jeu ---------------

def test_apply_user_profile_ajoute_et_retire_des_variables():
    env = core.apply_user_profile({"PA_REMOVED": "x", "KEEP": "y"}, PROFILE)

    assert env["PA_TEST_VAR"] == "1"
    assert "PA_REMOVED" not in env
    assert env["KEEP"] == "y"


def test_base_env_applique_le_profil_affecte_sur_core(monkeypatch):
    monkeypatch.setattr(core, "USER_PROFILE_DATA", PROFILE)

    env = core.base_env(exe_path="/g/game.exe", exe_type="dx11",
                        prefix_path="/tmp/prefix", proton_dir="/tmp/proton")

    assert env["PA_TEST_VAR"] == "1"


# --- exécution réelle de la CLI (sous-processus) ------------------------------

@needs_cli
def test_cli_reelle_avec_profil_n_a_plus_de_nameerror(home_with_profile):
    env = {**os.environ, "HOME": str(home_with_profile)}

    result = subprocess.run(
        [sys.executable, CLI, str(home_with_profile / "absent.exe"), "--profile", "dx9dg"],
        env=env, capture_output=True, text=True, timeout=60,
    )

    assert "NameError" not in result.stderr
    assert "Traceback" not in result.stderr
