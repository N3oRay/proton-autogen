from proton_autogen.profiles.base import init_env


# ---------------------------------------------------
# RageMP
# ---------------------------------------------------
def env_ragemp():
    env = init_env()

    print("[proton-autogen] PROFILE: RageMP Compatibility")

    # Synchronisation Proton
    env["WINEESYNC"] = "1"
    env["WINEFSYNC"] = "1"

    env.pop("PROTON_NO_ESYNC", None)
    env.pop("PROTON_NO_FSYNC", None)

    # ------------------------------------------------
    # CEF / Chromium (RageMP UI)
    # ------------------------------------------------

    # Désactive l'accélération GPU CEF
    # utile sous Wine/Proton
    env["CEF_FORCE_GPU"] = "0"

    # Evite les problèmes ANGLE/OpenGL
    env["CEF_DISABLE_GPU"] = "1"

    # ------------------------------------------------
    # Réseau Windows
    # ------------------------------------------------

    # meilleure compatibilité WinHTTP
    env["WINHTTP_TIMEOUT"] = "60000"

    # ------------------------------------------------
    # Nettoyage overlays
    # ------------------------------------------------

    env.pop("DXVK_HUD", None)

    env.pop("MANGOHUD", None)
    env.pop("MANGOHUD_DLSYM", None)

    # ------------------------------------------------
    # DXVK
    # ------------------------------------------------

    # GTA reste en DX11 derrière RageMP
    env["DXVK_LOG_LEVEL"] = "none"

    # ------------------------------------------------
    # X11 (tu es sous Cinnamon/X11)
    # ------------------------------------------------

    env["SDL_VIDEODRIVER"] = "x11"

    return env
