"""Enregistrement automatique d'un programme lancé sans configuration.

`proton-autogen game.exe` (idem `proton-autogen run game.exe`, et le lancement
depuis l'UX) se comporte ainsi :

 - le fichier de configuration du programme existe : il est utilisé tel quel,
   avec le préfixe qu'il désigne (comportement inchangé) ;
 - il n'existe pas : il est créé avant le lancement, comme le ferait
   `proton-autogen add game.exe`, mais sans aucune question (un lancement
   depuis un gestionnaire de fichiers n'a pas de terminal). Le programme
   entre ainsi dans la bibliothèque dès son premier lancement.

Le préfixe enregistré est celui que ce lancement utilise (main par défaut,
ou celui de --ps / --pa / --pc) : l'enregistrement ne change donc pas la
façon dont le programme s'exécute.
"""
import os

from proton_autogen.loader import load_game_config
from proton_autogen.utils.logger import StructuredLogger

logger = StructuredLogger("proton-autogen.auto_register")

REGISTERED_EXT = (".exe", ".msi", ".bat", ".lnk")


def ensure_game_config(exe_path: str, prefix_mode: str = "main"):
    """Retourne la configuration du programme, en la créant si elle manque.

    Retourne None quand rien n'a été créé (type de fichier non pris en charge
    ou échec) : l'appelant lance alors le programme comme avant. Ne lève
    jamais d'exception : lancer le programme passe avant l'ajout.
    """
    try:
        existing = load_game_config(exe_path)
        if existing is not None:
            return existing  # ne jamais réécrire une config existante

        if not exe_path.lower().endswith(REGISTERED_EXT) or not os.path.isfile(exe_path):
            return None

        # Imports différés : editor et core chargent beaucoup de modules.
        from proton_autogen.core import get_prefix_path
        from proton_autogen.editor import add_game_ux

        prefix_path = get_prefix_path(prefix_mode, exe_path)
        prefix = {
            "name": os.path.basename(prefix_path.rstrip(os.sep)),
            "path": prefix_path,
        }

        add_game_ux(exe_path, prefix=prefix)
        config = load_game_config(exe_path)
        if config is not None:
            logger.info(
                "Configuration created for %s (prefix: %s)", exe_path, prefix["name"]
            )
        return config

    except Exception as exc:
        logger.warning("Automatic registration skipped for %s: %s", exe_path, exc)
        return None
