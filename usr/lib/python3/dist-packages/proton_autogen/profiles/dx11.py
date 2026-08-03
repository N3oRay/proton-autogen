import os
from proton_autogen.profiles.base import init_env
from proton_autogen.utils.logger import StructuredLogger

#-------------------------- Init Log -------------------
logger = StructuredLogger("proton-autogen.profiles.dx11")

LEGACY_RENDERER_RULES = {

    "ref_gl.dll": {
        "profile": "quake_opengl",
        "mesa_year": "2002"
    },

    "ref_gl1.dll": {
        "profile": "quake_opengl",
        "mesa_year": "2002"
    },

    "pvrgl.dll": {
        "profile": "powervr",
        "mesa_year": "2001"
    },

    "pvrgl32.dll": {
        "profile": "powervr",
        "mesa_year": "2001"
    }
}


def detect_legacy_renderer(exe_path):
    legacy_renderers = [
        "ref_gl.dll",
        "ref_gl1.dll",
        "pvrgl.dll",
        "pvrgl32.dll",
        "opengl32.dll"
    ]

    directory = os.path.dirname(exe_path)

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower() in legacy_renderers:
                print(f"[proton-autogen] Legacy renderer found: {file}")
                return file.lower()

    return None
# ---------------------------------------------------
# 2. DX11 PROFILE (most games)
# ---------------------------------------------------
def env_dx11(prefix=None, proton_path=None, exe_path=None):
    env = init_env()

    logger.info("[proton-autogen] PROFILE: DX11")
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

    # -----------------------------------------
    # Legacy OpenGL detection
    # -----------------------------------------
    if exe_path :
        renderer = detect_legacy_renderer(exe_path)
        if renderer:
            logger.info(f"[proton-autogen] Applying OpenGL compatibility fix: {renderer}")

            rules = LEGACY_RENDERER_RULES.get(renderer)
            if rules:
                logger.info("Legacy mouse/input")
                env["SDL_MOUSE_RELATIVE_MODE"] = "1"
                env["WINE_MOUSE_WARP"] = "0"
                env["PROTON_OLD_GL_STRING"] = "1"
                env["MESA_EXTENSION_MAX_YEAR"] = rules["mesa_year"]

    return env

def env_dx11BNet(prefix=None, proton_path=None, exe_path=None):
    env = init_env()

    logger.info("[proton-autogen] PROFILE: DX11 Battle.net")

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
