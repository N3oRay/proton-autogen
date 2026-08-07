# analyser.py

from shutil import which
import os


def is_flatpak():
    """Return True when running inside a Flatpak sandbox."""
    return os.path.exists("/.flatpak-info")


# ---------------------------------------------------------------------
# Detection without subprocess / run
# ---------------------------------------------------------------------

def host_paths():
    """
    Return paths that can contain host-side tools.

    No process is spawned.
    """
    paths = []

    # PATH actuel
    paths.extend(os.environ.get("PATH", "").split(os.pathsep))

    if is_flatpak():
        home = os.path.expanduser("~")

        # Steam native
        paths.extend([
            os.path.join(home, ".steam", "root", "bin"),
            os.path.join(home, ".steam", "steam", "bin"),
            os.path.join(home, ".local", "bin"),
            os.path.join(home, "bin"),
        ])

        # Steam Flatpak
        paths.extend([
            os.path.join(
                home,
                ".var", "app",
                "com.valvesoftware.Steam",
                ".local", "share", "Steam", "bin"
            ),
        ])

        # System
        paths.extend([
            "/usr/bin",
            "/usr/local/bin",
            "/bin",
            "/usr/sbin",
            "/usr/local/sbin",
            "/sbin",
        ])

    # Déduplication
    return list(dict.fromkeys(
        p for p in paths
        if p and os.path.isdir(p)
    ))


_HOST_PATH = os.pathsep.join(host_paths())


def host_which(binary):
    """
    Detect an executable without spawning a process.

    Uses shutil.which() against a predefined host PATH.
    """
    return which(binary, path=_HOST_PATH) is not None


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
