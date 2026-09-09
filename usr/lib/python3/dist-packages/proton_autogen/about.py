from proton_autogen.i18n import detect_help_env_lang
from proton_autogen.data_paths import get_docs_root


def get_about_text():
    root = get_docs_root()
    lang = detect_help_env_lang()

    candidates = [
        f"about_{lang}.txt",
        "about_en.txt"
    ]

    for file in candidates:
        path = root / file
        if path.exists():
            return path.read_text(encoding="utf-8")

    return "📄 Documentation not available."


def afficher_abouts():
    print(get_about_text())


def afficher_abouts_label():
    return get_about_text()
