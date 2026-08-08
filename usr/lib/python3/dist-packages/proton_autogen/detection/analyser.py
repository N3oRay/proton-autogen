# analyser.py

from shutil import which
from functools import lru_cache
import os


def is_flatpak():
    return os.path.exists("/.flatpak-info")


# ---------------------------------------------------------------------------
# Host binary detection
# ---------------------------------------------------------------------------

# Emplacements classiques des exécutables sur l'hôte.
#
# Dans un Flatpak :
#   /run/host/usr/bin     -> /usr/bin
#   /run/host/usr/games   -> /usr/games
#   /run/host/usr/local/bin
#   /run/host/bin
#   /run/host/sbin
#   /run/host/usr/sbin
#
# usr/games est important pour gamescope/gamemoderun sur certaines
# distributions Debian/Ubuntu/Linux Mint.
HOST_BIN_DIRS = (
    "/run/host/usr/bin",
    "/run/host/usr/games",
    "/run/host/usr/local/bin",
    "/run/host/bin",
    "/run/host/sbin",
    "/run/host/usr/sbin",
)


@lru_cache(maxsize=None)
def host_which(binary):
    """
    Recherche un binaire sans exécuter quoi que ce soit.

    Hors Flatpak :
        utilise le PATH normal.

    Dans Flatpak :
        recherche directement dans le système de fichiers hôte
        monté sous /run/host.
    """

    if not binary:
        return None

    # ------------------------------------------------------------
    # Exécution normale
    # ------------------------------------------------------------
    if not is_flatpak():
        return which(binary)

    # ------------------------------------------------------------
    # Flatpak
    # ------------------------------------------------------------
    for directory in HOST_BIN_DIRS:
        path = os.path.join(directory, binary)

        if os.path.isfile(path) and os.access(path, os.X_OK):
            return path

    return None


# ---------------------------------------------------------------------------
# Feature detection
# ---------------------------------------------------------------------------

def has_proton_call():
    return host_which("proton-call") is not None


def has_wine():
    return host_which("wine") is not None


def has_mangohud():
    return host_which("mangohud") is not None


def has_gamemode():
    return host_which("gamemoderun") is not None


def has_gamescope():
    return host_which("gamescope") is not None


def has_xrandr():
    return host_which("xrandr") is not None
