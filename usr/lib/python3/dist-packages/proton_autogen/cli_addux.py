"""Commande CLI `addux` : enregistre un programme puis ouvre l'UX dessus.

Usage : proton-autogen addux <programme.exe>

Pensée pour l'intégration aux gestionnaires de fichiers (clic droit) :
 - non interactive : utilise `add_game_ux` (aucun input(), contrairement
   à `add_game` qui demande le préfixe dans le terminal) ;
 - idempotente : `add_game_ux` réécrit toujours la config. Si le programme
   est déjà enregistré, on n'y touche donc pas (réglages conservés) ;
 - UX déjà ouverte : la commande lui délègue le travail (action D-Bus) au
   lieu d'ouvrir une seconde fenêtre ;
 - en cas d'erreur : notification bureau (pas de terminal visible).
"""
import os
import shutil
import subprocess
from pathlib import Path

VALID_EXT = {".exe", ".msi", ".bat", ".lnk"}


def _notify(title: str, body: str) -> None:
    """Notification bureau optionnelle (sans effet si notify-send est absent)."""
    exe = shutil.which("notify-send")
    if exe:
        subprocess.run([exe, "-i", "proton-autogen", title, body], check=False)


def _fail(message: str) -> int:
    print(f"addux: {message}")
    _notify("Proton-Autogen", message)
    return 1


def run_addux(raw_path: str) -> int:
    # abspath (et non resolve) : même clé de config que run() et add_game_ux()
    path = Path(os.path.abspath(os.path.expanduser(raw_path)))

    if not path.is_file():
        return _fail(f"file not found: {path}")
    if path.suffix.lower() not in VALID_EXT:
        return _fail(f"unsupported file type: {path.suffix or path.name}")

    exe_path = str(path)

    # 1) add : logique existante, version sans terminal
    from proton_autogen.loader import get_game_config_path

    config_path, _gid = get_game_config_path(exe_path)

    if os.path.exists(config_path):
        print(f"addux: already registered: {path.name}")
    else:
        from proton_autogen.editor import add_game_ux

        try:
            add_game_ux(exe_path)
        except Exception as exc:  # add_game_ux peut lever (Proton absent, E/S...)
            return _fail(f"add failed for {path.name}: {exc}")
        print(f"addux: added: {path.name}")

    # 2) UX : import différé (charge GTK 4 uniquement ici)
    from proton_autogen.ux.dashboard import start_dashboard

    start_dashboard(open_path=exe_path)
    return 0
