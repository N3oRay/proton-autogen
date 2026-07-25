#!/usr/bin/env python3
import os
import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

from proton_autogen.ux.widgets.headerbar import DashboardHeaderBar
from proton_autogen.ux.widgets.toast import ToastOverlay
from proton_autogen.ux.recent_carousel import RecentCarousel
from proton_autogen.ux.favorites_carousel import FavoritesCarousel
from proton_autogen.ux.game_list import GameList


class DashboardUIMixin:
    """Construction de l'interface du Dashboard.
    Doit être mixé avec une classe qui expose self.games, self.lang,
    self.launch_game, self.edit_game, etc.
    """
    # -------------------------
    # UI
    # -------------------------
    def build_ui(self):
        overlay = self._build_overlay_and_background()
        root = self._build_root_container(overlay)

        self._build_header()
        self._build_stats(root)
        self._build_carousels(root)
        self._build_search(root)
        self._build_game_list(root)
        self._build_status_bar(root)
        # themes
        self.update_background(self.get_application().current_style)

    # -------------------------
    def _build_overlay_and_background(self):
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
        # TOAST OVERLAY
        # =========================
        self.toast = ToastOverlay()
        overlay.add_overlay(self.toast)

        return overlay
    # =========================
    # ROOT CONTAINER
    # =========================
    def _build_root_container(self, overlay):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
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
        wrapper.append(root)

        overlay.add_overlay(wrapper)
        return root
    # =========================
    # HEADER BAR (MODERN GTK4)
    # =========================
    def _build_header(self):
        header = DashboardHeaderBar(
            self.get_application(),
            on_refresh=lambda *_: self.refresh_games(),
            on_add=self.on_add_game,
            on_change_style=self.on_change_style,
            show_refresh=self.SHOW_REFRESH_BUTTON,
            show_add=self.SHOW_ADD_BUTTON,
        )
        self.set_titlebar(header)

    # =========================
    # GAME STATS
    # =========================
    def _build_stats(self, root):
        stats = self.build_global_stats(self.games)
        self.stats_label = Gtk.Label(
            label=f"🎮 {stats['total_games']} games  •  "
            f"⏱ {stats['hours']}h {stats['minutes']}m  •  "
            f"⭐ {stats['favorites']}"
        )
        self.stats_label.add_css_class("home-label")
        root.append(self.stats_label)

    # =========================
    # FAVORITES / RECENT GAMES COLLAPSE
    # =========================
    # QUICK CAROUSELS
    # =========================

    def _build_carousels(self, root):
        carousel_buttons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.favorites_btn = Gtk.Button(label="⭐ Favorites")
        self.recent_btn = Gtk.Button(label="🕘 Recently played")
        self.favorites_btn.add_css_class("section-toggle")
        self.recent_btn.add_css_class("section-toggle")
        carousel_buttons.append(self.favorites_btn)
        carousel_buttons.append(self.recent_btn)
        root.append(carousel_buttons)

        self.carousel_revealer = Gtk.Revealer()
        self.carousel_revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_DOWN)
        self.carousel_revealer.set_transition_duration(250)

        self.carousel_stack = Gtk.Stack()
        self.carousel_stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)

        # Favorites
        self.favorites_carousel = FavoritesCarousel(
            on_launch=self.launch_game, on_edit=self.edit_game, lang=self.lang
        )
        # Recent
        self.recent_carousel = RecentCarousel(
            on_launch=self.launch_game, on_edit=self.edit_game, lang=self.lang
        )

        self.carousel_stack.add_named(self.favorites_carousel, "favorites")
        self.carousel_stack.add_named(self.recent_carousel, "recent")
        self.carousel_revealer.set_child(self.carousel_stack)
        root.append(self.carousel_revealer)
        # état initial fermé
        self.carousel_revealer.set_reveal_child(False)

        self.favorites_btn.connect("clicked", self._on_show_favorites)
        self.recent_btn.connect("clicked", self._on_show_recent)

    def _on_show_favorites(self, _btn):
        self._toggle_carousel("favorites")

    def _on_show_recent(self, _btn):
        self._toggle_carousel("recent")

    def _toggle_carousel(self, name):
        if self.current_carousel == name and self.carousel_revealer.get_reveal_child():
            self.carousel_revealer.set_reveal_child(False)
            self.current_carousel = None
        else:
            self.current_carousel = name
            self.carousel_stack.set_visible_child_name(name)
            self.carousel_revealer.set_reveal_child(True)
        self.update_carousel_buttons()

    def _build_search(self, root):
        # =========================
        # GAME SEARCH
        # =========================
        self.search = Gtk.SearchEntry()
        self.search.set_placeholder_text("Search games...")
        self.search.connect("search-changed", self.on_search_changed)
        root.append(self.search)

    def _build_game_list(self, root):
        # =========================
        # GAME LIST
        # =========================
        self.game_list = GameList(
            on_launch=self.launch_game,
            on_edit=self.edit_game,
            on_delete=self.delete_game,
            on_refresh=self.refresh_games,
            on_export_lutris=self.export_lutris_handler,
            lang=self.lang,
        )
        self.game_list.set_vexpand(True)
        self.game_list.set_hexpand(True)
        self.game_list.set_halign(Gtk.Align.FILL)
        self.game_list.set_size_request(780, -1)
        root.append(self.game_list)

    def _build_status_bar(self, root):
        # =========================
        # STATUS BAR
        # =========================
        status_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.spinner = Gtk.Spinner()
        self.spinner.set_visible(False)

        self.status = Gtk.Label(label="Ready")
        #--------------------------------------------
        self.status.set_xalign(0)
        self.status.add_css_class("home-label")

        status_box.append(self.spinner)
        status_box.append(self.status)
        root.append(status_box)
