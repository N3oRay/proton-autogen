from proton_autogen.profiles.dotnet import env_dotnet
#Add .NET C# profile with RAGE:MP and FiveM detection - profile : csharp
import os
import sys

DEBUG = "--debug" in sys.argv

def detect_managed_launcher(exe_path=None):
    if DEBUG:
        print( f"[detect_managed_launcher] {exe_path} " )

    if not exe_path:
        return None

    exe = os.path.basename(exe_path).lower()

    if DEBUG:
        print( f"[detect_managed_launcher] {exe} " )

    #
    # Known launchers (reference)
    #
    # "ragemp.exe": "ragemp",
    # "ragemp_v.exe": "ragemp",

    # Dynamic detection is preferred because FiveM build numbers
    # change frequently.
    # "fivem.exe": "fivem",
    # "fivem_b2189.exe": "fivem",
    # "fivem_b2372.exe": "fivem",
    # "fivem_b2545.exe": "fivem",
    # "fivem_b2612.exe": "fivem",
    # "fivem_b2699.exe": "fivem",
    # "fivem_b2802.exe": "fivem",
    # "fivem_b2944.exe": "fivem",
    # "fivem_b3095.exe": "fivem",
    # "fivem_b3258.exe": "fivem",
    #

    if "ragemp" in exe or "ragemultiplayer" in exe:
        return "ragemp"

    if "fivem" in exe:
        return "fivem"

    if "playnite" in exe:
        return "playnite"

    if "voiceattack" in exe:
        return "voiceattack"

    return None

def env_dotnet_csharp( prefix=None, proton_path=None, exe_path=None, ):
    """
    .NET C# profile.

    Optimized for Windows applications written in C# /
    .NET Framework.

    Reuses the standard .NET profile and applies a few
    compatibility tweaks suitable for desktop applications
    and launchers.
    """

    env = env_dotnet(prefix=prefix, proton_path=proton_path, exe_path=exe_path, )

    print("[proton-autogen] PROFILE: .NET C#")

    #
    # Runtime and synchronization settings
    #
    # Optimized for .NET applications and game-related
    # launchers using Proton/Wine.
    #

    env.update({
        "WINEESYNC": "1",
        "WINEFSYNC": "1",
        "WINE_SIMULATE_WRITECOPY": "1",
    })

    env.pop("PROTON_NO_ESYNC", None)
    env.pop("PROTON_NO_FSYNC", None)
    env.pop("DXVK_HUD", "0")

    #
    # Remove variables that may have been injected for games.
    #

    for var in (
        "DXVK_HUD",
        "DXVK_ASYNC",
        "MANGOHUD",
        "VKD3D_CONFIG",
        "PROTON_USE_WINED3D",
    ):
        env.pop(var, None)

    #
    # Game launcher detection
    #
    # Applies additional compatibility settings for
    # managed game launchers such as RAGE:MP and FiveM.
    #
    if exe_path:
        launcher = detect_managed_launcher(exe_path)

        if launcher:
            print(
                f"[proton-autogen] {launcher.upper()} detected"
            )

            if launcher == "ragemp":
                env["LIBGL_ALWAYS_SOFTWARE"] = "1"
                #env["GALLIUM_DRIVER"] = "llvmpipe"
                env["WINEDLLOVERRIDES"] = (
                    "mscoree=b;"
                    "winhttp=n,b;"
                    "d3dcompiler_47=n,b"
                )
                #env["CEF_LOG_FILE"] = "/tmp/ragemp-cef.log"
                #env["CEF_LOG_SEVERITY"] = "info"
                #env["CEF_DISABLE_GPU"] = "1"
                #env["CHROME_FLAGS"] = "--disable-gpu --disable-gpu-compositing --disable-software-rasterizer"
                #env["CHROME_FLAGS"] = "--disable-gpu --disable-gpu-compositing"
                env["CHROME_FLAGS"] = "--disable-gpu"

                #env["ANGLE_DEFAULT_PLATFORM"] = "swiftshader"
                #env["CHROME_FLAGS"] = "--use-angle=swiftshader"
            elif launcher == "fivem":
                env["WINEDLLOVERRIDES"] = (
                    "mscoree=b;"
                    "winhttp=n,b;"
                    "d3dcompiler_47=n,b"
                )

            elif launcher == "playnite":
                env["WINEDLLOVERRIDES"] = (
                    "mscoree=b;"
                    "winhttp=n,b;"
                    "d3dcompiler_47=n,b"
                )

                env["WINE_SIMULATE_WRITECOPY"] = "1"

                env["PROTON_USE_WINED3D"] = "1"

                # Désactive les problèmes de rendu WPF/D3D
                env["LIBGL_ALWAYS_SOFTWARE"] = "1"
            elif launcher == "voiceattack" :
                env["WINEDLLOVERRIDES"] = (
                    "mscoree=b;"
                    "winhttp=n,b;"
                    "d3dcompiler_47=n,b"
                )

                env["WINE_SIMULATE_WRITECOPY"] = "1"
            else:
                env["WINEDLLOVERRIDES"] = env.get(
                    "WINEDLLOVERRIDES",
                    "mscoree=b"
                )




    return env
