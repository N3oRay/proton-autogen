"""
Option « Debug DXVK » (par jeu).

Applique DXVK_LOG_LEVEL / DXVK_LOG_PATH / DXVK_HUD et range les logs dans :

    <CONFIG_DIR>/logs/<version_de_proton>/<jeu>/

Règles de sécurité :
  * jamais de DXVK_HUD si un overlay MangoHud (ou --mangoapp) est actif ;
  * jamais de HUD sur les profils où il est volontairement désactivé ;
  * rien du tout en mode WineD3D (DXVK n'est pas chargé, aucun log produit) ;
  * une variable déjà définie par l'utilisateur (variables personnalisées)
    n'est jamais écrasée.
"""
import os
import re
from pathlib import Path

from proton_autogen.config import CONFIG_DIR
from proton_autogen.utils.logger import StructuredLogger

logger = StructuredLogger("proton-autogen.dxvk_debug")

DXVK_LOG_LEVEL = "info"      # none | error | warn | info | debug
DXVK_HUD_VALUE = "1"

# Profils où le HUD DXVK est volontairement coupé (cf. apply_dxvk_hud, core.py)
HUD_EXCLUDED_PROFILES = ("dotnet_csharp", "dotnet", "dx9opengl", "valve")


def log_root() -> Path:
    return Path(str(CONFIG_DIR)).expanduser() / "logs"


def _slug(text, fallback="unknown") -> str:
    """Nom de dossier sûr (ni espace, ni '/', ni caractère exotique)."""
    s = re.sub(r"[^\w.\-]+", "_", str(text or "").strip()).strip("._")
    return s or fallback


def proton_label(proton_dir) -> str:
    """'/.../compatibilitytools.d/GE-Proton10-4/' -> 'GE-Proton10-4'."""
    name = os.path.basename(os.path.normpath(str(proton_dir or "")))
    return _slug(name, "proton")


def get_dxvk_log_dir(proton_dir, game_name=None, exe_path="") -> Path:
    """<logs>/<proton>/<jeu>/ — créé si absent (DXVK ne le crée pas lui-même)."""
    game = game_name or Path(str(exe_path or "")).stem
    path = log_root() / proton_label(proton_dir) / _slug(game, "game")
    path.mkdir(parents=True, exist_ok=True)
    return path


def _set(env, custom_env, key, value):
    """Pose key=value sauf si l'utilisateur l'a définie lui-même."""
    if key in custom_env:
        logger.info(f"DXVK debug: {key} kept from custom env")
        return
    env[key] = value


def apply_dxvk_debug(env, proton_dir, exe_path="", game_name=None,
                     exe_type="", overlay_active=False, custom_env=None):
    """
    À appeler APRÈS configure_mangohud_env() (qui force DXVK_HUD=0 quand
    MangoHud est actif) et après l'application des variables personnalisées.
    """
    custom_env = custom_env or {}

    if env.get("PROTON_USE_WINED3D") == "1":
        logger.info("DXVK debug ignored: WineD3D mode (DXVK not loaded)")
        return env

    # --- Logs -----------------------------------------------------------
    try:
        log_dir = get_dxvk_log_dir(proton_dir, game_name, exe_path)
    except OSError as e:
        logger.warning(f"DXVK debug: cannot create log dir: {e}")
        log_dir = None

    if log_dir is not None:
        _set(env, custom_env, "DXVK_LOG_LEVEL", DXVK_LOG_LEVEL)
        # Chemin absolu : DXVK ne développe pas « ~ ».
        _set(env, custom_env, "DXVK_LOG_PATH", str(log_dir))
        logger.info(f"DXVK debug: logs -> {log_dir}")

    # --- HUD (jamais en conflit avec MangoHud) ---------------------------
    if overlay_active or env.get("MANGOHUD") == "1":
        logger.info("DXVK debug: HUD untouched (MangoHud overlay active)")
    elif exe_type in HUD_EXCLUDED_PROFILES:
        logger.info(f"DXVK debug: HUD skipped for profile '{exe_type}'")
    elif env.get("DXVK_HUD", "") in ("", "0"):
        # Une valeur plus riche (ex. --debug : devinfo,fps,version) est conservée.
        _set(env, custom_env, "DXVK_HUD", DXVK_HUD_VALUE)

    return env
