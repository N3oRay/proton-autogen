import time
from pathlib import Path
from proton_autogen.notify import notifications
from proton_autogen.stats import update_playtime
from proton_autogen.save_prompt import save_prompt_center


def finalize_session(
    exe_path,
    start_time,
    exit_code=None,
    prefix_path=None,
    game_name=None,
    game_id=None,
    release_year=None,
    save_backup_enabled=True,
):
    """
    Finalise une session de jeu et met à jour les statistiques.

    Args:
        exe_path (str): chemin du jeu
        start_time (float): time.time() au lancement
        exit_code (int|None): code retour du process (si disponible)
        prefix_path (str|None): chemin du prefix Wine/Proton résolu pour
            cette session, si connu (permet de détecter des saves dans
            drive_c/users/.../Saved Games etc.)
        game_name (str|None): nom du jeu, pour affiner la détection dans
            le prefix et personnaliser le dialogue
        game_id (str|None): identifiant stable du jeu, utilisé comme clé
            pour se souvenir du dernier fingerprint de save proposé
        release_year (int|None): année de sortie du jeu, si connue, pour
            la variante de message "vieux jeu" ("Save your memories")
        save_backup_enabled (bool): False désactive la détection de save
            pour ce jeu (toggle par jeu dans l'éditeur de jeu)

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

    # -------------------------
    # save detection prompt
    # -------------------------
    # Never allowed to break session finalization: any failure here is
    # swallowed inside save_prompt_center.maybe_prompt() itself.
    save_prompt_center.maybe_prompt(
        exe_path,
        prefix_path=prefix_path,
        game_name=game_name,
        game_id=game_id,
        release_year=release_year,
        enabled=save_backup_enabled,
    )

    return result
