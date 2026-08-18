import os
import subprocess
from proton_autogen.utils.logger import StructuredLogger
#-------------------------- Init Log -------------------
logger = StructuredLogger("proton-autogen.mangohud")

MANGOHUD_OPENGL_EXE_TYPES = {
    "dx9",
    "dx9opengl",
    "oldgame",
    "ut99",
    "ut3",
    "valve",
}

MANGOHUD_VULKAN_EXE_TYPES = {
    "vulkan",
    "dxvk",
}


def find_mangohud_shim():
    """
    Search for the libMangoHud_shim.so library in the most common
    32-bit installation directories.

    The function iterates through a predefined list of candidate paths
    and returns the first existing library found.

    Returns:
        str | None:
            - The full path to libMangoHud_shim.so if found.
            - None if the library is not found in any of the checked locations.
    """
    """
    candidates = [
        "/usr/lib32/mangohud/libMangoHud_shim.so",
        "/usr/lib/i386-linux-gnu/mangohud/libMangoHud_shim.so",
        "/usr/local/lib/i386-linux-gnu/mangohud/libMangoHud_shim.so",
        "/usr/local/lib32/mangohud/libMangoHud_shim.so",
    ]
    """
    candidates = [
        # Arch Linux / CachyOS / EndeavourOS / Manjaro
        "/usr/lib32/mangohud/libMangoHud_shim.so",

        # Debian / Ubuntu / Linux Mint
        "/usr/lib/i386-linux-gnu/mangohud/libMangoHud_shim.so",

        # MangoHud official installer
        "/usr/lib/mangohud/i386-linux-gnu/libMangoHud_shim.so",

        # Installations locales
        "/usr/local/lib32/mangohud/libMangoHud_shim.so",
        "/usr/local/lib/i386-linux-gnu/mangohud/libMangoHud_shim.so",

        # Steam Runtime 32 bits (si fourni)
        os.path.expanduser(
            "~/.steam/root/ubuntu12_32/steam-runtime/usr/lib/mangohud/libMangoHud_shim.so"
        ),

        # Flatpak Runtime 32 bits (rare)
        "/var/lib/flatpak/runtime/org.freedesktop.Platform.VulkanLayer.MangoHud/current/active/files/lib/i386-linux-gnu/libMangoHud_shim.so",

        os.path.expanduser(
            "~/.local/share/flatpak/runtime/"
            "org.freedesktop.Platform.VulkanLayer.MangoHud/"
            "current/active/files/lib/i386-linux-gnu/libMangoHud_shim.so"
        ),
    ]

    for path in candidates:
        if os.path.exists(path):
            return path

    return None


def check_mangohud_abi(lib):
    out = subprocess.getoutput(f"ldd {lib}")
    return "libspdlog.so.1.15" not in out

def add_ld_preload(env, library):
    """
    Ajoute une bibliothèque à LD_PRELOAD sans écraser
    les bibliothèques déjà présentes.
    """
    if not os.path.exists(library):
        logger.warn(f"Missing library: {library}")
        return env

    current = env.get("LD_PRELOAD", "")

    if current:
        if library not in current.split(":"):
            env["LD_PRELOAD"] = f"{library}:{current}"
    else:
        env["LD_PRELOAD"] = library

    return env


def is_32bit_exe(arch):
    return arch == "32bit"




def configure_mangohud_env(env, exe_path, exe_type, mangohud_available, arch, fps_limit=60,):
    """Configure MangoHud environment variables for the current executable."""

    if not mangohud_available:
        env.pop("MANGOHUD", None)
        return env

    env["MANGOHUD"] = "1"
    env["MANGOHUD_DLSYM"] = "1"
    env["DXVK_HUD"] = "0"

    # FPS cap only if needed
    if "fps_limit" not in env.get("MANGOHUD_CONFIG", ""):
        env["MANGOHUD_CONFIG"] =  f"fps_limit={fps_limit}"

    is_32bit = is_32bit_exe(arch)

    # OpenGL only for legacy DX9 / old games
    if exe_type in MANGOHUD_OPENGL_EXE_TYPES:
        env["MANGOHUD_OPENGL"] = "1"
    else:
        env.pop("MANGOHUD_OPENGL", None)

    # 32-bit shim only when needed
    if is_32bit:
        logger.info("32-bit legacy game detected")

        mangohud_shim = find_mangohud_shim()

        if mangohud_shim and os.path.exists(mangohud_shim):
            if not check_mangohud_abi(mangohud_shim):
                logger.info("MangoHud ABI mismatch detected - skipping")
            else:
                env = add_ld_preload(env, mangohud_shim)
                logger.info("Loaded MangoHud 32-bit shim")
        else:
            logger.info(
                "No MangoHud 32-bit shim found, relying on Proton runtime"
            )

    # Vulkan explicit toggle
    if exe_type in MANGOHUD_VULKAN_EXE_TYPES:
        env["MANGOHUD"] = "1"


    return env
