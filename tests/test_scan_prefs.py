"""Option « scan automatique des nouvelles applications » — sans GTK."""

import os
import subprocess
import sys
import textwrap

import pytest

from proton_autogen import backend
from proton_autogen.utils import scan_prefs
from proton_autogen.utils.scan_prefs import load_scan_options, save_scan_options

pytestmark = pytest.mark.unit


@pytest.fixture
def conf(tmp_path, monkeypatch):
    path = tmp_path / "proton-autogen-ux.conf"
    monkeypatch.setattr(scan_prefs, "CONFIG_PATH", path)
    return path


# --- préférence ---------------------------------------------------------------

def test_active_par_defaut_comportement_historique(conf):
    assert load_scan_options() is True


def test_aller_retour(conf):
    save_scan_options(False)
    assert load_scan_options() is False
    save_scan_options(True)
    assert load_scan_options() is True


def test_cle_persistee_inchangee(conf):
    # Les utilisateurs qui ont déjà sauvegardé l'option ont cette clé : ne pas la renommer.
    save_scan_options(False)
    content = conf.read_text(encoding="utf-8")
    assert "[ui]" in content and "scan_options = false" in content


def test_conserve_les_autres_reglages(conf):
    conf.write_text("[ui]\ntheme = gta\n[window]\nwidth = 900\n", encoding="utf-8")

    save_scan_options(False)

    content = conf.read_text(encoding="utf-8")
    assert "theme = gta" in content and "width = 900" in content
    assert load_scan_options() is False


def test_fichier_corrompu_garde_le_comportement_historique(conf):
    conf.write_text("[ui\nscan_options = ???", encoding="utf-8")
    assert load_scan_options() is True


def test_valeur_invalide_garde_le_comportement_historique(conf):
    conf.write_text("[ui]\nscan_options = peut-etre\n", encoding="utf-8")
    assert load_scan_options() is True


def test_ancien_import_ux_toujours_valide():
    from proton_autogen.ux import settings_scan

    assert settings_scan.load_scan_options is scan_prefs.load_scan_options
    assert settings_scan.save_scan_options is scan_prefs.save_scan_options


def test_meme_fichier_que_ux_themes(tmp_path):
    code = textwrap.dedent("""
        from proton_autogen.ux import themes
        from proton_autogen.utils import scan_prefs
        assert scan_prefs.CONFIG_PATH == themes.CONFIG_PATH, (scan_prefs.CONFIG_PATH, themes.CONFIG_PATH)
    """)
    result = subprocess.run([sys.executable, "-c", code], env={**os.environ, "HOME": str(tmp_path)},
                            capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stderr


# --- effet sur le chargement --------------------------------------------------

@pytest.fixture
def stubs(monkeypatch):
    state = {"search_calls": 0, "enabled": True}

    monkeypatch.setattr(backend, "load_registered_games_ux", lambda: ["/r/a.exe", "/r/b.exe"])

    def fake_search(root=None):
        state["search_calls"] += 1
        return ["/s/c.exe", "/r/a.exe"]

    monkeypatch.setattr(backend, "find_windows_programs_ux_search", fake_search)
    monkeypatch.setattr(backend, "load_scan_options", lambda *a, **k: state["enabled"])
    return state


def test_scan_actif_ajoute_les_nouvelles_apps_sans_doublon(stubs):
    assert backend.find_windows_programs_ux() == ["/r/a.exe", "/r/b.exe", "/s/c.exe"]
    assert stubs["search_calls"] == 1


def test_scan_desactive_ne_charge_que_les_apps_connues(stubs):
    stubs["enabled"] = False

    assert backend.find_windows_programs_ux() == ["/r/a.exe", "/r/b.exe"]
    assert stubs["search_calls"] == 0                  # aucune arborescence parcourue


def test_scan_reel_sur_une_arborescence(tmp_path, monkeypatch):
    for rel in ("Jeux/Game/game.exe", "Téléchargements/tool/tool.exe"):
        p = tmp_path / rel
        p.parent.mkdir(parents=True)
        p.write_bytes(b"MZ")

    monkeypatch.setattr(backend, "load_registered_games_ux", lambda: [])
    backend.find_windows_programs_ux_search.cache_clear()

    try:
        monkeypatch.setattr(backend, "load_scan_options", lambda *a, **k: True)
        found = {p[len(str(tmp_path)) + 1:] for p in backend.find_windows_programs_ux(tmp_path)}
        assert found == {"Jeux/Game/game.exe", "Téléchargements/tool/tool.exe"}

        monkeypatch.setattr(backend, "load_scan_options", lambda *a, **k: False)
        assert backend.find_windows_programs_ux(tmp_path) == []
    finally:
        backend.find_windows_programs_ux_search.cache_clear()


def test_apps_connues_toujours_presentes_scan_desactive(stubs):
    stubs["enabled"] = False
    assert set(backend.find_windows_programs_ux()) >= {"/r/a.exe", "/r/b.exe"}
