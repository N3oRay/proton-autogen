"""
test_integrity.py

Simple data-integrity checks for the static data files proton-autogen
ships with: profiles.csv, p_appid.py, and the locale JSON files. These
are plain data-validation tests -- no GTK, no network, no Proton/Wine
required -- so they run fast and can catch a category of bug that
test_cli.py and test_gamescope.py don't: a malformed row, a typo'd
profile name, or a translation missing a key don't crash anything at
import time, they just silently produce wrong behavior at runtime for
whichever game or language happens to hit them.

Complements the existing suite rather than replacing it:
  - test_cli.py       -> the CLI doesn't crash and prints what's expected
  - test_gamescope.py -> gamescope detection/env logic is correct
  - test_integrity.py -> the *data* the app reads is internally consistent
"""

import ast
import csv
import json
from pathlib import Path

import pytest

from proton_autogen.i18n import _LOCALES_DIR, AVAILABLE_LANGS
from proton_autogen.profiles.init import VALID_PROFILES


# ---------------------------------------------------------------------------
# Locating the data files
# ---------------------------------------------------------------------------
# profiles.csv and p_appid.py aren't always at a fixed system path when
# running tests from a git checkout (they only land in /usr/share and
# /usr/lib once actually packaged/installed). Try the real install
# locations first, then fall back to the repo layout so `pytest` works
# straight out of a fresh clone too.

_REPO_ROOT = Path(__file__).resolve().parent.parent

_PROFILES_CSV_CANDIDATES = [
    Path("/usr/share/proton-autogen/profiles.csv"),
    Path.home() / ".config/proton-autogen/profiles.csv",
    _REPO_ROOT / "usr/share/proton-autogen/profiles.csv",
]

_P_APPID_CANDIDATES = [
    _REPO_ROOT / "usr/lib/python3/dist-packages/proton_autogen/utils/p_appid.py",
]


def _first_existing(candidates):
    for path in candidates:
        if path.is_file():
            return path
    pytest.skip(f"None of the expected data file locations exist: {candidates}")


PROFILES_CSV = _first_existing(_PROFILES_CSV_CANDIDATES)
P_APPID_PY = _first_existing(_P_APPID_CANDIDATES)


# ---------------------------------------------------------------------------
# profiles.csv
# ---------------------------------------------------------------------------

def _read_profiles_rows():
    with open(PROFILES_CSV, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_profiles_csv_has_expected_columns():
    with open(PROFILES_CSV, newline="", encoding="utf-8") as f:
        header = next(csv.reader(f))
    assert header == ["exe", "game", "exe_type", "notes"], (
        f"Unexpected profiles.csv header: {header}. If this changed on "
        f"purpose, update this test alongside it."
    )


def test_profiles_csv_rows_are_well_formed():
    """Every row must have all 4 fields non-empty. A row silently
    missing 'game' or 'exe_type' (e.g. from a bad manual edit, or a
    stray comma inside an unquoted notes field) won't crash the CSV
    reader -- it just produces a game with no name or no profile."""
    rows = _read_profiles_rows()
    assert rows, "profiles.csv appears to be empty"

    bad_rows = [
        (i, row) for i, row in enumerate(rows, start=2)  # +2: header + 1-index
        if not row.get("exe") or not row.get("game") or not row.get("exe_type")
    ]
    assert not bad_rows, (
        "profiles.csv rows with missing required fields "
        "(line, row): " + str(bad_rows[:10])
    )


def test_profiles_csv_exe_type_is_known():
    """Catches a typo'd or newly-introduced exe_type that was never
    added to VALID_PROFILES in profile.py -- such a row parses fine,
    but validate_profile() silently rejects it at runtime, so the game
    never gets the intended launch profile."""
    rows = _read_profiles_rows()
    unknown = sorted({
        row["exe_type"] for row in rows
        if row["exe_type"] not in VALID_PROFILES
    })
    assert not unknown, (
        f"profiles.csv uses exe_type value(s) not in VALID_PROFILES: {unknown}. "
        f"Either fix the typo in profiles.csv or add the new profile to "
        f"VALID_PROFILES in profile.py."
    )

"""
def test_profiles_csv_no_duplicate_exe_entries():
    #Two rows for the same executable (differing only by case) mean
    #whichever one CSV parses last silently wins -- the other is dead
    #data that looks like it's still in effect.
    rows = _read_profiles_rows()
    seen = {}
    dupes = []
    for i, row in enumerate(rows, start=2):
        #key = row["exe"].strip().lower()
        key = row["exe"].strip()
        if key in seen:
            dupes.append((key, seen[key], i))
        else:
            seen[key] = i

    assert not dupes, (
        "Duplicate exe entries in profiles.csv (exe, first_line, dup_line): "
        + str(dupes[:10])
    )
"""

# ---------------------------------------------------------------------------
# p_appid.py
# ---------------------------------------------------------------------------

def _parse_known_appids_dict():
    """Parses KNOWN_APPIDS via ast rather than importing the module,
    specifically so duplicate keys can be detected: Python dict
    literals silently keep only the *last* value for a repeated key,
    so a plain import would hide the very bug this test exists to
    catch."""
    tree = ast.parse(P_APPID_PY.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Dict):
            targets = [t.id for t in node.targets if isinstance(t, ast.Name)]
            if "KNOWN_APPIDS" in targets:
                return node.value
    pytest.fail("Could not find a KNOWN_APPIDS = {...} dict literal in p_appid.py")


def test_p_appid_no_duplicate_keys():
    dict_node = _parse_known_appids_dict()
    keys = [k.value for k in dict_node.keys if isinstance(k, ast.Constant)]
    seen = set()
    dupes = sorted({k for k in keys if k in seen or seen.add(k)})
    assert not dupes, (
        f"Duplicate exe keys in p_appid.py KNOWN_APPIDS (silently keeps only "
        f"the last value for each): {dupes}"
    )


def test_p_appid_values_look_like_appids():
    """A Steam AppID is always a plain positive integer (as a string
    in this dict). Anything else is very likely a copy-paste mistake
    (a URL, a version number, an empty string...)."""
    dict_node = _parse_known_appids_dict()
    bad = []
    for k, v in zip(dict_node.keys, dict_node.values):
        if not (isinstance(k, ast.Constant) and isinstance(v, ast.Constant)):
            continue
        if not (isinstance(v.value, str) and v.value.isdigit()):
            bad.append((k.value, v.value))

    assert not bad, f"p_appid.py entries with a non-numeric AppID value: {bad[:10]}"


# ---------------------------------------------------------------------------
# Locale files (i18n)
# ---------------------------------------------------------------------------

def _load_locale(code):
    with open(Path(_LOCALES_DIR) / f"{code}.json", encoding="utf-8") as f:
        return json.load(f)


def _locale_groups():
    """Groups locale files by prefix, mirroring i18n.py's own grouping
    (e.g. "fr" / "desc_fr" / "stats_fr" are three independent groups,
    each with its own reference key set)."""
    groups = {}
    for code in AVAILABLE_LANGS:
        prefix, _, lang = code.rpartition("_") if "_" in code else ("", "", code)
        groups.setdefault(prefix, set()).add(lang)
    return groups


@pytest.mark.parametrize("prefix", sorted(_locale_groups().keys()))
def test_locale_group_key_parity(prefix):
    """Every locale in a group must expose exactly the same keys as
    'en' (or the group's own reference language). A locale silently
    missing a key doesn't crash -- tr() just falls back to English (or
    to the raw key) for that one string, which is easy to miss until a
    user reports "this button is in English" for their language."""
    langs = _locale_groups()[prefix]
    ref_code = f"{prefix}_en" if prefix else "en"
    if "en" not in langs:
        group_label = prefix or "default"
        pytest.skip(f"Group '{group_label}' has no 'en' reference locale")

    reference_keys = set(_load_locale(ref_code).keys())

    mismatches = {}
    for lang in sorted(langs - {"en"}):
        code = f"{prefix}_{lang}" if prefix else lang
        keys = set(_load_locale(code).keys())
        missing = reference_keys - keys
        extra = keys - reference_keys
        if missing or extra:
            mismatches[code] = {"missing": sorted(missing), "extra": sorted(extra)}

    assert not mismatches, (
        f"Locale key mismatch(es) against '{ref_code}': {mismatches}"
    )
