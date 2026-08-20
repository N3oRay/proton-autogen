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
    # Divers
    # =================================================
    "u4": "u4.svg", # Uncharted
    "killer": "u4.svg", # Uncharted
    "tll": "tlou.svg", # The Last of Us
    "tlou": "tlou.svg",
    "girl": "tlou.svg",

    "spiderman": "spiderman.svg",
    "spider-man": "spiderman.svg",

    "bat-Man": "batman.svg",
    "batman": "batman.svg",

    "proton": "proton.svg",
    "shop": "1shop.svg",
    "new": "2renew.svg",
    "scan": "2renew.svg",
    "saver": "2renew.svg",
    "crown": "3crown.svg",
    "best": "3crown.svg",
    "vip": "3crown.svg",
    "book": "4book.svg",
    "browser": "4book.svg",
    "reading": "4book.svg",
    "reader": "4book.svg",
    "lector": "4book.svg",
    "keyboard": "5key.svg",
    "clavier": "5key.svg",
    "box": "6box.svg",
    "runtime": "6box.svg",
    "craft": "6box.svg",
    "compil": "6box.svg",
    "motion": "6box.svg",
    "usb": "6box.svg",
    "pack": "6box.svg",
    "tablet": "7tablet.svg",
    "redsn0w": "7tablet.svg",
    "palm": "7tablet.svg",
    "smart": "7tablet.svg",
    "sexy": "8sexy.svg",
    "charme": "8sexy.svg",
    "love": "9love.svg",
    "unreal": "10unreal.svg",
    "gpu": "11gpu.svg",
    "cpu": "11gpu.svg",
    "npu": "11gpu.svg",
    "intel": "11gpu.svg",
    "amd": "11gpu.svg",
    "nvidia": "11gpu.svg",
    "memory": "12ram.svg",
    "memoire": "12ram.svg",
    "alimentation": "13alim.svg",
    "supply": "13alim.svg",
    "casque": "14casque.svg",
    "headphone": "14casque.svg",
    "bluetooth": "14casque.svg",
    "micro": "14casque.svg",
    "communication": "14casque.svg",
    "pixman": "15print.svg",
    "epson": "15print.svg",
    "printer": "15print.svg",
    "print": "15print.svg",
    "canon": "15print.svg",
    "brother": "15print.svg",

    "x-com": "16alien.svg",
    "street": "17street.svg",
    "crysis": "18crysis.svg",
    "fallout3": "19fallout.svg",
    "falloutnv": "19fallout.svg",

    # =================================================
    # Launchers
    # =================================================

    "steam": "Steam_icon_logo.svg",
    "steamclient": "Steam_icon_logo.svg",
    "valve": "Steam_icon_logo.svg",
    "epic": "Epic_Games_logo.svg",
    "epicgames": "Epic_Games_logo.svg",
    "epiclauncher": "Epic_Games_logo.svg",
    "gog": "king.svg",
    "goggalaxy": "king.svg",
    "galaxy": "king.svg",

    # =================================================
    # Battle.net
    # =================================================
    "battlenet": "battle-net-64.svg",
    "battle.net": "battle-net-64.svg",
    "diablo ii resurrected": "battle-net-64.svg",
    "d2r": "battle-net-64.svg",
    "diablo iii": "battle-net-64.svg",
    "diablo iv": "battle-net-64.svg",
    "diablo immortal": "battle-net-64.svg",
    "hearthstone": "battle-net-64.svg",
    "heroes of the storm": "battle-net-64.svg",
    "heroesofthestorm": "battle-net-64.svg",
    "overwatch": "battle-net-64.svg",
    "overwatch2": "battle-net-64.svg",
    "starcraft": "battle-net-64.svg",
    "starcraft remastered": "battle-net-64.svg",
    "starcraft ii": "battle-net-64.svg",
    "sc2": "battle-net-64.svg",
    "warcraft iii": "battle-net-64.svg",
    "warcraft iii reforged": "battle-net-64.svg",
    "warcraft iii launcher": "battle-net-64.svg",
    "wow": "battle-net-64.svg",
    "world of warcraft": "battle-net-64.svg",
    "wowclassic": "battle-net-64.svg",
    "wowclassict": "battle-net-64.svg",
    "wowclassicera": "battle-net-64.svg",
    "wowb": "battle-net-64.svg",
    "warcraft rumble": "battle-net-64.svg",
    "diablo": "battle-net-64.svg",
    "blizzard": "battle-net-64.svg",


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
    "rage-multiplayer": "gta.svg",
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
    "swep1rcr": "star.svg",
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
    "muxer": "boombox.svg",
    "boombox": "boombox.svg",
    "vocalist": "boombox.svg",
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

def normalize_name(value):
    """
    Normalise un nom pour comparaison.
    """
    return re.sub(
        r"[^a-z0-9]",
        "",
        value.lower()
    )

SORTED_ICON_MAPPING = sorted(
    (
        (normalize_name(keyword), path)
        for keyword, icon in ICON_MAPPING.items()
        if (path := ASSET_DIR / icon).exists()
    ),
    key=lambda item: len(item[0]),
    reverse=True,
)


IMAGE_EXTENSIONS = {
    #".png",
    #".jpg",
    #".jpeg",
    ".gif",
    ".ico",
}


def find_internal_icon(game):

    name = normalize_name(game.get("name", ""))

    if not name:
        return None

    for keyword, icon_path in SORTED_ICON_MAPPING:
        if keyword in name:
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

_ICON_PATH_CACHE = {}  # game_path -> icon_path résolu (ou None)

def _resolve_icon_path(game):
    game_path = str(game.get("path"))

    if game_path in _ICON_PATH_CACHE:
        return _ICON_PATH_CACHE[game_path]

    icon_path = find_game_icon(game)
    if icon_path is None:
        icon_path = find_internal_icon(game)

    _ICON_PATH_CACHE[game_path] = icon_path
    return icon_path


def load_game_icon(game, size=48):
    icon_path = _resolve_icon_path(game)

    cache_key = (str(icon_path), size) if icon_path else ("__default__", size)
    pixbuf = _ICON_CACHE.get(cache_key)

    try:
        if pixbuf is None:
            pixbuf = _load_pixbuf(icon_path if icon_path else DEFAULT_ICON, size)
            _ICON_CACHE[cache_key] = pixbuf

        image = Gtk.Image.new_from_pixbuf(pixbuf)
        image.set_pixel_size(size)

    except Exception:
        try:
            pixbuf = _load_pixbuf(DEFAULT_ICON, size)
            image = Gtk.Image.new_from_pixbuf(pixbuf)
        except Exception:
            image = Gtk.Image.new_from_icon_name("application-x-executable")
            image.set_pixel_size(size)

    image.add_css_class("game-icon")
    return image
