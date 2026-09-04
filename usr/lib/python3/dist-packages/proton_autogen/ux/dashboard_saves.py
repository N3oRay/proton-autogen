"""
proton_autogen/ux/dashboard_saves.py

DashboardSavesMixin -- GTK4 dialog for the end-of-session save-backup
prompt (proton_autogen.save_prompt / save_detection / save_backup).

Wiring, already applied in dashboard.py:

    from proton_autogen.ux.dashboard_saves import DashboardSavesMixin

    class Dashboard(DashboardMiniMixin, DashboardUIMixin, ...,
                     DashboardSavesMixin, Gtk.ApplicationWindow):
        def __init__(self, app):
            ...
            notifications.set_callback(self.notify_toast)
            self._init_save_prompt_bridge()   # <- registers this mixin
            ...

session.finalize_session() runs on the game-launch thread (backend.run()
is invoked off the GTK main thread so the UI stays responsive during a
blocking Proton call), so the callback save_prompt_center invokes here
must marshal back onto the GTK main loop -- exactly like notify.py
already does for toasts, via GLib.idle_add.
"""

import threading
from datetime import datetime
from pathlib import Path

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gio

from proton_autogen.i18n import tr
from proton_autogen.notify import notifications
from proton_autogen.core import get_prefix_path
from proton_autogen.save_detection import detect_save_paths, compute_save_fingerprint
from proton_autogen.save_prompt import (
    save_prompt_center,
    resolve_game_key,
    GameTarget,
    SavePromptPayload,
)
from proton_autogen.save_backup import create_backup, list_backups, backup_archive_path


class DashboardSavesMixin:
    """Mixed into Dashboard. Expects `self` to be usable as a GTK
    `transient_for` window (i.e. Dashboard itself is a Gtk.Window /
    Gtk.ApplicationWindow subclass)."""

    # -------------------------
    # Wiring
    # -------------------------
    def _init_save_prompt_bridge(self):
        save_prompt_center.set_callback(self._on_save_prompt_requested)

    def _on_save_prompt_requested(self, payload: SavePromptPayload):
        # Called from the game-launch worker thread. GLib.idle_add
        # marshals dialog creation back onto the GTK main loop.
        GLib.idle_add(self._show_save_backup_dialog, payload)
        return False

    # -------------------------
    # Dialog
    # -------------------------
    def _show_save_backup_dialog(self, payload: SavePromptPayload):
        game_name = payload.game_name or Path(payload.exe_path).stem
        multi = len(payload.locations) > 1

        if payload.is_legacy:
            title = tr("save_memories_title") or "💾 Save your memories"
            body = tr("save_memories_body", game=game_name) or (
                f"We found save data for this game.\n"
                f"Your progress may be worth keeping."
            )
        elif multi:
            title = tr("save_backup_multi_title") or "💾 Save files detected"
            body = tr("save_backup_multi_body") or "We found save data in:"
        else:
            title = tr("save_backup_title") or "💾 Save your progress?"
            body = tr("save_backup_body") or (
                "Your save files were modified during this session."
            )

        dialog = Gtk.Window(
            transient_for=self,
            modal=True,
            resizable=False,
            title=title,
        )
        dialog.add_css_class("save-backup-dialog")
        dialog.set_default_size(440, -1)

        box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=10,
            margin_top=16,
            margin_bottom=16,
            margin_start=16,
            margin_end=16,
        )

        title_label = Gtk.Label()
        title_label.set_markup(f"<b>{GLib.markup_escape_text(title)}</b>")
        title_label.set_xalign(0)
        box.append(title_label)

        body_label = Gtk.Label(label=body)
        body_label.set_xalign(0)
        body_label.set_wrap(True)
        box.append(body_label)

        # One row per detected location, using its human-friendly label
        # (e.g. "BASEQ2/SAVE", "Saved Games/MyGame") rather than the
        # full absolute path, to keep the dialog readable.
        for loc in payload.locations:
            row = Gtk.Label(label=f"`{loc.label}`")
            row.add_css_class("save-location-path")
            row.set_xalign(0)
            row.set_wrap(True)
            row.set_selectable(True)
            box.append(row)

        button_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        button_row.set_halign(Gtk.Align.END)

        not_now_btn = Gtk.Button(label=tr("not_now") or "Not now")
        not_now_btn.add_css_class("alternative-action")
        not_now_btn.connect("clicked", self._on_save_backup_dismissed, dialog, payload)

        backup_label = (
            (tr("backup_all") or "Backup all") if multi
            else (tr("backup_saves") or "Backup saves")
        )
        backup_btn = Gtk.Button(label=backup_label)
        backup_btn.add_css_class("suggested-action")
        backup_btn.connect("clicked", self._on_save_backup_confirmed, dialog, payload)

        button_row.append(not_now_btn)
        button_row.append(backup_btn)
        box.append(button_row)

        dialog.set_child(box)
        dialog.present()

        return False  # GLib.idle_add: run once, don't repeat

    # -------------------------
    # Manual "Memory" save manager
    # -------------------------
    # Entry point wired from game_editor.py's "🧠 Memory" button:
    #
    #     editor.on_memory_requested = self._on_memory_requested
    #
    # (same pattern already used for editor.on_protondb_requested,
    # wherever GameEditor is instantiated).
    def _on_memory_requested(self, game: dict):
        self.open_save_manager(game)

    def open_save_manager(self, game: dict, game_id: "str | None" = None):
        """Opens the save manager window for a game on demand. Unlike
        the automatic end-of-session dialog, this always opens (no
        fingerprint gating) and additionally shows this game's backup
        history, so the user can find a save they backed up earlier.

        `game_id` should be the same value passed to backend.run(...,
        game_id=...) when this game is launched, so the history/
        fingerprint lookups line up exactly with the automatic flow.
        Leave it None if you don't have it handy -- both paths then
        fall back to the exe path consistently either way (see
        save_prompt.resolve_game_key)."""

        exe_path = game.get("path")
        if not exe_path:
            return

        game_name = game.get("name") or Path(exe_path).stem
        prefix_mode = game.get("prefix", {}).get("name", "main")

        try:
            prefix_path = get_prefix_path(prefix_mode, exe_path)
        except Exception:
            prefix_path = None

        key = resolve_game_key(exe_path, game_id)

        try:
            target = GameTarget(exe_path=exe_path, prefix_path=prefix_path, name=game_name)
            locations = detect_save_paths(target)
        except Exception:
            locations = []

        self._show_save_manager_dialog(key, game_name, locations)

    def _show_save_manager_dialog(self, key: str, game_name: str, locations: list):
        title = tr("memory_window_title", game=game_name) or f"\U0001F9E0 Memory — {game_name}"

        dialog = Gtk.Window(
            transient_for=self,
            modal=False,
            resizable=True,
            title=title,
        )
        dialog.add_css_class("save-manager-dialog")
        dialog.set_default_size(460, 680)

        outer = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=14,
            margin_top=16,
            margin_bottom=16,
            margin_start=16,
            margin_end=16,
        )

        header = Gtk.Label()
        header.set_markup(f"<b>{GLib.markup_escape_text(title)}</b>")
        header.set_xalign(0)
        outer.append(header)

        # --- Current save data ---
        current_label = Gtk.Label(label=tr("memory_current_saves_section") or "Current save data")
        current_label.add_css_class("title-5")
        current_label.set_xalign(0)
        outer.append(current_label)

        if locations:
            for loc in locations:
                row = Gtk.Label(label=f"`{loc.label}`")
                row.add_css_class("save-location-path")
                row.set_xalign(0)
                row.set_wrap(True)
                row.set_selectable(True)
                outer.append(row)

            backup_now_btn = Gtk.Button(label=tr("memory_backup_now") or "Backup now")
            backup_now_btn.add_css_class("suggested-action")
            backup_now_btn.set_halign(Gtk.Align.START)
            backup_now_btn.connect(
                "clicked", self._on_manual_backup_clicked, key, locations, dialog
            )
            outer.append(backup_now_btn)
        else:
            empty_label = Gtk.Label(
                label=tr("memory_no_current_saves") or "No save data detected for this game."
            )
            empty_label.set_xalign(0)
            empty_label.add_css_class("dim-label")
            outer.append(empty_label)

        outer.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))

        # --- Backup history ---
        history_label = Gtk.Label(label=tr("memory_history_section") or "Previous backups")
        history_label.add_css_class("title-5")
        history_label.set_xalign(0)
        outer.append(history_label)

        history_scroll = Gtk.ScrolledWindow()
        history_scroll.set_vexpand(True)
        history_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        history_list = Gtk.ListBox()
        history_list.add_css_class("save-history-list")
        history_list.set_selection_mode(Gtk.SelectionMode.NONE)
        history_scroll.set_child(history_list)
        outer.append(history_scroll)

        dialog.set_child(outer)
        # Stashed on the window instance so a manual backup made from
        # this same dialog can refresh the visible list in place,
        # without closing/reopening the whole window.
        dialog._history_list = history_list

        self._populate_history_list(history_list, key)

        dialog.present()

    def _populate_history_list(self, history_list: Gtk.ListBox, key: str):
        child = history_list.get_first_child()
        while child is not None:
            nxt = child.get_next_sibling()
            history_list.remove(child)
            child = nxt

        entries = list_backups(key)

        if not entries:
            row = Gtk.Label(label=tr("memory_no_history") or "No backups yet.")
            row.add_css_class("dim-label")
            row.set_xalign(0)
            row.set_margin_top(6)
            row.set_margin_bottom(6)
            history_list.append(row)
            return

        # Most recent first -- list_backups() returns oldest-first.
        for entry in reversed(entries):
            row_box = Gtk.Box(
                orientation=Gtk.Orientation.HORIZONTAL,
                spacing=10,
                margin_top=6,
                margin_bottom=6,
                margin_start=4,
                margin_end=4,
            )

            text_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            text_box.set_hexpand(True)

            date_row = Gtk.Label(label=self._format_backup_date(entry.get("created_at", "")))
            date_row.set_xalign(0)
            date_row.add_css_class("save-history-date")

            archive_row = Gtk.Label(label=entry.get("archive", ""))
            archive_row.set_xalign(0)
            archive_row.add_css_class("dim-label")
            archive_row.set_selectable(True)

            text_box.append(date_row)
            text_box.append(archive_row)

            # Open button + folder path displayed underneath
            action_box = Gtk.Box(
                orientation=Gtk.Orientation.VERTICAL,
                spacing=3,
            )
            action_box.set_halign(Gtk.Align.END)

            open_btn = Gtk.Button(label=tr("memory_open_folder") or "Open folder")
            open_btn.add_css_class("suggested-action")
            open_btn.connect(
                "clicked", self._on_open_backup_folder, key, entry.get("archive", "")
            )

            folder = backup_archive_path(
                key, entry.get("archive", "")
            ).parent

            path_label = Gtk.Label(label=str(folder))
            path_label.add_css_class("dim-label")
            path_label.add_css_class("save-backup-path")
            path_label.set_xalign(1)
            path_label.set_wrap(True)
            path_label.set_selectable(True)

            action_box.append(open_btn)
            action_box.append(path_label)

            row_box.append(text_box)
            row_box.append(action_box)
            history_list.append(row_box)

    @staticmethod
    def _format_backup_date(iso_string: str) -> str:
        try:
            return datetime.fromisoformat(iso_string).strftime("%Y-%m-%d %H:%M")
        except (ValueError, TypeError):
            return iso_string or "?"

    def _on_open_backup_folder(self, _btn, key: str, archive_name: str):
        try:
            folder = backup_archive_path(key, archive_name).parent
            uri = folder.as_uri()

            Gio.AppInfo.launch_default_for_uri(uri, None)

        except Exception as exc:
            print(f"Could not open backup folder: {exc}")

    def _on_manual_backup_clicked(self, btn, key: str, locations: list, dialog):
        btn.set_sensitive(False)

        def _do_backup():
            archive_path = create_backup(key, locations)
            fingerprint = compute_save_fingerprint(locations)
            GLib.idle_add(
                self._on_manual_backup_finished, archive_path, key, fingerprint, dialog, btn
            )

        threading.Thread(target=_do_backup, daemon=True).start()

    def _on_manual_backup_finished(self, archive_path, key, fingerprint, dialog, btn):
        btn.set_sensitive(True)

        if archive_path:
            # A manual backup counts as "seen": this avoids the automatic
            # end-of-session prompt firing again right after for the
            # exact same, now-backed-up, save state.
            save_prompt_center.acknowledge(key, fingerprint)

            notifications.notify(
                "info",
                tr("save_backup_done_title") or "Backup complete",
                tr("save_backup_done_message", path=str(archive_path))
                or f"Save data backed up to {archive_path}",
                ui=True,
            )

            history_list = getattr(dialog, "_history_list", None)
            if history_list is not None:
                self._populate_history_list(history_list, key)
        else:
            notifications.notify(
                "error",
                tr("save_backup_failed_title") or "Backup failed",
                tr("save_backup_failed_message")
                or "Could not back up save data. Check logs for details.",
                ui=True,
            )

        return False  # GLib.idle_add: run once, don't repeat

    # -------------------------
    # Actions
    # -------------------------
    def _on_save_backup_dismissed(self, _btn, dialog, payload: SavePromptPayload):
        # "Not now" still acknowledges the fingerprint: the goal is to
        # avoid re-nagging about the SAME unchanged save on every future
        # launch. A genuine new change to the save data will still
        # trigger the prompt again next time.
        save_prompt_center.acknowledge(payload.game_id, payload.fingerprint)
        dialog.close()

    def _on_save_backup_confirmed(self, _btn, dialog, payload: SavePromptPayload):
        dialog.close()

        # Zipping is I/O-bound and must not block the GTK main loop,
        # consistent with how the rest of the app treats blocking work
        # (game launch itself runs off-thread too).
        def _do_backup():
            archive_path = create_backup(payload.game_id, payload.locations)
            GLib.idle_add(self._on_backup_finished, archive_path, payload)

        threading.Thread(target=_do_backup, daemon=True).start()

    def _on_backup_finished(self, archive_path, payload: SavePromptPayload):
        save_prompt_center.acknowledge(payload.game_id, payload.fingerprint)

        if archive_path:
            notifications.notify(
                "info",
                tr("save_backup_done_title") or "Backup complete",
                tr("save_backup_done_message", path=str(archive_path))
                or f"Save data backed up to {archive_path}",
                ui=True,
            )
        else:
            notifications.notify(
                "error",
                tr("save_backup_failed_title") or "Backup failed",
                tr("save_backup_failed_message")
                or "Could not back up save data. Check logs for details.",
                ui=True,
            )

        return False  # GLib.idle_add: run once, don't repeat
