# desc.py : info-bulles / UX descriptions

import os
import json

from gi.repository import Gtk

# ------------------------------------------------------------------------------------
# DESCRIPTIONS : chargement paresseux
#
# Même stratégie que i18n.py : chaque langue vit dans son propre fichier
# et n'est chargée en mémoire qu'à la première demande d'une info-bulle
# dans cette langue. "en" sert de repli.
#
# Les fichiers vivent dans locales/ (partagé avec i18n.py) mais sont
# préfixés "desc_" (desc_fr.json, desc_en.json...) pour éviter toute
# collision avec les fichiers de traduction de l'UI (fr.json, en.json...).
# ------------------------------------------------------------------------------------

_DESC_DIR = os.path.join(os.path.dirname(__file__), "locales")
_DESC_PREFIX = "desc_"

# Cache des langues déjà chargées : {code: {key: text}}
_DESC_CACHE: dict[str, dict] = {}


def _discover_available_desc_langs() -> set[str]:
    try:
        return {
            fname[len(_DESC_PREFIX):-5]  # retire "desc_" et ".json"
            for fname in os.listdir(_DESC_DIR)
            if fname.startswith(_DESC_PREFIX) and fname.endswith(".json")
        }
    except OSError:
        return {"en"}


AVAILABLE_DESC_LANGS = _discover_available_desc_langs()


def _load_desc_file(code: str) -> dict:
    path = os.path.join(_DESC_DIR, f"{_DESC_PREFIX}{code}.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _get_desc_table(lang: str) -> dict:
    """Retourne la table de descriptions d'une langue, en la chargeant et la
    mettant en cache au besoin. Replie sur 'en' si le fichier est manquant
    ou corrompu."""
    if lang in _DESC_CACHE:
        return _DESC_CACHE[lang]

    try:
        table = _load_desc_file(lang)
    except (OSError, json.JSONDecodeError) as e:
        print(f"[desc] WARNING: échec du chargement de '{lang}' ({e}), repli sur 'en'")
        if lang == "en":
            table = {}
        else:
            return _get_desc_table("en")

    _DESC_CACHE[lang] = table
    return table


# -----------------------------
# CORE API
# -----------------------------
def get_description(key: str, lang: str = "en") -> str:
    """
    Return localized description for a given key.
    Falls back to English if language not found.
    """
    lang_table = _get_desc_table(lang) if lang in AVAILABLE_DESC_LANGS else _get_desc_table("en")
    return lang_table.get(key, "")


# -----------------------------
# GTK TOOLTIP HELPERS
# -----------------------------
def set_tooltip(widget, key: str, lang: str = "en"):
    """
    Attach tooltip text to a GTK widget.
    """
    text = get_description(key, lang)
    if text:
        widget.set_tooltip_text(text)


def set_tooltip_from_text(widget, text: str):
    """
    Direct tooltip without key system.
    """
    if text:
        widget.set_tooltip_text(text)


def set_tooltip_if_available(widget, key: str, lang: str = "en"):
    """
    Safe version: never fails even if key is missing.
    """
    try:
        text = get_description(key, lang)
        if text:
            widget.set_tooltip_text(text)
    except Exception:
        pass


# -----------------------------
# BATCH TOOLTIP HELPERS
# -----------------------------
def apply_tooltips(widget_map: dict, lang: str = "en"):
    """
    Apply multiple tooltips at once.

    Example:
        apply_tooltips({
            self.mangohud: "mangohud",
            self.gamemode: "gamemode",
            self.prefix: "prefix"
        })
    """
    for widget, key in widget_map.items():
        set_tooltip_if_available(widget, key, lang)


# -----------------------------
# UTILITY: KEY HELPERS
# -----------------------------
def has_description(key: str, lang: str = "en") -> bool:
    """
    Check if a description exists for a key.
    """
    lang_table = _get_desc_table(lang) if lang in AVAILABLE_DESC_LANGS else _get_desc_table("en")
    return key in lang_table


def list_keys(lang: str = "en") -> list:
    """
    Return all available description keys.
    """
    lang_table = _get_desc_table(lang) if lang in AVAILABLE_DESC_LANGS else _get_desc_table("en")
    return list(lang_table.keys())


# -----------------------------
# OPTIONAL UX HELPERS
# -----------------------------
def attach_tooltip(widget, key: str, lang: str = "en"):
    """
    Alias cleaner pour set_tooltip (UX-friendly naming).
    """
    set_tooltip(widget, key, lang)


def attach_tooltips(widget_map: dict, lang: str = "en"):
    """
    Alias batch UX-friendly.
    """
    apply_tooltips(widget_map, lang)
