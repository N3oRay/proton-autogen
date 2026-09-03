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

Strategy 3 also falls back to Proton's well-known compat-user directory
name ("steamuser") if drive_c/users/ can't be listed at all -- a real,
if unusual, POSIX permission combination (traversable but not listable)
can otherwise make an entire prefix silently yield no results.

Fingerprinting is done by walking the full save subtree and hashing
(relative path, mtime, size) per file rather than trusting parent
directory sizes -- `ls -l` can report a directory as 0 bytes even when
it contains real files (observed on ext4 with certain Quake II save
slots), so directory-level stat() alone is not a reliable change signal.
"""

from __future__ import annotations

import hashlib
from proton_autogen.utils.logger import StructuredLogger
import os
import re
from dataclasses import dataclass, field
from pathlib import Path

#-------------------------- Init Log -------------------
logger = StructuredLogger("proton-autogen.save_detection")


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

# Subset of the above where game folders are typically named after the
# game itself rather than under a curated "Saved Games"/"My Games"
# convention -- and where Windows/Wine also dumps a lot of unrelated
# per-user clutter (browser caches, GPU shader caches, telemetry...).
# Used to scope the blocklist-based fallback below.
APPDATA_SUBPATHS: frozenset[str] = frozenset({"AppData/Local", "AppData/Roaming"})

# Known non-game folders found under AppData/Local and AppData/Roaming
# inside a Wine prefix. Never proposed as save data, even by the
# fallback tier below (see find_prefix_user_saves): these are standard
# Windows user-profile / Wine internals, not any specific game's data.
APPDATA_SYSTEM_FOLDER_BLOCKLIST: frozenset[str] = frozenset({
    "microsoft",
    "microsoft_corporation",
    "temp",
    "tmp",
    "google",
    "mozilla",
    "packages",
    "connecteddevicesplatform",
    "crashdumps",
    "d3dscache",
    "nvidia",
    "nvidia corporation",
    "amd",
    "comms",
    "elevateddiagnostics",
    "programs",
    "publishers",
})

# How many directory levels below the install dir / prefix save subpath we
# are willing to recurse into when looking for a named save directory.
# Keeps the scan fast on large, asset-heavy install directories.
MAX_SCAN_DEPTH = 3

# Proton always creates its Windows compat-user profile under this exact
# name inside drive_c/users/, regardless of the real Linux username --
# forced via STEAM_COMPAT_* environment variables at prefix creation
# time. Used as an explicit fallback in find_prefix_user_saves(): if
# listing drive_c/users/ fails or yields nothing (unusual permissions on
# that specific prefix -- e.g. traversable but not listable, a real
# POSIX permission combination -- or any other enumeration quirk), we
# still know exactly where Proton would have put the user's profile and
# can check it directly rather than silently detecting nothing.
DEFAULT_PROTON_USER = "steamuser"


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

# If game_name is given, subfolders are matched against it using a
# two-step name heuristic:
#
#   1. conservative matching using words of at least 4 characters;
#   2. permissive fallback using all alphanumeric tokens, including
#      abbreviations and sequel numbers.
#
# The permissive step intentionally favors false positives over false
# negatives.

_STOPWORDS = frozenset({
    "the",
    "of",
    "and",
    "for",
    "a",
    "an",
    "edition",
    "game",
    "games",
})


def _significant_words_step1(name: str) -> set[str]:
    """Return significant words of at least 4 characters.

    Step 1 is the conservative matcher. It avoids short/common tokens
    such as numbers and abbreviations to reduce false positives.
    """
    words = re.findall(r"[a-z0-9]+", name.lower())
    result = {
        w
        for w in words
        if len(w) >= 4 and w not in _STOPWORDS
    }

    logger.debug(
        "Save detection Step 1: %r -> %s",
        name,
        sorted(result),
    )

    return result


def _significant_words_step2(name: str) -> set[str]:
    """Return all normalized alphanumeric words.

    Step 2 is the permissive fallback matcher. Short tokens such as
    '2', 'ii', 'v', 'nfs', etc. are deliberately retained.
    """
    words = re.findall(r"[a-z0-9]+", name.lower())
    result = {
        w
        for w in words
        if w not in _STOPWORDS
    }

    logger.debug(
        "Save detection Step 2: %r -> %s",
        name,
        sorted(result),
    )

    return result


def _folder_matches_game(folder_name: str, game_name: str) -> bool:
    """Return True if a folder plausibly belongs to the game.

    Matching is performed in two steps:
      1. Conservative match using words >= 4 characters.
      2. Permissive fallback using all alphanumeric words.
    """

    logger.debug(
        "Save detection: comparing folder=%r with game=%r",
        folder_name,
        game_name,
    )

    # ---------------------------------------------------------------
    # Step 1: conservative matching
    # ---------------------------------------------------------------
    folder_words = _significant_words_step1(folder_name)
    game_words = _significant_words_step1(game_name)

    common_words = folder_words & game_words

    if common_words:
        logger.debug(
            "Save detection: STEP 1 MATCH: folder=%r game=%r common=%s",
            folder_name,
            game_name,
            sorted(common_words),
        )
        return True

    logger.debug(
        "Save detection: STEP 1 NO MATCH: folder=%r game=%r",
        folder_name,
        game_name,
    )

    # ---------------------------------------------------------------
    # Step 2: permissive matching
    # ---------------------------------------------------------------
    folder_words = _significant_words_step2(folder_name)
    game_words = _significant_words_step2(game_name)

    common_words = folder_words & game_words

    if common_words:
        logger.debug(
            "Save detection: STEP 2 MATCH: folder=%r game=%r common=%s",
            folder_name,
            game_name,
            sorted(common_words),
        )
        return True

    logger.debug(
        "Save detection: STEP 2 NO MATCH: folder=%r game=%r",
        folder_name,
        game_name,
    )

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

    If game_name is given, subfolders are matched against it by shared
    significant words (see _folder_matches_game) rather than a strict
    substring test, so abbreviated on-disk folder names (e.g. "NFS
    Underground 2" for "Need for Speed Underground 2") are still found.
    If no folder matches under AppData/Local or AppData/Roaming
    specifically, every remaining subfolder there is proposed instead,
    except a small blocklist of known Windows/Wine system folders (see
    APPDATA_SYSTEM_FOLDER_BLOCKLIST) -- publishers' folder-naming
    conventions vary too much to guarantee a name-based match always
    succeeds, and a missed save is worse than an extra folder offered
    for backup. Without a game_name at all, every non-empty subpath is
    returned as a whole.
    """
    users_dir = prefix_path / "drive_c" / "users"

    if not users_dir.is_dir():
        logger.debug(
            "Save detection: users directory not found: %s",
            users_dir,
        )
        return []

    found: list[SaveLocation] = []

    try:
        user_dirs = [d for d in users_dir.iterdir() if d.is_dir()]
    except (OSError, PermissionError) as exc:
        logger.debug(
            "Save detection: cannot list users directory %s: %s",
            users_dir,
            exc,
        )
        user_dirs = []

    # Fallback: whether listing failed outright above, or simply didn't
    # surface Proton's compat user for some reason, its name is always
    # "steamuser" -- check it directly rather than silently detecting
    # nothing for the whole prefix. Cheap (a single is_dir() check) and
    # a no-op if it was already picked up above.
    default_user_dir = users_dir / DEFAULT_PROTON_USER
    if default_user_dir.is_dir() and default_user_dir not in user_dirs:
        logger.debug(
            "Save detection: adding default Proton user directory: %s",
            default_user_dir,
        )
        user_dirs.append(default_user_dir)

    if not user_dirs:
        logger.debug(
            "Save detection: no user directories found under %s "
            "(including default '%s' fallback)",
            users_dir,
            DEFAULT_PROTON_USER,
        )
        return []

    logger.debug(
        "Save detection: scanning prefix %s for game %r",
        prefix_path,
        game_name,
    )

    for user_dir in user_dirs:
        for subpath in PREFIX_USER_SAVE_SUBPATHS:
            candidate = user_dir / subpath

            if not candidate.is_dir():
                continue

            if game_name:
                try:
                    subfolders = [
                        c for c in candidate.iterdir()
                        if c.is_dir()
                    ]
                except (OSError, PermissionError):
                    subfolders = []

                matched_names: set[str] = set()

                for sub in subfolders:
                    if _folder_matches_game(sub.name, game_name):
                        if _dir_has_content(sub):
                            logger.info(
                                "Save detection: found save directory: %s",
                                sub,
                            )

                            found.append(SaveLocation(
                                path=sub,
                                kind="prefix_dir",
                                label=f"{subpath}/{sub.name}",
                            ))

                        matched_names.add(sub.name)

                # Fallback tier for AppData/Local and AppData/Roaming.
                if subpath in APPDATA_SUBPATHS and not matched_names:
                    logger.debug(
                        "Save detection: no game-name match in %s; "
                        "using AppData fallback",
                        candidate,
                    )

                    for sub in subfolders:
                        if sub.name.lower() in APPDATA_SYSTEM_FOLDER_BLOCKLIST:
                            continue

                        if _dir_has_content(sub):
                            logger.info(
                                "Save detection: fallback save directory: %s",
                                sub,
                            )

                            found.append(SaveLocation(
                                path=sub,
                                kind="prefix_dir",
                                label=f"{subpath}/{sub.name}",
                            ))

            else:
                if _dir_has_content(candidate):
                    logger.info(
                        "Save detection: found save directory: %s",
                        candidate,
                    )

                    found.append(SaveLocation(
                        path=candidate,
                        kind="prefix_dir",
                        label=subpath,
                    ))

    logger.debug(
        "Save detection: prefix scan found %d location(s)",
        len(found),
    )

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
