"""proton_autogen.utils.steam_appid

Détection de l'AppID Steam d'un jeu, utilisée pour renseigner les
variables STEAM_COMPAT_APP_ID / SteamAppId / SteamGameId nécessaires
au bon fonctionnement de certains launchers, overlays et caches de
shaders indexés par AppID.
"""

import os
import re
from pathlib import Path
from typing import Optional

from proton_autogen.utils.logger import StructuredLogger

logger = StructuredLogger("proton-autogen.utils.steam_appid")

_ENV_KEYS = ("STEAM_COMPAT_APP_ID", "SteamAppId", "SteamGameId")
_FALLBACK_APPID = "480"  # Spacewar, AppID de test générique Valve

_ACF_INSTALLDIR_RE = re.compile(r'"installdir"\s*"([^"]+)"')
_ACF_FILENAME_RE = re.compile(r"appmanifest_(\d+)\.acf$")

# -----------------------------------------------------------------
# AppIDs connus pour des exécutables spécifiques, utilisés en dernier
# recours quand aucune détection automatique (env, appmanifest,
# steam_appid.txt) n'a abouti. Utile pour les jeux anciens copiés
# hors de leur bibliothèque Steam d'origine (GOG, backups, etc.).
# Clé : nom de fichier de l'exécutable (insensible à la casse).
# -----------------------------------------------------------------
KNOWN_APPIDS = {
    # -----------------------------
    # Valve / GoldSrc
    # -----------------------------
    "hl.exe": "70",                     # Half-Life
    "cstrike.exe": "10",                # Counter-Strike
    "czero.exe": "80",                  # Counter-Strike: Condition Zero
    "gearbox.exe": "50",                # Opposing Force
    "bshift.exe": "130",                # Blue Shift
    "dmc.exe": "40",                    # Deathmatch Classic
    "ricochet.exe": "60",               # Ricochet
    "tfc.exe": "20",                    # Team Fortress Classic
    "svencoop.exe": "225840",           # Sven Co-op

    # -----------------------------
    # Source
    # -----------------------------
    "hl2.exe": "220",                   # Half-Life 2
    "hl2_ep1.exe": "380",               # Episode One
    "hl2_ep2.exe": "420",               # Episode Two
    "portal.exe": "400",                # Portal
    "portal2.exe": "620",               # Portal 2
    "left4dead.exe": "500",             # Left 4 Dead
    "left4dead2.exe": "550",            # Left 4 Dead 2
    "hl2mp.exe": "320",                 # HL2 Deathmatch
    "tf.exe": "440",                    # Team Fortress 2
    "dods.exe": "300",                  # Day of Defeat Source
    "csgo.exe": "730",                  # CS:GO / CS2
    "gmod.exe": "4000",                 # Garry's Mod
    "swarm.exe": "630",                 # Alien Swarm

    # -----------------------------
    # Unreal Tournament
    # -----------------------------
    "UnrealTournament.exe": "13240",
    "ut99.exe": "13240",
    "ut2004.exe": "13230",
    "ut3.exe": "13210",

    # -----------------------------
    # Unreal
    # -----------------------------
    "unreal.exe": "13250",              # Unreal Gold

    # -----------------------------
    # Quake
    # -----------------------------
    "quake.exe": "2310",
    "glquake.exe": "2310",
    "winquake.exe": "2310",
    "quake2.exe": "2320",
    "quake3.exe": "2200",
    "quake4.exe": "2210",

    # -----------------------------
    # id Software (Doom)
    # -----------------------------
    "doom.exe": "2280",                 # DOOM (1993)
    "doom2.exe": "2300",                # DOOM II
    "doom3.exe": "9050",
    "doom3bfg.exe": "208200",

    # -----------------------------
    # GTA
    # -----------------------------
    "gta-vc.exe": "12110",              # Vice City
    "gta3.exe": "12100",                # GTA III
    "gta_sa.exe": "12120",              # San Andreas
    "GTA5.exe": "271590",

    # -----------------------------
    # Rockstar (autres)
    # -----------------------------
    "MaxPayne.exe": "12140",
    "MaxPayne2.exe": "12150",

    # -----------------------------
    # Bethesda
    # -----------------------------
    "Morrowind.exe": "22320",
    "Oblivion.exe": "22330",
    "Skyrim.exe": "72850",
    "SkyrimSE.exe": "489830",

    # -----------------------------
    # Fallout
    # -----------------------------
    "Fallout3.exe": "22370",
    "FalloutNV.exe": "22380",
    "Fallout4.exe": "377160",

    # -----------------------------
    # BioShock
    # -----------------------------
    "Bioshock.exe": "7670",
    "Bioshock2.exe": "8850",

    # -----------------------------
    # Deus Ex
    # -----------------------------
    "DeusEx.exe": "6910",
    "DXHR.exe": "238010",               # Human Revolution

    # -----------------------------
    # Crysis
    # -----------------------------
    "Crysis.exe": "17300",
    "Crysis64.exe": "17300",

    # -----------------------------
    # Far Cry
    # -----------------------------
    "FarCry.exe": "13520",

    # -----------------------------
    # ARMA
    # -----------------------------
    "arma3.exe": "107410",
    "arma3_x64.exe": "107410",
}

# Index normalisé (casse basse) pour une recherche insensible à la casse,
# construit une seule fois à l'import.
_KNOWN_APPIDS_LOWER = {name.lower(): appid for name, appid in KNOWN_APPIDS.items()}


def _from_environment() -> Optional[str]:
    """Vérifie si l'AppID est déjà fourni via une variable d'environnement."""
    for key in _ENV_KEYS:
        value = os.environ.get(key)
        if value and value.isdigit():
            return value
    return None


def _from_appmanifest(exe_path: Path) -> Optional[str]:
    """Recherche l'AppID via appmanifest_<id>.acf dans la bibliothèque Steam.

    Fonctionne pour les chemins de la forme :
        <library>/steamapps/common/<installdir>/.../exe

    Le nom du fichier contient déjà l'AppID ; on vérifie simplement que
    son champ "installdir" correspond au dossier du jeu pour confirmer
    la correspondance (un même dossier "steamapps" peut contenir
    plusieurs manifestes).
    """
    parts = exe_path.parts

    if "common" not in parts:
        return None

    common_index = parts.index("common")

    if common_index + 1 >= len(parts):
        return None

    game_dir = parts[common_index + 1]
    steamapps_dir = Path(*parts[:common_index])

    if not steamapps_dir.is_dir():
        return None

    try:
        acf_files = list(steamapps_dir.glob("appmanifest_*.acf"))
    except OSError:
        return None

    for acf in acf_files:
        filename_match = _ACF_FILENAME_RE.search(acf.name)
        if not filename_match:
            continue

        try:
            content = acf.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        installdir_match = _ACF_INSTALLDIR_RE.search(content)
        if installdir_match and installdir_match.group(1) == game_dir:
            return filename_match.group(1)

    return None


def _from_local_txt(exe_path: Path) -> Optional[str]:
    """Vérifie la présence d'un steam_appid.txt à côté de l'exécutable."""
    txt = exe_path.with_name("steam_appid.txt")

    if not txt.exists():
        return None

    try:
        appid = txt.read_text(encoding="utf-8", errors="ignore").strip()
    except OSError:
        return None

    return appid if appid.isdigit() else None


def _from_known_appids(exe_path: Path) -> Optional[str]:
    """Recherche l'AppID dans la liste des exécutables connus (KNOWN_APPIDS).

    Comparaison insensible à la casse sur le nom de fichier uniquement.
    """
    return _KNOWN_APPIDS_LOWER.get(exe_path.name.lower())


def detect_steam_appid(exe_path: str) -> str:
    """
    Détecte l'AppID Steam associé à un exécutable.

    Ordre de priorité :
      1. Variables d'environnement déjà définies
         (STEAM_COMPAT_APP_ID, SteamAppId, SteamGameId).
      2. appmanifest_<id>.acf dans la bibliothèque Steam du jeu.
      3. steam_appid.txt à côté de l'exécutable.
      4. Liste d'exécutables connus (KNOWN_APPIDS).
      5. Fallback : "480" (Spacewar, AppID générique Valve).

    Args:
        exe_path: chemin vers l'exécutable du jeu.

    Returns:
        L'AppID détecté, sous forme de chaîne numérique.
    """
    path = Path(exe_path)

    appid = _from_environment()
    if appid:
        logger.debug(f"AppID from environment: {appid}")
        return appid

    appid = _from_appmanifest(path)
    if appid:
        logger.debug(f"AppID from appmanifest: {appid}")
        return appid

    appid = _from_local_txt(path)
    if appid:
        logger.debug(f"AppID from steam_appid.txt: {appid}")
        return appid

    appid = _from_known_appids(path)
    if appid:
        logger.debug(f"AppID from known executables list: {appid} ({path.name})")
        return appid

    logger.debug(
        f"No AppID detected for {exe_path}, using fallback {_FALLBACK_APPID}"
    )
    return _FALLBACK_APPID
