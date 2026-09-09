from proton_autogen.i18n import detect_help_env_lang
from proton_autogen.data_paths import get_docs_root


def get_about_proton_text():
    root = get_docs_root()
    lang = detect_help_env_lang()

    candidates = [
        f"about_proton_{lang}.txt",
        "about_proton_en.txt",
    ]

    for file in candidates:
        path = root / file

        if path.exists():
            return path.read_text(encoding="utf-8")

    return "📄 Documentation not available."


def afficher_about_protons():
    print(get_about_proton_text())


def afficher_about_protons_label():
    return get_about_proton_text()
