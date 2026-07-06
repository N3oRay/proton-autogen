

from proton_autogen.profiles.base import init_env


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
