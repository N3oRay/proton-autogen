#flatpak.py
#---------- warp flatpak -----------------------------------
from proton_autogen.utils.logger import StructuredLogger

#-------------------------- Init Log -------------------
logger = StructuredLogger("proton-autogen.flatpak")

import os


def is_flatpak():
    """Return True when running inside a Flatpak sandbox."""
    if logger:
        logger.info("Detect flatpak")
    return os.path.exists("/.flatpak-info")


def wrap_host_command(cmd, logger=None):
    """Wrap a command with flatpak-spawn --host when needed."""
    if not is_flatpak():
        return cmd

    if logger:
        logger.info("Running command on host via flatpak-spawn")

    return ["flatpak-spawn", "--host", *cmd]
