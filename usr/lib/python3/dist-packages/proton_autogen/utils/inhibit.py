#!/usr/bin/env python3
# inhibit.py
"""
Verrou anti-veille pendant l'exécution d'un jeu.

Empêche l'écran de s'éteindre / l'ordinateur de se mettre en veille /
le capot de suspendre la session pendant qu'un jeu tourne — ce que
Steam et les autres launchers font déjà en interne.

Principe : le jeu est lancé comme ENFANT DIRECT de `systemd-inhibit`.
Ce dernier détient le verrou tant que ce processus tourne et le
libère automatiquement à sa sortie, normale ou tuée (SIGTERM/SIGKILL
sur le groupe de processus, cf. process_manager). Aucune gestion de
cycle de vie séparée n'est donc nécessaire côté proton-autogen : pas
d'acquire()/release() à appeler, pas d'état à nettoyer en cas de
crash — la durée de vie du verrou est structurellement identique à
celle du processus qu'il protège.

Trois modes (réglage global, Réglages > Comportement) :
  - "never"    : jamais de verrou.
  - "always"   : verrou pour tous les jeux (réglage par défaut).
  - "per_game" : verrou uniquement si activé sur le profil du jeu
                 (case à cocher dans l'éditeur, comme MangoHud/GameMode).
"""

import shutil
import configparser
from pathlib import Path

# Même fichier que les autres réglages de comportement UX
# (remember_window_size, mini_mode...) — voir themes.py.
CONFIG_PATH = Path.home() / ".config" / "proton-autogen" / "proton-autogen-ux.conf"

INHIBIT_MODES = ("never", "always", "per_game")
DEFAULT_INHIBIT_MODE = "always"

# --what=idle:sleep:handle-lid-switch : couvre l'extinction d'écran par
# inactivité, la mise en veille système, ET la fermeture du capot —
# nécessaire pour le jeu à la manette où aucune activité clavier/souris
# ne remonte à KDE Plasma pour repousser l'inhibiteur d'idle par défaut.
WHAT = "idle:sleep:handle-lid-switch"
WHO = "proton-autogen"


def has_systemd_inhibit() -> bool:
    """True si systemd-inhibit est disponible sur le système (absent
    sur les systèmes non-systemd : autre init, certaines distros
    minimalistes)."""
    return shutil.which("systemd-inhibit") is not None


# -------------------------------------------------------------------
# CONFIG (mode global)
# -------------------------------------------------------------------

def load_inhibit_mode() -> str:
    """Lit le mode global. Retombe sur DEFAULT_INHIBIT_MODE si absent,
    illisible, ou si le fichier contient une valeur invalide (ex.
    édition manuelle malheureuse)."""
    cfg = configparser.ConfigParser()

    if not CONFIG_PATH.exists():
        return DEFAULT_INHIBIT_MODE

    try:
        cfg.read(CONFIG_PATH)
        value = cfg.get(
            "behavior", "inhibit_sleep_mode", fallback=DEFAULT_INHIBIT_MODE
        ).strip()
    except Exception:
        return DEFAULT_INHIBIT_MODE

    return value if value in INHIBIT_MODES else DEFAULT_INHIBIT_MODE


def save_inhibit_mode(mode: str):
    if mode not in INHIBIT_MODES:
        return

    cfg = configparser.ConfigParser()
    if CONFIG_PATH.exists():
        try:
            cfg.read(CONFIG_PATH)
        except Exception:
            pass

    if "behavior" not in cfg:
        cfg["behavior"] = {}

    cfg["behavior"]["inhibit_sleep_mode"] = mode

    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        cfg.write(f)


# -------------------------------------------------------------------
# DECISION + ENROBAGE DE LA COMMANDE
# -------------------------------------------------------------------

def should_inhibit(features: dict | None) -> bool:
    """Décide si le verrou s'applique à CE lancement, en croisant le
    mode global et l'éventuelle surcharge par jeu."""
    mode = load_inhibit_mode()

    if mode == "never":
        return False

    if mode == "always":
        return True

    # mode == "per_game" : uniquement si explicitement coché sur ce
    # profil (comme les toggles MangoHud/GameMode/GameScope).
    features = features or {}
    return bool(features.get("inhibit_sleep", False))


def wrap_command_with_inhibit(cmd: list, features: dict | None, game_name: str = "") -> list:
    """Préfixe `cmd` par systemd-inhibit si applicable.

    Retourne `cmd` INCHANGÉ si le verrou est désactivé (mode "never",
    ou "per_game" sans le toggle du jeu) ou si systemd-inhibit est
    indisponible — échec silencieux volontaire : l'absence du verrou
    ne doit jamais empêcher un jeu de se lancer.
    """
    if not should_inhibit(features):
        return cmd

    if not has_systemd_inhibit():
        return cmd

    why = f"Playing {game_name}" if game_name else "proton-autogen game running"

    return [
        "systemd-inhibit",
        f"--what={WHAT}",
        f"--who={WHO}",
        f"--why={why}",
        "--mode=block",
    ] + cmd
