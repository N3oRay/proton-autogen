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
"""

import os
import re
import signal
import subprocess
import threading
import time
from dataclasses import dataclass
from typing import Dict, Optional, Any

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
        pids = [int(p) for p in out.stdout.split() if p.strip()]

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
) -> bool:
    """
    Enregistre un processus Proton.
    Plusieurs game_id différents peuvent être actifs simultanément.
    Un même game_id ne doit représenter qu'une seule instance.
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

    return True


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
        return True


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
        return False

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
            return False
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
            return False
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
    return removed


# ---------------------------------------------------------------------------
# Debug information
# ---------------------------------------------------------------------------

def get_info(game_id: str) -> Optional[dict]:
    record = get(game_id)
    if record is None:
        return None

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
