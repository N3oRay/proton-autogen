
import locale

from functools import lru_cache
from pathlib import Path

from proton_autogen.data_paths import get_docs_root


DEFAULT_LANGUAGE = "en"
TRANSLATION_PREFIX = "cachy_"
TRANSLATION_EXTENSION = ".txt"


def detect_language() -> str:
    """Detect the system language."""
    try:
        lang, _ = locale.getlocale()
    except (ValueError, TypeError):
        lang = None

    if not lang:
        return DEFAULT_LANGUAGE

    # Normalize language identifiers:
    # fr_FR -> fr, pt-BR -> pt, zh_CN -> zh
    return lang.replace("-", "_").split("_")[0].lower()


@lru_cache(maxsize=1)
def get_available_languages() -> set[str]:
    """Discover all available translations automatically."""
    root = Path(get_docs_root())

    return {
        path.stem.removeprefix(TRANSLATION_PREFIX)
        for path in root.glob(f"{TRANSLATION_PREFIX}*{TRANSLATION_EXTENSION}")
    }


def get_cachy_text() -> str:
    """Load the best available translation."""
    root = Path(get_docs_root())

    language = detect_language()
    available = get_available_languages()

    # Try detected language, then English
    candidates = [language, DEFAULT_LANGUAGE]

    for lang in candidates:
        if lang in available:
            path = root / f"{TRANSLATION_PREFIX}{lang}{TRANSLATION_EXTENSION}"
            return path.read_text(encoding="utf-8")

    return "📄 Documentation not available."


def afficher_cachy():
    print(get_cachy_text())


def afficher_cachy_label():
    return get_cachy_text()
