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
from pathlib import Path

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib

from proton_autogen.i18n import tr
from proton_autogen.notify import notifications
from proton_autogen.save_prompt import save_prompt_center, SavePromptPayload
from proton_autogen.save_backup import create_backup


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
        dialog.set_default_size(420, -1)

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
