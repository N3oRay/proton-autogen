from pathlib import Path
import locale
import os


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

DEV_DOCS = Path(__file__).parent / "docs"
SYS_DOCS = Path("/usr/share/proton-autogen/docs")


def get_docs_root():
    if DEV_DOCS.exists():
        return DEV_DOCS
    return SYS_DOCS


def get_cachy_text():
    root = get_docs_root()
    lang = detect_language()

    candidates = [
        f"cachy_{lang}.txt",
        "cachy_en.txt"
    ]

    for file in candidates:
        path = root / file
        if path.exists():
            return path.read_text(encoding="utf-8")

    return "📄 Documentation not available."


def afficher_cachy():
    print(get_cachy_text())


def afficher_cachy_label():
    return get_cachy_text()
