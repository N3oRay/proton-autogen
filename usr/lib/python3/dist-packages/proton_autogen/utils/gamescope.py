# proton_autogen/utils/gamescope.py

from typing import List
import subprocess
import re
from proton_autogen.detection.analyser import has_gamescope
from proton_autogen.utils.logger import StructuredLogger
DEFAULT_GAMESCOPE_WIDTH = 1920
DEFAULT_GAMESCOPE_HEIGHT = 1080

logger = StructuredLogger("proton-autogen.gamescope")

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
    "supported DRM formats",
    "vulkan:   AR",
    "vulkan:   XR",
    "vulkan:   AB",
    "vulkan:   XB",
    "vulkan:   RG",
    "vulkan:   NV",
    "Creating Gamescope nested swapchain",
    "The XKEYBOARD keymap compiler",
    "X11 cannot support keycodes above 255",
    "[Gamescope WSI]",
]

# Fusion globale
LOG_FILTERS = list(set(DEFAULT_LOG_FILTERS + GAMESCOPE_LOG_FILTERS))



def detect_screen_resolution() -> tuple[int, int] | None:
    """
    Detect active monitor resolution using xrandr.
    Ignores the virtual desktop size.
    """

    logger.debug("===== Detect Screen Resolution =====")

    try:
        result = subprocess.run(
            ["xrandr", "--current"],
            capture_output=True,
            text=True,
            check=True,
        )

        if logger:
            logger.debug("xrandr output:")
            logger.debug(result.stdout)

        lines = result.stdout.splitlines()

        for line in lines:
            logger.debug(f"xrandr line: {line}")

            # Active mode line example:
            # "   1920x1200     59.95*+"
            match = re.search(
                r"\s+(\d+)x(\d+)\s+.*\*",
                line
            )

            if match:
                width = int(match.group(1))
                height = int(match.group(2))

                logger.info(
                    f"Detected screen resolution: {width}x{height}"
                )

                return width, height

    except FileNotFoundError:
        logger.warning(
            "xrandr not found, using fallback resolution"
        )

    except subprocess.CalledProcessError as e:
        logger.warning(
            f"xrandr failed: {e}"
        )

    except OSError as e:
        logger.warning(
            f"xrandr OS error: {e}"
        )

    logger.info(
        f"Using fallback resolution: "
        f"{DEFAULT_GAMESCOPE_WIDTH}x{DEFAULT_GAMESCOPE_HEIGHT}"
    )

    return DEFAULT_GAMESCOPE_WIDTH, DEFAULT_GAMESCOPE_HEIGHT




# Clean var after make command
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
    """Supprime les variables d'environnement liées à Gamescope."""
    for key in GAMESCOPE_KEYS:
        env.pop(key, None)


# Quake 2 : 1280x960
# jeux modernes : 1920x1080
# Steam Deck : 1280x800
# anciens jeux 4:3 : scaling automatique

def gamescope_enabled(env: dict) -> bool:
    """
    Returns True if Gamescope should be used.
    """
    return env.get("USE_GAMESCOPE", "0") == "1"

#Sample : gamescope -w 1920 -h 1200 --fullscreen --force-grab-cursor -- proton-autogen QUAKE2.EXE

# proton_autogen/utils/gamescope.py


def init_gamescope_env( enabled: bool = False, width: int = 1920, height: int = 1080, refresh: int | None = None, fullscreen: bool = True, cursor: bool = True, ) -> dict:
    """
    Initialise les paramètres Gamescope.
    Ne lance aucune commande.
    """

    env = {}

    env["USE_GAMESCOPE"] = "1" if enabled else "0"

    if enabled:
        env["GAMESCOPE_WIDTH"] = str(width)
        env["GAMESCOPE_HEIGHT"] = str(height)

        if refresh:
            env["GAMESCOPE_REFRESH"] = str(refresh)

        env["GAMESCOPE_FULLSCREEN"] = "1" if fullscreen else "0"
        env["GAMESCOPE_CURSOR"] = "1" if cursor else "0"

    return env


def build_gamescope_command(env: dict) -> List[str]:
    """
    Build the Gamescope command from environment variables.
    """

    if not gamescope_enabled(env):
        return []

    cmd = ["gamescope"]

    # Output resolution
    if env.get("GAMESCOPE_WIDTH"):
        cmd += ["-w", env["GAMESCOPE_WIDTH"]]

    if env.get("GAMESCOPE_HEIGHT"):
        cmd += ["-h", env["GAMESCOPE_HEIGHT"]]

    # Internal rendering resolution
    if env.get("GAMESCOPE_NESTED_WIDTH"):
        cmd += ["-W", env["GAMESCOPE_NESTED_WIDTH"]]

    if env.get("GAMESCOPE_NESTED_HEIGHT"):
        cmd += ["-H", env["GAMESCOPE_NESTED_HEIGHT"]]

    # Refresh rate
    if env.get("GAMESCOPE_REFRESH"):
        cmd += ["-r", env["GAMESCOPE_REFRESH"]]

    # Options
    if env.get("GAMESCOPE_FULLSCREEN") == "1":
        cmd.append("--fullscreen")

    if env.get("GAMESCOPE_CURSOR") == "1":
        cmd.append("--force-grab-cursor")

    if env.get("GAMESCOPE_BORDERLESS") == "1":
        cmd.append("--borderless")  #cmd.append("-b")      # or "--borderless" # instable !

    cmd.append("--")

    return cmd


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

    Automatically detects display resolution if width/height are not set.
    """

    clear_gamescope_env(env)

    if not enabled or not has_gamescope():
        return env

    if width is None or height is None:
        width, height = detect_screen_resolution()

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

    return env
