from proton_autogen.profiles.base import init_env


# ---------------------------------------------------
# .NET / Windows Application PROFILE
# ---------------------------------------------------
def env_dotnet():
    env = init_env()

    print("[proton-autogen] PROFILE: DOTNET")

    # Pas d'intégration Xalia
    env["PROTON_USE_XALIA"] = "0"

    # Applications .NET : privilégier la stabilité
    env["PROTON_NO_ESYNC"] = "1"
    env["PROTON_NO_FSYNC"] = "1"

    env["WINEESYNC"] = "0"
    env["WINEFSYNC"] = "0"

    # Ne pas forcer DXVK
    env["PROTON_USE_WINED3D"] = "1"

    # Nettoyage variables graphiques jeux
    env.pop("DXVK_HUD", None)
    env.pop("DXVK_ASYNC", None)
    env.pop("VKD3D_CONFIG", None)

    # Eviter les overrides automatiques
    env["WINEDLLOVERRIDES"] = ""

    # .NET aime un comportement Windows classique
    env["WINE_SIMULATE_WRITECOPY"] = "0"

    # Audio / multimédia plus compatible
    env["WINE_DISABLE_GSTREAMER"] = "0"

    # UI desktop
    env["WINEDLLOVERRIDES"] = (
        "mscoree=n;"
        "mshtml=n"
    )

    # Pas de tweaks Mesa
    env.pop("mesa_glthread", None)
    env.pop("vblank_mode", None)

    return env
