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

def resolve_game_features(game: dict, system: dict):
    features = game.get("features", {}).copy()

    gpu_mode = features.get("gpu", "auto")

    if gpu_mode == "auto":
        gpu_mode = detect_gpu_profile(system)

    features["gpu"] = gpu_mode

    return features

def detect_gpu_profile(system):
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


def gpu_env(system, features):
    if features.get("gpu") != "performance":
        return {}

    if system.get("gpu") == "nvidia":
        return {
            "PROTON_ENABLE_NVAPI": "1",
            "__GL_SHADER_DISK_CACHE": "1"
        }

    if system.get("gpu") == "amd":
        return {
            "RADV_PERFTEST": "aco"
        }

    return {}
