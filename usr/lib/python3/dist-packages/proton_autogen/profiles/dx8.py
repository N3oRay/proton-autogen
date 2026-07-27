
from pathlib import Path
from proton_autogen.profiles.base import init_env
from proton_autogen.utils.dllresolver import resolve_game_dlls

from proton_autogen.utils.logger import StructuredLogger

logger = StructuredLogger("proton-autogen.profiles.env_dx8")


def env_dx8(prefix=None, proton_path=None, exe_path=None):
    env = init_env()

    logger.info("[proton-autogen] PROFILE: OLD GAME (DirectDraw/dgVoodoo)")

    # dgVoodoo prend la main sur les anciens API DirectX
    env.pop("WINEDLLOVERRIDES", None)

    env["WINEDLLOVERRIDES"] = "ddraw=n,b"

    #env["WINEDLLOVERRIDES"] = ( "ddraw=n,b;" "d3d8=n,b;" "d3d9=n,b;" "dxgi=n;" "d3d11=n" )
    env["WINE_FULLSCREEN_FSR"] = "1"

    # Pas de DXVK/VKD3D
    #env["PROTON_USE_WINED3D"] = "1"
    # Pas de DXVK/VKD3D forcé
    env.pop("PROTON_USE_WINED3D", None)

    # Jeux anciens
    env["PROTON_NO_ESYNC"] = "1"
    env["PROTON_NO_FSYNC"] = "1"
    env["WINEESYNC"] = "0"
    env["WINEFSYNC"] = "0"

    # Évite certains soucis Mesa
    env["vblank_mode"] = "0"

    # Désactive les overlays
    env.pop("DXVK_HUD", None)
    env["DXVK_ENABLE_NVAPI"] = "0"

    return env


def env_dx8dg(prefix=None, proton_path=None, exe_path=None, inject_dll=False):
    env = init_env()
    if inject_dll:
        if exe_path:
            try:
                injected = resolve_game_dlls(
                    game_dir=Path(exe_path).parent,
                    proton_path=proton_path,
                    required_dlls=["ddraw.dll"],
                )

                if injected:
                    logger.info("Injected DLLs: %s", ", ".join(injected))

            except RuntimeError as e:
                logger.error("DLL injection failed: %s", e)

    logger.info("[proton-autogen] PROFILE: DirectDraw (native override)")

    # Wrapper DirectDraw local
    env["WINEDLLOVERRIDES"] = "ddraw=n,b"
    #env["WINEDLLOVERRIDES"] = "ddraw=n"

    # Utiliser DXVK si disponible
    env["PROTON_USE_WINED3D"] = "1"
    env["PULSE_LATENCY_MSEC"] = "150"

    # Pas de synchronisation Wine
    env["PROTON_NO_ESYNC"] = "1"
    env["PROTON_NO_FSYNC"] = "1"
    env["WINEESYNC"] = "0"
    env["WINEFSYNC"] = "0"

    #env["WINE_DDRAW_FLIP_TO_BLIT"] = "1"

    #env["WINED3D_GLSL"] = "disabled"
    #env["WINED3D_FBO"] = "0"

    # Pas de FSR
    env.pop("WINE_FULLSCREEN_FSR", None)

    # Pas de tweak Mesa
    env.pop("vblank_mode", None)
    env.pop("DXVK_HUD", None)
    env.pop("WINED3D_GLSL", None)
    env.pop("WINED3D_FBO", None)

    return env
