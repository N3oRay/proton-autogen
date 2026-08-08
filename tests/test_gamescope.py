import subprocess
import pytest

from proton_autogen.utils.gamescope import (
    detect_screen_resolution,
    apply_gamescope,
    init_gamescope_env,
    clear_gamescope_env,
    gamescope_enabled,
    build_gamescope_command,
)



# ---------------------------------
# detect_screen_resolution
# ---------------------------------

def test_detect_screen_resolution_primary_monitor(monkeypatch):

    fake_output = """
Screen 0: minimum 320 x 200, current 3600 x 1200
HDMI-A-0 connected 1920x1080+0+0
   1920x1080     59.95*+
"""

    result = subprocess.CompletedProcess(
        args=[],
        returncode=0,
        stdout=fake_output,
        stderr=""
    )

    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *a, **kw: result
    )

    assert detect_screen_resolution() == (1920, 1080)


def test_detect_screen_resolution_no_xrandr(monkeypatch):
    """
    xrandr absent -> fallback desktop.
    """

    def raise_error(*args, **kwargs):
        raise FileNotFoundError

    monkeypatch.setattr(
        subprocess,
        "run",
        raise_error
    )

    width, height = detect_screen_resolution()

    assert width == 1920
    assert height == 1080


def test_detect_screen_resolution_invalid_output(monkeypatch):

    result = subprocess.CompletedProcess(
        args=[],
        returncode=0,
        stdout="invalid",
        stderr=""
    )

    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *a, **kw: result
    )

    width, height = detect_screen_resolution()

    assert (width, height) == (1920, 1080)


def test_apply_gamescope_auto_resolution(monkeypatch):

    monkeypatch.setattr(
        "proton_autogen.utils.gamescope.has_gamescope",
        lambda: True
    )

    monkeypatch.setattr(
        "proton_autogen.utils.gamescope.detect_screen_resolution",
        lambda: (1920, 1200)
    )

    env = {}

    result = apply_gamescope(
        env,
        enabled=True
    )

    assert result["USE_GAMESCOPE"] == "1"
    assert result["GAMESCOPE_WIDTH"] == "1920"
    assert result["GAMESCOPE_HEIGHT"] == "1200"



def test_apply_gamescope_disabled_cleans_env():

    env = {
        "USE_GAMESCOPE": "1",
        "GAMESCOPE_WIDTH": "1920",
        "GAMESCOPE_HEIGHT": "1200",
    }

    result = apply_gamescope(
        env,
        enabled=False
    )

    assert "USE_GAMESCOPE" not in result
    assert "GAMESCOPE_WIDTH" not in result
    assert "GAMESCOPE_HEIGHT" not in result
