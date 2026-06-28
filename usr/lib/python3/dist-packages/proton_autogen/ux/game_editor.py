#!/usr/bin/env python3
#game_editor.py
import gi
import os
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk


from proton_autogen.backend import save_game_config
from proton_autogen.backend import find_all_protons
from proton_autogen.desc import set_tooltip


# -----------------------------
# GAME EDITOR WINDOW
# -----------------------------
class GameEditor(Gtk.Window):

    def __init__(self, app, game, lang):
        super().__init__(application=app)
        self.set_title("Edit Game Profile")
        self.set_default_size(520, 420)
        #self.set_resizable(True)
        self.on_saved = None
        self.set_size_request(520, 420)
        self.profile_model = [ "launcher", "dx11", "dx11Bnet", "dx12", "dx9", "dx9opengl", "oldgame", "valve", "ut3", "ut99", "legacy", "desktop"]
        self.prefix_model = ["main", "shared", "auto", "custom"]

        self.game = game
        self.lang = lang
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
        title.add_css_class("title-4")
        root.append(title)

        # -------------------------
        # PROFILE SELECT
        # -------------------------
        self.profile = Gtk.DropDown.new_from_strings(self.profile_model)

        current_profile = self.game.get("exe_type", "dx11")

        if current_profile in self.profile_model:
            self.profile.set_selected(self.profile_model.index(current_profile))

        root.append(self._row("Profile", self.profile))

        # -------------------------
        # PROTON SELECT (simplifié)
        # -------------------------
        #self.proton = Gtk.Entry()
        #self.proton.set_text(self.game.get("proton", "GE-Proton"))

        self.protons = find_all_protons()
        self.proton_names = [os.path.basename(p) for p in self.protons]
        self.proton = Gtk.DropDown.new_from_strings(self.protons)
        current = self.game.get("proton", "")
        if current in self.protons:
            self.proton.set_selected(self.protons.index(current))

        root.append(self._row("Proton", self.proton))

        # -------------------------
        # PREFIX MODE
        # -------------------------
        self.prefix = Gtk.DropDown.new_from_strings(self.prefix_model)
        set_tooltip(self.prefix, "prefix", self.lang)

        current_prefix = self.game.get("prefix", {}).get("name", "main")


        if current_prefix in self.prefix_model:
            self.prefix.set_selected(self.prefix_model.index(current_prefix))
        root.append(self._row("Prefix", self.prefix))

        # -------------------------
        # TOGGLES
        # -------------------------
        features = self.game.get("features", {})

        self.mangohud = Gtk.CheckButton(label="Enable MangoHud")
        self.mangohud.add_css_class("feature-toggle")
        self.mangohud.set_active(features.get("mangohud", False))
        set_tooltip(self.mangohud, "mangohud", self.lang)  #new code

        self.gamemode = Gtk.CheckButton(label="Enable GameMode")
        self.gamemode.add_css_class("feature-toggle")
        self.gamemode.set_active(features.get("gamemode", False))
        set_tooltip(self.gamemode, "gamemode", self.lang) #new code


        root.append(self.mangohud)
        root.append(self.gamemode)

        # -------------------------
        # SAVE BUTTON
        # -------------------------
        save_btn = Gtk.Button(label="Save configuration")
        save_btn.add_css_class("suggested-action")
        save_btn.connect("clicked", self.on_save)

        root.append(save_btn)

    # -------------------------
    # UI HELPERS
    # -------------------------
    def _row(self, label_text, widget):

        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        label = Gtk.Label(label=label_text, xalign=0)
        label.set_width_chars(10)
        label.add_css_class("dim-label")

        row.append(label)
        row.append(widget)

        return row

    # -------------------------
    # SAVE LOGIC
    # -------------------------

    def on_save(self, _btn):

        proton = ""
        if self.protons and self.proton.get_selected() >= 0:
            proton = self.protons[self.proton.get_selected()]

        exe_type = self.profile_model[self.profile.get_selected()] if self.profile.get_selected() >= 0 else "dx11"
        prefix = self.prefix_model[self.prefix.get_selected()] if self.prefix.get_selected() >= 0 else "main"

        data = {
            "path": self.game["path"],
            "name": self.game.get("name"),
            "exe_type": exe_type,
            "proton": proton,
            "prefix": {
                "name": prefix
            },
            "features": {
                "mangohud": self.mangohud.get_active(),
                "gamemode": self.gamemode.get_active()
            }
        }

        save_game_config(data)

        if self.on_saved:
            self.on_saved(data)

        self.close()
