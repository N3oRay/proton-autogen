#!/usr/bin/env python3

"""
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
"""

import os
import signal
import threading
import time
from dataclasses import dataclass
from typing import Dict, Optional, Any


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_STOP_TIMEOUT = 5.0


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
# Internal helpers
# ---------------------------------------------------------------------------

def _safe_pid(process) -> Optional[int]:
    """
    Retourne le PID du processus si disponible.
    """
    try:
        return int(process.pid)
    except (AttributeError, TypeError, ValueError):
        return None


def _is_running(process) -> bool:
    """
    Vérifie si le processus est encore vivant.
    """
    try:
        return process.poll() is None
    except Exception:
        return False


def _terminate_process_group(process) -> bool:
    """
    Envoie SIGTERM à tout le groupe de processus.

    core.py utilise :

        start_new_session=True

    donc le PID du processus devient également le PGID
    de sa nouvelle session.

    Cela permet de terminer Proton + Wine + les processus
    enfants appartenant au même groupe.
    """

    pid = _safe_pid(process)

    if pid is None:
        return False

    try:
        os.killpg(pid, signal.SIGTERM)
        return True

    except ProcessLookupError:
        return False

    except PermissionError:
        return False

    except OSError:
        return False


def _kill_process_group(process) -> bool:
    """
    Force l'arrêt de tout le groupe avec SIGKILL.
    """

    pid = _safe_pid(process)

    if pid is None:
        return False

    try:
        os.killpg(pid, signal.SIGKILL)
        return True

    except ProcessLookupError:
        return False

    except PermissionError:
        return False

    except OSError:
        return False


def _wait_process(process, timeout: float) -> bool:
    """
    Attend la fin du processus pendant timeout secondes.

    Retourne True si le processus est terminé.
    """

    timeout = max(0.0, float(timeout))

    try:
        process.wait(timeout=timeout)
        return True

    except Exception:
        return False


def _remove_if_same(game_id: str, process) -> bool:
    """
    Supprime l'entrée uniquement si elle correspond toujours
    au même objet Popen.

    Très important lorsque plusieurs jeux sont lancés.

    Exemple :

        game A -> PID 100
        game B -> PID 200

    Si A termine pendant qu'une opération agit sur B,
    A ne doit jamais supprimer l'entrée de B.
    """

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
) -> bool:
    """
    Enregistre un processus Proton.

    Plusieurs game_id différents peuvent être actifs simultanément.

    Un même game_id ne doit représenter qu'une seule instance.
    """

    if not game_id:
        return False

    if process is None:
        return False

    game_id = str(game_id)

    record = ProcessRecord(
        game_id=game_id,
        process=process,
        prefix_path=prefix_path,
        proton_dir=proton_dir,
        env=env,
    )

    with _lock:

        # Une seule instance pour un même game_id.
        existing = _processes.get(game_id)

        if existing is not None:
            existing_process = existing.process

            if _is_running(existing_process):
                return False

            # Ancien processus terminé.
            del _processes[game_id]

        _processes[game_id] = record

    return True


# ---------------------------------------------------------------------------
# Unregister
# ---------------------------------------------------------------------------

def unregister(game_id: str, process=None) -> bool:
    """
    Retire un processus du registre.

    Si process est fourni, l'entrée est supprimée uniquement si
    elle correspond au même objet Popen.

    Cette protection évite les race conditions.
    """

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
    """
    Retourne l'enregistrement d'un jeu.
    """

    if not game_id:
        return None

    with _lock:
        return _processes.get(str(game_id))


def get_process(game_id: str):
    """
    Retourne directement l'objet Popen.
    """

    record = get(game_id)

    if record is None:
        return None

    return record.process


def is_running(game_id: str) -> bool:
    """
    Indique si le jeu est actuellement enregistré et vivant.
    """

    record = get(game_id)

    if record is None:
        return False

    if _is_running(record.process):
        return True

    # Nettoyage opportuniste.
    unregister(game_id, record.process)

    return False


def list_running() -> Dict[str, ProcessRecord]:
    """
    Retourne une copie du registre des processus actuellement connus.

    Le dictionnaire retourné peut être utilisé sans conserver le lock.
    """

    running = {}

    with _lock:

        for game_id, record in list(_processes.items()):

            if _is_running(record.process):
                running[game_id] = record

    return running


def list_game_ids():
    """
    Retourne la liste des game_id actuellement actifs.
    """

    return list(list_running().keys())


def count() -> int:
    """
    Nombre de jeux actuellement actifs.
    """

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

        1. retrouver game_id
        2. SIGTERM au groupe Proton/Wine
        3. attendre jusqu'à timeout secondes
        4. si toujours vivant :
               SIGKILL au groupe
        5. attendre la fin
        6. supprimer l'entrée du registre

    Retourne True si un processus correspondant a été trouvé.

    IMPORTANT :

        stop(game_id)

    est volontairement la forme principale utilisée par dashboard_actions.py.
    """

    if not game_id:
        return False

    game_id = str(game_id)

    # -------------------------------------------------------
    # Normalisation du timeout
    # -------------------------------------------------------

    try:
        timeout = float(timeout)

    except (TypeError, ValueError):
        timeout = DEFAULT_STOP_TIMEOUT

    timeout = max(0.0, timeout)

    # -------------------------------------------------------
    # Recherche du processus
    # -------------------------------------------------------

    with _lock:

        record = _processes.get(game_id)

        if record is None:
            return False

        process = record.process

    # -------------------------------------------------------
    # Process déjà terminé
    # -------------------------------------------------------

    if not _is_running(process):

        _remove_if_same(game_id, process)
        return False

    # -------------------------------------------------------
    # Phase 1 : arrêt propre
    # -------------------------------------------------------

    _terminate_process_group(process)

    # -------------------------------------------------------
    # Phase 2 : attente
    # -------------------------------------------------------

    if _wait_process(process, timeout):

        _remove_if_same(game_id, process)
        return True

    # -------------------------------------------------------
    # Phase 3 : force kill
    # -------------------------------------------------------

    _kill_process_group(process)

    # -------------------------------------------------------
    # Attente finale
    # -------------------------------------------------------

    try:
        process.wait(timeout=2.0)

    except Exception:
        pass

    # -------------------------------------------------------
    # Nettoyage
    # -------------------------------------------------------

    _remove_if_same(game_id, process)

    return True


# ---------------------------------------------------------------------------
# Force stop
# ---------------------------------------------------------------------------

def force_stop(game_id: str) -> bool:
    """
    Arrêt immédiat sans attendre 5 secondes.

    Utile si l'UI veut proposer ultérieurement un bouton
    "Forcer l'arrêt".
    """

    if not game_id:
        return False

    game_id = str(game_id)

    with _lock:

        record = _processes.get(game_id)

        if record is None:
            return False

        process = record.process

    if not _is_running(process):

        _remove_if_same(game_id, process)
        return False

    _kill_process_group(process)

    try:
        process.wait(timeout=2.0)

    except Exception:
        pass

    _remove_if_same(game_id, process)

    return True


# ---------------------------------------------------------------------------
# Stop all
# ---------------------------------------------------------------------------

def stop_all(
    timeout: float = DEFAULT_STOP_TIMEOUT,
) -> int:
    """
    Arrête tous les jeux actuellement enregistrés.

    Chaque jeu est traité indépendamment.

    Retourne le nombre de jeux pour lesquels un arrêt
    a été demandé.
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
    """
    Supprime du registre les processus terminés.

    Retourne le nombre d'entrées supprimées.
    """

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
    """
    Retourne des informations simples sur un processus.
    """

    record = get(game_id)

    if record is None:
        return None

    pid = _safe_pid(record.process)

    return {
        "game_id": record.game_id,
        "pid": pid,
        "running": _is_running(record.process),
        "prefix_path": record.prefix_path,
        "proton_dir": record.proton_dir,
        "registered_at": record.registered_at,
    }


def get_all_info() -> Dict[str, dict]:
    """
    Retourne les informations de tous les processus.
    """

    result = {}

    with _lock:

        for game_id, record in list(_processes.items()):

            result[game_id] = {
                "game_id": game_id,
                "pid": _safe_pid(record.process),
                "running": _is_running(record.process),
                "prefix_path": record.prefix_path,
                "proton_dir": record.proton_dir,
                "registered_at": record.registered_at,
            }

    return result
