#diag.py
import os
import sys
import re
import platform

from proton_autogen.core import has_wine, has_gamemode, has_mangohud, has_proton_call, VERSION, load_proton_paths



# ----------------------------
# PROTON SCORE (robuste)
# ----------------------------
def proton_score(name: str):
    name = name.lower()

    priority = 0
    if "cachy" in name:
        priority = 4
    elif "ge" in name:
        priority = 3
    elif "experimental" in name:
        priority = 2
    elif "proton" in name:
        priority = 1

    numbers = list(map(int, re.findall(r"\d+", name)))
    major = numbers[0] if len(numbers) > 0 else 0
    minor = numbers[1] if len(numbers) > 1 else 0

    return (priority, major, minor, name)


# ----------------------------
# SYSTEM PROTON DETECTION (FIXED)
# ----------------------------
# Known system-wide Proton locations.
# We intentionally avoid recursive scans of /usr/share
# and /usr/lib for performance and predictability.
def find_system_proton():
    locations = [
        "/usr/share/steam/compatibilitytools.d",
        "/usr/local/share/steam/compatibilitytools.d",
        "/usr/lib/steam/compatibilitytools.d",
    ]

    candidates = []

    def is_proton_name(name: str) -> bool:
        n = name.lower()

        return (
            "proton" in n
            or "ge-proton" in n
            or "proton-ge" in n
            or "experimental" in n
            or "hotfix" in n
            or "cachy" in n
        )

    for base in locations:

        if not os.path.isdir(base):
            continue

        try:
            for d in os.listdir(base):
                full = os.path.join(base, d)

                if (
                    os.path.isdir(full)
                    and is_proton_name(d)
                ):
                    candidates.append(full)

        except (PermissionError, FileNotFoundError):
            continue

    if not candidates:
        return None

    candidates.sort(
        key=lambda p: proton_score(
            os.path.basename(p)
        ),
        reverse=True
    )

    return os.path.realpath(candidates[0])

# ----------------------------
# MAIN FIXED FIND PROTON
# ----------------------------
def find_proton():
    candidates = []
    seen = set()

    def is_proton_dir(name: str) -> bool:
        return re.search(r"proton", name, re.IGNORECASE) is not None

    def add(path):
        if not path:
            return
        path = os.path.expanduser(path)
        path = os.path.realpath(path)

        if not os.path.exists(path):
            return

        if path in seen:
            return

        seen.add(path)

        candidates.append({
            "name": os.path.basename(path),
            "path": path
        })

    # scan steam + system
    for base in load_proton_paths():
        base = os.path.expanduser(base)

        if not os.path.exists(base):
            continue

        try:
            for d in os.listdir(base):
                full = os.path.join(base, d)

                if os.path.isdir(full) and is_proton_dir(d):
                    add(full)

        except (PermissionError, FileNotFoundError):
            continue

    # system proton explicit
    p_system_proton = find_system_proton()
    if p_system_proton:
        add(p_system_proton)

    if not candidates:
        return None

    candidates.sort(key=lambda c: proton_score(c["name"]), reverse=True)

    return candidates[0]


def find_all_protons():
    protons = []
    seen = set()

    def is_proton(name: str) -> bool:
        n = name.lower()

        # vrais candidats Proton
        return (
            "proton" in n
            or "ge-proton" in n
            or n.startswith("ge-proton")
            or "proton-ge" in n
            or "cachy" in n
            or "experimental" in n
            or "hotfix" in n
        )

    def normalize(name: str) -> str:
        return re.sub(r"[^a-z0-9]", "", name.lower())

    for base in load_proton_paths():
        base = os.path.expanduser(base)

        if not os.path.isdir(base):
            continue

        try:
            for d in os.listdir(base):
                full = os.path.join(base, d)

                if not os.path.isdir(full):
                    continue

                if not is_proton(d):
                    continue

                key = normalize(d)

                if key in seen:
                    continue

                seen.add(key)
                protons.append(full)

        except (PermissionError, FileNotFoundError):
            continue

    return protons



def get_distro():
    try:
        with open("/etc/os-release") as f:
            data = f.read().lower()

        if "linuxmint" in data:
            return "linuxmint"
        if "cachyos" in data:
            return "cachyos"
        if "arch" in data:
            return "arch"
        if "debian" in data:
            return "debian"
        if "ubuntu" in data:
            return "ubuntu"
    except:
        pass

    return platform.system().lower()


def _yesno(value: bool) -> str:
    return "yes" if value else "no"


def print_diagnostic():
    print("proton-autogen diagnostic\n")

    print(f"Version      : {VERSION}")
    print(f"Python       : {sys.version.split()[0]}\n")

    runtime_checks = {
        "proton-call": has_proton_call(),
        "wine       ": has_wine(),
        "gamemode   ": has_gamemode(),
        "mangohud   ": has_mangohud(),
    }

    print("Runtime:")
    for name, ok in runtime_checks.items():
        print(f"  {name} : {_yesno(ok)}")

    print(f"\nPlatform     : {sys.platform}\n")

    protons = find_all_protons()
    print(f"Detected Proton installations: {len(protons)}\n")

    if not protons:
        print("  none\n")
        print_install_hints()
        return

    selected = find_proton()

    selected_path = None
    if isinstance(selected, dict):
        selected_path = selected.get("path")
    elif isinstance(selected, str):
        selected_path = selected

    selected_path = os.path.realpath(selected_path) if selected_path else None

    protons_sorted = sorted(
        protons,
        key=lambda x: os.path.basename(x).lower()
    )

    for proton in protons_sorted:
        proton_real = os.path.realpath(proton)

        marker = " [selected]" if selected_path and proton_real == selected_path else ""

        print(f"  {os.path.basename(proton)}{marker}")
        print(f"    {proton}")

    print("")
    print_install_hints()

def print_install_hints():
    print("== Installation suggestions ==\n")

    distro = get_distro()

    missing = [
        ("proton-call", has_proton_call()),
        ("wine64", has_wine()),
        ("gamemode", has_gamemode()),
        ("mangohud", has_mangohud()),
    ]

    missing_list = [name for name, ok in missing if not ok]

    if missing_list:
        print("Missing components detected:\n")

        for m in missing_list:
            print(f"  - {m}")

        print("\nDetected system:", distro)

        # -----------------------------
        # Debian / Ubuntu / Linux Mint
        # -----------------------------
        if distro in ["debian", "ubuntu", "linuxmint"]:
            print("\nRecommended install commands (APT-based):\n")
            print("sudo apt update")
            print("sudo apt install wine64 gamemode mangohud\n")

        # -----------------------------
        # Arch / CachyOS
        # -----------------------------
        elif distro in ["arch", "cachyos"]:
            print("\nRecommended install commands (Pacman-based):\n")
            print("sudo pacman -S wine gamemode mangohud\n")

        # -----------------------------
        # fallback
        # -----------------------------
        else:
            print("\nGeneric Linux install commands:\n")
            print("wine / gamemode / mangohud must be installed via your package manager\n")

        # -----------------------------
        # Flatpak (universal)
        # -----------------------------
        print("Optional (recommended for Proton management):\n")
        print("  Flatpak ProtonUp-Qt:")
        print("    flatpak install flathub net.davidotek.pupgui2\n")

        # -----------------------------
        # Steam
        # -----------------------------
        if distro in ["debian", "ubuntu", "linuxmint"]:
            print("Or Steam-based Proton management:")
            print("  sudo apt install steam\n")
        elif distro in ["arch", "cachyos"]:
            print("Or Steam-based Proton management:")
            print("  sudo pacman -S steam\n")
        else:
            print("Install Steam from your package manager or Flatpak\n")

    else:
        print("All optional runtime components are installed.\n")

    print("Recommended setup order:")

    steps = [
        "Install Steam",
        "Install Proton via Steam or ProtonUp-Qt",
        "Install gamemode + mangohud for performance overlay",
        "Restart session (important for gamemode)",
    ]

    for i, step in enumerate(steps, 1):
        print(f"  {i}. {step}")

    print("")
