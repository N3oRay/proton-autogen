from proton_autogen.profiles.base import init_env

# ---------------------------------------------------
# 3. DX12 PROFILE (VKD3D)
# ---------------------------------------------------
def env_dx12(prefix=None, proton_path=None):
    env = init_env()

    print("[proton-autogen] PROFILE: DX12 - VKD3D")

    env["PROTON_NO_ESYNC"] = "0"
    env["PROTON_NO_FSYNC"] = "0"

    # VKD3D tuning (safe default)
    env["VKD3D_CONFIG"] = "dxr"

    env["WINEDLLOVERRIDES"] = ""

    env["WINEESYNC"] = "1"
    env["WINEFSYNC"] = "1"

    # DO NOT enable RADV_PERFTEST by default (breaks some setups)
    # env["RADV_PERFTEST"] = "gpl"  # optional advanced users only

    env["vblank_mode"] = "0"
    env["mesa_glthread"] = "true"

    return env
