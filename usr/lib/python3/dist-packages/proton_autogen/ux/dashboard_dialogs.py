#!/usr/bin/env python3
import os
import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk

from proton_autogen.color_label import insert_colored_text, insert_sensor_text, insert_about_text
from proton_autogen.core import get_about_text, get_about_proton_text
from proton_autogen.info import get_help_text
from proton_autogen.sensor import get_sensors_text, get_mangohud_advice
from proton_autogen.requis import afficher_requirements_label
from proton_autogen.backend import get_diagnostic_text


class DashboardDialogsMixin:
    """Boîtes de dialogue du Dashboard (About, Help, Diagnostic, Sensors, ...).
    Doit être mixé avec une classe Gtk.ApplicationWindow.
    """

    # -------------------------
    # BUILD DIALOG (générique)
    # -------------------------
    def build_dialog(self, title, content_widget, width=600, height=800):
        win = Gtk.Window(
            title=title,
            transient_for=self,
            modal=True
        )
        win.add_css_class("style")
        win.set_default_size(width, height)

        overlay = Gtk.Overlay()
        win.set_child(overlay)

        base = os.path.dirname(__file__)
        logo = Gtk.Image.new_from_file(
            os.path.join(base, "assets", "logo-pa.jpg")
        )
        logo.set_opacity(0.06)
        overlay.set_child(logo)

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        root.set_margin_top(10)
        root.set_margin_bottom(10)
        root.set_margin_start(10)
        root.set_margin_end(10)
        root.add_css_class("dialog-content")
        root.append(content_widget)

        overlay.add_overlay(root)
        win.present()

        return win

    # -------------------------
    # Helper interne : ScrolledWindow + TextView monospace
    # -------------------------
    def _build_text_view(self, wrap=True, left_margin=6, right_margin=6):
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_hexpand(True)

        textview = Gtk.TextView()
        textview.set_editable(False)
        textview.set_cursor_visible(False)
        textview.set_monospace(True)
        textview.set_left_margin(left_margin)
        textview.set_right_margin(right_margin)
        if wrap:
            textview.set_wrap_mode(Gtk.WrapMode.WORD)

        scroll.set_child(textview)
        return scroll, textview

    # -------------------------
    # DIALOG ABOUT
    # -------------------------
    def show_about_dialog(self):
        scroll, textview = self._build_text_view()
        insert_about_text(textview.get_buffer(), get_about_text())
        self.build_dialog("About", scroll, width=700, height=750)

    # -------------------------
    # DIALOG ABOUT PROTON
    # -------------------------
    def show_about_proton_dialog(self):
        scroll, textview = self._build_text_view()
        insert_colored_text(textview.get_buffer(), get_about_proton_text())
        self.build_dialog("About Proton", scroll, width=700, height=750)

    # -------------------------
    # DIALOG HELP
    # -------------------------
    def show_help_dialog(self):
        scroll, textview = self._build_text_view(left_margin=8, right_margin=8)
        textview.set_pixels_above_lines(2)
        textview.set_pixels_below_lines(2)
        insert_colored_text(textview.get_buffer(), get_help_text())
        self.build_dialog("Help", scroll, width=700, height=800)

    # -------------------------
    # DIALOG DIAGNOSTIC
    # -------------------------
    def show_diagnostic_dialog(self):
        scroll, textview = self._build_text_view(left_margin=0, right_margin=0)
        insert_colored_text(textview.get_buffer(), get_diagnostic_text())
        self.build_dialog("Diagnostic", scroll, width=800, height=750)

    # -------------------------
    # DIALOG REQUIS
    # -------------------------
    def show_requis_dialog(self):
        scroll, textview = self._build_text_view()
        insert_colored_text(textview.get_buffer(), afficher_requirements_label())
        self.build_dialog("Requis", scroll, width=700, height=650)

    # -------------------------
    # DIALOG SENSORS
    # -------------------------
    def show_sensors_dialog(self):
        scroll, textview = self._build_text_view(left_margin=0, right_margin=0)
        insert_sensor_text(textview.get_buffer(), get_sensors_text())
        self.build_dialog("Sensors", scroll, width=750, height=600)

    # -------------------------
    # DIALOG MANGOHUD ADVICE
    # -------------------------
    def show_mangohud_advice_dialog(self):
        scroll, textview = self._build_text_view(left_margin=0, right_margin=0)
        insert_colored_text(textview.get_buffer(), get_mangohud_advice())
        self.build_dialog("MangoHud Config Advice", scroll, width=750, height=500)

    # -------------------------
    # EXPORT LUTRIS - MESSAGE DIALOG
    # -------------------------
    def show_export_dialog(self, file_path):
        file_path = str(file_path)

        win = Gtk.Window(
            transient_for=self,
            modal=True,
            title="Export Lutris terminé"
        )
        win.set_default_size(520, 180)
        win.set_destroy_with_parent(True)
        win.add_css_class("export-dialog")

        box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=12,
            margin_top=20,
            margin_bottom=20,
            margin_start=20,
            margin_end=20
        )

        title = Gtk.Label(label="✔ Export Lutris terminé")
        title.add_css_class("export-title")
        box.append(title)

        entry = Gtk.Entry()
        entry.set_text(file_path)
        entry.set_editable(False)
        entry.set_can_focus(True)
        entry.add_css_class("export-path")
        box.append(entry)

        def copy_to_clipboard(_):
            display = Gdk.Display.get_default()
            clipboard = display.get_clipboard()
            clipboard.set(file_path)

        btn_copy = Gtk.Button(label="Copy path")
        btn_copy.connect("clicked", copy_to_clipboard)

        btn_close = Gtk.Button(label="OK")
        btn_close.connect("clicked", lambda *_: win.close())

        buttons = Gtk.Box(spacing=8)
        buttons.append(btn_copy)
        buttons.append(btn_close)
        box.append(buttons)

        win.set_child(box)
        win.present()
