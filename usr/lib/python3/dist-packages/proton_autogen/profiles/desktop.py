
from proton_autogen.profiles.base import init_env
#-----------------------------------------------------------
# 7. PROFILE DESKTOP
#-----------------------------------------------------------

def env_desktop(prefix=None, proton_path=None, exe_path=None):
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



def env_win95(prefix=None, proton_path=None, exe_path=None):
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


def env_win95Beta(prefix=None, proton_path=None, exe_path=None):
    env = init_env()
    print("[proton-autogen] PROFILE: Win 95 Beta")

    env["PROTON_USE_XALIA"] = "0"
    env["PROTON_USE_WINED3D"] = "1"

    env["PROTON_NO_ESYNC"] = "1"
    env["PROTON_NO_FSYNC"] = "1"

    env["WINEESYNC"] = "0"
    env["WINEFSYNC"] = "0"

    return env


#-----------------------------------------------------------
# DirectDraw
#-----------------------------------------------------------

def env_DDraw(prefix=None, proton_path=None, exe_path=None):
    env = init_env()

    print("[proton-autogen] PROFILE: DirectDraw (BETA)")

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
