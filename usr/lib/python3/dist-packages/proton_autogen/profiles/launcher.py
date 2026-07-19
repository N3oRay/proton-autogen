from proton_autogen.profiles.base import init_env
# ---------------------------------------------------
# 1. LAUNCHER PROFILE (Battle.net, EA App, Ubisoft)
# ---------------------------------------------------
def env_launcher(prefix=None, proton_path=None, exe_path=None):
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


def env_install_clean(prefix=None, proton_path=None, exe_path=None):
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
