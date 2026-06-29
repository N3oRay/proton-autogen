#!/usr/bin/env python3

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, GLib
# =========================================================
# launch  - GAME
# =========================================================

def show_launch_dialog(self, game_name):
    """Display a modal dialog while a game is launching."""

    dialog = Gtk.Window(
        title="Launching",
        transient_for=self,
        modal=True,
        resizable=False,
        default_width=380,
        default_height=220,
    )

    dialog.add_css_class("launch-dialog")

    box = Gtk.Box(
        orientation=Gtk.Orientation.VERTICAL,
        spacing=18,
        margin_top=24,
        margin_bottom=24,
        margin_start=24,
        margin_end=24,
        halign=Gtk.Align.CENTER,
        valign=Gtk.Align.CENTER,
    )

    spinner = Gtk.Spinner()
    spinner.set_size_request(48, 48)
    spinner.set_halign(Gtk.Align.CENTER)
    spinner.start()

    title = Gtk.Label(label="Launching game")
    title.add_css_class("launch-title")
    title.set_halign(Gtk.Align.CENTER)

    game = Gtk.Label(label=game_name)
    game.add_css_class("launch-game")
    game.set_wrap(True)
    game.set_justify(Gtk.Justification.CENTER)
    game.set_halign(Gtk.Align.CENTER)

    info = Gtk.Label(label="Please wait...")
    info.add_css_class("launch-info")
    info.set_halign(Gtk.Align.CENTER)

    box.append(spinner)
    box.append(title)
    box.append(game)
    box.append(info)

    dialog.set_child(box)

    self.launch_dialog = dialog
    dialog.present()


def hide_launch_dialog(self):
    """Close the launch dialog if it exists."""

    if getattr(self, "launch_dialog", None):
        self.launch_dialog.close()
        self.launch_dialog = None

# =========================================================
# FILE PICKER - ADD GAME
# =========================================================
def open_game_file_dialog(parent, callback):
    """
    Ouvre un FileDialog GTK4 pour sélectionner un .exe
    Compatible X11 + Wayland (native GTK4 API)
    """

    dialog = Gtk.FileDialog()
    dialog.set_title("Select game executable")

    def _on_result(dialog, result):
        try:
            file = dialog.open_finish(result)

            if not file:
                callback(None)
                return

            path = file.get_path()
            callback(path)

        except Exception as e:
            print("[dialogs] FileDialog error:", e)
            callback(None)

    dialog.open(parent, None, _on_result)


# =========================================================
# SIMPLE MESSAGE DIALOG
# =========================================================
def show_message(parent, title: str, message: str):
    """
    Simple info dialog (GTK4)
    """

    dialog = Gtk.AlertDialog()
    dialog.set_title(title)
    dialog.set_message(message)

    dialog.show(parent, None)


# =========================================================
# CONFIRMATION DIALOG
# =========================================================
def show_confirm(parent, title: str, message: str, callback):
    """
    Yes/No dialog (useful for delete game, reset prefix, etc.)
    """

    dialog = Gtk.AlertDialog()
    dialog.set_title(title)
    dialog.set_message(message)

    dialog.set_buttons(["Cancel", "OK"])
    dialog.set_default_button(1)
    dialog.set_cancel_button(0)

    def _on_response(dialog, result):
        try:
            response = dialog.choose_finish(result)
            # 1 = OK, 0 = Cancel
            callback(response == 1)
        except Exception as e:
            print("[dialogs] Confirm error:", e)
            callback(False)

    dialog.choose(parent, None, _on_response)


# =========================================================
# ERROR DIALOG (UX SAFE)
# =========================================================
def show_error(parent, title: str, error: str):
    """
    Error popup safe for UX
    """

    dialog = Gtk.AlertDialog()
    dialog.set_title(title)
    dialog.set_message(error)

    dialog.show(parent, None)
