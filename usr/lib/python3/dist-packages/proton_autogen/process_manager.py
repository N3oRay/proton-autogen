# process_manager.py — version corrigée
import os
import signal
import time
import subprocess
import threading

from proton_autogen.utils.logger import StructuredLogger

logger = StructuredLogger("proton-autogen.process_manager")

_lock = threading.Lock()
_registry: dict[str, subprocess.Popen] = {}


def register(game_id: str, proc: subprocess.Popen) -> None:
    with _lock:
        _registry[game_id] = proc
    logger.info("Process registered", game_id=game_id, pid=proc.pid)


def unregister(game_id: str) -> None:
    with _lock:
        _registry.pop(game_id, None)


def is_running(game_id: str) -> bool:
    with _lock:
        proc = _registry.get(game_id)
    return proc is not None and proc.poll() is None


def stop(game_id: str, kill_after: float = 5.0) -> bool:
    with _lock:
        proc = _registry.get(game_id)

    if proc is None or proc.poll() is not None:
        logger.warning("Stop requested but no active process", game_id=game_id)
        return False

    try:
        pgid = os.getpgid(proc.pid)
    except ProcessLookupError:
        logger.warning("Process already gone", game_id=game_id, pid=proc.pid)
        return False

    logger.info("Sending SIGTERM", game_id=game_id, pgid=pgid)
    os.killpg(pgid, signal.SIGTERM)

    # ⚠️ PAS de proc.wait() ici — le thread run_process() s'en charge déjà.
    def escalate():
        time.sleep(kill_after)
        if proc.poll() is None:
            try:
                pgid2 = os.getpgid(proc.pid)
                logger.warning("SIGTERM ignored, sending SIGKILL", game_id=game_id, pgid=pgid2)
                os.killpg(pgid2, signal.SIGKILL)
            except ProcessLookupError:
                pass

    threading.Thread(target=escalate, daemon=True).start()
    return True
