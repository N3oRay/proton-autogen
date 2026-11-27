#!/usr/bin/env python3

# game_more_menu.py
"""
Menu « ⋮ » (plus d'actions) d'un jeu, partagé par la liste et la grille.

Contenu, dans cet ordre :
    Ouvrir le dossier
    Exporter vers Lutris
    Exporter vers Bottles
    ───────────────
    Retirer le jeu de la bibliothèque

  - build_more_menu(on_action) : le popover ; on_action(nom_d_action) est appelé
    APRÈS la fermeture du popover ;
  - make_more_button(popover)  : le bouton ⋮ qui l'ouvre (Gtk.MenuButton).

Le popover réutilise les classes CSS du menu contextuel de la grille
(`game-grid-context-popover`, `game-grid-menu-button`, `game-grid-menu-delete`) :
tous les thèmes le stylent déjà, sans CSS supplémentaire.
"""

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
from gi.repository import Gdk, Gtk

from proton_autogen.i18n import tr

ACTION_OPEN_FOLDER = "open_folder"
ACTION_EXPORT_LUTRIS = "export_lutris"
ACTION_EXPORT_BOTTLES = "export_bottles"
ACTION_REMOVE = "remove"

MORE_ICON = "view-more-symbolic"   # ⋮ (vertical) dans Adwaita
MORE_GLYPH = "⋮"                   # secours si le thème d'icônes n'a pas l'icône

# (action, clé de traduction, classe CSS du bouton)
_ITEMS = (
    (ACTION_OPEN_FOLDER, "open_folder", "game-grid-menu-button"),
    (ACTION_EXPORT_LUTRIS, "export_lutris", "game-grid-menu-button"),
    (ACTION_EXPORT_BOTTLES, "export_bottles", "game-grid-menu-button"),
    (ACTION_REMOVE, "remove_from_library", "game-grid-menu-delete"),
)


def build_more_menu(on_action, lutris_enabled=True):
    """Construit le popover du menu ⋮.

    on_action(name) est appelé avec ACTION_* après fermeture du popover.
    lutris_enabled=False masque « Exporter vers Lutris »."""
    popover = Gtk.Popover()
    popover.add_css_class("game-grid-context-popover")
    popover.set_has_arrow(True)
    popover.set_autohide(True)

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
    box.add_css_class("game-grid-context-menu")
    box.set_margin_top(5)
    box.set_margin_bottom(5)
    box.set_margin_start(5)
    box.set_margin_end(5)

    def activate(name):
        popover.popdown()
        on_action(name)

    for action, key, css_class in _ITEMS:
        if action == ACTION_EXPORT_LUTRIS and not lutris_enabled:
            continue

        if action == ACTION_REMOVE:
            separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
            separator.set_margin_top(3)
            separator.set_margin_bottom(3)
            box.append(separator)

        button = Gtk.Button(label=tr(key))
        button.set_halign(Gtk.Align.FILL)
        button.add_css_class(css_class)
        button.connect("clicked", lambda _b, name=action: activate(name))
        # Repérable par les tests et les technologies d'assistance.
        button.set_name(f"more-{action}")
        box.append(button)

    popover.set_child(box)
    return popover


def _has_icon(icon_name):
    display = Gdk.Display.get_default()
    if display is None:
        return False
    return Gtk.IconTheme.get_for_display(display).has_icon(icon_name)


def make_more_button(popover, css_classes=(), label=None):
    """Bouton ⋮ qui ouvre `popover`.

    Sans `label` : bouton icône seul (liste). Avec `label` : « ⋮  <label> »
    (entrée du menu contextuel de la grille). `css_classes` est appliqué au
    bouton interne du Gtk.MenuButton, c'est lui que les thèmes stylent."""
    button = Gtk.MenuButton()
    button.set_popover(popover)
    button.set_tooltip_text(tr("more_actions"))
    button.set_valign(Gtk.Align.CENTER)

    if label:
        button.set_label(f"{MORE_GLYPH}  {label}")
    elif _has_icon(MORE_ICON):
        button.set_icon_name(MORE_ICON)
    else:
        button.set_label(MORE_GLYPH)

    inner = button.get_first_child()
    if inner is not None:
        for css_class in css_classes:
            inner.add_css_class(css_class)
    return button
