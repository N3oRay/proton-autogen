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


# ---------------------------------
# Options : upscaling FSR, limiteur de FPS, capture du curseur
# ---------------------------------

from proton_autogen.core import (  # noqa: E402
    _apply_gamescope_features,
    _as_bool,
    _parse_gamescope_fps_limit,
)


@pytest.fixture
def screen_2560(monkeypatch, gamescope_available):
    monkeypatch.setattr(
        f"{MODULE}.detect_screen_resolution", lambda: (2560, 1440)
    )


def _command_from_features(features):
    env = _apply_gamescope_features({}, True, features)
    return build_gamescope_command(env)


def test_init_gamescope_env_fsr_flag():
    assert "GAMESCOPE_FSR" not in init_gamescope_env(
        enabled=True, width=1920, height=1080
    )
    assert init_gamescope_env(
        enabled=True, width=1920, height=1080, fsr=True
    )["GAMESCOPE_FSR"] == "1"


def test_clear_gamescope_env_removes_fsr():
    env = {"GAMESCOPE_FSR": "1", "OTHER_VARIABLE": "keep"}

    clear_gamescope_env(env)

    assert env == {"OTHER_VARIABLE": "keep"}


def test_apply_gamescope_passes_fsr_and_refresh(gamescope_available):
    result = apply_gamescope(
        {}, enabled=True, width=1920, height=1080, refresh=75, fsr=True
    )

    assert result["GAMESCOPE_FSR"] == "1"
    assert result["GAMESCOPE_REFRESH"] == "75"


def test_build_command_fsr_and_refresh_order():
    env = init_gamescope_env(
        enabled=True,
        refresh=60,
        internal_width=1280,
        internal_height=720,
        output_width=1920,
        output_height=1080,
        mode="custom",
        fsr=True,
    )

    assert build_gamescope_command(env) == [
        "gamescope",
        "-W", "1920", "-H", "1080",
        "-w", "1280", "-h", "720",
        "-r", "60",
        "-F", "fsr",
        "--fullscreen",
        "--force-grab-cursor",
        "--",
    ]


def test_build_command_without_fsr_has_no_filter():
    env = init_gamescope_env(enabled=True, width=1920, height=1080)

    assert "-F" not in build_gamescope_command(env)


def test_features_defaults_keep_historical_behaviour(screen_2560):
    """Config existante sans les nouvelles clés : comportement inchangé."""
    command = _command_from_features({})

    assert command == [
        "gamescope",
        "-W", "2560", "-H", "1440",
        "--fullscreen",
        "--force-grab-cursor",
        "--",
    ]


def test_features_fsr_and_fps_limit(screen_2560):
    command = _command_from_features(
        {
            "gamescope_internal_resolution": "1280x720",
            "gamescope_fsr": True,
            "gamescope_fps_limit": 60,
        }
    )

    assert command == [
        "gamescope",
        "-W", "2560", "-H", "1440",
        "-w", "1280", "-h", "720",
        "-r", "60",
        "-F", "fsr",
        "--fullscreen",
        "--force-grab-cursor",
        "--",
    ]


def test_features_force_grab_cursor_disabled(screen_2560):
    command = _command_from_features({"gamescope_force_grab_cursor": False})

    assert "--force-grab-cursor" not in command
    assert "--fullscreen" in command


@pytest.mark.parametrize("value", [0, None, "", "abc", -5, "0"])
def test_features_fps_limit_disabled_or_invalid(screen_2560, value):
    assert "-r" not in _command_from_features({"gamescope_fps_limit": value})


def test_features_fps_limit_string_and_clamp(screen_2560):
    command = _command_from_features({"gamescope_fps_limit": "144"})
    assert command[command.index("-r") + 1] == "144"

    command = _command_from_features({"gamescope_fps_limit": 5000})
    assert command[command.index("-r") + 1] == "1000"


def test_features_disabled_gamescope_produces_nothing(screen_2560):
    env = _apply_gamescope_features(
        {}, False, {"gamescope_fsr": True, "gamescope_fps_limit": 60}
    )

    assert build_gamescope_command(env) == []


@pytest.mark.parametrize(
    "value, default, expected",
    [
        (True, False, True),
        (False, True, False),
        (1, False, True),
        (0, True, False),
        ("true", False, True),
        ("OFF", True, False),
        (" 1 ", False, True),
        (None, True, True),
        (None, False, False),
        ("peut-être", True, True),
    ],
)
def test_as_bool(value, default, expected):
    assert _as_bool(value, default) is expected


@pytest.mark.parametrize(
    "value, expected",
    [(60, 60), ("90", 90), (0, None), (-1, None), (None, None),
     ("x", None), (1, 1), (1000, 1000), (1001, 1000)],
)
def test_parse_gamescope_fps_limit(value, expected):
    assert _parse_gamescope_fps_limit(value) == expected


# ---------------------------------
# Options : NIS, scaler (integer / stretch), HDR, VRR, mangoapp
# ---------------------------------

def test_init_gamescope_env_new_flags():
    env = init_gamescope_env(
        enabled=True,
        width=1920,
        height=1080,
        nis=True,
        scaler="integer",
        hdr=True,
        adaptive_sync=True,
        mangoapp=True,
    )

    assert env["GAMESCOPE_NIS"] == "1"
    assert env["GAMESCOPE_SCALER"] == "integer"
    assert env["GAMESCOPE_HDR"] == "1"
    assert env["GAMESCOPE_ADAPTIVE_SYNC"] == "1"
    assert env["GAMESCOPE_MANGOAPP"] == "1"


def test_init_gamescope_env_new_flags_absent_by_default():
    env = init_gamescope_env(enabled=True, width=1920, height=1080)

    for key in (
        "GAMESCOPE_NIS",
        "GAMESCOPE_SCALER",
        "GAMESCOPE_HDR",
        "GAMESCOPE_ADAPTIVE_SYNC",
        "GAMESCOPE_MANGOAPP",
    ):
        assert key not in env


@pytest.mark.parametrize("scaler", [None, "", "auto", "AUTO", "bidon"])
def test_scaler_auto_or_invalid_adds_nothing(scaler):
    env = init_gamescope_env(
        enabled=True, width=1920, height=1080, scaler=scaler
    )

    assert "GAMESCOPE_SCALER" not in env
    assert "-S" not in build_gamescope_command(env)


@pytest.mark.parametrize("scaler", ["integer", "stretch", "fit", "fill"])
def test_scaler_values_reach_command(scaler):
    env = init_gamescope_env(
        enabled=True, width=1920, height=1080, scaler=scaler
    )

    command = build_gamescope_command(env)

    assert command[command.index("-S") + 1] == scaler


def test_clear_gamescope_env_removes_new_keys():
    env = {
        "GAMESCOPE_NIS": "1",
        "GAMESCOPE_SCALER": "integer",
        "GAMESCOPE_HDR": "1",
        "GAMESCOPE_ADAPTIVE_SYNC": "1",
        "GAMESCOPE_MANGOAPP": "1",
        "OTHER_VARIABLE": "keep",
    }

    clear_gamescope_env(env)

    assert env == {"OTHER_VARIABLE": "keep"}


def test_build_command_nis():
    env = init_gamescope_env(enabled=True, width=1920, height=1080, nis=True)
    command = build_gamescope_command(env)

    assert command[command.index("-F") + 1] == "nis"


def test_build_command_fsr_has_priority_over_nis():
    env = init_gamescope_env(
        enabled=True, width=1920, height=1080, fsr=True, nis=True
    )
    command = build_gamescope_command(env)

    assert command.count("-F") == 1
    assert command[command.index("-F") + 1] == "fsr"


def test_build_command_display_flags_order():
    env = init_gamescope_env(
        enabled=True,
        width=1920,
        height=1080,
        scaler="stretch",
        nis=True,
        adaptive_sync=True,
        hdr=True,
        mangoapp=True,
    )

    assert build_gamescope_command(env) == [
        "gamescope",
        "-W", "1920", "-H", "1080",
        "-S", "stretch",
        "-F", "nis",
        "--fullscreen",
        "--force-grab-cursor",
        "--adaptive-sync",
        "--hdr-enabled",
        "--mangoapp",
        "--",
    ]


def test_apply_gamescope_passes_new_flags(gamescope_available):
    result = apply_gamescope(
        {},
        enabled=True,
        width=1920,
        height=1080,
        nis=True,
        scaler="integer",
        hdr=True,
        adaptive_sync=True,
        mangoapp=True,
    )

    assert result["GAMESCOPE_NIS"] == "1"
    assert result["GAMESCOPE_SCALER"] == "integer"
    assert result["GAMESCOPE_HDR"] == "1"
    assert result["GAMESCOPE_ADAPTIVE_SYNC"] == "1"
    assert result["GAMESCOPE_MANGOAPP"] == "1"


# --- depuis la configuration du jeu (core) ---

def test_features_new_options_default_off(screen_2560):
    command = _command_from_features({})

    for flag in ("-S", "-F", "--adaptive-sync", "--hdr-enabled", "--mangoapp"):
        assert flag not in command


def test_features_nis(screen_2560):
    command = _command_from_features({"gamescope_nis": True})

    assert command[command.index("-F") + 1] == "nis"


def test_features_fsr_wins_over_nis(screen_2560):
    command = _command_from_features(
        {"gamescope_fsr": True, "gamescope_nis": True}
    )

    assert command.count("-F") == 1
    assert command[command.index("-F") + 1] == "fsr"


def test_features_integer_scaling(screen_2560):
    command = _command_from_features({"gamescope_integer_scaling": True})

    assert command[command.index("-S") + 1] == "integer"


def test_features_stretch(screen_2560):
    command = _command_from_features({"gamescope_stretch": True})

    assert command[command.index("-S") + 1] == "stretch"


def test_features_integer_wins_over_stretch(screen_2560):
    command = _command_from_features(
        {"gamescope_integer_scaling": True, "gamescope_stretch": True}
    )

    assert command.count("-S") == 1
    assert command[command.index("-S") + 1] == "integer"


def test_features_hdr_vrr_mangoapp(screen_2560):
    command = _command_from_features(
        {
            "gamescope_hdr": True,
            "gamescope_adaptive_sync": True,
            "gamescope_mangoapp": True,
        }
    )

    assert "--hdr-enabled" in command
    assert "--adaptive-sync" in command
    assert "--mangoapp" in command


def test_features_string_booleans_are_understood(screen_2560):
    command = _command_from_features(
        {"gamescope_hdr": "true", "gamescope_adaptive_sync": "false"}
    )

    assert "--hdr-enabled" in command
    assert "--adaptive-sync" not in command


def test_mangoapp_removes_mangohud_layer(screen_2560):
    """--mangoapp remplace la couche MangoHud : pas de double overlay."""
    env = _apply_gamescope_features(
        {"MANGOHUD": "1", "MANGOHUD_CONFIG": "fps_limit=60"},
        True,
        {"gamescope_mangoapp": True},
    )

    assert "MANGOHUD" not in env
    # La configuration reste disponible pour mangoapp.
    assert env["MANGOHUD_CONFIG"] == "fps_limit=60"


def test_mangohud_layer_kept_without_mangoapp(screen_2560):
    env = _apply_gamescope_features({"MANGOHUD": "1"}, True, {})

    assert env["MANGOHUD"] == "1"


def test_mangoapp_ignored_when_gamescope_disabled(screen_2560):
    env = _apply_gamescope_features(
        {"MANGOHUD": "1"}, False, {"gamescope_mangoapp": True}
    )

    assert env["MANGOHUD"] == "1"
    assert build_gamescope_command(env) == []


# --- exemples de configurations courantes ---

import shlex  # noqa: E402

_VALUE_FLAGS = {"-W", "-H", "-w", "-h", "-r", "-F", "-S"}
_LONG_FORMS = {"-f": "--fullscreen", "-b": "--borderless"}


def _flags(tokens):
    """Transforme une liste d'arguments en {drapeau: valeur | True}."""
    flags, i = {}, 0
    while i < len(tokens):
        token = _LONG_FORMS.get(tokens[i], tokens[i])
        if token in _VALUE_FLAGS and i + 1 < len(tokens):
            flags[token] = tokens[i + 1]
            i += 2
        else:
            flags[token] = True
            i += 1
    return flags


def _example_flags(example):
    """Arguments d'un exemple « gamescope ... -- %command% »."""
    tokens = shlex.split(example)[1:]
    return _flags(tokens[: tokens.index("--")])


COMMON_EXAMPLES = [
    (
        "gamescope -f -W 1920 -H 1080 -r 60 -- %command%",
        {"gamescope_output_resolution": "1920x1080", "gamescope_fps_limit": 60},
    ),
    (
        "gamescope -f -r 144 -- %command%",
        {"gamescope_fps_limit": 144},
    ),
    (
        "gamescope -f -r 120 -- %command%",
        {"gamescope_fps_limit": 120},
    ),
    (
        "gamescope -f -w 1280 -h 720 -W 1920 -H 1080 -F fsr -- %command%",
        {
            "gamescope_internal_resolution": "1280x720",
            "gamescope_output_resolution": "1920x1080",
            "gamescope_fsr": True,
        },
    ),
    (
        "gamescope -f -w 1280 -h 720 -W 1920 -H 1080 -F nis -- %command%",
        {
            "gamescope_internal_resolution": "1280x720",
            "gamescope_output_resolution": "1920x1080",
            "gamescope_nis": True,
        },
    ),
    (
        "gamescope -f --hdr-enabled --adaptive-sync -- %command%",
        {"gamescope_hdr": True, "gamescope_adaptive_sync": True},
    ),
    (
        "gamescope -f --mangoapp -- %command%",
        {"gamescope_mangoapp": True},
    ),
    (
        "gamescope -f -w 1920 -h 1080 -W 2560 -H 1440 -r 144 -F fsr "
        "--mangoapp -- %command%",
        {
            "gamescope_internal_resolution": "1920x1080",
            "gamescope_output_resolution": "2560x1440",
            "gamescope_fps_limit": 144,
            "gamescope_fsr": True,
            "gamescope_mangoapp": True,
        },
    ),
]


@pytest.mark.parametrize("example, features", COMMON_EXAMPLES)
def test_common_example_configurations(screen_2560, example, features):
    """
    La configuration produit les mêmes options que l'exemple.

    Écarts tolérés : -W/-H (résolution de l'écran, détectée) quand l'exemple
    ne les donne pas, et --force-grab-cursor (activé par défaut).
    """
    expected = _example_flags(example)
    actual = _flags(_command_from_features(features)[1:-1])

    for flag, value in expected.items():
        assert actual.get(flag) == value, f"{flag}: {actual.get(flag)!r}"

    allowed_extras = {"--force-grab-cursor"}
    if "-W" not in expected:
        allowed_extras |= {"-W", "-H"}

    assert set(actual) - set(expected) <= allowed_extras
