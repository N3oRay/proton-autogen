#!/usr/bin/env python3
import re
import threading
from pathlib import Path
from gi.repository import GLib

from proton_autogen.i18n import tr
from proton_autogen.lutris import export_game_to_lutris_yaml
from proton_autogen.progress import Progress
from proton_autogen.backend import run
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

        name = game.get("name", tr("unknown_game"))
        self.status.set_text(tr("launching_game", name=name))
        self.set_sensitive(False)
        show_launch_dialog(self, name)

        # Ferme automatiquement après 3 secondes
        GLib.timeout_add_seconds(3, self._close_launch_dialog)

        def worker():
            progress = Progress(callback=self.progress_callback)

            # Le jeu est maintenant en cours d'exécution
            GLib.idle_add(
                self.status.set_text,
                tr("running_game", name=name),
            )

            try:
                run(game["path"], progress=progress)

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
