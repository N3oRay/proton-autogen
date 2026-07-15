#profile.py proton-autogen
import os
from pathlib import Path
from proton_autogen.utils.logger import StructuredLogger
from proton_autogen.session import finalize_session, notifications

import csv

#-------------------------- Init Log -------------------
logger = StructuredLogger("proton-autogen.profiles.init")


VALID_PROFILES = [
    "launcher",
    "dx11",
    "dx11Bnet",
    "dx12",
    "dx9",
    "dx9opengl",
    "gtav_compat",
    "gtav_x11",
    "gtav_safe",
    "oldgame",
    "valve",
    "ut3",
    "ut99",
    "legacy",
    "desktop",
]


_GAME_DATABASE = None


def validate_profile(profile):

    if profile in VALID_PROFILES:
        return profile

    return None

def load_game_database():

    global _GAME_DATABASE

    if _GAME_DATABASE is not None:
        return _GAME_DATABASE

    database = {}

    paths = [
        "/usr/share/proton-autogen/profiles.csv",
        os.path.expanduser(
            "~/.config/proton-autogen/profiles.csv"
        ),
    ]

    for path in paths:
        if not os.path.exists(path):
            continue

        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                exe = row.get("exe", "").lower()

                if exe:
                    database[exe] = row

    _GAME_DATABASE = list(database.values())

    return _GAME_DATABASE



def find_game_profile(exe):
    #logger.info(f"Find profile in db : {exe}")
    exe = exe.lower()

    for game in load_game_database():

        game_exe = game.get("exe", "").lower()

        if game_exe == exe:
            return game

    return None

def detect_exe_type(exe_path):
    #notifications.notify( "info", "proton-autogen", f"Analyzing executable: {os.path.basename(exe_path)}", ui=True )
    #logger.info(f"Analyzing executable: {os.path.basename(exe_path)}")

    db_game = find_game_profile(
        os.path.basename(exe_path)
    )

    if db_game:

        profile = validate_profile(
            db_game.get("exe_type")
        )

        if profile:
            #notifications.notify( "info", "proton-autogen", f"Profile executable: {os.path.basename(exe_path)} from database: {profile}", ui=True )
            logger.info(f"Profile executable: {os.path.basename(exe_path)} from database: {profile}")
            return profile

    return detect_exe_type_legacy(exe_path)

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def choose_profile():
    # Note: dx8dg, dx9dg -> instable
    profiles = VALID_PROFILES

    print("\nAvailable profiles:\n")

    for idx, p in enumerate(profiles, start=1):
        print(f"[{idx}] {p}")

    print("[d] Detect automatically")

    while True:
        choice = input("\nSelection: ").strip().lower()

        if choice == "d":
            return None  # on utilisera detect_exe_type()

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(profiles):
                return profiles[idx]
        except ValueError:
            pass

        print("Invalid selection")


def detect_exe_type_legacy(exe_path: str) -> str:
    """
    Simple heuristic to classify executable type for proton-autogen.
    Returns: launcher | dx11 | dx11Bnet | dx12 | oldgame | ut3 | ut99 | legacy | desktop
    """

    name = os.path.basename(exe_path).lower()

    #------------------------------
    # 0. Dx11 ( Game DirectX : Jeux connus pour fonctionner avec le profil DXVK/D3D11 )

    dxvk_keywords = [
        # Rockstar
        "gta v", "gta 5", "gtav", "gta5", "max payne 3",
        # Racing
        "dirt 2", "dirt 3",
        # RPG
        "witcher 2", "witcher 3", "witcher3",
        # Online
        "final fantasy xiv",
        # Modern DX11
        "monster hunter world", "dark souls 3", "dark souls iii", "resident evil 2", "resident evil 3", "days gone", "horizon zero dawn", "death stranding", "red dead redemption 2",
    ]

    if any(k in name for k in dxvk_keywords):
        return "dx11"

    # -----------------------------
    # 0. Dx11 (highest priority)
    # -----------------------------
    batte_keywords = [
        "battle.net", "battlenet", "battle net", "blizzard agent", "heroesofthestorm", "heroes of the storm", "hots",
        "blizzard", "blizzard update", "blizzard launcher", "battle.net launcher", "battlenet launcher", "battle.net helper", "battle.net helper.exe",
    ]

    if any(k in name for k in batte_keywords):
        return "dx11Bnet"

    # -----------------------------
    # 0. legacy (highest priority)
    # -----------------------------

    legacy_app_keywords = [
        "photoshop", "photoshp", "paintshop", "imageready", "acdsee",
    ]

    if any(k in name for k in legacy_app_keywords):
        return "legacy"

    # -----------------------------
    # 1. LAUNCHERS (highest priority)
    # -----------------------------
    launcher_keywords = [
        "launcher", "ubisoft connect", "ubisoft", "uplay", "epicgameslauncher", "steamwebhelper", "ea app", "eadesktop", "origin",
    ]

    if any(k in name for k in launcher_keywords):
        return "launcher"

    # -----------------------------
    # 2. OLD GAMES (DX8 / DX9 era)
    # -----------------------------
    oldgame_keywords = [
        "doom95",
    ]

    if any(k in name for k in oldgame_keywords):
        return "oldgame"

    dx9_keywords = [
        "dx9",
        # Need for Speed
        "speed2",
        "nfsc",
        "undercover",
    ]

    if any(k in name for k in dx9_keywords):
        return "dx9"



    dx9opengl_keywords = [
        "most wanted", "carbon", "left 4 dead", "left4dead", "left 4 dead 2", "left4dead2", "source engine", "gta 4", "mass effect 3",
        # Need for Speed
        "nfsu2", "nfsmw", "portal", "pro street", "underground", "underground 2", "grid", "dirt", "hl2", "dx8",
        # Bethesda
        "flatout", "flatout 2", "flatout ultimate carnage", "trackmania", "trackmania nations", "burnout paradise",
        #RPG
        "gta iv", "portal2", "counter-strike source", "counter strike source", "team fortress 2", "tesv", "falloutnv",
        #STAR WARS
        "swtor", "star wars the old republic", "the witcher", "mass effect", "mass effect 2", "oblivion", "skyrim",
        "fallout 3", "fallout new vegas", "dragon age origins", "dragon age 2", "fallout nv", "directx 8", "directx 9", "rcr", "swep1rcr", "ut99", "quake"
    ]

    if any(k in name for k in dx9opengl_keywords):
        return "dx9opengl"

    # -----------------------------
    # 3. VALVE SIERRA - old Game
    # -----------------------------
    valve_keywords = [
        "counter-strike", "hl1", "hl", "tfc", "dmc", "ricochet", "half-life", "half life", "half-life"
    ]

    if any(k in name for k in valve_keywords):
        return "valve"

    # -----------------------------
    # 3. DX12 GAMES (modern AAA)
    # -----------------------------
    dx12_keywords = [
        "dx12", "d3d12", "cyberpunk", "starfield", "hogwarts", "elden", "diablo", "warzone", "elden ring", "hogwarts legacy",
    ]

    if any(k in name for k in dx12_keywords):
        return "dx12"

    # -----------------------------
    # 6. LAUNCHERS (highest priority env_ut3)
    # -----------------------------
    ut3_keywords = [
        # -----------------------------
        # Unreal Tournament 3 / UE3 spécifique
        # -----------------------------
        "ut3", "unreal3", "unrealtournament3", "unreal tournament 3", "utgame", "ut3editor", "unrealfrontend", "13210",
        # -----------------------------
        # UE3 (même base moteur que UT3)
        # -----------------------------
        "bioshock", "bioshock2", "borderlands", "borderlands2", "mirror's edge", "mirrors edge", "dead space",
        # -----------------------------
        # Gamebryo / DX9 RPG (souvent même era problématique Proton)
        # -----------------------------
        "fallout3", "fallout new vegas", "falloutnv", "the witcher", "witcher2",
        # -----------------------------
        # Source Engine DX9
        # -----------------------------
        "hl2", "half-life 2", "portal", "portal2", "left 4 dead", "left4dead", "left 4 dead 2", "tf2", "team fortress 2",
        # -----------------------------
        # Open-world DX9 era
        # -----------------------------
        "gta4", "grand theft auto iv", "saints row 2", "mafia2", "just cause", "just cause 2",
        # -----------------------------
        # STALKER / X-Ray engine DX9
        # -----------------------------
        "stalker", "shadow of chernobyl", "clear sky", "call of pripyat",
    ]
    if any(k in name for k in ut3_keywords):
        return "ut3"

    # -----------------------------
    # 5. LAUNCHERS (highest priority)
    # -----------------------------
    ut99_keywords = [
        "ut99",
        "unrealtournament",
    ]
    if any(k in name for k in ut99_keywords):
        return "ut99"

    # -----------------------------
    # 7. DESKTOP
    # -----------------------------
    desktop_keywords = [
        "winrar",
        "7zfm",
        "7zip",
        "notepad++",
        "foobar2000",
        "vlc",
        "putty",
    ]
    if any(k in name for k in desktop_keywords):
        return "desktop"

    # -----------------------------
    # 4. DEFAULT = DX11 (safe fallback)
    # -----------------------------
    return "dx11"
#---------------------------------------------------------------------------------------------
