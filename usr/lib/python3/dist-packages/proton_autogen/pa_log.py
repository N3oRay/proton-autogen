#pa_log.py

import subprocess
import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, Gdk, GLib



# -----------------------------------------------------------
VALID_LEVELS = {"info", "warning", "error"}


def build_message_type(level: str, title: str, message: str):
    return {
        "level": level if level in VALID_LEVELS else "info",
        "title": title,
        "message": message,
    }


# -----------------------------
# CONSOLE
# -----------------------------
def _print(status):
    print(f"[{status['level'].upper()}] {status['title']}")
    print(status["message"])

# -----------------------------
# Toast
# -----------------------------

def _notify_toast(status, parent=None, timeout=3):
    """
    Toast non bloquant GTK4 (overlay simple)
    """

    win = Gtk.Window(
        transient_for=parent,
        decorated=False,
        resizable=False,
        modal=False,
    )

    win.set_default_size(300, 80)
    win.add_css_class("toast-window")

    box = Gtk.Box(
        orientation=Gtk.Orientation.VERTICAL,
        spacing=6,
        margin_top=10,
        margin_bottom=10,
        margin_start=10,
        margin_end=10,
    )

    title = Gtk.Label()
    title.set_markup(f"<b>{status.get('title','')}</b>")
    title.set_xalign(0)

    message = Gtk.Label(label=status.get("message", ""))
    message.set_xalign(0)
    message.set_wrap(True)

    box.append(title)
    box.append(message)

    win.set_child(box)

    # position simple (top-right approximatif)
    win.present()

    # auto close
    GLib.timeout_add_seconds(timeout, win.close)

    return win
# -----------------------------
# GTK UI (Dialog simple stable GTK4)
# -----------------------------

# ------------------------------------
# SHOW RESULT
# ------------------------------------
def show_result(status, ux_handler=None):
    if status["success"]:
        return

    print(f"[{status['level'].upper()}] {status['title']}")
    print(status["message"])

    if ux_handler:
        ux_handler(status)

#-----------------------------------------------------------

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

        5: (
            "error",
            "Launch failed",
            "CWD - current working directory. Unable to launch the game."
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
