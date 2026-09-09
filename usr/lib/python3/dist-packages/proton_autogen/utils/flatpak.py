#flatpak.py
#---------- warp flatpak -----------------------------------
from proton_autogen.utils.logger import StructuredLogger
from proton_autogen.profiles.def_env import ENV_VARS

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
    Prepare the environment used by a command executed on the host
    through flatpak-spawn --host.
    """
    if not is_flatpak():
        return env

    env = env.copy()

    # --------------------------------------------------
    # Host user / HOME
    # --------------------------------------------------

    host_user = os.environ.get("USER") or os.environ.get("LOGNAME")

    if host_user:
        env["USER"] = host_user
        env["LOGNAME"] = host_user
        env["HOME"] = f"/home/{host_user}"

    # --------------------------------------------------
    # Host runtime / DBus
    # --------------------------------------------------

    runtime_dir = os.environ.get("XDG_RUNTIME_DIR")

    if runtime_dir:
        env["XDG_RUNTIME_DIR"] = runtime_dir
        env["DBUS_SESSION_BUS_ADDRESS"] = (
            f"unix:path={runtime_dir}/bus"
        )

    # --------------------------------------------------
    # X11
    # --------------------------------------------------

    display = os.environ.get("DISPLAY")

    if display:
        env["DISPLAY"] = display

    xauthority = env["HOME"] + "/.Xauthority"

    if os.path.exists(xauthority):
        env["XAUTHORITY"] = xauthority

    logger.info(
        "Prepared host environment for Proton: "
        f"USER={env.get('USER')} "
        f"HOME={env.get('HOME')} "
        f"DISPLAY={env.get('DISPLAY')} "
        f"XDG_RUNTIME_DIR={env.get('XDG_RUNTIME_DIR')} "
        f"DBUS_SESSION_BUS_ADDRESS={env.get('DBUS_SESSION_BUS_ADDRESS')} "
        f"XAUTHORITY={env.get('XAUTHORITY')}"
    )

    return env




def wrap_host_command(cmd, env=None, logger=None):
    """
    Execute command on the host from inside Flatpak.

    Forward only:
      - variables explicitly declared in ENV_VARS
      - STEAM*
      - PROTON*
      - WINE*
      - DXVK*
      - DBUS*
      - GAMEMODE
      - DISPLAY
      - XAUTHORITY

    Environment values are passed untouched to flatpak-spawn.
    This is important for PATH-like variables containing ':' or spaces.
    """

    if not is_flatpak():
        return cmd

    if logger:
        logger.info("Running command on host via flatpak-spawn")

    host_cmd = [
        "flatpak-spawn",
        "--host",
    ]

    if not env:
        host_cmd.extend(cmd)
        return host_cmd

    # --------------------------------------------------
    # Variables explicitly declared in ENV_VARS
    # --------------------------------------------------

    allowed_names = {
        item["name"]
        for item in ENV_VARS
        if isinstance(item, dict) and item.get("name")
    }

    # --------------------------------------------------
    # Variable families
    # --------------------------------------------------

    allowed_prefixes = (
        "STEAM",
        "PROTON",
        "WINE",
        "DXVK",
        "DBUS",
    )

    allowed_exact = {
        "GAMEMODE",
        "DISPLAY",
        "XAUTHORITY",
    }

    forwarded = []

    for name, value in env.items():

        # Ignore variables with a None value.
        if value is None:
            continue

        if (
            name in allowed_names
            or name in allowed_exact
            or name.startswith(allowed_prefixes)
        ):
            # flatpak-spawn expects:
            #
            #   --env=VAR=VALUE
            #
            # Keep the complete expression as ONE argument.
            host_cmd.append(
                f"--env={name}={value}"
            )

            forwarded.append(name)

    if logger:
        logger.debug(
            "Forwarded host environment variables: "
            + ", ".join(sorted(forwarded))
        )

    host_cmd.extend(cmd)

    return host_cmd
