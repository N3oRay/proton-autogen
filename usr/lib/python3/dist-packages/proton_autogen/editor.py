
import os
import json
from pathlib import Path
from proton_autogen.utils.logger import StructuredLogger
from proton_autogen.config import VERSION, CONFIG_FILE, CONFIG_DIR, PREFIX_DIR, PREFIX_DIR_PATH
from proton_autogen.loader import get_game_config_path
from proton_autogen.profiles.init import detect_exe_type, choose_profile
from proton_autogen.loader import load_game_config
from proton_autogen.core import make_output_path, PREFIX_DIR_PATH
from proton_autogen.diag import find_all_protons, find_proton

import uuid

logger = StructuredLogger("proton-autogen.editor")


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


def list_prefixes():
    root = os.path.expanduser(PREFIX_DIR)

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


#Liste prefixes for UX:
def list_prefixes_ux():
    root = os.path.expanduser(PREFIX_DIR)

    prefixes = [
        "main",
        "shared",
        "auto",
        "custom",
        "Proton Custom",
    ]

    if os.path.isdir(root):
        for name in sorted(os.listdir(root)):
            path = os.path.join(root, name)

            if os.path.isdir(path) and name not in ("main", "shared", "auto", "custom", "Proton Custom"):
                prefixes.append(name)

    return prefixes


def choose_prefix(exe_path: str):
    prefixes = list_prefixes()
    root = os.path.expanduser(PREFIX_DIR)

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
                #name = f"auto-{uuid.uuid4().hex[:8]}"
                # choix automatique pour UI
                root = PREFIX_DIR_PATH
                path, name = make_output_path(exe_path, root)

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
    cfg_path, _ = get_game_config_path(exe_path)

    print("Checking config:", cfg_path)

    try:
        cfg = load_game_config(exe_path)

    except (json.JSONDecodeError, OSError) as e:
        print(f"Invalid config ignored: {cfg_path} ({e})")
        return None

    if not isinstance(cfg, dict):
        return None

    prefix = cfg.get("prefix")

    if not isinstance(prefix, dict):
        return None

    # Compatibilité anciens fichiers
    if "path" not in prefix:
        prefix["path"] = os.path.join(
            os.path.expanduser(PREFIX_DIR),
            prefix["name"]
        )

    return prefix

def find_existing_prefix_for_game_v1(exe_path: str):

    cfg_path, _ = get_game_config_path(exe_path)

    print("Checking config:", cfg_path)

    try:
        cfg = load_game_config(exe_path)

    except (json.JSONDecodeError, OSError) as e:
        print(f"Invalid config ignored: {cfg_path} ({e})")
        return None

    if not isinstance(cfg, dict):
        return None

    return cfg.get("prefix")


# add game for UX

def add_game_ux(exe_path: str, prefix=None):
    """
    Add game from GTK UI.
    No terminal interaction.
    """

    exe_path = os.path.abspath(exe_path)

    if not os.path.exists(exe_path):
        raise FileNotFoundError(
            f"Game file not found: {exe_path}"
        )

    os.makedirs(CONFIG_DIR, exist_ok=True)

    config_path, gid = get_game_config_path(exe_path)

    proton = find_proton()
    exe_type = detect_exe_type(exe_path)


    # ----------------------------------
    # PREFIX
    # ----------------------------------

    if prefix is None:

        existing_prefix = find_existing_prefix_for_game(exe_path)

        if existing_prefix:
            prefix = existing_prefix

        else:
            # choix automatique pour UI
            root = PREFIX_DIR_PATH
            path, name = make_output_path(exe_path, root)
            prefix = {
                "name": name,
                "path": path
            }


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


        "proton": (
            proton.get("path")
            if isinstance(proton, dict)
            else proton
        ),


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


    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(
            config,
            f,
            indent=2
        )


    return config

# -- rm game for UX:

def rm_game_ux(exe_path: str, config_path: str = None) -> bool:

    logger.info("Remove game requested")

    if isinstance(exe_path, dict):
        exe_path = exe_path.get("path")

    if not isinstance(exe_path, str):
        logger.warning(f"Invalid executable path: {exe_path!r}")
        return False

    target = None

    # 1) chemin fourni par l'UX
    if config_path:
        target = config_path
        logger.debug(f"Using provided config path: {target}")

    # 2) résolution normale
    else:
        exe_path = os.path.abspath(exe_path)
        target, _ = get_game_config_path(exe_path)

    # 3) fallback recherche réelle
    if not target or not os.path.isfile(target):
        logger.warning(
            "Config not found by id, searching by path..."
        )

        config_dir = os.path.expanduser(
            "~/.config/proton-autogen/games"
        )

        for filename in os.listdir(config_dir):
            if not filename.endswith(".json"):
                continue

            candidate = os.path.join(config_dir, filename)

            try:
                with open(candidate) as f:
                    config = json.load(f)

                if os.path.abspath(config.get("path", "")) == exe_path:
                    target = candidate
                    logger.info(
                        f"Found config by path match: {target}"
                    )
                    break

            except Exception:
                continue

    if not target or not os.path.isfile(target):
        logger.warning(
            f"Config file does not exist: {target}"
        )
        return False

    try:
        os.remove(target)
        logger.info(
            f"Game configuration removed successfully: {target}"
        )
        return True

    except OSError as e:
        logger.error(
            f"Failed to remove config {target}: {e}"
        )
        return False

# -- add game for UI
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
            prefix = choose_prefix(exe_path)
    else:
        prefix = choose_prefix(exe_path)

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
        current_env_profile = config.get("env_profile") or config.get("exe_type")
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
            prefix = choose_prefix(exe_path)

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
