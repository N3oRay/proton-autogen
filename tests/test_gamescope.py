import subprocess

import pytest

from proton_autogen.utils import gamescope as gs
from proton_autogen.utils.gamescope import (
    DEFAULT_GAMESCOPE_HEIGHT,
    DEFAULT_GAMESCOPE_INTERNAL_HEIGHT,
    DEFAULT_GAMESCOPE_INTERNAL_WIDTH,
    DEFAULT_GAMESCOPE_WIDTH,
    _ensure_gamescope_legacy_aliases,
    _parse_resolution,
    apply_gamescope,
    build_gamescope_command,
    clear_gamescope_env,
    detect_screen_resolution,
    gamescope_enabled,
    init_gamescope_env,
)

MODULE = "proton_autogen.utils.gamescope"


# ---------------------------------
# Fixtures
# ---------------------------------

@pytest.fixture
def xrandr_available(monkeypatch):
    """xrandr présent, hors Flatpak : isole les tests de la machine hôte."""
    monkeypatch.setattr(f"{MODULE}.has_xrandr", lambda: True)
    monkeypatch.setattr(f"{MODULE}.is_flatpak", lambda: False)


@pytest.fixture
def gamescope_available(monkeypatch):
    monkeypatch.setattr(f"{MODULE}.has_gamescope", lambda: True)


def _fake_run(stdout="", returncode=0):
    result = subprocess.CompletedProcess(
        args=[], returncode=returncode, stdout=stdout, stderr=""
    )
    return lambda *a, **kw: result


# ---------------------------------
# detect_screen_resolution
# ---------------------------------

def test_detect_screen_resolution_primary_monitor(
    monkeypatch, xrandr_available
):
    # Résolution volontairement différente du fallback (1920x1080) :
    # le test échoue si la détection retombe sur la valeur par défaut.
    fake_output = """
Screen 0: minimum 320 x 200, current 4480 x 1440
DP-1 connected primary 2560x1440+0+0
   2560x1440    143.97*+ 119.99
   1920x1080     60.00
HDMI-1 connected 1920x1080+2560+0
   1920x1080     60.00*+
"""
    monkeypatch.setattr(subprocess, "run", _fake_run(fake_output))

    assert detect_screen_resolution() == (2560, 1440)


def test_detect_screen_resolution_no_xrandr_binary(monkeypatch):
    """has_xrandr() négatif -> fallback sans exécuter xrandr."""
    monkeypatch.setattr(f"{MODULE}.has_xrandr", lambda: False)

    def must_not_run(*args, **kwargs):
        raise AssertionError("xrandr ne doit pas être exécuté")

    monkeypatch.setattr(subprocess, "run", must_not_run)

    assert detect_screen_resolution() == (
        DEFAULT_GAMESCOPE_WIDTH,
        DEFAULT_GAMESCOPE_HEIGHT,
    )


def test_detect_screen_resolution_xrandr_file_not_found(
    monkeypatch, xrandr_available
):
    """xrandr annoncé présent mais introuvable à l'exécution -> fallback."""

    def raise_error(*args, **kwargs):
        raise FileNotFoundError

    monkeypatch.setattr(subprocess, "run", raise_error)

    assert detect_screen_resolution() == (1920, 1080)


def test_detect_screen_resolution_xrandr_fails(monkeypatch, xrandr_available):
    def raise_error(*args, **kwargs):
        raise subprocess.CalledProcessError(1, "xrandr", stderr="boom")

    monkeypatch.setattr(subprocess, "run", raise_error)

    assert detect_screen_resolution() == (1920, 1080)


def test_detect_screen_resolution_invalid_output(
    monkeypatch, xrandr_available
):
    monkeypatch.setattr(subprocess, "run", _fake_run("invalid"))

    assert detect_screen_resolution() == (1920, 1080)


def test_detect_screen_resolution_flatpak_uses_host(monkeypatch):
    monkeypatch.setattr(f"{MODULE}.has_xrandr", lambda: True)
    monkeypatch.setattr(f"{MODULE}.is_flatpak", lambda: True)

    captured = {}

    def fake_run(command, **kwargs):
        captured["command"] = command
        return subprocess.CompletedProcess(
            args=command,
            returncode=0,
            stdout="   3840x2160     60.00*+\n",
            stderr="",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)

    assert detect_screen_resolution() == (3840, 2160)
    assert captured["command"] == [
        "flatpak-spawn", "--host", "xrandr", "--current",
    ]


# ---------------------------------
# apply_gamescope
# ---------------------------------

def test_apply_gamescope_auto_resolution(monkeypatch, gamescope_available):
    """Mode par défaut « output » : la résolution détectée devient -W/-H."""
    monkeypatch.setattr(
        f"{MODULE}.detect_screen_resolution", lambda: (1920, 1200)
    )

    result = apply_gamescope({}, enabled=True)

    assert result["USE_GAMESCOPE"] == "1"
    assert result["GAMESCOPE_OUTPUT_WIDTH"] == "1920"
    assert result["GAMESCOPE_OUTPUT_HEIGHT"] == "1200"
    # Aucune résolution interne en mode « output » (pas de -w/-h).
    assert "GAMESCOPE_INTERNAL_WIDTH" not in result
    assert "GAMESCOPE_INTERNAL_HEIGHT" not in result
    # Les anciennes variables ne sont plus produites.
    assert "GAMESCOPE_WIDTH" not in result
    assert "GAMESCOPE_HEIGHT" not in result


def test_apply_gamescope_explicit_size_skips_detection(
    monkeypatch, gamescope_available
):
    def must_not_detect():
        raise AssertionError("la détection ne doit pas être appelée")

    monkeypatch.setattr(f"{MODULE}.detect_screen_resolution", must_not_detect)

    result = apply_gamescope(
        {}, enabled=True, width=2560, height=1440, mode="output"
    )

    assert result["GAMESCOPE_OUTPUT_WIDTH"] == "2560"
    assert result["GAMESCOPE_OUTPUT_HEIGHT"] == "1440"


def test_apply_gamescope_internal_mode_uses_defaults(
    monkeypatch, gamescope_available
):
    monkeypatch.setattr(
        f"{MODULE}.detect_screen_resolution", lambda: (1920, 1080)
    )

    result = apply_gamescope({}, enabled=True, mode="internal")

    assert result["GAMESCOPE_INTERNAL_WIDTH"] == str(
        DEFAULT_GAMESCOPE_INTERNAL_WIDTH
    )
    assert result["GAMESCOPE_INTERNAL_HEIGHT"] == str(
        DEFAULT_GAMESCOPE_INTERNAL_HEIGHT
    )
    assert "GAMESCOPE_OUTPUT_WIDTH" not in result
    assert "GAMESCOPE_OUTPUT_HEIGHT" not in result


def test_apply_gamescope_custom_mode(monkeypatch, gamescope_available):
    """Interne choisie, sortie automatique (détectée)."""
    monkeypatch.setattr(
        f"{MODULE}.detect_screen_resolution", lambda: (1920, 1080)
    )

    result = apply_gamescope(
        {},
        enabled=True,
        internal_width=1280,
        internal_height=800,
        mode="custom",
    )

    assert result["GAMESCOPE_INTERNAL_WIDTH"] == "1280"
    assert result["GAMESCOPE_INTERNAL_HEIGHT"] == "800"
    assert result["GAMESCOPE_OUTPUT_WIDTH"] == "1920"
    assert result["GAMESCOPE_OUTPUT_HEIGHT"] == "1080"


def test_apply_gamescope_custom_mode_both_explicit(gamescope_available):
    result = apply_gamescope(
        {},
        enabled=True,
        width=1920,
        height=1080,
        internal_width=1280,
        internal_height=720,
        output_width=3840,
        output_height=2160,
        mode="custom",
    )

    assert result["GAMESCOPE_INTERNAL_WIDTH"] == "1280"
    assert result["GAMESCOPE_INTERNAL_HEIGHT"] == "720"
    assert result["GAMESCOPE_OUTPUT_WIDTH"] == "3840"
    assert result["GAMESCOPE_OUTPUT_HEIGHT"] == "2160"


def test_apply_gamescope_options(gamescope_available):
    result = apply_gamescope(
        {},
        enabled=True,
        width=1920,
        height=1080,
        refresh=144,
        fullscreen=False,
        cursor=False,
    )

    assert result["GAMESCOPE_REFRESH"] == "144"
    assert result["GAMESCOPE_FULLSCREEN"] == "0"
    assert result["GAMESCOPE_CURSOR"] == "0"


def test_apply_gamescope_replaces_previous_values(gamescope_available):
    env = {
        "USE_GAMESCOPE": "1",
        "GAMESCOPE_INTERNAL_WIDTH": "800",
        "GAMESCOPE_INTERNAL_HEIGHT": "600",
        "OTHER_VARIABLE": "keep",
    }

    result = apply_gamescope(
        env, enabled=True, width=1920, height=1080, mode="output"
    )

    # Les anciennes valeurs internes ne fuient pas dans la nouvelle config.
    assert "GAMESCOPE_INTERNAL_WIDTH" not in result
    assert "GAMESCOPE_INTERNAL_HEIGHT" not in result
    assert result["GAMESCOPE_OUTPUT_WIDTH"] == "1920"
    assert result["OTHER_VARIABLE"] == "keep"


def test_apply_gamescope_unavailable(monkeypatch):
    monkeypatch.setattr(f"{MODULE}.has_gamescope", lambda: False)

    result = apply_gamescope(
        {"GAMESCOPE_OUTPUT_WIDTH": "1920"}, enabled=True
    )

    assert not gamescope_enabled(result)
    assert "GAMESCOPE_OUTPUT_WIDTH" not in result


def test_apply_gamescope_disabled_cleans_env():

    env = {
        "USE_GAMESCOPE": "1",
        "GAMESCOPE_WIDTH": "1920",
        "GAMESCOPE_HEIGHT": "1200",
        "GAMESCOPE_INTERNAL_WIDTH": "1280",
        "GAMESCOPE_INTERNAL_HEIGHT": "720",
        "GAMESCOPE_OUTPUT_WIDTH": "1920",
        "GAMESCOPE_OUTPUT_HEIGHT": "1200",
        "OTHER_VARIABLE": "keep",
    }

    result = apply_gamescope(env, enabled=False)

    assert "USE_GAMESCOPE" not in result
    for key in (
        "GAMESCOPE_WIDTH",
        "GAMESCOPE_HEIGHT",
        "GAMESCOPE_INTERNAL_WIDTH",
        "GAMESCOPE_INTERNAL_HEIGHT",
        "GAMESCOPE_OUTPUT_WIDTH",
        "GAMESCOPE_OUTPUT_HEIGHT",
    ):
        assert key not in result
    assert result["OTHER_VARIABLE"] == "keep"


# ---------------------------------
# init / clear / enabled
# ---------------------------------

def test_init_gamescope_env_disabled():
    assert init_gamescope_env(enabled=False) == {"USE_GAMESCOPE": "0"}


def test_init_gamescope_env_output_mode():
    env = init_gamescope_env(
        enabled=True, width=1920, height=1080, refresh=60
    )

    assert env["USE_GAMESCOPE"] == "1"
    assert env["GAMESCOPE_OUTPUT_WIDTH"] == "1920"
    assert env["GAMESCOPE_OUTPUT_HEIGHT"] == "1080"
    assert env["GAMESCOPE_REFRESH"] == "60"
    assert env["GAMESCOPE_FULLSCREEN"] == "1"
    assert env["GAMESCOPE_CURSOR"] == "1"
    assert "GAMESCOPE_INTERNAL_WIDTH" not in env


def test_init_gamescope_env_custom_mode():
    env = init_gamescope_env(
        enabled=True,
        internal_width=1280,
        internal_height=720,
        output_width=1920,
        output_height=1080,
        mode="custom",
    )

    assert env["GAMESCOPE_INTERNAL_WIDTH"] == "1280"
    assert env["GAMESCOPE_INTERNAL_HEIGHT"] == "720"
    assert env["GAMESCOPE_OUTPUT_WIDTH"] == "1920"
    assert env["GAMESCOPE_OUTPUT_HEIGHT"] == "1080"


def test_clear_gamescope_env_keeps_other_variables():
    env = {
        "USE_GAMESCOPE": "1",
        "GAMESCOPE_INTERNAL_WIDTH": "1280",
        "GAMESCOPE_OUTPUT_WIDTH": "1920",
        "OTHER_VARIABLE": "keep",
    }

    clear_gamescope_env(env)

    assert env == {"OTHER_VARIABLE": "keep"}


def test_gamescope_enabled():
    assert gamescope_enabled({"USE_GAMESCOPE": "1"})
    assert not gamescope_enabled({"USE_GAMESCOPE": "0"})
    assert not gamescope_enabled({})


def test_legacy_aliases_map_to_new_names():
    env = {
        "GAMESCOPE_WIDTH": "1280",
        "GAMESCOPE_HEIGHT": "720",
        "GAMESCOPE_NESTED_WIDTH": "1920",
        "GAMESCOPE_NESTED_HEIGHT": "1080",
    }

    _ensure_gamescope_legacy_aliases(env)

    assert env["GAMESCOPE_INTERNAL_WIDTH"] == "1280"
    assert env["GAMESCOPE_INTERNAL_HEIGHT"] == "720"
    assert env["GAMESCOPE_OUTPUT_WIDTH"] == "1920"
    assert env["GAMESCOPE_OUTPUT_HEIGHT"] == "1080"


# ---------------------------------
# build_gamescope_command
# ---------------------------------

def test_build_command_disabled():
    assert build_gamescope_command({"USE_GAMESCOPE": "0"}) == []
    assert build_gamescope_command({}) == []


def test_build_command_output_only():
    env = init_gamescope_env(
        enabled=True, width=1920, height=1080, mode="output"
    )

    command = build_gamescope_command(env)

    assert command == [
        "gamescope",
        "-W", "1920", "-H", "1080",
        "--fullscreen",
        "--force-grab-cursor",
        "--",
    ]
    assert "-w" not in command
    assert "-h" not in command


def test_build_command_custom_full():
    env = init_gamescope_env(
        enabled=True,
        refresh=60,
        internal_width=1280,
        internal_height=720,
        output_width=1920,
        output_height=1080,
        mode="custom",
    )
    env["GAMESCOPE_BORDERLESS"] = "1"

    assert build_gamescope_command(env) == [
        "gamescope",
        "-W", "1920", "-H", "1080",
        "-w", "1280", "-h", "720",
        "-r", "60",
        "--fullscreen",
        "--force-grab-cursor",
        "--borderless",
        "--",
    ]


def test_build_command_without_fullscreen_nor_cursor():
    env = init_gamescope_env(
        enabled=True,
        width=1920,
        height=1080,
        fullscreen=False,
        cursor=False,
    )

    command = build_gamescope_command(env)

    assert "--fullscreen" not in command
    assert "--force-grab-cursor" not in command
    assert command[0] == "gamescope"
    assert command[-1] == "--"


def test_build_command_legacy_names():
    env = {
        "USE_GAMESCOPE": "1",
        "GAMESCOPE_NESTED_WIDTH": "1920",
        "GAMESCOPE_NESTED_HEIGHT": "1080",
        "GAMESCOPE_WIDTH": "1280",
        "GAMESCOPE_HEIGHT": "720",
    }

    assert build_gamescope_command(env) == [
        "gamescope",
        "-W", "1920", "-H", "1080",
        "-w", "1280", "-h", "720",
        "--",
    ]


# ---------------------------------
# _parse_resolution
# ---------------------------------

@pytest.mark.parametrize(
    "value, expected",
    [
        ("1920x1080", (1920, 1080)),
        (" 1280X800 ", (1280, 800)),
        ((1600, 900), (1600, 900)),
        ([1366, 768], (1366, 768)),
        ("auto", (111, 222)),
        ("", (111, 222)),
        (None, (111, 222)),
        ("n'importe quoi", (111, 222)),
        ((1280, "x"), (111, 222)),
    ],
)
def test_parse_resolution(value, expected):
    assert _parse_resolution(value, 111, 222) == expected
