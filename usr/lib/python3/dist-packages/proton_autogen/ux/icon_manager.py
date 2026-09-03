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

# =================================================
# SVG À AJOUTER PROGRESSIVEMENT
# =================================================
#
# Objectif :
# Ajouter uniquement les icônes SVG qui ne sont PAS
# déjà couvertes par ICON_MAPPING.
#
# Une icône doit être ajoutée uniquement lorsqu'un
# programme Windows réel nécessite une représentation
# visuelle qui n'existe pas encore.
#
# IMPORTANT :
# - Ne pas recréer une icône déjà disponible.
# - Ne pas créer une icône spécifique à chaque logiciel.
# - Privilégier les icônes thématiques réutilisables.
# - Vérifier d'abord les alias existants dans ICON_MAPPING.
#
# =================================================
# 01 - WINDOWS / SYSTÈME
# =================================================
# windows.svg
# system.svg
# service.svg
# driver.svg
# process.svg
# task.svg
# registry.svg
# explorer.svg
# desktop.svg
# startup.svg
#
# Mots-clés potentiels :
# windows, system, system32, service, services,
# driver, dll, process, processes, taskmgr,
# registry, regedit, explorer, desktop,
# startup, autostart
#
# =================================================
# 02 - STOCKAGE / DISQUES AVANCÉS
# =================================================
# disk.svg
# drive.svg
# storage.svg
# ssd.svg
# hdd.svg
# partition.svg
# backup.svg
# recovery.svg
# clone.svg
# iso.svg
# mount.svg
# folder.svg
# file.svg
#
# Mots-clés potentiels :
# disk, drive, storage, ssd, hdd, partition,
# backup, recovery, clone, cloning, iso, mount,
# folder, file
#
# =================================================
# 03 - SÉCURITÉ
# =================================================
# security.svg
# antivirus.svg
# firewall.svg
# virus.svg
# shield.svg
# password.svg
# lock.svg
# unlock.svg
# privacy.svg
# certificate.svg
# encryption.svg
#
# Mots-clés potentiels :
# security, antivirus, firewall, malware, virus,
# defender, password, credential, lock, unlock,
# privacy, certificate, ssl, tls, encryption,
# decrypt, authentication, auth
#
# =================================================
# 04 - RÉSEAU AVANCÉ
# =================================================
# internet.svg
# proxy.svg
# dns.svg
# dhcp.svg
# ip.svg
# port.svg
# client.svg
# remote.svg
# rdp.svg
# ssh.svg
# ftp.svg
#
# Mots-clés potentiels :
# internet, proxy, dns, dhcp, ip, tcp, udp,
# port, client, remote, rdp, ssh, ftp, http,
# websocket
#
# =================================================
# 05 - DÉVELOPPEMENT / PROGRAMMATION
# =================================================
# code.svg
# debug.svg
# debugger.svg
# compiler.svg
# node.svg
# npm.svg
# git.svg
# github.svg
# cmake.svg
# rust.svg
# go.svg
# api.svg
# sdk.svg
#
# Mots-clés potentiels :
# code, debug, debugger, compiler, node, nodejs,
# npm, git, github, cmake, gcc, clang, rust,
# go, php, perl, ruby, api, sdk
#
# =================================================
# 06 - VIDÉO / CAPTURE / STREAMING
# =================================================
# codec.svg
# stream.svg
# capture.svg
# screenshot.svg
# record.svg
# webcam.svg
# display.svg
# monitor.svg
#
# Mots-clés potentiels :
# codec, stream, capture, screenshot, record,
# recording, webcam, display, monitor, screen,
# hdr
#
# =================================================
# 07 - AUDIO
# =================================================
# audio.svg
# speaker.svg
# mixer.svg
# equalizer.svg
# microphone.svg
# recording.svg
# asio.svg
# wasapi.svg
# midi.svg
#
# Mots-clés potentiels :
# audio, speaker, mixer, equalizer, microphone,
# recording, asio, wasapi, dac, midi, sound,
# voice, music
#
# =================================================
# 08 - CLOUD / SYNCHRONISATION AVANCÉE
# =================================================
# cloud.svg
# upload.svg
# backup-cloud.svg
#
# Mots-clés potentiels :
# cloud, upload, onedrive, dropbox,
# google-drive, icloud
#
# =================================================
# 09 - INSTALLATION / MISE À JOUR
# =================================================
# installer.svg
# uninstall.svg
# updater.svg
# upgrade.svg
# patch.svg
# repair.svg
# maintenance.svg
# portable.svg
# bootstrap.svg
# package.svg
#
# Mots-clés potentiels :
# installer, uninstall, remove, updater, upgrade,
# patch, repair, maintenance, portable,
# bootstrap, package, package-manager
#
# =================================================
# 10 - DIAGNOSTIC / MONITORING
# =================================================
# diagnostic.svg
# benchmark.svg
# stress.svg
# temperature.svg
# sensor.svg
# performance.svg
# monitoring.svg
# stats.svg
# log.svg
# logger.svg
# profiler.svg
# analyzer.svg
#
# Mots-clés potentiels :
# diagnostic, benchmark, stress, temperature,
# sensor, performance, monitoring, stats, log,
# logger, profiler, analyzer, analyze
#
# =================================================
# 11 - BUREAUTIQUE / DOCUMENTS
# =================================================
# document.svg
# pdf.svg
# text.svg
# editor.svg
# spreadsheet.svg
# sql.svg
# csv.svg
# json.svg
# xml.svg
#
# Mots-clés potentiels :
# word, excel, powerpoint, pdf, document, text,
# editor, notepad, spreadsheet, sql, csv, json,
# xml
#
# =================================================
# 12 - GRAPHISME / CRÉATION
# =================================================
# drawing.svg
# paint.svg
# vector.svg
# 3d.svg
# modeling.svg
# render.svg
# rendering.svg
# animation.svg
# design.svg
#
# Mots-clés potentiels :
# drawing, paint, vector, 3d, modeling, render,
# rendering, animation, illustrator, premiere,
# davinci, aftereffects
#
# =================================================
# 13 - PÉRIPHÉRIQUES
# =================================================
# controller.svg
# gamepad.svg
# webcam.svg
# camera.svg
# dock.svg
# serial.svg
# hid.svg
#
# Mots-clés potentiels :
# controller, gamepad, webcam, camera, dock,
# bluetooth, serial, com, hid, joystick
#
# =================================================
# 14 - BASES DE DONNÉES SPÉCIFIQUES
# =================================================
# sql.svg
# mysql.svg
# postgresql.svg
# sqlite.svg
# mongodb.svg
# redis.svg
#
# Mots-clés potentiels :
# sql, mysql, mariadb, postgresql, postgres,
# sqlite, mongodb, mongo, redis
#
# =================================================
# 15 - VIRTUALISATION / CONTENEURS
# =================================================
# virtual-machine.svg
# virtualization.svg
# vm.svg
# container.svg
# hypervisor.svg
#
# Mots-clés potentiels :
# vm, virtualmachine, virtualization,
# virtualbox, vmware, hypervisor, container,
# kubernetes, wsl
#
# =================================================
# 16 - IA / MACHINE LEARNING
# =================================================
# ai.svg
# neural.svg
# brain.svg
# machine-learning.svg
# chatbot.svg
# llm.svg
# gpu-ai.svg
#
# Mots-clés potentiels :
# ai, artificial-intelligence, neural,
# neural-network, machine-learning, ml,
# chatbot, llm, inference, ollama, cuda,
# tensor, pytorch, tensorflow
#
# =================================================
# 17 - TÉLÉCHARGEMENT / PARTAGE
# =================================================
# download.svg
# upload.svg
# torrent.svg
# share.svg
# transfer.svg
#
# Mots-clés potentiels :
# download, downloader, upload, torrent,
# bittorrent, share, sharing, transfer
#
# =================================================
# RÈGLE D'AJOUT
# =================================================
#
# Lorsqu'un nouvel EXE est identifié :
#
# 1. Vérifier le nom exact de l'EXE.
# 2. Vérifier sa fonction réelle.
# 3. Chercher un mot-clé déjà présent dans
#    ICON_MAPPING.
# 4. Vérifier si une icône existante peut convenir.
# 5. Si aucune icône ne convient :
#       -> rechercher / ajouter un nouveau SVG.
# 6. Ajouter ensuite les alias nécessaires.
#
# =================================================
# PRIORITÉ
# =================================================
#
# [ ] EXE Windows réellement identifié
# [ ] Fonction vérifiée
# [ ] Aucun mapping existant adapté
# [ ] SVG réellement nécessaire
# [ ] Catégorie générique
# [ ] Réutilisable pour plusieurs programmes
# [ ] Aucun doublon avec les SVG existants
#
# =================================================
# IMPORTANT
# =================================================
#
# Ce bloc représente UNIQUEMENT les SVG restant
# potentiellement à ajouter.
#
# Dès qu'un SVG est ajouté dans ICON_MAPPING :
#
#     -> supprimer ici le SVG correspondant
#     -> supprimer les mots-clés désormais couverts
#
# Ne jamais conserver une catégorie déjà correctement
# couverte par ICON_MAPPING.
#
# Exemple :
#
# "python": "brand-python.svg"
#     -> ne pas ajouter python.svg
#
# "gpu": "gpu.svg"
#     -> ne pas ajouter gpu.svg
#
# "docker": "brand-docker.svg"
#     -> ne pas ajouter docker.svg
#
# "terminal": "terminal-2.svg"
#     -> ne pas ajouter terminal.svg
#
# "video": "video.svg"
#     -> ne pas ajouter video.svg
#
# =================================================
# FIN DE LA LISTE DES SVG À AJOUTER
# =================================================



ICON_MAPPING = {

    # =================================================
    # Nouveaux SVG - Système / Développement / Réseau
    # =================================================

    # -------------------------------------------------
    # Réglages / Configuration
    # -------------------------------------------------
    "adjustments": "adjustments-cog.svg",
    "configuration": "adjustments-cog.svg",
    "options": "adjustments-cog.svg",

    "adjustments-code": "adjustments-code.svg",
    "developer": "adjustments-code.svg",
    "development": "adjustments-code.svg",
    "dev": "adjustments-code.svg",
    "coding": "adjustments-code.svg",

    # -------------------------------------------------
    # PowerShell
    # -------------------------------------------------
    "powershell": "brand-powershell.svg",
    "pwsh": "brand-powershell.svg",

    # -------------------------------------------------
    # Python
    # -------------------------------------------------
    "python": "brand-python.svg",
    "pythonw": "brand-python.svg",

    # -------------------------------------------------
    # Docker
    # -------------------------------------------------
    "docker": "brand-docker.svg",
    "dockerd": "brand-docker.svg",

    # -------------------------------------------------
    # Android / Mobile
    # -------------------------------------------------
    "android": "brand-android.svg",
    "adb": "brand-android.svg",
    "fastboot": "brand-android.svg",

    "mobile": "device-mobile-charging.svg",
    "smartphone": "device-mobile-charging.svg",
    "phone": "device-mobile-charging.svg",

    # -------------------------------------------------
    # Microsoft Office
    # -------------------------------------------------
    "office": "brand-office.svg",
    "microsoftoffice": "brand-office.svg",
    "msoffice": "brand-office.svg",

    # -------------------------------------------------
    # Databricks
    # -------------------------------------------------
    "databricks": "brand-databricks.svg",

    # -------------------------------------------------
    # YouTube
    # -------------------------------------------------
    "youtube": "brand-youtube.svg",

    # =================================================
    # Matériel / Hardware
    # =================================================

    # -------------------------------------------------
    # CPU
    # -------------------------------------------------
    "cpu": "cpu.svg",
    "processor": "cpu.svg",
    "processeur": "cpu.svg",

    # -------------------------------------------------
    # GPU
    # -------------------------------------------------
    "gpu": "gpu.svg",
    "graphics": "gpu.svg",
    "graphicscard": "gpu.svg",
    "videocard": "gpu.svg",

    # -------------------------------------------------
    # Ordinateur portable
    # -------------------------------------------------
    "laptop": "device-laptop.svg",
    "notebook": "device-laptop.svg",

    # -------------------------------------------------
    # Souris
    # -------------------------------------------------
    "mouse": "mouse-2.svg",

    # =================================================
    # Réseau
    # =================================================

    # -------------------------------------------------
    # Routeur
    # -------------------------------------------------
    "router": "router.svg",

    # -------------------------------------------------
    # Serveur
    # -------------------------------------------------
    "server": "server-2.svg",
    "servers": "server-2.svg",

    # -------------------------------------------------
    # Serveur / Configuration
    # -------------------------------------------------
    "serverconfig": "server-cog.svg",
    "server-config": "server-cog.svg",
    "servermanager": "server-cog.svg",
    "server-management": "server-cog.svg",

    # -------------------------------------------------
    # Monde / téléchargement réseau
    # -------------------------------------------------
    "world-download": "world-download.svg",
    "internet-download": "world-download.svg",

    # =================================================
    # Base de données
    # =================================================

    "database": "database.svg",
    "db": "database.svg",

    "database-import": "database-import.svg",
    "db-import": "database-import.svg",
    "import-database": "database-import.svg",

    # =================================================
    # Fichiers / Archives
    # =================================================

    "zip": "file-type-zip.svg",
    "7zip": "file-type-zip.svg",
    "7z": "file-type-zip.svg",
    "archive": "file-type-zip.svg",
    "compressed": "file-type-zip.svg",
    "compression": "file-type-zip.svg",

    # =================================================
    # Sauvegarde / Restauration
    # =================================================

    "restore": "restore.svg",
    "restoration": "restore.svg",
    "restorer": "restore.svg",

    # =================================================
    # Terminal
    # =================================================

    "terminal": "terminal-2.svg",
    "console": "terminal-2.svg",
    "command": "terminal-2.svg",
    "commandline": "terminal-2.svg",
    "command-line": "terminal-2.svg",

    # =================================================
    # Vidéo / Multimédia
    # =================================================

    "video": "video.svg",
    "videoeditor": "video.svg",
    "video-editor": "video.svg",
    "encoder": "video.svg",
    "decoder": "video.svg",

    # -------------------------------------------------
    # Film / Média
    # -------------------------------------------------
    "film": "film.svg",
    "movie": "film.svg",
    "movies": "film.svg",
    "cinema": "film.svg",

    # =================================================
    # Disques / Médias
    # =================================================

    "disc": "disc.svg",
    "disk": "disc.svg",
    "cd": "disc.svg",
    "dvd": "disc.svg",
    "bluray": "disc.svg",

    # =================================================
    # Rotation / Synchronisation
    # =================================================

    "rotate": "rotate-clockwise-2.svg",
    "rotation": "rotate-clockwise-2.svg",
    "refresh": "rotate-clockwise-2.svg",
    "reload": "rotate-clockwise-2.svg",
    "sync": "rotate-clockwise-2.svg",
    "synchronize": "rotate-clockwise-2.svg",

    # =================================================
    # Affichage / Mur / Écran
    # =================================================

    "wall": "wall.svg",


    # =================================================
    # Divers
    # =================================================
    "u4": "u4.svg", # Uncharted
    "killer": "u4.svg", # Uncharted
    "tll": "tlou.svg", # The Last of Us
    "tlou": "tlou.svg",
    "girl": "tlou.svg",
    "assassins": "assassins.svg",
    "creed": "assassins.svg",
    "apple": "apple.svg",
    "itune": "apple.svg",
    "iphone": "apple.svg",
    "redsn0w": "apple.svg",
    "ios": "apple.svg",
    "pinball": "pinball.svg",

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
    "palm": "7tablet.svg",
    "smart": "7tablet.svg",
    "sexy": "8sexy.svg",
    "charme": "8sexy.svg",
    "love": "9love.svg",
    "unreal": "10unreal.svg",
    "gpu": "11gpu.svg",
    "cpu": "11gpu.svg",
    "npu": "11gpu.svg",
    "bios": "11gpu.svg",
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
    "photosh": "photoshop.svg",
    "blender": "blender.svg",
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
            "Jeu.ico",
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
