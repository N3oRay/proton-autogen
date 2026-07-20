#!/usr/bin/env python3

#dashboard.py
import os
import gi
import threading
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, Gdk, GLib

from proton_autogen.ux.game_list import GameList
from proton_autogen.ux.game_editor import GameEditor
from proton_autogen.ux.widgets.headerbar import DashboardHeaderBar
from proton_autogen.ux.widgets.toast import ToastOverlay
from proton_autogen.ux.recent_carousel import RecentCarousel
from proton_autogen.ux.dialogs import open_game_file_dialog, show_launch_dialog, hide_launch_dialog
from proton_autogen.ux.themes import load_saved_theme, save_theme, AVAILABLE_THEMES, DEFAULT_THEME, BACKGROUND_THEMES, STYLE_CSS

from proton_autogen.ux.search import filter_games
from proton_autogen.notify import notifications
from proton_autogen.progress import Progress
from proton_autogen.editor import add_game_ux, rm_game_ux
from proton_autogen.backend import run, list_programs_ux, get_diagnostic_text
from proton_autogen.stats import is_recent_launch
from proton_autogen.color_label import insert_colored_text, insert_sensor_text, insert_about_text
from proton_autogen.core import print_about, get_about_text, detect_help_env_lang
from proton_autogen.info import print_help, get_help_text
from proton_autogen.sensor import get_sensors_text, print_sensors, get_mangohud_advice
from proton_autogen.requis import afficher_prerequis_label


addbouton = True
refreshbouton = True

# -----------------------------
# MAIN WINDOW
# -----------------------------
class Dashboard(Gtk.ApplicationWindow):

    def __init__(self, app):
        super().__init__(application=app)
        self.set_title("Proton-Autogen")
        self.set_icon_name("proton-autogen")
        self.set_default_size(930, 900)
        self.set_size_request(930, 900)
        self.games = []
        self.lang = detect_help_env_lang()
        notifications.set_callback(self.notify_toast)

        self.build_ui()
        self.refresh_games()

    # -------------------------
    # Notify Toast
    # -------------------------
    def notify_toast(self, status, timeout=3):

        self.toast.show(
            title=status.get("title", ""),
            message=status.get("message", ""),
            timeout=timeout,
        )

    # -------------------------
    # Progres Barre
    # -------------------------
    def progress_callback(self, percent, message):
        def update():
            self.status.set_text(
                f"{message} ({percent}%)"
            )
            return False

        GLib.idle_add(update)


    # -------------------------
    # Change Theme
    # -------------------------
    def on_change_style(self, _btn):
        app = self.get_application()
        # on fait défiler les thèmes
        if hasattr(app, "cycle_style"):
            app.cycle_style()
            # Changement du background
            self.update_background(app.current_style)
            # feedback rapide
            self.status.set_text(f"Style: {app.current_style}")
        else:
            # fallback ancien comportement
            if app.current_style == "fluent":
                app.apply_style("adwaita")
                self.status.set_text("Style: Adwaita")
            else:
                app.apply_style("fluent")
                self.status.set_text("Style: Proton Autogen")
            self.update_background(app.current_style)


    # -------------------------
    # Show MangoHud Sensors :
    # -------------------------
    def show_mangohud_advice_dialog(self):

        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_hexpand(True)

        textview = Gtk.TextView()
        textview.set_editable(False)
        textview.set_cursor_visible(False)
        textview.set_monospace(True)

        buffer = textview.get_buffer()
        insert_colored_text(buffer, get_mangohud_advice())

        scroll.set_child(textview)

        self.build_dialog(
            "MangoHud Config Advice",
            scroll,
            width=750,
            height=500
        )

    # -------------------------
    # Show Sensors :
    # -------------------------
    def show_sensors_dialog(self):

        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_hexpand(True)

        textview = Gtk.TextView()
        textview.set_editable(False)
        textview.set_cursor_visible(False)
        textview.set_monospace(True)

        buffer = textview.get_buffer()
        insert_sensor_text(buffer, get_sensors_text())

        scroll.set_child(textview)

        self.build_dialog(
            "Sensors",
            scroll,
            width=750,
            height=600
        )

    # -------------------------
    # MESSAGE DIAG:
    # -------------------------
    def show_export_dialog(self, file_path):
        file_path = str(file_path)

        win = Gtk.Window(
            transient_for=self,
            modal=True,
            title="Export Lutris terminé"
        )

        win.set_default_size(520, 180)
        win.set_destroy_with_parent(True)
        win.add_css_class("export-dialog")

        box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=12,
            margin_top=20,
            margin_bottom=20,
            margin_start=20,
            margin_end=20
        )

        # TITLE
        title = Gtk.Label(label="✔ Export Lutris terminé")
        title.add_css_class("export-title")
        box.append(title)

        # -------------------------
        # SELECTABLE PATH (SAFE)
        # -------------------------
        entry = Gtk.Entry()
        entry.set_text(file_path)
        entry.set_editable(False)
        entry.set_can_focus(True)
        entry.add_css_class("export-path")

        box.append(entry)

        # COPY BUTTON
        def copy_to_clipboard(_):
            display = Gdk.Display.get_default()
            clipboard = display.get_clipboard()
            clipboard.set(file_path)

        btn_copy = Gtk.Button(label="Copy path")
        btn_copy.connect("clicked", copy_to_clipboard)

        # CLOSE BUTTON
        btn_close = Gtk.Button(label="OK")
        btn_close.connect("clicked", lambda *_: win.close())

        buttons = Gtk.Box(spacing=8)
        buttons.append(btn_copy)
        buttons.append(btn_close)

        box.append(buttons)

        win.set_child(box)
        win.present()

    # -------------------------
    # EXPORT LUTRIS
    # -------------------------
    def export_lutris_handler(self, game):
        from proton_autogen.lutris import export_game_to_lutris_yaml
        from pathlib import Path
        import os
        import re

        try:
            # -----------------------------
            # 1. YAML generation
            # -----------------------------
            yaml_text = export_game_to_lutris_yaml(game)

            # -----------------------------
            # 2. Safe filename
            # -----------------------------
            def sanitize(name: str) -> str:
                name = name.strip()
                name = re.sub(r"[^\w\-_. ]", "_", name)
                name = name.replace(" ", "_")
                return name or "game"

            game_name = sanitize(game.get("name", "game"))

            # 3. Export directory (XDG-friendly)
            export_dir = Path.home() / ".local" / "share" / "proton-autogen" / "lutris_exports"
            export_dir.mkdir(parents=True, exist_ok=True)
            file_path = export_dir / f"{game_name}-lutris.yml"
            # 4. Write file safely
            file_path.write_text(yaml_text, encoding="utf-8")
            # 5. UX feedback (better than print)
            print(f"[OK] Export Lutris terminé: {file_path}")
            self.show_export_dialog(file_path)
            self.toast.success("Lutris export completed")

            return str(file_path)

        except Exception as e:
            print(f"[ERROR] Export Lutris échoué: {e}")
            self.toast.error("Lutris export failed")
            return None


    # -------------------------
    # STATS
    # -------------------------
    def build_global_stats(self, games):
        total = len(games)

        total_seconds = sum(
            g.get("playtime", {}).get("seconds", 0)
            for g in games
        )

        favorites = sum(g.get("favorite", False) for g in games)

        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60

        return { "total_games": total, "hours": hours, "minutes": minutes, "favorites": favorites, }

    def update_stats(self, games):
        stats = self.build_global_stats(games)

        self.stats_label.set_text( f"🎮 {stats['total_games']} games  •  " f"⏱ {stats['hours']}h {stats['minutes']}m  •  " f"⭐ {stats['favorites']}" )
        self.stats_label.add_css_class("home-label")


    def update_background(self, theme):
        base = os.path.dirname(__file__)

        backgrounds = BACKGROUND_THEMES

        filename = backgrounds.get(theme, "logo-pa.jpg")

        self.background.set_filename(
            os.path.join(base, "assets", filename)
        )

    # -------------------------
    # UI
    # -------------------------
    def build_ui(self):

        # =========================
        # OVERLAY
        # =========================
        overlay = Gtk.Overlay()
        self.set_child(overlay)
        self._overlay = overlay

        # =========================
        # BACKGROUND IMAGE
        # =========================
        base = os.path.dirname(__file__)
        self.background = Gtk.Picture.new_for_filename(
            os.path.join(base, "assets", "logo-pa.jpg")
        )

        self.background.set_content_fit(Gtk.ContentFit.COVER)
        self.background.set_hexpand(True)
        self.background.set_vexpand(True)

        overlay.set_child(self.background)

        # =========================
        # ROOT CONTAINER
        # =========================
        root = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=8,
        )

        root.set_vexpand(True)
        root.set_hexpand(True)
        root.set_halign(Gtk.Align.FILL)
        root.set_valign(Gtk.Align.FILL)

        root.set_margin_top(10)
        root.set_margin_bottom(10)
        root.set_margin_start(5)
        root.set_margin_end(10)
        root.add_css_class("style")

        # Le contenu est affiché au-dessus du fond
        wrapper = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        wrapper.set_halign(Gtk.Align.CENTER)
        wrapper.set_valign(Gtk.Align.FILL)
        wrapper.set_margin_start(0)
        wrapper.set_margin_end(0)
        wrapper.set_margin_top(0)
        wrapper.set_margin_bottom(0)
        wrapper.append(root)

        overlay.add_overlay(wrapper)

        # =========================
        # TOAST OVERLAY
        # =========================
        self.toast = ToastOverlay()
        overlay.add_overlay(self.toast)

        # =========================
        # HEADER BAR (MODERN GTK4)
        # =========================

        header = DashboardHeaderBar(
            self.get_application(),
            on_refresh=lambda *_: self.refresh_games(),
            on_add=self.on_add_game,
            on_change_style=self.on_change_style,
            show_refresh=refreshbouton,
            show_add=addbouton,
        )

        self.set_titlebar(header)


        # =========================
        # GAME STATS
        # =========================
        stats = self.build_global_stats(self.games)

        self.stats_label = Gtk.Label(
            label=f"🎮 {stats['total_games']} games  •  "
            f"⏱ {stats['hours']}h {stats['minutes']}m  •  "
            f"⭐ {stats['favorites']}"
        )

        self.stats_label.add_css_class("home-label")
        root.append(self.stats_label)

        # =========================
        # RECENT GAMES COLLAPSE
        # =========================

        recent_header = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=8
        )

        recent_btn = Gtk.Button( label="▼ Recently played" )
        recent_btn.add_css_class("section-toggle")
        self.recent_revealer = Gtk.Revealer()

        self.recent_revealer.set_transition_type(
            Gtk.RevealerTransitionType.SLIDE_DOWN
        )

        self.recent_revealer.set_transition_duration(
            250
        )


        self.recent_carousel = RecentCarousel(
            on_launch=self.launch_game,
            on_edit=self.edit_game,
            lang=self.lang
        )

        self.recent_carousel.set_vexpand(False)
        self.recent_revealer.set_child(
            self.recent_carousel
        )

        self.recent_carousel.set_vexpand(False)

        # état initial : True -> ouvert / False -> Fermer
        self.recent_revealer.set_reveal_child(False)


        def toggle_recent(_btn):

            visible = self.recent_revealer.get_reveal_child()

            self.recent_revealer.set_reveal_child(
                not visible
            )

            if visible:
                recent_btn.set_label( "▶ Recently played" )
            else:
                recent_btn.set_label( "▼ Recently played" )

        recent_btn.connect( "clicked", toggle_recent )
        recent_header.append( recent_btn )
        root.append( recent_header )
        root.append( self.recent_revealer )


        # =========================
        # GAME SEARCH
        # =========================
        self.search = Gtk.SearchEntry()
        self.search.set_placeholder_text("Search games...")

        self.search.connect(
            "search-changed",
            self.on_search_changed
        )

        root.append(self.search)

        # =========================
        # GAME LIST
        # =========================
        self.game_list = GameList(
            on_launch=self.launch_game,
            on_edit=self.edit_game,
            on_delete=self.delete_game,
            on_refresh=self.refresh_games,
            on_export_lutris=self.export_lutris_handler,
            lang=self.lang
        )

        self.game_list.set_vexpand(True)
        self.game_list.set_hexpand(True)
        self.game_list.set_halign(Gtk.Align.FILL)
        self.game_list.set_size_request(780, -1)
        root.append(self.game_list)

        # =========================
        # STATUS BAR
        # =========================
        self.status = Gtk.Label(label="Ready")
        self.status.set_xalign(0)
        self.status.add_css_class("home-label")

        root.append(self.status)
        # themes
        self.update_background(self.get_application().current_style)


    # -------------------------
    # STATS
    # -------------------------
    def activity_score(self, g):
        p = g.get("playtime", {})
        return (
            p.get("seconds", 0) * 0.3 +
            (1 if g.get("favorite") else 0) * 1000 +
            (is_recent_launch(p, 7) * 500)
        )

    # ---------------------------------
    # SEARCH Recent games for Caroussel
    # ---------------------------------
    def get_recent_games(self, games, limit=6):
        return sorted(
            games,
            key=self.activity_score,
            reverse=True
        )[:limit]

    # -------------------------
    # SEARCH
    # -------------------------
    def on_search_changed(self, entry):

        text = entry.get_text()
        games = filter_games(self.games, text)
        self.game_list.set_games(games)
        # Caroussel
        if hasattr(self, "recent_carousel"):
            self.recent_carousel.set_games(
                self.get_recent_games(
                    self.games,
                    6
                )
            )
        self.status.set_text(
            f"{len(games)} game(s)"
        )
        self.update_stats(games)


    # -------------------------
    # DATA
    # -------------------------
    def refresh_games(self):
        self.status.set_text("Loading games...")
        self.toast.info("Loading games...")

        games = list_programs_ux(self.lang) or []

        # normalize safe format (future-proof)
        self.games = [
            {
                "name": g.get("name", "Unknown"),
                "path": g.get("path"),
                "config_path": g.get("config_path"), #new
                "exe_type": g.get("exe_type", "dx11"),
                "proton": g.get("proton", ""),
                "prefix": g.get("prefix", {}),
                "features": g.get("features", {}),

                # 👇 AJOUT IMPORTANT
                "favorite": g.get("favorite", False),
                "playtime": g.get("playtime", {}),
                "badges": g.get("badges", []),
            }
            for g in games
            if isinstance(g, dict)
        ]

        if hasattr(self, "game_list"):
            #self.game_list.set_games(self.games)
            if hasattr(self, "search"):
                filtered = filter_games(
                    self.games,
                    self.search.get_text()
                )
            else:
                filtered = self.games

            self.game_list.set_games(filtered)
            self.update_stats(filtered)
            # Chargement du CAROUSEL
            if hasattr(self, "recent_carousel"):

                recent = self.get_recent_games(
                    self.games,
                    6
                )

                self.recent_carousel.set_games(
                    recent
                )

        if not self.games:
            self.status.set_text("No games found")
        else:
            self.status.set_text(f"{len(self.games)} games installed")

        if hasattr(self, "status"):
            self.status.add_css_class("label-bottom")

    # -------------------------
    # BUILD DIALOG
    # -------------------------

    def build_dialog(self, title, content_widget, width=600, height=800):

        win = Gtk.Window(
            title=title,
            transient_for=self,
            modal=True
        )

        win.add_css_class("style")
        win.set_default_size(width, height)

        overlay = Gtk.Overlay()
        win.set_child(overlay)

        base = os.path.dirname(__file__)

        logo = Gtk.Image.new_from_file(
            os.path.join(base, "assets", "logo-pa.jpg")
        )
        logo.set_opacity(0.06)

        overlay.set_child(logo)


        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        root.set_margin_top(10)
        root.set_margin_bottom(10)
        root.set_margin_start(10)
        root.set_margin_end(10)
        root.add_css_class("dialog-content")

        root.append(content_widget)

        overlay.add_overlay(root)

        win.present()

        return win


    # -------------------------
    # DIALOG REQUIS
    # -------------------------
    def show_requis_dialog(self):

        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_hexpand(True)

        textview = Gtk.TextView()
        textview.set_editable(False)
        textview.set_cursor_visible(False)
        textview.set_monospace(True)
        textview.set_left_margin(6)
        textview.set_right_margin(6)
        textview.set_wrap_mode(Gtk.WrapMode.WORD)

        buffer = textview.get_buffer()
        insert_colored_text(buffer, afficher_prerequis_label())
        #buffer.set_text(afficher_prerequis_label())

        scroll.set_child(textview)

        self.build_dialog( "Requis", scroll, width=700, height=650 )

    # -------------------------
    # DIALOG ABOUT
    # -------------------------
    def show_about_dialog(self):

        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_hexpand(True)

        textview = Gtk.TextView()
        textview.set_editable(False)
        textview.set_cursor_visible(False)
        textview.set_monospace(True)
        textview.set_left_margin(6)
        textview.set_right_margin(6)
        textview.set_wrap_mode(Gtk.WrapMode.WORD)

        buffer = textview.get_buffer()
        insert_about_text(buffer, get_about_text())

        scroll.set_child(textview)

        self.build_dialog( "About", scroll, width=700, height=750 )
    # -------------------------
    # DIALOG HELP
    # -------------------------
    def show_help_dialog(self):

        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_hexpand(True)

        textview = Gtk.TextView()
        textview.set_editable(False)
        textview.set_cursor_visible(False)
        textview.set_monospace(True)
        textview.set_wrap_mode(Gtk.WrapMode.WORD)
        textview.set_left_margin(8)
        textview.set_right_margin(8)
        textview.set_pixels_above_lines(2)
        textview.set_pixels_below_lines(2)

        buffer = textview.get_buffer()
        insert_colored_text(buffer, get_help_text())

        scroll.set_child(textview)

        self.build_dialog( "Help", scroll, width=700, height=800 )

    # -------------------------
    # DIALOG DIAGNOSTIC
    # -------------------------
    def show_diagnostic_dialog(self):

        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_hexpand(True)

        textview = Gtk.TextView()
        textview.set_editable(False)
        textview.set_cursor_visible(False)
        textview.set_monospace(True)
        textview.set_wrap_mode(Gtk.WrapMode.WORD)

        buffer = textview.get_buffer()
        insert_colored_text(buffer, get_diagnostic_text())
        #buffer.set_text(get_diagnostic_text())

        scroll.set_child(textview)

        self.build_dialog(
            "Diagnostic",
            scroll,
            width=800,
            height=750
        )


    # -------------------------
    # ACTIONS
    # -------------------------
    def _close_launch_dialog(self):
        hide_launch_dialog(self)
        self.set_sensitive(True)
        self.status.set_text("Ready")
        return False  # le timer ne se répète pas

    def launch_game(self, game):

        if not game.get("path"):
            return

        name = game.get("name", "Unknown")
        self.status.set_text(f"Launching {name}...")
        self.set_sensitive(False)
        show_launch_dialog(self, name)

        # Ferme automatiquement après 3 secondes
        GLib.timeout_add_seconds(3, self._close_launch_dialog)

        def worker():
            progress = Progress(
                callback=self.progress_callback
            )

            try:
                run(
                    game["path"],
                    progress=progress
                )

            except Exception as e:
                msg = str(e)
                GLib.idle_add(
                    lambda:
                        self.status.set_text(
                            f"Launch failed: {msg}"
                        )
                )
                print("[UX] Launch error:", e)

        threading.Thread(target=worker, daemon=True).start()


    def edit_game(self, game):
        editor = GameEditor(self.get_application(), game, self.lang)
        self.status.set_text("Updating...")

        def after_save(game):
            self.game_list.update_game(game)

            self.status.set_text(f"{game.get('name')} updated ✔")
            self.toast.success(f"{game.get('name')} updated")
            self.editor = None  # cleanup

        def on_close(_editor):
            self.status.set_text("Ready")

        editor.on_saved = after_save
        editor.connect("destroy", lambda *_: on_close(editor))
        editor.present()

    def on_add_game(self, _btn):
        open_game_file_dialog(self, self._on_file_selected)

    def delete_game(self, game):

        if rm_game_ux(
            game.get("path"),
            game.get("config_path")
        ):
            self.refresh_games()
            self.status.set_text(f"{game['name']} removed from library")
            self.toast.success(f"{game['name']} removed from library")
        else:
            self.status.set_text("Unable to remove game")
            self.toast.error("Unable to remove game")

    def _on_file_selected(self, path):
        if not path:
            return

        try:
            game = add_game_ux(path)
            self.status.set_text( f"{game['name']} added ✔" )
            self.refresh_games()
            self.toast.success(f"{game['name']} added")

        except Exception as e:
            self.status.set_text("Add game failed")
            self.toast.error("Unable to add game")

            print("[UX] Add game error:", e)


# -----------------------------
# GTK APPLICATION
# -----------------------------
class ProtonAutogenApp(Gtk.Application):

    def __init__(self):
        super().__init__(application_id="io.github.protonautogen")

        base = os.path.dirname(__file__)
        # CSS provider réutilisable
        self.css_provider = Gtk.CssProvider()
        # map des fichiers CSS (assure-toi que les fichiers existent dans assets/)
        style_map = STYLE_CSS
        self._style_map = style_map

        # charge le thème sauvegardé (ou défaut)
        saved = load_saved_theme()
        if saved not in AVAILABLE_THEMES:
            saved = DEFAULT_THEME
        self.current_style = saved

        # applique le thème initial
        self.apply_style(self.current_style)

    def apply_style(self, style_name):

        path = self._style_map.get(style_name)
        if not path:
            return

        display = Gdk.Display.get_default()
        if display is None:
            return

        # Retire l'ancien provider
        if hasattr(self, "css_provider") and self.css_provider:
            Gtk.StyleContext.remove_provider_for_display(
                display,
                self.css_provider
            )

        # Nouveau provider propre
        provider = Gtk.CssProvider()

        try:
            provider.load_from_path(path)
        except Exception as e:
            print(f"[WARN] CSS error {path}: {e}")
            return

        Gtk.StyleContext.add_provider_for_display(
            display,
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        self.css_provider = provider
        self.current_style = style_name

        save_theme(style_name)

    def cycle_style(self):
        # choisis l'indice suivant dans AVAILABLE_THEMES et applique
        try:
            idx = AVAILABLE_THEMES.index(self.current_style)
        except ValueError:
            idx = 0
        next_idx = (idx + 1) % len(AVAILABLE_THEMES)
        next_theme = AVAILABLE_THEMES[next_idx]
        self.apply_style(next_theme)

    def do_activate(self):
        self._create_actions()
        win = Dashboard(self)
        win.present()


    def _create_actions(self):

        # --------------------------
        # Mangohud SENSORS
        # -------------------------
        mgh = Gio.SimpleAction.new("mangohud", None)

        def open_mgh(*a):
            win = self.get_active_window()
            if win:
                win.show_mangohud_advice_dialog()

        mgh.connect("activate", open_mgh)
        self.add_action(mgh)

        # --------------------------
        # SENSORS
        # -------------------------
        sensors = Gio.SimpleAction.new("sensors", None)

        def open_sensors(*a):
            win = self.get_active_window()
            if win:
                win.show_sensors_dialog()

        sensors.connect("activate", open_sensors)
        self.add_action(sensors)

        # -------------------------
        # DIAGNOSTIC
        # -------------------------
        diag = Gio.SimpleAction.new("diag", None)

        def open_diag(*args):
            win = self.get_active_window()
            if win:
                win.show_diagnostic_dialog()

        diag.connect("activate", open_diag)
        self.add_action(diag)

        # -------------------------
        # HELP
        # -------------------------
        help_ = Gio.SimpleAction.new("help", None)

        def open_help(*a):
            win = self.get_active_window()
            if win:
                win.show_help_dialog()

        help_.connect("activate", open_help)
        self.add_action(help_)

        # -------------------------
        # ABOUT
        # -------------------------
        about = Gio.SimpleAction.new("about", None)

        def open_about(*a):
            win = self.get_active_window()
            if win:
                win.show_about_dialog()

        about.connect("activate", open_about)
        self.add_action(about)


        # -------------------------
        # Requis
        # -------------------------
        requis = Gio.SimpleAction.new("requis", None)

        def open_requis(*a):
            win = self.get_active_window()
            if win:
                win.show_requis_dialog()

        requis.connect("activate", open_requis)
        self.add_action(requis)

        # -------------------------
        # SHORTCUTS
        # -------------------------
        self.set_accels_for_action("app.diag", ["<Ctrl>D"])
        self.set_accels_for_action("app.help", ["F1"])
        self.set_accels_for_action("app.sensors", ["F2"])
        self.set_accels_for_action("app.mangohud", ["F3"])
        self.set_accels_for_action("app.requis", ["F4"])
        self.set_accels_for_action("app.about", ["F5"])


def start_dashboard():
    app = ProtonAutogenApp()
    app.run()
