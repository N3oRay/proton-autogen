#!/usr/bin/env python3
# game_list.py
import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Pango, GObject, Gio
from proton_autogen.stats import get_game_badges
from proton_autogen.i18n import tr, set_language
from proton_autogen.ux.icon_manager import load_game_icon

LUTRIS_EXPORT_ENABLED = True


class GameItem(GObject.GObject):
    """Wrapper GObject autour d'un dict 'game', requis par Gio.ListStore."""

    def __init__(self, game_data):
        super().__init__()
        self.data = game_data


class GameList(Gtk.Box):

    def __init__(self, on_launch=None, on_edit=None, on_delete=None,
                 on_export_lutris=None, on_refresh=None, on_install=None, lang="en"):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        self.on_launch = on_launch
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_export_lutris = on_export_lutris
        self.on_install = on_install   # <-- nouveau
        self.refresh_games = on_refresh
        self.lang = lang
        set_language(self.lang)

        self.games = []
        self.store = Gio.ListStore(item_type=GameItem)
        self.path_index = {}  # path -> index dans le store

        selection_model = Gtk.NoSelection(model=self.store)

        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", self._on_setup)
        factory.connect("bind", self._on_bind)
        factory.connect("unbind", self._on_unbind)

        self.list_view = Gtk.ListView(model=selection_model, factory=factory)
        self.list_view.add_css_class("game-list")

        scroll = Gtk.ScrolledWindow()
        scroll.add_css_class("game-scroll")
        scroll.set_vexpand(True)
        scroll.set_child(self.list_view)

        self.append(scroll)

    # -------------------------
    # PUBLIC API
    # -------------------------
    def set_games(self, games):
        self.games = games
        self.refresh()

    def refresh(self):
        self.store.remove_all()
        self.path_index.clear()

        for i, game in enumerate(self.games):
            self.store.append(GameItem(game))
            self.path_index[game.get("path")] = i

    def update_game(self, updated_game):
        path = updated_game.get("path")
        if not path or path not in self.path_index:
            return

        index = self.path_index[path]
        item = self.store.get_item(index)
        if item is None:
            return

        item.data = updated_game
        # Force le ré-affichage de cette ligne (déclenche unbind + bind)
        self.store.items_changed(index, 1, 1)

    # -------------------------
    # FACTORY: SETUP (construction des widgets, une fois par ligne recyclée)
    # -------------------------
    def _on_setup(self, factory, list_item):
        container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        container.add_css_class("game-container")
        container.set_margin_top(6)
        container.set_margin_bottom(6)
        container.set_margin_start(1)
        container.set_margin_end(1)

        left_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        left_box.set_valign(Gtk.Align.CENTER)

        icon_holder = Gtk.Box()  # l'icône réelle est injectée au bind (dépend du jeu)

        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        info_box.set_hexpand(True)
        info_box.set_valign(Gtk.Align.CENTER)
        info_box.set_size_request(300, -1)

        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        header_box.set_halign(Gtk.Align.START)

        title = self._make_label("", "title-4")
        badges_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        badges_box.set_halign(Gtk.Align.START)
        badges_box.add_css_class("badges")

        header_box.append(title)
        header_box.append(badges_box)

        subtitle = self._make_label("", "dim-label1")
        subtitle1 = self._make_label("", "dim-label1")
        subtitle2 = self._make_label("", "dim-label2", wrap=True)
        subtitle3 = self._make_label("", "dim-label2", wrap=True)

        info_box.append(header_box)
        info_box.append(subtitle)
        info_box.append(subtitle1)
        info_box.append(subtitle2)
        info_box.append(subtitle3)

        left_box.append(icon_holder)
        left_box.append(info_box)

        btn_delete = Gtk.Button()
        btn_delete.set_icon_name("user-trash-symbolic")
        btn_delete.add_css_class("btn-delete")
        btn_delete.set_tooltip_text(tr("remove_from_library"))
        btn_delete.set_valign(Gtk.Align.CENTER)

        btn_export = None
        if LUTRIS_EXPORT_ENABLED:
            btn_export = Gtk.Button()
            btn_export.set_icon_name("document-save-symbolic")
            btn_export.add_css_class("btn-export")
            btn_export.set_valign(Gtk.Align.CENTER)
            btn_export.set_size_request(18, 18)
            btn_export.set_tooltip_text(tr("export_lutris"))

        # bouton creation de raccourci bureau:
        btn_install = Gtk.Button()
        btn_install.set_icon_name("system-run-symbolic")
        btn_install.add_css_class("btn-install")
        btn_install.set_valign(Gtk.Align.CENTER)
        btn_install.set_size_request(24, 18)
        btn_install.set_tooltip_text(tr("install_shortcut"))

        # bouton launch:
        btn_launch = Gtk.Button(label="▶")
        btn_launch.add_css_class("btn-launch")
        btn_launch.set_valign(Gtk.Align.CENTER)
        btn_launch.set_size_request(24, 18)

        # bouton edit:
        btn_edit = Gtk.Button(label=tr("edit"))
        btn_edit.add_css_class("btn-edit")
        btn_edit.set_valign(Gtk.Align.CENTER)
        btn_edit.set_size_request(80, 18)

        container.append(left_box)
        container.append(btn_delete)
        if btn_export:
            container.append(Gtk.Label(label=""))
            container.append(btn_export)
            container.append(Gtk.Label(label=""))
        container.append(btn_install)      # <-- nouveau
        container.append(btn_edit)
        container.append(btn_launch)

        # Références gardées sur le container pour être réutilisées au bind()
        container.icon_holder = icon_holder
        container.title_label = title
        container.badges_box = badges_box
        container.subtitle_label = subtitle
        container.subtitle1_label = subtitle1
        container.subtitle2_label = subtitle2
        container.subtitle3_label = subtitle3
        container.btn_delete = btn_delete
        container.btn_export = btn_export
        container.btn_launch = btn_launch
        container.btn_install = btn_install     # <-- nouveau
        container.btn_edit = btn_edit
        container.handler_ids = {}  # signal handlers connectés au bind, à retirer à l'unbind

        list_item.set_child(container)

    # -------------------------
    # FACTORY: BIND (remplissage des données pour la ligne visible)
    # -------------------------
    def _on_bind(self, factory, list_item):
        item = list_item.get_item()
        container = list_item.get_child()
        game = item.data

        # ICON
        icon = load_game_icon(game, size=48)
        icon.set_size_request(48, 48)
        icon.add_css_class("game-icon")

        old_icon = container.icon_holder.get_first_child()
        if old_icon:
            container.icon_holder.remove(old_icon)
        container.icon_holder.append(icon)

        # TEXTE
        container.title_label.set_text(game.get("name", "Unknown"))
        container.subtitle_label.set_text(self._format_subtitle(game))
        container.subtitle1_label.set_text(self._format_subtitle_options(game))
        container.subtitle2_label.set_text(self._format_subtitle_path(game))
        container.subtitle3_label.set_text(self._format_subtitle_env(game))

        # BADGES
        child = container.badges_box.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            container.badges_box.remove(child)
            child = next_child

        for b in get_game_badges(game, self.lang):
            container.badges_box.append(self._create_badge(b))

        # CALLBACKS (connectés au bind, retirés à l'unbind pour éviter les doublons)
        container.handler_ids["delete"] = container.btn_delete.connect(
            "clicked", lambda _b: self._delete(item.data)
        )
        if container.btn_export:
            container.handler_ids["export"] = container.btn_export.connect(
                "clicked", lambda _b: self._export_lutris(item.data)
            )
        container.handler_ids["launch"] = container.btn_launch.connect(
            "clicked", lambda _b: self._launch(item.data)
        )
        container.handler_ids["edit"] = container.btn_edit.connect(
            "clicked", lambda _b: self._edit(item.data)
        )
        #nouveau bouton create shortcut install
        container.handler_ids["install"] = container.btn_install.connect(
            "clicked", lambda _b: self._install(item.data)
        )

    # -------------------------
    # FACTORY: UNBIND (nettoyage avant recyclage de la ligne)
    # -------------------------
    def _on_unbind(self, factory, list_item):
        container = list_item.get_child()
        if not container:
            return

        for name, btn in (
            ("delete", container.btn_delete),
            ("export", container.btn_export),
            ("install", container.btn_install),   # <-- nouveau
            ("launch", container.btn_launch),
            ("edit", container.btn_edit),
        ):
            handler_id = container.handler_ids.pop(name, None)
            if handler_id is not None and btn is not None:
                btn.disconnect(handler_id)

    # -------------------------
    # BADGES  protondb
    # -------------------------
    def _format_badges(self, game):
        badges = list(get_game_badges(game, self.lang))
        protondb_info = game.get("protondb")

        if protondb_info:
            badges.insert(0, {
                "type": "protondb",
                "label": f"{protondb_info.emoji} {protondb_info.tier.upper()}",
                "text": f"ProtonDB — confiance : {protondb_info.confidence} ({protondb_info.total_votes} rapports)",
                "css": ["badge-protondb"],
            })

        return badges

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

        tooltip = b.get("text")
        if isinstance(tooltip, str) and tooltip.strip():
            label.set_tooltip_text(tooltip.strip())

        label.set_name(f"badge-{b.get('type', 'unknown')}")
        return label

    def _make_label(self, text, css_class, wrap=False):
        label = Gtk.Label(label=text, xalign=0)
        label.set_halign(Gtk.Align.START)
        label.add_css_class(css_class)
        if wrap:
            label.set_wrap(True)
            label.set_wrap_mode(Pango.EllipsizeMode.MIDDLE)
            label.set_selectable(True)
        return label

    # -------------------------
    # FORMAT
    # -------------------------
    def _format_subtitle(self, game):
        profile = game.get("exe_type", "auto")
        proton = game.get("proton", "")
        proton_name = proton.split("/")[-1] if proton else "default"
        return f"Profile: {profile} | Proton: {proton_name}"

    def _format_subtitle_options(self, game):
        # Fix: game.get("prefix") peut valoir None (pas seulement absent)
        prefix = (game.get("prefix") or {}).get("name", "main")

        features = game.get("features", {})
        options = []
        if features.get("mangohud"):
            fps_limit = features.get("fps_limit")
            if fps_limit:
                options.append(f"MangoHud ({fps_limit} fps)")
            else:
                options.append("MangoHud")
        if features.get("gamemode"):
            options.append("GameMode")
        if features.get("gamescope"):
            options.append("GameScope")

        features_text = ", ".join(options) if options else "None"
        return f"Prefix: {prefix} | Features: {features_text}"

    def _format_subtitle_path(self, game):
        return game.get("path", "")

    def _format_subtitle_env(self, game):
        env = game.get("env", {}) or {}
        if not env:
            return ""

        pairs = ", ".join(f"{k}={v}" for k, v in env.items())
        return f"{tr('env_vars')}: {pairs}"

    # -------------------------
    # CALLBACKS
    # -------------------------
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
