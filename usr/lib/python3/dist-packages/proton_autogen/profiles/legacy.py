import os
from proton_autogen.profiles.base import init_env
# ---------------------------------------------------
# BASE CLEANER (shared)
# ---------------------------------------------------
# ---------------------------------------------------
# 0. LAUNCHER PROFILE (legacy Photoshop 6)
# ---------------------------------------------------
def env_legacy_app(prefix=None, proton_path=None):
    env = init_env()

    print("[proton-autogen] PROFILE: LEGACY APPLICATION")
    env["PROTON_USE_XALIA"] = "0"

    env["PROTON_NO_ESYNC"] = "1"
    env["PROTON_NO_FSYNC"] = "1"

    env["WINEESYNC"] = "0"
    env["WINEFSYNC"] = "0"

    env.pop("DXVK_HUD", None)

    env["vblank_mode"] = "0"
    env["mesa_glthread"] = "true"

    return env


# ---------------------------------------------------
# 4. OLD GAME PROFILE (DX8 / DX9 / WineD3D)
# ---------------------------------------------------
def env_oldgame(prefix=None, proton_path=None):
    env = init_env()

    print("[proton-autogen] PROFILE: OLD GAME (DX8/DX9)")

    env["PROTON_USE_WINED3D"] = "1"

    env["WINEDLLOVERRIDES"] = "d3d8=n,b"

    env["PROTON_NO_ESYNC"] = "1"
    env["PROTON_NO_FSYNC"] = "1"

    env["WINEESYNC"] = "0"
    env["WINEFSYNC"] = "0"

    # disable DXVK completely behaviorally (WineD3D takes over)
    env.pop("DXVK_HUD", None)

    env["vblank_mode"] = "0"
    env["mesa_glthread"] = "true"

    return env


def env_quake(prefix=None, proton_path=None):
    env = init_env()

    print("[proton-autogen] PROFILE: QUAKE II CLEAN")
    #print("[proton-autogen] RECOMMANDATION: Pour une expérience stable, utiliser Yamagi Quake II")
    print("\033[93m[proton-autogen] RECOMMANDATION: Yamagi Quake II est recommandé pour stabilité\033[0m")
    print("[proton-autogen] https://www.yamagi.org/quake2/")

    # désactiver Xalia
    env["PROTON_USE_XALIA"] = "0"

    # forcer WineD3D (old OpenGL path)
    env["PROTON_USE_WINED3D"] = "1"


    # prefix propre
    env["WINEPREFIX"] = os.path.expanduser("~/quake2-test")

    # sync stable (laisser Proton gérer)
    env.pop("PROTON_NO_ESYNC", None)
    env.pop("PROTON_NO_FSYNC", None)
    env.pop("WINEESYNC", None)
    env.pop("WINEFSYNC", None)

    # pas d’overrides cassants
    env.pop("WINEDLLOVERRIDES", None)

    return env

#-----------------------------------------------------------
# 6. PROFILE (UT3)
#-----------------------------------------------------------

def env_ut3(prefix=None, proton_path=None):
    env = init_env()

    print("[proton-autogen] PROFILE: UT3 FIXED (BETA)")

    env["PROTON_NO_FSYNC"] = "1"
    env["PROTON_NO_ESYNC"] = "0"

    # IMPORTANT UE3 stability AMD Polaris
    env["WINEESYNC"] = "1"
    env["WINEFSYNC"] = "0"

    # DXVK must stay clean
    env.pop("PROTON_USE_WINED3D", None)
    env.pop("WINEDLLOVERRIDES", None)

    # DEBUG ONLY (désactivé par défaut)
    env.pop("DXVK_HUD", None)

    # UE3 stability tweak
    env["DXVK_CONFIG"] = "dxgi.customSwapchain=false"

    env["vblank_mode"] = "0"
    env["mesa_glthread"] = "true"

    return env
