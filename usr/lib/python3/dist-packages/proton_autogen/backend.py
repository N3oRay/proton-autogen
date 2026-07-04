#backend.py proton-autogen
import os
import json
import hashlib
import re
import sys
import shutil
import subprocess
import uuid
import time
from gi.repository import GLib
from pathlib import Path
from shutil import which
from time import perf_counter
import configparser
from proton_autogen.loader import save_game_config, load_game_config, get_game_config_path
from proton_autogen.core import *
from proton_autogen.profile import *
from proton_autogen.i18n import *
from proton_autogen.stats import *
from proton_autogen.pa_log import show_result, handle_result, show_message
from proton_autogen.pa_log import notify_simple
from proton_autogen.diag import find_all_protons, find_proton
# new files:
from proton_autogen.dector import resolve_game_features
from proton_autogen.system import detect_system_info
from proton_autogen.session import finalize_session, notifications
from proton_autogen.proton_call import launch_proton_call


#notifications.notify("info", "Update", "Game launched")

#-----
# proton-autogen: improved profile system (launcher / DX11 / DX12 / oldgames)
# fixed environment leaks between profiles
# better WineD3D support for DX8/DX9 (UT99)
# stability fixes for Battle.net and legacy games
#-------------------------------------------
# Support legacy (Photoshop)
# ----------------------------
# PROTON PATHS FIXED (robuste multi-distro)
# ----------------------------

def print_runtime_info(proton, exe_path, mangohud_available):
    print("[proton-autogen] Runtime information")
    print(f"  Executable : {exe_path}")
    print(f"  Proton     : {proton_name(proton)}")
    print(f"  Path       : {proton_path(proton)}")
    print("  proton-call:", "detected" if has_proton_call() else "missing")
    print("  GameMode  :", "available" if has_gamemode() else "unavailable")
    print("  MangoHud  :", "available" if mangohud_available else "unavailable")
    print("")
# ---------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------

def run(exe_path: str, launch_mode="proton", prefix_mode="main"):
    start_time = time.time() # Stats
    result_code = 0 # Stats
    exe_path = os.path.abspath(exe_path)

    if not os.path.exists(exe_path):
        print(f"Error: file not found: {exe_path}")

        notifications.notify("warning", "Missing file", f"file not found: {exe_path}")
        sys.exit(1)

    # Proton path (à adapter)
    #proton = os.path.expanduser(
    #    "~/.steam/debian-installation/compatibilitytools.d/GE-Proton10-34/"
    #)
    mangohud_available = has_mangohud()

    config = load_game_config(exe_path)

    system = detect_system_info()  # ou équivalent existant dans core
    print("[proton-autogen] System information:")
    for key, value in system.items():
        print(f"  {key}: {value}")
    #-------------------------------- Compatibility old profil ------
    exe_type = None

    if config:
        exe_type = config.get("exe_type") or config.get("env_profile")

    if not exe_type:
        exe_type = detect_exe_type(exe_path)
    #---------------------------------------Mode PRO -------------------------
    if USER_PROFILE_DATA:
        exe_type = USER_PROFILE_DATA.get("base") or USER_PROFILE_DATA.get("name") or exe_type
    #-------------------------------------------------------------------------

    if config:
        saved_proton_name = config.get("proton")
        features = config.get("features", {})

        cfg_mangohud = normalize_flag(features.get("mangohud"), False)
        cfg_gamemode = normalize_flag(features.get("gamemode"), False)
        # Load features -----------------------------------------------
        rfeatures = resolve_game_features(
            {"features": features},
            system
        )
        # Message features -----------------------------------------------
        message = " | ".join(
            f"{key}: {value}"
            for key, value in rfeatures.items()
        )
        notifications.notify("info", "proton-autogen", message, ui=True)

        proton = find_proton_by_name(saved_proton_name)

        if not proton:
            print("[proton-autogen] stored Proton missing → fallback")
            proton = find_proton()
    else:
        # By Default
        cfg_mangohud = False
        cfg_gamemode = False
        rfeatures = None
        proton = find_proton()


    enable_mangohud = cfg_mangohud if config else False
    enable_gamemode = cfg_gamemode if config else False

    # CLI overrides (priorité utilisateur)
    if "--mangohud" in sys.argv:
        enable_mangohud = True

    if "--gamemode" in sys.argv:
        enable_gamemode = True


    if proton:
        print_runtime_info(proton, exe_path, mangohud_available)
    else:
        print("[proton-autogen] ERROR: No Proton installation found")
        print("")
        print("Install GE-Proton with:")
        print("  protonup-qt")
        print("")
        print("Or install Proton-GE from command line:")
        print("  protonup -d ~/.steam/root/compatibilitytools.d")
        print("")
        print("Then restart Steam and try again.")
        sys.exit(1)

    if launch_mode == "proton-call" and has_proton_call():
        launch_proton_call(
            exe_path=exe_path,
            proton=proton,
            system=system,
            features=rfeatures,
            enable_mangohud=enable_mangohud,
            enable_gamemode=enable_gamemode,
            start_time=start_time,
            extra_args=[]
        )

    elif launch_mode == "proton" and proton:

        # ----------------------------
        # Prefix resolution (IMPORTANT PART)
        # ----------------------------
        if config and config.get("prefix"):
            prefix_mode = config["prefix"].get("name", prefix_mode)
            #Message
            notifications.notify("info", "proton-autogen", f"LOAD CONFIG PREFIX : {prefix_mode}", ui=True)

        result_code = -1
        result_code = run_game_proton(exe_path=exe_path, exe_type=exe_type, proton=proton, system=system, features=rfeatures, enable_mangohud=enable_mangohud,
         enable_gamemode=enable_gamemode, prefix_mode=prefix_mode)
        if DEBUG or VERBOSE:
            print(type(result_code))
            print(result_code)

            if isinstance(result_code, subprocess.CompletedProcess):
                print(result_code.returncode)
        status = handle_result(result_code)
        finalize_session(exe_path, start_time, result_code) # Stats

        show_result(status, show_message)

        sys.exit(status["code"])

    elif launch_mode == "wine":

        result_code = -1
        result_code = run_standard(exe_path)
        status = handle_result(result_code)
        finalize_session(exe_path, start_time, result_code) # Stats

        show_result(status, show_message)

        sys.exit(status["code"])

#---------------------------------------------------------------------------------------------


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

def get_diagnostic_text():
    lines = []

    lines.append("proton-autogen diagnostic\n")

    lines.append(f"Version      : {VERSION}")
    lines.append(f"Python       : {sys.version.split()[0]}\n")

    lines.append("Runtime:")
    lines.append(f"  proton-call : {'yes' if has_proton_call() else 'no'}")
    lines.append(f"  wine        : {'yes' if has_wine() else 'no'}")
    lines.append(f"  gamemode    : {'yes' if has_gamemode() else 'no'}")
    lines.append(f"  mangohud    : {'yes' if has_mangohud() else 'no'}\n")

    lines.append(f"Platform     : {sys.platform}\n")

    protons = find_all_protons()
    lines.append(f"Detected Proton installations: {len(protons)}\n")

    if not protons:
        lines.append("  none\n")
        return "\n".join(lines)

    selected = find_proton()

    if isinstance(selected, dict):
        selected_path = selected.get("path")
    else:
        selected_path = selected

    selected_path = os.path.realpath(selected_path) if selected_path else None

    protons_sorted = sorted(protons, key=lambda x: os.path.basename(x).lower())

    for proton in protons_sorted:
        proton_real = os.path.realpath(proton)

        marker = " [selected]" if selected_path and proton_real == selected_path else ""

        lines.append(f"  {os.path.basename(proton)}{marker}")
        lines.append(f"    {proton}")

    lines.append("")
    return "\n".join(lines)



def normalize_flag(value, default=True):
    if value is None:
        return default
    if isinstance(value, str):
        return value.lower() in ("1", "true", "yes", "on")
    return bool(value)




def list_prefixes():
    root = os.path.expanduser("~/Documents/Proton/env")

    if not os.path.isdir(root):
        return []

    prefixes = []

    for name in sorted(os.listdir(root)):
        path = os.path.join(root, name)

        if not os.path.isdir(path):
            continue

        prefixes.append({
            "name": name,
            "path": path
        })

    return prefixes


def create_new_prefix():
    name = input("Prefix name (empty = auto): ").strip()

    if not name:
        name = f"auto-{uuid.uuid4().hex[:8]}"

    root = os.path.expanduser("~/Documents/Proton/env")
    path = os.path.join(root, name)

    os.makedirs(path, exist_ok=True)

    return name

def choose_prefix():
    prefixes = list_prefixes()
    root = os.path.expanduser("~/Documents/Proton/env")

    print("\nAvailable prefixes:\n")

    for idx, prefix in enumerate(prefixes, start=1):
        print(f"[{idx}] {prefix['name']}")

    print("[new] Create new prefix")

    while True:
        choice = input("\nSelection: ").strip().lower()

        # -------------------------
        # NEW PREFIX
        # -------------------------
        if choice == "new":
            name = input("Prefix name (empty = auto): ").strip()

            if not name:
                name = f"auto-{uuid.uuid4().hex[:8]}"

            path = os.path.join(root, name)
            os.makedirs(path, exist_ok=True)

            return {
                "name": name,
                "path": path
            }

        # -------------------------
        # EXISTING PREFIX
        # -------------------------
        try:
            idx = int(choice) - 1

            if 0 <= idx < len(prefixes):
                return prefixes[idx]

        except ValueError:
            pass

        print("Invalid selection")

def find_existing_prefix_for_game(exe_path: str):
    cfg = load_game_config(exe_path)

    if not cfg:
        return None

    return cfg.get("prefix")


def add_game(exe_path: str):
    exe_path = os.path.abspath(exe_path)

    if not os.path.exists(exe_path):
        print(f"Error: file not found: {exe_path}")
        return

    os.makedirs(CONFIG_DIR, exist_ok=True)
    config_path, gid = get_game_config_path(exe_path)

    proton = find_proton()
    exe_type = detect_exe_type(exe_path)

    # ----------------------------------
    # PREFIX LOGIC (reuse if exists)
    # ----------------------------------
    existing_prefix = find_existing_prefix_for_game(exe_path)

    if existing_prefix:
        print("\n[proton-autogen] Existing prefix found:")
        print(f"  {existing_prefix['name']} -> {existing_prefix['path']}")

        choice = input("Reuse this prefix ? (Y/n) : ").strip().lower()

        if choice not in ("n", "no"):
            prefix = existing_prefix
        else:
            prefix = choose_prefix()
    else:
        prefix = choose_prefix()

    config = {
        "id": gid,
        "name": os.path.basename(exe_path),
        "path": exe_path,

        "favorite": False,

        "playtime": {
            "seconds": 0,
            "launch_count": 0,
            "last_session": 0,
            "last_launch": None
        },

        "exe_type": exe_type,

        "proton": proton.get("path") if isinstance(proton, dict) else proton,

        # IMPORTANT
        "prefix": {
            "name": prefix["name"],
            "path": prefix["path"]
        },

        "features": {
            "mangohud": False,
            "gamemode": False,
            "xalia": None,
            "gpu": "auto"
        },

        "sync": {
            "esync": "auto",
            "fsync": "auto"
        },

        "env_profile": exe_type,

        "env": {
            "DXVK_ASYNC": "1"
        }
    }

    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

    print("[proton-autogen] Game added:")
    print(f"  name     : {config['name']}")
    print(f"  id       : {gid}")
    print(f"  profile  : {exe_type}")
    print(f"  prefix   : {prefix['name']}")
    print(f"  config   : {config_path}")


def choose_proton():
    protons = find_all_protons()

    if not protons:
        print("No Proton found.")
        return None

    # IMPORTANT: single source of truth
    protons = sorted(protons, key=lambda x: os.path.basename(x).lower())

    selected = find_proton()

    selected_path = None
    if isinstance(selected, dict):
        selected_path = selected["path"]
    else:
        selected_path = selected

    print("\nAvailable Protons:\n")

    for idx, p in enumerate(protons, start=1):
        mark = ""
        if selected_path and os.path.realpath(p) == os.path.realpath(selected_path):
            mark = " (current)"

        print(f"[{idx}] {os.path.basename(p)}{mark}")
        print(f"    {p}")

    print("[d] Auto (best match)")

    while True:
        choice = input("\nSelection: ").strip().lower()

        if choice == "d":
            return find_proton()

        try:
            idx = int(choice) - 1

            if 0 <= idx < len(protons):
                return protons[idx]
        except ValueError:
            pass

        print("Invalid selection")




# -- Save game for UI
def edit_game_ui(exe_path: str):

    if isinstance(exe_path, dict):
        exe_path = exe_path.get("path")

    if not isinstance(exe_path, str):
        return

    exe_path = os.path.abspath(exe_path)

    config_path, gid = get_game_config_path(exe_path)

    if not os.path.exists(config_path):
        print("[proton-autogen] Game not registered.")
        return

    with open(config_path, "r") as f:
        config = json.load(f)

    while True:
        print("\n=== Edit Game ===")
        current_env_profile = config.get("exe_type") or config.get("env_profile")
        print(f"1) Profile    : {current_env_profile}")
        print(f"2) Proton     : {os.path.basename(config['proton'])}")
        print(f"3) Prefix     : {config['prefix']['name']}")
        print(f"4) MangoHud   : {config['features']['mangohud']}")
        print(f"5) GameMode   : {config['features']['gamemode']}")
        print(f"6) GPU Mode   : {config['features'].get('gpu', 'auto')}")
        print("7) Save & Quit")
        print("0) Cancel")

        choice = input("\nSelection: ").strip()

        if choice == "1":
            print(f"\nCurrent profile: {current_env_profile}")
            print(f"Detected profile: {detect_exe_type(exe_path)}")

            profile = choose_profile()

            if profile is None:
                config["env_profile"] = detect_exe_type(exe_path)
            else:
                config["env_profile"] = profile

        elif choice == "2":
            proton = choose_proton()

            if proton:
                config["proton"] = proton["path"] if isinstance(proton, dict) else proton
                print(f"Selected Proton: {os.path.basename(config['proton'])}")
            else:
                print("No Proton selected.")

        elif choice == "3":
            prefix = choose_prefix()

            config["prefix"] = {
                "name": prefix["name"],
                "path": prefix["path"]
            }

        elif choice == "4":
            current = config["features"].get("mangohud", False)
            config["features"]["mangohud"] = not current

        elif choice == "5":
            current = config["features"].get("gamemode", False)
            config["features"]["gamemode"] = not current

        elif choice == "6":
            modes = ["auto", "safe", "balanced", "performance"]

            current = config["features"].get("gpu", "auto")

            print("\nGPU mode:")
            for i, mode in enumerate(modes, 1):
                marker = "*" if mode == current else " "
                print(f"{i}) [{marker}] {mode}")

            sel = input("Selection: ").strip()

            if sel in ("1", "2", "3", "4"):
                config["features"]["gpu"] = modes[int(sel) - 1]

        elif choice == "7":
            with open(config_path, "w") as f:
                json.dump(config, f, indent=2)

            print("[proton-autogen] Configuration updated.")
            return

        elif choice == "0":
            print("[proton-autogen] Cancelled.")
            return

        else:
            print("Invalid selection.")



def load_registered_games():
    games_dir = Path.home() / ".config/proton-autogen/games"

    if not games_dir.exists():
        return []

    games = []

    for file in games_dir.glob("*.json"):

        try:
            with file.open("r", encoding="utf-8") as f:
                data = json.load(f)

            exe = data.get("path")

            if not exe:
                continue

            games.append({
                "id": data.get("id"),
                "name": data.get("name") or Path(exe).name,
                "path": exe,
                "source": "database"
            })

        except (json.JSONDecodeError, OSError) as e:
            print(f"Erreur lecture {file}: {e}")

    return games

def load_registered_games_ux():
    """
    Retourne uniquement les chemins des .exe déjà enregistrés
    Format compatible avec find_windows_programs_ux()
    """

    games = load_registered_games()

    return [
        game["path"]
        for game in games
        if game.get("path")
    ]

def find_windows_programs_ux(root=None):

    programs = []
    programs.extend(load_registered_games_ux())
    programs.extend(find_windows_programs_ux_search(root))

    # suppression doublons
    return list(dict.fromkeys(programs))


"""
Recherche les programmes Windows (.exe) dans les dossiers utilisateur
et retourne leurs chemins.
"""
excluded_dirs = {
    # cache / temp
    ".cache", "cache", "tmp", ".tmp", "temp", ".temp", "appcache", ".cargo", '.config', "configs",
    # dev
    "__pycache__", "node_modules", ".git", ".svn", "JAVA", "www", ".gnupg", ".p2", ".rpmdb", ".rustup", ".ssh", ".var", ".vnc", ".nuget", ".omnisharp", ".m2", ".pki", ".lime", ".java",
    ".eclipse", ".fltk", ".fonts", ".dotnet", ".dbus", ".config", ".icons", ".conky", ".swt", ".templateengine", ".themes", ".thunderbird", ".npm", ".gvfs",
    ".uno", "pipeline", "eclipse-workspace", "eclipse-installer"
    # personnal
    "Musique", "Modèles", "Images", "customFiles", "docs", "bsa", "pdf", "Serene-Conky", ".mozilla", "os", ".wavemonrc", "steal",

    # gaming
    ".steam", "dgVoodoo2", "deb-installer", "depotcache", "friends", "linux64", "linux32",


    # steam apps
    "steamui", "steamrt64", "steamrt32", "userdata", "ubuntu12_32", "ubuntu12_64", "resource", "package", "root", "sdk64", "bin64", "bin32", "bin", "clientui", "controller_base",

    # Proton
    "compatibilitytools.d",

    # backups
    "backup", "backups", "old", "recovery", "stockages", "zip", "tar", "Vidéos", "Modèles",

    # misc noise
    "drivers", "bios", "logs", "log", "old", "tmp", "www", "mail", "personnel", "virus", "malware",
}
    #excluded_dirs = { ".steam", ".cache", "pfx", "drive_c", "windows", "old", "tmp", "dgVoodoo2", "stockages", "drivers", "bios", "JAVA", "www", "mail", "personnel", "virus", }
excluded_names = { "setup.exe", "install.exe", }
MAX_DEPTH = 6  # 👈 réglable


def find_windows_programs_ux_search(root=None):
    start = perf_counter()

    root = Path.home() if root is None else Path(root)

    allowed_roots = [
        root / "Bureau",
        root / "Downloads",
        root / "Jeux",
        root / "Téléchargements",
    ]

    programs = []

    for base in allowed_roots:
        if not base.is_dir():
            continue

        base_depth = len(base.parts)

        for dirpath, dirnames, filenames in os.walk(base):

            depth = len(Path(dirpath).parts) - base_depth
            if depth >= MAX_DEPTH:
                dirnames.clear()
                continue

            dirnames[:] = [
                d for d in dirnames
                if d not in excluded_dirs
            ]

            for filename in filenames:
                name = filename.lower()

                if not name.endswith(".exe"):
                    continue

                if name.startswith("unins"):
                    continue

                if name in excluded_names:
                    continue

                programs.append(str(Path(dirpath) / filename))

    print(f"The program search finished in {perf_counter() - start:.3f}s")

    return programs



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

def list_programs_ux(lang: str = "en"):
    programs = find_windows_programs_ux()

    if not programs:
        return []

    result = []

    for exe in sorted(programs):
        config = load_game_config(exe) or {}

        badges = get_game_badges({
            "favorite": config.get("favorite", False),
            "playtime": config.get("playtime", {}),
        },lang)

        result.append({
            "name": config.get("name", exe.split("/")[-1]),
            "path": exe,
            "exe_type": config.get("exe_type", detect_exe_type(exe)),
            "proton": config.get("proton", ""),
            "prefix": config.get("prefix", {"name": "main"}),
            "features": config.get("features", {
                "mangohud": False,
                "gamemode": False,
            }),

            "favorite": config.get("favorite", False),
            "playtime": config.get("playtime", {
                "seconds": 0,
                "launch_count": 0,
                "last_session": 0,
                "last_launch": None,
            }),
            "badges": badges,   # 👈 NEW
        })

    return result

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
