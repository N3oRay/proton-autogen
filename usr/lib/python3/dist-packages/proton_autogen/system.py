import os
import subprocess

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
        # NVIDIA check
        if subprocess.run(
            ["which", "nvidia-smi"],
            capture_output=True
        ).returncode == 0:
            system["gpu"] = "nvidia"

        # AMD check fallback
        elif os.path.exists("/sys/class/drm/card0/device/vendor"):
            try:
                with open("/sys/class/drm/card0/device/vendor", "r") as f:
                    vendor = f.read().strip()

                # AMD vendor id = 0x1002
                if vendor == "0x1002":
                    system["gpu"] = "amd"
            except:
                pass

        # fallback Intel
        else:
            system["gpu"] = "intel"

    except Exception:
        system["gpu"] = "unknown"

    return system
