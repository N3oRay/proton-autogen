#!/usr/bin/env python3

"""
running_registry
Registre inter-processus des jeux en cours d'exécution.

Pourquoi ce module existe
-------------------------
process_manager garde ses enregistrements dans un dictionnaire Python,
donc dans la mémoire d'UN SEUL processus. Un jeu lancé depuis le CLI
(`proton-autogen game.exe`) est enregistré dans la mémoire du processus
CLI : la fenêtre UX (`--ux`), qui est un autre processus, ne peut ni le
voir ni l'arrêter.

Ce module écrit un petit fichier JSON par jeu dans le dossier de données
EXISTANT de proton-autogen (~/.local/share/proton-autogen/, le même que
logs/ et backups/), lisible par tous les processus proton-autogen.
Aucun nouveau répertoire n'est créé : les fichiers sont à plat, nommés
running-<game_id>.json.

Fonctionnement
--------------
    - un fichier  running-<game_id>.json  par jeu enregistré
    - écriture atomique (fichier temporaire + os.replace)
    - fichiers 0600 (données de session, pas de partage)
    - un enregistrement est considéré vivant si :
        1. le PID principal existe ET son heure de démarrage correspond
           (protège contre la réutilisation d'un PID), ou
        2. le PID principal est mort mais son groupe de processus a encore
           des membres (le Popen local peut mourir avant le vrai jeu)
    - les enregistrements périmés sont purgés à la lecture (y compris après
      un redémarrage : l'heure de démarrage du PID ne correspond plus)

Le dossier peut être forcé avec la variable PROTON_AUTOGEN_STATE_DIR
(tests, installations atypiques).

Ce module ne dépend ni de GTK ni de process_manager.
"""

import json
import os
import re
import tempfile
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Optional

try:
    import psutil
except ImportError:  # psutil est une dépendance du projet, mais on reste tolérant
    psutil = None


SCHEMA_VERSION = 1

# Fichiers à plat dans le dossier de données existant.
FILE_PREFIX = "running-"
FILE_SUFFIX = ".json"

# game_id = md5 hexadécimal dans le projet ; on accepte un jeu de
# caractères sûr plus large, jamais de séparateur de chemin.
_ID_RE = re.compile(r"^[A-Za-z0-9_.-]{1,128}$")

# Tolérance (secondes) entre l'heure de démarrage enregistrée et celle
# relue plus tard : psutil et /proc n'ont pas la même granularité.
START_TIME_TOLERANCE = 1.5


# ---------------------------------------------------------------------------
# Enregistrement
# ---------------------------------------------------------------------------

@dataclass
class RegistryRecord:
    game_id: str
    pid: int
    pgid: Optional[int] = None
    start_time: Optional[float] = None   # heure de démarrage du PID (epoch)
    owner_pid: int = 0                   # processus proton-autogen qui a lancé
    name: Optional[str] = None
    exe_path: Optional[str] = None
    prefix_path: Optional[str] = None
    proton_dir: Optional[str] = None
    registered_at: float = 0.0           # horloge murale (epoch)
    schema: int = SCHEMA_VERSION

    def to_info(self) -> dict:
        """Même forme que process_manager.get_info(), plus 'external'."""
        return {
            "game_id": self.game_id,
            "pid": self.pid,
            "running": True,
            "prefix_path": self.prefix_path,
            "proton_dir": self.proton_dir,
            "exe_path": self.exe_path,
            "registered_at": self.registered_at,
            "name": self.name,
            "external": self.owner_pid != os.getpid(),
        }


# ---------------------------------------------------------------------------
# Chemins
# ---------------------------------------------------------------------------

def registry_dir() -> Path:
    """
    Dossier contenant les fichiers running-<game_id>.json : le dossier de
    données existant de proton-autogen (même racine que logs/ et backups/).
    """
    override = os.environ.get("PROTON_AUTOGEN_STATE_DIR")
    if override:
        return Path(override)

    return Path.home() / ".local/share/proton-autogen"


def _valid_id(game_id) -> bool:
    return bool(game_id) and bool(_ID_RE.match(str(game_id)))


def _record_path(game_id: str) -> Optional[Path]:
    if not _valid_id(game_id):
        return None
    return registry_dir() / f"{FILE_PREFIX}{game_id}{FILE_SUFFIX}"


def _ensure_dir() -> Optional[Path]:
    directory = registry_dir()
    try:
        # Le dossier existe déjà dans l'usage normal (logs/, backups/) ;
        # on ne le crée que s'il manque, sans sous-dossier dédié.
        directory.mkdir(parents=True, exist_ok=True)
        return directory
    except OSError:
        return None


# ---------------------------------------------------------------------------
# Informations système sur un PID
# ---------------------------------------------------------------------------

def process_start_time(pid: int) -> Optional[float]:
    """Heure de démarrage (epoch) d'un PID, ou None s'il n'existe pas."""
    if psutil is not None:
        try:
            return float(psutil.Process(pid).create_time())
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            return None
        except Exception:
            return None

    # Repli /proc : champ 22 (starttime, en ticks depuis le boot)
    try:
        with open(f"/proc/{pid}/stat", "r", encoding="utf-8", errors="replace") as f:
            raw = f.read()
        # Le nom (champ 2) est entre parenthèses et peut contenir espaces
        # et parenthèses : on coupe après la DERNIÈRE parenthèse fermante.
        fields = raw.rsplit(")", 1)[1].split()
        ticks = int(fields[19])
        with open("/proc/stat", "r", encoding="utf-8") as f:
            btime = next(int(l.split()[1]) for l in f if l.startswith("btime"))
        return btime + ticks / os.sysconf("SC_CLK_TCK")
    except (OSError, ValueError, IndexError, StopIteration):
        return None


def _pid_exists(pid: int) -> bool:
    if not isinstance(pid, int) or pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False

    # Un zombie répond à kill(pid, 0) : on ne le compte pas comme vivant.
    if psutil is not None:
        try:
            return psutil.Process(pid).status() != psutil.STATUS_ZOMBIE
        except psutil.NoSuchProcess:
            return False
        except Exception:
            return True
    return True


def _group_has_members(pgid: Optional[int]) -> bool:
    """Vrai si au moins un processus appartient encore au groupe pgid."""
    if not isinstance(pgid, int) or pgid <= 1:
        return False

    # Test rapide : le groupe existe-t-il ?
    try:
        os.killpg(pgid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        pass
    except OSError:
        return False

    # killpg(pgid, 0) réussit aussi si le groupe ne contient que des
    # zombies (processus terminés mais pas encore « récoltés ») : on
    # vérifie donc qu'au moins un membre n'est pas un zombie.
    return _group_has_live_member(pgid)


def _group_has_live_member(pgid: int) -> bool:
    try:
        entries = os.listdir("/proc")
    except OSError:
        return True   # /proc illisible : on garde le résultat de killpg

    for entry in entries:
        if not entry.isdigit():
            continue
        try:
            with open(f"/proc/{entry}/stat", "r", encoding="utf-8", errors="replace") as f:
                raw = f.read()
            # Après la dernière ")" : état, ppid, pgrp, ...
            fields = raw.rsplit(")", 1)[1].split()
            state, group = fields[0], int(fields[2])
        except (OSError, ValueError, IndexError):
            continue   # le processus a disparu pendant le scan

        if group == pgid and state not in ("Z", "X"):
            return True

    return False


# ---------------------------------------------------------------------------
# Écriture / lecture
# ---------------------------------------------------------------------------

def write(
    game_id: str,
    pid: int,
    pgid: Optional[int] = None,
    owner_pid: Optional[int] = None,
    name: Optional[str] = None,
    exe_path: Optional[str] = None,
    prefix_path: Optional[str] = None,
    proton_dir: Optional[str] = None,
) -> bool:
    """Écrit (ou remplace) l'enregistrement d'un jeu. Best-effort."""
    path = _record_path(game_id)
    directory = _ensure_dir()
    if path is None or directory is None or not isinstance(pid, int) or pid <= 0:
        return False

    if pgid is None:
        try:
            pgid = os.getpgid(pid)
        except OSError:
            pgid = None

    record = RegistryRecord(
        game_id=str(game_id),
        pid=pid,
        pgid=pgid,
        start_time=process_start_time(pid),
        owner_pid=owner_pid if owner_pid is not None else os.getpid(),
        name=name,
        exe_path=exe_path,
        prefix_path=prefix_path,
        proton_dir=proton_dir,
        registered_at=time.time(),
    )

    tmp_name = None
    try:
        fd, tmp_name = tempfile.mkstemp(dir=directory, prefix=".running-tmp-", suffix=FILE_SUFFIX)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(asdict(record), f)
        os.chmod(tmp_name, 0o600)
        os.replace(tmp_name, path)
        return True
    except OSError:
        if tmp_name:
            try:
                os.unlink(tmp_name)
            except OSError:
                pass
        return False


def read(game_id: str) -> Optional[RegistryRecord]:
    """Relit un enregistrement. Ne vérifie PAS qu'il est vivant."""
    path = _record_path(game_id)
    if path is None:
        return None

    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return None

    return _record_from_dict(data, expected_id=str(game_id))


def _record_from_dict(data, expected_id: Optional[str] = None) -> Optional[RegistryRecord]:
    if not isinstance(data, dict):
        return None

    try:
        game_id = str(data["game_id"])
        pid = int(data["pid"])
    except (KeyError, TypeError, ValueError):
        return None

    # L'identifiant interne doit correspondre au nom du fichier.
    if not _valid_id(game_id) or (expected_id is not None and game_id != expected_id):
        return None

    def _opt_int(key):
        value = data.get(key)
        return value if isinstance(value, int) and not isinstance(value, bool) else None

    def _opt_str(key):
        value = data.get(key)
        return value if isinstance(value, str) else None

    start_time = data.get("start_time")
    if not isinstance(start_time, (int, float)) or isinstance(start_time, bool):
        start_time = None

    registered_at = data.get("registered_at")
    if not isinstance(registered_at, (int, float)) or isinstance(registered_at, bool):
        registered_at = 0.0

    return RegistryRecord(
        game_id=game_id,
        pid=pid,
        pgid=_opt_int("pgid"),
        start_time=start_time,
        owner_pid=_opt_int("owner_pid") or 0,
        name=_opt_str("name"),
        exe_path=_opt_str("exe_path"),
        prefix_path=_opt_str("prefix_path"),
        proton_dir=_opt_str("proton_dir"),
        registered_at=float(registered_at),
    )


def remove(game_id: str) -> bool:
    path = _record_path(game_id)
    if path is None:
        return False
    try:
        path.unlink()
        return True
    except FileNotFoundError:
        return False
    except OSError:
        return False


def list_records() -> Dict[str, RegistryRecord]:
    """Tous les enregistrements lisibles (vivants ou non)."""
    directory = registry_dir()
    records: Dict[str, RegistryRecord] = {}

    try:
        entries = list(directory.glob(f"{FILE_PREFIX}*{FILE_SUFFIX}"))
    except OSError:
        return records

    for path in entries:
        game_id = path.name[len(FILE_PREFIX):-len(FILE_SUFFIX)]
        if not _valid_id(game_id):
            continue
        record = read(game_id)
        if record is not None:
            records[game_id] = record

    return records


# ---------------------------------------------------------------------------
# Vivacité
# ---------------------------------------------------------------------------

def main_pid_matches(record: RegistryRecord) -> bool:
    """Le PID principal existe ET c'est bien le même processus."""
    if not _pid_exists(record.pid):
        return False

    if record.start_time is None:
        return True   # rien à comparer : on fait confiance au PID

    current = process_start_time(record.pid)
    if current is None:
        return False

    return abs(current - record.start_time) <= START_TIME_TOLERANCE


def pid_was_reused(record: RegistryRecord) -> bool:
    """Le PID principal existe mais appartient à un autre processus."""
    return _pid_exists(record.pid) and not main_pid_matches(record)


def is_alive(record: RegistryRecord) -> bool:
    """
    Vrai si le jeu enregistré tourne encore :
        - PID principal identique, ou
        - PID principal mort (Popen local parti avant le jeu) mais le
          groupe de processus a encore des membres.

    Si le PID a été réutilisé par un autre processus, on ne regarde pas le
    groupe : son numéro ne désigne plus forcément notre jeu.
    """
    if main_pid_matches(record):
        return True

    if pid_was_reused(record):
        return False

    return _group_has_members(record.pgid)


def purge_stale(is_alive_fn=is_alive) -> int:
    """Supprime les enregistrements dont le jeu n'existe plus."""
    removed = 0
    for game_id, record in list_records().items():
        if not is_alive_fn(record):
            if remove(game_id):
                removed += 1
    return removed
