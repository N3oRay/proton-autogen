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
import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GObject

# Nombre maximum de messages conservés en mémoire. Au-delà, les plus
# anciens sont supprimés silencieusement (pas de fuite mémoire sur une
# session longue avec beaucoup de lancements/arrêts de jeux).
MAX_HISTORY = 200

# La logique de nettoyage (sans GTK) vit désormais dans status_text.py.
# Ces noms restent importables d'ici : aucun import existant ne casse.
from proton_autogen.status_text import (  # noqa: F401
    MAX_DISPLAY_LINES,
    strip_ansi,
    clean_message,
    cap_lines,
    _ANSI_RE,
    _ERROR_HINT_RE,
    _STDERR_PREFIX,
    _strip_stderr_prefix,
)


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
        Délègue à clean_message() (fonction pure, module-level) —
        conservé comme méthode ici uniquement pour compatibilité avec
        le code existant qui appelle StatusLabel._format_message().
        """
        return clean_message(text, level)

    @staticmethod
    def _cap_lines(text: str, max_lines: int = MAX_DISPLAY_LINES) -> str:
        """Délègue à cap_lines() (fonction pure, module-level)."""
        return cap_lines(text, max_lines)

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
