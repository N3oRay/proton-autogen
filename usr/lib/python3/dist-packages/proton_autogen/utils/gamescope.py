# proton_autogen/utils/gamescope.py

from typing import List
import os
import re
import subprocess

from proton_autogen.detection.analyser import (
    has_gamescope,
    has_xrandr,
    is_flatpak,
)

from proton_autogen.utils.logger import StructuredLogger


DEFAULT_GAMESCOPE_WIDTH = 1920
DEFAULT_GAMESCOPE_HEIGHT = 1080

logger = StructuredLogger("proton-autogen.gamescope")


# ---------------------------------------------------------
# Log filters
# ---------------------------------------------------------

DEFAULT_LOG_FILTERS = [
    # MangoHud 32/64 bits
    "wrong ELF class",

    # MangoHud sensors
    "Could not find cpu temp sensor location",

    # XKB warnings Gamescope
    "Could not resolve keysym",
    "Unsupported maximum keycode",
    "Errors from xkbcomp are not fatal",

    # Gamescope D-Bus
    "sd_bus_call",
    "D-Bus call to get unit corresponding",

    # Gamescope buffers
    "got the same buffer committed twice",

    # Vulkan noise
    "ATTENTION: default value of option",
    "[Gamescope WSI] No application info given",

    # ProtonFixes inutile
    "ProtonFixes",
]


GAMESCOPE_LOG_FILTERS = [
    "scriptmgr:",
    "supported DRM formats",
    "pipewire:",
    "AR24",
    "XR24",
    "AB24",
    "XB24",
    "RG16",
    "NV12",
    "AB4H",
    "XB4H",
    "AB48",
    "XB48",
    "AB30",
    "XB30",
    "AR30",
    "XR30",
    "Creating Gamescope nested swapchain",
    "The XKEYBOARD keymap compiler",
    "X11 cannot support keycodes above 255",
    "[Gamescope WSI] No application info given",
    "No CAP_SYS_NICE",
    "Performance will be affected",
]


LOG_FILTERS = list(
    set(DEFAULT_LOG_FILTERS + GAMESCOPE_LOG_FILTERS)
)


# ---------------------------------------------------------
# Screen resolution
# ---------------------------------------------------------

def detect_screen_resolution() -> tuple[int, int]:
    """
    Detect the active screen resolution using xrandr.

    Important:
        - Detection of xrandr itself does NOT execute anything.
        - This function executes xrandr only because the actual
          screen resolution must be queried at runtime.
        - Inside Flatpak, xrandr is executed on the host.
    """

    logger.debug("===== Detect Screen Resolution =====")

    # -----------------------------------------------------
    # First check: does xrandr exist?
    #
    # This uses the new filesystem-based analyser.
    # No subprocess is used here.
    # -----------------------------------------------------

    if not has_xrandr():
        logger.warning(
            "xrandr not found, using fallback resolution"
        )

        logger.info(
            f"Using fallback resolution: "
            f"{DEFAULT_GAMESCOPE_WIDTH}x{DEFAULT_GAMESCOPE_HEIGHT}"
        )

        return (
            DEFAULT_GAMESCOPE_WIDTH,
            DEFAULT_GAMESCOPE_HEIGHT,
        )

    # -----------------------------------------------------
    # Build command
    # -----------------------------------------------------

    if is_flatpak():
        # xrandr exists on the host.
        #
        # We deliberately execute it through flatpak-spawn
        # because the sandbox does not necessarily contain
        # the host xrandr runtime environment.
        command = [
            "flatpak-spawn",
            "--host",
            "xrandr",
            "--current",
        ]

        logger.debug(
            "Running host xrandr through flatpak-spawn"
        )

    else:
        command = [
            "xrandr",
            "--current",
        ]

    # -----------------------------------------------------
    # Execute xrandr
    # -----------------------------------------------------

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
        )

        logger.debug("xrandr output:")
        logger.debug(result.stdout)

        # -------------------------------------------------
        # Parse active mode
        #
        # Example:
        #
        #     1920x1200     59.95*+
        #
        # We specifically look for '*', which marks
        # the active mode.
        # -------------------------------------------------

        for line in result.stdout.splitlines():

            logger.debug(
                f"xrandr line: {line}"
            )

            match = re.search(
                r"\s+(\d+)x(\d+)\s+.*\*",
                line,
            )

            if not match:
                continue

            width = int(match.group(1))
            height = int(match.group(2))

            logger.info(
                f"Detected screen resolution: "
                f"{width}x{height}"
            )

            return width, height

    except FileNotFoundError:
        logger.warning(
            "xrandr command not available, "
            "using fallback resolution"
        )

    except subprocess.CalledProcessError as e:
        logger.warning(
            f"xrandr failed: {e}"
        )

        if e.stderr:
            logger.debug(
                f"xrandr stderr: {e.stderr}"
            )

    except OSError as e:
        logger.warning(
            f"xrandr OS error: {e}"
        )

    # -----------------------------------------------------
    # Fallback
    # -----------------------------------------------------

    logger.info(
        f"Using fallback resolution: "
        f"{DEFAULT_GAMESCOPE_WIDTH}x"
        f"{DEFAULT_GAMESCOPE_HEIGHT}"
    )

    return (
        DEFAULT_GAMESCOPE_WIDTH,
        DEFAULT_GAMESCOPE_HEIGHT,
    )


# ---------------------------------------------------------
# Environment
# ---------------------------------------------------------

GAMESCOPE_KEYS = (
    "USE_GAMESCOPE",
    "GAMESCOPE_WIDTH",
    "GAMESCOPE_HEIGHT",
    "GAMESCOPE_REFRESH",
    "GAMESCOPE_FULLSCREEN",
    "GAMESCOPE_CURSOR",
    "GAMESCOPE_NESTED_WIDTH",
    "GAMESCOPE_NESTED_HEIGHT",
    "GAMESCOPE_BORDERLESS",
)


def clear_gamescope_env(env: dict) -> None:
    """Remove Gamescope-related environment variables."""

    for key in GAMESCOPE_KEYS:
        env.pop(key, None)


# Quake 2 : 1280x960
# jeux modernes : 1920x1080
# Steam Deck : 1280x800
# anciens jeux 4:3 : scaling automatique

def gamescope_enabled(env: dict) -> bool:
    """
    Return True if Gamescope should be used.
    """

    return env.get("USE_GAMESCOPE", "0") == "1"

#Sample : gamescope -w 1920 -h 1200 --fullscreen --force-grab-cursor -- proton-autogen QUAKE2.EXE

# ---------------------------------------------------------
# Environment initialization
# ---------------------------------------------------------

def init_gamescope_env(
    enabled: bool = False,
    width: int = DEFAULT_GAMESCOPE_WIDTH,
    height: int = DEFAULT_GAMESCOPE_HEIGHT,
    refresh: int | None = None,
    fullscreen: bool = True,
    cursor: bool = True,
) -> dict:
    """
    Initialize Gamescope parameters.

    This function does not execute any command.
    """

    env = {}

    env["USE_GAMESCOPE"] = (
        "1" if enabled else "0"
    )

    if enabled:

        env["GAMESCOPE_WIDTH"] = str(width)
        env["GAMESCOPE_HEIGHT"] = str(height)

        if refresh:
            env["GAMESCOPE_REFRESH"] = str(refresh)

        env["GAMESCOPE_FULLSCREEN"] = (
            "1" if fullscreen else "0"
        )

        env["GAMESCOPE_CURSOR"] = (
            "1" if cursor else "0"
        )

    return env


# ---------------------------------------------------------
# Command builder
# ---------------------------------------------------------

def build_gamescope_command(env: dict) -> List[str]:
    """
    Build the Gamescope command from environment variables.

    This function does not execute Gamescope.
    """

    if not gamescope_enabled(env):
        return []

    cmd = ["gamescope"]

    # Output resolution
    if env.get("GAMESCOPE_WIDTH"):
        cmd += [
            "-w",
            env["GAMESCOPE_WIDTH"],
        ]

    if env.get("GAMESCOPE_HEIGHT"):
        cmd += [
            "-h",
            env["GAMESCOPE_HEIGHT"],
        ]

    # Internal rendering resolution
    if env.get("GAMESCOPE_NESTED_WIDTH"):
        cmd += [
            "-W",
            env["GAMESCOPE_NESTED_WIDTH"],
        ]

    if env.get("GAMESCOPE_NESTED_HEIGHT"):
        cmd += [
            "-H",
            env["GAMESCOPE_NESTED_HEIGHT"],
        ]

    # Refresh rate
    if env.get("GAMESCOPE_REFRESH"):
        cmd += [
            "-r",
            env["GAMESCOPE_REFRESH"],
        ]

    # Fullscreen
    if env.get("GAMESCOPE_FULLSCREEN") == "1":
        cmd.append("--fullscreen")

    # Cursor
    if env.get("GAMESCOPE_CURSOR") == "1":
        cmd.append("--force-grab-cursor")

    # Borderless
    if env.get("GAMESCOPE_BORDERLESS") == "1":
        cmd.append("--borderless")

    cmd.append("--")

    return cmd


# ---------------------------------------------------------
# Apply Gamescope
# ---------------------------------------------------------

def apply_gamescope(
    env: dict,
    enabled: bool,
    width: int | None = None,
    height: int | None = None,
    refresh: int | None = None,
    fullscreen: bool = True,
    cursor: bool = True,
) -> dict:
    """
    Apply Gamescope environment variables.

    If width/height are not specified, the active screen
    resolution is detected with xrandr.

    Gamescope itself is never executed here.
    """

    clear_gamescope_env(env)

    # -----------------------------------------------------
    # Gamescope unavailable
    #
    # has_gamescope() performs filesystem detection only.
    # -----------------------------------------------------

    if not enabled:
        return env

    if not has_gamescope():
        logger.warning(
            "Gamescope requested but not available"
        )
        return env

    # -----------------------------------------------------
    # Automatic resolution
    # -----------------------------------------------------

    if width is None or height is None:
        width, height = detect_screen_resolution()

    # -----------------------------------------------------
    # Apply configuration
    # -----------------------------------------------------

    env.update(
        init_gamescope_env(
            enabled=True,
            width=width,
            height=height,
            refresh=refresh,
            fullscreen=fullscreen,
            cursor=cursor,
        )
    )

    logger.debug(
        f"Gamescope configured: "
        f"{width}x{height}"
    )

    return env
