"""
save_detection.py

Detection of save-game locations for games launched through Proton-Autogen.

Three independent, complementary strategies are used, since legacy games
(DOS/Win95-era) and modern Windows games follow very different conventions:

  1. Install-local save FILES sitting directly next to the game executable
     (e.g. Command & Conquer: Alerte Rouge -> SAVEGAME.000, SAVEGAME.001 ...)

  2. Install-local save DIRECTORIES nested a few levels under the install
     dir, identified by name rather than fixed path
     (e.g. Fallout -> DATA/SAVEGAME/SLOT01,
           Quake II -> BASEQ2/SAVE/{CURRENT,SAVE0..SAVE5},
           Quake II mission packs -> XATRIX/SAVE, ROGUE/SAVE, ...)

  3. Prefix-standard save locations following modern Windows conventions,
     found under drive_c/users/<user>/ inside the game's Wine/Proton
     prefix (Saved Games, Documents/My Games, AppData/Local, AppData/Roaming).

This module intentionally favors generic name/pattern matching over a
per-game path database: new legacy titles are expected to "just work"
without maintaining an ever-growing lookup table. False positives are
tolerated (worst case: an unnecessary backup); false negatives are not
(worst case: silent data loss), so detection stays permissive.

Fingerprinting is done by walking the full save subtree and hashing
(relative path, mtime, size) per file rather than trusting parent
directory sizes -- `ls -l` can report a directory as 0 bytes even when
it contains real files (observed on ext4 with certain Quake II save
slots), so directory-level stat() alone is not a reliable change signal.
"""

from __future__ import annotations

import hashlib
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Patterns
# ---------------------------------------------------------------------------

# File-name globs for saves written directly into the install directory.
# Case-insensitive matching is applied at call time (see _matches_any_glob).
INSTALL_LOCAL_SAVE_FILE_PATTERNS: tuple[str, ...] = (
    "savegame.*",   # Command & Conquer / Westwood engine (SAVEGAME.000 ...)
    "*.sav",
    "*.sgm",
    "save*.dta",
)

# Directory names (case-insensitive) that indicate a save folder when found
# nested under the install directory. Matched by exact (lowercased) name,
# not by glob, to avoid accidentally matching unrelated asset folders.
SAVE_DIR_NAMES: frozenset[str] = frozenset({
    "savegame",
    "savegames",
    "save",
    "saves",
})

# Sub-paths checked under drive_c/users/<user>/ inside a Wine/Proton prefix.
PREFIX_USER_SAVE_SUBPATHS: tuple[str, ...] = (
    "Saved Games",
    "Documents/My Games",
    "My Documents",       # older Wine prefixes
    "AppData/Local",
    "AppData/Roaming",
)

# How many directory levels below the install dir / prefix save subpath we
# are willing to recurse into when looking for a named save directory.
# Keeps the scan fast on large, asset-heavy install directories.
MAX_SCAN_DEPTH = 3


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class SaveLocation:
    """A single detected save location, ready to be shown to the user
    and/or backed up."""

    path: Path
    kind: str                      # "install_file" | "install_dir" | "prefix_dir"
    label: str = field(default="")  # human-friendly, e.g. relative folder name

    def __post_init__(self) -> None:
        if not self.label:
            self.label = self.path.name


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _matches_any_glob(name: str, patterns: tuple[str, ...]) -> bool:
    import fnmatch
    lname = name.lower()
    return any(fnmatch.fnmatch(lname, pat) for pat in patterns)


def _dir_has_content(path: Path) -> bool:
    """True if the directory contains at least one entry. Cheap check,
    avoids proposing empty save folders for backup."""
    try:
        next(path.iterdir())
        return True
    except (StopIteration, OSError, PermissionError):
        return False


# ---------------------------------------------------------------------------
# Strategy 1: install-local save files
# ---------------------------------------------------------------------------

def find_install_local_save_files(install_dir: Path) -> list[SaveLocation]:
    """Files matching a known save-file pattern directly at the root of
    the install directory (e.g. SAVEGAME.000-004 for Command & Conquer)."""
    if not install_dir.is_dir():
        return []

    found: list[SaveLocation] = []
    try:
        entries = list(install_dir.iterdir())
    except (OSError, PermissionError) as exc:
        logger.debug("Cannot list %s: %s", install_dir, exc)
        return []

    for entry in entries:
        try:
            if entry.is_file() and _matches_any_glob(entry.name, INSTALL_LOCAL_SAVE_FILE_PATTERNS):
                found.append(SaveLocation(path=entry, kind="install_file"))
        except (OSError, PermissionError):
            continue

    return found


# ---------------------------------------------------------------------------
# Strategy 2: install-local save directories, nested by name
# ---------------------------------------------------------------------------

def find_install_nested_save_dirs(
    install_dir: Path,
    max_depth: int = MAX_SCAN_DEPTH,
) -> list[SaveLocation]:
    """Directories named SAVE / SAVEGAME / Saves / SaveGames (any casing),
    found at limited depth under the install directory. Covers engines
    that keep saves in a dedicated subfolder rather than the install root
    (Fallout: DATA/SAVEGAME/SLOT01, Quake II: BASEQ2/SAVE/... and any
    mission-pack directory following the same layout, e.g. XATRIX/SAVE).

    Once a matching directory is found, we do not recurse further into it:
    the whole folder (including future save slots) is treated as a single
    backup unit.
    """
    if not install_dir.is_dir():
        return []

    found: list[SaveLocation] = []

    def _walk(current: Path, depth: int) -> None:
        if depth > max_depth:
            return
        try:
            children = list(current.iterdir())
        except (OSError, PermissionError) as exc:
            logger.debug("Cannot list %s: %s", current, exc)
            return

        for entry in children:
            try:
                if not entry.is_dir():
                    continue
            except (OSError, PermissionError):
                continue

            if entry.name.lower() in SAVE_DIR_NAMES:
                if _dir_has_content(entry):
                    # label includes the parent folder for context, e.g.
                    # "BASEQ2/SAVE" rather than just "SAVE", which matters
                    # when a game has several mod/expansion save dirs.
                    try:
                        rel_label = str(entry.relative_to(install_dir))
                    except ValueError:
                        rel_label = entry.name
                    found.append(SaveLocation(path=entry, kind="install_dir", label=rel_label))
                continue  # do not descend into a recognized save dir

            _walk(entry, depth + 1)

    _walk(install_dir, depth=0)
    return found


# ---------------------------------------------------------------------------
# Strategy 3: prefix-standard save locations
# ---------------------------------------------------------------------------

def find_prefix_user_saves(
    prefix_path: Path,
    game_name: str | None = None,
) -> list[SaveLocation]:
    """Modern-convention save locations under drive_c/users/<user>/ inside
    a given Wine/Proton prefix. Works for any prefix path, not just Steam's
    compatdata layout, so custom prefixes (e.g. `.wine-alerte`, a Bottles
    or Lutris prefix, or an arbitrary `~/Documents/Proton/env/<name>/pfx`)
    are all covered the same way.

    If game_name is given, subfolders are matched loosely against it
    (case-insensitive substring) to avoid pulling in unrelated games that
    happen to share the same "Saved Games" parent across many titles.
    Otherwise, all non-empty subpaths are returned as candidates.
    """
    users_dir = prefix_path / "drive_c" / "users"
    if not users_dir.is_dir():
        return []

    found: list[SaveLocation] = []
    try:
        user_dirs = [d for d in users_dir.iterdir() if d.is_dir()]
    except (OSError, PermissionError) as exc:
        logger.debug("Cannot list %s: %s", users_dir, exc)
        return []

    for user_dir in user_dirs:
        for subpath in PREFIX_USER_SAVE_SUBPATHS:
            candidate = user_dir / subpath
            if not candidate.is_dir():
                continue

            if game_name:
                needle = game_name.lower()
                try:
                    matches = [
                        c for c in candidate.iterdir()
                        if c.is_dir() and needle in c.name.lower()
                    ]
                except (OSError, PermissionError):
                    matches = []
                for match in matches:
                    if _dir_has_content(match):
                        found.append(SaveLocation(
                            path=match,
                            kind="prefix_dir",
                            label=f"{subpath}/{match.name}",
                        ))
            else:
                if _dir_has_content(candidate):
                    found.append(SaveLocation(path=candidate, kind="prefix_dir", label=subpath))

    return found


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def detect_save_paths(game) -> list[SaveLocation]:
    """Main entry point. `game` is expected to expose:
      - game.exe_path   (str | Path)  -- path to the game's .exe
      - game.prefix_path (str | Path | None)
      - game.name        (str | None)

    Combines all three detection strategies. Deduplicates by resolved
    path in case a location would otherwise be reported twice.
    """
    results: list[SaveLocation] = []

    install_dir = Path(game.exe_path).parent
    results.extend(find_install_local_save_files(install_dir))
    results.extend(find_install_nested_save_dirs(install_dir))

    prefix_path = getattr(game, "prefix_path", None)
    if prefix_path:
        results.extend(find_prefix_user_saves(Path(prefix_path), getattr(game, "name", None)))

    seen: set[Path] = set()
    deduped: list[SaveLocation] = []
    for loc in results:
        resolved = loc.path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        deduped.append(loc)

    return deduped


# ---------------------------------------------------------------------------
# Fingerprinting (change detection)
# ---------------------------------------------------------------------------

def compute_save_fingerprint(locations: list[SaveLocation]) -> str:
    """Lightweight fingerprint over (relative path, mtime_ns, size) for
    every file under the given save locations. Directory-level stat()
    is deliberately never used as a shortcut: a save directory can report
    a misleadingly small/zero size at the directory-entry level while
    still containing real file content (observed with some Quake II
    save slots on ext4), so every location is walked recursively.

    mtime+size is used rather than a full content hash to keep this cheap
    enough to run synchronously right after a game process exits, even
    for save data in the tens/hundreds of MB range.
    """
    entries: list[str] = []

    for loc in locations:
        base = loc.path
        if base.is_file():
            _append_file_entry(entries, base, base.parent)
        elif base.is_dir():
            for root, _dirs, files in os.walk(base):
                root_path = Path(root)
                for fname in files:
                    _append_file_entry(entries, root_path / fname, base)

    entries.sort()
    raw = "|".join(entries)
    return hashlib.sha256(raw.encode("utf-8", errors="replace")).hexdigest()


def _append_file_entry(entries: list[str], fpath: Path, base: Path) -> None:
    try:
        st = fpath.stat()
        rel = fpath.relative_to(base)
    except (OSError, PermissionError, ValueError):
        # File vanished, permission denied, or not actually relative to
        # base -- skip silently rather than failing the whole fingerprint.
        return
    entries.append(f"{rel}:{st.st_mtime_ns}:{st.st_size}")


def has_save_changed(previous_fingerprint: str | None, current_fingerprint: str) -> bool:
    """True if this is a new fingerprint (game closed, save data present)
    and it differs from the last one we stored for this game. A None
    previous fingerprint (never backed up / never seen before) counts
    as changed."""
    if previous_fingerprint is None:
        return bool(current_fingerprint)
    return previous_fingerprint != current_fingerprint
