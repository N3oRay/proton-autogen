#!/usr/bin/env python3
# cover_manager.py
"""
Gestion des jaquettes (images de présentation) de la vue Bibliothèque.

Rôle
----
    - import_cover()  : copie l'image choisie par l'utilisateur dans le
                        dossier de données de proton-autogen, redimensionnée
                        (l'original peut être déplacé / supprimé sans casser
                        la bibliothèque)
    - remove_cover()  : supprime une jaquette gérée par proton-autogen
    - request_cover() : fournit une Gdk.Texture déjà recadrée à la taille
                        d'une carte, avec cache LRU et chargement hors du
                        thread GTK (pas de gel de l'UI au premier affichage)

Aucune dépendance ajoutée : uniquement GdkPixbuf / Gdk / GLib (PyGObject),
déjà requis par le projet.

Stockage
--------
    ~/.local/share/proton-autogen/covers/<md5(chemin exe)>-<horodatage>.(png|jpg)

Le nom change à chaque import : le cache de textures n'a donc jamais à être
invalidé (nouveau chemin = nouvelle clé), et l'ancien fichier est supprimé.

Règles de threading
-------------------
Le cache (_TEXTURE_CACHE) n'est lu et écrit QUE depuis le thread principal
GTK. Le thread worker ne fait que décoder / recadrer un GdkPixbuf (thread-safe)
et renvoie le résultat via GLib.idle_add.
"""

import hashlib
import math
import os
import time
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Callable, Optional

import gi

gi.require_version("Gdk", "4.0")
gi.require_version("GdkPixbuf", "2.0")
from gi.repository import Gdk, GdkPixbuf, GLib


# Ratio hauteur / largeur d'une jaquette (portrait 2:3, format « boîte de jeu »).
COVER_RATIO = 1.5

# Taille maximale de l'image stockée : suffisante pour le zoom maximal de la
# vue (208 px de large) sur écran HiDPI, sans garder une photo de 20 Mo.
STORED_MAX_WIDTH = 600
STORED_MAX_HEIGHT = 900

# Nombre maximal de textures gardées en mémoire (une par jaquette ET par taille
# de zoom). 600x900 → ~2 Mo en RGBA, mais les textures en cache sont à la
# taille d'affichage (≈ 0,1 à 0,5 Mo) : 128 entrées restent légères.
_TEXTURE_CACHE_MAX = 128

_TEXTURE_CACHE: "OrderedDict[tuple, Gdk.Texture]" = OrderedDict()

# Peu de workers : le décodage d'image est CPU-bound, et le premier affichage
# d'une bibliothèque ne doit pas saturer la machine pendant qu'un jeu démarre.
_EXECUTOR = ThreadPoolExecutor(max_workers=2, thread_name_prefix="cover")


# ---------------------------------------------------------------------------
# Chemins
# ---------------------------------------------------------------------------

def covers_dir() -> Path:
    """Dossier des jaquettes, sous le dossier de données existant."""
    return Path.home() / ".local/share/proton-autogen" / "covers"


def _game_id(game_path: str) -> str:
    # Même calcul que loader._game_id() : un identifiant stable par exécutable.
    return hashlib.md5(os.path.abspath(game_path).encode()).hexdigest()


def is_managed(path) -> bool:
    """Vrai si `path` est un fichier du dossier covers/ (jamais ailleurs)."""
    if not path:
        return False
    try:
        return Path(path).resolve().parent == covers_dir().resolve()
    except (OSError, RuntimeError):
        return False


# ---------------------------------------------------------------------------
# Validation / import / suppression
# ---------------------------------------------------------------------------

def _file_size(path) -> Optional[tuple]:
    """(largeur, hauteur) lues dans l'en-tête, sans décoder l'image."""
    try:
        info = GdkPixbuf.Pixbuf.get_file_info(str(path))
    except (GLib.Error, TypeError):
        return None

    if not info or info[0] is None:
        return None

    _fmt, width, height = info
    if width <= 0 or height <= 0:
        return None

    return width, height


def is_supported_image(path) -> bool:
    """Vrai si GdkPixbuf sait lire ce fichier (png, jpg, webp, gif, ...
    selon les loaders installés sur le système)."""
    return bool(path) and Path(path).is_file() and _file_size(path) is not None


def import_cover(src_path, game_path: str) -> Optional[str]:
    """
    Copie `src_path` dans covers/ (redimensionné si trop grand) et retourne
    le chemin stocké, ou None en cas d'échec. N'efface jamais `src_path`.
    """
    size = _file_size(src_path)
    if size is None:
        return None

    width, height = size
    tmp = None

    try:
        if width > STORED_MAX_WIDTH or height > STORED_MAX_HEIGHT:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
                str(src_path), STORED_MAX_WIDTH, STORED_MAX_HEIGHT
            )
        else:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(str(src_path))

        # Photos de téléphone : respecte l'orientation EXIF.
        rotated = pixbuf.apply_embedded_orientation()
        if rotated is not None:
            pixbuf = rotated

        directory = covers_dir()
        directory.mkdir(parents=True, exist_ok=True)

        # PNG pour garder la transparence, JPEG sinon (beaucoup plus léger).
        if pixbuf.get_has_alpha():
            fmt, ext, keys, values = "png", "png", [], []
        else:
            fmt, ext, keys, values = "jpeg", "jpg", ["quality"], ["90"]

        final = directory / f"{_game_id(game_path)}-{time.time_ns()}.{ext}"
        tmp = final.with_suffix(final.suffix + ".tmp")

        # Écriture atomique : jamais de jaquette à moitié écrite.
        pixbuf.savev(str(tmp), fmt, keys, values)
        os.replace(tmp, final)
        return str(final)

    except (GLib.Error, OSError):
        if tmp is not None:
            try:
                tmp.unlink()
            except OSError:
                pass
        return None


def remove_cover(path) -> bool:
    """Supprime une jaquette, uniquement si elle est dans covers/."""
    if not is_managed(path):
        return False
    try:
        Path(path).unlink()
        return True
    except OSError:
        return False


# ---------------------------------------------------------------------------
# Chargement / recadrage / cache
# ---------------------------------------------------------------------------

def _cover_pixbuf(path, width: int, height: int):
    """
    Image recadrée « cover » à width x height : remplit toute la carte,
    centrée, sans déformation. Thread-safe (n'utilise que GdkPixbuf).
    """
    size = _file_size(path)
    if size is None:
        return None

    src_w, src_h = size
    scale = max(width / src_w, height / src_h)
    scaled_w = max(width, math.ceil(src_w * scale))
    scaled_h = max(height, math.ceil(src_h * scale))

    try:
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            str(path), scaled_w, scaled_h, False
        )
        # Pas d'orientation EXIF ici : import_cover() l'a déjà appliquée
        # une fois pour toutes sur le fichier stocké.
        x = max(0, (pixbuf.get_width() - width) // 2)
        y = max(0, (pixbuf.get_height() - height) // 2)
        width = min(width, pixbuf.get_width())
        height = min(height, pixbuf.get_height())

        # copy() : libère le grand pixbuf parent (le sous-pixbuf le référence).
        return pixbuf.new_subpixbuf(x, y, width, height).copy()

    except GLib.Error:
        return None


def _cache_key(path, width: int, height: int) -> tuple:
    return (str(path), width, height)


def _cache_get(key):
    texture = _TEXTURE_CACHE.get(key)
    if texture is not None:
        _TEXTURE_CACHE.move_to_end(key)
    return texture


def _cache_put(key, texture) -> None:
    _TEXTURE_CACHE[key] = texture
    _TEXTURE_CACHE.move_to_end(key)
    while len(_TEXTURE_CACHE) > _TEXTURE_CACHE_MAX:
        _TEXTURE_CACHE.popitem(last=False)


def load_texture_sync(path, width: int, height: int):
    """Chargement immédiat (petites tailles : aperçu de l'éditeur)."""
    key = _cache_key(path, width, height)
    texture = _cache_get(key)
    if texture is not None:
        return texture

    pixbuf = _cover_pixbuf(path, width, height)
    if pixbuf is None:
        return None

    texture = Gdk.Texture.new_for_pixbuf(pixbuf)
    _cache_put(key, texture)
    return texture


def request_cover(
    path,
    width: int,
    height: int,
    callback: Callable[[Optional[Gdk.Texture]], None],
) -> Optional[Gdk.Texture]:
    """
    Retourne la texture tout de suite si elle est en cache. Sinon retourne
    None, charge l'image dans un worker, puis appelle `callback(texture)`
    depuis le thread principal (texture=None si l'image est illisible).

    Le callback doit vérifier que la carte n'a pas été recyclée entre-temps
    (voir GameBiblio._on_cover_ready).
    """
    if not path:
        return None

    key = _cache_key(path, width, height)
    texture = _cache_get(key)
    if texture is not None:
        return texture

    def _deliver(pixbuf):
        # Thread principal.
        texture = None
        if pixbuf is not None:
            texture = _cache_get(key)  # un autre bind a pu finir avant
            if texture is None:
                texture = Gdk.Texture.new_for_pixbuf(pixbuf)
                _cache_put(key, texture)
        callback(texture)
        return False  # GLib.idle_add : ne pas rappeler

    def _work():
        pixbuf = _cover_pixbuf(path, width, height)
        GLib.idle_add(_deliver, pixbuf)

    _EXECUTOR.submit(_work)
    return None
