#!/usr/bin/env python3
# ux/adw_rows.py
"""
Interrupteurs AdwSwitchRow (ON/OFF) avec repli sur Gtk.CheckButton.

Un seul widget Adwaita est utilisé, volontairement : les autres lignes
(listes, champs) agrandissaient trop les menus.

    new_switch(title, active)  -> AdwSwitchRow  (ou CheckButton en repli)
    new_switch_list()          -> conteneur compact pour les interrupteurs

Les deux variantes partagent la même API : get_active() / set_active() et
le signal "notify::active".

Adwaita n'est utilisé que si libadwaita >= 1.4 est disponible (AdwSwitchRow).
Sinon — ou avec PROTON_AUTOGEN_NO_ADW=1 — l'interface reste celle d'avant.

NB : Adw.init() est appelé à l'import (idempotent si l'application l'a déjà
fait) ; il applique la feuille de style libadwaita à toute l'application.
"""

import os

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk

Adw = None

if not os.environ.get("PROTON_AUTOGEN_NO_ADW"):
    try:
        gi.require_version("Adw", "1")
        from gi.repository import Adw as _Adw

        if _Adw.get_minor_version() >= 4:
            Adw = _Adw
            if not Adw.is_initialized():
                Adw.init()
    except (ValueError, ImportError):
        Adw = None

USE_ADW = Adw is not None

# Lignes resserrées : hauteur proche de celle d'une case à cocher.
_COMPACT_CSS = b"""
.pa-switch-list row > box.header { min-height: 0; padding-top: 2px; padding-bottom: 2px; }
.pa-switch-list row { min-height: 0; }
"""
_css_loaded = False


def _load_compact_css():
    global _css_loaded
    if _css_loaded:
        return
    display = Gdk.Display.get_default()
    if display is None:
        return
    provider = Gtk.CssProvider()
    provider.load_from_data(_COMPACT_CSS)
    Gtk.StyleContext.add_provider_for_display(
        display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )
    _css_loaded = True


def new_switch(title: str, active: bool = False):
    if USE_ADW:
        row = Adw.SwitchRow(title=title)
        row.set_active(bool(active))
        return row

    check = Gtk.CheckButton(label=title)
    check.add_css_class("feature-toggle")
    check.set_active(bool(active))
    return check


def new_switch_list():
    """Conteneur des interrupteurs : liste compacte (Adwaita) ou simple
    boîte verticale (repli, rendu identique à l'ancien)."""
    if USE_ADW:
        _load_compact_css()
        box = Gtk.ListBox()
        box.set_selection_mode(Gtk.SelectionMode.NONE)
        box.add_css_class("boxed-list")
        box.add_css_class("pa-switch-list")
        return box

    return Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)


def list_add(container, widget):
    container.append(widget)
