#!/usr/bin/env python3

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, GLib

from proton_autogen.ux.dashboard_status import clean_message, cap_lines

# La popup de lancement est petite et de hauteur FIXE (resizable=False,
# default_height=220) : impossible d'y laisser le même plafond que la
# barre de statut du bas (MAX_DISPLAY_LINES=6 lignes dans
# dashboard_status.py), sous peine de texte qui déborde du cadre.
LAUNCH_DIALOG_MAX_LINES = 2


# =========================================================
# STANDARD GTK4 DIALOG
# =========================================================

def _create_dialog(parent, title: str, message: str, icon_name: str):
    """
    Create a reusable native GTK4 dialog window.
    Compatible with GTK 4.14.
    """

    dialog = Gtk.Window(
        title=title,
        modal=True,
        resizable=False,
        default_width=420,
    )

    if parent is not None:
        dialog.set_transient_for(parent)

    dialog.add_css_class("app-dialog")

    # Main container
    main_box = Gtk.Box(
        orientation=Gtk.Orientation.VERTICAL,
        spacing=20,
        margin_top=24,
        margin_bottom=20,
        margin_start=24,
        margin_end=24,
    )

    # Message area
    content_box = Gtk.Box(
        orientation=Gtk.Orientation.HORIZONTAL,
        spacing=16,
        valign=Gtk.Align.CENTER,
    )

    # Symbolic GTK icon
    icon = Gtk.Image.new_from_icon_name(icon_name)
    icon.set_pixel_size(36)
    icon.set_valign(Gtk.Align.START)

    content_box.append(icon)

    # Message
    label = Gtk.Label(label=message)
    label.set_wrap(True)
    label.set_xalign(0)
    label.set_yalign(0.5)
    label.set_max_width_chars(55)
    label.set_hexpand(True)

    content_box.append(label)
    main_box.append(content_box)

    dialog.set_child(main_box)

    return dialog, main_box

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
    info.set_wrap(True)
    info.set_justify(Gtk.Justification.CENTER)
    # Évite qu'un message de progression un peu long ("stdout: ...")
    # ne fasse exploser la largeur fixe (380px) de la popup.
    info.set_max_width_chars(40)

    box.append(spinner)
    box.append(title)
    box.append(game)
    box.append(info)

    dialog.set_child(box)

    self.launch_dialog = dialog
    # Référence gardée pour update_launch_dialog_info() : permet à
    # dashboard_actions.py d'afficher les messages réels déjà produits
    # par Progress (core.run_process) au lieu du texte statique
    # "Please wait...", sans changer la signature de cette fonction.
    self.launch_dialog_info_label = info
    dialog.present()


def update_launch_dialog_info(self, text: str):
    """Met à jour le texte de la popup de lancement en cours, si elle
    est encore affichée. Sans effet sinon (ex. popup déjà fermée entre
    deux appels asynchrones) — pas d'exception à gérer côté appelant.

    Le texte passe par le même nettoyage que la barre de statut du bas
    (clean_message() dans dashboard_status.py) avant affichage :
    suppression des codes ANSI bruts émis par wine/gamescope/vulkan
    (ex. "^[[38;5;208m..."), retrait du préfixe "stderr:". Sans ce
    nettoyage, les lignes de log brutes remontées par Progress
    s'affichaient illisibles dans la popup — voir StatusLabel dans
    dashboard_status.py, qui applique déjà ce nettoyage pour la barre
    de statut, réutilisé ici plutôt que dupliqué.

    Plafonné à LAUNCH_DIALOG_MAX_LINES lignes (popup petite, hauteur
    fixe), contre MAX_DISPLAY_LINES pour la barre de statut du bas.

    Prévu pour être appelé à fréquence modérée (throttlée en amont, cf.
    MIN_PROGRESS_UPDATE_INTERVAL dans core.py) : chaque appel ne fait
    qu'un set_text() sur un seul Gtk.Label, coût négligeable.
    """

    label = getattr(self, "launch_dialog_info_label", None)
    if label is None:
        return

    full_text, _level = clean_message(text)
    if not full_text:
        return  # message vide après nettoyage (ex. ligne blanche) : on garde l'affichage précédent

    display_text = cap_lines(full_text, max_lines=LAUNCH_DIALOG_MAX_LINES)
    label.set_text(display_text)


def hide_launch_dialog(self):
    """Close the launch dialog if it exists."""

    if getattr(self, "launch_dialog", None):
        self.launch_dialog.close()
        self.launch_dialog = None
        self.launch_dialog_info_label = None

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
    """Display a standard GTK4 information dialog."""

    dialog, box = _create_dialog(
        parent,
        title,
        message,
        "dialog-information-symbolic",
    )

    button_box = Gtk.Box(
        orientation=Gtk.Orientation.HORIZONTAL,
        spacing=8,
        halign=Gtk.Align.END,
    )

    close_button = Gtk.Button(label="Close")
    close_button.add_css_class("suggested-action")
    close_button.connect("clicked", lambda _b: dialog.close())

    button_box.append(close_button)
    box.append(button_box)

    dialog.present()


# =========================================================
# CONFIRMATION DIALOG
# =========================================================
def show_confirm(parent, title: str, message: str, callback):
    """Display a standard GTK4 confirmation dialog."""

    dialog, box = _create_dialog(
        parent,
        title,
        message,
        "dialog-question-symbolic",
    )

    button_box = Gtk.Box(
        orientation=Gtk.Orientation.HORIZONTAL,
        spacing=8,
        halign=Gtk.Align.END,
    )

    cancel_button = Gtk.Button(label="Cancel")
    ok_button = Gtk.Button(label="OK")

    ok_button.add_css_class("suggested-action")

    # Ensure callback is executed only once
    responded = False

    def _respond(value):
        nonlocal responded

        if responded:
            return

        responded = True
        callback(value)
        dialog.close()

    cancel_button.connect(
        "clicked",
        lambda _b: _respond(False),
    )

    ok_button.connect(
        "clicked",
        lambda _b: _respond(True),
    )

    # Closing the window is equivalent to Cancel
    def _on_close(_dialog):
        if not responded:
            _respond(False)
        return False

    dialog.connect("close-request", _on_close)

    button_box.append(cancel_button)
    button_box.append(ok_button)

    box.append(button_box)

    dialog.present()


# =========================================================
# ERROR DIALOG (UX SAFE)
# =========================================================
def show_error(parent, title: str, error: str):
    """Display a standard GTK4 error dialog."""

    dialog, box = _create_dialog(
        parent,
        title,
        error,
        "dialog-error-symbolic",
    )

    button_box = Gtk.Box(
        orientation=Gtk.Orientation.HORIZONTAL,
        spacing=8,
        halign=Gtk.Align.END,
    )

    close_button = Gtk.Button(label="Close")
    close_button.add_css_class("suggested-action")
    close_button.connect("clicked", lambda _b: dialog.close())

    button_box.append(close_button)
    box.append(button_box)

    dialog.present()
