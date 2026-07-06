import os
import subprocess

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
    candidates = [
        "/usr/lib32/mangohud/libMangoHud_shim.so",
        "/usr/lib/i386-linux-gnu/mangohud/libMangoHud_shim.so",
        "/usr/local/lib/i386-linux-gnu/mangohud/libMangoHud_shim.so",
        "/usr/local/lib32/mangohud/libMangoHud_shim.so",
    ]

    for path in candidates:
        if os.path.exists(path):
            return path

    return None


def check_mangohud_abi(lib):
    out = subprocess.getoutput(f"ldd {lib}")
    return "libspdlog.so.1.15" not in out
