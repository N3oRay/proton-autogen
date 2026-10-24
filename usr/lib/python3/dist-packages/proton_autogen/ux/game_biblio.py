#!/usr/bin/env python3
# game_biblio.py
"""
Vue « Bibliothèque » : une jaquette portrait (2:3) par jeu.

Principe
--------
GameBiblio hérite de GameGrid et ne remplace que la construction et le
remplissage des cartes (_on_setup / _on_bind / _on_unbind). Tout le reste est
réutilisé tel quel :

    - API publique : set_games(), refresh(), update_game()
    - zoom (zoom_in / zoom_out / set_icon_size) : ici, `icon_size` est la
      LARGEUR de la jaquette, la hauteur vaut largeur x COVER_RATIO
    - calcul du nombre de colonnes et debounce du redimensionnement
    - menu contextuel (clic droit, touche Menu, Maj+F10), callbacks
    - accessibilité : le clic gauche passe par un Gtk.Button focusable

Image de la carte
-----------------
    1. game["cover_image"] si l'utilisateur en a choisi une (game_editor.py)
    2. sinon, l'icône habituelle du jeu (load_game_icon) sur un fond dégradé

Le titre est superposé en bas de la jaquette, avec une étoile si le jeu est
en favori. Les jaquettes sont chargées hors du thread GTK (cover_manager) ;
en attendant, la carte affiche le repli.

Aucun fichier CSS ajouté au paquet : les styles sont embarqués ci-dessous,
volontairement neutres (couleurs en dur, aucune variable @accent) pour
rester lisibles sur les sept thèmes, et enregistrés avec une priorité
inférieure à celle des thèmes, qui peuvent donc les surcharger.
"""

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, Gdk, Pango

from proton_autogen.i18n import tr
from proton_autogen.ux import cover_manager
from proton_autogen.ux.game_grid import GameGrid
from proton_autogen.ux.icon_manager import load_game_icon


# Largeur de jaquette au premier affichage (le zoom Ctrl +/- l'ajuste ensuite
# entre MIN_ICON_SIZE et MAX_ICON_SIZE de game_grid.py).
DEFAULT_COVER_WIDTH = 144


_CSS = """
.game-biblio-card {
    padding: 4px;
}

.game-biblio-cover-button {
    padding: 0;
    min-width: 0;
    min-height: 0;
    border-radius: 10px;
}

.game-biblio-cover {
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.45);
}

.game-biblio-placeholder {
    background-image: linear-gradient(
        160deg,
        rgba(64, 76, 120, 0.95),
        rgba(20, 22, 38, 0.98)
    );
}

.game-biblio-title {
    color: #ffffff;
    font-weight: 600;
    padding: 22px 8px 8px 8px;
    background-image: linear-gradient(
        to top,
        rgba(0, 0, 0, 0.85),
        rgba(0, 0, 0, 0)
    );
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);
}

.game-biblio-star {
    color: #ffd54a;
    background-color: rgba(0, 0, 0, 0.55);
    border-radius: 999px;
    padding: 1px 6px;
    margin: 6px;
}

.game-biblio-cover-button:focus-visible {
    outline: 2px solid rgba(120, 170, 255, 0.95);
    outline-offset: 2px;
}
"""

_css_loaded = False


def _ensure_css():
    """Enregistre les styles de la vue, une seule fois par processus."""
    global _css_loaded

    if _css_loaded:
        return

    display = Gdk.Display.get_default()
    if display is None:
        return

    provider = Gtk.CssProvider()

    try:
        provider.load_from_string(_CSS)          # GTK >= 4.12
    except AttributeError:
        provider.load_from_data(_CSS.encode())   # GTK 4.0 - 4.10

    # APPLICATION - 1 : les thèmes (priorité APPLICATION) gardent le dernier mot.
    Gtk.StyleContext.add_provider_for_display(
        display,
        provider,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION - 1,
    )

    _css_loaded = True


class GameBiblio(GameGrid):
    """Vue Bibliothèque : grille de jaquettes personnalisables."""

    # Espacement horizontal entre cartes pour le calcul des colonnes
    # (GameGrid._update_grid_columns). Plus serré que la grille d'icônes,
    # dont la valeur de 64 px est pensée pour des cartes avec titre dessous.
    CARD_SPACING = 20

    def __init__(self, *args, **kwargs):
        _ensure_css()

        super().__init__(*args, **kwargs)

        self.add_css_class("game-biblio")
        self.grid_view.add_css_class("game-biblio-view")

        # Largeur de départ propre à cette vue (le zoom reste indépendant
        # de celui de la grille d'icônes : chaque instance a son icon_size).
        self.icon_size = DEFAULT_COVER_WIDTH
        self._update_size_label()

    # -----------------------------------------------------------------
    # Géométrie
    # -----------------------------------------------------------------

    def _cover_size(self):
        width = self.icon_size
        height = int(width * cover_manager.COVER_RATIO)
        return width, height

    # =================================================================
    # FACTORY - SETUP
    # =================================================================

    def _on_setup(self, factory, list_item):
        """Construit une carte (une fois par widget recyclé)."""

        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        card.add_css_class("game-biblio-card")
        card.set_halign(Gtk.Align.CENTER)
        card.set_valign(Gtk.Align.START)
        card.set_hexpand(False)
        card.set_vexpand(False)

        # Gtk.Button plutôt que Box + GestureClick : focusable au Tab,
        # activable à Entrée/Espace, rôle « bouton » pour Orca (même choix
        # que GameGrid).
        button = Gtk.Button()
        button.set_has_frame(False)
        button.add_css_class("flat")
        button.add_css_class("game-biblio-cover-button")
        button.set_halign(Gtk.Align.CENTER)
        button.set_valign(Gtk.Align.CENTER)
        button.set_cursor(Gdk.Cursor.new_from_name("pointer"))

        # Menu contextuel au clavier (touche Menu / Maj+F10) : géré par
        # GameGrid._on_icon_key_pressed, qui lit button.card / card.game.
        key_controller = Gtk.EventControllerKey()
        key_controller.connect("key-pressed", self._on_icon_key_pressed)
        button.add_controller(key_controller)

        # --- Jaquette : pile « cover » (image) / « placeholder » (repli) ---
        stack = Gtk.Stack()
        stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        stack.set_transition_duration(120)

        picture = Gtk.Picture()
        picture.set_content_fit(Gtk.ContentFit.COVER)
        picture.set_can_shrink(True)
        stack.add_named(picture, "cover")

        placeholder = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        placeholder.add_css_class("game-biblio-placeholder")
        stack.add_named(placeholder, "placeholder")

        # --- Superpositions : titre en bas, étoile favori en haut à droite ---
        overlay = Gtk.Overlay()
        overlay.add_css_class("game-biblio-cover")
        # Arrondit réellement l'image (sans overflow, le radius CSS ne
        # découpe pas le contenu enfant).
        overlay.set_overflow(Gtk.Overflow.HIDDEN)
        overlay.set_child(stack)

        title = Gtk.Label()
        title.add_css_class("game-biblio-title")
        title.set_halign(Gtk.Align.FILL)
        title.set_valign(Gtk.Align.END)
        title.set_xalign(0.5)
        title.set_justify(Gtk.Justification.CENTER)
        title.set_wrap(True)
        title.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
        title.set_lines(2)
        title.set_ellipsize(Pango.EllipsizeMode.END)
        overlay.add_overlay(title)

        star = Gtk.Label(label="★")
        star.add_css_class("game-biblio-star")
        star.set_halign(Gtk.Align.END)
        star.set_valign(Gtk.Align.START)
        star.set_visible(False)
        overlay.add_overlay(star)

        button.set_child(overlay)
        card.append(button)

        # Attributs lus par les méthodes héritées de GameGrid
        # (_on_icon_activated, _on_icon_key_pressed, _on_right_click, ...).
        card.icon_holder = button
        card.title_label = title
        card.game = None
        button.card = card

        # Attributs propres à GameBiblio.
        card.cover_stack = stack
        card.cover_picture = picture
        card.cover_placeholder = placeholder
        card.cover_star = star
        card.cover_key = None   # clé de la jaquette attendue (anti-recyclage)

        # Clic gauche / Entrée / Espace = lancement.
        button.connect("clicked", self._on_icon_activated)

        # Clic droit = menu contextuel.
        right_click = Gtk.GestureClick()
        right_click.set_button(3)
        right_click.connect("released", self._on_right_click)
        card.add_controller(right_click)

        list_item.set_child(card)

    # =================================================================
    # FACTORY - BIND / UNBIND
    # =================================================================

    def _on_bind(self, factory, list_item):
        item = list_item.get_item()
        card = list_item.get_child()

        if item is None or card is None:
            return

        game = item.data
        card.game = game

        width, height = self._cover_size()
        card.icon_holder.set_size_request(width, height)
        card.cover_stack.set_size_request(width, height)

        game_name = game.get("name", "Unknown")
        card.title_label.set_text(game_name)
        card.cover_star.set_visible(bool(game.get("favorite")))

        card.icon_holder.update_property(
            [Gtk.AccessibleProperty.LABEL],
            [game_name],
        )
        card.icon_holder.set_tooltip_text(
            f"{game_name}\n"
            f"{tr('shortcuts_grid_launch') or 'Entrée / Espace : lancer'}\n"
            f"{tr('shortcuts_grid_menu') or 'Menu ou Maj+F10 : options'}"
        )

        self._apply_cover(card, game, width, height)

    def _on_unbind(self, factory, list_item):
        card = list_item.get_child()

        if card is not None:
            # Une jaquette qui arrive après le recyclage de la carte sera
            # ignorée par _on_cover_ready.
            card.cover_key = None

        super()._on_unbind(factory, list_item)

    # -----------------------------------------------------------------
    # Jaquette
    # -----------------------------------------------------------------

    def _apply_cover(self, card, game, width, height):
        cover = game.get("cover_image")

        if not cover:
            card.cover_key = None
            self._show_placeholder(card, game, width)
            return

        key = (cover, width, height)
        card.cover_key = key

        texture = cover_manager.request_cover(
            cover,
            width,
            height,
            lambda tex, _card=card, _key=key: self._on_cover_ready(_card, _key, tex),
        )

        if texture is not None:
            self._show_cover(card, texture)
        else:
            # Chargement en cours (ou fichier illisible) : repli visible.
            self._show_placeholder(card, game, width)

    def _on_cover_ready(self, card, key, texture):
        # La carte a été recyclée pour un autre jeu (ou une autre taille de
        # zoom) pendant le chargement : ne rien afficher.
        if card.cover_key != key or texture is None:
            return

        self._show_cover(card, texture)

    @staticmethod
    def _show_cover(card, texture):
        card.cover_picture.set_paintable(texture)
        card.cover_stack.set_visible_child_name("cover")

    @staticmethod
    def _show_placeholder(card, game, width):
        box = card.cover_placeholder

        child = box.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            box.remove(child)
            child = next_child

        icon = load_game_icon(game, size=max(32, width // 2))
        icon.set_halign(Gtk.Align.CENTER)
        icon.set_valign(Gtk.Align.CENTER)
        icon.set_hexpand(True)
        icon.set_vexpand(True)
        box.append(icon)

        card.cover_stack.set_visible_child_name("placeholder")
