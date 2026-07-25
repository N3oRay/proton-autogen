#!/usr/bin/env python3
import re
import threading
from pathlib import Path
from gi.repository import GLib

from proton_autogen.lutris import export_game_to_lutris_yaml
from proton_autogen.progress import Progress
from proton_autogen.backend import run
from proton_autogen.ux.game_editor import GameEditor
from proton_autogen.ux.dialogs import show_launch_dialog, hide_launch_dialog
from proton_autogen.ux.dialogs import open_game_file_dialog
from proton_autogen.editor import add_game_ux, rm_game_ux


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

            print(f"[OK] Export Lutris terminé: {file_path}")
            self.show_export_dialog(file_path)
            self.toast.success("Lutris export completed")

            return str(file_path)

        except Exception as e:
            print(f"[ERROR] Export Lutris échoué: {e}")
            self.toast.error("Lutris export failed")
            return None

    # -------------------------
    # LAUNCH GAME
    # -------------------------
    def _close_launch_dialog(self):
        hide_launch_dialog(self)
        self.set_sensitive(True)
        self.status.set_text("Ready")
        return False  # le timer ne se répète pas

    def launch_game(self, game):
        GLib.idle_add(self.spinner.start)
        GLib.idle_add(self.spinner.set_visible, True)

        if not game.get("path"):
            return

        name = game.get("name", "Unknown")
        self.status.set_text(f"Launching {name}...")
        self.set_sensitive(False)
        show_launch_dialog(self, name)

        # Ferme automatiquement après 3 secondes
        GLib.timeout_add_seconds(3, self._close_launch_dialog)

        def worker():
            progress = Progress(callback=self.progress_callback)

            try:
                run(game["path"], progress=progress)
            except Exception as e:
                msg = str(e)
                GLib.idle_add(
                    lambda: self.status.set_text(f"Launch failed: {msg}")
                )
                print("[UX] Launch error:", e)
            finally:
                GLib.idle_add(self.spinner.stop)
                GLib.idle_add(self.spinner.set_visible, False)
                GLib.idle_add(self.status.set_text, "Ready")

        threading.Thread(target=worker, daemon=True).start()

    # -------------------------
    # EDIT GAME
    # -------------------------
    def edit_game(self, game):
        editor = GameEditor(self.get_application(), game, self.lang)
        self.status.set_text("Updating...")

        def after_save(game):
            self.refresh_games()

        def on_close(_editor):
            self.status.set_text("Ready")

        editor.on_saved = after_save
        editor.connect("destroy", lambda *_: on_close(editor))
        editor.present()

    # -------------------------
    # DELETE GAME
    # -------------------------
    def delete_game(self, game):
        if rm_game_ux(game.get("path"), game.get("config_path")):
            self.refresh_games()
            self.status.set_text(f"{game['name']} removed from library")
            self.toast.success(f"{game['name']} removed from library")
        else:
            self.status.set_text("Unable to remove game")
            self.toast.error("Unable to remove game")

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
            self.status.set_text(f"{game['name']} added ✔")
            self.refresh_games()
            self.toast.success(f"{game['name']} added")

        except Exception as e:
            self.status.set_text("Add game failed")
            self.toast.error("Unable to add game")
            print("[UX] Add game error:", e)
