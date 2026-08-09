#!/usr/bin/env python3
import re
import threading
import hashlib
from pathlib import Path
import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib

from proton_autogen.i18n import tr
from proton_autogen.lutris import export_game_to_lutris_yaml
from proton_autogen.progress import Progress
from proton_autogen.backend import run
from proton_autogen import process_manager
from proton_autogen.ux.game_editor import GameEditor
from proton_autogen.ux.dialogs import show_launch_dialog, hide_launch_dialog
from proton_autogen.ux.dialogs import open_game_file_dialog
from proton_autogen.editor import add_game_ux, rm_game_ux
from proton_autogen.utils.logger import StructuredLogger
logger = StructuredLogger("proton-autogen.ux.dashboard_actions")


class DashboardActionsMixin:
    """Actions métier du Dashboard (lancement, édition, suppression, export...).
    Doit être mixé avec une classe qui expose self.toast, self.status, self.spinner,
    self.show_export_dialog (DashboardDialogsMixin), self.refresh_games, self.lang,
    self.get_application().
    État de suivi du jeu en cours (un seul jeu suivi à la fois) :
        self._current_game_id
        self._current_game_name
    """

    @staticmethod
    def _sanitize_filename(name: str) -> str:
        name = name.strip()
        name = re.sub(r"[^\w\-_. ]", "_", name)
        name = name.replace(" ", "_")
        return name or "game"

    # -------------------------
    # EXPORT LUTRIS
    # -------------------------
    def export_lutris_handler(self, game):
        try:
            yaml_text = export_game_to_lutris_yaml(game)
            game_name = self._sanitize_filename(game.get("name", "game"))

            export_dir = Path.home() / ".local" / "share" / "proton-autogen" / "lutris_exports"
            export_dir.mkdir(parents=True, exist_ok=True)
            file_path = export_dir / f"{game_name}-lutris.yml"
            file_path.write_text(yaml_text, encoding="utf-8")

            logger.info(f"{tr('lutris_export_completed')}: {file_path}")
            self.show_export_dialog(file_path)
            self.toast.success(tr("lutris_export_completed"))

            return str(file_path)

        except Exception as e:
            logger.error(f"{tr('lutris_export_failed')}: {e}")
            self.toast.error(tr("lutris_export_failed"))
            return None


    # -------------------------
    # LAUNCH GAME
    # -------------------------
    def _close_launch_dialog(self):
        hide_launch_dialog(self)
        self.set_sensitive(True)
        self.status.set_text(tr("ready"))
        return False  # le timer ne se répète pas

    def launch_game(self, game):
        GLib.idle_add(self.spinner.start)
        GLib.idle_add(self.spinner.set_visible, True)

        if not game.get("path"):
            self.status.set_text(tr("missing_game_path"))
            self.toast.error(tr("missing_game_path"))
            GLib.idle_add(self.spinner.stop)
            GLib.idle_add(self.spinner.set_visible, False)
            return

        game_path = game["path"]
        game_id = hashlib.md5(game_path.encode()).hexdigest()
        name = game.get("name", tr("unknown_game"))

        self.status.set_text(tr("launching_game", name=name))
        self.set_sensitive(False)
        show_launch_dialog(self, name)

        # Ferme automatiquement après 3 secondes
        GLib.timeout_add_seconds(3, self._close_launch_dialog)

        # Le jeu devient "en cours" — lu par stop_running_game()
        # et par le binding du bouton Stop côté UI mixin.
        self._current_game_id = game_id
        self._current_game_name = name
        # Prise en charge muli run ---------------------
        if not hasattr(self, "_running_games"):
            self._running_games = {}   # game_id -> name

        self._running_games[game_id] = name
        #-----------------------------------------------
        GLib.idle_add(self._update_stop_button_state, True)

        def worker():
            progress = Progress(callback=self.progress_callback)

            # Le jeu est maintenant en cours d'exécution
            GLib.idle_add(
                self.status.set_text,
                tr("running_game", name=name),
            )

            try:
                run(game_path, progress=progress, game_id=game_id)

                # Le processus s'est terminé normalement
                GLib.idle_add(
                    self.status.set_text,
                    tr("game_finished", name=name),
                )

            except Exception as e:
                msg = str(e)

                GLib.idle_add(
                    self.status.set_text,
                    tr("launch_failed", error=msg),
                )

                logger.error(f"Launch error: {e}")

            finally:
                GLib.idle_add(self.spinner.stop)
                GLib.idle_add(self.spinner.set_visible, False)

                # Le jeu n'est plus en cours (fin normale, crash, ou arrêt manuel).
                # On ne réinitialise que si c'est toujours le même jeu suivi
                # (protection basique contre une course avec un lancement suivant).
                if getattr(self, "_current_game_id", None) == game_id:
                    self._current_game_id = None
                    self._current_game_name = None
                    #GLib.idle_add(self._update_stop_button_state, False)
                    self._running_games.pop(game_id, None)
                    GLib.idle_add(
                        self._update_stop_button_state,
                        bool(self._running_games)
                    )

        threading.Thread(target=worker, daemon=True).start()


    # -------------------------
    # STOP GAME — SELECTOR
    # -------------------------
    def _show_stop_selector(self, running):
        """
        Affiche une boîte de dialogue permettant de choisir quel jeu arrêter
        lorsque plusieurs jeux sont actuellement en cours d'exécution.

        running:
            dict {game_id: game_name}
        """

        if not running:
            self.toast.error(tr("no_active_game"))
            return

        dialog = Gtk.Dialog(
            title=tr("select_game_to_stop"),
            transient_for=self,
            modal=True,
        )

        dialog.set_default_size(420, -1)
        dialog.add_css_class("stop-dialog")

        content = dialog.get_content_area()
        content.set_margin_top(16)
        content.set_margin_bottom(16)
        content.set_margin_start(16)
        content.set_margin_end(16)

        # Texte explicatif
        label = Gtk.Label(
            label=tr("select_game_to_stop_detail"),
            wrap=True,
            xalign=0,
        )
        label.set_margin_bottom(12)
        content.append(label)

        # Liste des jeux
        list_box = Gtk.ListBox()
        list_box.set_selection_mode(Gtk.SelectionMode.SINGLE)
        list_box.add_css_class("boxed-list")

        # Conserve le mapping row -> game_id
        rows = {}

        for game_id, game_name in running.items():
            row = Gtk.ListBoxRow()

            row_box = Gtk.Box(
                orientation=Gtk.Orientation.HORIZONTAL,
                spacing=12,
            )
            row_box.set_margin_top(10)
            row_box.set_margin_bottom(10)
            row_box.set_margin_start(12)
            row_box.set_margin_end(12)

            name_label = Gtk.Label(
                label=game_name,
                xalign=0,
                hexpand=True,
            )

            row_box.append(name_label)
            row.set_child(row_box)

            list_box.append(row)
            rows[row] = game_id

        content.append(list_box)

        # Boutons
        btn_cancel = dialog.add_button(
            tr("cancel"),
            Gtk.ResponseType.CANCEL,
        )

        btn_stop = dialog.add_button(
            tr("stop_game"),
            Gtk.ResponseType.ACCEPT,
        )

        btn_cancel.add_css_class("section-toggle")
        btn_stop.add_css_class("section-toggle")
        btn_stop.add_css_class("destructive-action")

        # Désactivé tant qu'aucun jeu n'est sélectionné
        btn_stop.set_sensitive(False)

        # Active le bouton "Arrêter" lorsqu'un jeu est sélectionné
        def on_selection_changed(_list_box, _row):
            selected = list_box.get_selected_row()
            btn_stop.set_sensitive(selected is not None)

        list_box.connect("row-selected", on_selection_changed)

        def on_response(_dialog, response):
            if response != Gtk.ResponseType.ACCEPT:
                dialog.destroy()
                return

            selected_row = list_box.get_selected_row()

            if selected_row is None:
                return

            game_id = rows.get(selected_row)

            if not game_id:
                dialog.destroy()
                return

            game_name = running.get(
                game_id,
                tr("unknown_game"),
            )

            # Ferme le sélecteur avant d'afficher la confirmation
            dialog.destroy()

            # Confirmation finale
            self.confirm_stop_dialog(
                game_name,
                on_confirm=lambda: self.stop_running_game(game_id),
            )

        dialog.connect("response", on_response)

        # Double-clic sur un jeu = sélection + arrêt
        def on_row_activated(_list_box, row):
            game_id = rows.get(row)

            if not game_id:
                return

            game_name = running.get(
                game_id,
                tr("unknown_game"),
            )

            dialog.destroy()

            self.confirm_stop_dialog(
                game_name,
                on_confirm=lambda: self.stop_running_game(game_id),
            )

        list_box.connect("row-activated", on_row_activated)

        dialog.set_default_response(Gtk.ResponseType.CANCEL)
        dialog.present()



    # -------------------------
    # STOP GAME
    # -------------------------
    def confirm_stop_dialog_old(self, game_name, on_confirm):
        dialog = Gtk.AlertDialog()
        dialog.set_message(tr("confirm_stop_title"))
        dialog.set_detail(tr("confirm_stop_detail", name=game_name))
        dialog.set_buttons([tr("cancel"), tr("stop_game")])
        dialog.set_default_button(0)
        dialog.set_cancel_button(0)

        def on_response(source, result):
            try:
                choice = source.choose_finish(result)
            except GLib.Error:
                return
            if choice == 1:
                on_confirm()

        dialog.choose(self, None, on_response)

    def confirm_stop_dialog(self, game_name, on_confirm):
        dialog = Gtk.Dialog(
            title=tr("confirm_stop_title"),
            transient_for=self,
            modal=True,
        )
        dialog.set_default_size(360, -1)
        dialog.add_css_class("stop-dialog")

        content = dialog.get_content_area()
        content.set_margin_top(16)
        content.set_margin_bottom(16)
        content.set_margin_start(16)
        content.set_margin_end(16)
        content.append(Gtk.Label(label=tr("confirm_stop_detail", name=game_name), wrap=True))

        btn_cancel = dialog.add_button(tr("cancel"), Gtk.ResponseType.CANCEL)
        btn_stop = dialog.add_button(tr("stop_game"), Gtk.ResponseType.ACCEPT)

        # Style global partagé par les deux boutons
        for btn in (btn_cancel, btn_stop):
            btn.add_css_class("section-toggle") #section-toggle or  btn-stop-global or dialog-action-btn

        # Variante spécifique au bouton destructif
        btn_stop.add_css_class("destructive-action")

        dialog.set_default_response(Gtk.ResponseType.CANCEL)

        def on_response(source, response):
            if response == Gtk.ResponseType.ACCEPT:
                on_confirm()
            dialog.destroy()

        dialog.connect("response", on_response)
        dialog.present()

    def on_stop_button_clicked(self, _btn=None):
        running = getattr(self, "_running_games", {})

        if not running:
            self.toast.error(tr("no_active_game"))
            return

        if len(running) == 1:
            game_id, name = next(iter(running.items()))
            self.confirm_stop_dialog(name, on_confirm=lambda: self.stop_running_game(game_id))
        else:
            # Plusieurs jeux en cours : afficher une liste à choisir, ou tout arrêter
            self._show_stop_selector(running)

    def stop_running_game(self, game_id):
        name = getattr(self, "_running_games", {}).get(game_id, tr("unknown_game"))

        if process_manager.stop(game_id):
            logger.info("Stop requested by user", game_id=game_id, name=name)
            self.status.set_text(tr("stopping_game", name=name))
            self.toast.success(tr("stopping_game", name=name))
        else:
            logger.warning("Stop requested but process already gone", game_id=game_id)
            self._running_games.pop(game_id, None)
            GLib.idle_add(self._update_stop_button_state, bool(self._running_games))


    # -------------------------
    # EDIT GAME
    # -------------------------
    def edit_game(self, game):
        editor = GameEditor(self.get_application(), game, self.lang)
        self.status.set_text(tr("updating"))

        def after_save(game):
            self.refresh_games()

        def on_close(_editor):
            self.status.set_text(tr("ready"))

        editor.on_saved = after_save
        editor.connect("destroy", lambda *_: on_close(editor))
        editor.present()

    # -------------------------
    # DELETE GAME
    # -------------------------
    def delete_game(self, game):
        game_name = game.get("name", tr("unknown_game"))

        if rm_game_ux(game.get("path"), game.get("config_path")):
            self.refresh_games()
            self.status.set_text(
                tr("game_removed_from_library", name=game_name)
            )
            self.toast.success(
                tr("game_removed_from_library", name=game_name)
            )
        else:
            self.status.set_text(tr("unable_to_remove_game"))
            self.toast.error(tr("unable_to_remove_game"))

    # -------------------------
    # ADD GAME
    # -------------------------
    def on_add_game(self, _btn):
        open_game_file_dialog(self, self._on_file_selected)

    def _on_file_selected(self, path):
        if not path:
            return

        try:
            game = add_game_ux(path)
            self.status.set_text(
                tr("game_added", name=game["name"])
            )
            self.refresh_games()
            self.toast.success(
                tr("game_added_to_library", name=game["name"])
            )

        except Exception as e:
            self.status.set_text(tr("add_game_failed"))
            self.toast.error(tr("unable_to_add_game"))
            logger.error(f"Add game error: {e}")
