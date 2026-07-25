#dector.py


# "GPU Optimization Mode: Performance"
#"label": "Performance (NVIDIA RTX optimized)"
#"description": "Optimized for NVIDIA GPUs with Proton-GE and Vulkan caching"

#auto	système décide
#safe	stabilité
#balanced	défaut recommandé
#performance	priorité FPS

# Dectection des profils GPU / OS
# dector.py

# Résout les fonctionnalités du jeu avant leur utilisation.
# Les options automatiques (ex. gpu="auto") sont remplacées
# par une valeur adaptée au système détecté, sans modifier
# la configuration d'origine du jeu.
# Si l'utilisateur n'a pas choisi explicitement un profil GPU, on le détermine automatiquement en fonction du système.

#Note:
# OK - DXVK_ASYNC: Enables asynchronous shader compilation to reduce stuttering caused by shader loading.
# OK - PROTON_ENABLE_NVAPI: Enables NVIDIA NVAPI support for NVIDIA-specific features.
# OK - PROTON_USE_NTSYNC: Enables NTSync for improved synchronization performance and lower CPU overhead.
# NO - PROTON_ENABLE_WAYLAND: Enables native Wayland support in Proton when available.
# KO - PROTON_ENABLE_HDR: Enables HDR support for compatible games. Deprecated in Proton-CachyOS, where HDR is enabled automatically.
# OK - gamemoderun: Launches the game through GameMode to apply gaming performance optimizations.
# NA - –use-d3d11: Forces the game to use the Direct3D 11 renderer.

# -USEALLAVAILABLECORES: Instructs Unreal Engine to use all available CPU cores. (Principalement pour des jeux Unreal Engine (UE4/UE5).
#Quelques exemples où elle est documentée ou officiellement reconnue :
# Satisfactory (UE5) : le wiki officiel documente -USEALLAVAILABLECORES parmi les arguments disponibles.
#Fortnite (UE5) : l'argument est fréquemment cité dans les guides dédiés à Unreal)

def resolve_game_features(game: dict, system: dict):
    features = game.get("features", {}).copy()

    gpu_mode = features.get("gpu", "auto")

    if gpu_mode == "auto":
        gpu_mode = detect_gpu_profile(system)

    features["gpu"] = gpu_mode

    return features


def detect_wayland_mode(system, features=None):
    """
    Détermine si Proton doit utiliser Wayland natif.

    Retour:
        True  -> activer Wayland Proton
        False -> rester X11/XWayland
    """

    if not isinstance(system, dict):
        system = {}

    if not isinstance(features, dict):
        features = {}

    # Override utilisateur
    mode = features.get("wayland", "auto")

    if mode == "on":
        return True

    if mode == "off":
        return False

    # Auto
    wayland = system.get("wayland", False)
    gpu = system.get("gpu", "").lower()

    # Steam Deck : Wayland natif recommandé
    if system.get("steam_deck"):
        return True

    # NVIDIA + Wayland :
    # rester prudent (CEF, anciens jeux, launchers)
    if wayland and gpu == "nvidia":
        return False

    # AMD/Intel modernes :
    # généralement OK
    if wayland and gpu in ("amd", "intel"):
        return True

    return False



def detect_gpu_profile(system):
    gpu = system.get("gpu")
    gpu_hybrid = system.get("gpu_hybrid", False)
    wayland = system.get("wayland", False)
    steam_deck = system.get("steam_deck", False)

    ram = system.get("ram", 0)
    vram = system.get("vram", 0)
    cpu_threads = system.get("cpu_threads", system.get("cpu_cores", 0))

    # Cas particuliers
    if steam_deck:
        return "balanced"

    # Wayland reste le choix le plus sûr
    if wayland:
        return "safe"

    # GPU hybride : privilégier la stabilité
    if gpu_hybrid:
        return "balanced"

    # Machines haut de gamme
    if (
        gpu in ("nvidia", "amd")
        and vram >= 8
        and ram >= 16
        and cpu_threads >= 8
    ):
        return "extreme"

    # Machines moyenne gamme
    if (
        gpu in ("nvidia", "amd")
        and vram >= 4
        and ram >= 8
        and cpu_threads >= 2
    ):
        return "performance"



    # GPU dédié mais configuration moyenne
    if gpu in ("nvidia", "amd"):
        return "balanced"

    # GPU intégré ou inconnu
    return "safe"



def gpu_env(system=None, features=None):
    """
    Génère les variables d'environnement GPU selon le profil choisi.

    Args:
        system (dict): informations système détectées
        features (dict): options du jeu

    Returns:
        dict: variables environnementales à appliquer
    """

    # Sécurité : éviter None ou mauvais type
    if not isinstance(system, dict):
        system = {}

    if not isinstance(features, dict):
        features = {}

    env = {}
    # -----------------------
    # Wayland / X11 Proton
    # -----------------------
    if detect_wayland_mode(system, features):
        env["PROTON_ENABLE_WAYLAND"] = "1"
    else:
        env["PROTON_ENABLE_WAYLAND"] = "0"

    # Valeurs par défaut
    profile = features.get("gpu", "auto")
    gpu = system.get("gpu", "")

    # Normalisation
    if not isinstance(profile, str):
        profile = "auto"

    if not isinstance(gpu, str):
        gpu = ""

    gpu = gpu.lower()


    # Les autres profils (auto...) ne modifient rien
    if profile not in ("balanced", "performance", "extreme"):
        return env
    # Profils GPU pris en charge
    if gpu == "nvidia":
        env["__GL_SHADER_DISK_CACHE"] = "1"

        if profile in ("performance", "extreme"):
            env["PROTON_ENABLE_NVAPI"] = "1"

        if profile == "extreme":
            env["__GL_SHADER_DISK_CACHE_SKIP_CLEANUP"] = "1"


    elif gpu == "amd":
        if profile == "balanced":
            env["MESA_SHADER_CACHE_MAX_SIZE"] = "5G"

        elif profile == "performance":
            env["RADV_PERFTEST"] = "aco,sam"
            env["MESA_SHADER_CACHE_MAX_SIZE"] = "10G"

        elif profile == "extreme":
            env["RADV_PERFTEST"] = "aco,gpl"
            env["MESA_SHADER_CACHE_MAX_SIZE"] = "20G"

            if system.get("sam_support"):
                env["RADV_PERFTEST"] += ",sam" #sam : améliore l'accès CPU → VRAM sur les GPU compatibles.

    # Intel / inconnu :
    # on ne force rien
    return env


#PROTON_DISABLE_NVAPI=1 DXVK_NVAPI_VKREFLEX=1 RADV_PERFMODE=high PROTON_USE_NTSYNC=1 RADV_PERFTEST=sam
#----------------------------------------------------------------
#system = { "gpu": "nvidia", "gpu_hybrid": False, "wayland": True, "steam_deck": False, "cpu_cores": 8, "cpu_threads": 16, "ram": 32, "vram": 12, }

def detect_gpu_profile_simple(system):
    gpu = system.get("gpu")
    wayland = system.get("wayland")
    steam_deck = system.get("steam_deck")

    if steam_deck:
        return "balanced"

    if wayland:
        return "safe"

    if gpu in ("nvidia", "amd"):
        return "performance"

    return "balanced"
#----------------------------------------------------------------


def detect_use_all_available_cores(system):
    if system.get("steam_deck"):
        return False

    if system.get("cpu_threads", 0) >= 8:
        return True

    return False

def cpu_args(system, features):
    enabled = features.get("use_all_available_cores", "auto")

    if enabled == "auto":
        enabled = detect_use_all_available_cores(system)

    return ["-USEALLAVAILABLECORES"] if enabled else []
