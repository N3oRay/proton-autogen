#!/usr/bin/env python3
import os
import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Pango

from proton_autogen.ux.widgets.headerbar import DashboardHeaderBar
from proton_autogen.ux.widgets.toast import ToastOverlay
from proton_autogen.ux.recent_carousel import RecentCarousel
from proton_autogen.ux.favorites_carousel import FavoritesCarousel
from proton_autogen.ux.game_list import GameList
from proton_autogen.ux.dashboard_status import StatusLabel
from proton_autogen.i18n import tr


class DashboardUIMixin:
    """Construction de l'interface du Dashboard.
    Doit être mixé avec une classe qui expose self.games, self.lang,
    self.launch_game, self.edit_game, etc.
    """
    # -------------------------
    # UI
    # -------------------------
    def build_ui(self):
        overlay = self._build_root_overlay()
        root = self._build_root_container(overlay)

        self._build_header()
        self._build_stats(root)
        self._build_carousels(root)
        self._build_search(root)
        self._build_game_list(root)
        self._build_status_bar(root)

        # Le toast est ajouté EN DERNIER : dans un Gtk.Overlay, les enfants
        # ajoutés via add_overlay() s'empilent dans leur ordre d'ajout, le
        # dernier étant peint par-dessus les autres. En l'ajoutant après le
        # wrapper (qui contient tout le contenu principal), on garantit que
        # le toast reste toujours au premier plan, quoi qu'on ajoute avant lui.
        self._build_toast(overlay)
        # themes
        self.update_background(self.get_application().current_style)

    # -------------------------
    def _build_root_overlay(self):
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

        return overlay

    def _build_toast(self, overlay):
        # =========================
        # TOAST OVERLAY (doit rester le dernier enfant ajouté à l'overlay)
        # =========================
        self.toast = ToastOverlay()
        overlay.add_overlay(self.toast)
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
        self.favorites_btn = Gtk.Button(label=f"⭐ {tr('favorites')}")
        self.recent_btn = Gtk.Button(label=f"🕘 {tr('recently_played')}")
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
        self.search.set_placeholder_text(tr("search_placeholder"))
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
            on_install=self.show_create_shortcut_dialog,   # <-- nouveau
            lang=self.lang,
        )
        self.game_list.set_vexpand(True)
        self.game_list.set_hexpand(True)
        self.game_list.set_halign(Gtk.Align.FILL)
        self.game_list.set_size_request(860, -1)
        root.append(self.game_list)

    def _update_stop_button_state(self, is_running: bool, game_name: str = None):
        """
        Appelé par DashboardActionsMixin (launch_game / stop_running_game)
        pour activer/désactiver et relabelliser le bouton Stop global.
        """
        self.stop_btn.set_visible(is_running)

        if is_running and game_name:
            self.stop_btn.set_label(f"■ {tr('stop_game')} — {game_name}")
        else:
            self.stop_btn.set_label(f"■ {tr('stop_game')}")

    # =========================
    # STATUS BAR + HISTORIQUE
    # =========================
    def _build_status_bar(self, root):
        status_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        status_box.add_css_class("status-box")
        self.spinner = Gtk.Spinner()
        self.spinner.set_visible(False)

        # StatusLabel se comporte comme un Gtk.Label classique pour tout
        # le code existant (self.status.set_text(...)), mais alimente en
        # plus un historique consultable (voir dashboard_status.py).
        self.status = StatusLabel(label=tr("ready"))
        self.status.set_xalign(0)
        self.status.add_css_class("home-label")
        self.status.set_hexpand(True)
        self.status.set_ellipsize(Pango.EllipsizeMode.END)

        # Bouton pour déplier/replier l'historique des messages
        self.status_history_btn = Gtk.ToggleButton()
        self.status_history_btn.set_icon_name("pan-up-symbolic")
        self.status_history_btn.add_css_class("section-toggle")
        self.status_history_btn.set_tooltip_text(tr("status_history_toggle"))
        self.status_history_btn.connect("toggled", self._on_toggle_status_history)

        # Bouton Stop global — visible seulement si un jeu tourne
        self.stop_btn = Gtk.Button(label="■ " + tr("stop_game"))
        self.stop_btn.add_css_class("section-toggle")
        self.stop_btn.set_visible(False)
        self.stop_btn.connect("clicked", self.on_stop_button_clicked)

        status_box.append(self.spinner)
        status_box.append(self.status)
        status_box.append(self.status_history_btn)
        status_box.append(self.stop_btn)
        root.append(status_box)

        self._build_status_history_panel(root)

    def _build_status_history_panel(self, root):
        # =========================
        # PANNEAU DÉROULANT D'HISTORIQUE
        # =========================
        self.status_history_revealer = Gtk.Revealer()
        self.status_history_revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_DOWN)
        self.status_history_revealer.set_transition_duration(200)

        panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        panel.add_css_class("status-history-panel")
        panel.set_margin_top(4)

        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        title = Gtk.Label(label=tr("status_history_title"), xalign=0)
        title.add_css_class("dim-label1")
        title.set_hexpand(True)

        clear_btn = Gtk.Button(label=tr("status_history_clear"))
        clear_btn.add_css_class("alternative-action")
        clear_btn.connect("clicked", self._on_clear_status_history)

        header.append(title)
        header.append(clear_btn)
        panel.append(header)

        self.status_history_list = Gtk.ListBox()
        self.status_history_list.set_selection_mode(Gtk.SelectionMode.NONE)
        self.status_history_list.add_css_class("status-history-list")

        scroll = Gtk.ScrolledWindow()
        scroll.set_min_content_height(140)
        scroll.set_max_content_height(220)
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_child(self.status_history_list)
        panel.append(scroll)

        self.status_history_revealer.set_child(panel)
        root.append(self.status_history_revealer)
        # état initial fermé
        self.status_history_revealer.set_reveal_child(False)

        # Rafraîchit la liste à chaque nouveau message / vidage
        self.status.connect("history-changed", self._on_status_history_changed)
        self._refresh_status_history_list()

    def _on_toggle_status_history(self, btn):
        expanded = btn.get_active()
        self.status_history_revealer.set_reveal_child(expanded)
        btn.set_icon_name("pan-down-symbolic" if expanded else "pan-up-symbolic")

    def _on_clear_status_history(self, _btn):
        self.status.clear_history()

    def _on_status_history_changed(self, _label):
        self._refresh_status_history_list()

    def _refresh_status_history_list(self):
        # Vide la liste actuelle
        child = self.status_history_list.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self.status_history_list.remove(child)
            child = next_child

        history = self.status.get_history()

        if not history:
            empty = Gtk.Label(label=tr("status_history_empty"), xalign=0)
            empty.add_css_class("dim-label2")
            empty.set_margin_top(6)
            empty.set_margin_bottom(6)
            empty.set_margin_start(4)
            self.status_history_list.append(empty)
            return

        for entry in history:
            self.status_history_list.append(self._build_status_history_row(entry))

    def _build_status_history_row(self, entry):
        row = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        row.set_margin_top(2)
        row.set_margin_bottom(2)
        row.set_margin_start(4)
        row.set_margin_end(4)

        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        time_label = Gtk.Label(label=entry.timestamp.strftime("%H:%M:%S"))
        time_label.add_css_class("dim-label2")
        time_label.set_width_chars(8)
        time_label.set_xalign(0)
        time_label.set_valign(Gtk.Align.START)

        text_label = Gtk.Label(label=entry.text, xalign=0)
        text_label.set_wrap(True)
        text_label.set_hexpand(True)
        text_label.add_css_class("status-history-entry")

        if entry.level == "error":
            text_label.add_css_class("status-history-error")
        elif entry.level == "success":
            text_label.add_css_class("status-history-success")

        header.append(time_label)
        header.append(text_label)
        row.append(header)

        # Message tronqué dans la barre (dump multi-lignes) : le texte
        # complet reste consultable derrière un "Détails" dépliable.
        if entry.has_more:
            expander = Gtk.Expander(label=tr("status_history_details"))
            expander.add_css_class("status-history-expander")

            detail_label = Gtk.Label(label=entry.full_text, xalign=0)
            detail_label.set_wrap(True)
            detail_label.set_selectable(True)
            detail_label.add_css_class("status-history-detail")
            detail_label.set_margin_top(4)
            detail_label.set_margin_start(16)

            expander.set_child(detail_label)
            row.append(expander)

        return row
