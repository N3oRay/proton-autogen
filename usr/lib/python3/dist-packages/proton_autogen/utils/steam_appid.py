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
from proton_autogen.utils.p_appid import KNOWN_APPIDS
logger = StructuredLogger("proton-autogen.utils.steam_appid")

_ENV_KEYS = ("STEAM_COMPAT_APP_ID", "SteamAppId", "SteamGameId")
_FALLBACK_APPID = "480"  # Spacewar, AppID de test générique Valve

_ACF_INSTALLDIR_RE = re.compile(r'"installdir"\s*"([^"]+)"')
_ACF_FILENAME_RE = re.compile(r"appmanifest_(\d+)\.acf$")



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

def detect_steam_appid(exe_path: str, fallback: bool = True) -> Optional[str]:
    path = Path(exe_path).resolve()

    appid = _from_environment()
    if appid:
        logger.info(f"Steam AppID detected: {appid} (environment)")
        return appid

    appid = _from_appmanifest(path)
    if appid:
        logger.info(f"Steam AppID detected: {appid} (appmanifest)")
        return appid

    appid = _from_local_txt(path)
    if appid:
        logger.info(f"Steam AppID detected: {appid} (steam_appid.txt)")
        return appid

    appid = _from_known_appids(path)
    if appid:
        logger.info(f"Steam AppID detected: {appid} (known executable: {path.name})")
        return appid

    if not fallback:
        logger.debug(f"No Steam AppID detected for {path.name} (fallback désactivé)")
        return None

    logger.info(f"Steam AppID fallback: {_FALLBACK_APPID} (unknown executable: {path.name})")
    return _FALLBACK_APPID
