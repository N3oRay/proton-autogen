import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from proton_autogen.ux.recent_card import RecentGameCard


class RecentCarousel(Gtk.Box):

    MAX_VISIBLE = 3

    CARD_WIDTH = 238
    CARD_SPACING = 6

    VIEWPORT_WIDTH = (
        MAX_VISIBLE * CARD_WIDTH
        + (MAX_VISIBLE - 1) * CARD_SPACING
    )

    def __init__(
        self,
        on_launch=None,
        on_edit=None,
        lang="en",
    ):
        super().__init__(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=6,
        )

        self.games = []
        self.index = 0

        self.lang = lang
        self.on_launch = on_launch
        self.on_edit = on_edit

        #
        # Previous button
        #

        self.prev_button = Gtk.Button(
            icon_name="go-previous-symbolic"
        )
        self.prev_button.add_css_class("carousel-button")
        self.prev_button.connect(
            "clicked",
            self._on_previous,
        )

        self.append(self.prev_button)

        #
        # Viewport
        #

        self.viewport = Gtk.Box()

        self.viewport.set_size_request(
            self.VIEWPORT_WIDTH,
            -1,
        )

        self.viewport.set_hexpand(False)

        self.append(self.viewport)

        #
        # Cards container
        #

        self.cards_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=self.CARD_SPACING,
        )

        self.viewport.append(self.cards_box)

        #
        # Next button
        #

        self.next_button = Gtk.Button(
            icon_name="go-next-symbolic"
        )
        self.next_button.add_css_class("carousel-button")
        self.next_button.connect(
            "clicked",
            self._on_next,
        )

        self.append(self.next_button)

        self._update_buttons()

    #
    # Public API
    #

    def set_games(self, games):

        self.games = list(games)

        max_index = max(
            0,
            len(self.games) - self.MAX_VISIBLE
        )

        self.index = min(
            self.index,
            max_index
        )

        self.refresh()

    #
    # Rendering
    #

    def refresh(self):

        self._clear_cards()

        end = self.index + self.MAX_VISIBLE

        for game in self.games[self.index:end]:

            card = RecentGameCard(
                game,
                self.lang,
                self.on_launch,
                self.on_edit,
            )

            self.cards_box.append(card)

        self._update_buttons()

    #
    # Navigation
    #

    def _on_previous(self, *_):

        if self.index <= 0:
            return

        self.index -= 1
        self.refresh()

    def _on_next(self, *_):

        if self.index + self.MAX_VISIBLE >= len(self.games):
            return

        self.index += 1
        self.refresh()

    #
    # Helpers
    #

    def _clear_cards(self):

        while child := self.cards_box.get_first_child():
            self.cards_box.remove(child)

    def _update_buttons(self):

        has_navigation = (
            len(self.games) > self.MAX_VISIBLE
        )

        self.prev_button.set_visible(
            has_navigation
        )

        self.next_button.set_visible(
            has_navigation
        )

        self.prev_button.set_sensitive(
            self.index > 0
        )

        self.next_button.set_sensitive(
            self.index + self.MAX_VISIBLE < len(self.games)
        )
