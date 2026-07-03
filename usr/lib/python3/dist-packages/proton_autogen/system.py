import os
import subprocess

from pathlib import Path

def detect_gpu():
    vendors = set()

    drm = Path("/sys/class/drm")

    if not drm.exists():
        return "unknown"

    for card in drm.glob("card[0-9]*"):
        vendor = card / "device/vendor"

        if vendor.exists():
            try:
                vendors.add(vendor.read_text().strip())
            except OSError:
                pass

    # priorité au GPU le plus performant
    if "0x10de" in vendors:
        return "nvidia"

    if "0x1002" in vendors:
        return "amd"

    if "0x8086" in vendors:
        return "intel"

    return "unknown"

def detect_system_info():
    system = {
        "gpu": "unknown",
        "wayland": False,
        "steam_deck": False,
        "desktop": os.environ.get("XDG_CURRENT_DESKTOP", "").lower(),
    }

    # -------------------------
    # Wayland detection
    # -------------------------
    system["wayland"] = (
        os.environ.get("XDG_SESSION_TYPE", "").lower() == "wayland"
        or "wayland" in os.environ.get("WAYLAND_DISPLAY", "").lower()
    )

    # -------------------------
    # Steam Deck detection
    # -------------------------
    # simple heuristics (robuste enough)
    if (
        "steamdeck" in system["desktop"]
        or os.path.exists("/usr/bin/steamdeck")
        or os.path.exists("/etc/steam_deck")
    ):
        system["steam_deck"] = True

    # -------------------------
    # GPU detection (simple + practical)
    # -------------------------
    try:
        system["gpu"] = detect_gpu()

    except Exception:
        system["gpu"] = "unknown"

    return system
