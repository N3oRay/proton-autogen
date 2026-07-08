#!/usr/bin/env python3

#dashboard.py
import os
import gi
import threading
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, Gdk, GLib

from proton_autogen.ux.game_list import GameList
from proton_autogen.ux.game_editor import GameEditor
from proton_autogen.ux.dialogs import open_game_file_dialog, show_launch_dialog, hide_launch_dialog
from proton_autogen.ux.menu import attach_menu
from proton_autogen.ux.themes import load_saved_theme, save_theme, AVAILABLE_THEMES, DEFAULT_THEME

from proton_autogen.ux.search import filter_games
from proton_autogen.notify import notifications
from proton_autogen.progress import Progress
from proton_autogen.editor import add_game_ux
from proton_autogen.backend import (
    run,
    list_programs_ux,
    get_diagnostic_text,
)

from proton_autogen.stats import is_recent_launch
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
        self.set_default_size(850, 900)
        self.set_size_request(850, 900)
        self.games = []
        self.lang = detect_help_env_lang()
        notifications.set_callback(self._notify_toast_ui)

        self.build_ui()
        self.refresh_games()

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
    # Show TOAST
    # -------------------------

    def _limit_toasts(self, max_toasts=5):
        children = []
        child = self._toast_box.get_first_child()

        while child:
            children.append(child)
            child = child.get_next_sibling()

        while len(children) > max_toasts:
            old = children.pop(0)
            old.unparent()

    def _notify_toast_ui(self, status, timeout=3):
        text = f"{status.get('title','')} — {status.get('message','')}"

        label = Gtk.Label(label=text)
        label.set_wrap(True)
        label.set_xalign(0)
        label.add_css_class("toast")

        frame = Gtk.Frame()
        frame.set_child(label)
        frame.add_css_class("toast-container")

        revealer = Gtk.Revealer()
        revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_DOWN)
        revealer.set_transition_duration(250)
        revealer.set_child(frame)
        #revealer.set_reveal_child(True)
        GLib.idle_add(lambda: revealer.set_reveal_child(True))

        # Limite 5
        self._toast_box.append(revealer)
        self._limit_toasts(5)

        def destroy_toast():
            revealer.set_reveal_child(False)

            def remove():
                if revealer.get_parent():
                    revealer.unparent()
                return False

            GLib.timeout_add(250, remove)
            return False

        GLib.timeout_add_seconds(timeout, destroy_toast)

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
        buffer.set_text(get_mangohud_advice())

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
        buffer.set_text(get_sensors_text())

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

        # -------------------------
        # COPY BUTTON
        # -------------------------
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

            # -----------------------------
            # 3. Export directory (XDG-friendly)
            # -----------------------------
            export_dir = Path.home() / ".local" / "share" / "proton-autogen" / "lutris_exports"
            export_dir.mkdir(parents=True, exist_ok=True)

            file_path = export_dir / f"{game_name}-lutris.yml"

            # -----------------------------
            # 4. Write file safely
            # -----------------------------
            file_path.write_text(yaml_text, encoding="utf-8")

            # -----------------------------
            # 5. UX feedback (better than print)
            # -----------------------------
            print(f"[OK] Export Lutris terminé: {file_path}")
            self.show_export_dialog(file_path)

            return str(file_path)

        except Exception as e:
            print(f"[ERROR] Export Lutris échoué: {e}")
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

        return {
            "total_games": total,
            "hours": hours,
            "minutes": minutes,
            "favorites": favorites,
        }

    def update_stats(self, games):
        stats = self.build_global_stats(games)

        self.stats_label.set_text(
            f"🎮 {stats['total_games']} games  •  "
            f"⏱ {stats['hours']}h {stats['minutes']}m  •  "
            f"⭐ {stats['favorites']}"
        )
        self.stats_label.add_css_class("home-label")


    def update_background(self, theme):
        base = os.path.dirname(__file__)

        backgrounds = {
            "fluent": "logo-pa.jpg",
            "adwaita": "logo-adwaita.jpg",
            "hellokit": "logo-hellokit.jpg",
        }

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
        self._toast_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self._toast_box.set_halign(Gtk.Align.CENTER)
        self._toast_box.set_valign(Gtk.Align.START)
        self._toast_box.set_margin_top(12)
        self._toast_box.set_spacing(6)

        overlay.add_overlay(self._toast_box)

        # =========================
        # HEADER BAR (MODERN GTK4)
        # =========================
        header = Gtk.HeaderBar()
        header.add_css_class("main-header")
        self.set_titlebar(header)

        # REFRESH
        if refreshbouton:
            refresh_btn = Gtk.Button(icon_name="view-refresh-symbolic")
            refresh_btn.set_tooltip_text("Refresh game list")
            refresh_btn.connect("clicked", lambda *_: self.refresh_games())

            header.pack_start(refresh_btn)

        # ADD GAME
        if addbouton:
            add_btn = Gtk.Button(label="+")
            #add_btn.set_sensitive(False)
            add_btn.add_css_class("suggested-action")
            add_btn.connect("clicked", self.on_add_game)
            header.pack_start(add_btn)

        # MENU BUTTON
        menu_btn = Gtk.MenuButton(label="☰")
        attach_menu(menu_btn, self.get_application())
        header.pack_end(menu_btn)



        # =========================
        # STYLE SWITCH BUTTON
        # =========================
        style_btn = Gtk.Button(icon_name="applications-graphics-symbolic")
        style_btn.set_tooltip_text("Change UI style")
        style_btn.add_css_class("app-button")
        style_btn.connect("clicked", self.on_change_style)

        header.pack_end(style_btn)

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
            on_refresh=self.refresh_games,
            on_export_lutris=self.export_lutris_handler,
            lang=self.lang
        )
        #self.game_list.set_on_refresh(self.refresh_games)

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

    # -------------------------
    # SEARCH
    # -------------------------
    def on_search_changed(self, entry):

        text = entry.get_text()

        games = filter_games(self.games, text)

        self.game_list.set_games(games)

        self.status.set_text(
            f"{len(games)} game(s)"
        )
        self.update_stats(games)


    # -------------------------
    # DATA
    # -------------------------
    def refresh_games(self):
        self.status.set_text("Loading games...")

        games = list_programs_ux(self.lang) or []

        # normalize safe format (future-proof)
        self.games = [
            {
                "name": g.get("name", "Unknown"),
                "path": g.get("path"),
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
        buffer.set_text(afficher_prerequis_label())

        scroll.set_child(textview)

        self.build_dialog(
            "Requis",
            scroll,
            width=700,
            height=650
        )

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
        buffer.set_text(get_about_text())

        scroll.set_child(textview)

        self.build_dialog(
            "About",
            scroll,
            width=700,
            height=650
        )
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
        buffer.set_text(get_help_text())

        scroll.set_child(textview)

        self.build_dialog(
            "Help",
            scroll,
            width=700,
            height=800
        )

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
        buffer.set_text(get_diagnostic_text())

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
            self.editor = None  # cleanup

        def on_close(_editor):
            self.status.set_text("Ready")

        editor.on_saved = after_save
        editor.connect("destroy", lambda *_: on_close(editor))
        editor.present()

    def on_add_game(self, _btn):
        open_game_file_dialog(self, self._on_file_selected)

    def _on_file_selected(self, path):
        if not path:
            return

        try:
            game = add_game_ux(path)

            self.status.set_text(
                f"{game['name']} added ✔"
            )

            self.refresh_games()

        except Exception as e:
            self.status.set_text(
                "Add game failed"
            )

            print("[UX] Add game error:", e)


# -----------------------------
# GTK APPLICATION
# -----------------------------
class ProtonAutogenApp(Gtk.Application):

    def __init__(self):
        super().__init__(application_id="com.proton.autogen")

        base = os.path.dirname(__file__)

        # CSS provider réutilisable
        self.css_provider = Gtk.CssProvider()

        # map des fichiers CSS (assure-toi que les fichiers existent dans assets/)
        style_map = {
            "fluent": os.path.join(base, "assets", "style.css"),
            "adwaita": os.path.join(base, "assets", "style_adwaita.css"),
            "hellokit": os.path.join(base, "assets", "hello-kit.css"),
        }
        self._style_map = style_map

        # charge le thème sauvegardé (ou défaut)
        saved = load_saved_theme()
        if saved not in AVAILABLE_THEMES:
            saved = DEFAULT_THEME
        self.current_style = saved

        # applique le thème initial
        self.apply_style(self.current_style)

    def apply_style(self, style_name):
        # path du CSS à appliquer
        path = self._style_map.get(style_name)
        if not path:
            return

        # enlève le provider précédent (si présent) pour éviter accumulations
        try:
            Gtk.StyleContext.remove_provider_for_display(
                Gdk.Display.get_default(),
                self.css_provider
            )
        except Exception:
            # ignore si non supporté / pas encore ajouté
            pass

        # recharge le provider avec le nouveau fichier
        try:
            self.css_provider.load_from_path(path)
        except Exception as e:
            # si échec, on loggue et on retourne
            print(f"[WARN] Echec chargement CSS {path}: {e}")
            return

        # ajoute le provider pour l'affichage (priorité application)
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            self.css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

        # met à jour l'état et sauvegarde le choix
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
