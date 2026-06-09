from gi.repository import Nautilus, GObject
import subprocess
import os

class ProtonAutogenExtension(GObject.GObject, Nautilus.MenuProvider):

    def run_proton(self, file_path):
        subprocess.Popen(["/usr/bin/proton-autogen", file_path])

    def menu_activate(self, menu, file):
        self.run_proton(file.get_location().get_path())

    def get_file_items(self, window, files):
        if len(files) != 1:
            return

        file = files[0]
        if not file.get_name().lower().endswith(".exe"):
            return

        item = Nautilus.MenuItem(
            name="ProtonAutogenOpen",
            label="Open with Proton-Autogen",
            tip="Run this .exe using Proton or Wine fallback"
        )

        item.connect("activate", self.menu_activate, file)

        return [item]
