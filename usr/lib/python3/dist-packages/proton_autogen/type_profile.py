
import os
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
# GTA V
# ---------------------------------------------------
def env_gtav_compat():
    env = init_env()

    print("[proton-autogen] PROFILE: GTA V Compatibility")

    # Activer ESYNC/FSYNC
    env["WINEESYNC"] = "1"
    env["WINEFSYNC"] = "1"

    # Laisser Proton gérer ESYNC/FSYNC
    env.pop("PROTON_NO_ESYNC", None)
    env.pop("PROTON_NO_FSYNC", None)

    # Compatibilité mémoire
    env["WINE_SIMULATE_WRITECOPY"] = "1"

    # Désactiver tout HUD éventuel
    env.pop("DXVK_HUD", None)

    # Désactiver le VSync Mesa
    env["vblank_mode"] = "0"

    return env



def env_gtav_x11():
    env = init_env()

    print("[proton-autogen] PROFILE: GTA V X11")

    # Synchronisation
    env["WINEESYNC"] = "1"
    env["WINEFSYNC"] = "1"

    env.pop("PROTON_NO_ESYNC", None)
    env.pop("PROTON_NO_FSYNC", None)

    # Compatibilité mémoire
    env["WINE_SIMULATE_WRITECOPY"] = "1"

    # Désactive les overlays
    env.pop("DXVK_HUD", None)

    # Désactive le VSync Mesa
    env["vblank_mode"] = "0"

    # Force X11 via SDL
    env["SDL_VIDEODRIVER"] = "x11"

    return env


def env_gtav_safe():
    env = init_env()

    print("[proton-autogen] PROFILE: GTA V SAFE")

    # Synchronisation
    env["WINEESYNC"] = "1"
    env["WINEFSYNC"] = "1"

    env.pop("PROTON_NO_ESYNC", None)
    env.pop("PROTON_NO_FSYNC", None)

    # Compatibilité mémoire
    env["WINE_SIMULATE_WRITECOPY"] = "1"

    # Nettoyage des overlays
    env.pop("DXVK_HUD", None)

    # Désactive le VSync Mesa
    env["vblank_mode"] = "0"

    # Désactive HDR DXVK
    env["DXVK_HDR"] = "0"

    # Force X11
    env["SDL_VIDEODRIVER"] = "x11"

    # Désactive Gamescope si l'utilisateur le lance
    env.pop("GAMESCOPE_WSI", None)
    env.pop("ENABLE_GAMESCOPE_WSI", None)

    return env
