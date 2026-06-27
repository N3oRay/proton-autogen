#!/usr/bin/env python3

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

from proton_autogen.backend import edit_game


# -----------------------------
# GAME EDITOR WINDOW
# -----------------------------
class GameEditor(Gtk.Window):

    def __init__(self, app, game):
        super().__init__(application=app)
        self.set_title("Edit Game Profile")
        self.set_default_size(520, 420)
        #self.set_resizable(True)
        self.set_size_request(520, 420)

        self.game = game
        self.build_ui()

    # -------------------------
    # UI
    # -------------------------
    def build_ui(self):

        root = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=12,
            margin_top=12,
            margin_bottom=12,
            margin_start=12,
            margin_end=12
        )
        self.set_child(root)

        # -------------------------
        # TITLE
        # -------------------------
        title = Gtk.Label(label=self.game.get("name", "Game"))
        title.add_css_class("title-2")
        root.append(title)

        # -------------------------
        # PROFILE SELECT
        # -------------------------
        self.profile = Gtk.DropDown.new_from_strings([
            "dx11",
            "dx12",
            "oldgame",
            "launcher",
            "legacy",
            "ut99",
            "quake",
            "valve"
        ])
        self.profile.set_selected(0)
        root.append(self._row("Profile", self.profile))

        # -------------------------
        # PROTON SELECT (simplifié)
        # -------------------------
        self.proton = Gtk.Entry()
        self.proton.set_text(self.game.get("proton", "GE-Proton"))
        root.append(self._row("Proton", self.proton))

        # -------------------------
        # PREFIX MODE
        # -------------------------
        self.prefix = Gtk.DropDown.new_from_strings([
            "main",
            "shared",
            "auto",
            "custom"
        ])
        self.prefix.set_selected(0)
        root.append(self._row("Prefix", self.prefix))

        # -------------------------
        # TOGGLES
        # -------------------------
        self.mangohud = Gtk.CheckButton(label="Enable MangoHud")
        self.gamemode = Gtk.CheckButton(label="Enable GameMode")

        root.append(self.mangohud)
        root.append(self.gamemode)

        # -------------------------
        # SAVE BUTTON
        # -------------------------
        save_btn = Gtk.Button(label="Save")
        save_btn.connect("clicked", self.on_save)

        root.append(save_btn)

    # -------------------------
    # UI HELPERS
    # -------------------------
    def _row(self, label_text, widget):

        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        label = Gtk.Label(label=label_text, xalign=0)
        label.set_width_chars(10)

        row.append(label)
        row.append(widget)

        return row

    # -------------------------
    # SAVE LOGIC
    # -------------------------
    def on_save(self, _btn):

        profile_map = [
            "dx11",
            "dx12",
            "oldgame",
            "launcher",
            "legacy",
            "ut99",
            "quake",
            "valve"
        ]

        data = {
            "path": self.game["path"],
            "name": self.game.get("name"),
            "exe_type": profile_map[self.profile.get_selected()],
            "proton": self.proton.get_text(),
            "prefix": {
                "name": ["main", "shared", "auto", "custom"][self.prefix.get_selected()]
            },
            "features": {
                "mangohud": self.mangohud.get_active(),
                "gamemode": self.gamemode.get_active()
            }
        }

        try:
            edit_game(self.game["path"], data)
        except TypeError:
            edit_game(data)

        self.close()
