"""Tests de proton_autogen.ux.mini_settings — purs, sans GTK.

Le fichier de config est redirigé vers un dossier temporaire : aucun test
ne touche à ~/.config.
"""

import pytest

from proton_autogen.ux import mini_settings as ms

pytestmark = pytest.mark.unit

_SESSION_VARS = (
    "XDG_SESSION_TYPE", "XDG_CURRENT_DESKTOP", "XDG_SESSION_DESKTOP",
    "DESKTOP_SESSION", "HYPRLAND_INSTANCE_SIGNATURE",
    "PROTON_AUTOGEN_FORCE_MINIMIZE",
)


@pytest.fixture(autouse=True)
def isolated(monkeypatch, tmp_path):
    monkeypatch.setattr(ms, "CONFIG_PATH", tmp_path / "ux.conf")
    for var in _SESSION_VARS:
        monkeypatch.delenv(var, raising=False)


# --- détection de la session ----------------------------------------------

def test_x11_est_supporte(monkeypatch):
    monkeypatch.setenv("XDG_SESSION_TYPE", "x11")
    assert ms.detect_minimize_support() == (True, "x11")


@pytest.mark.parametrize("desktop", ["KDE", "GNOME", "ubuntu:GNOME", "XFCE", "Budgie:GNOME"])
def test_wayland_bureaux_complets_supportes(monkeypatch, desktop):
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    monkeypatch.setenv("XDG_CURRENT_DESKTOP", desktop)
    assert ms.detect_minimize_support()[0] is True


@pytest.mark.parametrize("desktop", ["sway", "river", "wayfire", "labwc"])
def test_wayland_compositeurs_tiling_non_supportes(monkeypatch, desktop):
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    monkeypatch.setenv("XDG_CURRENT_DESKTOP", desktop)
    supported, reason = ms.detect_minimize_support()
    assert supported is False
    assert desktop in reason


def test_wayland_bureau_inconnu_non_supporte(monkeypatch):
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    monkeypatch.setenv("XDG_CURRENT_DESKTOP", "MonCompositeur")
    assert ms.detect_minimize_support()[0] is False


def test_hyprland_prioritaire_meme_sous_x11(monkeypatch):
    monkeypatch.setenv("XDG_SESSION_TYPE", "x11")
    monkeypatch.setenv("HYPRLAND_INSTANCE_SIGNATURE", "abc")
    assert ms.detect_minimize_support()[0] is False


def test_session_inconnue_prudente():
    assert ms.detect_minimize_support()[0] is False


def test_detect_session_info_normalise_en_minuscules(monkeypatch):
    monkeypatch.setenv("XDG_SESSION_TYPE", " Wayland ")
    monkeypatch.setenv("XDG_SESSION_DESKTOP", "KDE")
    assert ms._detect_session_info() == ("wayland", "kde")


# --- préférences ----------------------------------------------------------

def test_mini_mode_actif_par_defaut_sans_fichier():
    assert ms.load_mini_mode_enabled() is True
    assert ms.load_mini_mode_enabled(default=False) is False


def test_mini_mode_aller_retour():
    ms.save_mini_mode_enabled(False)
    assert ms.load_mini_mode_enabled() is False
    ms.save_mini_mode_enabled(True)
    assert ms.load_mini_mode_enabled() is True


def test_mini_mode_fichier_corrompu_renvoie_le_defaut(tmp_path):
    ms.CONFIG_PATH.write_text("[mini\nmini_mode = ???", encoding="utf-8")
    assert ms.load_mini_mode_enabled() is True


def test_minimize_mode_defaut_et_aller_retour():
    assert ms.load_minimize_mode() == "auto"
    ms.save_minimize_mode("off")
    assert ms.load_minimize_mode() == "off"


def test_minimize_mode_refuse_une_valeur_invalide():
    with pytest.raises(ValueError):
        ms.save_minimize_mode("peut-etre")


def test_minimize_mode_valeur_inconnue_dans_le_fichier_revient_a_auto():
    ms.CONFIG_PATH.write_text("[mini]\nminimize = bizarre\n", encoding="utf-8")
    assert ms.load_minimize_mode() == "auto"


def test_les_deux_preferences_coexistent_dans_le_meme_fichier():
    ms.save_mini_mode_enabled(False)
    ms.save_minimize_mode("on")
    assert ms.load_mini_mode_enabled() is False
    assert ms.load_minimize_mode() == "on"


def test_save_conserve_les_autres_sections():
    ms.CONFIG_PATH.write_text("[theme]\nname = dark\n", encoding="utf-8")
    ms.save_mini_mode_enabled(False)
    content = ms.CONFIG_PATH.read_text(encoding="utf-8")
    assert "[theme]" in content and "name = dark" in content


# --- décision finale ------------------------------------------------------

@pytest.mark.parametrize("value,expected", [
    ("1", True), ("true", True), ("yes", True),
    ("0", False), ("false", False), ("NO", False), ("off", False),
])
def test_variable_d_environnement_prioritaire(monkeypatch, value, expected):
    monkeypatch.setenv("PROTON_AUTOGEN_FORCE_MINIMIZE", value)
    ms.save_minimize_mode("off" if expected else "on")   # doit être ignoré
    assert ms.resolve_minimize_enabled()[0] is expected


def test_preference_on_force_meme_sur_compositeur_tiling(monkeypatch):
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    monkeypatch.setenv("XDG_CURRENT_DESKTOP", "sway")
    ms.save_minimize_mode("on")
    assert ms.resolve_minimize_enabled()[0] is True


def test_preference_off_desactive_meme_sous_x11(monkeypatch):
    monkeypatch.setenv("XDG_SESSION_TYPE", "x11")
    ms.save_minimize_mode("off")
    assert ms.resolve_minimize_enabled()[0] is False


def test_mode_auto_suit_la_detection(monkeypatch):
    monkeypatch.setenv("XDG_SESSION_TYPE", "x11")
    assert ms.resolve_minimize_enabled() == ms.detect_minimize_support()
