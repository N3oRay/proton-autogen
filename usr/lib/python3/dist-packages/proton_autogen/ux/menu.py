#!/usr/bin/env python3

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Gio", "2.0")

from gi.repository import Gtk, Gio


# =========================================================
# MAIN MENU MODEL (GTK4 / WAYLAND SAFE)
# =========================================================
def build_app_menu(app):
    """
    Creates Gio.Menu + actions binding
    Compatible with GTK4 MenuButton
    """

    menu = Gio.Menu()

    menu.append("Diagnostics", "app.diag")
    menu.append("Help", "app.help")
    menu.append("About", "app.about")

    return menu


# =========================================================
# POPUP MENU (fallback / optional UX)
# =========================================================
def create_popover_menu(parent, actions=None):
    """
    Lightweight fallback menu (manual GTK4 popover)
    Useful if you want custom UI instead of Gio.Menu
    """

    pop = Gtk.PopoverMenu()

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

    def make_btn(label, callback):
        btn = Gtk.Button(label=label)
        btn.connect("clicked", lambda x: callback())
        return btn

    # Default actions
    if actions is None:
        actions = {}

    box.append(make_btn("Diagnostics", actions.get("diag", lambda: None)))
    box.append(make_btn("Help", actions.get("help", lambda: None)))
    box.append(make_btn("About", actions.get("about", lambda: None)))

    pop.set_child(box)
    pop.set_parent(parent)

    return pop


# =========================================================
# ATTACH MENU TO HEADER BUTTON
# =========================================================
def attach_menu(menu_button: Gtk.MenuButton, app):
    """
    Attach Gio.Menu to a MenuButton (recommended GTK4 way)
    """

    menu_button.set_menu_model(build_app_menu(app))
