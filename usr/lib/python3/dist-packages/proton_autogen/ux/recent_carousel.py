import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from proton_autogen.ux.recent_card import RecentGameCard


class RecentCarousel(Gtk.Box):

    MAX_VISIBLE = 3

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
            self._on_previous
        )

        self.append(
            self.prev_button
        )

        #
        # Cards container
        #

        self.cards_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=6,
           # hexpand=True,
        )

        self.cards_box.set_size_request(730, -1)

        self.append(
            self.cards_box
        )

        #
        # Next button
        #

        self.next_button = Gtk.Button(
            icon_name="go-next-symbolic"
        )
        self.next_button.add_css_class("carousel-button")

        self.next_button.connect(
            "clicked",
            self._on_next
        )

        self.append(
            self.next_button
        )

        self._update_buttons()

    #
    # Public API
    #

    def set_games(self, games):

        self.games = list(games)

        if self.index > max(0, len(self.games) - self.MAX_VISIBLE):
            self.index = max(0, len(self.games) - self.MAX_VISIBLE)

        self.refresh()

    #
    # Rendering
    #

    def refresh(self):

        while child := self.cards_box.get_first_child():
            self.cards_box.remove(child)

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

        if self.index > 0:
            self.index -= 1
            self.refresh()

    def _on_next(self, *_):

        if self.index + self.MAX_VISIBLE < len(self.games):
            self.index += 1
            self.refresh()

    #
    # Helpers
    #

    def _update_buttons(self):

        self.prev_button.set_sensitive(
            self.index > 0
        )

        self.next_button.set_sensitive(
            self.index + self.MAX_VISIBLE < len(self.games)
        )
