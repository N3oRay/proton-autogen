from proton_autogen.profiles.base import init_env

# ---------------------------------------------------
# 2. DX11 PROFILE (most games)
# ---------------------------------------------------
def env_dx11(prefix=None, proton_path=None):
    env = init_env()

    print("[proton-autogen] PROFILE: DX11")
    env["PROTON_USE_XALIA"] = "0"

    env["PROTON_NO_ESYNC"] = "0"
    env["PROTON_NO_FSYNC"] = "0"

    env["WINEDLLOVERRIDES"] = ""

    env["WINEESYNC"] = "1"
    env["WINEFSYNC"] = "1"

    # Safe modern Vulkan behavior
    env["WINE_SIMULATE_WRITECOPY"] = "1"

    env.pop("DXVK_HUD", None)

    env["vblank_mode"] = "0"
    env["mesa_glthread"] = "true"

    return env

def env_dx11BNet(prefix=None, proton_path=None):
    env = init_env()

    print("[proton-autogen] PROFILE: DX11 Battle.net")

    env["PROTON_USE_XALIA"] = "0"

    # DXVK / Vulkan stability
    env["DXVK_CONFIG"] = "dxgi.syncInterval=1"
    env["RADV_PERFTEST"] = "gpl,nggc"

    # Shader stability (important HOTS)
    env["DXVK_ASYNC"] = "1"

    env.pop("DXVK_HUD", None)

    # Clean Proton-managed sync (IMPORTANT)
    env.pop("PROTON_NO_ESYNC", None)
    env.pop("PROTON_NO_FSYNC", None)
    env.pop("WINEESYNC", None)
    env.pop("WINEFSYNC", None)

    env.pop("WINEDLLOVERRIDES", None)

    # silence multimedia stack
    env["GST_PLUGIN_PATH"] = ""
    env["GST_DEBUG"] = "0"
    env["WINE_DISABLE_GSTREAMER"] = "1"

    env["vblank_mode"] = "0"
    env["mesa_glthread"] = "true"

    return env
