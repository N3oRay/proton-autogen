import os
from proton_autogen.profiles.base import init_env

LEGACY_RENDERER_RULES = {

    "ref_gl.dll": {
        "profile": "quake_opengl",
        "mesa_year": "2002",
        "mouse_fix": True
    },

    "ref_gl1.dll": {
        "profile": "quake_opengl",
        "mesa_year": "2002",
        "mouse_fix": True
    },

    "pvrgl.dll": {
        "profile": "powervr",
        "mesa_year": "2001",
        "mouse_fix": True
    },

    "pvrgl32.dll": {
        "profile": "powervr",
        "mesa_year": "2001",
        "mouse_fix": True
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

def env_dx9(prefix=None, proton_path=None, exe_path=None):
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

    # -----------------------------------------
    # Legacy OpenGL detection
    # -----------------------------------------
    if exe_path :
        renderer = detect_legacy_renderer(exe_path)
        if renderer:
            print(f"[proton-autogen] Applying OpenGL compatibility fix: {renderer}")

            rules = LEGACY_RENDERER_RULES.get(renderer)
            if rules:
                env["PROTON_OLD_GL_STRING"] = "1"
                env["MESA_EXTENSION_MAX_YEAR"] = rules["mesa_year"]


    return env

def env_dx9dg(prefix=None, proton_path=None, exe_path=None):
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

    # -----------------------------------------
    # Legacy OpenGL detection
    # -----------------------------------------
    if exe_path :
        renderer = detect_legacy_renderer(exe_path)
        if renderer:
            print(f"[proton-autogen] Applying OpenGL compatibility fix: {renderer}")

            rules = LEGACY_RENDERER_RULES.get(renderer)
            if rules:
                env["PROTON_OLD_GL_STRING"] = "1"
                env["MESA_EXTENSION_MAX_YEAR"] = rules["mesa_year"]

    return env

def env_dx9opengl(prefix=None, proton_path=None, exe_path=None):
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

    # -----------------------------------------
    # Legacy OpenGL detection
    # -----------------------------------------
    if exe_path :
        renderer = detect_legacy_renderer(exe_path)
        if renderer:
            print(f"[proton-autogen] Applying OpenGL compatibility fix: {renderer}")

            rules = LEGACY_RENDERER_RULES.get(renderer)
            if rules:
                if rules.get("mouse_fix"):
                    env["PROTON_USE_XALIA"] = "0"
                    env["SDL_MOUSE_RELATIVE_MODE"] = "1"
                    env["SDL_VIDEO_X11_MOUSE_GRAB"] = "1"

                    env["WINE_FULLSCREEN_MOUSE_CAPTURE"] = "1"
                    env["SDL_VIDEO_X11_NET_WM_BYPASS_COMPOSITOR"] = "1"

                env["WINE_FULLSCREEN_WINDOW"] = "1"
                env["SDL_VIDEO_X11_NET_WM_BYPASS_COMPOSITOR"] = "1"
                env["SDL_VIDEO_X11_XRANDR"] = "1"
                # Legacy mouse/input

                env["WINE_MOUSE_WARP"] = "0"
                #env["WINE_DISABLE_MOUSE_CAPTURE"] = "0"

                env["WINE_FULLSCREEN_FSR"] = "0"
                env["WINE_FULLSCREEN_INTEGER_SCALING"] = "0"

                env["WINEDLLOVERRIDES"] = "dinput=n,b;dinput8=n,b"
                env["PROTON_OLD_GL_STRING"] = "1"
                env["MESA_EXTENSION_MAX_YEAR"] = rules["mesa_year"]


    return env
