#!/usr/bin/env python3
# status_text.py
"""
Nettoyage des messages de statut — SANS GTK.

Fonctions pures (texte -> texte) qui préparent les lignes stdout/stderr des
jeux (gamescope, vulkan, wine...) avant affichage : suppression des codes
ANSI, détection du niveau « error », retrait du préfixe « stderr: » et
plafonnement du nombre de lignes.

Extrait tel quel de ux/dashboard_status.py. Ce module reste importable d'ici
sous les mêmes noms (strip_ansi, clean_message, cap_lines, MAX_DISPLAY_LINES)
pour ne casser aucun import existant ; la barre de statut (StatusLabel) et la
popup de lancement (ux/dialogs.py) l'utilisent toujours.
"""

import re

from proton_autogen.i18n import tr

# Nombre maximum de lignes affichées directement dans la barre de
# statut (le reste n'est visible que dans le panneau d'historique).
MAX_DISPLAY_LINES = 6


# ------------------------------------------------------------------------------------
# NETTOYAGE COULEUR / CONTRÔLE (pure, sans GTK)
# ------------------------------------------------------------------------------------

# Un seul regex combiné (OSC + CSI + autres caractères de contrôle) au
# lieu de 3 regex distincts : une seule passe sur le texte et une seule
# allocation de chaîne, au lieu de 3 passes chaînées.
#   - OSC : "\x1b]0;titre\x07"          (titre de fenêtre, hyperliens)
#   - CSI : "\x1b[38;5;208m", "\x1b[0m"  (couleurs, curseur)
#   - autres caractères de contrôle non imprimables (hors \n / \t)
_ANSI_RE = re.compile(
    r"\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)"
    r"|\x1b\[[0-9;?]*[a-zA-Z]"
    r"|[\x00-\x08\x0b\x0c\x0e-\x1f]"
)


def strip_ansi(text: str) -> str:
    """Supprime en une seule passe les séquences ANSI (couleur, curseur,
    OSC) et les caractères de contrôle non imprimables d'un texte."""
    return _ANSI_RE.sub("", text)


# Détection du niveau "error" : un seul regex combiné plutôt qu'une
# boucle sur 8 regex séparés. Motifs redondants supprimés :
#   - "error\s*:" est un cas particulier de "error\b" (\b matche déjà
#     avant ":") -> un seul suffit.
#   - "traceback\s*\(most recent call last\)" est un cas particulier de
#     "traceback\s*\(" -> un seul suffit.
# Pas de re.MULTILINE : comme avant, seul le tout début du message est
# vérifié (un message qui commence par une trace d'erreur), pas chaque
# ligne individuellement.
_ERROR_HINT_RE = re.compile(
    r"^\s*(?:stderr\s*:|error\b|fatal\b|failed\b|failure\b|traceback\s*\()",
    re.IGNORECASE,
)

# Préfixe "stderr:" en tête de message : simple comparaison de chaîne
# (moins coûteux qu'un regex pour un test aussi ciblé, pas de moteur
# regex à invoquer).
_STDERR_PREFIX = "stderr"


def _strip_stderr_prefix(text: str) -> str:
    stripped = text.lstrip()
    lower = stripped.lower()
    if lower.startswith(_STDERR_PREFIX):
        rest = stripped[len(_STDERR_PREFIX):].lstrip()
        if rest.startswith(":"):
            return rest[1:].lstrip()
    return text


# ------------------------------------------------------------------------------------
# NETTOYAGE COMPLET (pure, sans GTK) — réutilisable par tout appelant
# ------------------------------------------------------------------------------------
#
# Extrait de StatusLabel._format_message()/_cap_lines() pour être
# réutilisable ailleurs sans dépendre du widget StatusLabel lui-même.
# Utilisé par StatusLabel.set_text() (barre de statut du bas) ET par
# proton_autogen.ux.dialogs.update_launch_dialog_info() (popup de
# lancement) : les deux affichent des messages issus des mêmes lignes
# stdout/stderr de core.run_process(), donc les mêmes risques de codes
# ANSI bruts et de préfixes "stderr:" s'appliquent aux deux — pas de
# raison d'avoir deux implémentations qui pourraient diverger.

def clean_message(text, level: str = "info"):
    """
    Nettoie un message de statut brut : suppression ANSI, normalisation
    des fins de ligne, détection de niveau d'erreur, suppression du
    préfixe "stderr:". Ne fait AUCUN plafonnement de lignes (cf.
    cap_lines() séparément — les appelants n'ont pas tous la même
    largeur/hauteur disponible).

    Retourne (texte_nettoye_complet, niveau).
    """

    if text is None:
        return "", level

    text = str(text)

    if not text.strip():
        return "", level

    # Supprime couleurs / séquences de contrôle AVANT toute autre
    # étape : sinon les codes ANSI polluent la détection de motifs
    # et le split par lignes. Une seule passe regex (voir strip_ansi).
    text = strip_ansi(text)

    # Normalisation des fins de lignes.
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Nettoyage des espaces en fin de ligne + suppression des lignes
    # vides au début et à la fin.
    lines = [line.rstrip() for line in text.splitlines()]

    while lines and not lines[0]:
        lines.pop(0)

    while lines and not lines[-1]:
        lines.pop()

    text = "\n".join(lines)

    # Détection d'erreur : un seul regex combiné (voir _ERROR_HINT_RE).
    if level == "info" and _ERROR_HINT_RE.match(text):
        level = "error"

    # Suppression du préfixe "stderr:" : comparaison de chaîne, pas
    # de regex (voir _strip_stderr_prefix).
    text = _strip_stderr_prefix(text)

    return text, level


def cap_lines(text: str, max_lines: int = MAX_DISPLAY_LINES) -> str:
    """Plafonne `text` à `max_lines` lignes ; ajoute une note indiquant
    le nombre de lignes masquées. `max_lines` est paramétrable car tous
    les appelants n'ont pas le même espace disponible (la popup de
    lancement, plus petite et de hauteur fixe, en accepte beaucoup
    moins que la barre de statut du bas)."""
    lines = text.split("\n")

    if len(lines) <= max_lines:
        return text

    hidden = len(lines) - max_lines
    capped = lines[:max_lines]
    capped.append(tr("status_more_lines").format(count=hidden))
    return "\n".join(capped)
