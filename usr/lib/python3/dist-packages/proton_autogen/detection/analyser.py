#analyser.py
from shutil import which
import os
import subprocess


def is_flatpak():
    return os.path.exists("/.flatpak-info")


def host_which(binary):
    """
    Recherche un exécutable dans le PATH de l'hôte
    lorsqu'on tourne dans un sandbox Flatpak.
    """
    if not is_flatpak():
        return which(binary) is not None

    try:
        result = subprocess.run(
            ["flatpak-spawn", "--host", "sh", "-c", f"command -v '{binary}'"],
            capture_output=True,
            text=True,
            timeout=2,
        )

        return result.returncode == 0 and bool(result.stdout.strip())

    except Exception:
        return False


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
