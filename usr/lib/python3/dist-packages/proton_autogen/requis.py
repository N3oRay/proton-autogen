from pathlib import Path
import locale
import os
import subprocess
from proton_autogen.cachyos import get_cachy_text


def has_nvidia_gpu():
    try:
        output = subprocess.check_output(
            ["lspci"],
            text=True
        ).lower()

        return "nvidia" in output

    except Exception:
        return False

def get_display_server():
    session_type = os.environ.get("XDG_SESSION_TYPE", "").lower()

    if session_type == "wayland":
        return "wayland"
    if session_type == "x11":
        return "x11"

    return "unknown"

def is_steam_deck():
    try:
        with open("/etc/os-release", encoding="utf-8") as f:
            data = f.read().lower()
        return "steamos" in data or "steamdeck" in data
    except FileNotFoundError:
        return False


def detect_gaming_environment():
    env = {
        "steam_deck": is_steam_deck(),
        "display_server": get_display_server(),
        "nvidia": has_nvidia_gpu()
    }

    return env


"""
env = detect_gaming_environment()

if env["steam_deck"]:
    print("Steam Deck detected → enabling handheld optimizations")

if env["display_server"] == "wayland":
    print("Wayland session → adjust MangoHud / overlays")

if env["nvidia"]:
    print("NVIDIA GPU detected → enable compatibility hints")
"""

def detect_language():
    lang = locale.getlocale()[0]

    if not lang:
        return "en"

    lang = lang.lower()

    if lang.startswith("fr"):
        return "fr"
    if lang.startswith("de"):
        return "de"
    if lang.startswith("es"):
        return "es"
    if lang.startswith("zh"):
        return "zh"
    if lang.startswith("uk"):
        return "uk"
    if lang.startswith("pt"):
        return "pt"

    return "en"


def detect_distro():
    try:
        with open("/etc/os-release", encoding="utf-8") as f:
            data = f.read().lower()

        if any(x in data for x in ("arch", "cachyos", "endeavouros")):
            return "arch"

        if any(x in data for x in ("ubuntu", "linuxmint", "mint", "pop")):
            return "ubuntu"

    except FileNotFoundError:
        pass

    return "ubuntu"


DEV_DOCS = Path(__file__).parent / "docs"
SYS_DOCS = Path("/usr/share/proton-autogen/docs")

"""
def get_docs_root():
    if DEV_DOCS.exists():
        return DEV_DOCS
    return SYS_DOCS
"""

def get_docs_root():

    candidates = [
        DEV_DOCS,
        SYS_DOCS,
    ]

    for path in candidates:
        if path.exists():
            return path

    return SYS_DOCS

def is_cachyos():
    try:
        with open("/etc/os-release", encoding="utf-8") as f:
            data = f.read().lower()

        return "cachyos" in data

    except FileNotFoundError:
        return False

def get_requirements_text():

    root = get_docs_root()

    lang = detect_language()
    distro = detect_distro()

    texts = []

    # Distribution
    for filename in (
        f"{distro}_{lang}.txt",
        f"{distro}_en.txt"
    ):
        path = root / filename

        if path.exists():
            texts.append(
                path.read_text(encoding="utf-8")
            )
            break


    # CachyOS
    if is_cachyos():
        cachy = get_cachy_text()

        if cachy:
            texts.append(cachy)


    return "\n\n".join(texts) if texts else (
        "📄 Documentation not available."
    )


def get_prerequisites_text():
    root = get_docs_root()

    lang = detect_language()
    distro = detect_distro()

    file_path = root / f"{distro}_{lang}.txt"

    if file_path.exists():
        return file_path.read_text(encoding="utf-8")

    fallback = root / f"{distro}_en.txt"
    if fallback.exists():
        return fallback.read_text(encoding="utf-8")

    return "Documentation not available."


def afficher_requirements():
    print(get_requirements_text())


def afficher_requirements_label():
    return get_requirements_text()
