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
from pathlib import Path
from shutil import which
import configparser
from proton_autogen.loader import save_game_config, load_game_config, get_game_config_path
from proton_autogen.core import *
from proton_autogen.profile import *
from proton_autogen.i18n import *
from proton_autogen.stats import *

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
# ----------------------------------------------------------------------------------------------------
def finalize_session(exe_path, start_time, exit_code=None):
    """
    Finalise une session de jeu et met à jour les statistiques.

    Args:
        exe_path (str): chemin du jeu
        start_time (float): time.time() au lancement
        exit_code (int|None): code retour du process (si disponible)

    Returns:
        dict: résumé de la session
    """

    end_time = time.time()
    session_seconds = int(end_time - start_time)

    result = {
        "exe_path": exe_path,
        "session_seconds": session_seconds,
        "exit_code": exit_code,
        "status": "unknown",
        "updated": False
    }

    # -------------------------
    # ignore sessions trop courtes
    # -------------------------
    if session_seconds <= 0:
        result["status"] = "ignored_too_short"
        return result

    # -------------------------
    # interprétation du résultat
    # -------------------------
    if exit_code is None:
        result["status"] = "no_exit_code"
    elif exit_code == 0:
        result["status"] = "clean_exit"
    else:
        result["status"] = "crash_or_error"

    # -------------------------
    # update stats
    # -------------------------
    try:
        update_playtime(exe_path, session_seconds)
        result["updated"] = True
    except Exception as e:
        print("[proton-autogen] stats update failed:", e)
        result["error"] = str(e)

    return result
# ---------------------------------------------------------------------------------------------------

def run(exe_path: str, launch_mode="proton", prefix_mode="main"):
    start_time = time.time() # Stats
    result_code = 0 # Stats
    exe_path = os.path.abspath(exe_path)

    if not os.path.exists(exe_path):
        print(f"Error: file not found: {exe_path}")
        sys.exit(1)

    # Proton path (à adapter)
    #proton = os.path.expanduser(
    #    "~/.steam/debian-installation/compatibilitytools.d/GE-Proton10-34/"
    #)
    mangohud_available = has_mangohud()

    config = load_game_config(exe_path)
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
        proton = find_proton_by_name(saved_proton_name)

        if not proton:
            print("[proton-autogen] stored Proton missing → fallback")
            proton = find_proton()
    else:
        # By Default
        cfg_mangohud = False
        cfg_gamemode = False
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
        env = base_env(
            enable_mangohud=enable_mangohud,
            enable_gamemode=enable_gamemode,
            exe_path=exe_path,
            exe_type=exe_type
        )
        env["GE_PROTON"] = proton_path(proton)
        env["GAME_EXE"] = exe_path

        if enable_mangohud:
            if mangohud_available:
                print("[proton-autogen] MangoHud enabled")
                env["MANGOHUD"] = "1"
                env["MANGOHUD_DLSYM"] = "1"
                env["DXVK_HUD"] = "0"
                env.pop("LD_PRELOAD", None)
            else:
                print("[proton-autogen] WARNING: MangoHud requested but not installed")

        cmd = []

        if enable_gamemode:
            if has_gamemode():
                print("[proton-autogen] GameMode enabled")
                #cmd.append("gamemoderun")
                env["GAMEMODE"] = "1"
        elif DEBUG or VERBOSE:
            print("[proton-autogen] GameMode not found")

        cmd = [
            "proton-call",
            "-c", proton_path(proton),
            "-r", exe_path,
            "--",
        ] + [exe_path] + sys.argv[2:]

        print(f"[proton-autogen] Launching with {proton_name(proton)}")

        result_code = -1
        result_code = subprocess.run(cmd, env=env)
        #
        finalize_session(exe_path, start_time, result_code) # Stats
        sys.exit(result_code)

    elif launch_mode == "proton" and proton:

        # ----------------------------
        # Prefix resolution (IMPORTANT PART)
        # ----------------------------
        if config and config.get("prefix"):
            prefix_mode = config["prefix"].get("name", prefix_mode)
            print(f"[proton-autogen] LOAD CONFIG PREFIX: {prefix_mode}")

        result_code = -1
        result_code = run_game_proton(exe_path, exe_type, proton, "proton", enable_mangohud, enable_gamemode, prefix_mode)
        finalize_session(exe_path, start_time, result_code) # Stats
        sys.exit(result_code)

    elif launch_mode == "wine":

        result_code = -1
        result_code = run_standard(exe_path)
        finalize_session(exe_path, start_time, result_code) # Stats
        sys.exit(result_code)


#---------------------------------------------------------------------------------------------
def proton_name(p):
    if isinstance(p, dict):
        return p.get("name", "Unknown Proton")
    return os.path.basename(p) if p else "Unknown Proton"



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
            "xalia": None
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
        print("6) Save & Quit")
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

def find_windows_programs_ux_search(root=None):
    if root is None:
        root = Path.home()

    allowed_roots = [
        root / "Bureau",
        root / "Downloads",
        root / "Jeux",
        root / "Téléchargements",
    ]

    excluded_dirs = { ".steam", ".cache", "pfx", "drive_c", "windows", "old", "tmp", "dgVoodoo2", "stockages", "drivers", "bios", "JAVA", "www", "mail", "personnel", "virus", }
    excluded_names = { "setup.exe", "install.exe", }
    MAX_DEPTH = 6  # 👈 réglable

    programs = []

    for base in allowed_roots:
        if not base.exists():
            continue

        base_depth = len(base.parts)

        for path in base.rglob("*.exe"):

            # 🚀 filtre dossiers
            if any(part in excluded_dirs for part in path.parts):
                continue

            # 🚀 limite profondeur
            if len(path.parts) - base_depth > MAX_DEPTH:
                continue

            name = path.name.lower()

            if name.startswith("unins"):
                continue

            if name in excluded_names:
                continue

            programs.append(str(path))

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
