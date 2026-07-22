#core.py proton-autogen

import os
import sys
import subprocess
import hashlib
import json
from collections import defaultdict

from pathlib import Path

from proton_autogen.config import VERSION, CONFIG_FILE, CONFIG_DIR, PREFIX_DIR, PREFIX_DIR_PATH
from proton_autogen.utils.logger import StructuredLogger
from proton_autogen.progress import Progress
from proton_autogen.pa_log import log_profile_env, log_profile_summary, log_mangohud_env, log_executable_info

from proton_autogen.notify import notifications
from proton_autogen.profiles.def_env import ENV_VARS

from proton_autogen.profiles.legacy import env_legacy_app, env_oldgame, env_ut3, env_quake
from proton_autogen.profiles.dx8 import env_dx8dg
from proton_autogen.profiles.dx9 import env_dx9, env_dx9dg, env_dx9opengl
from proton_autogen.profiles.dx11 import env_dx11, env_dx11BNet
from proton_autogen.profiles.modern import env_dx12
from proton_autogen.profiles.engines import env_goldsrc_full, env_gold_test, env_goldsrc, env_ut99
from proton_autogen.profiles.desktop import env_desktop, env_win95, env_win95Beta, env_DDraw
from proton_autogen.profiles.launcher import env_launcher, env_install_clean
from proton_autogen.profiles.type_profile import env_gtav_compat, env_gtav_x11, env_gtav_safe
from proton_autogen.profiles.dotnet_csharp import env_dotnet_csharp
from proton_autogen.profiles.dotnet import env_dotnet

from proton_autogen.detection.analyser import has_proton_call, has_wine, has_mangohud, has_gamemode
from proton_autogen.detection.proton import DEFAULT_PROTON_PATHS
from proton_autogen.detection.mangohud import find_mangohud_shim, check_mangohud_abi
from proton_autogen.dector import resolve_game_features, gpu_env

from proton_autogen.util_path import proton_path, proton_name
from proton_autogen.about import afficher_abouts, afficher_abouts_label


import configparser


DEBUG = "--debug" in sys.argv
VERBOSE = "--verbose" in sys.argv
#-------------------------- Profile PRO -------------------
USER_PROFILE = None
USER_PROFILE_DATA = None
#-------------------------- Init Log -------------------
logger = StructuredLogger("proton-autogen.core")

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

    # ------------------------------------
    # normalization + deduplication (SAFE)
    # ------------------------------------
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

#------------------------------------------------------------------------------------
def detect_help_env_lang():
    """
    Détecte la langue pour --help-env :
    priorité = CLI > env LANGUAGE > défaut en
    """

    # 1. Override CLI
    if "--en" in sys.argv:
        return "en"
    if "--fr" in sys.argv:
        return "fr"

    # 2. Variable d'environnement système
    lang_env = os.environ.get("LANGUAGE") or os.environ.get("LANG")

    if lang_env:
        lang_env = lang_env.lower()

        if lang_env.startswith("fr"):
            return "fr"
        if lang_env.startswith("en"):
            return "en"

    # 3. défaut
    return "en"


def print_help_env(lang="fr"):
    groups = defaultdict(list)

    for var in ENV_VARS:
        groups[var.get("type", "unknown")].append(var)

    for group, vars_ in sorted(groups.items()):
        print(f"\n[{group.upper()}]\n")

        for var in vars_:
            desc = var.get("description_en" if lang == "en" else "description_fr", "")
            print(f"- {var['name']}: {desc}")
#-----------------------------------------------------------------------------------------------

def apply_user_profile(env, profile):
    if not profile:
        return env

    logger.info(f"[proton-autogen] FORCE PROFILE USER: {profile.get('name', 'unknown')}")

    # safe override
    for k, v in profile.get("env", {}).items():
        env[k] = str(v)

    # safe removals only (whitelist possible plus tard)
    for k in profile.get("remove", []):
        env.pop(k, None)

    return env

def load_user_profile(name):
    path = os.path.expanduser(
        f"~/.config/proton-autogen/profiles/{name}.json"
    )

    if not os.path.exists(path):
        return {}

    with open(path, "r") as f:
        return json.load(f)

#---------------------------------------------------------------------
# set des variables autorisées
ALLOWED_ENV_VARS = {var["name"] for var in ENV_VARS}


def filter_env(env: dict) -> dict:
    """
    Ne garde que les variables déclarées dans ENV_VARS.
    """
    return {k: v for k, v in env.items() if k in ALLOWED_ENV_VARS}

#------------------------------------------------------------------------------
# new version for extract variables only ALLOWED_ENV_VARS in ENV_VARS
def export_default_profiles():
    base_dir = os.path.expanduser("~/.config/proton-autogen/profiles")
    os.makedirs(base_dir, exist_ok=True)

    profiles = {
        "legacy": env_legacy_app(),
        "launcher": env_launcher(),
        "dx11": env_dx11(),
        "dx11Bnet": env_dx11BNet(),
        "dx12": env_dx12(),
        "oldgame": env_oldgame(),
        "dx8dg": env_dx8dg(),
        "dx9dg": env_dx9dg(),
        "dx9": env_dx9(),
        "dx9opengl": env_dx9opengl(),
        "gtav_compat": env_gtav_compat(),
        "gtav_x11": env_gtav_x11(),
        "gtav_safe": env_gtav_safe(),
        "dotnet_csharp": env_dotnet_csharp(),
        "install": env_install_clean(),
        "ut99": env_ut99(),
        "quake": env_quake(),
        "win95": env_win95(),
        "directdraw": env_DDraw(),
        "ut3": env_ut3(),
        "valve": env_goldsrc(),
        "desktop": env_desktop(),
        "dotnet": env_dotnet(),
    }

    for name, env in profiles.items():

        # ✅ filtrage strict ici
        filtered_env = filter_env(env)

        data = {
            "name": name,
            "env": filtered_env,
            "remove": [],
            "base": name
        }

        path = os.path.join(base_dir, f"{name}.json")

        with open(path, "w") as f:
            json.dump(data, f, indent=2)

        print(f"[export] {name}.json generated ({len(filtered_env)} vars)")
#------------------------------------------------------------------------------
# old version for full extract variables
def export_default_profiles_full():
    base_dir = os.path.expanduser("~/.config/proton-autogen/profiles")
    os.makedirs(base_dir, exist_ok=True)

    profiles = {
        "legacy": env_legacy_app(),
        "launcher": env_launcher(),
        "dx11": env_dx11(),
        "dx11Bnet": env_dx11BNet(),
        "dx12": env_dx12(),
        "dx9": env_dx9(),
        "dx8dg": env_dx8dg(),
        "dx9dg": env_dx9dg(),
        "dx9opengl": env_dx9opengl(),
        "gtav_compat": env_gtav_compat(),
        "gtav_x11": env_gtav_x11(),
        "gtav_safe": env_gtav_safe(),
        "dotnet_csharp": env_dotnet_csharp(),
        "install": env_install_clean(),
        "oldgame": env_oldgame(),
        "ut99": env_ut99(),
        "quake": env_quake(),
        "win95": env_win95(),
        "directdraw": env_DDraw(),
        "ut3": env_ut3(),
        "valve": env_goldsrc(),
        "desktop": env_desktop(),
        "dotnet": env_dotnet(),
    }


    for name, env in profiles.items():

        data = {
            "name": name,
            "env": env,
            "remove": [],
            "base": name
        }

        path = os.path.join(base_dir, f"{name}.json")

        with open(path, "w") as f:
            json.dump(data, f, indent=2)

        print(f"[export] {name}.json generated")

def load_profile_from_cli(sys_argv):
    idx = sys_argv.index("--profile")

    if idx + 1 >= len(sys_argv):
        logger.error("ERROR: --profile requires a name")
        sys.exit(1)

    name = sys_argv[idx + 1]
    profile = load_user_profile(name)

    if not profile:
        logger.error(f"ERROR: profile not found: {name}")
        sys.exit(1)

    return name, profile
#-----------------------------------------------------------------------------
def print_proton_paths():
    print("Proton search paths")
    print("───────────────────")

    seen = set()
    proton_count = 0
    steam_runtime_count = 0

    for path in load_proton_paths():
        expanded = os.path.expanduser(path)
        real = os.path.realpath(expanded)

        # Dedup Steam symlinks
        if real in seen:
            continue
        seen.add(real)

        if not os.path.isdir(expanded):
            print(f"✗ {expanded}")
            continue

        try:
            entries = [
                e for e in os.listdir(expanded)
                if os.path.isdir(os.path.join(expanded, e))
            ]
        except (PermissionError, FileNotFoundError):
            print(f"✗ {expanded} (unreadable)")
            continue

        count = len(entries)

        # Classification
        if "compatibilitytools.d" in expanded:
            label = "Compatibility Tools"
            proton_count += count
        elif "steamapps/common" in expanded:
            label = "Steam Runtimes"
            steam_runtime_count += count
        else:
            label = "System"
            proton_count += count

        if count == 0:
            print(f"⚠ {expanded} (empty)")
        else:
            print(f"✓ {expanded} ({count} entries)")

        print(f"   [{label}]")

        for e in sorted(entries):
            print(f"   • {e}")

    print("")
    print(f"Total compatibility tools: {proton_count}")
    print(f"Steam runtimes: {steam_runtime_count}")
    print("")
    print("Note:")
    print("  Compatibility tools = real Proton builds")
    print("  Steam runtimes = execution dependencies (not Proton)")




#-----------------------------------------------------------
# PROFILE HUD
#-----------------------------------------------------------

def apply_dxvk_hud(env, exe_type, enable_mangohud, debug_mode=False):
    """
    Apply DXVK HUD settings compatible with proton-autogen.
    """

    # MangoHud override
    if enable_mangohud:
        env.pop("DXVK_HUD", None)
        return env

    SAFE_PROFILES = ["dotnet_csharp", "dotnet"]

    # Debug mode
    if debug_mode and exe_type not in SAFE_PROFILES:
        env["DXVK_HUD"] = "devinfo,fps,version"
        return env

    if debug_mode and exe_type in SAFE_PROFILES:
        env["DXVK_HUD"] = "0"
        return env

    # Default clean state
    env.pop("DXVK_HUD", None)
    return env



# MAKE PREFIX -----------------------------------------------------
def make_output_path(exe_path: str, root: str) -> tuple[str, str]:
    """Construit un chemin de sortie unique à partir du chemin d'un exécutable.

    Si l'exécutable est déjà situé dans un préfixe Proton (.../<prefix>/pfx/...),
    le nom du préfixe existant est réutilisé.
    """

    logger.info(f"make_output_path EXE PATH: {exe_path}")

    path = Path(exe_path)

    # Recherche d'un dossier "pfx"
    parts = path.parts
    if "pfx" in parts:
        pfx_index = parts.index("pfx")
        if pfx_index > 0:
            prefix_name = parts[pfx_index - 1]
            prefix_path = os.path.join(root, prefix_name)

            logger.info(
                f"Préfixe Proton détecté : {prefix_name}"
            )
            return prefix_path, prefix_name

    # Comportement actuel
    name = path.stem

    safe_name = (
        name.replace(" ", "_")
            .replace("/", "_")
            .replace("\\", "_")
    )

    short_hash = hashlib.md5(exe_path.encode("utf-8")).hexdigest()[:8]

    prefix_name = f"{safe_name}-{short_hash}"
    prefix_path = os.path.join(root, prefix_name)

    logger.info(
        f"Préfixe généré : {prefix_path} ({prefix_name})"
    )

    return prefix_path, prefix_name


# Return the Wine/Proton prefix path for the selected prefix mode.
def get_prefix_path(prefix_mode: str, exe_path: str) -> str:

    root = PREFIX_DIR_PATH

    if prefix_mode != "auto":
        # déjà résolu → on le traite comme prefix direct
        return os.path.join(root, prefix_mode)

    if prefix_mode == "auto":
        output, short_hash = make_output_path(exe_path, root)

        return output



def get_prefix_path_v2(prefix_mode: str, exe_path: str) -> str:

    root = PREFIX_DIR_PATH

    if prefix_mode == "auto":
        output, short_hash = make_output_path(exe_path, root)

        return output

    if prefix_mode.startswith("auto-"):
        # déjà résolu → on le traite comme prefix direct
        return os.path.join(root, prefix_mode)

    prefixes = {
        "main": os.path.join(root, "main"),
        "shared": os.path.join(root, "shared"),
        "Battle": os.path.join(root, "Battle"),
        "Battle.net": os.path.join(root, "Battle.net"),
        "custom": os.path.join(root, "custom"),
        "Proton Custom": os.path.join(root, "Proton Custom"),
        #"custom": os.path.expanduser("~/Documents/Proton/env/Proton Custom"),
    }

    return prefixes.get(prefix_mode, prefixes["main"])

def add_ld_preload(env, library):
    """
    Ajoute une bibliothèque à LD_PRELOAD sans écraser
    les bibliothèques déjà présentes.
    """
    if not os.path.exists(library):
        logger.warn(f"Missing library: {library}")
        return env

    current = env.get("LD_PRELOAD", "")

    if current:
        if library not in current.split(":"):
            env["LD_PRELOAD"] = f"{library}:{current}"
    else:
        env["LD_PRELOAD"] = library

    return env


def is_32bit_exe(path):
    return get_exe_arch(path) == "32bit"

# -------------------------------------------------------------------------------------------------------------------------------------
# Two independent threads handle the simultaneous reading of standard and error outputs to ensure smooth display and prevent deadlocks.
# -------------------------------------------------------------------------------------------------------------------------------------
from pathlib import Path
import subprocess
import threading


def _read_stdout(pipe):
    for line in pipe:
        logger.info(line, end="")


def _read_stderr(pipe, filters):
    for line in pipe:
        if any(f in line for f in filters):
            continue
        logger.warn(line, end="")



def run_filtered(cmd, env=None, filters=None, cwd=None):

    if filters is None:
        filters = []

    process = subprocess.Popen(
        cmd,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )

    t_out = threading.Thread(target=_read_stdout, args=(process.stdout,))
    t_err = threading.Thread(target=_read_stderr, args=(process.stderr, filters))

    t_out.start()
    t_err.start()

    process.wait()

    t_out.join()
    t_err.join()

    return process.returncode

# -------------------------------------------------------------------------------------------------------------------------------------

# Wine fallback execution.
# The executable is started from its parent directory to preserve
# relative paths required by some applications (DLLs, assets, etc.).
def run_standard(exe_path: str):
    logger.info("[proton-autogen] Proton unavailable → using Wine fallback")

    if not has_wine():
        logger.error(
            """No runtime found.

        Missing:
          - Proton
          - Wine

        Install Wine:
          sudo apt install wine"""
        )
        sys.exit(1)

    if not Path(exe_path).is_file():
        logger.error(f"✗ File not found: {exe_path}")
        sys.exit(1)

    try:
        exe_path = Path(exe_path).resolve()

        result = subprocess.run(
            ["wine", str(exe_path)],
            cwd=str(exe_path.parent)
        )

        #sys.exit(result.returncode)
        return result.returncode

    except Exception as e:
        logger.error(f"✗ Error running {exe_path} with Wine: {e}")
        return 1



def base_env(enable_mangohud=False, enable_gamemode=False, exe_path="", exe_type="", prefix_path=None, proton_dir=None):
    logger.info("Initializing environment", exe_type=exe_type, mangohud=enable_mangohud, gamemode=enable_gamemode)

    """
    Build a clean Wine/Proton environment for game execution.

    Profiles:
        launcher -> Battle.net, EA App, Ubisoft Connect
        dx11     -> standard games (DX11/DX9 via DXVK)
        dx12     -> VKD3D-Proton games
        oldgame  -> DX8/DX9 WineD3D fallback
    """
    env_factories = {
        "launcher": env_launcher,
        "legacy": env_legacy_app,
        "desktop": env_desktop,
        "dx11": env_dx11,
        "dx11Bnet": env_dx11BNet,
        "dx12": env_dx12,
        "ut99": env_ut99,
        "quake": env_quake,
        "win95": env_win95,
        "directdraw": env_DDraw,
        "ut3": env_ut3,
        "oldgame": env_oldgame,
        "valve": env_goldsrc,
        "dx9": env_dx9,
        "dx8dg": env_dx8dg,
        "dx9dg": env_dx9dg,
        "dx9opengl": env_dx9opengl,
        "gtav_compat": env_gtav_compat,
        "gtav_x11": env_gtav_x11,
        "gtav_safe": env_gtav_safe,
        "dotnet_csharp": env_dotnet_csharp,
        "dotnet": env_dotnet,
    }

    factory = env_factories.get(exe_type, env_dx11)

    env = factory(
        prefix=prefix_path,
        proton_path=proton_dir,
        exe_path=exe_path
    )


    # FORCE CLEAN GRAPHICS PIPELINE FOR OLD GAMES
    if exe_type in ["dx8dg", "dx9dg"]:
        env["DXVK_HUD"] = ""
        env.pop("DXVK_HUD", None)
        env.pop("VKD3D_CONFIG", None)

        # IMPORTANT: kill DXVK behavior fully
        env["WINEDLLOVERRIDES"] = (
            env.get("WINEDLLOVERRIDES", "") + ";dxgi=n;d3d11=n;d3d10=n"
        )

    # -----------------------------
    # MangoHud
    # -----------------------------
    if enable_mangohud and has_mangohud():
        env["MANGOHUD"] = "1"
        env["MANGOHUD_DLSYM"] = "1"
    else:
        env.pop("MANGOHUD", None)
        env.pop("MANGOHUD_DLSYM", None)

    # -----------------------------
    # GameMode
    # -----------------------------
    if enable_gamemode and has_gamemode():
        env["GAMEMODE"] = "1"

    # -----------------------------
    # DEBUG HUD (safe only)
    # -----------------------------
    env = apply_dxvk_hud(
        env,
        exe_type,
        enable_mangohud,
        debug_mode=DEBUG
    )

    # -----------------------------
    # USER PRO
    # -----------------------------
    profile = USER_PROFILE_DATA if USER_PROFILE_DATA else None
    env = apply_user_profile(env, profile)

    if DEBUG:
        env["PROTON_LOG"] = "1"
        #env["WINEDEBUG"] = "-all" #WINEDEBUG=+err,+warn
        #env["WINEDEBUG"] = "+err,+warn"
        #env["WINEDEBUG"] = "+seh,+tid"
        env["WINEDEBUG"] = "+loaddll,+module"
    elif VERBOSE:
        env["PROTON_LOG"] = "1"
        #env["WINEDEBUG"] = "-all,-trace,-relay,-seh"
        env["WINEDEBUG"] = "+seh,+loaddll,+tid"
    else:
        env["PROTON_LOG"] = "0"
    return env

def get_exe_arch(path):
    result = subprocess.run(
        ["file", path],
        capture_output=True,
        text=True
    )

    output = result.stdout.lower()

    if "pe32+" in output:
        return "64bit"

    if "pe32" in output:
        return "32bit"

    return "unknown"


def add_ld_preload(env, lib):
    existing = env.get("LD_PRELOAD", "")
    if existing:
        if lib not in existing.split(":"):
            env["LD_PRELOAD"] = lib + ":" + existing
    else:
        env["LD_PRELOAD"] = lib
    return env


def run_game_proton(exe_path, exe_type, proton,
                    system, features,
                    enable_mangohud=False, enable_gamemode=False,
                    prefix_mode="main", progress=None):

    if progress is None:
        progress = Progress()


    arch = get_exe_arch(exe_path)
    if progress is not None:
        progress.update( 85, f"EXE architecture: {arch}" )
    notifications.notify("info", "INFO", f"EXE architecture: {arch}")

    game_id = hashlib.md5(exe_path.encode()).hexdigest()

    # -------------------------
    # Proton Path & Prefix Path
    # -------------------------
    prefix_path = get_prefix_path(prefix_mode, exe_path)
    proton_dir = proton_path(proton)

    if not os.path.isdir(proton_dir):
        logger.error(
            f"Invalid Proton path: {proton_dir}"
        )
        return -1

    # =========================
    # PROTON MODE
    # =========================
    env = base_env(
        enable_mangohud=enable_mangohud,
        enable_gamemode=enable_gamemode,
        exe_path=exe_path,
        exe_type=exe_type,
        prefix_path=prefix_path,
        proton_dir=proton_dir
        )


    #Notification UX:
    notifications.notify("info", "Prefix mode", f"Prefix mode : {prefix_mode}")
    notifications.notify("info", "Prefix path", f"Prefix path : {prefix_path}")

    env["STEAM_COMPAT_DATA_PATH"] = prefix_path
    os.makedirs(prefix_path, exist_ok=True)

    env["STEAM_COMPAT_CLIENT_INSTALL_PATH"] = os.path.expanduser("~/.steam/steam")
    env["STEAM_COMPAT_TOOL_PATHS"] = proton_dir
    # -------------------------
    # GPU layer (UX + system merge)
    # -------------------------
    env.update(gpu_env(system, features))

    cmd = [
        os.path.join(proton_path(proton), "proton"),
        "run",
        exe_path
    ]

    # =========================
    # COMMON OPTIONS
    # =========================

    if enable_mangohud and has_mangohud():
        env["MANGOHUD"] = "1"
        env["MANGOHUD_DLSYM"] = "1"
        env["DXVK_HUD"] = "0"

        # FPS cap only if needed
        if "fps_limit" not in env.get("MANGOHUD_CONFIG", ""):
            env["MANGOHUD_CONFIG"] = "fps_limit=60"

        is_32bit = is_32bit_exe(exe_path)

        # OpenGL only for legacy DX9 / old games
        if exe_type in ["dx9", "dx9opengl", "oldgame", "ut99", "ut3", "valve"]:
            env["MANGOHUD_OPENGL"] = "1"
        else:
            env.pop("MANGOHUD_OPENGL", None)

        # 32-bit shim only when needed
        if is_32bit:
            logger.info("32-bit legacy game detected")

            mangohud_shim = find_mangohud_shim()

            if mangohud_shim and os.path.exists(mangohud_shim):
                if not check_mangohud_abi(mangohud_shim):
                    logger.info("MangoHud ABI mismatch detected - skipping")
                else:
                    env = add_ld_preload(env, mangohud_shim)
                    logger.info("Loaded MangoHud 32-bit shim")
            else:
                logger.info("No MangoHud 32-bit shim found, relying on Proton runtime")

        # optional: Vulkan explicit toggle
        if exe_type in ["vulkan", "dxvk"]:
            env["MANGOHUD"] = "1"
    else:
        env.pop("MANGOHUD", None)

    if enable_gamemode and has_gamemode():
        env["GAMEMODE"] = "1"

    # Set Default env:
    env.setdefault("STEAM_COMPAT_APP_ID", "480")
    env.setdefault("SteamAppId", "480")
    env.setdefault("SteamGameId", "480")


    if VERBOSE or DEBUG:
        # Affichage des log debug CLI
        log_profile_env(logger, env)
    else:
        # Affichage des log summary CLI
        log_profile_summary(logger, env, exe_type)
    if progress is not None:
        progress.update( 83, f"Launch mode: Proton " )
    logger.info(f"Launch mode: Proton ")


    if enable_mangohud and has_mangohud():
        # DEBUG ENVIRONMENT
        log_mangohud_env(logger, env)

        filters = [ "wrong ELF class", ]
        result_code = -1
        # Code KO

        cmd_cwd = os.path.dirname(exe_path)

        if not os.path.isdir(cmd_cwd):
            logger.warning(
                f"Invalid cwd {cmd_cwd}, using home"
            )
            cmd_cwd = os.path.expanduser("~")

        returncode = run_filtered(
            cmd,
            env=env,
            filters=filters,
            cwd=cmd_cwd,
        )

        return returncode
    else:
        # Code OK
        result_code = -1
        cmd_cwd = os.path.dirname(exe_path)
        #logger
        log_executable_info(logger, exe_path, cmd_cwd)
        if progress is not None:
            progress.update( 84, f"EXE PATH   : {exe_path}" )

        returncode = 0
        if VERBOSE or DEBUG:
            proc = subprocess.run(
                cmd,
                cwd=cmd_cwd,
                env=env,
                text=True,
                capture_output=True,
            )

            logger.info(proc.stdout)
            logger.warn(proc.stderr)
            logger.info(proc.returncode)
            returncode = proc.returncode
        else:
            proc = subprocess.Popen(
                cmd,
                cwd=cmd_cwd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            # Logger with pourcent
            percent = 85
            for line in proc.stdout:
                if progress is not None:
                    progress.update(percent, f"Launch: {line.rstrip()}")
                    percent = min(percent + 1, 99)

                logger.info(line.rstrip())

            returncode = proc.wait()

            logger.info(f"CompletedProcess: {returncode!r}")

        home = Path.home()
        for log in sorted(home.glob("steam-*.log")):
            logger.info(f"Proton log available: {log}")

        return returncode


#from proton_autogen.about import afficher_abouts, afficher_abouts_label
def print_about():
    afficher_abouts()


def get_about_text():
    return f"""{afficher_abouts_label()}"""
