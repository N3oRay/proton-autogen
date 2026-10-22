#!/usr/bin/env python3

# dashboard_drop.py
"""
Import d'un ou plusieurs `.exe` par glisser-déposer sur la fenêtre.

Fonctionnement :
  - Un Gtk.DropTarget est posé sur toute la fenêtre (Dashboard). Il
    accepte les fichiers (Gdk.FileList ou Gio.File seul), tels que
    fournis par Nautilus, Dolphin, Nemo, Thunar, Caja...
  - Pendant le survol, la classe CSS "drop-active" est ajoutée à la
    fenêtre (retour visuel) et retirée à la sortie / au dépôt.
  - Au dépôt, seuls les fichiers `.exe` (insensible à la casse) sont
    retenus ; le reste est ignoré et signalé.
  - Chaque exécutable passe par add_game_ux() (même chemin que le
    bouton "Ajouter"), SAUF s'il possède déjà une config : add_game_ux()
    réécrit le JSON en entier (temps de jeu, features, env perdus), on
    l'ignore donc comme le fait import_selected() dans import_scan.py.
  - Le travail (find_proton() peut scanner le disque) tourne dans un
    thread ; le résultat revient sur le thread GTK via GLib.idle_add.
  - La liste est rafraîchie UNE seule fois et un seul toast récapitulatif
    est affiché, même pour un dépôt multiple.

La logique de tri (pure, sans GTK) est en haut du module pour rester
testable indépendamment de l'interface.

Câblage dans dashboard.py :
    from proton_autogen.ux.dashboard_drop import DashboardDropMixin
    class Dashboard(..., DashboardRunningMixin, DashboardDropMixin, Gtk.ApplicationWindow):
    ...
    self.build_ui()
    self._init_drop_target()   # après build_ui()

DashboardDropMixin doit être mixé avec Dashboard : il utilise
self.toast, self.status et self.refresh_games().
"""

import threading
from pathlib import Path

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
from gi.repository import Gtk, Gdk, Gio, GLib

from proton_autogen.i18n import tr
from proton_autogen.editor import add_game_ux
from proton_autogen.loader import get_game_config_path
from proton_autogen.diag import find_proton
from proton_autogen.utils.logger import StructuredLogger

logger = StructuredLogger("proton-autogen.ux.dashboard_drop")

DROP_ACTIVE_CSS_CLASS = "drop-active"
ACCEPTED_EXTENSIONS = (".exe",)


# ------------------------------------------------------------------------------------
# LOGIQUE PURE (sans GTK)
# ------------------------------------------------------------------------------------

def is_exe_path(path) -> bool:
    """True si `path` désigne un fichier .exe existant (casse ignorée)."""
    if not path:
        return False
    p = Path(path)
    return p.suffix.lower() in ACCEPTED_EXTENSIONS and p.is_file()


def split_dropped_paths(paths):
    """Sépare les chemins déposés en (exécutables valides, ignorés),
    sans doublons, en conservant l'ordre du dépôt."""
    accepted, rejected, seen = [], [], set()

    for path in paths:
        if not path or path in seen:
            continue
        seen.add(path)
        (accepted if is_exe_path(path) else rejected).append(path)

    return accepted, rejected


def _tr(key: str, fallback: str, **kwargs) -> str:
    """tr() avec repli lisible tant que la clé n'est pas dans les locales."""
    try:
        text = tr(key, **kwargs) if kwargs else tr(key)
    except Exception:
        text = None
    if not text or text == key:
        return fallback.format(**kwargs) if kwargs else fallback
    return text


# ------------------------------------------------------------------------------------
# PARTIE GTK
# ------------------------------------------------------------------------------------

class DashboardDropMixin:

    def _init_drop_target(self):
        """À appeler une fois, après build_ui()."""
        target = Gtk.DropTarget.new(type=Gdk.FileList, actions=Gdk.DragAction.COPY)
        # Certains gestionnaires de fichiers envoient un Gio.File unique
        # plutôt qu'une Gdk.FileList : on accepte les deux.
        target.set_gtypes([Gdk.FileList, Gio.File])
        target.connect("enter", self._on_drop_enter)
        target.connect("leave", self._on_drop_leave)
        target.connect("drop", self._on_drop)
        self.add_controller(target)

    # -------------------------
    # Retour visuel
    # -------------------------
    def _on_drop_enter(self, _target, _x, _y):
        self.add_css_class(DROP_ACTIVE_CSS_CLASS)
        return Gdk.DragAction.COPY

    def _on_drop_leave(self, _target):
        self.remove_css_class(DROP_ACTIVE_CSS_CLASS)

    # -------------------------
    # Dépôt
    # -------------------------
    @staticmethod
    def _paths_from_drop_value(value):
        if isinstance(value, Gdk.FileList):
            files = value.get_files()
        elif isinstance(value, Gio.File):
            files = [value]
        else:
            return []

        # get_path() vaut None pour un fichier non local (ex. sftp://) :
        # on l'ignore, Proton ne pourrait de toute façon pas le lancer.
        return [f.get_path() for f in files if f.get_path()]

    def _on_drop(self, _target, value, _x, _y):
        self.remove_css_class(DROP_ACTIVE_CSS_CLASS)

        paths = self._paths_from_drop_value(value)
        accepted, rejected = split_dropped_paths(paths)

        if not accepted:
            msg = _tr("drop_no_exe", "Aucun fichier .exe dans ce dépôt")
            self.toast.warning(msg)
            self.status.set_text(msg)
            return False

        # Ne pas bloquer le thread GTK : find_proton() peut être lent.
        threading.Thread(
            target=self._drop_import_worker,
            args=(accepted, rejected),
            daemon=True,
        ).start()
        return True

    def _drop_import_worker(self, accepted, rejected):
        added, skipped, failed = [], [], []

        try:
            cached_proton = find_proton()   # un seul appel pour tout le dépôt
        except Exception as e:
            logger.error(f"Drop import: find_proton failed: {e}")
            cached_proton = None            # add_game_ux() retentera lui-même

        for path in accepted:
            try:
                config_path, _gid = get_game_config_path(path)
                if Path(config_path).is_file():
                    skipped.append(path)    # déjà dans la bibliothèque
                    continue

                game = add_game_ux(path, proton=cached_proton)
                added.append(game.get("name") or Path(path).stem)
            except Exception as e:
                failed.append(path)
                logger.error(f"Drop import failed for {path}: {e}")

        GLib.idle_add(self._on_drop_import_done, added, skipped, failed, rejected)

    def _on_drop_import_done(self, added, skipped, failed, rejected):
        if added:
            self.refresh_games()   # une seule fois, quel que soit le nombre

        self._report_drop_result(added, skipped, failed, rejected)
        return False   # GLib.idle_add : ne pas se répéter

    def _report_drop_result(self, added, skipped, failed, rejected):
        if added:
            if len(added) == 1:
                text = tr("game_added_to_library", name=added[0])
            else:
                text = _tr(
                    "drop_games_added",
                    "{count} jeux ajoutés à la bibliothèque",
                    count=len(added),
                )
            self.toast.success(text)
            self.status.set_text(text)

        if skipped:
            text = _tr(
                "drop_already_present",
                "{count} jeu(x) déjà dans la bibliothèque",
                count=len(skipped),
            )
            (self.toast.info if added else self.toast.warning)(text)
            if not added:
                self.status.set_text(text)

        if failed:
            self.toast.error(
                _tr("drop_failed", "{count} fichier(s) n'ont pas pu être ajoutés",
                    count=len(failed))
            )

        if rejected:
            self.toast.warning(
                _tr("drop_ignored", "{count} fichier(s) ignoré(s) (pas un .exe)",
                    count=len(rejected))
            )
