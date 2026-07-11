#!/usr/bin/env python3

import gi
import os

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, Pango

from proton_autogen.stats import get_game_badges


class RecentCarousel(Gtk.Box):

    def __init__(
        self,
        on_launch=None,
        on_edit=None,
        lang="en"
    ):
        super().__init__(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=6
        )

        self.on_launch = on_launch
        self.on_edit = on_edit
        self.lang = lang

        self.games = []

        # -----------------------------
        # HORIZONTAL SCROLL
        # -----------------------------

        self.scroll = Gtk.ScrolledWindow()

        self.scroll.set_policy(
            Gtk.PolicyType.AUTOMATIC,
            Gtk.PolicyType.NEVER
        )

        self.scroll.set_hexpand(True)

        self.flow = Gtk.FlowBox()

        self.flow.set_orientation(
            Gtk.Orientation.HORIZONTAL
        )

        self.flow.set_selection_mode(
            Gtk.SelectionMode.NONE
        )

        self.flow.set_homogeneous(False)

        self.scroll.set_child(self.flow)

        self.append(self.scroll)



    # -----------------------------
    # PUBLIC API
    # -----------------------------

    def set_games(self, games):

        self.games = games
        self.refresh()



    def refresh(self):

        self.flow.remove_all()

        for game in self.games:

            card = self._create_card(game)

            self.flow.insert(
                card,
                -1
            )



    # -----------------------------
    # GAME CARD
    # -----------------------------

    def _create_card(self, game):

        box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=5
        )

        box.add_css_class(
            "recent-card"
        )

        box.set_size_request(
            220,
            130
        )


        # TITLE

        title = Gtk.Label(
            label=game.get(
                "name",
                "Unknown"
            )
        )

        title.set_xalign(0)

        title.add_css_class(
            "title-4"
        )



        # BADGES

        badges_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=4
        )


        badges = get_game_badges(
            game,
            self.lang
        )


        for badge in badges:

            badges_box.append(
                self._create_badge(
                    badge
                )
            )



        # INFO

        proton = os.path.basename(
            game.get(
                "proton",
                ""
            )
        )

        if not proton:
            proton = "default"


        info = Gtk.Label(
            label=f"Proton: {proton}"
        )

        info.set_xalign(0)

        info.add_css_class(
            "dim-label1"
        )



        # BUTTONS

        buttons = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=4
        )


        btn_launch = Gtk.Button(
            label="▶"
        )

        btn_launch.add_css_class( "btn-launch" )

        btn_launch.connect(
            "clicked",
            lambda _b, g=game:
                self._launch(g)
        )


        btn_edit = Gtk.Button(
            label="Edit"
        )
        btn_edit.add_css_class("btn-edit")

        btn_edit.connect(
            "clicked",
            lambda _b, g=game:
                self._edit(g)
        )


        buttons.append(btn_edit)
        buttons.append(btn_launch)



        box.append(title)
        box.append(badges_box)
        box.append(info)
        box.append(buttons)


        row = Gtk.FlowBoxChild()

        row.set_child(box)

        row.game_data = game


        return row



    # -----------------------------
    # BADGES
    # -----------------------------

    def _create_badge(self, badge):

        label = Gtk.Label(
            label=badge.get(
                "label",
                ""
            )
        )

        label.add_css_class(
            "badge"
        )


        css = badge.get(
            "css",
            []
        )

        if isinstance(css, str):
            css = [css]


        for c in css:
            label.add_css_class(c)


        tooltip = badge.get(
            "text"
        )

        if tooltip:
            label.set_tooltip_text(
                tooltip
            )


        return label



    # -----------------------------
    # CALLBACKS
    # -----------------------------

    def _launch(self, game):

        if self.on_launch:
            self.on_launch(game)



    def _edit(self, game):

        if self.on_edit:
            self.on_edit(game)
