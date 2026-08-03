from proton_autogen.profiles.base import init_env
from proton_autogen.utils.logger import StructuredLogger
#-------------------------- Init Log -------------------
logger = StructuredLogger("proton-autogen.profiles.ragemp")


# ---------------------------------------------------
# RageMP - old profiles - New dotnet_csharp
# ---------------------------------------------------
def env_ragemp(prefix=None, proton_path=None, exe_path=None):
    env = init_env()

    logger.info("[proton-autogen] PROFILE: RageMP Compatibility")

    # Synchronisation Proton
    env["WINEESYNC"] = "1"
    env["WINEFSYNC"] = "1"

    env.pop("PROTON_NO_ESYNC", None)
    env.pop("PROTON_NO_FSYNC", None)

    # ------------------------------------------------
    # CEF / Chromium (RageMP UI)
    # ------------------------------------------------

    # CEF (RageMP launcher/UI)
    env["CEF_FORCE_GPU"] = "1"
    env.pop("CEF_DISABLE_GPU", None)

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
