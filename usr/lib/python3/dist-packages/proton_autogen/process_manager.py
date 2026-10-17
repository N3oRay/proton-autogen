#!/usr/bin/env python3

"""
process_manager
Proton-Autogen process manager.

Responsabilités :
    - enregistrer les processus Proton lancés par core.py
    - supporter plusieurs jeux simultanément
    - identifier chaque jeu par game_id
    - arrêter proprement un jeu
    - attendre jusqu'à 5 secondes
    - forcer l'arrêt du groupe de processus après timeout
    - éviter qu'un jeu termine accidentellement l'enregistrement d'un autre
    - être sûr vis-à-vis des threads utilisés par core.py

Point important (retour d'expérience) :
    Le Popen local (celui de la commande proton/gamescope/wine) peut se
    terminer ou être tué prématurément (ex: reaper de gamescope d'une
    autre session, wineserver qui se détache) sans que le jeu réel soit
    mort. os.killpg sur ce seul Popen n'est donc pas suffisant : on
    complète systématiquement par un `wineserver -k` scopé au préfixe,
    qui est le mécanisme officiel Wine pour arrêter tout ce qui est
    rattaché à un WINEPREFIX donné, indépendamment du pgid/session.

Suivi inter-processus (CLI <-> UX) :
    Le dictionnaire _processes n'existe que dans la mémoire du processus qui
    a lancé le jeu. Pour qu'un jeu lancé depuis le CLI soit visible et
    arrêtable depuis l'UX (et inversement), chaque enregistrement est aussi
    écrit dans un fichier via running_registry
    (~/.local/share/proton-autogen/running-<game_id>.json). Les jeux lancés par un AUTRE
    processus sont exposés par list_external() / get_info() / is_running()
    et arrêtables par stop() (via le groupe de processus enregistré, puis
    wineserver -k, puis kill par PID).
"""

import os
import re
import signal
import subprocess
import threading
import time
from dataclasses import dataclass
from typing import Dict, Optional, Any

from proton_autogen import running_registry
from proton_autogen.utils.logger import StructuredLogger

logger = StructuredLogger("proton-autogen.process_manager")


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_STOP_TIMEOUT = 5.0
WINESERVER_KILL_TIMEOUT = 5.0
PGREP_TIMEOUT = 2.0


# ---------------------------------------------------------------------------
# Process record
# ---------------------------------------------------------------------------

@dataclass
class ProcessRecord:
    game_id: str
    process: Any

    prefix_path: Optional[str] = None
    proton_dir: Optional[str] = None
    env: Optional[dict] = None
    exe_path: Optional[str] = None   # <-- ajouté pour pgrep de secours

    registered_at: float = 0.0

    def __post_init__(self):
        if not self.registered_at:
            self.registered_at = time.monotonic()


# ---------------------------------------------------------------------------
# Global process registry
# ---------------------------------------------------------------------------

_processes: Dict[str, ProcessRecord] = {}

_lock = threading.RLock()


# ---------------------------------------------------------------------------
# Internal helpers — Popen local
# ---------------------------------------------------------------------------

def _safe_pid(process) -> Optional[int]:
    try:
        return int(process.pid)
    except (AttributeError, TypeError, ValueError):
        return None


def _is_running(process) -> bool:
    try:
        return process.poll() is None
    except Exception:
        return False


def _terminate_process_group(process) -> bool:
    pid = _safe_pid(process)
    if pid is None:
        return False
    try:
        os.killpg(pid, signal.SIGTERM)
        return True
    except (ProcessLookupError, PermissionError, OSError):
        return False


def _kill_process_group(process) -> bool:
    pid = _safe_pid(process)
    if pid is None:
        return False
    try:
        os.killpg(pid, signal.SIGKILL)
        return True
    except (ProcessLookupError, PermissionError, OSError):
        return False


def _wait_process(process, timeout: float) -> bool:
    timeout = max(0.0, float(timeout))
    try:
        process.wait(timeout=timeout)
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Internal helpers — vérification / arrêt indépendants du Popen local
# ---------------------------------------------------------------------------

# Ajouter un cache avec TTL court (0.5-1 sec)
_pgrep_cache: Dict[str, tuple[float, list]] = {}
_pgrep_cache_lock = threading.Lock()

_LAUNCHER_NAMES = ("proton-autogen", "proton_autogen")


def _is_launcher_process(pid: int) -> bool:
    """
    Vrai si pid est proton-autogen lui-même (CLI ou UX), ce processus ou
    son parent.

    `pgrep -f game.exe` correspond à la ligne de commande COMPLÈTE : la
    commande `proton-autogen game.exe` contient donc le nom de l'exe et
    serait tuée par _kill_stray_pids() comme un « reste » du jeu. On
    l'exclut en regardant l'interpréteur et le script (argv[0], argv[1]).
    """
    if pid in (os.getpid(), os.getppid()):
        return True

    try:
        with open(f"/proc/{pid}/cmdline", "rb") as f:
            argv = f.read().split(b"\0")[:2]
    except OSError:
        return False

    for arg in argv:
        base = os.path.basename(arg.decode("utf-8", "replace"))
        if base in _LAUNCHER_NAMES:
            return True

    return False

def _find_pids_by_exe(exe_path: str, use_cache=True) -> list:
    if not exe_path:
        return []

    exe_basename = os.path.basename(exe_path)

    # Vérifier cache
    if use_cache:
        with _pgrep_cache_lock:
            cached_time, cached_pids = _pgrep_cache.get(exe_basename, (0, None))
            if cached_pids is not None and (time.monotonic() - cached_time) < 1.0:
                return cached_pids

    try:
        out = subprocess.run(
            ["pgrep", "-if", re.escape(exe_basename)],
            capture_output=True,
            text=True,
            timeout=PGREP_TIMEOUT,
        )
        pids = [
            int(p) for p in out.stdout.split()
            if p.strip() and not _is_launcher_process(int(p))
        ]

        # Mettre en cache
        with _pgrep_cache_lock:
            _pgrep_cache[exe_basename] = (time.monotonic(), pids)

        return pids
    except Exception as e:
        logger.warning(f"pgrep failed for {exe_basename}: {e}")
        return []


def _kill_wineserver_for_prefix(prefix_path: Optional[str], proton_dir: Optional[str]) -> bool:
    """
    Arrête tous les processus rattachés à un préfixe Wine via
    `wineserver -k`, le mécanisme officiel Wine. Indépendant du
    pgid/session du Popen local — c'est le filet de sécurité principal.
    """
    if not prefix_path or not proton_dir:
        return False

    wineserver_bin = os.path.join(proton_dir, "files", "bin", "wineserver")

    if not os.path.isfile(wineserver_bin):
        logger.warning(f"wineserver binary not found: {wineserver_bin}")
        return False

    env = os.environ.copy()
    env["WINEPREFIX"] = prefix_path

    try:
        logger.info(f"Killing wineserver for prefix: {prefix_path}")
        subprocess.run(
            [wineserver_bin, "-k"],
            env=env,
            timeout=WINESERVER_KILL_TIMEOUT,
        )
        return True
    except subprocess.TimeoutExpired:
        logger.warning(f"wineserver -k timed out for prefix: {prefix_path}")
        return False
    except Exception as e:
        logger.warning(f"wineserver -k failed for prefix {prefix_path}: {e}")
        return False


def _kill_stray_pids(exe_path: str) -> int:
    """
    Filet de sécurité final : tue directement par PID tout process
    correspondant encore au nom de l'exe, après le passage de
    wineserver -k. Retourne le nombre de PID tués.
    """
    pids = _find_pids_by_exe(exe_path)
    killed = 0

    for pid in pids:
        try:
            os.kill(pid, signal.SIGKILL)
            killed += 1
            logger.warning(f"Killed stray PID {pid} for {os.path.basename(exe_path)}")
        except (ProcessLookupError, PermissionError, OSError):
            continue

    return killed


def _remove_if_same(game_id: str, process) -> bool:
    with _lock:
        record = _processes.get(game_id)
        if record is None:
            return False
        if record.process is not process:
            return False
        del _processes[game_id]

    running_registry.remove(game_id)
    return True


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

def register(
    game_id: str,
    process,
    prefix_path: Optional[str] = None,
    proton_dir: Optional[str] = None,
    env: Optional[dict] = None,
    exe_path: Optional[str] = None,
    name: Optional[str] = None,
) -> bool:
    """
    Enregistre un processus Proton.
    Plusieurs game_id différents peuvent être actifs simultanément.
    Un même game_id ne doit représenter qu'une seule instance.

    L'enregistrement est aussi écrit dans le registre partagé
    (running_registry) pour être visible des autres processus
    proton-autogen (CLI <-> UX).
    """

    if not game_id or process is None:
        return False

    game_id = str(game_id)

    record = ProcessRecord(
        game_id=game_id,
        process=process,
        prefix_path=prefix_path,
        proton_dir=proton_dir,
        env=env,
        exe_path=exe_path,
    )

    with _lock:
        existing = _processes.get(game_id)

        if existing is not None:
            if _is_running(existing.process):
                logger.warning(
                    f"register() refused: game_id {game_id} already has a running process"
                )
                return False
            del _processes[game_id]

        _processes[game_id] = record

    _publish(record, name)
    return True


def _publish(record: ProcessRecord, name: Optional[str] = None) -> None:
    """Écrit l'enregistrement dans le registre partagé (best-effort)."""
    pid = _safe_pid(record.process)
    if pid is None:
        return

    try:
        running_registry.write(
            record.game_id,
            pid=pid,
            owner_pid=os.getpid(),
            name=name or (
                os.path.splitext(os.path.basename(record.exe_path))[0]
                if record.exe_path else None
            ),
            exe_path=record.exe_path,
            prefix_path=record.prefix_path,
            proton_dir=record.proton_dir,
        )
    except Exception as e:
        logger.warning(f"running_registry write failed for {record.game_id}: {e}")


# ---------------------------------------------------------------------------
# Unregister
# ---------------------------------------------------------------------------

def unregister(game_id: str, process=None) -> bool:
    if not game_id:
        return False

    game_id = str(game_id)

    with _lock:
        record = _processes.get(game_id)
        if record is None:
            return False
        if process is not None and record.process is not process:
            return False
        del _processes[game_id]
        still_running = _is_running(record.process)

    # Si le Popen local est terminé, le jeu l'est aussi dans le cas normal :
    # on retire le fichier. S'il tourne encore (ex. CLI interrompu par
    # Ctrl+C alors que le jeu continue), on LAISSE le fichier : l'UX doit
    # pouvoir voir et arrêter ce jeu devenu orphelin. Il sera purgé dès que
    # le processus aura disparu (cf. list_external / purge_stale).
    if not still_running:
        running_registry.remove(game_id)
    return True


# ---------------------------------------------------------------------------
# Jeux lancés par un autre processus (CLI <-> UX)
# ---------------------------------------------------------------------------

def _external_alive(record) -> bool:
    """
    Vivacité d'un jeu enregistré par un autre processus : PID/groupe
    (running_registry), puis pgrep par nom d'exe en dernier recours.
    Peut lancer pgrep : ne pas appeler depuis le thread principal GTK.
    """
    if running_registry.is_alive(record):
        return True

    # PID réutilisé par un autre programme : le pgrep par nom serait
    # trompeur pour ce même identifiant, on conclut directement.
    if running_registry.pid_was_reused(record):
        return False

    return bool(record.exe_path and _find_pids_by_exe(record.exe_path))


def get_external(game_id: str):
    """
    Enregistrement vivant d'un jeu lancé par un AUTRE processus, ou None.
    Purge l'enregistrement s'il est périmé.
    """
    if not game_id:
        return None

    game_id = str(game_id)
    record = running_registry.read(game_id)
    if record is None or record.owner_pid == os.getpid():
        return None

    if _external_alive(record):
        return record

    running_registry.remove(game_id)
    return None


def list_external() -> Dict[str, dict]:
    """
    Jeux en cours lancés par un autre processus proton-autogen, sous la
    forme {game_id: info}. Les enregistrements périmés sont purgés.

    Appeler depuis un thread de travail (peut lancer pgrep).
    """
    external = {}

    for game_id, record in running_registry.list_records().items():
        if record.owner_pid == os.getpid():
            continue

        if _external_alive(record):
            external[game_id] = record.to_info()
        else:
            running_registry.remove(game_id)

    return external


# ---------------------------------------------------------------------------
# Getters
# ---------------------------------------------------------------------------

def get(game_id: str) -> Optional[ProcessRecord]:
    if not game_id:
        return None
    with _lock:
        return _processes.get(str(game_id))


def get_process(game_id: str):
    record = get(game_id)
    return record.process if record else None


def is_running(game_id: str) -> bool:
    """
    Indique si le jeu est actuellement enregistré et vivant.
    Vérifie d'abord le Popen local ; si celui-ci semble mort mais
    qu'on a un exe_path, double-vérifie via pgrep avant de conclure
    que le jeu est réellement terminé.
    """
    record = get(game_id)
    if record is None:
        # Pas lancé par ce processus : peut l'être par un autre (CLI/UX).
        return get_external(game_id) is not None

    if _is_running(record.process):
        return True

    # Le Popen local semble mort — double vérification indépendante
    if record.exe_path and _find_pids_by_exe(record.exe_path):
        logger.warning(
            f"Popen for game_id {game_id} reports dead, "
            f"but real process still found via pgrep"
        )
        return True

    # Vraiment mort — nettoyage opportuniste
    unregister(game_id, record.process)
    return False


def list_running() -> Dict[str, ProcessRecord]:
    running = {}
    with _lock:
        for game_id, record in list(_processes.items()):
            if _is_running(record.process):
                running[game_id] = record
    return running


def list_game_ids():
    return list(list_running().keys())


def count() -> int:
    return len(list_running())


# ---------------------------------------------------------------------------
# Stop d'un jeu lancé par un autre processus
# ---------------------------------------------------------------------------

def _safe_external_pgid(record) -> Optional[int]:
    """
    pgid utilisable pour killpg, ou None. Refuse 0/1 et notre propre
    groupe : un enregistrement corrompu ou périmé ne doit jamais nous
    faire tuer proton-autogen lui-même ni un processus système.
    """
    pgid = record.pgid
    if not isinstance(pgid, int) or pgid <= 1:
        return None
    try:
        if pgid == os.getpgrp():
            return None
    except OSError:
        return None
    return pgid


def _stop_external(game_id: str, timeout: float) -> bool:
    """
    Arrête un jeu enregistré par un autre processus. Même séquence que
    stop(), sans objet Popen :
        1. SIGTERM au groupe enregistré, attente jusqu'à timeout
        2. SIGKILL au groupe s'il reste des membres
        3. wineserver -k scopé au préfixe
        4. kill direct des PID restants (par nom d'exe)
        5. suppression de l'enregistrement
    Le processus propriétaire (ex. le CLI) vit dans un autre groupe : il
    n'est pas touché et termine normalement (statistiques, sauvegardes).
    """
    record = running_registry.read(game_id)
    if record is None or record.owner_pid == os.getpid():
        return False

    pgid = _safe_external_pgid(record)

    if pgid is not None and running_registry.is_alive(record):
        try:
            os.killpg(pgid, signal.SIGTERM)
        except OSError:
            pass

        deadline = time.monotonic() + max(0.0, timeout)
        while time.monotonic() < deadline and running_registry.is_alive(record):
            time.sleep(0.1)

        if running_registry.is_alive(record):
            try:
                os.killpg(pgid, signal.SIGKILL)
            except OSError:
                pass

    wineserver_killed = _kill_wineserver_for_prefix(record.prefix_path, record.proton_dir)

    stray_killed = 0
    if record.exe_path:
        time.sleep(0.3)
        stray_killed = _kill_stray_pids(record.exe_path)

    running_registry.remove(game_id)

    logger.info(
        f"stop() summary for external game_id={game_id}: "
        f"owner_pid={record.owner_pid}, "
        f"wineserver_killed={wineserver_killed}, "
        f"stray_pids_killed={stray_killed}"
    )

    return True


# ---------------------------------------------------------------------------
# Stop
# ---------------------------------------------------------------------------

def stop(
    game_id: str,
    timeout: float = DEFAULT_STOP_TIMEOUT,
) -> bool:
    """
    Arrête un jeu.

    Séquence :
        1. retrouver l'enregistrement (garde prefix_path/proton_dir/exe_path
           même si le Popen local est déjà mort, pour le filet de sécurité)
        2. SIGTERM au groupe du Popen local (si vivant)
        3. attendre jusqu'à timeout secondes
        4. si toujours vivant : SIGKILL au groupe
        5. dans tous les cas : wineserver -k scopé au préfixe
           (filet de sécurité principal, indépendant du pgid)
        6. si le process réel est encore détecté via pgrep : kill direct
        7. supprimer l'entrée du registre

    Retourne True si un enregistrement correspondant a été trouvé
    et qu'une tentative d'arrêt a été effectuée (pas nécessairement
    que le process du Popen local était encore vivant).
    """

    if not game_id:
        return False

    game_id = str(game_id)

    try:
        timeout = float(timeout)
    except (TypeError, ValueError):
        timeout = DEFAULT_STOP_TIMEOUT
    timeout = max(0.0, timeout)

    with _lock:
        record = _processes.get(game_id)
        if record is None:
            # Jeu lancé par un autre processus (CLI <-> UX) ?
            return _stop_external(game_id, timeout)
        process = record.process
        prefix_path = record.prefix_path
        proton_dir = record.proton_dir
        exe_path = record.exe_path

    popen_was_running = _is_running(process)

    # -------------------------------------------------------
    # Phase 1 : arrêt propre du Popen local (si encore vivant)
    # -------------------------------------------------------
    if popen_was_running:
        _terminate_process_group(process)

        if not _wait_process(process, timeout):
            _kill_process_group(process)
            try:
                process.wait(timeout=2.0)
            except Exception:
                pass

    # -------------------------------------------------------
    # Phase 2 : filet de sécurité — wineserver -k
    # Exécuté systématiquement, que le Popen local ait été
    # vivant ou non : c'est justement le cas où le Popen
    # local ment sur l'état réel du jeu qu'on veut couvrir.
    # -------------------------------------------------------
    wineserver_killed = _kill_wineserver_for_prefix(prefix_path, proton_dir)

    # -------------------------------------------------------
    # Phase 3 : filet de sécurité final — kill direct par PID
    # -------------------------------------------------------
    stray_killed = 0
    if exe_path:
        # Petite pause pour laisser wineserver -k faire effet
        time.sleep(0.3)
        stray_killed = _kill_stray_pids(exe_path)

    # -------------------------------------------------------
    # Nettoyage registre
    # -------------------------------------------------------
    _remove_if_same(game_id, process)

    logger.info(
        f"stop() summary for game_id={game_id}: "
        f"popen_was_running={popen_was_running}, "
        f"wineserver_killed={wineserver_killed}, "
        f"stray_pids_killed={stray_killed}"
    )

    return True


# ---------------------------------------------------------------------------
# Force stop
# ---------------------------------------------------------------------------

def force_stop(game_id: str) -> bool:
    """
    Arrêt immédiat sans attendre : SIGKILL direct + wineserver -k +
    nettoyage stray PID, sans la phase SIGTERM/wait.
    """

    if not game_id:
        return False

    game_id = str(game_id)

    with _lock:
        record = _processes.get(game_id)
        if record is None:
            return _stop_external(game_id, 0.0)
        process = record.process
        prefix_path = record.prefix_path
        proton_dir = record.proton_dir
        exe_path = record.exe_path

    if _is_running(process):
        _kill_process_group(process)
        try:
            process.wait(timeout=2.0)
        except Exception:
            pass

    _kill_wineserver_for_prefix(prefix_path, proton_dir)

    if exe_path:
        time.sleep(0.3)
        _kill_stray_pids(exe_path)

    _remove_if_same(game_id, process)

    return True


# ---------------------------------------------------------------------------
# Stop all
# ---------------------------------------------------------------------------

def stop_all(timeout: float = DEFAULT_STOP_TIMEOUT) -> int:
    """
    Arrête les jeux lancés par CE processus uniquement. Les jeux lancés
    par un autre processus (CLI) ne sont volontairement pas touchés :
    fermer la fenêtre UX ne doit pas tuer un jeu lancé depuis un terminal.
    """
    with _lock:
        game_ids = list(_processes.keys())

    stopped = 0
    for game_id in game_ids:
        try:
            if stop(game_id, timeout=timeout):
                stopped += 1
        except Exception:
            continue

    return stopped


# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------

def cleanup_finished() -> int:
    removed = 0
    with _lock:
        for game_id, record in list(_processes.items()):
            if not _is_running(record.process):
                del _processes[game_id]
                removed += 1
                running_registry.remove(game_id)

    # Enregistrements d'autres processus dont le jeu n'existe plus
    running_registry.purge_stale()
    return removed


# ---------------------------------------------------------------------------
# Debug information
# ---------------------------------------------------------------------------

def get_info(game_id: str) -> Optional[dict]:
    record = get(game_id)
    if record is None:
        external = get_external(game_id)
        return external.to_info() if external else None

    return {
        "game_id": record.game_id,
        "pid": _safe_pid(record.process),
        "running": _is_running(record.process),
        "prefix_path": record.prefix_path,
        "proton_dir": record.proton_dir,
        "exe_path": record.exe_path,
        "registered_at": record.registered_at,
    }


def get_all_info() -> Dict[str, dict]:
    result = {}
    with _lock:
        for game_id, record in list(_processes.items()):
            result[game_id] = {
                "game_id": game_id,
                "pid": _safe_pid(record.process),
                "running": _is_running(record.process),
                "prefix_path": record.prefix_path,
                "proton_dir": record.proton_dir,
                "exe_path": record.exe_path,
                "registered_at": record.registered_at,
            }
    return result
