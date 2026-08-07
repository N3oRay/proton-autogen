#flatpak.py
#---------- warp flatpak -----------------------------------
from proton_autogen.utils.logger import StructuredLogger

#-------------------------- Init Log -------------------
logger = StructuredLogger("proton-autogen.flatpak")

import os


def is_flatpak():
    """Return True when running inside a Flatpak sandbox."""
    detected = os.path.exists("/.flatpak-info")

    if detected:
        logger.info("Detect flatpak")

    return detected



def prepare_host_env(env):
    """
    Adjust environment variables when moving execution
    from Flatpak sandbox to host.
    """
    if not is_flatpak():
        return env

    env = env.copy()

    # Restore host user bus
    runtime_dir = os.environ.get("XDG_RUNTIME_DIR")

    if runtime_dir:
        env["DBUS_SESSION_BUS_ADDRESS"] = (
            f"unix:path={runtime_dir}/bus"
        )

    # X11 auth inside sandbox is not valid on host
    xauth = os.path.expanduser("~/.Xauthority")

    if os.path.exists(xauth):
        env["XAUTHORITY"] = xauth

    logger.info(
        "Prepared host environment for Proton"
    )

    return env


def wrap_host_command(cmd, logger=None):
    """Wrap a command with flatpak-spawn --host when needed."""
    if not is_flatpak():
        return cmd

    if logger:
        logger.info("Running command on host via flatpak-spawn")
        logger.info(
            f"Host DISPLAY={os.environ.get('DISPLAY')}"
        )
        logger.info(
            f"Host DBUS={os.environ.get('DBUS_SESSION_BUS_ADDRESS')}"
        )

    return ["flatpak-spawn", "--host", *cmd]
