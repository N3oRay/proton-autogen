# proton_autogen/utils/gamescope.py

from typing import List


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

def init_gamescope_env(enabled=False, width="1920", height="1200",
                       refresh=None, fullscreen=True, cursor=True):
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
