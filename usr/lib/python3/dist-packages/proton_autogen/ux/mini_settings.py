#!/usr/bin/env python3
# mini_settings.py
"""
Réglages et détection du « mode réduit » — SANS GTK.

  - detect_minimize_support() : Gtk.Window.minimize() a-t-il une chance de
    fonctionner sur la session courante (X11, Wayland, compositeurs tiling) ?
  - load/save_mini_mode_enabled(), load/save_minimize_mode() : préférences
    [mini] du fichier proton-autogen-ux.conf
  - resolve_minimize_enabled() : décision finale (variable d'environnement,
    puis préférence, puis détection automatique)

Extrait tel quel de ux/dashboard_mini.py, qui reste le point d'entrée
historique : tous ces noms y sont toujours importables.
"""

import configparser
import os

from proton_autogen.ux.themes import CONFIG_PATH


# ------------------------------------------------------------------------------------
# DÉTECTION DE SUPPORT DE minimize() (pure, sans GTK — testable isolément)
# ------------------------------------------------------------------------------------

# Environnements de bureau Wayland "complets" connus pour honorer
# correctement xdg_toplevel.set_minimized (testé via KWin/Mutter). Tout
# ce qui n'y figure pas est traité comme non fiable par défaut : les
# compositeurs tiling (Hyprland, Sway, river, wayfire, labwc...) n'ont
# généralement pas de notion de fenêtre "minimisée" faute de barre des
# tâches vers laquelle réduire, et ignorent silencieusement la requête.
# Volontairement une liste blanche (opt-in) plutôt qu'une liste noire :
# en cas de doute sur un compositeur inconnu, on préfère ne pas
# prétendre à un mode réduit qui n'aurait aucun effet visible.
_WAYLAND_MINIMIZE_SUPPORTED = {
    "kde", "plasma", "gnome", "gnome-shell", "cinnamon", "mate", "xfce", "budgie",
}

# Compositeurs Wayland tiling connus pour NE PAS honorer la requête.
# Cette liste sert uniquement à enrichir le message de log (nommer
# explicitement le compositeur détecté) — la décision elle-même repose
# sur l'absence de _WAYLAND_MINIMIZE_SUPPORTED, pas sur cette liste.
_WAYLAND_MINIMIZE_KNOWN_UNSUPPORTED = {
    "hyprland", "sway", "river", "wayfire", "labwc", "dwl",
}


def _detect_session_info() -> tuple[str, str]:
    """Retourne (type_session, id_bureau) en minuscules, d'après les
    variables d'environnement standard XDG."""
    session_type = os.environ.get("XDG_SESSION_TYPE", "").strip().lower()

    desktop = (
        os.environ.get("XDG_CURRENT_DESKTOP", "")
        or os.environ.get("XDG_SESSION_DESKTOP", "")
        or os.environ.get("DESKTOP_SESSION", "")
    ).strip().lower()

    return session_type, desktop


def detect_minimize_support() -> tuple[bool, str]:
    """
    Détermine si Gtk.Window.minimize() a une chance raisonnable de
    fonctionner sur la session courante.

    Retourne (supporté, raison) — la raison est uniquement destinée au
    logging/diagnostic, jamais affichée à l'utilisateur.

      - X11 : toujours supporté (iconify est un mécanisme ICCCM
        standard, indépendant du gestionnaire de fenêtres).
      - Hyprland : détecté explicitement via la variable
        HYPRLAND_INSTANCE_SIGNATURE, posée par Hyprland lui-même — plus
        fiable que XDG_CURRENT_DESKTOP, qui peut varier selon la
        méthode de lancement de la session.
      - Wayland, autre bureau : supporté uniquement si l'identifiant de
        bureau figure dans la liste blanche _WAYLAND_MINIMIZE_SUPPORTED
        (KDE, GNOME, XFCE...). Non supporté par défaut sinon.
      - Type de session inconnu (rare) : posture prudente, non supporté.
    """
    if "HYPRLAND_INSTANCE_SIGNATURE" in os.environ:
        return False, "hyprland (HYPRLAND_INSTANCE_SIGNATURE détectée)"

    session_type, desktop = _detect_session_info()

    if session_type == "x11":
        return True, "x11"

    if session_type == "wayland":
        # XDG_CURRENT_DESKTOP peut contenir plusieurs valeurs séparées
        # par ':' (ex: "ubuntu:GNOME") -> on teste chaque segment.
        segments = [d for d in desktop.split(":") if d]

        for seg in segments:
            if seg in _WAYLAND_MINIMIZE_SUPPORTED:
                return True, f"wayland/{seg}"

        for seg in segments:
            if seg in _WAYLAND_MINIMIZE_KNOWN_UNSUPPORTED:
                return False, f"wayland/{seg} (compositeur tiling connu)"

        return False, f"wayland/{desktop or 'inconnu'} (hors liste blanche)"

    return False, f"type de session inconnu ({session_type or 'non défini'})"


# ------------------------------------------------------------------------------------
# CONFIGURATION (pure, sans GTK) — réutilise le même fichier que themes.py
# ------------------------------------------------------------------------------------

def load_mini_mode_enabled(default: bool = True) -> bool:
    """Lit la préférence utilisateur [mini] mini_mode dans le même
    fichier de config que le thème (proton-autogen-ux.conf). Activé par
    défaut ; peut être désactivé sans toucher au reste de la config."""
    cfg = configparser.ConfigParser()

    if CONFIG_PATH.exists():
        try:
            cfg.read(CONFIG_PATH)
            return cfg.getboolean("mini", "mini_mode", fallback=default)
        except Exception:
            return default

    return default


def save_mini_mode_enabled(enabled: bool):
    cfg = configparser.ConfigParser()

    if CONFIG_PATH.exists():
        try:
            cfg.read(CONFIG_PATH)
        except Exception:
            pass

    if "mini" not in cfg:
        cfg["mini"] = {}

    cfg["mini"]["mini_mode"] = "true" if enabled else "false"

    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        cfg.write(f)


_VALID_MINIMIZE_MODES = ("auto", "on", "off")


def load_minimize_mode(default: str = "auto") -> str:
    """Lit [mini] minimize dans proton-autogen-ux.conf :
      - "auto" (défaut) : suit detect_minimize_support().
      - "on"  : force minimize() même hors liste blanche (utile si la
        détection se trompe sur un compositeur non répertorié qui
        honore en fait la requête).
      - "off" : désactive minimize() quel que soit le résultat de la
        détection, sans affecter le reste du mode réduit (notification
        toujours active).
    """
    cfg = configparser.ConfigParser()

    if CONFIG_PATH.exists():
        try:
            cfg.read(CONFIG_PATH)
            value = cfg.get("mini", "minimize", fallback=default).strip().lower()
            if value in _VALID_MINIMIZE_MODES:
                return value
        except Exception:
            pass

    return default


def save_minimize_mode(mode: str):
    if mode not in _VALID_MINIMIZE_MODES:
        raise ValueError(f"mode invalide: {mode!r} (attendu: {_VALID_MINIMIZE_MODES})")

    cfg = configparser.ConfigParser()

    if CONFIG_PATH.exists():
        try:
            cfg.read(CONFIG_PATH)
        except Exception:
            pass

    if "mini" not in cfg:
        cfg["mini"] = {}

    cfg["mini"]["minimize"] = mode

    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        cfg.write(f)


def resolve_minimize_enabled() -> tuple[bool, str]:
    """Résout la décision finale minimize() oui/non, dans cet ordre de
    priorité :

      1. Variable d'environnement PROTON_AUTOGEN_FORCE_MINIMIZE (1/0),
         utile pour tester sans toucher au fichier de config.
      2. Préférence persistée [mini] minimize ("on"/"off").
      3. Détection automatique (detect_minimize_support()).

    Retourne (activé, raison) pour le logging.
    """
    env_override = os.environ.get("PROTON_AUTOGEN_FORCE_MINIMIZE")
    if env_override is not None:
        enabled = env_override.strip().lower() not in ("0", "false", "no", "off")
        return enabled, f"variable d'environnement PROTON_AUTOGEN_FORCE_MINIMIZE={env_override!r}"

    mode = load_minimize_mode()

    if mode == "on":
        return True, "forcé via config ([mini] minimize = on)"

    if mode == "off":
        return False, "désactivé via config ([mini] minimize = off)"

    return detect_minimize_support()
