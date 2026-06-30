#pa_log.py

import subprocess
import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, Gdk, GLib

# ------------------------------------
# SHOW MESSAGE
# ------------------------------------
def show_message(status):
    """
    Affiche un message utilisateur.

    status = {
        "success": False,
        "code": 10,
        "level": "error",
        "title": "Proton not found",
        "message": "Install Proton GE."
    }
    """

    level = status.get("level", "info")

    if level == "error":
        message_type = Gtk.MessageType.ERROR
    elif level == "warning":
        message_type = Gtk.MessageType.WARNING
    else:
        message_type = Gtk.MessageType.INFO

    dialog = Gtk.MessageDialog(
        transient_for=None,
        modal=True,
        message_type=message_type,
        buttons=Gtk.ButtonsType.OK,
        text=status["title"],
    )

    dialog.format_secondary_text(status["message"])

    dialog.connect("response", lambda d, r: d.destroy())
    dialog.show()

def show_result(status, ux_handler=None):
    if status["success"]:
        return

    print(f"[{status['level'].upper()}] {status['title']}")
    print(status["message"])

    if ux_handler:
        ux_handler(status)


def handle_result(result):
    """
    Normalise le résultat d'une exécution.

    Retourne toujours un dictionnaire :
        {
            "code": int,
            "success": bool,
            "level": "info|warning|error",
            "title": str,
            "message": str,
        }
    """

    if isinstance(result, subprocess.CompletedProcess):
        code = result.returncode
    elif isinstance(result, bool):
        code = 0 if result else 1
    elif isinstance(result, int):
        code = result
    elif result is None:
        code = 1
    else:
        code = 255

    messages = {
        0: (
            "info",
            "Game closed",
            "The game exited normally."
        ),

        1: (
            "error",
            "Launch failed",
            "Unable to launch the game."
        ),

        10: (
            "error",
            "File not found",
            "The selected executable does not exist."
        ),

        11: (
            "error",
            "Proton not found",
            "No compatible Proton installation was found."
        ),

        20: (
            "error",
            "Game crashed",
            "The game terminated unexpectedly."
        ),

        255: (
            "error",
            "Unknown error",
            "An unexpected error occurred."
        ),
    }

    level, title, message = messages.get(
        code,
        (
            "warning",
            "Exit code",
            f"Process exited with code {code}."
        ),
    )

    return {
        "code": code,
        "success": code == 0,
        "level": level,
        "title": title,
        "message": message,
    }
