#backend.py proton-autogen core
import os
import json
import hashlib
import re
import sys
import shutil
import subprocess
from pathlib import Path
from shutil import which
import configparser


CONFIG_FILE = os.path.expanduser("~/.config/proton-autogen.conf")
CONFIG_DIR = os.path.expanduser("~/.config/proton-autogen/games")

VERSION = "2.3.9"
# ----------------------------
# PROTON PATHS FIXED (robuste multi-distro)
# ----------------------------
DEFAULT_PROTON_PATHS = [
    # Steam natif
    "~/.steam/root/compatibilitytools.d",
    "~/.steam/steam/compatibilitytools.d",
    "~/.local/share/Steam/compatibilitytools.d",

    # Steam runtimes
    "~/.steam/steam/steamapps/common",
    "~/.local/share/Steam/steamapps/common",

    # system-wide (CachyOS / Arch / custom builds)
    "/usr/share/steam/compatibilitytools.d",
]

def load_proton_paths():
    def create_default_config():
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)

        sample = """[proton]
# Flatpak Steam in ~/.config/proton-autogen.conf by default
# Add custom Proton locations here
# You can separate paths with newlines, ":" or ";"

paths = ~/.var/app/com.valvesoftware.Steam/.local/share/Steam/compatibilitytools.d;~/.var/app/com.valvesoftware.Steam/.steam/root/compatibilitytools.d
"""

        try:
            with open(CONFIG_FILE, "w") as f:
                f.write(sample)
        except Exception:
            pass

    # ----------------------------
    # base paths (always safe)
    # ----------------------------
    base_paths = [os.path.expanduser(p) for p in DEFAULT_PROTON_PATHS]

    # ----------------------------
    # auto-create config if missing
    # ----------------------------
    if not os.path.isfile(CONFIG_FILE):
        create_default_config()
        return base_paths

    config = configparser.ConfigParser()

    try:
        config.read(CONFIG_FILE)

        if config.has_section("proton") and config.has_option("proton", "paths"):
            raw = config["proton"]["paths"]

            for p in re.split(r"[;:\n]", raw):
                p = os.path.expanduser(p.strip())
                if p:
                    base_paths.append(p)

    except Exception:
        # fail-safe: never break proton detection
        return base_paths

    # ----------------------------
    # normalization + deduplication (SAFE VERSION)
    # ----------------------------
    cleaned = []
    seen = set()

    for p in base_paths:
        if not p:
            continue

        # keep symlinks safe (Steam/Flatpak compatibility)
        p = os.path.expanduser(p)
        p = os.path.normpath(p)

        # stable dedup key
        key = p.lower()

        if key in seen:
            continue

        seen.add(key)
        cleaned.append(p)

    return cleaned

def proton_path(p):
    if isinstance(p, dict):
        return p.get("path")
    return p

def proton_name(p):
    if isinstance(p, dict):
        return p.get("name", "Unknown Proton")
    return os.path.basename(p) if p else "Unknown Proton"

def has_wine():
    return which("wine") is not None

def has_proton_call():
    return which("proton-call") is not None

def list_protons():
    protons = find_all_protons()

    if not protons:
        print("No Proton installation found")
        return

    selected = find_proton()

    # normalisation du selected → toujours un path string
    selected_path = None
    if isinstance(selected, dict):
        selected_path = selected.get("path")
    else:
        selected_path = selected

    # sécurité (évite None)
    selected_path = os.path.realpath(selected_path) if selected_path else None

    def sort_key(p):
        return os.path.basename(p).lower()

    print("Detected Proton installations:\n")

    for proton in sorted(protons, key=sort_key):
        proton_real = os.path.realpath(proton)

        is_selected = (selected_path == proton_real)
        suffix = " (selected)" if is_selected else ""

        print(f"  {os.path.basename(proton)}{suffix}")
        print(f"    {proton}\n")

def print_diagnostic():
    print("proton-autogen diagnostic\n")

    print(f"Version      : {VERSION}")
    print(f"Python       : {sys.version.split()[0]}\n")

    print("Runtime:")
    print(f"  proton-call : {'yes' if has_proton_call() else 'no'}")
    print(f"  wine        : {'yes' if has_wine() else 'no'}")
    print(f"  gamemode    : {'yes' if has_gamemode() else 'no'}")
    print(f"  mangohud    : {'yes' if has_mangohud() else 'no'}\n")

    print(f"Platform     : {sys.platform}\n")

    protons = find_all_protons()
    print(f"Detected Proton installations: {len(protons)}\n")

    if not protons:
        print("  none\n")
        return

    selected = find_proton()

    # ----------------------------
    # normalize selected → string path
    # ----------------------------
    if isinstance(selected, dict):
        selected_path = selected.get("path")
    else:
        selected_path = selected

    selected_path = os.path.realpath(selected_path) if selected_path else None

    # ----------------------------
    # sort once
    # ----------------------------
    protons_sorted = sorted(protons, key=lambda x: os.path.basename(x).lower())

    for proton in protons_sorted:
        proton_real = os.path.realpath(proton)

        marker = " [selected]" if selected_path and proton_real == selected_path else ""

        print(f"  {os.path.basename(proton)}{marker}")
        print(f"    {proton}")

    print("")

def find_all_protons():
    protons = []
    seen = set()

    def is_proton(name: str) -> bool:
        n = name.lower()

        # vrais candidats Proton
        return (
            "proton" in n
            or "ge-proton" in n
            or n.startswith("ge-proton")
            or "proton-ge" in n
            or "cachy" in n
            or "experimental" in n
            or "hotfix" in n
        )

    def normalize(name: str) -> str:
        return re.sub(r"[^a-z0-9]", "", name.lower())

    for base in load_proton_paths():
        base = os.path.expanduser(base)

        if not os.path.isdir(base):
            continue

        try:
            for d in os.listdir(base):
                full = os.path.join(base, d)

                if not os.path.isdir(full):
                    continue

                if not is_proton(d):
                    continue

                key = normalize(d)

                if key in seen:
                    continue

                seen.add(key)
                protons.append(full)

        except (PermissionError, FileNotFoundError):
            continue

    return protons
# ----------------------------
# SYSTEM PROTON DETECTION (FIXED)
# ----------------------------
# Known system-wide Proton locations.
# We intentionally avoid recursive scans of /usr/share
# and /usr/lib for performance and predictability.
def find_system_proton():
    locations = [
        "/usr/share/steam/compatibilitytools.d",
        "/usr/local/share/steam/compatibilitytools.d",
        "/usr/lib/steam/compatibilitytools.d",
    ]

    candidates = []

    def is_proton_name(name: str) -> bool:
        n = name.lower()

        return (
            "proton" in n
            or "ge-proton" in n
            or "proton-ge" in n
            or "experimental" in n
            or "hotfix" in n
            or "cachy" in n
        )

    for base in locations:

        if not os.path.isdir(base):
            continue

        try:
            for d in os.listdir(base):
                full = os.path.join(base, d)

                if (
                    os.path.isdir(full)
                    and is_proton_name(d)
                ):
                    candidates.append(full)

        except (PermissionError, FileNotFoundError):
            continue

    if not candidates:
        return None

    candidates.sort(
        key=lambda p: proton_score(
            os.path.basename(p)
        ),
        reverse=True
    )

    return os.path.realpath(candidates[0])


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

# ----------------------------
# PROTON SCORE (robuste)
# ----------------------------
def proton_score(name: str):
    name = name.lower()

    priority = 0
    if "cachy" in name:
        priority = 4
    elif "ge" in name:
        priority = 3
    elif "experimental" in name:
        priority = 2
    elif "proton" in name:
        priority = 1

    numbers = list(map(int, re.findall(r"\d+", name)))
    major = numbers[0] if len(numbers) > 0 else 0
    minor = numbers[1] if len(numbers) > 1 else 0

    return (priority, major, minor, name)


# ----------------------------
# MAIN FIXED FIND PROTON
# ----------------------------
def find_proton():
    candidates = []
    seen = set()

    def is_proton_dir(name: str) -> bool:
        return re.search(r"proton", name, re.IGNORECASE) is not None

    def add(path):
        if not path:
            return
        path = os.path.expanduser(path)
        path = os.path.realpath(path)

        if not os.path.exists(path):
            return

        if path in seen:
            return

        seen.add(path)

        candidates.append({
            "name": os.path.basename(path),
            "path": path
        })

    # scan steam + system
    for base in load_proton_paths():
        base = os.path.expanduser(base)

        if not os.path.exists(base):
            continue

        try:
            for d in os.listdir(base):
                full = os.path.join(base, d)

                if os.path.isdir(full) and is_proton_dir(d):
                    add(full)

        except (PermissionError, FileNotFoundError):
            continue

    # system proton explicit
    p_system_proton = find_system_proton()
    if p_system_proton:
        add(p_system_proton)

    if not candidates:
        return None

    candidates.sort(key=lambda c: proton_score(c["name"]), reverse=True)

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
        "proton": proton.get("path") if isinstance(proton, dict) else proton,
        "mangohud": False, # has_mangohud()
        "gamemode": False, # has_gamemode()
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

    candidates = []

    def score(name: str):
        n = name.lower()

        # priorité distributions Proton
        priority = 0
        if "ge" in n:
            priority += 30
        if "cachy" in n:
            priority += 25
        if "experimental" in n:
            priority += 10
        if "proton" in n:
            priority += 5

        # versioning (plus c’est grand, mieux c’est)
        numbers = [int(x) for x in re.findall(r"\d+", n)]
        major = numbers[0] if len(numbers) > 0 else 0
        minor = numbers[1] if len(numbers) > 1 else 0

        return (priority, major, minor)

    for base in load_proton_paths():
        base = os.path.expanduser(base)

        if not os.path.exists(base):
            continue

        try:
            for d in os.listdir(base):
                full = os.path.join(base, d)

                if not os.path.isdir(full):
                    continue

                norm = _normalize(d)

                # filtre strict : doit contenir proton OU être proton-like
                if "proton" not in norm:
                    continue

                # match exact
                if norm == target:
                    return full

                # match partiel
                if target in norm or norm in target:
                    candidates.append((score(d), full))

        except (PermissionError, FileNotFoundError):
            continue

    if not candidates:
        return None

    # meilleur match
    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]
