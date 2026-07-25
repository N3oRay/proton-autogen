#!/usr/bin/env python3

#dashboard.py
import os
import gi
import threading
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, Gdk, GLib
from proton_autogen.ux.dashboard_ui import DashboardUIMixin
from proton_autogen.ux.dashboard_dialogs import DashboardDialogsMixin
from proton_autogen.ux.game_list import GameList
from proton_autogen.ux.game_editor import GameEditor
from proton_autogen.ux.widgets.headerbar import DashboardHeaderBar
from proton_autogen.ux.widgets.toast import ToastOverlay
from proton_autogen.ux.recent_carousel import RecentCarousel
from proton_autogen.ux.favorites_carousel import FavoritesCarousel
from proton_autogen.ux.dialogs import open_game_file_dialog, show_launch_dialog, hide_launch_dialog
from proton_autogen.ux.themes import load_saved_theme, save_theme, AVAILABLE_THEMES, DEFAULT_THEME, BACKGROUND_THEMES, STYLE_CSS

from proton_autogen.ux.search import filter_games
from proton_autogen.notify import notifications
from proton_autogen.progress import Progress
from proton_autogen.editor import add_game_ux, rm_game_ux
from proton_autogen.backend import run, list_programs_ux
from proton_autogen.stats import is_recent_launch

from proton_autogen.core import detect_help_env_lang
from proton_autogen.info import print_help


# -----------------------------
# MAIN WINDOW
# -----------------------------
class Dashboard(DashboardUIMixin, DashboardDialogsMixin, Gtk.ApplicationWindow):
    SHOW_ADD_BUTTON = True
    SHOW_REFRESH_BUTTON = True

    def __init__(self, app):
        super().__init__(application=app)
        self.set_title("Proton-Autogen")
        self.set_icon_name("proton-autogen")
        self.set_default_size(930, 900)
        self.set_size_request(930, 900)
        self.games = []
        self.current_carousel = None
        self.lang = detect_help_env_lang()
        notifications.set_callback(self.notify_toast)

        self.build_ui()   # vient du mixin
        self.refresh_games()

    # Notify Toast
    def notify_toast(self, status, timeout=3):

        self.toast.show(
            title=status.get("title", ""),
            message=status.get("message", ""),
            timeout=timeout,
        )

    # Progres Barre
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

    # update css carousel
    def update_carousel_buttons(self):
        self.favorites_btn.remove_css_class("suggested-action")
        self.recent_btn.remove_css_class("suggested-action")

        if self.current_carousel == "favorites":
            self.favorites_btn.add_css_class("suggested-action")
        elif self.current_carousel == "recent":
            self.recent_btn.add_css_class("suggested-action")



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


    def get_favorite_games(self, games, limit=6):

        return [
            g for g in games
            if g.get("favorite", False)
        ][:limit]

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
        self.spinner.set_visible(True)
        self.spinner.start()

        def worker():
            try:
                games = list_programs_ux(self.lang) or []
            except Exception as e:
                GLib.idle_add(self._on_refresh_error, str(e))
                return
            GLib.idle_add(self._on_games_loaded, games)

        threading.Thread(target=worker, daemon=True).start()


    def _on_refresh_error(self, error_msg):
        self.spinner.stop()
        self.spinner.set_visible(False)
        self.status.set_text("Erreur de chargement")
        self.toast.error(f"Échec du chargement des jeux : {error_msg}")
        return False


    def _on_games_loaded(self, games):
        self.spinner.stop()
        self.spinner.set_visible(False)

        self.games = [
            {
                "name": g.get("name", "Unknown"),
                "path": g.get("path"),
                "config_path": g.get("config_path"),
                "exe_type": g.get("exe_type", "dx11"),
                "proton": g.get("proton", ""),
                "prefix": g.get("prefix", {}),
                "features": g.get("features", {}),
                "favorite": g.get("favorite", False),
                "playtime": g.get("playtime", {}),
                "badges": g.get("badges", []),
            }
            for g in games
            if isinstance(g, dict)
        ]

        if hasattr(self, "game_list"):
            filtered = (
                filter_games(self.games, self.search.get_text())
                if hasattr(self, "search")
                else self.games
            )
            self.game_list.set_games(filtered)
            self.update_stats(filtered)

            if hasattr(self, "recent_carousel"):
                self.recent_carousel.set_games(self.get_recent_games(self.games, 6))
            if hasattr(self, "favorites_carousel"):
                self.favorites_carousel.set_games(self.get_favorite_games(self.games, 6))

        self.status.set_text(
            f"{len(self.games)} games installed" if self.games else "No games found"
        )
        self.status.add_css_class("label-bottom")
        return False





    # -------------------------
    # ACTIONS
    # -------------------------
    def _close_launch_dialog(self):
        hide_launch_dialog(self)
        self.set_sensitive(True)
        self.status.set_text("Ready")
        return False  # le timer ne se répète pas

    def launch_game(self, game):

        GLib.idle_add(self.spinner.start) # new code
        GLib.idle_add(self.spinner.set_visible, True) # new code

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
            finally:
                GLib.idle_add(self.spinner.stop)
                GLib.idle_add(self.spinner.set_visible, False)
                GLib.idle_add(self.status.set_text, "Ready")

        threading.Thread(target=worker, daemon=True).start()


    def edit_game(self, game):
        editor = GameEditor(self.get_application(), game, self.lang)
        self.status.set_text("Updating...")

        def after_save(game):
            #self.game_list.update_game(game)
            self.refresh_games()

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

        # Mangohud SENSORS
        mgh = Gio.SimpleAction.new("mangohud", None)

        def open_mgh(*a):
            win = self.get_active_window()
            if win:
                win.show_mangohud_advice_dialog()

        mgh.connect("activate", open_mgh)
        self.add_action(mgh)

        # SENSORS
        sensors = Gio.SimpleAction.new("sensors", None)

        def open_sensors(*a):
            win = self.get_active_window()
            if win:
                win.show_sensors_dialog()

        sensors.connect("activate", open_sensors)
        self.add_action(sensors)

        # DIAGNOSTIC
        diag = Gio.SimpleAction.new("diag", None)

        def open_diag(*args):
            win = self.get_active_window()
            if win:
                win.show_diagnostic_dialog()

        diag.connect("activate", open_diag)
        self.add_action(diag)

        # HELP
        help_ = Gio.SimpleAction.new("help", None)

        def open_help(*a):
            win = self.get_active_window()
            if win:
                win.show_help_dialog()

        help_.connect("activate", open_help)
        self.add_action(help_)

        # ABOUT
        about = Gio.SimpleAction.new("about", None)

        def open_about(*a):
            win = self.get_active_window()
            if win:
                win.show_about_dialog()

        about.connect("activate", open_about)
        self.add_action(about)

        # Requis
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
