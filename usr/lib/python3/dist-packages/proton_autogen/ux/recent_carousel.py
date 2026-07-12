import gi
import os

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from proton_autogen.ux.recent_card import RecentGameCard


class RecentCarousel(Gtk.Box):

    def __init__(
        self,
        on_launch=None,
        on_edit=None,
        lang="en"
    ):

        super().__init__(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=0
        )


        self.games = []
        self.lang = lang
        self.on_launch = on_launch
        self.on_edit = on_edit


        self.scroll = Gtk.ScrolledWindow()

        self.scroll.set_policy(
            Gtk.PolicyType.AUTOMATIC,
            Gtk.PolicyType.NEVER
        )


        # IMPORTANT
        self.scroll.set_min_content_height(
            48
        )

        self.scroll.set_max_content_height(
            48
        )


        self.flow = Gtk.FlowBox()


        self.flow.set_orientation(
            Gtk.Orientation.HORIZONTAL
        )

        self.flow.set_selection_mode(
            Gtk.SelectionMode.NONE
        )


        self.flow.set_row_spacing(0)
        self.flow.set_column_spacing(6)


        self.scroll.set_child(
            self.flow
        )

        self.append(
            self.scroll
        )



    def set_games(self, games):

        self.games = games
        self.refresh()



    def refresh(self):

        self.flow.remove_all()


        for game in self.games:

            card = RecentGameCard(
                game,
                self.lang,
                self.on_launch,
                self.on_edit
            )


            child = Gtk.FlowBoxChild()

            child.set_child(
                card
            )


            child.set_margin_top(0)
            child.set_margin_bottom(0)


            self.flow.insert(
                child,
                -1
            )
