#proton_autogen/ux/ icon_manager.py

from pathlib import Path
import re
from gi.repository import Gtk, GdkPixbuf


_ICON_CACHE = {}

ASSET_DIR = (
    Path(__file__).parent /
    "assets" /
    "svg"
)


DEFAULT_ICON = (
    ASSET_DIR /
    "gamepad.svg"
)

ICON_MAPPING = {

    # =================================================
    # Launchers
    # =================================================

    "steam": "Steam_icon_logo.svg",
    "steamclient": "Steam_icon_logo.svg",
    "valve": "Steam_icon_logo.svg",
    "epic": "Epic_Games_logo.svg",
    "epicgames": "Epic_Games_logo.svg",
    "epiclauncher": "Epic_Games_logo.svg",
    "battlenet": "battle-net-64.svg",
    "battle.net": "battle-net-64.svg",
    "blizzard": "battle-net-64.svg",
    "gog": "king.svg",
    "goggalaxy": "king.svg",
    "galaxy": "king.svg",


    # =================================================
    # Gaming / Action
    # =================================================

    "battle": "battle-gear.svg",
    "combat": "battle-gear.svg",
    "fighter": "battle-gear.svg",
    "tank": "battle-tank.svg",
    "mech": "battle-mech.svg",
    "robot": "battle-mech.svg",
    "cyber": "cyborg-face.svg",
    "cyborg": "cyborg-face.svg",
    "hacker": "cyborg-face.svg",
    "war": "great-war-tank.svg",
    "warfare": "great-war-tank.svg",
    "military": "great-war-tank.svg",
    "ship": "battleship.svg",
    "navy": "battleship.svg",
    "axe": "battered-axe.svg",
    "viking": "viking-church.svg",

    "king": "king.svg",
    "chess": "chess-king.svg",
    "files": "files.svg",
    "fallout": "fallout.svg",
    # GTA Multiplayer
    "ragemultiplayer": "gta.svg",
    "ragemultiplayer": "gta.svg",
    "ragemp": "gta.svg",
    "fivem": "gta.svg",
    "altv": "gta.svg",
    "alt:v": "gta.svg",
    "gtav": "gta.svg",
    "gta5": "gta.svg",
    "setup": "setup.svg",
    "board": "mb.svg",
    "pingouin": "pingouin.svg",
    "linux": "pingouin.svg",
    "photo": "image.svg",
    "image": "image.svg",
    "javaw": "battle-mech.svg",
    "fabric": "battle-mech.svg",
    "forge": "battle-mech.svg",

    "wine64": "wine.svg",
    "winecfg": "wine.svg",
    "wineboot": "wine.svg",
    "wineconsole": "wine.svg",

    # =================================================
    # Adventure / Simulation / Sport
    # =================================================

    "walk": "walking-scout.svg",
    "scout": "walking-scout.svg",

    "turret": "walking-turret.svg",

    "bike": "cycling.svg",
    "cycle": "cycling.svg",

    "hike": "hiking.svg",
    "hiking": "hiking.svg",

    "goal": "goal-keeper.svg",
    "sport": "goal-keeper.svg",
    "fifa": "goal-keeper.svg",

    "gta": "gta.svg",
    "firem": "gta.svg",
    "sky": "sky.svg",
    "cat": "cat.svg",
    "chat": "cat.svg",
    "voice": "sound.svg",
    "starwars": "star.svg",
    "starwar": "star.svg",
    "swr": "star.svg",
    "star": "star.svg",
    "sega": "sega.svg",
    "sonic": "sega.svg",
    "bench": "wipe.svg",
    "wipe": "wipe.svg",
    "window": "wine.svg",

    "ffmpeg": "wine.svg",
    "ffplay": "wine.svg",
    "avast": "wine.svg",
    "rufus": "power-button.svg",
    "mod": "mod.svg",

    "dotnet": "mesh-network.svg",
    "network": "network-bars.svg",
    "ucc": "network-bars.svg",
    "furmark": "network-bars.svg",
    "vpn": "network-bars.svg",
    "ethernet": "network-bars.svg",
    "wifi": "network-bars.svg",
    "sound": "sound.svg",
    # =================================================
    # Ambiance / Décoration
    # =================================================

    "alien": "alien-bug.svg",
    "monster": "alien-bug.svg",
    "space": "steam-blast.svg",
    "rocket": "firework-rocket.svg",
    "energy": "energy-arrow.svg",
    "power": "power-lightning.svg",
    "music": "boombox.svg",
    "box": "boombox.svg",
    "smile": "smile.svg",
    "happy": "delighted.svg",
    "green": "green-power.svg",
    "clock": "clockwork.svg",
    "work": "clockwork.svg",
    "breath": "energy-breath.svg",
    "falling": "falling.svg",
    "blob": "falling-blob.svg",
    "heart": "heart-battery.svg",
    "battery": "heart-battery.svg",

    # =================================================
    # Outils
    # =================================================

    "settings": "settings.svg",
    "connect": "connect.svg",
    "putty": "connect.svg",
    "scanner": "connect.svg",
    "config": "settings.svg",
    "origin": "gamepad.svg",
    "eaapp": "gamepad.svg",
    "ubisoft": "king.svg",
    "uplay": "king.svg",
    "rockstar": "battered-axe.svg",
    "riot": "cyborg-face.svg",
    "itch": "boombox.svg",
    "minecraft": "battle-mech.svg",
    "hl": "Epic_Games_logo.svg",

    "dos": "wine.svg",
    "winrar": "winrar.svg",
    "7z": "winrar.svg",
    "7zip": "winrar.svg",
    "zip": "winrar.svg",
    "hammer": "hammer.svg",
    "update": "cute.svg",
    "cute": "cute.svg",
    "play": "cute.svg",
    "role": "role-play.svg",
    "rpg": "role-play.svg",
    "snow": "snow.svg",
    "install": "run.svg",
    "goto": "run.svg",
    "gen": "run.svg",
    "sanity": "run.svg",
    "check": "run.svg",

    "alert": "alert-triangle.svg",
    "warning": "alert-triangle.svg",
    "danger": "alert-triangle.svg",
    "error": "alert-triangle.svg",

}


#DEFAULT_ICON = "application-x-executable"

IMAGE_EXTENSIONS = {
    #".png",
    #".jpg",
    #".jpeg",
    ".gif",
    ".ico",
}




def normalize_name(value):
    """
    Normalise un nom pour comparaison.
    """
    return re.sub(
        r"[^a-z0-9]",
        "",
        value.lower()
    )


def find_internal_icon(game):

    name = normalize_name(
        game.get("name", "")
    )

    if not name:
        return None


    # Recherche par mot-clé (du plus spécifique au plus générique)
    for keyword, icon in sorted(
        ICON_MAPPING.items(),
        key=lambda item: len(normalize_name(item[0])),
        reverse=True,
    ):

        key = normalize_name(keyword)

        if key in name:

            icon_path = ASSET_DIR / icon

            if icon_path.exists():
                return icon_path


    return None





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


        candidates = [
            "gfw_high.ico",
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


        #
        # Recherche limitée
        #
        try:

            for file in directory.iterdir():

                if (
                    file.is_file()
                    and file.suffix.lower()
                    in IMAGE_EXTENSIONS
                ):
                    return file

        except (
            PermissionError,
            OSError
        ):
            pass


    except (
        FileNotFoundError,
        PermissionError,
        OSError
    ):
        pass


    return None



# -------------------------------------------------
# Chargement image
# -------------------------------------------------

def _load_pixbuf(path, size):

    return GdkPixbuf.Pixbuf.new_from_file_at_scale(
        str(path),
        size,
        size,
        True
    )



# -------------------------------------------------
# Création GTK Image
# -------------------------------------------------

# -------------------------------------------------
# Création GTK Image
# -------------------------------------------------

def load_game_icon(game, size=48):

    cache_key = (
        str(game.get("path")),
        size
    )


    icon_path = find_game_icon(game)

    if icon_path is None:
        icon_path = find_internal_icon(game)


    if icon_path:

        cache_key = (
            str(icon_path),
            size
        )


    pixbuf = _ICON_CACHE.get(cache_key)


    try:

        if pixbuf is None:

            if icon_path:

                pixbuf = _load_pixbuf(
                    icon_path,
                    size
                )



            else:

                pixbuf = _load_pixbuf(
                    DEFAULT_ICON,
                    size
                )


            _ICON_CACHE[cache_key] = pixbuf


        image = Gtk.Image.new_from_pixbuf(
            pixbuf
        )
        image.set_pixel_size(size)



    except Exception:

        try:

            pixbuf = _load_pixbuf(
                DEFAULT_ICON,
                size
            )

            image = Gtk.Image.new_from_pixbuf(
                pixbuf
            )

        except Exception:

            image = Gtk.Image.new_from_icon_name(
                "application-x-executable"
            )

            image.set_pixel_size(
                size
            )


    image.add_css_class(
        "game-icon"
    )

    return image
