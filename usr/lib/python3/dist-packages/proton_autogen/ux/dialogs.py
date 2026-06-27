#!/usr/bin/env python3

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, GLib


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
