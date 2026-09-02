"""
save_prompt.py

Bridges end-of-session save detection (save_detection.py) to the UI.

Mirrors the NotificationCenter pattern already used in notify.py: a
process-wide singleton holds an optional callback set by the Dashboard
at startup. session.py can therefore trigger a save-backup prompt
without importing GTK or knowing anything about how it's displayed --
exactly like notifications.notify() already does for toasts.

This module has NO gi/GTK import on purpose, so it stays safe to call
from headless CLI runs (`--run`): detection still happens (cheap, since
save_detection.py caps its scan depth), but with no callback registered
nothing is shown -- we just quietly remember the fingerprint so the
next launch doesn't re-detect the same unchanged save data.
"""

from __future__ import annotations

import datetime
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

from proton_autogen.config import CONFIG_DIR
from proton_autogen.save_detection import (
    SaveLocation,
    detect_save_paths,
    compute_save_fingerprint,
    has_save_changed,
)
from proton_autogen.utils.logger import StructuredLogger

logger = StructuredLogger("proton-autogen.save_prompt")

_FINGERPRINTS_FILE = Path(CONFIG_DIR) / "save-fingerprints.json"

# A game is treated as "legacy" (softer "Save your memories" wording)
# once it is at least this many years old. Simple heuristic for the
# MVP -- no real release-date database is required to use it; callers
# without release-year data simply never trigger the legacy wording.
LEGACY_GAME_AGE_YEARS = 10


@dataclass
class SavePromptPayload:
    """Everything the UI layer needs to build the backup dialog."""

    exe_path: str
    game_id: str
    game_name: Optional[str]
    locations: list[SaveLocation]
    fingerprint: str
    is_legacy: bool = False


class GameTarget:
    """Minimal shim so detect_save_paths() (which expects a `game`-like
    object exposing exe_path/prefix_path/name) can be driven from plain
    parameters, without coupling this module to the app's real Game
    model. Public so other callers -- e.g. the manual "Memory" save
    manager in dashboard_saves.py -- can reuse it instead of duplicating
    the same three-attribute shim."""

    def __init__(self, exe_path: str, prefix_path: Optional[str] = None, name: Optional[str] = None):
        self.exe_path = exe_path
        self.prefix_path = prefix_path
        self.name = name


# Kept for backward compatibility with any earlier internal references.
_FakeGame = GameTarget


def resolve_game_key(exe_path: str, game_id: Optional[str] = None) -> str:
    """Canonical key used to store/retrieve save fingerprints and backup
    history for a game. Centralized here so every caller -- the automatic
    end-of-session prompt (session.finalize_session -> maybe_prompt) and
    the manual "Memory" save manager opened from the game editor -- agree
    on the same identity for a given game. If you pass a stable game_id
    when launching (backend.run(..., game_id=...)), pass that SAME value
    here too; otherwise both fall back to exe_path and stay consistent
    with each other anyway."""
    return game_id or exe_path


class SavePromptCenter:
    """Process-wide bridge between save detection and the UI. Same shape
    as notify.NotificationCenter: set_callback() once at startup, then
    call maybe_prompt() from anywhere with no GTK import required."""

    def __init__(self) -> None:
        self._callback: Optional[Callable[[SavePromptPayload], None]] = None

    def set_callback(self, cb: Optional[Callable[[SavePromptPayload], None]]) -> None:
        self._callback = cb

    # -------------------------
    # Fingerprint persistence
    # -------------------------
    def _load_fingerprints(self) -> dict:
        try:
            with open(_FINGERPRINTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            return {}

    def _store_fingerprint(self, key: str, fingerprint: str) -> None:
        data = self._load_fingerprints()
        data[key] = fingerprint
        try:
            os.makedirs(_FINGERPRINTS_FILE.parent, exist_ok=True)
            with open(_FINGERPRINTS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except OSError as exc:
            logger.warning("Could not persist save fingerprint for %s: %s", key, exc)

    def acknowledge(self, game_id: str, fingerprint: str) -> None:
        """Called by the UI once the prompt has been shown and answered
        (whichever button the user picked -- 'Backup' or 'Not now'), so
        the same unchanged save data doesn't trigger the dialog again
        on the next launch. Only an actual future change re-triggers it."""
        if game_id:
            self._store_fingerprint(game_id, fingerprint)

    # -------------------------
    # Entry point
    # -------------------------
    def maybe_prompt(
        self,
        exe_path: str,
        prefix_path: Optional[str] = None,
        game_name: Optional[str] = None,
        game_id: Optional[str] = None,
        release_year: Optional[int] = None,
        enabled: bool = True,
    ) -> None:
        """Called at end-of-session (see session.finalize_session).
        Cheap no-op if the feature is disabled for this game, no save
        data is found, or nothing changed since the last prompt."""

        if not enabled:
            return

        try:
            game = _FakeGame(exe_path=exe_path, prefix_path=prefix_path, name=game_name)
            locations = detect_save_paths(game)
        except Exception as exc:
            # Detection must never break session finalization / stats.
            logger.warning("Save detection failed for %s: %s", exe_path, exc)
            return

        if not locations:
            return

        fingerprint = compute_save_fingerprint(locations)
        key = resolve_game_key(exe_path, game_id)
        previous = self._load_fingerprints().get(key)

        if not has_save_changed(previous, fingerprint):
            return

        if not self._callback:
            # Headless / no UI registered: there is nothing to show, and
            # we deliberately do NOT persist the fingerprint here. Only
            # acknowledge() -- called once the dialog has actually been
            # shown and answered -- is allowed to mark a fingerprint as
            # "seen". Persisting it here would silently swallow the
            # prompt forever: the next launch would compare against this
            # fingerprint, find no further change, and never show the
            # dialog even once the UI becomes available (e.g. right
            # after the mixin gets wired into Dashboard). The rescan
            # cost on future launches is cheap (depth-limited), so there
            # is no real downside to leaving it unpersisted.
            return

        is_legacy = bool(
            release_year
            and (datetime.date.today().year - release_year) >= LEGACY_GAME_AGE_YEARS
        )

        payload = SavePromptPayload(
            exe_path=exe_path,
            game_id=key,
            game_name=game_name,
            locations=locations,
            fingerprint=fingerprint,
            is_legacy=is_legacy,
        )

        self._callback(payload)


save_prompt_center = SavePromptCenter()
