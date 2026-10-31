#!/usr/bin/env python3
# ux/color_label.py
"""
Rendu GTK du moteur de mise en forme (ux/text_engine.py).

    insert_colored_text(buffer, texte)    aide, diagnostic, prérequis, ProtonDB, MangoHud
    insert_about_text(buffer, texte)      À propos
    insert_sensor_text(buffer, texte)     capteurs
    insert_changelog_text(buffer, texte)  debian/changelog

Les quatre fonctions gardent leur signature d'origine (+ `dark` optionnel) et ne
font plus qu'appeler render(buffer, texte, profil). Les règles de reconnaissance
et la palette vivent dans text_engine.py (sans GTK, testé sans écran).

Fond clair / sombre
-------------------
Les dialogues de deux thèmes (« cute » et « KDE »/givre) ont un fond clair ; les
autres un fond sombre. `dark=None` (défaut) déduit le mode du thème enregistré ;
un appelant peut le forcer avec dark=True / dark=False. En cas de doute (thème
inconnu, erreur de lecture), le mode sombre — l'apparence historique — s'applique.

Chaque mode a ses propres tags (« pa:dark:title », « pa:light:title »...) : un
même buffer peut être rendu dans les deux modes sans reliquat de couleurs.

Pango n'est importé qu'au moment de créer des tags : ce module s'importe sans GTK.
"""

import importlib
import os
from typing import Iterable, Optional

from proton_autogen.ux import text_engine
from proton_autogen.ux.text_engine import LOOKS, Look

# Ancien point d'entrée : « from proton_autogen.ux.color_label import colorize » reste valide.
colorize = text_engine.colorize

TAG_PREFIX = "pa"


def _pango():
    from gi.repository import Pango

    return Pango


# ---------------------------------------------------------------------------
# Mode clair / sombre
# ---------------------------------------------------------------------------

def current_theme_is_dark() -> bool:
    """Le thème appliqué a-t-il des dialogues sombres ? (sombre en cas de doute)"""
    try:
        # import_module : lit sys.modules avant l'attribut du paquet (substituable en test)
        themes = importlib.import_module("proton_autogen.ux.themes")

        css_file = os.path.basename(themes.STYLE_CSS.get(themes.load_saved_theme(), ""))
    except Exception:
        return True

    return not text_engine.is_light_theme_file(css_file)


# ---------------------------------------------------------------------------
# Tags
# ---------------------------------------------------------------------------

def tag_name(style: str, dark: bool) -> str:
    return f"{TAG_PREFIX}:{'dark' if dark else 'light'}:{style}"


def tag_properties(look: Look, dark: bool, pango) -> dict:
    """Propriétés Gtk.TextTag d'une apparence. `pango` : le module Pango."""
    props = {"foreground": look.color(dark)}

    if look.bold:
        props["weight"] = pango.Weight.BOLD
    if look.underline:
        props["underline"] = pango.Underline.SINGLE
    if look.monospace:
        props["family"] = "monospace"
    if look.scale != 1.0:
        props["scale"] = look.scale
    if look.above:
        props["pixels_above_lines"] = look.above
    if look.below:
        props["pixels_below_lines"] = look.below
    if look.margin:
        props["left_margin"] = look.margin
    if look.indent:
        props["indent"] = look.indent

    return props


def ensure_tags(buffer, styles: Iterable[str], dark: bool, pango=None) -> None:
    """Crée (une seule fois par buffer) les tags des rôles demandés."""
    tag_table = buffer.get_tag_table()

    for style in styles:
        name = tag_name(style, dark)

        if tag_table.lookup(name) is None:
            buffer.create_tag(name, **tag_properties(LOOKS[style], dark, pango or _pango()))


# ---------------------------------------------------------------------------
# Rendu
# ---------------------------------------------------------------------------

def render(buffer, text: str, profile: str, dark: Optional[bool] = None, pango=None) -> None:
    """Remplace le contenu de `buffer` par `text` mis en forme selon `profile`."""
    if dark is None:
        dark = current_theme_is_dark()

    ensure_tags(buffer, sorted(text_engine.styles_used(profile)), dark, pango)

    buffer.set_text("")

    for line in text_engine.parse_lines(text, profile):
        for span in line:
            end = buffer.get_end_iter()

            if span.style is None:
                buffer.insert(end, span.text)
            else:
                buffer.insert_with_tags_by_name(end, span.text, tag_name(span.style, dark))

        buffer.insert(buffer.get_end_iter(), "\n")


# ---------------------------------------------------------------------------
# API historique
# ---------------------------------------------------------------------------

def insert_colored_text(buffer, text, dark: Optional[bool] = None):
    render(buffer, text, "generic", dark)


def insert_about_text(buffer, text, dark: Optional[bool] = None):
    render(buffer, text, "about", dark)


def insert_sensor_text(buffer, text, dark: Optional[bool] = None):
    render(buffer, text, "sensors", dark)


def insert_changelog_text(buffer, text, dark: Optional[bool] = None):
    render(buffer, text, "changelog", dark)
