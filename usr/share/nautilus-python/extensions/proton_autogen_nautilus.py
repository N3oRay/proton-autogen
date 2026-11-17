"""Extension Nautilus : entrées de clic droit pour proton-autogen.

 - « Ouvrir avec Proton-Autogen » : lance le programme (comportement existant)
 - « Ajouter à Proton-Autogen »   : `proton-autogen addux <fichier>` (add + UX)

Compatible nautilus-python 3.0 (Nautilus < 43) et 4.0 (GTK4, Nautilus >= 43).
"""
import os
import shutil
import subprocess

import gi

try:
    gi.require_version("Nautilus", "4.0")
except ValueError:
    gi.require_version("Nautilus", "3.0")

from gi.repository import GObject, Nautilus

EXTS = (".exe", ".msi", ".bat", ".lnk")

_LABELS = {
    "en": ("Open with Proton-Autogen", "Add to Proton-Autogen"),
    "fr": ("Exécuter avec Proton-Autogen", "Ajouter à Proton-Autogen"),
}


def _labels():
    lang = (os.environ.get("LANGUAGE") or os.environ.get("LANG") or "en")[:2]
    return _LABELS.get(lang, _LABELS["en"])


def _binary():
    return shutil.which("proton-autogen") or "/usr/bin/proton-autogen"


class ProtonAutogenExtension(GObject.GObject, Nautilus.MenuProvider):

    @staticmethod
    def _spawn(*args):
        # Liste d'arguments (jamais de shell) : chemins avec espaces sûrs.
        subprocess.Popen(
            [_binary(), *args],
            stdin=subprocess.DEVNULL,
            start_new_session=True,
        )

    def _on_run(self, _menu, path):
        self._spawn(path)

    def _on_addux(self, _menu, path):
        self._spawn("addux", path)

    def get_file_items(self, *args):
        # 3.0 : (window, files) ; 4.0 : (files,) -> la liste est toujours en dernier.
        files = args[-1]
        if len(files) != 1:
            return []

        f = files[0]
        if f.get_uri_scheme() != "file" or not f.get_name().lower().endswith(EXTS):
            return []

        path = f.get_location().get_path()
        label_run, label_add = _labels()

        run_item = Nautilus.MenuItem(
            name="ProtonAutogen::Open",
            label=label_run,
            tip="Run this program using Proton or Wine fallback",
        )
        run_item.connect("activate", self._on_run, path)

        add_item = Nautilus.MenuItem(
            name="ProtonAutogen::AddUx",
            label=label_add,
            tip="Register this program in Proton-Autogen and open the UX",
        )
        add_item.connect("activate", self._on_addux, path)

        return [run_item, add_item]
