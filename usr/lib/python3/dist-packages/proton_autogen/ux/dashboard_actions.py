#!/usr/bin/env python3

#dashboard_actions.py
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
from proton_autogen.backend import run, fetch_protondb_info
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
    self.get_application(), et self._update_stop_button_state(is_running: bool)
    (DashboardUIMixin).

    État de suivi des applications en cours :
        self._running_games : dict[game_id, name]
            Source de vérité pour le suivi multi-jeux. Peuplé/vidé dans
            launch_game() ; lu par on_stop_button_clicked(), _show_stop_selector()
            et stop_running_game(). C'est ce dict (pas les deux attributs
            ci-dessous) qui pilote l'état du bouton Stop.

        self._current_game_id / self._current_game_name : Optional[str]
            Références au dernier jeu lancé, à titre indicatif seulement
            (ex. affichage). Ne pas s'appuyer dessus pour déterminer si un
            jeu tourne encore : plusieurs jeux peuvent être actifs en
            parallèle et ces deux attributs sont écrasés à chaque appel de
            launch_game(), donc ils ne reflètent pas fiablement l'ensemble
            des jeux en cours.
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
    # PROTONDB REQUEST
    # -------------------------
    def _on_protondb_requested(self, game):
        app_id = game.get("app_id")
        if not app_id:
            self.toast.warning(tr("no_app_id_configured"))
            return

        def worker():
            info = fetch_protondb_info(app_id)
            GLib.idle_add(self._apply_protondb_result, game, info)

        threading.Thread(target=worker, daemon=True).start()

    def _apply_protondb_result(self, game, info):
        if info:
            game["protondb"] = info
            self.game_list.update_game(game)   # méthode déjà existante dans game_list.py
        else:
            self.toast.warning(tr("protondb_fetch_failed"))
        return False  # important pour GLib.idle_add


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
        GLib.idle_add(self._update_stop_button_state, True, name)

        def worker():
            progress = Progress(callback=self.progress_callback)

            # Le jeu est maintenant en cours d'exécution
            GLib.idle_add(
                self.status.set_text,
                tr("running_game", name=name),
            )

            try:
                returncode = run(game_path, progress=progress, game_id=game_id)

                # run_game_proton()/run_process() retournent un code de
                # sortie entier plutôt que de lever une exception : un
                # crash (code non nul) passait donc jusqu'ici totalement
                # inaperçu ici, traité comme un succès silencieux.
                if returncode:
                    GLib.idle_add(
                        self.status.set_text,
                        tr("game_crashed", name=name, code=returncode),
                        "error",
                    )
                    GLib.idle_add(self.toast.error, tr("game_crashed", name=name, code=returncode))
                    logger.error(f"Game exited with non-zero code: {name} ({returncode})")

                    if hasattr(self, "notify_game_crashed"):
                        GLib.idle_add(self.notify_game_crashed, name, returncode)
                else:
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

                if hasattr(self, "notify_game_crashed"):
                    GLib.idle_add(self.notify_game_crashed, name, msg)

            finally:
                GLib.idle_add(self.spinner.stop)
                GLib.idle_add(self.spinner.set_visible, False)

                if getattr(self, "_current_game_id", None) == game_id:
                    self._current_game_id = None
                    self._current_game_name = None

                def _cleanup_running_state():
                    self._running_games.pop(game_id, None)
                    self._update_stop_button_state(bool(self._running_games))
                # Toujours recalculer l'état du bouton, peu importe quel jeu vient de finir
                GLib.idle_add(_cleanup_running_state)

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
        stopping = getattr(self, "_stopping_games", set())

        # On ne propose que les jeux pas déjà en cours d'arrêt
        stoppable = {gid: name for gid, name in running.items() if gid not in stopping}

        if not stoppable:
            if running:
                # Tous les jeux restants sont déjà en cours d'arrêt
                self.toast.error(tr("stop_already_in_progress"))
            else:
                self.toast.error(tr("no_active_game"))
            return

        if len(stoppable) == 1:
            game_id, name = next(iter(stoppable.items()))
            self.confirm_stop_dialog(name, on_confirm=lambda: self.stop_running_game(game_id))
        else:
            self._show_stop_selector(stoppable)

    def stop_running_game(self, game_id):
        name = getattr(self, "_running_games", {}).get(game_id, tr("unknown_game"))

        if not hasattr(self, "_stopping_games"):
            self._stopping_games = set()

        if game_id in self._stopping_games:
            self.toast.error(tr("already_stopping", name=name))
            return

        self._stopping_games.add(game_id)

        self.status.set_text(tr("stopping_game", name=name))
        self.toast.success(tr("stopping_game", name=name))

        def worker():
            try:
                stopped = process_manager.stop(game_id)

                if stopped:
                    logger.info("Stop requested by user", game_id=game_id, name=name)
                else:
                    logger.warning("Stop requested but process already gone", game_id=game_id)

                # Que stop() ait réussi ou trouvé le process déjà mort,
                # process_manager a fait tout ce qu'il pouvait faire.
                # On ne dépend plus du Popen original (géré par launch_game)
                # pour retirer le jeu de la liste : on le fait ici, immédiatement.
                def _finalize():
                    self._running_games.pop(game_id, None)
                    self._stopping_games.discard(game_id)
                    self._update_stop_button_state(bool(self._running_games))

                GLib.idle_add(_finalize)

            except Exception:
                # Filet de sécurité : ne jamais laisser _stopping_games bloqué
                # si process_manager.stop() lève une exception inattendue.
                GLib.idle_add(self._stopping_games.discard, game_id)
                GLib.idle_add(self._update_stop_button_state, bool(self._running_games))
                raise

        threading.Thread(target=worker, daemon=True).start()


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
