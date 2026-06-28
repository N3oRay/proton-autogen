# desc.py : info-bulles / UX descriptions

from gi.repository import Gtk


# -----------------------------
# CORE DESCRIPTIONS
# -----------------------------
_DESCRIPTIONS = {
    "fr": {
        "show_performance":
            "Affiche en jeu un panneau indiquant les FPS, l'utilisation du processeur (CPU), "
            "de la carte graphique (GPU), la mémoire et d'autres statistiques.",

        "optimize_performance":
            "Optimise automatiquement les performances du système pendant l'exécution du jeu "
            "en ajustant certaines priorités et paramètres.",

        "mangohud":
            "MangoHud est une surcouche graphique affichant en temps réel les FPS, la charge CPU/GPU, "
            "la température, la consommation mémoire et d'autres informations utiles.",

        "gamemode":
            "GameMode est un service qui optimise temporairement le système pendant l'exécution du jeu "
            "afin d'améliorer les performances et de réduire les ralentissements.",

        "prefix":
            "Un environnement séparé contenant la configuration Windows, les bibliothèques et les logiciels "
            "installés pour cette application. Chaque environnement est indépendant afin d'éviter les conflits entre les jeux.",

        "prefix_short":
            "Créer un environnement séparé pour cette application.",

        "performance_overlay":
            "Afficher les performances (FPS, CPU, GPU)",

        "system_optimization":
            "Optimiser les performances système",
    },

    "en": {
        "show_performance":
            "Displays an in-game overlay showing FPS, CPU usage, GPU usage, memory consumption "
            "and other useful performance statistics.",

        "optimize_performance":
            "Automatically optimizes system performance while the game is running by adjusting "
            "priorities and system settings.",

        "mangohud":
            "MangoHud is an in-game overlay that displays real-time FPS, CPU/GPU usage, "
            "temperatures, memory usage and other performance statistics.",

        "gamemode":
            "GameMode is a system service that temporarily optimizes your computer while a game "
            "is running to improve performance and reduce stuttering.",

        "prefix":
            "A separate environment containing the Windows configuration, installed libraries and "
            "applications used by this program. Each environment is isolated to avoid conflicts between games.",

        "prefix_short":
            "Create a separate environment for this application.",

        "performance_overlay":
            "Show performance (FPS, CPU, GPU)",

        "system_optimization":
            "Optimize system performance",
    }
}


# -----------------------------
# CORE API
# -----------------------------
def get_description(key: str, lang: str = "en") -> str:
    """
    Return localized description for a given key.
    Falls back to English if language not found.
    """
    lang_table = _DESCRIPTIONS.get(lang) or _DESCRIPTIONS["en"]
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
    lang_table = _DESCRIPTIONS.get(lang) or _DESCRIPTIONS["en"]
    return key in lang_table


def list_keys(lang: str = "en") -> list:
    """
    Return all available description keys.
    """
    lang_table = _DESCRIPTIONS.get(lang) or _DESCRIPTIONS["en"]
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
