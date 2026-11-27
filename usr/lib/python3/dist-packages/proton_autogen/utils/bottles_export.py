#!/usr/bin/env python3

# bottles_export.py
"""
« Exporter vers Bottle » : ajoute un jeu de la bibliothèque Proton-Autogen aux
programmes d'une bouteille Bottles existante.

Bottles garde les programmes ajoutés à la main dans la section
`External_Programs` du fichier `bottle.yml` de la bouteille (une entrée par
programme, clé = uuid). C'est exactement ce que fait « Ajouter un raccourci »
dans Bottles, et ce que fait `bottles-cli add` : l'entrée apparaît ensuite dans
la liste « Programmes » de la bouteille et se lance avec le runner de celle-ci.

Logique pure (sans GTK) :
  - bottles_roots()                  : dossiers de bouteilles (natif + Flatpak)
  - list_bottles()                   : bouteilles utilisables
  - build_program(game)              : entrée External_Programs d'un jeu
  - export_game_to_bottle(game, b)   : écrit l'entrée dans bottle.yml
  - bottles_running()                : Bottles est-il ouvert ? (meilleur effort)

Sécurité des données :
  - rien n'est écrit si le programme est déjà présent (même chemin) ;
  - bottle.yml est sauvegardé (bottle.yml.proton-autogen.bak) avant écriture ;
  - écriture atomique (fichier temporaire + os.replace), droits conservés ;
  - le résultat est relu et vérifié, la sauvegarde est restaurée en cas d'échec.

Limites : seules les bouteilles rangées dans les dossiers standard sont listées
(pas celles à chemin personnalisé) ; les bouteilles de type « Steam » sont
ignorées. Bottles garde sa configuration en mémoire : la bouteille doit être
rechargée (fermer/rouvrir Bottles) pour voir le nouveau programme.
"""

from __future__ import annotations

import os
import shutil
import tempfile
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Mapping, Optional, Tuple

import yaml

FLATPAK_ID = "com.usebottles.bottles"
BACKUP_NAME = "bottle.yml.proton-autogen.bak"

# Codes d'avertissement renvoyés dans ExportResult.warnings (traduits par l'UX).
WARNING_BOTTLES_RUNNING = "bottles_running"
WARNING_FLATPAK_SANDBOX = "flatpak_sandbox"

# Variables d'environnement propres à Proton / Steam : sans objet (ou nuisibles)
# dans une bouteille Bottles. WINEPREFIX / WINEARCH sont aussi refusées par
# Bottles lui-même.
_ENV_DROP_PREFIXES = ("PROTON_", "STEAM_COMPAT_")
_ENV_DROP_NAMES = frozenset({
    "WINEPREFIX", "WINEARCH", "SteamAppId", "SteamGameId", "SteamUser",
})


class BottlesExportError(Exception):
    """Échec attendu : message lisible, destiné à être affiché à l'utilisateur."""


@dataclass(frozen=True)
class Bottle:
    name: str           # nom affiché dans Bottles (clé « Name » de bottle.yml)
    directory: Path     # dossier de la bouteille
    source: str         # "native" ou "flatpak"

    @property
    def config_file(self) -> Path:
        return self.directory / "bottle.yml"


@dataclass
class ExportResult:
    status: str                      # "added" ou "already_present"
    program_id: str
    bottle: Bottle
    backup: Optional[Path] = None
    ignored_env: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


# --------------------------------------------------------------------------- #
# Découverte des bouteilles
# --------------------------------------------------------------------------- #

def bottles_roots() -> List[Tuple[str, Path]]:
    """Dossiers qui contiennent les bouteilles : (source, chemin)."""
    data_home = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share")
    roots = [("native", data_home / "bottles" / "bottles")]

    flatpak = Path.home() / ".var" / "app" / FLATPAK_ID / "data" / "bottles" / "bottles"
    if flatpak not in [root for _src, root in roots]:
        roots.append(("flatpak", flatpak))
    return roots


def _load_config(path: Path) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
    except (OSError, yaml.YAMLError, UnicodeDecodeError) as exc:
        raise BottlesExportError(f"cannot read {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise BottlesExportError(f"unexpected content in {path}")
    return data


def list_bottles(roots: Optional[List[Tuple[str, Path]]] = None) -> List[Bottle]:
    """Bouteilles utilisables, triées par nom.

    Ignore les dossiers sans bottle.yml lisible et les bouteilles « Steam »."""
    bottles: List[Bottle] = []
    for source, root in (roots if roots is not None else bottles_roots()):
        try:
            entries = sorted(p for p in Path(root).iterdir() if p.is_dir())
        except OSError:
            continue
        for directory in entries:
            config_file = directory / "bottle.yml"
            if not config_file.is_file():
                continue
            try:
                data = _load_config(config_file)
            except BottlesExportError:
                continue
            if data.get("Environment") == "Steam":
                continue
            name = data.get("Name")
            bottles.append(Bottle(
                name=str(name) if name else directory.name,
                directory=directory,
                source=source,
            ))
    return sorted(bottles, key=lambda b: (b.name.lower(), b.source))


def bottles_running() -> bool:
    """Bottles est-il ouvert ? Meilleur effort (psutil), False si indéterminé."""
    try:
        import psutil
    except ImportError:
        return False

    me = os.getpid()
    for process in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            if process.info["pid"] == me:
                continue
            if process.info["name"] == "bottles":
                return True
            for arg in process.info["cmdline"] or ():
                if arg.endswith("/bin/bottles") or FLATPAK_ID in arg.split("/"):
                    return True
        except (psutil.Error, OSError):
            continue
    return False


# --------------------------------------------------------------------------- #
# Construction de l'entrée « programme »
# --------------------------------------------------------------------------- #

def _game_executable(game: Mapping) -> Path:
    raw = game.get("path")
    if not raw:
        raise BottlesExportError("no executable path configured for this game")
    exe = Path(os.path.expandvars(os.fspath(raw))).expanduser()
    if not exe.is_absolute():
        exe = Path(os.path.abspath(exe))
    if not exe.is_file():
        raise BottlesExportError(f"executable not found: {exe}")
    return exe


def _exportable_env(game: Mapping) -> Tuple[dict, List[str]]:
    """(variables à exporter, noms ignorés). Seuls les couples str -> str passent."""
    env = game.get("env")
    kept, ignored = {}, []
    if not isinstance(env, Mapping):
        return kept, ignored
    for key, value in env.items():
        if (not isinstance(key, str) or not isinstance(value, str)
                or key in _ENV_DROP_NAMES or key.startswith(_ENV_DROP_PREFIXES)):
            ignored.append(str(key))
        else:
            kept[key] = value
    return kept, ignored


def build_program(game: Mapping, program_id: Optional[str] = None) -> Tuple[dict, List[str]]:
    """Entrée `External_Programs` d'un jeu : (programme, noms d'env ignorés).

    Mêmes clés que « Ajouter un raccourci » dans Bottles (id, name, executable,
    path, folder), plus : l'environnement du jeu (sans les variables propres à
    Proton) et GameMode s'il est activé. Les réglages DXVK / VKD3D restent ceux
    de la bouteille.
    """
    exe = _game_executable(game)
    env, ignored = _exportable_env(game)

    program = {
        "id": program_id or str(uuid.uuid4()),
        "name": str(game.get("name") or exe.stem),
        "executable": exe.name,
        "path": str(exe),
        "folder": str(exe.parent),
        "arguments": "",
        "icon": "",
    }
    if env:
        program["environment"] = env
    if (game.get("features") or {}).get("gamemode"):
        program["gamemode"] = True
    return program, ignored


# --------------------------------------------------------------------------- #
# Écriture
# --------------------------------------------------------------------------- #

def _write_config_atomic(path: Path, data: dict) -> None:
    """Réécrit bottle.yml comme Bottles : YAML « safe », indentation 4,
    fichier temporaire + os.replace, droits conservés."""
    mode = path.stat().st_mode & 0o777
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".bottle-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            yaml.safe_dump(data, handle, indent=4, allow_unicode=True)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(tmp, mode)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def export_game_to_bottle(game: Mapping, bottle: Bottle) -> ExportResult:
    """Ajoute `game` aux programmes de `bottle`.

    Ne duplique jamais : si un programme avec le même chemin existe déjà, rien
    n'est écrit et le statut est « already_present ».
    """
    config_file = bottle.config_file
    if not config_file.is_file():
        raise BottlesExportError(f"bottle configuration not found: {config_file}")

    program, ignored = build_program(game)
    data = _load_config(config_file)

    programs = data.get("External_Programs")
    if programs is None:
        programs = {}
    if not isinstance(programs, dict):
        raise BottlesExportError("unexpected 'External_Programs' section in bottle.yml")

    # Ordre voulu : le plus important d'abord (Bottles ouvert peut écraser la modification).
    warnings: List[str] = []
    if bottles_running():
        warnings.append(WARNING_BOTTLES_RUNNING)
    if bottle.source == "flatpak":
        warnings.append(WARNING_FLATPAK_SANDBOX)

    for existing_id, existing in programs.items():
        if isinstance(existing, dict) and existing.get("path") == program["path"]:
            return ExportResult("already_present", str(existing.get("id") or existing_id),
                                bottle, None, ignored, warnings)

    programs[program["id"]] = program
    data["External_Programs"] = programs

    backup = bottle.directory / BACKUP_NAME
    try:
        shutil.copy2(config_file, backup)
        _write_config_atomic(config_file, data)
        saved = _load_config(config_file)
        if program["id"] not in (saved.get("External_Programs") or {}):
            raise BottlesExportError("verification failed after writing bottle.yml")
    except BottlesExportError:
        shutil.copy2(backup, config_file)
        raise
    except (OSError, yaml.YAMLError) as exc:
        if backup.is_file():
            shutil.copy2(backup, config_file)
        raise BottlesExportError(f"cannot write {config_file}: {exc}") from exc

    return ExportResult("added", program["id"], bottle, backup, ignored, warnings)
