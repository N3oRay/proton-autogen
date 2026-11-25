"""Steam compatibility tool for Proton-Autogen (``proton-autogen install-steam``).

Installs a thin wrapper into ``<Steam>/compatibilitytools.d/Proton-Autogen/`` so
that Steam can launch a game through ``proton-autogen run``. The wrapper
(``steam_assets/``) only translates Steam's ``proton <verb> <exe> [args]``
call into ``proton-autogen run --steam -- <exe> [args]``.

This module only needs the standard library, so it can also be imported by the
Proton detection code (``is_wrapper_dir``) without any cost.

Exit codes (in addition to those of ``cli.py``): ``EXIT_ABORTED`` when the
user refuses (or cannot be asked), ``EXIT_INTEGRITY`` when the installation
fails its post-install verification.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat
import sys
import tempfile
import time
from pathlib import Path
from typing import Callable, Optional

TOOL_NAME = "Proton-Autogen"

ASSET_FILES = ("compatibilitytool.vdf", "toolmanifest.vdf", "proton")
MODULE_FILES = ("autogen_wrapper.py",)
LAUNCHER_FILE = "launcher.path"
MANIFEST_FILE = "INSTALL_MANIFEST.json"
EXECUTABLE_FILES = ("proton",)
MANAGED = ASSET_FILES + MODULE_FILES + (LAUNCHER_FILE,)

# Marker used by the Proton detection code to ignore this tool.
WRAPPER_MARKER = MODULE_FILES[0]

EXIT_ERROR = 1
EXIT_ABORTED = 4
EXIT_INTEGRITY = 5


class SteamInstallError(Exception):
    """Expected failure: clean message, dedicated exit code."""

    def __init__(self, message: str, code: int = EXIT_ERROR):
        super().__init__(message)
        self.code = code


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def is_wrapper_dir(path) -> bool:
    """True if ``path`` is the Proton-Autogen Steam wrapper, not a real Proton.

    Proton-Autogen scans ``compatibilitytools.d`` for folders named "*proton*";
    selecting its own wrapper would make it call itself forever.
    """
    return os.path.isfile(os.path.join(os.fspath(path), WRAPPER_MARKER))


def default_steam_root() -> Path:
    return Path.home() / ".steam" / "root"


def default_tools_dir() -> Path:
    return default_steam_root() / "compatibilitytools.d"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha_file(path: Path) -> str:
    return _sha(path.read_bytes())


def find_assets_dir(explicit=None) -> Path:
    needed = ASSET_FILES + MODULE_FILES
    candidates = (
        explicit,
        os.environ.get("PROTON_AUTOGEN_STEAM_ASSETS"),
        Path(__file__).resolve().parent / "steam_assets",
    )
    for cand in candidates:
        if cand and all((Path(cand) / name).is_file() for name in needed):
            return Path(cand)
    raise SteamInstallError(
        "Steam wrapper files not found (compatibilitytool.vdf, toolmanifest.vdf, "
        "proton, autogen_wrapper.py): incomplete installation?"
    )


def _resolve_launcher(explicit: Optional[str]) -> Path:
    candidates = [explicit, os.environ.get("PROTON_AUTOGEN_BIN"),
                  shutil.which("proton-autogen")]
    if os.path.basename(sys.argv[0]) == "proton-autogen":
        candidates.append(sys.argv[0])
    for cand in candidates:
        if cand:
            path = Path(cand).resolve()
            if path.is_file() and os.access(path, os.X_OK):
                return path
    raise SteamInstallError(
        "proton-autogen launcher not found or not executable (use --launcher)."
    )


def _confirm(message: str, assume_yes: bool) -> None:
    if assume_yes:
        return
    if not sys.stdin.isatty():
        raise SteamInstallError(
            message + "\nCannot ask for confirmation outside a terminal: "
            "re-run with --yes.",
            EXIT_ABORTED,
        )
    answer = input(f"{message}\nContinue? [y/N] ").strip().lower()
    if answer not in ("y", "yes", "o", "oui"):
        raise SteamInstallError("Installation cancelled.", EXIT_ABORTED)


def _atomic_write(path: Path, data: bytes, mode: int) -> None:
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".tmp-")
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
        os.chmod(tmp, mode)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _load_manifest(dest: Path) -> Optional[dict]:
    try:
        return json.loads((dest / MANIFEST_FILE).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


# --------------------------------------------------------------------------- #
# Verification (permissions + integrity)
# --------------------------------------------------------------------------- #

def verify(dest: Path) -> list:
    """Return the list of problems found (empty list = healthy installation)."""
    if not dest.is_dir():
        return [f"directory missing: {dest}"]

    problems = []
    st = dest.stat()
    if st.st_uid != os.getuid():
        problems.append("directory is not owned by the current user")
    if st.st_mode & stat.S_IWOTH:
        problems.append("directory is world-writable")

    manifest = _load_manifest(dest)
    if manifest is None:
        problems.append(f"{MANIFEST_FILE} missing or unreadable")
    recorded = (manifest or {}).get("files", {})

    for name in MANAGED:
        path = dest / name
        if not path.is_file():
            problems.append(f"missing file: {name}")
            continue
        if path.stat().st_mode & stat.S_IWOTH:
            problems.append(f"world-writable file: {name}")
        if manifest is not None and recorded.get(name) != _sha_file(path):
            problems.append(f"checksum differs from manifest: {name}")

    for name in EXECUTABLE_FILES:
        path = dest / name
        if path.is_file() and not os.access(path, os.X_OK):
            problems.append(f"not executable: {name}")

    vdf = dest / "compatibilitytool.vdf"
    if vdf.is_file():
        text = vdf.read_text(encoding="utf-8", errors="replace")
        if "compat_tools" not in text or f'"{TOOL_NAME}"' not in text:
            problems.append("invalid compatibilitytool.vdf")
    tm = dest / "toolmanifest.vdf"
    if tm.is_file() and "commandline" not in tm.read_text(
            encoding="utf-8", errors="replace"):
        problems.append("invalid toolmanifest.vdf (no commandline)")

    lp = dest / LAUNCHER_FILE
    if lp.is_file():
        target = lp.read_text(encoding="utf-8").strip()
        if not (target and os.path.isfile(target) and os.access(target, os.X_OK)):
            problems.append(f"referenced launcher not found: {target or '(empty)'}")

    return problems


def _apply_modes(dest: Path) -> None:
    dest.chmod(0o755)
    for name in MANAGED + (MANIFEST_FILE,):
        path = dest / name
        if path.is_file():
            path.chmod(0o755 if name in EXECUTABLE_FILES else 0o644)


# --------------------------------------------------------------------------- #
# Installation
# --------------------------------------------------------------------------- #

def _prepare_tools_dir(tools_dir: Path, custom: bool) -> None:
    if tools_dir.exists():
        if not tools_dir.is_dir():
            raise SteamInstallError(f"{tools_dir} exists but is not a directory.")
        return
    if not custom and not tools_dir.parent.exists():
        raise SteamInstallError(
            f"Steam not found ({tools_dir.parent} is missing). "
            "Start Steam once, or use --dest."
        )
    tools_dir.mkdir(parents=custom, mode=0o755)


def install(dest_root=None, assume_yes=False, assets_dir=None, launcher=None,
            out: Callable[[str], None] = print) -> Path:
    """Install (or update) the wrapper. Never overwrites a differing existing
    installation without confirmation; replaced files are backed up."""
    tools_dir = Path(dest_root).expanduser() if dest_root else default_tools_dir()
    assets = find_assets_dir(assets_dir)

    expected = {n: (assets / n).read_bytes() for n in ASSET_FILES + MODULE_FILES}
    expected[LAUNCHER_FILE] = (str(_resolve_launcher(launcher)) + "\n").encode()

    _prepare_tools_dir(tools_dir, custom=dest_root is not None)
    dest = tools_dir / TOOL_NAME
    if dest.exists() and not dest.is_dir():
        raise SteamInstallError(f"{dest} exists but is not a directory.")

    differing = []
    if dest.is_dir():
        for name, data in expected.items():
            path = dest / name
            if path.is_file() and _sha_file(path) != _sha(data):
                differing.append(name)

        if not differing and all((dest / n).is_file() for n in expected):
            _apply_modes(dest)
            if not verify(dest):
                out(f"Already up to date: {dest}")
                return dest

        if differing:
            _confirm(
                f"An existing installation in {dest} differs.\n"
                f"Files that would be replaced: {', '.join(differing)}\n"
                "(a .bak-<date> backup is made for each)",
                assume_yes,
            )

    dest.mkdir(mode=0o755, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    for name in differing:
        shutil.copy2(dest / name, dest / f"{name}.bak-{stamp}")

    for name, data in expected.items():
        _atomic_write(dest / name, data,
                      0o755 if name in EXECUTABLE_FILES else 0o644)

    manifest = {
        "tool": TOOL_NAME,
        "installed_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "files": {n: _sha(d) for n, d in expected.items()},
    }
    _atomic_write(dest / MANIFEST_FILE,
                  json.dumps(manifest, indent=2, sort_keys=True).encode(), 0o644)
    _apply_modes(dest)

    problems = verify(dest)
    if problems:
        raise SteamInstallError(
            "Verification failed:\n  - " + "\n  - ".join(problems), EXIT_INTEGRITY)

    out(f"Installed: {dest}")
    out(f"Restart Steam, then: game Properties > Compatibility > \"{TOOL_NAME}\".")
    return dest


def run_install_steam(dest=None, launcher=None, assume_yes=False, check=False,
                      out: Callable[[str], None] = print) -> int:
    """Entry point used by the ``install-steam`` CLI command.

    Raises ``SteamInstallError`` on failure; returns 0 on success."""
    if check:
        tools_dir = Path(dest).expanduser() if dest else default_tools_dir()
        problems = verify(tools_dir / TOOL_NAME)
        if problems:
            raise SteamInstallError(
                "Steam installation is not healthy:\n  - " + "\n  - ".join(problems),
                EXIT_INTEGRITY,
            )
        out("Steam installation is healthy.")
        return 0
    install(dest_root=dest, assume_yes=assume_yes, launcher=launcher, out=out)
    return 0
