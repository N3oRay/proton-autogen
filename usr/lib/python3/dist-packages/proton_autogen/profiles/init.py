#profile.py proton-autogen
import os
import json
from pathlib import Path
from proton_autogen.utils.logger import StructuredLogger
from proton_autogen.session import finalize_session, notifications
from proton_autogen.data_paths import get_profiles_file
from proton_autogen.profiles.capabilities import detect_capabilities


import csv

#-------------------------- Init Log -------------------
logger = StructuredLogger("proton-autogen.profiles.init")

# Liste principale des profiles
VALID_PROFILES = [
    "legacy",
    "launcher",
    "desktop",
    "dx8dg",
    "dx9",
    "dx9opengl",
    "dx11",
    "dx11Bnet",
    "dx12",
    "dotnet",
    "dotnet_csharp",
    "gtav_compat",
    "gtav_x11",
    "gtav_safe",
    "oldgame",
    "ut3",
    "ut99",
    "valve",
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
        get_profiles_file(),
        Path.home() / ".config/proton-autogen/profiles.csv",
    ]

    for path in paths:
        if not path.exists():
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
            logger.debug(f"Profile executable: {os.path.basename(exe_path)} from database: {profile}")
            return profile

    return detect_exe_type_legacy(exe_path)

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def detect_runtimeconfig(exe_path):
    """
    Cherche le fichier *.runtimeconfig.json associé à l'exécutable et en
    extrait le framework cible (tfm, runtime, version) s'il existe.

    Deux emplacements possibles selon la convention du SDK .NET :
      - "MonApp.exe.runtimeconfig.json" (rare, mais tolère les cas où
        l'extension .exe n'est pas retirée par l'outil de publication)
      - "MonApp.runtimeconfig.json"     (convention standard du SDK .NET
        Core/5+ : même nom de base que l'exécutable, extension remplacée)

    La présence de ce fichier signale une application .NET moderne
    (Core/5/6/7/8+), qui embarque son propre hôte CLR — à distinguer
    d'une application .NET Framework classique, qui n'en génère jamais
    et dépend du CLR installé côté système (cf. detect_dotnet_ui() et
    proton_autogen.profiles.dotnet.ensure_dotnet48()).

    Retourne None si aucun fichier trouvé ou illisible ; sinon un dict
    {"tfm": ..., "runtime": ..., "version": ...} (valeurs éventuellement
    None si absentes du JSON).
    """

    candidates = [
        exe_path + ".runtimeconfig.json",
        os.path.splitext(exe_path)[0] + ".runtimeconfig.json",
    ]

    for path in candidates:
        if not os.path.exists(path):
            continue

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            options = data.get("runtimeOptions", {})

            result = {
                "tfm": options.get("tfm"),
                "runtime": None,
                "version": None,
            }

            framework = options.get("framework")

            if framework:
                result["runtime"] = framework.get("name")
                result["version"] = framework.get("version")

            logger.debug(
                f"[detect_runtimeconfig] {os.path.basename(path)} -> "
                f"tfm={result['tfm']} runtime={result['runtime']} "
                f"version={result['version']}"
            )

            return result

        except (OSError, json.JSONDecodeError) as e:
            logger.debug(f"[detect_runtimeconfig] {path} illisible: {e}")

    return None


def detect_dotnet_ui(exe_dir):
    """
    Détecte la présence d'une UI .NET managée connue (WPF ou WinForms)
    par les DLL caractéristiques livrées à côté de l'exécutable.

    Un résultat non-None ("wpf"/"winforms") est un signal fort qu'il
    s'agit d'une application desktop C# — par opposition à un jeu
    Mono/Unity ou un outil CLI, qui n'embarquent ni l'un ni l'autre
    (cf. les entrées "dotnet" vs "dotnet_csharp" de profiles.csv, où
    ce critère sépare très proprement les deux catégories).

    Retourne None si le dossier est illisible ou si aucune des deux
    DLL n'est présente.
    """

    try:
        files = os.listdir(exe_dir)
    except OSError as e:
        logger.debug(f"[detect_dotnet_ui] {exe_dir} illisible: {e}")
        return None

    if "PresentationFramework.dll" in files:
        return "wpf"

    if "System.Windows.Forms.dll" in files:
        return "winforms"

    return None

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def choose_profile():
    # Note: dx8dg, dx9dg -> instable
    profiles = VALID_PROFILES

    logger.info("\nAvailable profiles:\n")

    for idx, p in enumerate(profiles, start=1):
        logger.info(f"[{idx}] {p}")

    logger.info("[d] Detect automatically")

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

        logger.info("Invalid selection")


def detect_exe_type_legacy(exe_path: str) -> str:
    """
    Simple heuristic to classify executable type for proton-autogen.
    Returns: launcher | dx11 | dx11Bnet | dx12 | oldgame | ut3 | ut99 | legacy | desktop | dotnet_csharp
    """

    name = os.path.basename(exe_path).lower()
     #------------------------------
    dotnet_keyworks = [
        # Installation uniquement, cela ne permet pas de faire fonctionner robloxplayer : Bloqué par design, aucune configuration Proton n'y changera rien
        # il n'existe à ce jour aucune méthode documentée fonctionnelle pour contourner Byfron/Hyperion
        "robloxplayerinstaller", "roblox", "robloxplayer", "robloxplayerbeta", "microsoftedgewebview2setup",

        # Riot Games (League of Legends, Valorant) — même famille de bootstrapper WebView2
        "riotclientservices", "riotclientinstaller", "riotclientux",

        # Applications .NET Framework / C# pures (utilisent mscoree comme Roblox)
        "paintdotnet", "paint.net", "sharex", "greenshot", "linqpad",
        "ilspy", "dotpeek",

        # Bootstrappers Visual Studio / outils Microsoft (mscoree natif)
        "vs_installer", "vs_bootstrapper",
        ]

    if any(k in name for k in dotnet_keyworks):
        return "dotnet_csharp"

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
    # 8. DÉTECTION INTELLIGENTE PAR CAPACITÉS (fallback avant dx11)
    # -----------------------------
    # Aucun nom connu (ni profiles.csv, ni les mots-clés ci-dessus) :
    # avant de router par défaut vers le profil DXVK "dx11" — qui ne
    # conviendrait pas forcément à cet exécutable —, on analyse
    # directement le PE (API graphique importée, DirectDraw,
    # architecture) et le dossier (moteur, .NET) plutôt que de deviner
    # à l'aveugle. Une seule analyse (detect_capabilities) alimente
    # toutes les vérifications qui suivent.
    exe_dir = os.path.dirname(exe_path) or "."
    caps = detect_capabilities(exe_path)

    if caps["anti_cheat"]:
        # Pas de profil dédié — c'est une information, pas une
        # décision de routage : le choix de Proton et certains réglages
        # (ex. PROTON_USE_SECCOMP) peuvent en dépendre, mais ça reste
        # à l'appréciation de l'utilisateur/d'une logique dédiée, pas de
        # ce sélecteur de profil.
        logger.info(
            f"[detect_exe_type_legacy] {name}: anti-cheat détecté "
            f"({caps['anti_cheat']}) — la compatibilité Proton peut en dépendre"
        )
        notifications.notify(
            "warning", "proton-autogen",
            f"{name}: anti-cheat {caps['anti_cheat'].upper()} détecté",
            ui=True,
        )

    graphics = caps["graphics"]

    # DirectDraw : cas particulier, combiné avec l'architecture ou D3D8
    # comme demandé — DirectDraw+x86 est le signe d'un jeu vraiment
    # ancien (-> oldgame), DirectDraw+D3D8 d'une transition D3D8/DDraw
    # typique fin années 90 (-> dx8dg).
    if caps["directdraw"]:
        if graphics["dx8"]:
            logger.debug(f"[detect_exe_type_legacy] {name}: DirectDraw + D3D8 -> dx8dg")
            return "dx8dg"

        if caps["architecture"] == "x86":
            logger.debug(f"[detect_exe_type_legacy] {name}: DirectDraw + x86 -> oldgame")
            return "oldgame"

        logger.debug(f"[detect_exe_type_legacy] {name}: DirectDraw (sans D3D8 ni x86) -> legacy")
        return "legacy"

    if graphics["dx12"]:
        logger.debug(f"[detect_exe_type_legacy] {name}: D3D12 importé -> dx12")
        return "dx12"

    if graphics["dx11"]:
        logger.debug(f"[detect_exe_type_legacy] {name}: D3D11 importé -> dx11")
        return "dx11"

    if graphics["dx9"] or graphics["dx8"] or graphics["dx10"] or graphics["opengl"]:
        logger.debug(
            f"[detect_exe_type_legacy] {name}: API DX8/9/10/OpenGL importée -> dx9opengl"
        )
        return "dx9opengl"

    if graphics["vulkan"]:
        # Pas de profil Vulkan dédié : un jeu Vulkan natif n'a de toute
        # façon pas besoin de traduction DXVK/VKD3D, le profil "dx12"
        # (réglages modernes génériques) reste le repli le plus sûr.
        logger.debug(f"[detect_exe_type_legacy] {name}: Vulkan natif -> dx12")
        return "dx12"

    # Aucune API graphique native détectée : peut-être une application
    # managée (.NET) plutôt qu'un jeu — mêmes vérifications qu'avant.
    #
    # Ordre volontaire : la détection d'UI (WPF/WinForms) est vérifiée
    # EN PREMIER car c'est le signal le plus décisif d'une application
    # desktop C# (-> dotnet_csharp). Un .runtimeconfig.json seul, sans
    # UI desktop connue, correspond typiquement à un jeu Mono/Unity ou
    # un outil CLI .NET (-> dotnet) : cf. la répartition réelle dans
    # profiles.csv, où ce critère sépare très proprement les deux
    # catégories.
    dotnet_ui = detect_dotnet_ui(exe_dir)

    if dotnet_ui is not None:
        logger.debug(
            f"[detect_exe_type_legacy] {name}: UI {dotnet_ui} détectée "
            f"sans profil connu -> dotnet_csharp"
        )
        return "dotnet_csharp"

    runtimeconfig = detect_runtimeconfig(exe_path)

    if runtimeconfig is not None:
        logger.debug(
            f"[detect_exe_type_legacy] {name}: runtimeconfig.json "
            f"détecté sans UI desktop connue -> dotnet"
        )
        return "dotnet"

    if caps["engine"]:
        # Un jeu Unity/Unreal/Godot dont on n'a détecté ni API
        # graphique par import PE (fréquent avec IL2CPP/des exécutables
        # empaquetés qui résolvent leurs DLL dynamiquement plutôt que
        # par import statique) ni signal .NET : on le journalise pour
        # diagnostic, mais dx11 reste le repli le plus sûr en pratique
        # pour ces moteurs sur Proton.
        logger.debug(
            f"[detect_exe_type_legacy] {name}: moteur {caps['engine']} détecté, "
            f"sans API graphique ni .NET identifiable -> dx11 (repli sûr)"
        )

    # -----------------------------
    # 4. DEFAULT = DX11 (safe fallback)
    # -----------------------------
    return "dx11"
#---------------------------------------------------------------------------------------------
