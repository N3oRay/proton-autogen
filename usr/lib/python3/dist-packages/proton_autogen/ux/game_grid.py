#!/usr/bin/env python3
# game_grid.py

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, Gdk, Gio, GObject, GLib, Pango

from proton_autogen.stats import get_game_badges
from proton_autogen.i18n import tr, set_language
from proton_autogen.ux.icon_manager import load_game_icon


LUTRIS_EXPORT_ENABLED = True

# Bornes et pas du zoom clavier (Ctrl + / Ctrl -). DEFAULT_ICON_SIZE
# reprend la taille fixe d'origine (160px) comme point de départ.
MIN_ICON_SIZE = 48
MAX_ICON_SIZE = 208
ICON_SIZE_STEP = 16
DEFAULT_ICON_SIZE = 128

# Espacement pour les contrôles de la grille
GRID_CARD_SPACING = 64  # Espacement entre les cartes (64)
GRID_HORIZONTAL_PADDING = 12
GRID_MIN_COLUMNS = 1
GRID_MAX_COLUMNS = 7
GRID_CARD_EXTRA_HEIGHT = 50


class GridGameItem(GObject.GObject):
    """
    Wrapper GObject autour d'un dict 'game'.

    Gtk.GridView utilise un modèle Gio.ListModel, donc les dictionnaires
    de jeux sont encapsulés dans ce petit objet.
    """

    def __init__(self, game_data):
        super().__init__()
        self.data = game_data


class GameGrid(Gtk.Box):
    """
    Vue grille des jeux.

    API volontairement proche de GameList :

        set_games(games)
        refresh()
        update_game(game)

    Les actions sont déléguées au parent via les callbacks.
    """

    def __init__(
        self,
        on_launch=None,
        on_edit=None,
        on_delete=None,
        on_export_lutris=None,
        on_refresh=None,
        on_install=None,
        on_protondb=None,
        lang="en",
    ):
        super().__init__(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=6,
        )

        self.on_launch = on_launch
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_export_lutris = on_export_lutris
        self.on_install = on_install
        self.on_protondb = on_protondb
        self.refresh_games = on_refresh

        self.lang = lang
        set_language(self.lang)

        self.games = []
        self.path_index = {}

        # Taille d'icône courante, modifiable via zoom_in()/zoom_out().
        # Instance (pas classe) : chaque GameGrid a son propre zoom.
        self.icon_size = DEFAULT_ICON_SIZE

        # Cache pour éviter les recalculs inutiles
        self._last_grid_width = 0
        self._resize_timeout_id = None

        # ---------------------------------------------------------
        # TOOLBAR (ZOOM CONTROLS)
        # ---------------------------------------------------------

        toolbar = Gtk.Box(spacing=6)
        toolbar.set_halign(Gtk.Align.START)
        toolbar.add_css_class("game-grid-toolbar")

        # Bouton Zoom -
        zoom_out_btn = Gtk.Button(label=tr("zoom_out") or "−")
        zoom_out_btn.connect("clicked", lambda _: self.zoom_out())
        zoom_out_btn.add_css_class("section-toggle")
        toolbar.append(zoom_out_btn)

        # Bouton Zoom +
        zoom_in_btn = Gtk.Button(label=tr("zoom_in") or "+")
        zoom_in_btn.connect("clicked", lambda _: self.zoom_in())
        zoom_in_btn.add_css_class("section-toggle")
        toolbar.append(zoom_in_btn)

        # Label info taille
        self.size_label = Gtk.Label()
        self.size_label.set_margin_start(12)
        self.size_label.set_visible(False)
        self._update_size_label()
        toolbar.append(self.size_label)

        self.append(toolbar)

        # ---------------------------------------------------------
        # MODEL
        # ---------------------------------------------------------

        self.store = Gio.ListStore(item_type=GridGameItem)

        selection_model = Gtk.NoSelection(model=self.store)

        # ---------------------------------------------------------
        # FACTORY
        # ---------------------------------------------------------

        factory = Gtk.SignalListItemFactory()

        factory.connect("setup", self._on_setup)
        factory.connect("bind", self._on_bind)
        factory.connect("unbind", self._on_unbind)

        # ---------------------------------------------------------
        # GRID VIEW
        # ---------------------------------------------------------

        self.grid_view = Gtk.GridView(
            model=selection_model,
            factory=factory,
        )

        self.grid_view.add_css_class("game-grid")

        # Min/max colonnes
        self.grid_view.set_min_columns(GRID_MIN_COLUMNS)
        self.grid_view.set_max_columns(GRID_MAX_COLUMNS)
        self._last_grid_width = 0

        self.grid_view.set_single_click_activate(False)
        # Recalcule le nombre de colonnes lorsque la largeur
        # de la vue change.
        #self.connect("notify::width", self._on_grid_width_changed)
        self.grid_view.connect(
            "notify::width",
            self._on_grid_width_changed,
        )

        scroll = Gtk.ScrolledWindow()
        scroll.add_css_class("game-scroll")
        #scroll.set_policy(
        #    Gtk.PolicyType.NEVER,
        #    Gtk.PolicyType.AUTOMATIC,
        #)
        scroll.set_vexpand(True)
        scroll.set_hexpand(True)
        scroll.set_child(self.grid_view)

        self.append(scroll)

        # Le GridView n'a sa largeur réelle qu'après le premier layout GTK.
        GLib.idle_add(self._update_grid_columns)


    def _update_size_label(self):
        """Met à jour le label affichant la taille actuelle."""
        if hasattr(self, "size_label"):
            self.size_label.set_text(f"{self.icon_size}px")


    def _update_grid_columns(self):
        """Adapte le nombre de colonnes à la largeur disponible."""

        width = self.grid_view.get_width()

        if width <= 0:
            return

        # Taille réelle d'une carte = icône + spacing
        card_width = self.icon_size + GRID_CARD_SPACING

        # Espace disponible après les marges
        available_width = max(
            1,
            width - (2 * GRID_HORIZONTAL_PADDING)
        )

        # Nombre de colonnes : remplit l'espace au maximum
        columns = max(
            GRID_MIN_COLUMNS,
            int(available_width / card_width)
        )

        columns = min(GRID_MAX_COLUMNS, columns)

        # N'actualise que si nécessaire
        if columns == self._last_grid_width:
            return

        self._last_grid_width = columns

        self.grid_view.set_min_columns(columns)
        self.grid_view.set_max_columns(columns)

        # Force la relayout
        self.grid_view.queue_resize()


    def _on_grid_width_changed(self, *_):
        """
        Gère le redimensionnement de la fenêtre avec débouncing.
        """

        # Annule le timeout précédent si actif
        if self._resize_timeout_id is not None:
            GLib.source_remove(self._resize_timeout_id)

        # Débounce : recalcule après 100ms sans changement
        self._resize_timeout_id = GLib.timeout_add(
            100,
            self._update_grid_columns
        )


    # =============================================================
    # PUBLIC API
    # =============================================================

    def set_games(self, games):
        self.games = games or []
        self.refresh()

    def refresh(self):
        self.store.remove_all()
        self.path_index.clear()

        for index, game in enumerate(self.games):
            self.store.append(GridGameItem(game))

            path = game.get("path")
            if path:
                self.path_index[path] = index

    def update_game(self, updated_game):
        if not updated_game:
            return

        path = updated_game.get("path")

        if not path:
            return

        if path not in self.path_index:
            return

        index = self.path_index[path]

        item = self.store.get_item(index)

        if item is None:
            return

        item.data = updated_game

        # Force le re-bind de la cellule.
        self.store.items_changed(index, 1, 1)

    # =============================================================
    # ZOOM (raccourcis clavier Ctrl + / Ctrl -, voir dashboard.py)
    # =============================================================

    def zoom_in(self):
        self.set_icon_size(self.icon_size + ICON_SIZE_STEP)

    def zoom_out(self):
        self.set_icon_size(self.icon_size - ICON_SIZE_STEP)

    def set_icon_size(self, size):
        size = max(MIN_ICON_SIZE, min(MAX_ICON_SIZE, size))

        if size == self.icon_size:
            return

        self.icon_size = size
        self._update_size_label()
        self._refresh_after_zoom()


    def _refresh_after_zoom(self):
        scroll = self.grid_view.get_parent()
        vadj = scroll.get_vadjustment() if scroll else None

        old_value = vadj.get_value() if vadj else 0

        self.refresh()

        # Le zoom change la largeur minimale des cartes,
        # donc le nombre de colonnes doit être recalculé.
        self._update_grid_columns()

        self.grid_view.queue_resize()

        def restore_scroll():
            if vadj:
                upper = vadj.get_upper()
                page_size = vadj.get_page_size()
                maximum = max(0, upper - page_size)

                vadj.set_value(min(old_value, maximum))

            return False

        GLib.idle_add(restore_scroll)

    # =============================================================
    # FACTORY - SETUP
    # =============================================================

    def _on_setup(self, factory, list_item):
        """
        Construit une carte.

        Cette méthode n'est appelée qu'une fois par widget recyclé.
        Les données du jeu sont injectées dans _on_bind().
        """

        card = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=6,
        )

        card.add_css_class("game-grid-card")

        card.set_halign(Gtk.Align.CENTER)
        card.set_valign(Gtk.Align.START)
        card.set_hexpand(False)
        card.set_vexpand(False)

        # Taille de la carte : appliquée dynamiquement à chaque bind
        # (voir _apply_size), pas ici — _on_setup ne s'exécute qu'une
        # fois par ligne recyclée, alors que le zoom doit s'appliquer à
        # toutes les cartes déjà construites au moment du zoom.

        # ---------------------------------------------------------
        # ICON
        # ---------------------------------------------------------

        icon_holder = Gtk.Box()

        icon_holder.set_halign(Gtk.Align.CENTER)
        icon_holder.set_valign(Gtk.Align.CENTER)

        icon_holder.add_css_class("game-grid-icon-holder")

        # ---------------------------------------------------------
        # NAME
        # ---------------------------------------------------------

        title = Gtk.Label()
        title.set_halign(Gtk.Align.CENTER)
        title.set_hexpand(False)
        title.set_wrap(True)
        title.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
        title.set_justify(Gtk.Justification.CENTER)
        title.add_css_class("game-grid-title")

        # ---------------------------------------------------------
        # BADGES
        # ---------------------------------------------------------

        badges_box = Gtk.FlowBox()
        badges_box.set_orientation(Gtk.Orientation.HORIZONTAL)
        badges_box.set_halign(Gtk.Align.CENTER)
        badges_box.set_valign(Gtk.Align.CENTER)
        # Espacement entre les badges
        badges_box.set_row_spacing(2)
        badges_box.set_column_spacing(2)
        # Nombre maximum de badges par ligne
        badges_box.set_max_children_per_line(6)
        # Évite que FlowBox essaie de faire une seule ligne
        badges_box.set_min_children_per_line(2)
        badges_box.set_selection_mode(Gtk.SelectionMode.NONE)
        badges_box.add_css_class("game-grid-badges")

        # ---------------------------------------------------------
        # CARD CONTENT
        # ---------------------------------------------------------

        card.append(icon_holder)
        card.append(title)
        card.append(badges_box)

        # Données conservées sur la carte.
        card.icon_holder = icon_holder
        card.title_label = title
        card.badges_box = badges_box

        card.game = None

        # ---------------------------------------------------------
        # MOUSE - LEFT / RIGHT
        # ---------------------------------------------------------

        click = Gtk.GestureClick()

        # Bouton gauche.
        click.set_button(1)
        click.connect("pressed", self._on_left_click)
        card.add_controller(click)

        # Bouton droit.
        right_click = Gtk.GestureClick()
        right_click.set_button(3)
        right_click.connect("released", self._on_right_click)
        card.add_controller(right_click)

        list_item.set_child(card)

    # =============================================================
    # FACTORY - BIND
    # =============================================================

    def _on_bind(self, factory, list_item):
        item = list_item.get_item()
        card = list_item.get_child()

        if item is None or card is None:
            return

        game = item.data
        card.game = game

        size = self.icon_size
        # Taille du conteneur d'icône (responsive)
        card.icon_holder.set_size_request(size, size)
        # Titre : exactement la largeur de l'icône
        card.title_label.set_size_request(size, -1)
        card.badges_box.set_size_request(size, -1)

        # Icône
        icon = load_game_icon(game, size=size)

        icon.set_size_request(size, size)
        icon.set_halign(Gtk.Align.CENTER)
        icon.set_valign(Gtk.Align.CENTER)
        icon.add_css_class("game-grid-icon")

        old_icon = card.icon_holder.get_first_child()

        if old_icon:
            card.icon_holder.remove(old_icon)

        card.icon_holder.append(icon)

        # Nom
        card.title_label.set_text(game.get("name", "Unknown"))

        # Badges
        self._clear_box(card.badges_box)

        try:
            for badge in self._format_badges(game):
                card.badges_box.append(
                    self._create_badge(badge, game)
                )

        except Exception:
            pass


    # -------------------------
    # BADGES  protondb
    # -------------------------
    def _format_badges(self, game):
        badges = list(get_game_badges(game, self.lang))
        protondb_info = game.get("protondb")

        if protondb_info:
            badges.insert(0, {
                "type": "protondb",
                "label": f"{protondb_info.emoji}",
                "text": f"ProtonDB — confiance : {protondb_info.tier.upper()} - {protondb_info.confidence} ({protondb_info.total_votes} rapports)",
                "css": ["badge-protondb"],
            })

        return badges

    # =============================================================
    # FACTORY - UNBIND
    # =============================================================

    def _on_unbind(self, factory, list_item):
        card = list_item.get_child()

        if card is None:
            return

        card.game = None

    # =============================================================
    # MOUSE
    # =============================================================

    def _on_left_click(self, gesture, n_press, x, y):
        card = gesture.get_widget()

        if card is None:
            return

        game = getattr(card, "game", None)

        if not game:
            return

        # Un seul clic gauche = lancement.
        self._launch(game)

    def _on_right_click(self, gesture, n_press, x, y):
        card = gesture.get_widget()

        if card is None:
            return

        game = getattr(card, "game", None)

        if not game:
            return

        self._show_context_menu(card, game, x, y)

    # =============================================================
    # CONTEXT MENU
    # =============================================================

    def _show_context_menu(self, card, game, x, y):
        """
        Menu contextuel du jeu.

        Clic droit :
            Modifier
            Ajouter raccourci
            Exporter Lutris
            Supprimer de la liste
        """

        popover = Gtk.Popover()
        popover.add_css_class("game-grid-context-popover")

        popover.set_parent(card)
        popover.set_has_arrow(True)
        popover.set_autohide(True)

        # Position du menu par rapport au clic droit.
        rectangle = Gdk.Rectangle()

        rectangle.x = int(x)
        rectangle.y = int(y)
        rectangle.width = 1
        rectangle.height = 1

        popover.set_pointing_to(rectangle)

        menu_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=2,
        )
        menu_box.add_css_class("game-grid-context-menu")

        menu_box.set_margin_top(5)
        menu_box.set_margin_bottom(5)
        menu_box.set_margin_start(5)
        menu_box.set_margin_end(5)

        # ---------------------------------------------------------
        # EDIT
        # ---------------------------------------------------------

        edit_button = Gtk.Button(
            label=tr("edit")
        )

        edit_button.set_halign(Gtk.Align.FILL)
        edit_button.add_css_class("game-grid-menu-button")

        edit_button.connect(
            "clicked",
            lambda _button: self._menu_action(
                popover,
                self._edit,
                game,
            ),
        )

        menu_box.append(edit_button)

        # ---------------------------------------------------------
        # INSTALL SHORTCUT
        # ---------------------------------------------------------

        install_button = Gtk.Button(
            label=tr("install_shortcut")
        )

        install_button.set_halign(Gtk.Align.FILL)
        install_button.add_css_class("game-grid-menu-button")

        install_button.connect(
            "clicked",
            lambda _button: self._menu_action(
                popover,
                self._install,
                game,
            ),
        )

        menu_box.append(install_button)

        # ---------------------------------------------------------
        # PROTONDB
        # ---------------------------------------------------------

        protondb_button = Gtk.Button(
            label="📊 ProtonDB"
        )

        protondb_button.set_halign(Gtk.Align.FILL)
        protondb_button.add_css_class("game-grid-menu-button")
        protondb_button.set_sensitive(False) # deactiver pour le moment
        protondb_button.connect(
            "clicked",
            lambda _button: self._menu_action(
                popover,
                self._show_protondb,
                game,
            ),
        )

        menu_box.append(protondb_button)

        # ---------------------------------------------------------
        # LUTRIS
        # ---------------------------------------------------------

        if LUTRIS_EXPORT_ENABLED:
            export_button = Gtk.Button(
                label=tr("export_lutris")
            )

            export_button.set_halign(Gtk.Align.FILL)
            export_button.add_css_class("game-grid-menu-button")

            export_button.connect(
                "clicked",
                lambda _button: self._menu_action(
                    popover,
                    self._export_lutris,
                    game,
                ),
            )

            menu_box.append(export_button)

        # ---------------------------------------------------------
        # SEPARATOR
        # ---------------------------------------------------------

        separator = Gtk.Separator(
            orientation=Gtk.Orientation.HORIZONTAL
        )

        separator.set_margin_top(3)
        separator.set_margin_bottom(3)

        menu_box.append(separator)

        # ---------------------------------------------------------
        # DELETE
        # ---------------------------------------------------------

        delete_button = Gtk.Button(
            label=tr("remove_from_library")
        )

        delete_button.set_halign(Gtk.Align.FILL)
        delete_button.add_css_class("game-grid-menu-delete")

        delete_button.connect(
            "clicked",
            lambda _button: self._menu_action(
                popover,
                self._delete,
                game,
            ),
        )

        menu_box.append(delete_button)

        popover.set_child(menu_box)

        # Conserve la référence pendant que le popover est affiché.
        card._game_grid_popover = popover

        popover.connect(
            "closed",
            lambda _popover: self._popover_closed(card),
        )

        popover.popup()

    def _menu_action(self, popover, callback, game):
        popover.popdown()
        callback(game)

    def _popover_closed(self, card):
        try:
            card._game_grid_popover = None
        except Exception:
            pass

    # =============================================================
    # BADGES
    # =============================================================

    def _create_badge(self, badge, game=None):
        label = Gtk.Label(
            label=badge.get("label", "")
        )

        label.add_css_class("badge")

        css = badge.get("css")

        if isinstance(css, str):
            css = [css]

        if isinstance(css, list):
            for css_class in css:
                if isinstance(css_class, str):
                    css_class = css_class.strip()

                    if css_class:
                        label.add_css_class(css_class)

        tooltip = badge.get("text")

        if isinstance(tooltip, str) and tooltip.strip():
            label.set_tooltip_text(tooltip.strip())

        label.set_name(
            f"badge-{badge.get('type', 'unknown')}"
        )

        # Badge ProtonDB : cliquable, ouvre le dialogue de détail
        # (show_protondb_dialog côté Dashboard, via self.on_protondb).
        if badge.get("type") == "protondb" and game is not None:
            label.add_css_class("badge-clickable")
            label.set_cursor(Gdk.Cursor.new_from_name("pointer"))
            click = Gtk.GestureClick()
            click.connect("released", lambda *_: self._show_protondb(game))
            label.add_controller(click)

        return label

    # =============================================================
    # HELPERS
    # =============================================================

    @staticmethod
    def _clear_box(box):
        child = box.get_first_child()

        while child:
            next_child = child.get_next_sibling()
            box.remove(child)
            child = next_child

    # =============================================================
    # CALLBACKS
    # =============================================================

    def _delete(self, game):
        if self.on_delete:
            self.on_delete(game)

    def _export_lutris(self, game):
        if self.on_export_lutris:
            self.on_export_lutris(game)

    def _launch(self, game):
        if self.on_launch:
            self.on_launch(game)

    def _edit(self, game):
        if self.on_edit:
            self.on_edit(game)

    def _install(self, game):
        if self.on_install:
            self.on_install(game)

    def _show_protondb(self, game):
        if self.on_protondb:
            self.on_protondb(game)
