#backend.py proton-autogen
import os
import json
import re
import sys
import subprocess
import time
from pathlib import Path
from proton_autogen.exceptions import ExecutableNotFoundError, ProtonNotFoundError, GameConfigError, PrefixError
from time import perf_counter
from proton_autogen.config import VERSION
from proton_autogen.utils.logger import StructuredLogger
from proton_autogen.progress import Progress

from proton_autogen.loader import save_game_config, load_game_config
from proton_autogen.core import (
    DEBUG,
    VERBOSE,
    USER_PROFILE,
    USER_PROFILE_DATA,

    run_game_proton,
    run_standard,

    has_mangohud,
    has_gamemode,
    has_gamescope,
    has_proton_call,
    has_wine,

    proton_name,
    proton_path,

    load_proton_paths,
)
from proton_autogen.profiles.init import detect_exe_type
from proton_autogen.i18n import tr, init_language
from proton_autogen.stats import get_game_badges, format_playtime, get_playtime_stats
from proton_autogen.pa_log import handle_result, result_to_line
from proton_autogen.diag import find_all_protons, find_proton
# new files:
from proton_autogen.dector import resolve_game_features
from proton_autogen.system import detect_system_info
from proton_autogen.session import finalize_session, notifications
from proton_autogen.proton_call import launch_proton_call

#-------------------------- Init Log -------------------
logger = StructuredLogger("proton-autogen.backend")
#-------------------------- Init Langue -------------------
init_language()

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
    print(f"[proton-autogen] {tr('runtime_information')}")

    print(f"  {tr('executable'):<10}: {exe_path}")
    print(f"  {tr('proton'):<10}: {proton_name(proton)}")
    print(f"  {tr('path'):<10}: {proton_path(proton)}")

    print(
        f"  {tr('proton_call'):<10}: ",
        tr("detected") if has_proton_call() else tr("missing")
    )

    print(
        f"  {tr('gamemode'):<10}: ",
        tr("available") if has_gamemode() else tr("unavailable")
    )

    print(
        f"  {tr('mangohud'):<10}: ",
        tr("available") if mangohud_available else tr("unavailable")
    )

    print("")
# ---------------------------------------------------------------------------------------------------

def log_game_stats(exe_path):
    playtime = get_playtime_stats(exe_path) or {}

    logger.info(
        "Statistics:"
        "\n  launches : %d"
        "\n  playtime : %s",
        playtime.get("launch_count", 0),
        format_playtime(playtime.get("seconds", 0)),
    )
# ---------------------------------------------------------------------------------------------------

def run(exe_path: str, launch_mode="proton", prefix_mode="main", progress=None):
    try:
        start_time = time.time() # Stats
        result_code = 0 # Stats
        if progress is None:
            progress = Progress()

        exe_path = os.path.abspath(exe_path)

        exe = Path(exe_path).resolve()
        progress.update(5, tr("checking_executable"))
        if not exe.exists():
            raise ExecutableNotFoundError(exe)

        # Proton path (à adapter)
        #proton = os.path.expanduser(
        #    "~/.steam/debian-installation/compatibilitytools.d/GE-Proton10-34/"
        #)
        mangohud_available = has_mangohud()

        config = load_game_config(exe_path)
        progress.update(25, tr("loading_game_configuration"))

        system = detect_system_info()  # ou équivalent existant dans core
        logger.info(
            "System information:\n" +
            "\n".join(f"  {key}: {value}" for key, value in system.items())
        )
        progress.update(60, tr("runtime_selected"))

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
            cfg_gamescope = normalize_flag(features.get("gamescope"), False)
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
                logger.warning(
                    "Stored Proton '%s' missing, using fallback",
                    saved_proton_name,
                )
                proton = find_proton()
        else:
            # By Default
            cfg_mangohud = False
            cfg_gamemode = False
            cfg_gamescope = False
            rfeatures = None
            proton = find_proton()

        progress.update(60, tr("runtime_selected"))
        enable_mangohud = cfg_mangohud if config else False
        enable_gamemode = cfg_gamemode if config else False
        enable_gamescope = cfg_gamescope if config else False

        # CLI overrides (priorité utilisateur)
        if "--mangohud" in sys.argv:
            enable_mangohud = True

        if "--gamemode" in sys.argv:
            enable_gamemode = True

        if "--gamescope" in sys.argv:
            enable_gamescope = True


        if proton:
            print_runtime_info(proton, exe_path, mangohud_available)
        else:
            raise ProtonNotFoundError(exe_path)

        if launch_mode == "proton-call" and has_proton_call():
            progress.update( 80, tr("starting_proton_call") )
            launch_proton_call(
                exe_path=exe_path,
                proton=proton,
                system=system,
                features=rfeatures,
                enable_mangohud=enable_mangohud,
                enable_gamemode=enable_gamemode,
                enable_gamescope=enable_gamescope,
                start_time=start_time,
                extra_args=[],
                progress=progress
            )

        elif launch_mode == "proton" and proton:

            # ----------------------------
            # Prefix resolution (IMPORTANT PART)
            # ----------------------------
            if config and config.get("prefix"):
                prefix_mode = config["prefix"].get("name", prefix_mode)
                #Message
                notifications.notify( "info", "proton-autogen", tr("load_config_prefix", prefix=prefix_mode), ui=True )

            result_code = -1
            progress.update(80, tr("starting_proton"))
            result_code = run_game_proton(exe_path=exe_path, exe_type=exe_type, proton=proton, system=system, features=rfeatures, enable_mangohud=enable_mangohud,
             enable_gamemode=enable_gamemode, enable_gamescope=enable_gamescope, prefix_mode=prefix_mode, progress=progress)
            if DEBUG or VERBOSE:
                logger.debug("Result type: %s", type(result_code))
                logger.debug("Result: %s", result_code)

                if isinstance(result_code, subprocess.CompletedProcess):
                    logger.info(
                        "Process return code: %s",
                        result_code.returncode,
                    )
            status = handle_result(result_code)
            # Update Stats
            finalize_session(exe_path, start_time, result_code)
            log_game_stats(exe_path)
            #show_result !
            progress.update( 100, result_to_line(status) )

            sys.exit(status["code"])

        elif launch_mode == "wine":

            result_code = -1
            progress.update(80, tr("starting_wine"))
            result_code = run_standard(exe_path)
            status = handle_result(result_code)
            # Update Stats
            finalize_session(exe_path, start_time, result_code) # Stats
            log_game_stats(exe_path)
            #show_result !
            progress.update( 100, result_to_line(status) )

            sys.exit(status["code"])

        progress.update(100, tr("run_started"))

    except ExecutableNotFoundError as e:
        logger.error(str(e))
        notifications.notify( "warning", tr("missing_executable_title"), tr("missing_executable_message"), ui=True, )
        sys.exit(1)

    except ProtonNotFoundError as e:
        message = tr("proton_not_found").strip()
        notifications.notify( "error", "proton-autogen", message, ui=True, )
        logger.error(str(e))
        sys.exit(2)

    except GameConfigError as e:
        logger.error(str(e))
        sys.exit(3)

    except PrefixError as e:
        logger.error(str(e))
        sys.exit(4)
    except Exception:
        logger.exception("Unexpected error")
        raise

#---------------------------------------------------------------------------------------------


def list_protons():
    protons = find_all_protons()

    if not protons:
        print(tr("no_proton_installation"))
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

    print(f"{tr('detected_proton_installations')}:\n")

    for proton in sorted(protons, key=sort_key):
        proton_real = os.path.realpath(proton)

        is_selected = (selected_path == proton_real)
        suffix = f" ({tr('selected')})" if is_selected else ""

        print(f"  {os.path.basename(proton)}{suffix}")
        print(f"    {proton}\n")

def get_diagnostic_text():
    lines = []

    lines.append(f"{tr('diagnostic')}\n")
    lines.append(f"{tr('version'):<12}: {VERSION}")
    lines.append(f"{tr('python'):<12}: {sys.version.split()[0]}\n")
    lines.append(f"{tr('runtime')}:")
    lines.append(
        f"  {tr('proton_call')} : "
        f"{tr('yes') if has_proton_call() else tr('no')}"
    )
    lines.append(
        f"  {tr('wine')} : "
        f"{tr('yes') if has_wine() else tr('no')}"
    )
    lines.append(
        f"  {tr('gamemode')} : "
        f"{tr('yes') if has_gamemode() else tr('no')}"
    )
    lines.append(
        f"  {tr('gamescope')} : "
        f"{tr('yes') if has_gamescope() else tr('no')}"
    )
    lines.append(
        f"  {tr('mangohud')} : "
        f"{tr('yes') if has_mangohud() else tr('no')}"
    )
    lines.append(
        f"{tr('platform'):<12}: {sys.platform}\n"
    )

    protons = find_all_protons()
    lines.append(
        f"{tr('detected_proton_installations')}: {len(protons)}\n"
    )

    if not protons:
        lines.append(f"  {tr('none')}\n")
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

        marker = f" [{tr('selected')}]" if selected_path and proton_real == selected_path else ""

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

excluded_names = { "setup.exe", "install.exe", }
MAX_DEPTH = 6  # 👈 réglable

from functools import lru_cache

@lru_cache(maxsize=1)
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
                and not d.startswith(".")
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

    print( tr( "search_finished", time=perf_counter() - start ) )

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
        print(tr("no_windows_programs"))
        return

    print(f"{tr('detected_programs')}:")
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
            "config_path": config.get("config_path"),
            "exe_type": config.get("exe_type", detect_exe_type(exe)),
            "proton": config.get("proton", ""),
            "prefix": config.get("prefix", {"name": "main"}),
            "features": config.get("features", {
                "mangohud": False,
                "gamemode": False,
                "gamescope": False,
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
# End backend
