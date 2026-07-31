import os
from proton_autogen.profiles.base import init_env
from proton_autogen.utils.logger import StructuredLogger
#-------------------------- Init Log -------------------
logger = StructuredLogger("proton-autogen.profiles.engines")
# -----------------------------------------------------------
# GoldSrc / Valve Legacy Renderer Rules
# -----------------------------------------------------------

GOLDSRC_RENDERER_RULES = {

    "hw.dll": {
        "profile": "goldsrc_opengl",
        "mesa_year": 2000,
        "mouse_fix": True
    }
}


def detect_goldsrc_renderer(exe_path):

    legacy_renderers = ["hw.dll"]

    directory = os.path.dirname(exe_path)

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower() in legacy_renderers:
                logger.info(
                    f"[proton-autogen] GoldSrc renderer found: {file}"
                )
                return file.lower()

    return None

def apply_goldsrc_legacy_fixes(env, exe_path):

    if not exe_path:
        return

    renderer = detect_goldsrc_renderer(exe_path)

    if renderer:

        logger.info(
            f"[proton-autogen] Applying GoldSrc OpenGL fix: {renderer}"
        )

        rules = GOLDSRC_RENDERER_RULES.get(renderer)

        if rules:

            env["PROTON_OLD_GL_STRING"] = "1"
            env["MESA_EXTENSION_MAX_YEAR"] = str(
                rules["mesa_year"]
            )

#-----------------------------------------------------------
# Valve - Sierra - Old Game (Hal-Life) env_goldsrc_full env_gold_test env_goldsrc
#----------------------------------------------------------- env_goldsrc
def env_goldsrc(prefix=None, proton_path=None, exe_path=None):
    env = init_env()

    logger.info("[proton-autogen] GOLDSRC STEAM-LIKE PROFILE")

    # =========================
    # 🎮 RENDERING
    # =========================
    # GoldSrc stable = OpenGL via WineD3D
    env["PROTON_USE_WINED3D"] = "1"
    env["DXVK_HUD"] = "0"
    env["VKD3D_CONFIG"] = ""

    # =========================
    # 🧠 SOUND (Miles Audio)
    # =========================
    # IMPORTANT: évite crash audio GoldSrc
    #env["WINEDLLOVERRIDES"] = "mss32=builtin"
    #env["WINEDLLOVERRIDES"] = "mss32=native,builtin"
    #env["WINEDLLOVERRIDES"] = "mss32=builtin"

    # =========================
    # 🖱️ INPUT (GoldSrc safe mode)
    # =========================
    # désactive Xalia proprement
    env["PROTON_USE_XALIA"] = "0"
    env["XALIA"] = "0"

    # SDL overrides forcés en mode neutre (évite input cassé)
    env["SDL_MOUSE_AUTO_CAPTURE"] = "0"
    env["SDL_MOUSE_RELATIVE_MODE_WARP"] = "0"
    env["SDL_HINT_GRAB_KEYBOARD"] = "0"

    # comportement fenêtre stable
    env["SDL_VIDEO_MINIMIZE_ON_FOCUS_LOSS"] = "0"

    env["SDL_VIDEO_X11_NET_WM_BYPASS_COMPOSITOR"] = "0"
    #env["MESA_GL_VERSION_OVERRIDE"] = "3.3"
    #env["MESA_GLSL_VERSION_OVERRIDE"] = "330"

    # =========================
    # ⚙️ SYNC (STABILITY MODE)
    # =========================
    env["PROTON_NO_ESYNC"] = "1"
    env["PROTON_NO_FSYNC"] = "1"
    env["WINEESYNC"] = "0"
    env["WINEFSYNC"] = "0"

    # =========================
    # Legacy OpenGL detection
    # =========================

    apply_goldsrc_legacy_fixes(env, exe_path)


    return env

def env_goldsrc_full(prefix=None, proton_path=None, exe_path=None):
    env = init_env()

    logger.info("[proton-autogen] PROFILE: GOLDSRC (Half-Life)")

    # OpenGL natif propre
    env.pop("PROTON_USE_WINED3D", None)

    #env["WINEDLLOVERRIDES"] = "mss32=n,b"

    # --- CRITICAL ---
    env["PROTON_USE_XALIA"] = "0"
    #env.pop("XALIA", None)

    # --- GOLD SRC FIX ---
    env["WINEDLLOVERRIDES"] = "mss32=native,builtin"

    # sync stable
    env.pop("PROTON_NO_ESYNC", None)
    env.pop("PROTON_NO_FSYNC", None)
    env.pop("WINEESYNC", None)
    env.pop("WINEFSYNC", None)

    # éviter interférences Vulkan/DXVK
    env.pop("DXVK_HUD", None)
    env.pop("VKD3D_CONFIG", None)

    # SDL input fixes (important pour GoldSrc)
    env["SDL_MOUSE_RELATIVE_MODE_WARP"] = "1"
    env["SDL_MOUSE_AUTO_CAPTURE"] = "1"
    env["SDL_HINT_GRAB_KEYBOARD"] = "1"
    env["SDL_VIDEO_X11_NET_WM_BYPASS_COMPOSITOR"] = "0"

    # IMPORTANT: évite double capture
    env["SDL_VIDEO_MINIMIZE_ON_FOCUS_LOSS"] = "0"

    # =========================
    # Legacy OpenGL detection
    # =========================

    apply_goldsrc_legacy_fixes(env, exe_path)

    return env

# ---------------------------------------------------
# PROFILE (UnrealTournament) AND QUAKE
# ---------------------------------------------------

def env_ut99(prefix=None, proton_path=None, exe_path=None):
    env = init_env()

    logger.info("[proton-autogen] PROFILE: UNREAL TOURNAMENT (UT99)")
    logger.info("[proton-autogen] Note: UT99 is more stable in windowed mode")

    env["PROTON_NO_ESYNC"] = "1"
    env["PROTON_NO_FSYNC"] = "1"
    env["PROTON_USE_WINED3D"] = "1"
    env["WINEDLLOVERRIDES"] = "d3d8=n,b"

    # sécurité : éviter toute interférence DXVK / async layers
    env.pop("DXVK_HUD", None)
    env["WINEESYNC"] = "0"
    env["WINEFSYNC"] = "0"

    env["vblank_mode"] = "0"
    env["mesa_glthread"] = "true"

    # =========================
    # Legacy OpenGL detection
    # =========================

    apply_goldsrc_legacy_fixes(env, exe_path)

    return env
