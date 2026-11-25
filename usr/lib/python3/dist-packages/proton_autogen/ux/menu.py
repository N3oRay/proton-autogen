#!/usr/bin/env python3

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Gio", "2.0")

from gi.repository import Gtk, Gio
from proton_autogen.i18n import tr
from proton_autogen.ux.dashboard_proton_update import make_menu_item



def add_menu_item(menu, label, action, icon_name):
    item = Gio.MenuItem.new(label, action)

    if icon_name:
        icon = Gio.ThemedIcon.new(icon_name)
        item.set_icon(icon)

    menu.append_item(item)

# =========================================================
# MAIN MENU MODEL (GTK4.14 / WAYLAND)
# =========================================================

def build_app_menu(app):

    menu = Gio.Menu()
    section = Gio.Menu()

    add_menu_item(
        section,
        tr("menu_settings"),
        "app.settings",
        "preferences-system-symbolic",
    )

    add_menu_item(
        section,
        tr("menu_shortcuts") or "Raccourcis clavier",
        "app.shortcuts",
        "input-keyboard-symbolic",
    )

    menu.append_section(None, section)

    section = Gio.Menu()

    add_menu_item(
        section,
        tr("menu_diagnostics"),
        "app.diag",
        "utilities-system-monitor-symbolic",
    )

    add_menu_item(
        section,
        tr("menu_sensors"),
        "app.sensors",
        "applications-system-symbolic",
    )

    add_menu_item(
        section,
        tr("menu_help_mangohud"),
        "app.mangohud",
        "applications-graphics-symbolic",
    )

    # ProtonPlus
    section.append_item(
        make_menu_item(
            tr("menu_proton_update") or "Mise à jour Proton"
        )
    )

    add_menu_item(
        section,
        tr("menu_steam_config"),
        "app.steam_config",
        "applications-games-symbolic",
    )

    menu.append_section(None, section)

    section = Gio.Menu()

    add_menu_item(
        section,
        tr("menu_help"),
        "app.help",
        "help-browser-symbolic",
    )

    add_menu_item(
        section,
        tr("menu_requirements"),
        "app.requis",
        "dialog-information-symbolic",
    )

    menu.append_section(None, section)

    section = Gio.Menu()

    add_menu_item(
        section,
        tr("menu_about_proton"),
        "app.aboutproton",
        "application-x-executable-symbolic",
    )

    add_menu_item(
        section,
        tr("menu_about"),
        "app.about",
        "help-about-symbolic",
    )

    menu.append_section(None, section)

    return menu

# =========================================================
# ATTACH MENU TO HEADER BUTTON
# =========================================================

def attach_menu(menu_button: Gtk.MenuButton, app):
    """
    Native GTK4 PopoverMenu.
    """

    menu_model = build_app_menu(app)

    popover = Gtk.PopoverMenu.new_from_model(menu_model)

    popover.add_css_class("main-app-menu")

    menu_button.set_popover(popover)

    menu_button.set_tooltip_text("Menu principal")

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
    box.append(make_btn(tr("menu_shortcuts") or "Raccourcis clavier", actions.get("shortcuts", lambda: None)))
    box.append(make_btn(tr("menu_diagnostics"), actions.get("diag", lambda: None)))
    box.append(make_btn(tr("menu_help"), actions.get("help", lambda: None)))
    box.append(make_btn(tr("menu_sensors"), actions.get("sensors", lambda: None)))
    box.append(make_btn(tr("menu_help_mangohud"), actions.get("mangohud", lambda: None)))
    box.append(make_btn(tr("menu_requirements"), actions.get("requis", lambda: None)))
    box.append(make_btn(tr("menu_proton_update") or "Mise à jour Proton", actions.get("proton_update", lambda: None)))
    box.append(make_btn(tr("menu_steam_config"), actions.get("steam_config", lambda: None)))
    box.append(make_btn(tr("menu_about_proton"), actions.get("aboutproton", lambda: None)))
    box.append(make_btn(tr("menu_about"), actions.get("about", lambda: None)))

    pop.set_child(box)
    pop.set_parent(parent)

    return pop
