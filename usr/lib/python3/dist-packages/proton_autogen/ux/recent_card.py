import gi
import os

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from proton_autogen.stats import get_game_badges


class RecentGameCard(Gtk.Box):

    def __init__(self, game, lang="en",
                 on_launch=None,
                 on_edit=None):

        super().__init__(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=0
        )

        self.game = game
        self.on_launch = on_launch
        self.on_edit = on_edit
        self.lang = lang


        self.set_size_request(
            220,
            42
        )

        self.add_css_class(
            "recent-card"
        )


        self.build()


    def build(self):

        # ------------------
        # TITLE
        # ------------------

        title = Gtk.Label(
            label=self.game.get(
                "name",
                "Unknown"
            )
        )

        title.set_xalign(0)

        title.add_css_class(
            "title-4"
        )


        # ------------------
        # BADGES
        # ------------------

        badges = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=2
        )


        for badge in get_game_badges(
            self.game,
            self.lang
        ):
            badges.append(
                self.make_badge(badge)
            )


        # ------------------
        # INFO
        # ------------------

        proton = os.path.basename(
            self.game.get(
                "proton",
                ""
            )
        ) or "default"


        info = Gtk.Label(
            label=f"Proton: {proton}"
        )

        info.set_xalign(0)
        info.add_css_class(
            "dim-label1"
        )


        # ------------------
        # BUTTONS
        # ------------------

        actions = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=3
        )


        edit = Gtk.Button(
            label="Edit"
        )

        edit.add_css_class(
            "btn-edit"
        )

        edit.set_size_request(
            50,
            22
        )


        launch = Gtk.Button(
            label="▶"
        )

        launch.add_css_class(
            "btn-launch"
        )

        launch.set_size_request(
            28,
            22
        )


        edit.connect(
            "clicked",
            lambda *_:
                self.on_edit(self.game)
        )


        launch.connect(
            "clicked",
            lambda *_:
                self.on_launch(self.game)
        )


        actions.append(edit)
        actions.append(launch)



        self.append(title)
        self.append(badges)
        self.append(info)
        self.append(actions)



    def make_badge(self, badge):

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


        if badge.get("text"):
            label.set_tooltip_text(
                badge["text"]
            )


        return label
