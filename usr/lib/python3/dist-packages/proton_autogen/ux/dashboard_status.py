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
"""

from datetime import datetime

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GObject

# Nombre maximum de messages conservés en mémoire. Au-delà, les plus
# anciens sont supprimés silencieusement (pas de fuite mémoire sur une
# session longue avec beaucoup de lancements/arrêts de jeux).
MAX_HISTORY = 200


class StatusEntry:
    """Un message de statut horodaté."""

    __slots__ = ("text", "level", "timestamp")

    def __init__(self, text: str, level: str = "info"):
        self.text = text
        self.level = level
        self.timestamp = datetime.now()


class StatusLabel(Gtk.Label):
    """Gtk.Label à mémoire : `set_text()` se comporte comme d'habitude
    pour tout le code existant, mais chaque texte non vide est en plus
    ajouté à un historique interne.

    Émet le signal "history-changed" à chaque modification de
    l'historique (ajout ou vidage), pour que l'UI puisse se
    rafraîchir sans polling.
    """

    __gsignals__ = {
        "history-changed": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._history: list[StatusEntry] = []

    # -------------------------
    # API standard Gtk.Label (compatible avec tout le code existant)
    # -------------------------
    def set_text(self, text, level: str = "info"):
        super().set_text(text)

        if text:
            self._history.append(StatusEntry(text, level))
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
