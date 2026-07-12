import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, Gdk

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
            orientation=Gtk.Orientation.VERTICAL,
            spacing=6,
        )

        self.games = []
        self.index = 0

        self.lang = lang
        self.on_launch = on_launch
        self.on_edit = on_edit

        #
        # Keyboard focus
        #

        self.set_focusable(True)

        self.key_controller = Gtk.EventControllerKey()

        self.key_controller.connect(
            "key-pressed",
            self._on_key_pressed,
        )

        self.add_controller(
            self.key_controller
        )

        #
        # Carousel line
        #

        self.carousel_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=6,
        )

        self.append(
            self.carousel_box
        )

        #
        # Previous button
        #

        self.prev_button = Gtk.Button(
            icon_name="go-previous-symbolic"
        )

        self.prev_button.add_css_class(
            "carousel-button"
        )

        self.prev_button.connect(
            "clicked",
            self._on_previous,
        )

        self.carousel_box.append(
            self.prev_button
        )

        #
        # Fixed viewport
        #

        self.viewport = Gtk.Box()

        self.viewport.set_size_request(
            self.VIEWPORT_WIDTH,
            -1,
        )

        self.carousel_box.append(
            self.viewport
        )

        #
        # Cards container
        #

        self.cards_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=self.CARD_SPACING,
        )

        self.viewport.append(
            self.cards_box
        )

        #
        # Next button
        #

        self.next_button = Gtk.Button(
            icon_name="go-next-symbolic"
        )

        self.next_button.add_css_class(
            "carousel-button"
        )

        self.next_button.connect(
            "clicked",
            self._on_next,
        )

        self.carousel_box.append(
            self.next_button
        )

        #
        # Counter
        #

        self.indicator = Gtk.Label()

        self.indicator.add_css_class(
            "carousel-indicator"
        )

        self.indicator.set_halign(
            Gtk.Align.CENTER
        )

        self.append(
            self.indicator
        )

        self._update_ui()

    #
    # Public API
    #

    def set_games(self, games):

        self.games = list(games)

        self.index = min(
            self.index,
            self._max_index()
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

            self.cards_box.append(
                card
            )

        self._update_ui()

    #
    # Navigation mouse
    #

    def _on_previous(self, *_):

        self.move_by(-1)

    def _on_next(self, *_):

        self.move_by(1)

    #
    # Navigation logic
    #

    def move_by(self, amount):

        new_index = self.index + amount

        new_index = max(
            0,
            min(
                new_index,
                self._max_index()
            )
        )

        if new_index != self.index:

            self.index = new_index
            self.refresh()

    def go_first(self):

        if self.index != 0:

            self.index = 0
            self.refresh()

    def go_last(self):

        last = self._max_index()

        if self.index != last:

            self.index = last
            self.refresh()

    #
    # Keyboard
    #

    def _on_key_pressed(
        self,
        controller,
        keyval,
        keycode,
        state,
    ):

        if keyval == Gdk.KEY_Left:
            self.move_by(-1)
            return True

        if keyval == Gdk.KEY_Right:
            self.move_by(1)
            return True

        if keyval == Gdk.KEY_Home:
            self.go_first()
            return True

        if keyval == Gdk.KEY_End:
            self.go_last()
            return True

        if keyval == Gdk.KEY_Page_Up:
            self.move_by(-self.MAX_VISIBLE)
            return True

        if keyval == Gdk.KEY_Page_Down:
            self.move_by(self.MAX_VISIBLE)
            return True

        return False

    #
    # Helpers
    #

    def _page_count(self):

        return max(
            1,
            (len(self.games) + self.MAX_VISIBLE - 1)
            // self.MAX_VISIBLE
        )


    def _current_page(self):

        return self.index // self.MAX_VISIBLE

    def _clear_cards(self):

        while child := self.cards_box.get_first_child():

            self.cards_box.remove(
                child
            )

    def _max_index(self):

        return max(
            0,
            len(self.games) - self.MAX_VISIBLE
        )

    def _update_ui(self):

        total = len(self.games)

        has_navigation = (
            total > self.MAX_VISIBLE
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
            self.index < self._max_index()
        )

        if total > self.MAX_VISIBLE:

            pages = self._page_count()

            current = self._current_page()

            dots = []

            for i in range(pages):

                if i == current:
                    dots.append("●")
                else:
                    dots.append("○")

            self.indicator.set_text(
                " ".join(dots)
            )

            self.indicator.set_visible(True)

        else:

            self.indicator.set_text("")
            self.indicator.set_visible(False)
