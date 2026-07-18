from proton_autogen.profiles.base import init_env

def env_dx9(prefix=None, proton_path=None):
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

def env_dx9dg(prefix=None, proton_path=None):
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

def env_dx9opengl(prefix=None, proton_path=None):
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
