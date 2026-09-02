"""
save_backup.py

Creates local ZIP backups of detected save locations (save_detection.py).
Kept separate from dashboard_saves.py so the backup logic has no GTK
dependency and can be unit-tested / reused (e.g. from a future CLI
`--backup-saves <game>` command) on its own.
"""

from __future__ import annotations

import json
import os
import zipfile
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from proton_autogen.config import CONFIG_DIR
from proton_autogen.save_detection import SaveLocation
from proton_autogen.utils.logger import StructuredLogger

logger = StructuredLogger("proton-autogen.save_backup")

# Backups live under the data dir, not CONFIG_DIR: they can grow large
# and are user data, not configuration.
BACKUPS_ROOT = Path(os.path.expanduser("~/.local/share/proton-autogen/backups"))


def _safe_game_dir_name(game_id: str) -> str:
    """game_id may contain path separators (it can fall back to the exe
    path when no stable id exists -- see save_prompt.py). Turn it into
    a single safe path component."""
    return game_id.replace(os.sep, "_").replace(":", "_").replace(" ", "_")


def create_backup(game_id: str, locations: list[SaveLocation]) -> Path | None:
    """Zips every detected save location for a game into a single
    timestamped archive. Returns the archive path, or None if there was
    nothing to back up.

    Each location keeps its `label` (e.g. "BASEQ2/SAVE") as the root
    folder inside the archive, so multiple save locations for the same
    game (install-local + prefix, or several mission-pack saves) don't
    collide or overwrite each other inside the zip.
    """
    if not locations:
        return None

    game_dir = BACKUPS_ROOT / _safe_game_dir_name(game_id)
    game_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    archive_path = game_dir / f"backup-{timestamp}.zip"

    # Two backups within the same second (e.g. clicking "Backup now"
    # twice quickly, or a manual backup right after an automatic one)
    # would otherwise silently overwrite the earlier archive, since the
    # timestamp only has second-level resolution. Disambiguate with a
    # numeric suffix rather than losing the earlier backup.
    if archive_path.exists():
        n = 2
        while True:
            candidate = game_dir / f"backup-{timestamp}-{n}.zip"
            if not candidate.exists():
                archive_path = candidate
                break
            n += 1

    try:
        with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for loc in locations:
                root_name = loc.label.replace(os.sep, "/").replace("\\", "/")
                if loc.path.is_file():
                    zf.write(loc.path, arcname=f"{root_name}")
                elif loc.path.is_dir():
                    # followlinks=False: Wine prefixes commonly contain
                    # junction-like symlinks; we don't want to follow
                    # them blindly into unrelated parts of the prefix.
                    for dirpath, _dirs, files in os.walk(loc.path, followlinks=False):
                        rel_dir = os.path.relpath(dirpath, loc.path)
                        for fname in files:
                            src = Path(dirpath) / fname
                            if rel_dir == ".":
                                arcname = f"{root_name}/{fname}"
                            else:
                                arcname = f"{root_name}/{rel_dir}/{fname}"
                            try:
                                zf.write(src, arcname=arcname)
                            except OSError as exc:
                                logger.warning("Skipping unreadable save file %s: %s", src, exc)
    except OSError as exc:
        logger.error("Failed to create save backup for %s: %s", game_id, exc)
        try:
            archive_path.unlink(missing_ok=True)
        except OSError:
            pass
        return None

    _append_history_entry(game_dir, archive_path, locations)
    return archive_path


def _append_history_entry(game_dir: Path, archive_path: Path, locations: list[SaveLocation]) -> None:
    """Small JSON history file per game, listing past backups. Kept
    minimal on purpose -- a future "restore" / history UI (v0.3/v0.4)
    reads this file rather than re-deriving history from the filesystem."""
    history_file = game_dir / "history.json"
    entries = []
    try:
        with open(history_file, "r", encoding="utf-8") as f:
            entries = json.load(f)
    except (OSError, json.JSONDecodeError):
        entries = []

    entries.append({
        "archive": archive_path.name,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "locations": [asdict(loc) | {"path": str(loc.path)} for loc in locations],
    })

    try:
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(entries, f, indent=2, default=str)
    except OSError as exc:
        logger.warning("Could not update backup history for %s: %s", game_dir, exc)


def list_backups(game_id: str) -> list[dict]:
    """Returns the backup history entries for a game, most recent last."""
    game_dir = BACKUPS_ROOT / _safe_game_dir_name(game_id)
    history_file = game_dir / "history.json"
    try:
        with open(history_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return []


def backup_dir_for(game_id: str) -> Path:
    """Public resolver for a game's backup directory (where its .zip
    archives and history.json live). Lets the UI offer an 'Open folder'
    action, or point a file manager at the whole history, without
    duplicating the private naming scheme used internally."""
    return BACKUPS_ROOT / _safe_game_dir_name(game_id)


def backup_archive_path(game_id: str, archive_name: str) -> Path:
    """Full path to a specific archive listed in list_backups()'s
    'archive' field. Used by the UI to open/reveal a single backup."""
    return backup_dir_for(game_id) / archive_name
