# proton_autogen/utils/gamescope.py

from typing import List, Tuple
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

DEFAULT_GAMESCOPE_INTERNAL_WIDTH = 1280
DEFAULT_GAMESCOPE_INTERNAL_HEIGHT = 720

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
    # GStreamer
    "GStreamer-WARNING",
    "i386-linux-gnu",

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

    if not has_xrandr():
        logger.warning("xrandr not found, using fallback resolution")
        logger.info(
            f"Using fallback resolution: "
            f"{DEFAULT_GAMESCOPE_WIDTH}x{DEFAULT_GAMESCOPE_HEIGHT}"
        )
        return (
            DEFAULT_GAMESCOPE_WIDTH,
            DEFAULT_GAMESCOPE_HEIGHT,
        )

    if is_flatpak():
        command = [
            "flatpak-spawn",
            "--host",
            "xrandr",
            "--current",
        ]
        logger.debug("Running host xrandr through flatpak-spawn")
    else:
        command = [
            "xrandr",
            "--current",
        ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
        )

        logger.debug("xrandr output:")
        logger.debug(result.stdout)

        for line in result.stdout.splitlines():
            logger.debug(f"xrandr line: {line}")

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
        logger.warning("xrandr command not available, using fallback resolution")

    except subprocess.CalledProcessError as e:
        logger.warning(f"xrandr failed: {e}")
        if e.stderr:
            logger.debug(f"xrandr stderr: {e.stderr}")

    except OSError as e:
        logger.warning(f"xrandr OS error: {e}")

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
    "GAMESCOPE_NESTED_WIDTH",
    "GAMESCOPE_NESTED_HEIGHT",
    "GAMESCOPE_INTERNAL_WIDTH",
    "GAMESCOPE_INTERNAL_HEIGHT",
    "GAMESCOPE_OUTPUT_WIDTH",
    "GAMESCOPE_OUTPUT_HEIGHT",
    "GAMESCOPE_REFRESH",
    "GAMESCOPE_FSR",
    "GAMESCOPE_NIS",
    "GAMESCOPE_SCALER",
    "GAMESCOPE_ADAPTIVE_SYNC",
    "GAMESCOPE_HDR",
    "GAMESCOPE_MANGOAPP",
    "GAMESCOPE_FULLSCREEN",
    "GAMESCOPE_CURSOR",
    "GAMESCOPE_BORDERLESS",
)


# Valeurs acceptées par -S (--scaler). « auto » est le comportement par
# défaut de Gamescope : aucun drapeau n'est alors transmis.
GAMESCOPE_SCALERS = ("auto", "integer", "fit", "fill", "stretch")


def clear_gamescope_env(env: dict) -> None:
    """Remove Gamescope-related environment variables."""
    for key in GAMESCOPE_KEYS:
        env.pop(key, None)


def gamescope_enabled(env: dict) -> bool:
    """
    Return True if Gamescope should be used.
    """
    return env.get("USE_GAMESCOPE", "0") == "1"


def _parse_resolution(value, fallback_w: int, fallback_h: int) -> Tuple[int, int]:
    """
    Parse a Gamescope resolution value.

    Supported examples:
      "1920x1080"
      "1280x800"
      "auto"
      None
    """
    if value in (None, "", "auto"):
        return fallback_w, fallback_h

    if isinstance(value, (tuple, list)) and len(value) == 2:
        try:
            return int(value[0]), int(value[1])
        except (TypeError, ValueError):
            return fallback_w, fallback_h

    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in ("", "auto"):
            return fallback_w, fallback_h

        match = re.fullmatch(r"(\d+)x(\d+)", normalized)
        if match:
            try:
                return int(match.group(1)), int(match.group(2))
            except ValueError:
                pass

    try:
        return int(value), fallback_h
    except (TypeError, ValueError):
        return fallback_w, fallback_h


def _ensure_gamescope_legacy_aliases(env: dict) -> None:
    """
    Compatibilité avec les anciennes variables.

    L’ancien nom GAMESCOPE_WIDTH/HEIGHT correspondait historiquement aux
    dimensions internes du rendu, mais l'utilité actuelle est surtout
    d’avoir des variables claires et séparées :
      - GAMESCOPE_INTERNAL_WIDTH/HEIGHT => -w/-h
      - GAMESCOPE_OUTPUT_WIDTH/HEIGHT => -W/-H
    """
    if "GAMESCOPE_INTERNAL_WIDTH" not in env and env.get("GAMESCOPE_WIDTH"):
        env["GAMESCOPE_INTERNAL_WIDTH"] = env["GAMESCOPE_WIDTH"]

    if "GAMESCOPE_INTERNAL_HEIGHT" not in env and env.get("GAMESCOPE_HEIGHT"):
        env["GAMESCOPE_INTERNAL_HEIGHT"] = env["GAMESCOPE_HEIGHT"]

    if "GAMESCOPE_OUTPUT_WIDTH" not in env and env.get("GAMESCOPE_NESTED_WIDTH"):
        env["GAMESCOPE_OUTPUT_WIDTH"] = env["GAMESCOPE_NESTED_WIDTH"]

    if "GAMESCOPE_OUTPUT_HEIGHT" not in env and env.get("GAMESCOPE_NESTED_HEIGHT"):
        env["GAMESCOPE_OUTPUT_HEIGHT"] = env["GAMESCOPE_NESTED_HEIGHT"]


def init_gamescope_env(
    enabled: bool = False,
    width: int | None = None,
    height: int | None = None,
    refresh: int | None = None,
    fullscreen: bool = True,
    cursor: bool = True,
    internal_width: int | str | None = None,
    internal_height: int | str | None = None,
    output_width: int | str | None = None,
    output_height: int | str | None = None,
    mode: str = "output",
    fsr: bool = False,
    nis: bool = False,
    scaler: str | None = None,
    hdr: bool = False,
    adaptive_sync: bool = False,
    mangoapp: bool = False,
) -> dict:
    """
    Initialize Gamescope parameters.

    This function does not execute any command.

    Modes:
      - "output": use -W/-H (default)
      - "internal": use -w/-h
      - "custom": use both
      - "auto": same as output

    Options:
      - refresh: limite de fréquence du jeu (-r), ignorée si vide ou 0
      - fsr: upscaling AMD FSR (-F fsr)
      - nis: upscaling NVIDIA Image Scaling (-F nis), ignoré si fsr
      - scaler: "integer", "stretch"... (-S), "auto"/None = défaut
      - hdr: sortie HDR (--hdr-enabled)
      - adaptive_sync: VRR FreeSync/G-Sync (--adaptive-sync)
      - mangoapp: overlay MangoHud via Gamescope (--mangoapp)
      - cursor: capture forcée du curseur (--force-grab-cursor)
    """

    env = {}

    env["USE_GAMESCOPE"] = "1" if enabled else "0"

    if not enabled:
        return env

    if width is None:
        width = DEFAULT_GAMESCOPE_WIDTH
    if height is None:
        height = DEFAULT_GAMESCOPE_HEIGHT

    if internal_width is None:
        internal_width = DEFAULT_GAMESCOPE_INTERNAL_WIDTH
    if internal_height is None:
        internal_height = DEFAULT_GAMESCOPE_INTERNAL_HEIGHT

    if output_width is None:
        output_width = width
    if output_height is None:
        output_height = height

    if mode in ("auto", "output"):
        env["GAMESCOPE_OUTPUT_WIDTH"] = str(output_width)
        env["GAMESCOPE_OUTPUT_HEIGHT"] = str(output_height)

    if mode in ("internal", "custom"):
        env["GAMESCOPE_INTERNAL_WIDTH"] = str(internal_width)
        env["GAMESCOPE_INTERNAL_HEIGHT"] = str(internal_height)

    if mode == "custom":
        env["GAMESCOPE_OUTPUT_WIDTH"] = str(output_width)
        env["GAMESCOPE_OUTPUT_HEIGHT"] = str(output_height)

    if refresh:
        env["GAMESCOPE_REFRESH"] = str(refresh)

    if fsr:
        env["GAMESCOPE_FSR"] = "1"

    if nis:
        env["GAMESCOPE_NIS"] = "1"

    scaler_value = str(scaler).strip().lower() if scaler else ""
    if scaler_value in GAMESCOPE_SCALERS:
        if scaler_value != "auto":
            env["GAMESCOPE_SCALER"] = scaler_value
    elif scaler_value:
        logger.warning(f"Unknown Gamescope scaler ignored: {scaler_value}")

    if adaptive_sync:
        env["GAMESCOPE_ADAPTIVE_SYNC"] = "1"

    if hdr:
        env["GAMESCOPE_HDR"] = "1"

    if mangoapp:
        env["GAMESCOPE_MANGOAPP"] = "1"

    env["GAMESCOPE_FULLSCREEN"] = "1" if fullscreen else "0"
    env["GAMESCOPE_CURSOR"] = "1" if cursor else "0"

    _ensure_gamescope_legacy_aliases(env)

    return env


# ---------------------------------------------------------
# Command builder
# ---------------------------------------------------------

def build_gamescope_command(env: dict) -> List[str]:
    """
    Build the Gamescope command from environment variables.

    This function does not execute Gamescope.

    Semantics:
      - -W/-H : output resolution
      - -w/-h : internal rendering resolution
    """

    if not gamescope_enabled(env):
        return []

    cmd = ["gamescope"]

    # Output resolution : -W/-H
    if env.get("GAMESCOPE_OUTPUT_WIDTH"):
        cmd += ["-W", env["GAMESCOPE_OUTPUT_WIDTH"]]

    if env.get("GAMESCOPE_OUTPUT_HEIGHT"):
        cmd += ["-H", env["GAMESCOPE_OUTPUT_HEIGHT"]]

    # Internal rendering resolution : -w/-h
    if env.get("GAMESCOPE_INTERNAL_WIDTH"):
        cmd += ["-w", env["GAMESCOPE_INTERNAL_WIDTH"]]

    if env.get("GAMESCOPE_INTERNAL_HEIGHT"):
        cmd += ["-h", env["GAMESCOPE_INTERNAL_HEIGHT"]]

    # Compatibilité avec les anciens noms.
    # Ces anciens alias ne devraient plus être utilisés :
    #  GAMESCOPE_WIDTH/HEIGHT = interne
    #  GAMESCOPE_NESTED_WIDTH/HEIGHT = sortie
    if env.get("GAMESCOPE_NESTED_WIDTH") and not env.get("GAMESCOPE_OUTPUT_WIDTH"):
        cmd += ["-W", env["GAMESCOPE_NESTED_WIDTH"]]

    if env.get("GAMESCOPE_NESTED_HEIGHT") and not env.get("GAMESCOPE_OUTPUT_HEIGHT"):
        cmd += ["-H", env["GAMESCOPE_NESTED_HEIGHT"]]

    if env.get("GAMESCOPE_WIDTH") and not env.get("GAMESCOPE_INTERNAL_WIDTH"):
        cmd += ["-w", env["GAMESCOPE_WIDTH"]]

    if env.get("GAMESCOPE_HEIGHT") and not env.get("GAMESCOPE_INTERNAL_HEIGHT"):
        cmd += ["-h", env["GAMESCOPE_HEIGHT"]]

    # Refresh rate
    if env.get("GAMESCOPE_REFRESH"):
        cmd += ["-r", env["GAMESCOPE_REFRESH"]]

    # Mise à l'échelle : -S (integer, stretch...). « auto » = défaut.
    scaler = (env.get("GAMESCOPE_SCALER") or "").strip().lower()
    if scaler in GAMESCOPE_SCALERS and scaler != "auto":
        cmd += ["-S", scaler]

    # Filtre d'upscaling : -F fsr ou -F nis (un seul filtre, FSR prioritaire)
    if env.get("GAMESCOPE_FSR") == "1":
        cmd += ["-F", "fsr"]
    elif env.get("GAMESCOPE_NIS") == "1":
        cmd += ["-F", "nis"]

    # Fullscreen
    if env.get("GAMESCOPE_FULLSCREEN") == "1":
        cmd.append("--fullscreen")

    # Cursor
    if env.get("GAMESCOPE_CURSOR") == "1":
        cmd.append("--force-grab-cursor")

    # Borderless
    if env.get("GAMESCOPE_BORDERLESS") == "1":
        cmd.append("--borderless")

    # Synchronisation adaptative (VRR)
    if env.get("GAMESCOPE_ADAPTIVE_SYNC") == "1":
        cmd.append("--adaptive-sync")

    # Sortie HDR
    if env.get("GAMESCOPE_HDR") == "1":
        cmd.append("--hdr-enabled")

    # Overlay MangoHud géré par Gamescope
    if env.get("GAMESCOPE_MANGOAPP") == "1":
        cmd.append("--mangoapp")

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
    internal_width: int | str | None = None,
    internal_height: int | str | None = None,
    output_width: int | str | None = None,
    output_height: int | str | None = None,
    mode: str = "output",
    fsr: bool = False,
    nis: bool = False,
    scaler: str | None = None,
    hdr: bool = False,
    adaptive_sync: bool = False,
    mangoapp: bool = False,
) -> dict:
    """
    Apply Gamescope environment variables.

    If width/height are not specified, the active screen
    resolution is detected with xrandr.

    Gamescope itself is never executed here.
    """

    clear_gamescope_env(env)

    if not enabled:
        return env

    if not has_gamescope():
        logger.warning("Gamescope requested but not available")
        return env

    if width is None or height is None:
        width, height = detect_screen_resolution()

    if mode in ("auto", "output"):
        if output_width is None:
            output_width = width
        if output_height is None:
            output_height = height
    else:
        if output_width is None:
            output_width = width
        if output_height is None:
            output_height = height

    if internal_width is None:
        internal_width = DEFAULT_GAMESCOPE_INTERNAL_WIDTH
    if internal_height is None:
        internal_height = DEFAULT_GAMESCOPE_INTERNAL_HEIGHT

    env.update(
        init_gamescope_env(
            enabled=True,
            width=width,
            height=height,
            refresh=refresh,
            fullscreen=fullscreen,
            cursor=cursor,
            internal_width=internal_width,
            internal_height=internal_height,
            output_width=output_width,
            output_height=output_height,
            mode=mode,
            fsr=fsr,
            nis=nis,
            scaler=scaler,
            hdr=hdr,
            adaptive_sync=adaptive_sync,
            mangoapp=mangoapp,
        )
    )

    logger.debug(
        f"Gamescope configured: "
        f"output={output_width}x{output_height}, "
        f"internal={internal_width}x{internal_height}, mode={mode}, "
        f"refresh={refresh or '-'}, fsr={fsr}, nis={nis}, "
        f"scaler={scaler or 'auto'}, hdr={hdr}, vrr={adaptive_sync}, "
        f"mangoapp={mangoapp}, cursor={cursor}"
    )

    return env
