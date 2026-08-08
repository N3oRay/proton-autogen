# analyser.py

from pathlib import Path
from shutil import which
import os


# ---------------------------------------------------------------------
# Flatpak
# ---------------------------------------------------------------------

def is_flatpak():
    """Return True when running inside a Flatpak sandbox."""
    return Path("/.flatpak-info").is_file()


# ---------------------------------------------------------------------
# Host executable detection
# ---------------------------------------------------------------------

# Chemins standards d'exécutables.
#
# Dans Flatpak, les chemins de l'hôte sont accessibles sous /run/host.
#
# Aucun subprocess n'est utilisé.
HOST_BIN_DIRS = (
    "/run/host/usr/local/bin",
    "/run/host/usr/bin",
    "/run/host/usr/games",
    "/run/host/usr/local/games",
    "/run/host/bin",
    "/run/host/usr/local/sbin",
    "/run/host/usr/sbin",
    "/run/host/sbin",
)


def host_which(binary):
    """
    Vérifie la présence d'un exécutable.

    Hors Flatpak :
        utilise le PATH courant avec shutil.which().

    Dans Flatpak :
        inspecte directement le filesystem de l'hôte
        via /run/host.

    Aucun processus n'est lancé.
    """

    # -------------------------------------------------------------
    # Système normal
    # -------------------------------------------------------------
    if not is_flatpak():
        return which(binary) is not None

    # -------------------------------------------------------------
    # Flatpak → filesystem hôte
    # -------------------------------------------------------------
    for directory in HOST_BIN_DIRS:
        path = Path(directory) / binary

        try:
            if path.is_file() and os.access(path, os.X_OK):
                return True
        except OSError:
            continue

    return False


# ---------------------------------------------------------------------
# Runtime detection
# ---------------------------------------------------------------------

def has_proton_call():
    return host_which("proton-call")


def has_wine():
    return host_which("wine")


def has_mangohud():
    return host_which("mangohud")


def has_gamemode():
    return host_which("gamemoderun")


def has_gamescope():
    return host_which("gamescope")
