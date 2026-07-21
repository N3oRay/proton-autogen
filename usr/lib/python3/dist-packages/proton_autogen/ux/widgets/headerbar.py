#!/usr/bin/env python3

import gi
gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, Gdk

from proton_autogen.ux.menu import attach_menu


class DashboardHeaderBar(Gtk.HeaderBar):
    def __init__(
        self,
        app,
        *,
        on_refresh=None,
        on_add=None,
        on_change_style=None,
        show_refresh=True,
        show_add=True,
    ):
        super().__init__()

        self.add_css_class("main-header")

        #
        # Refresh
        #
        if show_refresh:
            refresh_btn = Gtk.Button(icon_name="view-refresh-symbolic")
            refresh_btn.set_tooltip_text("Refresh game list")

            if on_refresh:
                refresh_btn.connect("clicked", on_refresh)

            self.pack_start(refresh_btn)

        #
        # Add Game
        #
        if show_add:
            add_btn = Gtk.Button(label="+")
            add_btn.add_css_class("suggested-action")

            if on_add:
                add_btn.connect("clicked", on_add)

            self.pack_start(add_btn)

        #
        # Style
        #
        display = Gdk.Display.get_default()
        theme = Gtk.IconTheme.get_for_display(display)

        icon = "applications-graphics-symbolic"
        if not theme.has_icon(icon):
            icon = "preferences-system-symbolic"

        style_btn = Gtk.Button(icon_name=icon)
        #style_btn = Gtk.Button( icon_name="applications-graphics-symbolic" )
        style_btn.set_tooltip_text("Change UI style")
        style_btn.add_css_class("app-button")

        if on_change_style:
            style_btn.connect("clicked", on_change_style)

        self.pack_end(style_btn)

        #
        # Menu
        #
        menu_btn = Gtk.MenuButton(label="☰")
        attach_menu(menu_btn, app)
        self.pack_end(menu_btn)
