#backend.py proton-autogen core
import os
import json
import hashlib
import re
import shutil
import subprocess
from pathlib import Path
from shutil import which

CONFIG_DIR = os.path.expanduser("~/.config/proton-autogen/games")


PROTON_PATHS = [
    # Steam native tools
    "~/.steam/root/compatibilitytools.d",
    "~/.steam/steam/compatibilitytools.d",
    "~/.local/share/Steam/compatibilitytools.d",

    # Flatpak Steam
    "~/.var/app/com.valvesoftware.Steam/.local/share/Steam/compatibilitytools.d",
    "~/.var/app/com.valvesoftware.Steam/.steam/root/compatibilitytools.d",

    # Steam libraries (IMPORTANT)
    "~/.steam/steam/steamapps/common",
    "~/.local/share/Steam/steamapps/common",

    # system-wide Proton (CachyOS / Arch)
    "/usr/share",
    "/usr/lib"
    # system Steam tools (IMPORTANT FIX)
    "/usr/share/steam/compatibilitytools.d"
]



def find_system_proton():

    # Arch / CachyOS
    if shutil.which("pacman"):
        try:
            subprocess.check_output(
                ["pacman", "-Q", "proton-cachyos"],
                stderr=subprocess.DEVNULL
            )
            return "proton-cachyos"
        except subprocess.CalledProcessError:
            pass

    # Debian / Ubuntu
    if shutil.which("dpkg"):
        try:
            subprocess.check_output(
                ["dpkg", "-s", "proton-cachyos"],
                stderr=subprocess.DEVNULL
            )
            return "proton-cachyos"
        except subprocess.CalledProcessError:
            pass

    # Fedora
    if shutil.which("rpm"):
        try:
            subprocess.check_output(
                ["rpm", "-q", "proton-cachyos"],
                stderr=subprocess.DEVNULL
            )
            return "proton-cachyos"
        except subprocess.CalledProcessError:
            pass

    return None

def normalize_flag(value, default=True):
    if value is None:
        return default
    if isinstance(value, str):
        return value.lower() in ("1", "true", "yes", "on")
    return bool(value)

def has_mangohud():
    return which("mangohud") is not None

def has_gamemode():
    return which("gamemoderun") is not None

def proton_score(name):
    numbers = [int(n) for n in re.findall(r'\d+', name)]

    major = numbers[0] if len(numbers) > 0 else 0
    minor = numbers[1] if len(numbers) > 1 else 0

    return (
        major,
        minor,
        name.lower()
    )


def find_proton():
    candidates = []

    def is_proton_dir(name: str) -> bool:
        return "proton" in name.lower()

    # Steam-based Proton
    for base in PROTON_PATHS:
        base = os.path.expanduser(base)

        if not os.path.exists(base):
            continue

        try:
            for d in os.listdir(base):
                full = os.path.join(base, d)

                if os.path.isdir(full) and is_proton_dir(d):
                    candidates.append(full)

        except PermissionError:
            continue

    # System Proton fallback
    system = find_system_proton()
    if system:
        # normalisation du format pour éviter crash du sort
        if isinstance(system, dict):
            candidates.append(system)
        else:
            candidates.append(system)

    if not candidates:
        return None

    def sort_key(x):
        # support string + dict (system proton)
        if isinstance(x, dict):
            name = x.get("name", "")
        else:
            name = os.path.basename(x)

        return proton_score(name)

    candidates.sort(key=sort_key, reverse=True)

    return candidates[0]

def _game_id(exe_path: str):
    return hashlib.md5(os.path.abspath(exe_path).encode()).hexdigest()


def load_game_config(exe_path):
    game_id = _game_id(exe_path)
    path = os.path.expanduser(f"~/.config/proton-autogen/games/{game_id}.json")

    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)

    return None


def add_game(exe_path: str):
    exe_path = os.path.abspath(exe_path)

    if not os.path.exists(exe_path):
        print(f"Error: file not found: {exe_path}")
        return

    os.makedirs(CONFIG_DIR, exist_ok=True)

    gid = _game_id(exe_path)
    config_path = os.path.join(CONFIG_DIR, gid + ".json")

    proton = find_proton()

    config = {
        "id": gid,
        "name": os.path.basename(exe_path),
        "path": exe_path,
        "proton": os.path.basename(proton) if proton else None,
        "mangohud": has_mangohud(),
        "gamemode": has_gamemode(),
        "env": {
            "DXVK_ASYNC": "1"
        }
    }

    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

    print("[proton-autogen] Game added:")
    print(f"  name   : {config['name']}")
    print(f"  id     : {gid}")
    print(f"  config : {config_path}")

def find_windows_programs(root=None):
    if root is None:
        root = os.path.expanduser("~")

    excluded_patterns = [
        "/.steam/",
        "/.cache/",
        "/pfx/",
        "/drive_c/windows/",
    ]

    excluded_names = {
        "setup.exe",
        "install.exe",
    }

    programs = []

    for current_root, dirs, files in os.walk(root):

        # Évite la descente dans certains dossiers
        dirs[:] = [
            d for d in dirs
            if not (
                d.startswith(".")
                or d == "pfx"
                or (
                    current_root.endswith("drive_c")
                    and d.lower() == "windows"
                )
            )
        ]

        for file in files:
            lower = file.lower()

            if not lower.endswith(".exe"):
                continue

            if lower.startswith("unins"):
                continue

            if lower in excluded_names:
                continue

            programs.append(
                os.path.join(current_root, file)
            )

    return programs


def list_programs():
    programs = find_windows_programs()

    if not programs:
        print("No Windows programs found")
        return

    print("Detected Windows programs:")
    print("")

    for exe in sorted(programs):
        print(exe)

def _normalize(name: str):
    return re.sub(r"[^a-z0-9]", "", name.lower())


def find_proton_by_name(name: str):
    if not name:
        return None

    target = _normalize(name)

    best_match = None

    for base in PROTON_PATHS:
        base = os.path.expanduser(base)

        if not os.path.exists(base):
            continue

        try:
            for d in os.listdir(base):
                full = os.path.join(base, d)

                if not os.path.isdir(full):
                    continue

                norm = _normalize(d)

                # match exact
                if norm == target:
                    return full

                # match partiel (fallback intelligent)
                if target in norm or norm in target:
                    best_match = full

        except PermissionError:
            continue

    return best_match
