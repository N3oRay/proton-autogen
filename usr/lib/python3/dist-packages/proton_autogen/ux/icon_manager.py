# icon_manager.py

from pathlib import Path
import os

from gi.repository import Gtk, GdkPixbuf


_ICON_CACHE = {}


DEFAULT_ICON = "application-x-executable"

IMAGE_EXTENSIONS = {
    ".png",
    #".jpg",
    #".jpeg",
    ".gif",
    ".ico",
}


# -------------------------------------------------
# Recherche icône
# -------------------------------------------------

def find_game_icon(game):

    try:

        path = game.get("path")

        if not path:
            return None

        exe = Path(path)

        if not exe.exists():
            return None


        directory = exe.parent


        if not directory.exists():
            return None


        candidates = [
            "icon.ico",
            "game.ico",
            "folder.ico",
            "icon.png",
            "folder.png",
        ]


        for name in candidates:

            icon = directory / name

            if icon.is_file():
                return icon


        # Recherche limitée
        # évite de scanner tout le disque

        for file in directory.iterdir():

            if (
                file.is_file()
                and file.suffix.lower() in IMAGE_EXTENSIONS
            ):
                return file


    except (
        FileNotFoundError,
        PermissionError,
        OSError
    ):

        pass


    return None



# -------------------------------------------------
# Création GTK Image
# -------------------------------------------------

def load_game_icon(game, size=48):

    cache_key = (
        game.get("path"),
        size
    )


    if cache_key in _ICON_CACHE:
        return _ICON_CACHE[cache_key]


    icon_path = find_game_icon(game)


    try:

        if icon_path:

            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                str(icon_path),
                size,
                size,
                True
            )

            image = Gtk.Image.new_from_pixbuf(
                pixbuf
            )

        else:

            image = Gtk.Image.new_from_icon_name(
                DEFAULT_ICON
            )

            image.set_pixel_size(size)


    except (
        Exception
    ):

        image = Gtk.Image.new_from_icon_name(
            DEFAULT_ICON
        )

        image.set_pixel_size(size)


    _ICON_CACHE[cache_key] = image

    return image
