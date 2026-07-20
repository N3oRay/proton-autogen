#!/usr/bin/env python3
#game_list.py
import gi
import os
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, Gdk, Pango
from proton_autogen.stats import get_game_badges


lutris = True



# -----------------------------
# GAME LIST WIDGET
# -----------------------------
class GameList(Gtk.Box):

    def __init__(self, on_launch=None, on_edit=None, on_delete=None, on_export_lutris=None, on_refresh=None, lang="en"):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        self.on_launch = on_launch
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.lang = lang
        self.refresh_games = on_refresh
        self.row_map = {}  # path -> row
        self.on_export_lutris = on_export_lutris

        self.games = []

        self.list_box = Gtk.ListBox()
        self.list_box.add_css_class("game-list")
        self.list_box.set_selection_mode(Gtk.SelectionMode.NONE)

        scroll = Gtk.ScrolledWindow()
        scroll.add_css_class("game-scroll")
        scroll.set_vexpand(True)
        scroll.set_child(self.list_box)

        self.append(scroll)

    # -------------------------
    # UPDATE
    # -------------------------

    def update_game(self, updated_game):
        path = updated_game.get("path")
        if not path:
            return

        row = self.row_map.get(path)
        if not row:
            return

        # update text directly (LIVE UI)
        row.title_label.set_text(updated_game.get("name", "Unknown"))
        row.subtitle_label.set_text(self._format_subtitle(updated_game))
        row.subtitle1_label.set_text(self._format_subtitle_options(updated_game))
        row.subtitle2_label.set_text(self._format_subtitle_path(updated_game))

        # update stored game reference (important)
        row.game_data = updated_game
        # -------------------------
        # BADGES UPDATE
        # -------------------------
        if hasattr(row, "badges_box"):
            child = row.badges_box.get_first_child()

            while child:
                next_child = child.get_next_sibling()
                row.badges_box.remove(child)
                child = next_child

            #for b in updated_game.get("badges", []):
            #    row.badges_box.append(self._create_badge(b))

            badges = get_game_badges(updated_game, self.lang)
            for b in badges:
                row.badges_box.append(self._create_badge(b))


    # -------------------------
    # PUBLIC API
    # -------------------------
    def set_games(self, games):
        self.games = games
        self.refresh()

    def refresh(self):
        self.list_box.remove_all()
        self.row_map.clear()

        for game in self.games:
            row = self._create_row(game)
            self.list_box.append(row)

            self.row_map[game["path"]] = row

    # -------------------------
    # BADGES
    # -------------------------
    def _create_badge(self, b):
        label_text = b.get("label", "")
        label = Gtk.Label(label=label_text)
        label.add_css_class("badge")
        css = b.get("css")

        if isinstance(css, str):
            css = [css]

        if isinstance(css, list):
            for c in css:
                if isinstance(c, str) and c.strip():
                    label.add_css_class(c.strip())

        # -------------------------
        # Tooltip sécurisé
        # -------------------------
        tooltip = b.get("text")
        if isinstance(tooltip, str) and tooltip.strip():
            label.set_tooltip_text(tooltip.strip())

        # -------------------------
        # Accessibilité (bonus propre)
        # -------------------------
        label.set_name(f"badge-{b.get('type', 'unknown')}")

        return label

    # -------------------------
    # UI ROW
    # -------------------------
    def _create_row(self, game):

        row = Gtk.ListBoxRow()
        row.add_css_class("game-row")

        container = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=5
        )
        container.add_css_class("game-container")
        container.set_margin_top(6)
        container.set_margin_bottom(6)
        container.set_margin_start(1)
        container.set_margin_end(1)

        # -------------------------
        # LEFT INFO BLOCK
        # -------------------------
        info_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=2
        )
        info_box.set_hexpand(True)
        info_box.set_valign(Gtk.Align.CENTER)

        title = Gtk.Label(label=game.get("name", "Unknown"), xalign=0)
        title.set_halign(Gtk.Align.START)
        title.add_css_class("title-4")

        # -------------------------
        # BADGES ROW
        # -------------------------
        header_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=8
        )
        header_box.set_halign(Gtk.Align.START)


        badges_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=6
        )
        badges_box.set_halign(Gtk.Align.START)

        # -------------------------
        # subtitle ROW
        # -------------------------

        subtitle = Gtk.Label(label=self._format_subtitle(game), xalign=0)
        subtitle.set_halign(Gtk.Align.START)
        subtitle.add_css_class("dim-label1")

        subtitle1 = Gtk.Label(label=self._format_subtitle_options(game), xalign=0)
        subtitle1.set_halign(Gtk.Align.START)
        subtitle1.add_css_class("dim-label1")


        subtitle2 = Gtk.Label(label=self._format_subtitle_path(game), xalign=0)
        subtitle2.set_halign(Gtk.Align.START)
        subtitle2.set_wrap(True)
        subtitle2.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
        subtitle2.set_selectable(True)
        subtitle2.add_css_class("dim-label2")

        # -------------------------
        # STORE REFERENCES (IMPORTANT)
        # -------------------------
        row.title_label = title
        row.subtitle_label = subtitle
        row.subtitle1_label = subtitle1
        row.subtitle2_label = subtitle2
        row.game_path = game.get("path")
        # -------------------------
        # MAJ GAME (IMPORTANT)
        # -------------------------

        row.game_data = game

        # -------------------------
        # BUILD
        # -------------------------

        # -------------------------
        # BADGES
        # -------------------------
        row.badges_box = badges_box

        #badges = game.get("badges", [])
        badges = get_game_badges(game, self.lang)

        if badges:
            for b in badges:
                badges_box.append(self._create_badge(b))

        badges_box.add_css_class("badges")
        header_box.append(title)
        header_box.append(badges_box)

        info_box.append(header_box)
        info_box.append(subtitle)
        info_box.append(subtitle1)
        info_box.append(subtitle2)
        info_box.set_hexpand(True)
        info_box.set_size_request(300, -1)

        btn_delete = Gtk.Button()
        btn_delete.set_icon_name("user-trash-symbolic")
        btn_delete.add_css_class("btn-delete")
        btn_delete.set_tooltip_text("Remove game from library")
        btn_delete.set_valign(Gtk.Align.CENTER)
        btn_delete.connect(
            "clicked",
            lambda _btn, row=row: self._delete(row.game_data)
        )

        if lutris:
            btn_export = Gtk.Button(label="⇩")
            btn_export.set_icon_name("document-save-symbolic")
            btn_export.add_css_class("btn-export")
            btn_export.set_valign(Gtk.Align.CENTER)
            btn_export.set_size_request(18, 18)
            btn_export.set_tooltip_text("Export Lutris (.yml)")
            btn_export.connect(
                "clicked",
                lambda _btn, row=row: self._export_lutris(row.game_data)
            )

        btn_launch = Gtk.Button(label="▶")
        btn_launch.add_css_class("btn-launch")
        btn_launch.set_valign(Gtk.Align.CENTER)
        btn_launch.set_size_request(24, 18)
        btn_launch.connect(
            "clicked",
            lambda _btn, row=row: self._launch(row.game_data)
        )



        btn_edit = Gtk.Button(label="Edit")
        btn_edit.add_css_class("btn-edit")
        btn_edit.set_valign(Gtk.Align.CENTER)
        btn_edit.set_size_request(60, 18)
        btn_edit.connect(
            "clicked",
            lambda _btn, row=row: self._edit(row.game_data)
        )

        # -------------------------
        # IMPORTANT: PUSH BUTTONS TO RIGHT
        # -------------------------
        spacer0 = Gtk.Label(label="")
        spacer = Gtk.Label(label="")
        #spacer.set_hexpand(True)

        # -------------------------
        # ASSEMBLE
        # -------------------------
        container.append(info_box)
        container.append(btn_delete)
        if lutris:
            container.append(spacer0)
            container.append(btn_export)
            container.append(spacer)
        container.append(btn_edit)
        container.append(btn_launch)

        row.set_child(container)

        return row

    # -----------------------------
    # DELETE DISPLAY
    # -----------------------------
    def _delete(self, game):
        if self.on_delete:
            self.on_delete(game)
    # -----------------------------
    # Lutris DISPLAY
    # -----------------------------
    def _export_lutris(self, game):
        if self.on_export_lutris:
            self.on_export_lutris(game)

    # -----------------------------
    # FORMAT DISPLAY
    # -----------------------------
    def _format_subtitle(self, game):
        profile = game.get("exe_type", "auto")

        proton = game.get("proton", "")
        proton_name = os.path.basename(proton) if proton else "default"

        return f"Profile: {profile} | Proton: {proton_name}"

    def _format_subtitle_options(self, game):
        prefix = game.get("prefix", {}).get("name", "main")

        features = game.get("features", {})
        options = []

        if features.get("mangohud"):
            options.append("MangoHud")

        if features.get("gamemode"):
            options.append("GameMode")

        features_text = ", ".join(options) if options else "None"

        return f"Prefix: {prefix} | Features: {features_text}"

    def _format_subtitle_path(self, game):

        path = game.get("path", "")

        return f" {path}"

    # -----------------------------
    # CALLBACKS
    # -----------------------------
    def _launch(self, game):
        if self.on_launch:
            self.on_launch(game)

    def _edit(self, game):
        if self.on_edit:
            self.on_edit(game)
