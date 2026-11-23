#!/usr/bin/env python3

# dashboard_proton_update.py
"""
Entrée de menu « Mise à jour Proton ».

  - ProtonPlus installé -> bouton « Ouvrir ProtonPlus » (avec son icône)
  - ProtonPlus absent   -> message + lien vers le GitHub du projet

Détection : binaire natif `protonplus` dans le PATH, ou Flatpak
com.vysp3r.ProtonPlus.

Trois morceaux, sur le modèle de dashboard_addux.py :
 - get_protonplus_command / find_protonplus_icon : logique pure (sans fenêtre) ;
 - DashboardProtonUpdateMixin : côté fenêtre (Dashboard) ;
 - register_proton_update_action : côté application, action `app.proton_update`
   (à appeler depuis _create_actions) ;
 - make_menu_item : Gio.MenuItem avec icône, utilisé par menu.py.
"""

import shutil
import subprocess
from pathlib import Path

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
from gi.repository import Gdk, Gio, Gtk

from proton_autogen.i18n import tr
from proton_autogen.utils.logger import StructuredLogger

logger = StructuredLogger("proton-autogen.ux.dashboard_proton_update")

ACTION_NAME = "proton_update"
PROTONPLUS_APP_ID = "com.vysp3r.ProtonPlus"
PROTONPLUS_GITHUB = "https://github.com/Vysp3r/ProtonPlus"

# 1) Icône du ProtonPlus installé (emplacement par défaut, puis exports Flatpak)
SYSTEM_ICON_CANDIDATES = (
    Path(f"/usr/share/icons/hicolor/256x256/apps/{PROTONPLUS_APP_ID}.png"),
    Path(f"/var/lib/flatpak/exports/share/icons/hicolor/256x256/apps/{PROTONPLUS_APP_ID}.png"),
    Path.home() / f".local/share/flatpak/exports/share/icons/hicolor/256x256/apps/{PROTONPLUS_APP_ID}.png",
    Path(f"/usr/share/icons/hicolor/scalable/apps/{PROTONPLUS_APP_ID}.svg"),
)

# 2) Icône embarquée dans proton-autogen (PNG par défaut), puis SVG,
#    puis emplacement d'origine
PROJECT_ICON_REL = Path("usr/share/icons/hicolor/scalable/apps")
PROJECT_ICON_NAMES = (
    f"{PROTONPLUS_APP_ID}.png",   # emplacement par défaut du projet
    f"{PROTONPLUS_APP_ID}.svg",
    "com_vysp3r_ProtonPlus.svg",  # fichier d'origine
)


# ------------------------------------------------------------------------------------
# DÉTECTION / ICÔNE (sans GTK, testable indépendamment)
# ------------------------------------------------------------------------------------

def get_protonplus_command():
    """Commande de lancement, ou None si ProtonPlus n'est pas installé."""
    if shutil.which("protonplus"):
        return ["protonplus"]

    if shutil.which("flatpak"):
        try:
            result = subprocess.run(
                ["flatpak", "info", PROTONPLUS_APP_ID],
                capture_output=True,
                timeout=3,
            )
            if result.returncode == 0:
                return ["flatpak", "run", PROTONPLUS_APP_ID]
        except (subprocess.SubprocessError, OSError):
            pass

    return None


def find_protonplus_icon():
    """Chemin de l'icône (Path) ou None.

    Ordre : icône système de ProtonPlus > icône embarquée dans
    usr/share/icons/hicolor/scalable/apps (en remontant depuis ce module) >
    emplacement d'origine (à côté de ce module)."""
    for path in SYSTEM_ICON_CANDIDATES:
        if path.is_file():
            return path

    here = Path(__file__).resolve()
    for parent in list(here.parents)[:5]:
        for name in PROJECT_ICON_NAMES:
            path = parent / PROJECT_ICON_REL / name
            if path.is_file():
                return path

    for name in PROJECT_ICON_NAMES:
        path = here.parent / name
        if path.is_file():
            return path

    return None


# ------------------------------------------------------------------------------------
# PARTIE GTK
# ------------------------------------------------------------------------------------

def build_protonplus_image(pixel_size=64):
    """Gtk.Image : fichier icône trouvé, sinon icône du thème, sinon générique."""
    path = find_protonplus_icon()
    if path is not None:
        image = Gtk.Image.new_from_file(str(path))
    else:
        theme = Gtk.IconTheme.get_for_display(Gdk.Display.get_default())
        name = (
            PROTONPLUS_APP_ID
            if theme.has_icon(PROTONPLUS_APP_ID)
            else "system-software-update-symbolic"
        )
        image = Gtk.Image.new_from_icon_name(name)
    image.set_pixel_size(pixel_size)
    return image


class DashboardProtonUpdateMixin:
    """Fenêtre « Mise à jour Proton ».

    Doit être mixé avec Dashboard (utilise self.toast et self.status s'ils
    existent)."""

    def show_proton_update_window(self):
        command = get_protonplus_command()

        window = Gtk.Window(
            title=tr("proton_update_title") or "Mise à jour Proton",
            transient_for=self,
            modal=True,
            default_width=420,
            resizable=False,
        )
        window.add_css_class("proton-update-window")

        root = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=14,
            margin_top=24,
            margin_bottom=24,
            margin_start=24,
            margin_end=24,
        )
        root.append(build_protonplus_image())

        if command:
            self._build_proton_update_installed(root, window, command)
        else:
            self._build_proton_update_missing(root)

        window.set_child(root)
        window.present()

    def _build_proton_update_installed(self, root, window, command):
        root.append(Gtk.Label(
            label=tr("proton_update_installed")
            or "Utilisez ProtonPlus pour installer ou mettre à jour "
               "vos versions de Proton.",
            wrap=True,
            justify=Gtk.Justification.CENTER,
        ))

        button = Gtk.Button(label=tr("proton_update_open") or "Ouvrir ProtonPlus")
        button.add_css_class("suggested-action")
        button.set_halign(Gtk.Align.CENTER)
        button.connect(
            "clicked", lambda _b: self._launch_protonplus(command, window)
        )
        root.append(button)

    def _build_proton_update_missing(self, root):
        root.append(Gtk.Label(
            label=tr("proton_update_missing")
            or "ProtonPlus n'est pas installé. Il permet de gérer "
               "facilement les versions de Proton. Cliquez ci-dessous "
               "pour l'installer.",
            wrap=True,
            justify=Gtk.Justification.CENTER,
        ))

        link = Gtk.LinkButton.new_with_label(
            PROTONPLUS_GITHUB,
            tr("proton_update_github") or "Installer ProtonPlus (GitHub)",
        )
        link.set_halign(Gtk.Align.CENTER)
        root.append(link)

    def _launch_protonplus(self, command, window):
        try:
            subprocess.Popen(
                command,
                start_new_session=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except OSError as exc:
            logger.error(f"Échec du lancement de ProtonPlus : {exc}")
            if hasattr(self, "toast"):
                self.toast.error(str(exc))
            return

        if hasattr(self, "status"):
            self.status.set_text(tr("proton_update_launched") or "ProtonPlus lancé")
        window.close()


# ------------------------------------------------------------------------------------
# ACTION (application) + ENTRÉE DE MENU
# ------------------------------------------------------------------------------------

def register_proton_update_action(app):
    """Enregistre `app.proton_update` ; à appeler depuis _create_actions."""
    action = Gio.SimpleAction.new(ACTION_NAME, None)

    def on_activate(_action, _param):
        # get_active_window() peut renvoyer une boîte de dialogue :
        # on cherche le tableau de bord lui-même.
        for win in app.get_windows():
            if hasattr(win, "show_proton_update_window"):
                win.show_proton_update_window()
                return

    action.connect("activate", on_activate)
    app.add_action(action)


def make_menu_item(label):
    """Gio.MenuItem « Mise à jour Proton » avec l'icône de ProtonPlus.

    Si la version de GTK n'affiche pas l'icône dans le popover, l'entrée
    reste fonctionnelle : l'icône est de toute façon dans la fenêtre."""
    item = Gio.MenuItem.new(label, f"app.{ACTION_NAME}")
    path = find_protonplus_icon()
    if path is not None:
        item.set_icon(Gio.FileIcon.new(Gio.File.new_for_path(str(path))))
    return item
