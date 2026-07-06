from proton_autogen.profiles.base import init_env

#-----------------------------------------------------------
# Valve - Sierra - Old Game (Hal-Life) env_goldsrc_full env_gold_test env_goldsrc
#-----------------------------------------------------------
def env_goldsrc():
    env = init_env()

    print("[proton-autogen] GOLDSRC STEAM-LIKE PROFILE")

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
    env["WINEDLLOVERRIDES"] = "mss32=builtin"

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
    env["MESA_GL_VERSION_OVERRIDE"] = "3.3"
    env["MESA_GLSL_VERSION_OVERRIDE"] = "330"

    # =========================
    # ⚙️ SYNC (STABILITY MODE)
    # =========================
    env["PROTON_NO_ESYNC"] = "1"
    env["PROTON_NO_FSYNC"] = "1"
    env["WINEESYNC"] = "0"
    env["WINEFSYNC"] = "0"

    # =========================
    # 🧪 DEBUG SAFE MODE
    # =========================
    #env["WINEDEBUG"] = "-all"
    #env["WINEDEBUG"] = "+loaddll,+module"

    return env


def env_gold_test():
    env = init_env()

    print("[proton-autogen] SAFE GOLDSRC PROFILE")

    # --- CRITICAL ---
    env["PROTON_USE_XALIA"] = "0"
    env["WINEDLLOVERRIDES"] = "mss32=builtin"

    # INPUT minimal
    env["SDL_MOUSE_RELATIVE_MODE_WARP"] = "1"
    env["SDL_MOUSE_AUTO_CAPTURE"] = "1"

    # compositing safe
    env["SDL_VIDEO_X11_NET_WM_BYPASS_COMPOSITOR"] = "0"

    return env

def env_goldsrc_full():
    env = init_env()

    print("[proton-autogen] PROFILE: GOLDSRC (Half-Life)")

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

    return env

# ---------------------------------------------------
# PROFILE (UnrealTournament) AND QUAKE
# ---------------------------------------------------

def env_ut99():
    env = init_env()

    print("[proton-autogen] PROFILE: UNREAL TOURNAMENT (UT99)")
    print("[proton-autogen] Note: UT99 is more stable in windowed mode")

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

    return env
