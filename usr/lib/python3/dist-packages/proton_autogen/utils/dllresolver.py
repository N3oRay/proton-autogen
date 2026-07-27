"""
proton_autogen.dllresolver

Installation des DLL Windows (ddraw, d3d8, d3d9, dsound)
pour les anciens jeux exécutés avec Proton.

Ordre de priorité :

1. DLL provenant du Proton utilisé pour lancer le jeu.
2. Wrapper embarqué dans proton-autogen.

Aucun scan récursif ni vérification SHA256 n'est effectué.
"""

from __future__ import annotations

import shutil
import struct
from pathlib import Path

from proton_autogen.utils.logger import StructuredLogger

logger = StructuredLogger("proton-autogen.dll_manager")

_MODULE_DIR = Path(__file__).resolve().parent


# ============================================================
# DLL supportées
# ============================================================

KNOWN_DLLS = {
    "ddraw.dll": "wrappers/ddraw.dll",
    "d3d8.dll": "wrappers/d3d8.dll",
    "d3d9.dll": "wrappers/d3d9.dll",
    "dsound.dll": "wrappers/dsound.dll",
}


# ============================================================
# Répertoires Wine d'un Proton
# ============================================================

PROTON_DLL_DIRS = (
    "files/lib/wine/i386-windows",
    "files/lib/wine/x86_64-windows",
    "files/lib/wine/d7vk/i386-windows",
    "files/lib/wine/d7vk/x86_64-windows",
    "files/lib/wine/dxvk-sarek/i386-windows",
    "files/lib/wine/dxvk-sarek/x86_64-windows",
)


# ============================================================
# Vérification PE32
# ============================================================

def is_pe32(path: Path) -> bool:
    """Retourne True si le fichier est une DLL PE32 Intel x86."""

    try:
        with path.open("rb") as f:

            if f.read(2) != b"MZ":
                return False

            f.seek(0x3C)
            pe_offset = struct.unpack("<I", f.read(4))[0]

            f.seek(pe_offset)

            if f.read(4) != b"PE\x00\x00":
                return False

            machine = struct.unpack("<H", f.read(2))[0]

            return machine == 0x14C

    except OSError:
        return False


# ============================================================
# Wrapper embarqué
# ============================================================

def resolve_wrapper(dll: str) -> Path | None:

    wrapper = _MODULE_DIR / KNOWN_DLLS[dll]

    if wrapper.is_file():
        return wrapper

    logger.error("Wrapper missing: %s", wrapper)

    return None


# ============================================================
# DLL Proton
# ============================================================

def find_proton_dll(
    proton_path: str | Path,
    dll: str,
) -> Path | None:

    proton_path = Path(proton_path)

    for directory in PROTON_DLL_DIRS:
        candidate = proton_path / directory / dll

        if candidate.is_file() and is_pe32(candidate):
            return candidate

    return None


# ============================================================
# Sélection source
# ============================================================

def find_best_dll(
    dll: str,
    proton_path: Path | None = None,
) -> Path | None:

    if proton_path:

        source = find_proton_dll(proton_path, dll)

        if source:
            return source

    source = resolve_wrapper(dll)

    if source:

        logger.debug("Using bundled wrapper: %s", source)

    return source


# ============================================================
# Copie
# ============================================================

def safe_copy(
    source: Path,
    target: Path,
) -> bool:

    try:

        target.parent.mkdir(parents=True, exist_ok=True)

        if target.exists():
            target.unlink()

        shutil.copyfile(source, target)

        logger.info("%s -> %s", source, target)

        return True

    except OSError as e:

        logger.error("Copy failed: %s", e)

        return False


# ============================================================
# Installation
# ============================================================

def install_dll(
    game_dir: Path,
    dll: str,
    proton_path: Path | None = None,
    force: bool = False,
) -> bool:

    target = game_dir / dll

    if target.exists() and not force:

        logger.debug("%s already present", dll)

        return True

    source = find_best_dll(
        dll,
        proton_path,
    )

    if source is None:

        logger.error("No source available for %s", dll)

        return False

    logger.info("Installing %s", dll)

    return safe_copy(
        source,
        target,
    )


# ============================================================
# API publique
# ============================================================

def resolve_game_dlls(
    game_dir: str | Path,
    proton_path: str | Path | None = None,
    required_dlls: list[str] | None = None,
    force: bool = False,
) -> list[str]:

    game_dir = Path(game_dir)

    if proton_path is not None:
        proton_path = Path(proton_path)

    game_dir = Path(game_dir)

    if not game_dir.is_dir():

        raise RuntimeError(f"Missing game directory: {game_dir}")

    installed = []

    dlls = required_dlls or list(KNOWN_DLLS.keys())

    for dll in dlls:

        if dll not in KNOWN_DLLS:

            logger.warning("Unknown DLL: %s", dll)

            continue

        if install_dll(
            game_dir=game_dir,
            dll=dll,
            proton_path=proton_path,
            force=force,
        ):
            installed.append(dll)

    return installed
