#!/usr/bin/env python3

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Gio", "2.0")

from gi.repository import Gtk, Gio
from proton_autogen.i18n import tr



# =========================================================
# MAIN MENU MODEL (GTK4 / WAYLAND SAFE)
# =========================================================
def build_app_menu(app):
    """
    Creates Gio.Menu + actions binding
    Compatible with GTK4 MenuButton
    """

    menu = Gio.Menu()

    menu.append(tr("menu_settings"), "app.settings")
    menu.append(tr("menu_diagnostics"), "app.diag")
    menu.append(tr("menu_sensors"), "app.sensors")
    menu.append(tr("menu_help_mangohud"), "app.mangohud")
    menu.append(tr("menu_help"), "app.help")
    menu.append(tr("menu_requirements"), "app.requis")
    menu.append(tr("menu_about_proton"), "app.aboutproton")
    menu.append(tr("menu_about"), "app.about")

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

    box.append(make_btn(tr("menu_settings"), actions.get("settings", lambda: None)))
    box.append(make_btn(tr("menu_diagnostics"), actions.get("diag", lambda: None)))
    box.append(make_btn(tr("menu_help"), actions.get("help", lambda: None)))
    box.append(make_btn(tr("menu_sensors"), actions.get("sensors", lambda: None)))
    box.append(make_btn(tr("menu_help_mangohud"), actions.get("mangohud", lambda: None)))
    box.append(make_btn(tr("menu_requirements"), actions.get("requis", lambda: None)))
    box.append(make_btn(tr("menu_about_proton"), actions.get("aboutproton", lambda: None)))
    box.append(make_btn(tr("menu_about"), actions.get("about", lambda: None)))

    pop.set_child(box)
    pop.set_parent(parent)

    return pop


# =========================================================
# ATTACH MENU TO HEADER BUTTON
# =========================================================
def attach_menu(menu_button: Gtk.MenuButton, app):
    """
    Clean GTK4 menu binding (avoids GtkPopoverMenu warnings)
    """

    menu_model = build_app_menu(app)

    popover = Gtk.PopoverMenu.new_from_model(menu_model)

    menu_button.set_popover(popover)

    # 🔥 important fix: avoids "broken active state"
    menu_button.set_can_focus(False)
    menu_button.set_focus_on_click(False)
