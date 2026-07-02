#core.py proton-autogen

import os
import sys
import subprocess
import hashlib
import json
from collections import defaultdict

from pathlib import Path
from shutil import which
import configparser

VERSION = "2.8.0"

CONFIG_FILE = os.path.expanduser("~/.config/proton-autogen.conf")
CONFIG_DIR = os.path.expanduser("~/.config/proton-autogen/games")

DEBUG = "--debug" in sys.argv
VERBOSE = "--verbose" in sys.argv
#-------------------------- Profile PRO -------------------
USER_PROFILE = None
USER_PROFILE_DATA = None

def proton_path(p):
    if isinstance(p, dict):
        return p.get("path")
    return p


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

    # ----------------------------
    # normalization + deduplication (SAFE VERSION)
    # ----------------------------
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



DEFAULT_PROTON_PATHS = [
    # Steam natif
    "~/.steam/root/compatibilitytools.d",
    "~/.steam/steam/compatibilitytools.d",
    "~/.local/share/Steam/compatibilitytools.d",

    # Steam runtimes
    "~/.steam/steam/steamapps/common",
    "~/.local/share/Steam/steamapps/common",

    # system-wide (CachyOS / Arch / custom builds)
    "/usr/share/steam/compatibilitytools.d",
]

ENV_VARS = [

    # =========================================================
    # DXVK
    # =========================================================
    {
        "name": "DXVK_FULLSCREEN",
        "type": "dxvk",
        "category": "compatibility",
        "description_fr": "Force DXVK à utiliser un mode plein écran exclusif ou contrôlé pour les applications Vulkan via DXVK.",
        "description_en": "Forces DXVK to use exclusive or controlled fullscreen mode for Vulkan-based applications."
    },
    {
        "name": "DXVK_ASYNC",
        "type": "proton",
        "category": "performance",
        "description_fr": "Active la compilation asynchrone des shaders avec DXVK afin de réduire les saccades liées à leur compilation pendant le jeu.",
        "description_en": "Enables asynchronous shader compilation in DXVK to reduce shader compilation stuttering during gameplay."
    },
    {
        "name": "DXVK_CONFIG",
        "type": "dxvk",
        "category": "configuration",
        "description_fr": "Configuration personnalisée DXVK.",
        "description_en": "Custom DXVK configuration."
    },
    {
        "name": "DXVK_HUD",
        "type": "dxvk",
        "category": "debug",
        "description_fr": "Affiche l'overlay DXVK (FPS, mémoire, shaders).",
        "description_en": "Displays DXVK HUD overlay."
    },
    {
        "name": "DXVK_LOG_LEVEL",
        "type": "dxvk",
        "category": "debug",
        "description_fr": "Niveau de logs DXVK.",
        "description_en": "DXVK logging level."
    },
    {
        "name": "DXVK_LOG_PATH",
        "type": "dxvk",
        "category": "debug",
        "description_fr": "Chemin des logs DXVK.",
        "description_en": "DXVK log output path."
    },
    {
        "name": "DXVK_STATE_CACHE",
        "type": "dxvk",
        "category": "performance",
        "description_fr": "Active le cache DXVK.",
        "description_en": "Enables DXVK state cache."
    },
    {
        "name": "DXVK_STATE_CACHE_PATH",
        "type": "dxvk",
        "category": "configuration",
        "description_fr": "Chemin du cache DXVK.",
        "description_en": "DXVK cache path."
    },
    {
        "name": "DXVK_STATE_CACHE_SIZE",
        "type": "dxvk",
        "category": "performance",
        "description_fr": "Taille du cache DXVK.",
        "description_en": "DXVK cache size limit."
    },
    {
        "name": "DXVK_ENABLE_NVAPI",
        "type": "dxvk",
        "category": "compatibility",
        "description_fr": "Active NVAPI via DXVK.",
        "description_en": "Enables NVAPI support."
    },
    {
        "name": "DXVK_FILTER_DEVICE_NAME",
        "type": "dxvk",
        "category": "graphics",
        "description_fr": "Force un GPU Vulkan.",
        "description_en": "Forces a specific Vulkan GPU."
    },
    {
        "name": "DXVK_FRAME_RATE",
        "type": "dxvk",
        "category": "performance",
        "description_fr": "Limite les FPS.",
        "description_en": "FPS limiter."
    },

    # =========================================================
    # VKD3D (DirectX 12)
    # =========================================================
    {
        "name": "VKD3D_CONFIG",
        "type": "vkd3d",
        "category": "configuration",
        "description_fr": "Configuration VKD3D-Proton (DX12).",
        "description_en": "VKD3D-Proton configuration."
    },
    {
        "name": "VKD3D_DEBUG",
        "type": "vkd3d",
        "category": "debug",
        "description_fr": "Logs VKD3D.",
        "description_en": "VKD3D debug output."
    },
    {
        "name": "VKD3D_SHADER_DEBUG",
        "type": "vkd3d",
        "category": "debug",
        "description_fr": "Debug shaders DX12.",
        "description_en": "DX12 shader debugging."
    },
    {
        "name": "VKD3D_FEATURE_LEVEL",
        "type": "vkd3d",
        "category": "compatibility",
        "description_fr": "Force un feature level DX12.",
        "description_en": "Forces DX12 feature level."
    },
    {
        "name": "VKD3D_DEBUGFLAGS",
        "type": "vkd3d",
        "category": "debug",
        "description_fr": "Flags debug VKD3D.",
        "description_en": "VKD3D debug flags."
    },

    # =========================================================
    # PROTON
    # =========================================================
    {
        "name": "PROTON_LOG",
        "type": "proton",
        "category": "debug",
        "description_fr": "Active les logs Proton.",
        "description_en": "Enables Proton logs."
    },
    {
        "name": "PROTON_LOG_DIR",
        "type": "proton",
        "category": "debug",
        "description_fr": "Dossier des logs Proton.",
        "description_en": "Proton log directory."
    },
    {
        "name": "PROTON_NO_ESYNC",
        "type": "proton",
        "category": "performance",
        "description_fr": "Désactive Esync.",
        "description_en": "Disables Esync."
    },
    {
        "name": "PROTON_NO_FSYNC",
        "type": "proton",
        "category": "performance",
        "description_fr": "Désactive Fsync.",
        "description_en": "Disables Fsync."
    },
    {
        "name": "PROTON_USE_WINED3D",
        "type": "proton",
        "category": "compatibility",
        "description_fr": "Utilise WineD3D au lieu de DXVK.",
        "description_en": "Uses WineD3D instead of DXVK."
    },
    {
        "name": "PROTON_ENABLE_NVAPI",
        "type": "proton",
        "category": "graphics",
        "description_fr": "Active le support de NVIDIA NVAPI dans Proton pour permettre l'utilisation de certaines fonctionnalités spécifiques aux cartes NVIDIA.",
        "description_en": "Enables NVIDIA NVAPI support in Proton, allowing access to certain NVIDIA-specific features."
    },
    {
        "name": "PROTON_ENABLE_WAYLAND",
        "type": "proton",
        "category": "graphics",
        "description_fr": "Active le support Wayland dans Proton lorsque disponible.",
        "description_en": "Enables Wayland support in Proton when available."
    },
    {
        "name": "PROTON_ENABLE_HDR",
        "type": "proton",
        "category": "graphics",
        "description_fr": "Active la prise en charge HDR pour les jeux compatibles via Proton. Dépréciée dans Proton-CachyOS où le HDR est géré automatiquement.",
        "description_en": "Enables HDR support for compatible games through Proton. Deprecated in Proton-CachyOS where HDR is handled automatically."
    },
    {
        "name": "PROTON_FORCE_LARGE_ADDRESS_AWARE",
        "type": "proton",
        "category": "compatibility",
        "description_fr": "Force LAA pour 32-bit.",
        "description_en": "Forces Large Address Awareness."
    },
    {
        "name": "PROTON_ENABLE_FSYNC",
        "type": "proton",
        "category": "performance",
        "description_fr": "Force Fsync Proton.",
        "description_en": "Enables Fsync."
    },

    {
        "name": "PROTON_USE_NTSYNC",
        "type": "proton",
        "category": "performance",
        "description_fr": "Active NTSync, une méthode de synchronisation plus efficace visant à améliorer les performances CPU et la compatibilité des jeux Windows.",
        "description_en": "Enables NTSync, a more efficient synchronization method designed to improve CPU performance and Windows game compatibility."
    },

    # =========================================================
    # WINE
    # =========================================================
    {
        "name": "WINEPREFIX",
        "type": "wine",
        "category": "configuration",
        "description_fr": "Préfixe Wine.",
        "description_en": "Wine prefix path."
    },
    {
        "name": "WINEARCH",
        "type": "wine",
        "category": "configuration",
        "description_fr": "Architecture Wine.",
        "description_en": "Wine architecture."
    },
    {
        "name": "WINEDEBUG",
        "type": "wine",
        "category": "debug",
        "description_fr": "Debug Wine.",
        "description_en": "Wine debug output."
    },
    {
        "name": "WINEDLLOVERRIDES",
        "type": "wine",
        "category": "compatibility",
        "description_fr": "Overrides DLL.",
        "description_en": "DLL override rules."
    },
    {
        "name": "WINEESYNC",
        "type": "wine",
        "category": "performance",
        "description_fr": "Esync Wine.",
        "description_en": "Wine Esync."
    },
    {
        "name": "WINEFSYNC",
        "type": "wine",
        "category": "performance",
        "description_fr": "Fsync Wine.",
        "description_en": "Wine Fsync."
    },
    {
        "name": "WINE_LARGE_ADDRESS_AWARE",
        "type": "wine",
        "category": "compatibility",
        "description_fr": "LAA Wine.",
        "description_en": "Large address aware mode."
    },

    {
        "name": "WINE_FULLSCREEN_FSR",
        "type": "wine",
        "category": "graphics",
        "description_fr": "Active ou désactive l'utilisation de FSR (FidelityFX Super Resolution) pour l'upscaling en plein écran dans Wine/Proton.",
        "description_en": "Enables or disables FidelityFX Super Resolution (FSR) upscaling in fullscreen mode in Wine/Proton."
    },
    {
        "name": "WINE_VK_FULLSCREEN_METHOD",
        "type": "wine",
        "category": "compatibility",
        "description_fr": "Définit la méthode utilisée par Wine pour gérer le plein écran Vulkan (ex: desktop, exclusive, auto).",
        "description_en": "Defines how Wine handles Vulkan fullscreen mode (e.g., desktop, exclusive, auto)."
    },
    # =========================================================
    # SDL
    # =========================================================

    {
        "name": "SDL_VIDEO_X11_NET_WM_BYPASS_COMPOSITOR",
        "type": "sdl",
        "category": "graphics",
        "description_fr": "Contrôle si SDL demande au compositeur X11 de contourner la composition (bypass). Peut réduire la latence ou les problèmes d'affichage, mais peut causer des soucis de focus ou de capture de souris sur certains gestionnaires de fenêtres.",
        "description_en": "Controls whether SDL requests the X11 compositor bypass. Can reduce latency and rendering issues, but may cause focus or mouse capture problems on some window managers."
    },

    {
        "name": "SDL_MOUSE_AUTO_CAPTURE",
        "type": "sdl",
        "category": "input",
        "description_fr": "Active la capture automatique de la souris lorsque la fenêtre devient active. Améliore le comportement des jeux en plein écran ou en mode FPS, en évitant la perte de contrôle de la souris.",
        "description_en": "Enables automatic mouse capture when the window becomes active. Improves mouse behavior in fullscreen or FPS-style games by preventing loss of mouse control."
    },
    {
        "name": "SDL_MOUSE_RELATIVE_MODE_WARP",
        "type": "sdl",
        "category": "input",
        "description_fr": "Active le mode de souris relative avec recentering (warp). Utilisé par certains jeux anciens pour simuler un mouvement continu de la souris. Peut améliorer la compatibilité avec les jeux DirectDraw ou moteurs anciens.",
        "description_en": "Enables relative mouse mode using pointer warping. Used by some older games to simulate continuous mouse movement. Can improve compatibility with DirectDraw or legacy engines."
    },
    {
        "name": "SDL_VIDEO_X11_NET_WM_BYPASS_COMPOSITOR",
        "type": "sdl",
        "category": "graphics",
        "description_fr": "Demande au gestionnaire de fenêtres X11 de contourner le compositeur pour la fenêtre SDL. Peut réduire la latence et améliorer la réactivité, mais peut aussi causer des problèmes de focus ou de capture de souris selon le gestionnaire de fenêtres.",
        "description_en": "Requests the X11 window manager to bypass the compositor for the SDL window. Can reduce latency and improve responsiveness, but may cause focus or mouse capture issues depending on the window manager."
    },
    {
        "name": "SDL_VIDEO_MINIMIZE_ON_FOCUS_LOSS",
        "type": "sdl",
        "category": "window",
        "description_fr": "Détermine si la fenêtre doit être minimisée lors d'une perte de focus. Utile pour éviter certains comportements de plein écran instable dans les anciens jeux.",
        "description_en": "Determines whether the window should be minimized when it loses focus. Useful to avoid unstable fullscreen behavior in older games."
    },
    {
        "name": "SDL_HINT_GRAB_KEYBOARD",
        "type": "sdl",
        "category": "input",
        "description_fr": "Force SDL à capturer le clavier lorsque la fenêtre est active. Empêche les touches de sortir du contexte du jeu, améliorant l'immersion et la compatibilité des anciens moteurs.",
        "description_en": "Forces SDL to grab the keyboard when the window is active. Prevents key input from leaving the game context, improving immersion and compatibility with legacy engines."
    },

    # =========================================================
    # VULKAN
    # =========================================================
    {
        "name": "VK_ICD_FILENAMES",
        "type": "vulkan",
        "category": "graphics",
        "description_fr": "ICD Vulkan forcé.",
        "description_en": "Forces Vulkan ICD."
    },
    {
        "name": "VK_LAYER_PATH",
        "type": "vulkan",
        "category": "graphics",
        "description_fr": "Chemin layers Vulkan.",
        "description_en": "Vulkan layers path."
    },
    {
        "name": "VK_INSTANCE_LAYERS",
        "type": "vulkan",
        "category": "graphics",
        "description_fr": "Layers Vulkan.",
        "description_en": "Vulkan instance layers."
    },
    {
        "name": "VK_LOADER_DEBUG",
        "type": "vulkan",
        "category": "debug",
        "description_fr": "Debug loader Vulkan.",
        "description_en": "Vulkan loader debug."
    },

    # =========================================================
    # MESA / AMD
    # =========================================================
    {
        "name": "MESA_VK_DEVICE_SELECT",
        "type": "mesa",
        "category": "graphics",
        "description_fr": "Sélection GPU Mesa.",
        "description_en": "Select Vulkan GPU."
    },
    {
        "name": "RADV_PERFTEST",
        "type": "mesa",
        "category": "performance",
        "description_fr": "Optimisations RADV.",
        "description_en": "RADV experimental features."
    },
    {
        "name": "RADV_DEBUG",
        "type": "mesa",
        "category": "debug",
        "description_fr": "Debug RADV.",
        "description_en": "RADV debug mode."
    },
    {
        "name": "mesa_glthread",
        "type": "mesa",
        "category": "performance",
        "description_fr": "Multithread OpenGL.",
        "description_en": "OpenGL threading."
    },

    {
        "name": "MESA_GL_VERSION_OVERRIDE",
        "type": "opengl",
        "category": "graphics",
        "description_fr": "Force la version d'OpenGL exposée par le pilote Mesa aux applications.",
        "description_en": "Forces the OpenGL version reported by the Mesa driver to applications."
    },
    {
        "name": "MESA_GLSL_VERSION_OVERRIDE",
        "type": "opengl",
        "category": "graphics",
        "description_fr": "Force la version du langage de shaders GLSL utilisée par Mesa pour la compilation des shaders.",
        "description_en": "Forces the GLSL shader language version used by Mesa for shader compilation."
    },

    # =========================================================
    # NVIDIA
    # =========================================================
    {
        "name": "__GL_SHADER_DISK_CACHE",
        "type": "nvidia",
        "category": "performance",
        "description_fr": "Cache shaders NVIDIA.",
        "description_en": "NVIDIA shader cache."
    },
    {
        "name": "__GL_SHADER_DISK_CACHE_PATH",
        "type": "nvidia",
        "category": "configuration",
        "description_fr": "Chemin cache NVIDIA.",
        "description_en": "NVIDIA cache path."
    },
    {
        "name": "__GL_SYNC_TO_VBLANK",
        "type": "nvidia",
        "category": "graphics",
        "description_fr": "VSync NVIDIA.",
        "description_en": "Vertical sync."
    },
    {
        "name": "__GL_THREADED_OPTIMIZATIONS",
        "type": "nvidia",
        "category": "performance",
        "description_fr": "Threading NVIDIA.",
        "description_en": "Threaded optimizations."
    },

    # =========================================================
    # SYSTEM LINUX
    # =========================================================
    {
        "name": "LD_LIBRARY_PATH",
        "type": "system",
        "category": "linux",
        "description_fr": "Librairies Linux.",
        "description_en": "Linux library path."
    },
    {
        "name": "LD_PRELOAD",
        "type": "system",
        "category": "linux",
        "description_fr": "Préchargement libs.",
        "description_en": "Preload libraries."
    },
    {
        "name": "MALLOC_ARENA_MAX",
        "type": "system",
        "category": "performance",
        "description_fr": "Optimisation mémoire.",
        "description_en": "Memory allocator tuning."
    },

    {
        "name": "GAMEMODERUN",
        "type": "system",
        "category": "performance",
        "description_fr": "Lance le jeu via GameMode afin d'appliquer automatiquement des optimisations système dédiées au jeu.",
        "description_en": "Launches the game through GameMode to automatically apply gaming-oriented system optimizations."
    },

    # =========================================================
    # STEAM
    # =========================================================
    {
        "name": "STEAM_COMPAT_APP_ID",
        "type": "steam",
        "category": "internal",
        "description_fr": "App Steam ID.",
        "description_en": "Steam app ID."
    },
    {
        "name": "STEAM_COMPAT_DATA_PATH",
        "type": "steam",
        "category": "internal",
        "description_fr": "Prefix Proton.",
        "description_en": "Proton prefix path."
    },
    {
        "name": "STEAM_COMPAT_TOOL_PATHS",
        "type": "steam",
        "category": "internal",
        "description_fr": "Tools Proton.",
        "description_en": "Proton tools path."
    },
    {
        "name": "STEAM_COMPAT_SHADER_PATH",
        "type": "steam",
        "category": "performance",
        "description_fr": "Cache shaders Steam.",
        "description_en": "Steam shader cache."
    },

    # =========================================================
    # HUD / OVERLAY
    # =========================================================
    {
        "name": "MANGOHUD",
        "type": "hud",
        "category": "overlay",
        "description_fr": "Overlay MangoHud.",
        "description_en": "MangoHud overlay."
    },
    {
        "name": "MANGOHUD_DLSYM",
        "type": "hud",
        "category": "compatibility",
        "description_fr": "Active le mode d'injection dynamique MangoHud via dlsym pour améliorer la détection des applications utilisant des bibliothèques graphiques chargées dynamiquement.",
        "description_en": "Enables MangoHud dynamic dlsym injection mode to improve detection of applications using dynamically loaded graphics libraries."
    },
    {
        "name": "MANGOHUD_CONFIG",
        "type": "hud",
        "category": "configuration",
        "description_fr": "Définit les paramètres de configuration MangoHud (affichage, métriques, limite FPS, position et options de l'overlay).",
        "description_en": "Defines MangoHud configuration parameters (display, metrics, FPS limit, position and overlay options)."
    },
    {
        "name": "MANGOHUD_OPENGL",
        "type": "hud",
        "category": "compatibility",
        "description_fr": "Active le support du rendu OpenGL dans MangoHud pour afficher l'overlay avec les applications utilisant OpenGL.",
        "description_en": "Enables MangoHud OpenGL rendering support to display the overlay with applications using OpenGL."
    },
    {
        "name": "vblank_mode",
        "type": "hud",
        "category": "graphics",
        "description_fr": "VSync Mesa.",
        "description_en": "Mesa vsync mode."
    },

    # =========================================================
    # WINE / GSTREAMER (MULTIMEDIA STACK CONTROL)
    # =========================================================
    {
        "name": "GST_PLUGIN_PATH",
        "type": "wine",
        "category": "compatibility",
        "description_fr": "Chemin des plugins GStreamer. Vide pour éviter les conflits avec les plugins système ou Proton.",
        "description_en": "GStreamer plugin path. Empty to avoid conflicts with system or Proton plugins."
    },
    {
        "name": "GST_DEBUG",
        "type": "wine",
        "category": "debug",
        "description_fr": "Niveau de logs GStreamer. 0 désactive totalement les logs.",
        "description_en": "GStreamer debug level. 0 disables all logging."
    },
    {
        "name": "WINE_DISABLE_GSTREAMER",
        "type": "wine",
        "category": "compatibility",
        "description_fr": "Désactive l’utilisation de GStreamer dans Wine pour éviter les erreurs multimédia et dépendances cassées.",
        "description_en": "Disables Wine GStreamer integration to prevent multimedia errors and broken dependencies."
    },
    # =========================================================
    # GAME
    # =========================================================
    {
        "name": "USE_D3D11",
        "type": "game",
        "category": "graphics",
        "description_fr": "Force l'utilisation du moteur de rendu Direct3D 11 au lieu de versions plus récentes de DirectX.",
        "description_en": "Forces the use of the Direct3D 11 renderer instead of newer DirectX versions."
    },
    {
        "name": "USEALLAVAILABLECORES",
        "type": "game",
        "category": "performance",
        "description_fr": "Demande au moteur Unreal Engine d'utiliser tous les cœurs CPU disponibles pour le traitement du jeu.",
        "description_en": "Instructs Unreal Engine to use all available CPU cores for game processing."
    }
]
#------------------------------------------------------------------------------------

def has_proton_call():
    return which("proton-call") is not None

def has_wine():
    return which("wine") is not None

def has_mangohud():
    return which("mangohud") is not None

def has_gamemode():
    return which("gamemoderun") is not None


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

    print(f"[proton-autogen] FORCE PROFILE USER: {profile.get('name', 'unknown')}")

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
        "install": env_install_clean(),
        "ut99": env_ut99(),
        "quake": env_quake(),
        "win95": env_win95(),
        "ut3": env_ut3(),
        "valve": env_goldsrc(),
        "desktop": env_desktop(),
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
        "install": env_install_clean(),
        "oldgame": env_oldgame(),
        "ut99": env_ut99(),
        "quake": env_quake(),
        "win95": env_win95(),
        "ut3": env_ut3(),
        "valve": env_goldsrc(),
        "desktop": env_desktop(),
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
        print("[proton-autogen] ERROR: --profile requires a name")
        sys.exit(1)

    name = sys_argv[idx + 1]
    profile = load_user_profile(name)

    if not profile:
        print(f"[proton-autogen] ERROR: profile not found: {name}")
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
    FIXED signature compatible with proton-autogen
    """

    # MangoHud override
    if enable_mangohud:
        env.pop("DXVK_HUD", None)
        return env

    # Debug mode
    if debug_mode:
        env["DXVK_HUD"] = "compiler"
        return env

    # Default clean state
    env.pop("DXVK_HUD", None)
    return env



# Return the Wine/Proton prefix path for the selected prefix mode.

def get_prefix_path(prefix_mode: str, exe_path: str) -> str:
    root = os.path.expanduser("~/Documents/Proton/env")

    if prefix_mode == "auto":
        name = os.path.splitext(os.path.basename(exe_path))[0]

        safe_name = (
            name.replace(" ", "_")
                .replace("/", "_")
                .replace("\\", "_")
        )

        short_hash = hashlib.md5(exe_path.encode()).hexdigest()[:8]

        return os.path.join(root, f"{safe_name}-{short_hash}")

    if prefix_mode.startswith("auto-"):
        # déjà résolu → on le traite comme prefix direct
        return os.path.join(root, prefix_mode)

    prefixes = {
        "main": os.path.join(root, "main"),
        "shared": os.path.join(root, "shared"),
        "custom": os.path.expanduser("~/Documents/Proton/env/Proton Custom"),
    }

    return prefixes.get(prefix_mode, prefixes["main"])


def get_prefix_path_v1(prefix_mode: str, exe_path: str) -> str:
    root = os.path.expanduser("~/Documents/Proton/env")

    if prefix_mode == "auto":
        name = os.path.splitext(
            os.path.basename(exe_path)
        )[0]

        # Nettoyage minimal du nom
        safe_name = (
            name.replace(" ", "_")
                .replace("/", "_")
                .replace("\\", "_")
        )

        short_hash = hashlib.md5(
            exe_path.encode()
        ).hexdigest()[:8]

        return os.path.join(
            root,
            f"{safe_name}-{short_hash}"
        )

    prefixes = {
        "main": os.path.join(root, "main"),
        "shared": os.path.join(root, "shared"),
        "custom": os.path.expanduser(
            "~/Documents/Proton/env/Proton Custom"
        ),
    }

    return prefixes.get(
        prefix_mode,
        prefixes["main"]
    )


def add_ld_preload(env, library):
    """
    Ajoute une bibliothèque à LD_PRELOAD sans écraser
    les bibliothèques déjà présentes.
    """
    if not os.path.exists(library):
        print(f"[proton-autogen] WARNING: missing library: {library}")
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
        print(line, end="")


def _read_stderr(pipe, filters):
    for line in pipe:
        if any(f in line for f in filters):
            continue
        print(line, end="")



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
def find_mangohud_shim():
    """
    Search for the libMangoHud_shim.so library in the most common
    32-bit installation directories.

    The function iterates through a predefined list of candidate paths
    and returns the first existing library found.

    Returns:
        str | None:
            - The full path to libMangoHud_shim.so if found.
            - None if the library is not found in any of the checked locations.
    """
    candidates = [
        "/usr/lib32/mangohud/libMangoHud_shim.so",
        "/usr/lib/i386-linux-gnu/mangohud/libMangoHud_shim.so",
        "/usr/local/lib/i386-linux-gnu/mangohud/libMangoHud_shim.so",
        "/usr/local/lib32/mangohud/libMangoHud_shim.so",
    ]

    for path in candidates:
        if os.path.exists(path):
            return path

    return None




# Wine fallback execution.
# The executable is started from its parent directory to preserve
# relative paths required by some applications (DLLs, assets, etc.).


def run_standard(exe_path: str):
    print("[proton-autogen] Proton unavailable → using Wine fallback")

    if not has_wine():
        print("[proton-autogen] ERROR: No runtime found")
        print()
        print("Missing:")
        print("  - Proton")
        print("  - Wine")
        print()
        print("Install Wine:")
        print("  sudo apt install wine")
        sys.exit(1)

    if not Path(exe_path).is_file():
        print(f"✗ File not found: {exe_path}")
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
        print(f"✗ Error running {exe_path} with Wine: {e}")
        #sys.exit(1)
        return 1



# ---------------------------------------------------
# BASE CLEANER (shared)
# ---------------------------------------------------
def init_env():
    env = os.environ.copy()

    for k in [
        "LD_PRELOAD",
        "LD_LIBRARY_PATH",
        "VK_ICD_FILENAMES",
        "VK_DRIVER_FILES",
        "DXVK_HUD",
        "VKD3D_CONFIG",
        "WINEDEBUG",
        "RADV_PERFTEST",
    ]:
        env.pop(k, None)


    # =========================
    # FIX GStreamer Proton/Wine
    # =========================
    for k in [
        "GST_PLUGIN_PATH",
        "GST_PLUGIN_SYSTEM_PATH",
        "GST_REGISTRY",
        "GST_REGISTRY_UPDATE",
        "GST_DEBUG",
    ]:
        env.pop(k, None)


    env["STEAM_COMPAT_APP_ID"] = "0"


    return env

# ---------------------------------------------------
# 0. LAUNCHER PROFILE (legacy Photoshop 6)
# ---------------------------------------------------
def env_legacy_app():
    env = init_env()

    print("[proton-autogen] PROFILE: LEGACY APPLICATION")
    env["PROTON_USE_XALIA"] = "0"

    env["PROTON_NO_ESYNC"] = "1"
    env["PROTON_NO_FSYNC"] = "1"

    env["WINEESYNC"] = "0"
    env["WINEFSYNC"] = "0"

    env.pop("DXVK_HUD", None)

    env["vblank_mode"] = "0"
    env["mesa_glthread"] = "true"

    return env


# ---------------------------------------------------
# 1. LAUNCHER PROFILE (Battle.net, EA App, Ubisoft)
# ---------------------------------------------------
def env_launcher():
    env = init_env()

    print("[proton-autogen] PROFILE: LAUNCHER")

    env["PROTON_NO_ESYNC"] = "1"
    env["PROTON_NO_FSYNC"] = "1"

    env["WINEESYNC"] = "0"
    env["WINEFSYNC"] = "0"

    env["WINEDLLOVERRIDES"] = ""
    env["PROTONFIXES_DISABLE"] = "1"

    # IMPORTANT: stability > performance
    env["WINE_SIMULATE_WRITECOPY"] = "1"

    env["vblank_mode"] = "0"
    env["mesa_glthread"] = "true"

    return env


# ---------------------------------------------------
# 2. DX11 PROFILE (most games)
# ---------------------------------------------------
def env_dx11():
    env = init_env()

    print("[proton-autogen] PROFILE: DX11")
    env["PROTON_USE_XALIA"] = "0"

    env["PROTON_NO_ESYNC"] = "0"
    env["PROTON_NO_FSYNC"] = "0"

    env["WINEDLLOVERRIDES"] = ""

    env["WINEESYNC"] = "1"
    env["WINEFSYNC"] = "1"

    # Safe modern Vulkan behavior
    env["WINE_SIMULATE_WRITECOPY"] = "1"

    env.pop("DXVK_HUD", None)

    env["vblank_mode"] = "0"
    env["mesa_glthread"] = "true"

    return env

def env_dx11BNet():
    env = init_env()

    print("[proton-autogen] PROFILE: DX11 Battle.net")

    env["PROTON_USE_XALIA"] = "0"

    # DXVK / Vulkan stability
    env["DXVK_CONFIG"] = "dxgi.syncInterval=1"
    env["RADV_PERFTEST"] = "gpl,nggc"

    # Shader stability (important HOTS)
    env["DXVK_ASYNC"] = "1"

    env.pop("DXVK_HUD", None)

    # Clean Proton-managed sync (IMPORTANT)
    env.pop("PROTON_NO_ESYNC", None)
    env.pop("PROTON_NO_FSYNC", None)
    env.pop("WINEESYNC", None)
    env.pop("WINEFSYNC", None)

    env.pop("WINEDLLOVERRIDES", None)

    # silence multimedia stack
    env["GST_PLUGIN_PATH"] = ""
    env["GST_DEBUG"] = "0"
    env["WINE_DISABLE_GSTREAMER"] = "1"

    env["vblank_mode"] = "0"
    env["mesa_glthread"] = "true"

    return env


# ---------------------------------------------------
# 3. DX12 PROFILE (VKD3D)
# ---------------------------------------------------
def env_dx12():
    env = init_env()

    print("[proton-autogen] PROFILE: DX12 - VKD3D")

    env["PROTON_NO_ESYNC"] = "0"
    env["PROTON_NO_FSYNC"] = "0"

    # VKD3D tuning (safe default)
    env["VKD3D_CONFIG"] = "dxr"

    env["WINEDLLOVERRIDES"] = ""

    env["WINEESYNC"] = "1"
    env["WINEFSYNC"] = "1"

    # DO NOT enable RADV_PERFTEST by default (breaks some setups)
    # env["RADV_PERFTEST"] = "gpl"  # optional advanced users only

    env["vblank_mode"] = "0"
    env["mesa_glthread"] = "true"

    return env


# ---------------------------------------------------
# 4. OLD GAME PROFILE (DX8 / DX9 / WineD3D)
# ---------------------------------------------------
def env_oldgame():
    env = init_env()

    print("[proton-autogen] PROFILE: OLD GAME (DX8/DX9)")

    env["PROTON_USE_WINED3D"] = "1"

    env["WINEDLLOVERRIDES"] = "d3d8=n,b"

    env["PROTON_NO_ESYNC"] = "1"
    env["PROTON_NO_FSYNC"] = "1"

    env["WINEESYNC"] = "0"
    env["WINEFSYNC"] = "0"

    # disable DXVK completely behaviorally (WineD3D takes over)
    env.pop("DXVK_HUD", None)

    env["vblank_mode"] = "0"
    env["mesa_glthread"] = "true"

    return env

def env_dx8dg():
    env = init_env()

    print("[proton-autogen] PROFILE: OLD GAME (DX8) dgVoodooCpl")

    # HARD DISABLE DXVK / VKD3D PATH
    env["WINEDLLOVERRIDES"] = (
        "d3d8=n,b;"
        "d3d9=n,b;"
        "ddraw=n,b;"
        "dxgi=n;"
        "d3d11=n;"
        "d3d10=n"
    )

    env["PROTON_USE_WINED3D"] = "1"

    env["WINEDLLOVERRIDES"] = "d3d8=n,b;d3d9=n,b;ddraw=n,b"

    env["PROTON_NO_ESYNC"] = "1"
    env["PROTON_NO_FSYNC"] = "1"

    env["WINEESYNC"] = "0"
    env["WINEFSYNC"] = "0"

    env["vblank_mode"] = "0"
    env["mesa_glthread"] = "true"

    env["DXVK_ENABLE_NVAPI"] = "0"
    env.pop("DXVK_HUD", None)

    return env

def env_dx9dg():
    env = init_env()

    print("[proton-autogen] PROFILE: OLD GAME (DX9) dgVoodooCpl")

    # HARD DISABLE DXVK / VKD3D PATH
    env["WINEDLLOVERRIDES"] = (
        "d3d8=n,b;"
        "d3d9=n,b;"
        "ddraw=n,b;"
        "dxgi=n;"
        "d3d11=n;"
        "d3d10=n"
    )

    env["PROTON_USE_WINED3D"] = "1"

    env["WINEDLLOVERRIDES"] = "d3d9=n,b;d3d8=n,b;ddraw=n,b"

    env["PROTON_NO_ESYNC"] = "1"
    env["PROTON_NO_FSYNC"] = "1"

    env["WINEESYNC"] = "0"
    env["WINEFSYNC"] = "0"

    env["vblank_mode"] = "0"
    env["mesa_glthread"] = "true"

    env["DXVK_ENABLE_NVAPI"] = "0"
    env.pop("DXVK_HUD", None)

    return env


def env_dx9():
    env = init_env()

    print("[proton-autogen] PROFILE: OLD GAME (DX8/DX9)")

    env["PROTON_USE_WINED3D"] = "1"

    #env["WINE_FULLSCREEN_FSR"] = "0"
    #env["WINE_VK_FULLSCREEN_METHOD"] = "desktop"
    #env["DXVK_FULLSCREEN"] = "0"
    #env["WINEDLLOVERRIDES"] = "d3d8=n,b"
    env["DXVK_FRAME_RATE"] = "60"
    env["MANGOHUD_CONFIG"] = "fps_limit=60"
    env["MANGOHUD_OPENGL"] = "1"

    env["PROTON_NO_ESYNC"] = "1"
    env["PROTON_NO_FSYNC"] = "1"

    env["WINEESYNC"] = "0"
    env["WINEFSYNC"] = "0"

    # disable DXVK completely behaviorally (WineD3D takes over)
    env.pop("DXVK_HUD", None)

    env.pop("vblank_mode", None)
    env.pop("mesa_glthread", None)


    return env


def env_install_clean():
    env = init_env()

    print("[proton-autogen] PROFILE: INSTALL CLEAN (legacy Windows setup)")

    # MUST: WineD3D only
    env["PROTON_USE_WINED3D"] = "1"

    # disable ALL async/sync complexity
    env["PROTON_NO_ESYNC"] = "1"
    env["PROTON_NO_FSYNC"] = "1"
    env["WINEESYNC"] = "0"
    env["WINEFSYNC"] = "0"

    # no overlays at all
    env.pop("DXVK_HUD", None)
    env.pop("MANGOHUD_CONFIG", None)
    env.pop("MANGOHUD_OPENGL", None)

    # kill all DLL override influence
    env.pop("WINEDLLOVERRIDES", None)

    # avoid driver-side tweaks
    env.pop("vblank_mode", None)
    env.pop("mesa_glthread", None)

    return env


def env_dx9opengl():
    env = init_env()

    print("[proton-autogen] PROFILE: OLD GAME (DX8/DX9) OPENGL")

    env["PROTON_USE_WINED3D"] = "1"

    env["DXVK_FRAME_RATE"] = "60"
    env["MANGOHUD_CONFIG"] = "fps_limit=60"
    env["MANGOHUD_OPENGL"] = "1"

    env["PROTON_NO_ESYNC"] = "1"
    env["PROTON_NO_FSYNC"] = "1"

    env["WINEESYNC"] = "0"
    env["WINEFSYNC"] = "0"

    # disable DXVK completely behaviorally (WineD3D takes over)
    env.pop("DXVK_HUD", None)

    env.pop("vblank_mode", None)
    env.pop("mesa_glthread", None)


    return env

# ---------------------------------------------------
# 5.  PROFILE (UnrealTournament) AND QUAKE
# ---------------------------------------------------

def env_ut99():
    env = init_env()

    print("[proton-autogen] PROFILE: UNREAL TOURNAMENT (UT99)")
    print("[proton-autogen] Note: UT99 is more stable in windowed mode")

    env["PROTON_NO_ESYNC"] = "1"
    env["PROTON_NO_FSYNC"] = "1"
    env["PROTON_USE_WINED3D"] = "1"
    env["WINEDLLOVERRIDES"] = "d3d8=n,b"

    # sécurité : éviter toute interférence DXVK / async layers
    env.pop("DXVK_HUD", None)
    env["WINEESYNC"] = "0"
    env["WINEFSYNC"] = "0"

    env["vblank_mode"] = "0"
    env["mesa_glthread"] = "true"

    return env


def env_quake():
    env = init_env()

    print("[proton-autogen] PROFILE: QUAKE II CLEAN")
    #print("[proton-autogen] RECOMMANDATION: Pour une expérience stable, utiliser Yamagi Quake II")
    print("\033[93m[proton-autogen] RECOMMANDATION: Yamagi Quake II est recommandé pour stabilité\033[0m")
    print("[proton-autogen] https://www.yamagi.org/quake2/")

    # désactiver Xalia
    env["PROTON_USE_XALIA"] = "0"

    # forcer WineD3D (old OpenGL path)
    env["PROTON_USE_WINED3D"] = "1"


    # prefix propre
    env["WINEPREFIX"] = os.path.expanduser("~/quake2-test")

    # sync stable (laisser Proton gérer)
    env.pop("PROTON_NO_ESYNC", None)
    env.pop("PROTON_NO_FSYNC", None)
    env.pop("WINEESYNC", None)
    env.pop("WINEFSYNC", None)

    # pas d’overrides cassants
    env.pop("WINEDLLOVERRIDES", None)

    return env

#-----------------------------------------------------------
# Valve - Sierra - Old Game (Hal-Life)
#-----------------------------------------------------------
def env_goldsrc():
    env = init_env()

    print("[proton-autogen] GOLDSRC STEAM-LIKE PROFILE")

    # =========================
    # 🎮 RENDERING
    # =========================
    # GoldSrc stable = OpenGL via WineD3D
    env["PROTON_USE_WINED3D"] = "1"
    env["DXVK_HUD"] = "0"
    env["VKD3D_CONFIG"] = ""

    # =========================
    # 🧠 SOUND (Miles Audio)
    # =========================
    # IMPORTANT: évite crash audio GoldSrc
    env["WINEDLLOVERRIDES"] = "mss32=builtin"

    # =========================
    # 🖱️ INPUT (GoldSrc safe mode)
    # =========================
    # désactive Xalia proprement
    env["PROTON_USE_XALIA"] = "0"
    env["XALIA"] = "0"

    # SDL overrides forcés en mode neutre (évite input cassé)
    env["SDL_MOUSE_AUTO_CAPTURE"] = "0"
    env["SDL_MOUSE_RELATIVE_MODE_WARP"] = "0"
    env["SDL_HINT_GRAB_KEYBOARD"] = "0"

    # comportement fenêtre stable
    env["SDL_VIDEO_MINIMIZE_ON_FOCUS_LOSS"] = "0"

    env["SDL_VIDEO_X11_NET_WM_BYPASS_COMPOSITOR"] = "0"
    env["MESA_GL_VERSION_OVERRIDE"] = "3.3"
    env["MESA_GLSL_VERSION_OVERRIDE"] = "330"

    # =========================
    # ⚙️ SYNC (STABILITY MODE)
    # =========================
    env["PROTON_NO_ESYNC"] = "1"
    env["PROTON_NO_FSYNC"] = "1"
    env["WINEESYNC"] = "0"
    env["WINEFSYNC"] = "0"

    # =========================
    # 🧪 DEBUG SAFE MODE
    # =========================
    #env["WINEDEBUG"] = "-all"
    #env["WINEDEBUG"] = "+loaddll,+module"

    return env


def env_gold_test():
    env = init_env()

    print("[proton-autogen] SAFE GOLDSRC PROFILE")

    # --- CRITICAL ---
    env["PROTON_USE_XALIA"] = "0"
    env["WINEDLLOVERRIDES"] = "mss32=builtin"

    # INPUT minimal
    env["SDL_MOUSE_RELATIVE_MODE_WARP"] = "1"
    env["SDL_MOUSE_AUTO_CAPTURE"] = "1"

    # compositing safe
    env["SDL_VIDEO_X11_NET_WM_BYPASS_COMPOSITOR"] = "0"

    return env

def env_goldsrc_full():
    env = init_env()

    print("[proton-autogen] PROFILE: GOLDSRC (Half-Life)")

    # OpenGL natif propre
    env.pop("PROTON_USE_WINED3D", None)

    #env["WINEDLLOVERRIDES"] = "mss32=n,b"

    # --- CRITICAL ---
    env["PROTON_USE_XALIA"] = "0"
    #env.pop("XALIA", None)

    # --- GOLD SRC FIX ---
    env["WINEDLLOVERRIDES"] = "mss32=native,builtin"

    # sync stable
    env.pop("PROTON_NO_ESYNC", None)
    env.pop("PROTON_NO_FSYNC", None)
    env.pop("WINEESYNC", None)
    env.pop("WINEFSYNC", None)

    # éviter interférences Vulkan/DXVK
    env.pop("DXVK_HUD", None)
    env.pop("VKD3D_CONFIG", None)

    # SDL input fixes (important pour GoldSrc)
    env["SDL_MOUSE_RELATIVE_MODE_WARP"] = "1"
    env["SDL_MOUSE_AUTO_CAPTURE"] = "1"
    env["SDL_HINT_GRAB_KEYBOARD"] = "1"
    env["SDL_VIDEO_X11_NET_WM_BYPASS_COMPOSITOR"] = "0"

    # IMPORTANT: évite double capture
    env["SDL_VIDEO_MINIMIZE_ON_FOCUS_LOSS"] = "0"

    return env
#-----------------------------------------------------------
# DirectDraw
#-----------------------------------------------------------
def env_win95():
    env = init_env()
    print("[proton-autogen] PROFILE: Win 95")

    env["PROTON_USE_XALIA"] = "0"
    env["PROTON_USE_WINED3D"] = "1"

    env["PROTON_NO_ESYNC"] = "1"
    env["PROTON_NO_FSYNC"] = "1"

    env["WINEESYNC"] = "0"
    env["WINEFSYNC"] = "0"

    #env["WINE_VK_FULLSCREEN_METHOD"] = "desktop"
    env["SDL_VIDEO_X11_NET_WM_BYPASS_COMPOSITOR"] = "0"

    env.pop("DXVK_HUD", None)
    env.pop("VKD3D_CONFIG", None)

    return env


def env_win95Beta():
    env = init_env()
    print("[proton-autogen] PROFILE: Win 95 Beta")

    env["PROTON_USE_XALIA"] = "0"
    env["PROTON_USE_WINED3D"] = "1"

    env["PROTON_NO_ESYNC"] = "1"
    env["PROTON_NO_FSYNC"] = "1"

    env["WINEESYNC"] = "0"
    env["WINEFSYNC"] = "0"

    return env

def env_DDraw():
    env = init_env()

    print("[proton-autogen] PROFILE: DirectDraw")

    env["PROTON_USE_XALIA"] = "0"

    env["PROTON_NO_ESYNC"] = "1"
    env["PROTON_NO_FSYNC"] = "1"

    env["WINEESYNC"] = "0"
    env["WINEFSYNC"] = "0"

    env.pop("WINEDLLOVERRIDES", None)
    env.pop("DXVK_HUD", None)

    env["vblank_mode"] = "0"
    env["mesa_glthread"] = "true"

    return env

#-----------------------------------------------------------
# 6. PROFILE (UT3)
#-----------------------------------------------------------

def env_ut3():
    env = init_env()

    print("[proton-autogen] PROFILE: UT3 FIXED (BETA)")

    env["PROTON_NO_FSYNC"] = "1"
    env["PROTON_NO_ESYNC"] = "0"

    # IMPORTANT UE3 stability AMD Polaris
    env["WINEESYNC"] = "1"
    env["WINEFSYNC"] = "0"

    # DXVK must stay clean
    env.pop("PROTON_USE_WINED3D", None)
    env.pop("WINEDLLOVERRIDES", None)

    # DEBUG ONLY (désactivé par défaut)
    env.pop("DXVK_HUD", None)

    # UE3 stability tweak
    env["DXVK_CONFIG"] = "dxgi.customSwapchain=false"

    env["vblank_mode"] = "0"
    env["mesa_glthread"] = "true"

    return env


#-----------------------------------------------------------
# 7. PROFILE DESKTOP
#-----------------------------------------------------------

def env_desktop():
    env = init_env()

    print("[proton-autogen] PROFILE: DESKTOP")
    env["PROTON_USE_XALIA"] = "0"

    env["PROTON_NO_ESYNC"] = "1"
    env["PROTON_NO_FSYNC"] = "1"

    env["WINEESYNC"] = "0"
    env["WINEFSYNC"] = "0"

    env.pop("DXVK_HUD", None)
    env.pop("VKD3D_CONFIG", None)

    env["vblank_mode"] = "0"
    env["mesa_glthread"] = "true"

    return env

def base_env(enable_mangohud=False, enable_gamemode=False, exe_path="", exe_type=""):
    print(f"[proton-autogen] INIT PROFILE - type: {exe_type}")

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
        "ut3": env_ut3,
        "oldgame": env_oldgame,
        "valve": env_goldsrc,
        "dx9": env_dx9,
        "dx8dg": env_dx8dg,
        "dx9dg": env_dx9dg,
        "dx9opengl": env_dx9opengl,
    }

    env = env_factories.get(exe_type, env_dx11)()


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
        env["WINEDEBUG"] = "+loaddll,+module"
    elif VERBOSE:
        env["PROTON_LOG"] = "1"
        env["WINEDEBUG"] = "-all,-trace,-relay,-seh"
    else:
        env["PROTON_LOG"] = "0"

    if DEBUG or VERBOSE:
        print(f"[proton-autogen] SYNC: WINEESYNC={env.get('WINEESYNC')} WINEFSYNC={env.get('WINEFSYNC')}")
        print(f"[proton-autogen] SYNC: PROTON_NO_FSYNC={env.get('PROTON_NO_FSYNC')} PROTON_NO_ESYNC={env.get('PROTON_NO_ESYNC')}")
        print(f"[proton-autogen] SYNC: WINEDLLOVERRIDES={env.get('WINEDLLOVERRIDES')} DXVK_HUD={env.get('DXVK_HUD')}")
        print(f"[proton-autogen] SYNC: PROTON_USE_WINED3D={env.get('PROTON_USE_WINED3D')} VKD3D_CONFIG={env.get('VKD3D_CONFIG')}")
        print(f"[proton-autogen] Xalia     : {'disabled' if env.get('PROTON_USE_XALIA') == '0' else 'enabled'}")
        # WINEDEBUG
        print(f"[proton-autogen] SYNC: WINEDEBUG={env.get('WINEDEBUG')} PROTON_LOG={env.get('PROTON_LOG')}")

        print("[DEBUG] DXVK =", "DXVK_HUD" not in env)
        print("[DEBUG] WINED3D =", env.get("PROTON_USE_WINED3D"))
        print("[DEBUG] VKD3D =", env.get("VKD3D_CONFIG"))
        print("[DEBUG] WINEDLLOVERRIDES =", env.get("WINEDLLOVERRIDES")) # WINEDLLOVERRIDES
        print(f"[DEBUG] FINAL EXEC: {exe_path}")
    else:
        print(f"[proton-autogen] SYNC: MANGOHUD={env.get('MANGOHUD')} MANGOHUD_DLSYM={env.get('MANGOHUD_DLSYM')}")
        print(
            f"[proton-autogen] Apply PROFILE={exe_type.upper()} | "
            f"SYNC={'ON' if env.get('WINEESYNC') == '1' else 'OFF'} | "
            f"WINED3D={'ON' if env.get('PROTON_USE_WINED3D') == '1' else 'OFF'} | "
            f"XALIA={'OFF' if env.get('PROTON_USE_XALIA') == '0' else 'ON'} | "
            f"DXVK_HUD={env.get('DXVK_HUD') or 'OFF'}"
        )


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


def check_mangohud_abi(lib):
    import subprocess
    out = subprocess.getoutput(f"ldd {lib}")
    return "libspdlog.so.1.15" not in out

def run_game_proton(exe_path, exe_type, proton, launch_mode="proton",
                    enable_mangohud=False, enable_gamemode=False,
                    prefix_mode="main"):


    arch = get_exe_arch(exe_path)
    print(f"[proton-autogen] EXE architecture: {arch}")

    game_id = hashlib.md5(exe_path.encode()).hexdigest()

    # =========================
    # PROTON MODE
    # =========================
    if launch_mode == "proton":

        env = base_env(
            enable_mangohud=enable_mangohud,
            enable_gamemode=enable_gamemode,
            exe_path=exe_path,
            exe_type=exe_type
        )

        prefix_path = get_prefix_path(prefix_mode, exe_path)
        print(f"[proton-autogen] Prefix mode : {prefix_mode}")
        print(f"[proton-autogen] Prefix path : {prefix_path}")

        env["STEAM_COMPAT_DATA_PATH"] = prefix_path
        os.makedirs(prefix_path, exist_ok=True)

        env["STEAM_COMPAT_CLIENT_INSTALL_PATH"] = os.path.expanduser("~/.steam/steam")
        env["STEAM_COMPAT_TOOL_PATHS"] = proton_path(proton)

        cmd = [
            os.path.join(proton_path(proton), "proton"),
            "run",
            exe_path
        ]

    # =========================
    # PROTON-CALL MODE
    # =========================
    elif launch_mode == "proton-call":

        env = base_env(
            enable_mangohud=enable_mangohud,
            enable_gamemode=enable_gamemode,
            exe_path=exe_path,
            exe_type=exe_type
        )

        # keep prefix if defined externally
        if "STEAM_COMPAT_DATA_PATH" not in os.environ:
            env.pop("STEAM_COMPAT_DATA_PATH", None)

        for k in [
            "STEAM_COMPAT_CLIENT_INSTALL_PATH",
            "STEAM_COMPAT_TOOL_PATHS",
            "STEAM_COMPAT_APP_ID"
        ]:
            env.pop(k, None)

        cmd = [
            "proton-call",
            "-c", proton_path(proton),
            "-r", exe_path,
            "--",
        ] + [exe_path] + sys.argv[2:]

    else:
        raise ValueError(f"Unknown launch mode: {launch_mode}")

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
            print("[proton-autogen] 32-bit legacy game detected")

            mangohud_shim = find_mangohud_shim()

            if mangohud_shim and os.path.exists(mangohud_shim):
                if not check_mangohud_abi(mangohud_shim):
                    print("[proton-autogen] MangoHud ABI mismatch detected - skipping")
                else:
                    env = add_ld_preload(env, mangohud_shim)
            else:
                print("[proton-autogen] MangoHud 32-bit shim missing")

        # optional: Vulkan explicit toggle
        if exe_type in ["vulkan", "dxvk"]:
            env["MANGOHUD"] = "1"
    else:
        env.pop("MANGOHUD", None)
    """
    if enable_mangohud and has_mangohud():
        env["MANGOHUD"] = "1"
        env["MANGOHUD_DLSYM"] = "1"
        env["MANGOHUD_OPENGL"] = "1"
        env["MANGOHUD_CONFIG"] = "fps_limit=60"
        env["DXVK_HUD"] = "0"

        if exe_type in ["dx9", "dx9opengl", "oldgame", "ut99", "ut3", "valve"]:

            if is_32bit_exe(exe_path):
                print("[proton-autogen] 32-bit legacy game detected")
                mangohud_shim = find_mangohud_shim()
                if mangohud_shim:
                    if os.path.exists(mangohud_shim):
                        env = add_ld_preload(env, mangohud_shim)
                    else:
                        print("[proton-autogen] MangoHud 32-bit shim missing")

    else:
        env.pop("MANGOHUD", None)
    """
    if enable_gamemode and has_gamemode():
        env["GAMEMODE"] = "1"

    print(f"[proton-autogen] Launch mode: {launch_mode}")


    if enable_mangohud and has_mangohud():
        # =========================
        # DEBUG ENVIRONMENT
        # =========================
        for key in [
            "MANGOHUD",
            "MANGOHUD_DLSYM",
            "MANGOHUD_CONFIG",
            "MANGOHUD_OPENGL",
            "LD_PRELOAD"
        ]:
            print(f"[DEBUG] {key}={env.get(key)}")
        filters = [ "wrong ELF class", ]
        result_code = -1
        # Code KO

        cmd_cwd = os.path.dirname(exe_path)

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
        returncode = subprocess.run(cmd, env=env, cwd=cmd_cwd)
        return returncode

def print_about():
    print(f"""proton-autogen
══════════════

Lightweight Proton launcher for Linux.

Automatically discovers Proton installations,
selects the best available version, and launches
Windows executables with minimal configuration.

Features
────────
• Automatic Proton discovery
• Smart version selection
• Wine fallback
• Per-game profiles
• GameMode support
• MangoHud integration
• Steam & Flatpak compatibility

Version : {VERSION}
Author  : N3oray
License : MIT

Repository
https://github.com/N3oRay/proton-autogen
PPA
sudo add-apt-repository ppa:n3oray/proton-autogen
""")


def get_about_text():
    return f"""PROTON-AUTOGEN

Lightweight Proton launcher for Linux.

Automatically discovers Proton installations,
selects the best available version, and launches
Windows executables with minimal configuration.

────────────────────────
FEATURES
────────────────────────
• Automatic Proton discovery
• Smart version selection
• Wine fallback
• Per-game profiles
• GameMode support
• MangoHud integration
• Steam & Flatpak compatibility

────────────────────────
VERSION
────────────────────────
{VERSION}

────────────────────────
AUTHOR
────────────────────────
N3oray

────────────────────────
LICENSE
────────────────────────
MIT

────────────────────────
REPOSITORY
────────────────────────
https://github.com/N3oRay/proton-autogen

────────────────────────
PPA
────────────────────────
sudo add-apt-repository ppa:n3oray/proton-autogen
"""
