#!/usr/bin/env python3

# dashboard_status.py
"""
Historique des messages de la barre de statut.

Le Dashboard utilise déjà `self.status.set_text(...)` un peu partout
(dashboard_actions.py, dashboard_mangohud.py, dashboard_creatshortcut.py,
dashboard.py...). Plutôt que de modifier tous ces appels, StatusLabel
surcharge Gtk.Label.set_text() : chaque appel existant continue de
fonctionner à l'identique, mais alimente en plus un historique borné,
consultable via le panneau déroulant construit dans dashboard_ui.py
(_build_status_bar / _build_status_history_panel).

Deux nettoyages sont appliqués avant affichage :

  1. Suppression des séquences ANSI (couleurs, curseur, titres de
     fenêtre OSC...) et des caractères de contrôle non imprimables.
     Sans ça, la sortie colorée de gamescope/vulkan/wine s'affiche
     comme du texte brut cassé dans le Gtk.Label (ex: "^[[38;5;208m").
  2. Plafonnement du nombre de lignes affichées DANS LA BARRE : un
     dump de démarrage gamescope fait facilement 25+ lignes, ce qui
     ferait exploser la hauteur de la barre de statut à chaque
     lancement. Le texte complet nettoyé reste disponible dans
     l'historique (entry.full_text), la barre n'affiche qu'un extrait
     avec une note "(+N lignes, voir l'historique)".
"""

from datetime import datetime
import re
import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GObject

from proton_autogen.i18n import tr

# Nombre maximum de messages conservés en mémoire. Au-delà, les plus
# anciens sont supprimés silencieusement (pas de fuite mémoire sur une
# session longue avec beaucoup de lancements/arrêts de jeux).
MAX_HISTORY = 200

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


class StatusEntry:
    """Un message de statut horodaté.

    `text` est la version affichée dans la liste (plafonnée à
    MAX_DISPLAY_LINES). `full_text` est le texte nettoyé complet ;
    identique à `text` quand le message n'a pas été tronqué.
    """

    __slots__ = ("text", "level", "timestamp", "full_text")

    def __init__(self, text: str, level: str = "info", full_text: str = None):
        self.text = text
        self.level = level
        self.timestamp = datetime.now()
        self.full_text = full_text if full_text is not None else text

    @property
    def has_more(self) -> bool:
        return self.full_text != self.text


class StatusLabel(Gtk.Label):
    """Gtk.Label à mémoire : `set_text()` se comporte comme d'habitude
    pour tout le code existant, mais chaque texte non vide est nettoyé
    (ANSI, plafonnement) et ajouté à un historique interne.

    Émet le signal "history-changed" à chaque modification de
    l'historique (ajout ou vidage), pour que l'UI puisse se
    rafraîchir sans polling.
    """

    __gsignals__ = {
        "history-changed": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._history: list = []

        # Quelques réglages utiles pour les messages longs.
        self.set_wrap(True)
        self.set_wrap_mode(2)  # Pango.WrapMode.WORD_CHAR
        self.set_xalign(0.0)

    # ------------------------------------------------------------------
    # Formatage
    # ------------------------------------------------------------------

    @staticmethod
    def _format_message(text, level: str):
        """
        Nettoie un message et détermine éventuellement son niveau.

        Retourne :
            (texte_nettoye_complet, niveau)
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

    @staticmethod
    def _cap_lines(text: str, max_lines: int = MAX_DISPLAY_LINES) -> str:
        """Plafonne le texte à max_lines lignes pour l'affichage dans
        la barre elle-même ; ajoute une note indiquant qu'il faut ouvrir
        l'historique pour voir la suite."""
        lines = text.split("\n")

        if len(lines) <= max_lines:
            return text

        hidden = len(lines) - max_lines
        capped = lines[:max_lines]
        capped.append(tr("status_more_lines").format(count=hidden))
        return "\n".join(capped)

    # ------------------------------------------------------------------
    # API Gtk.Label
    # ------------------------------------------------------------------

    def set_text(self, text, level: str = "info", record_history: bool = True):
        """
        Compatible avec Gtk.Label.set_text().

        Exemple :

            self.status.set_text("Jeu lancé")

        ou :

            self.status.set_text(stderr, level="error")

        record_history : mettre à False pour les mises à jour éphémères
            à haute fréquence (ex. frames d'un spinner d'attente, ~10x/s
            pendant tout un lancement de jeu). Dans ce cas, seul le texte
            affiché est mis à jour : pas de nettoyage ANSI, pas d'entrée
            d'historique, pas de signal "history-changed" — donc pas de
            reconstruction du panneau déroulant à chaque frame. Sans ce
            court-circuit, un spinner à 10 Hz reconstruit l'intégralité
            du Gtk.ListBox de l'historique (jusqu'à 200 lignes) dix fois
            par seconde, ce qui suffit à expliquer une surconsommation
            CPU pendant tout lancement de jeu.
        """

        if not record_history:
            super().set_text(str(text) if text is not None else "")
            return

        full_text, level = self._format_message(text, level)
        display_text = self._cap_lines(full_text)

        super().set_text(display_text)

        if full_text:
            self._history.append(
                StatusEntry(display_text, level, full_text=full_text)
            )

            if len(self._history) > MAX_HISTORY:
                overflow = len(self._history) - MAX_HISTORY
                del self._history[:overflow]

        self.emit("history-changed")

    # -------------------------
    # API historique
    # -------------------------
    def get_history(self):
        """Retourne les entrées, la plus récente en premier."""
        return list(reversed(self._history))

    def clear_history(self):
        self._history.clear()
        self.emit("history-changed")

    def has_history(self) -> bool:
        return bool(self._history)
