import time
from pathlib import Path
from proton_autogen.notify import notifications
from proton_autogen.stats import update_playtime


def finalize_session(exe_path, start_time, exit_code=None):
    """
    Finalise une session de jeu et met à jour les statistiques.

    Args:
        exe_path (str): chemin du jeu
        start_time (float): time.time() au lancement
        exit_code (int|None): code retour du process (si disponible)

    Returns:
        dict: résumé de la session
    """

    end_time = time.time()
    session_seconds = int(end_time - start_time)

    result = {
        "exe_path": exe_path,
        "session_seconds": session_seconds,
        "exit_code": exit_code,
        "status": "unknown",
        "updated": False
    }

    # -------------------------
    # ignore sessions trop courtes
    # -------------------------
    if session_seconds <= 0:
        result["status"] = "ignored_too_short"
        return result

    # -------------------------
    # interprétation du résultat
    # -------------------------
    if exit_code is None:
        result["status"] = "no_exit_code"
    elif exit_code == 0:
        result["status"] = "clean_exit"
    else:
        result["status"] = "crash_or_error"

    # -------------------------
    # update stats
    # -------------------------
    try:

        name = Path(exe_path).stem
        notifications.notify("info", "Update", f"Update Data : {name}", ui=True)

        update_playtime(exe_path, session_seconds)
        result["updated"] = True
    except Exception as e:
        print("[proton-autogen] stats update failed:", e)
        result["error"] = str(e)

    return result
