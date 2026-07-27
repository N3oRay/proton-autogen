"""proton_autogen.progress

Fournit une classe utilitaire pour reporter la progression d'une tâche
longue (ex. lancement d'un jeu via Proton) à un callback, avec un spinner
optionnel pour les phases sans progression mesurable.
"""

import threading
import time
from typing import Callable, Optional


class Progress:
    """Reporte la progression d'une opération longue à un callback.

    Thread-safe : `update()` peut être appelé depuis n'importe quel thread,
    y compris pendant qu'un spinner tourne en arrière-plan.

    Note importante (UI) :
        Le callback est invoqué depuis le thread appelant de `update()`,
        y compris le thread interne du spinner. Si le callback touche une
        UI (GTK, Qt...), l'appelant DOIT relayer l'appel vers le thread
        principal (ex. `GLib.idle_add`) — `Progress` ne le fait pas lui-même.
    """

    _spinner = ("⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏")

    def __init__(self, callback: Optional[Callable[[int, str], None]] = None):
        self.callback = callback
        self._lock = threading.Lock()
        self.current = {"percent": 0, "message": ""}

        self._running = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._spin = 0

    def update(self, percent: int, message: str) -> None:
        """Met à jour l'état de progression et notifie le callback.

        Args:
            percent: valeur clampée automatiquement entre 0 et 100.
            message: texte de statut associé.
        """
        percent = max(0, min(100, percent))

        with self._lock:
            self.current["percent"] = percent
            self.current["message"] = message

        if self.callback:
            self.callback(percent, message)

    def get_current(self) -> dict:
        """Retourne une copie thread-safe de l'état courant."""
        with self._lock:
            return dict(self.current)

    def start_spinner(
        self,
        percent: int = 90,
        message: str = "Launching",
        interval: float = 0.1,
    ) -> None:
        """Démarre un spinner animé en arrière-plan.

        Sans effet si un spinner est déjà en cours.
        """
        if self._running.is_set():
            return

        self._running.set()

        def worker():
            while self._running.is_set():
                frame = self._spinner[self._spin]
                self._spin = (self._spin + 1) % len(self._spinner)
                self.update(percent, f"{frame} {message}")
                time.sleep(interval)

        self._thread = threading.Thread(target=worker, daemon=True)
        self._thread.start()

    def stop_spinner(self, timeout: float = 1.0) -> None:
        """Arrête le spinner et attend la fin du thread (best-effort)."""
        self._running.clear()

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=timeout)

            if self._thread.is_alive():
                # Le thread n'a pas pu se terminer dans le délai imparti.
                # Il reste daemon donc ne bloquera pas l'arrêt du process,
                # mais on le signale pour éviter un échec silencieux.
                import logging
                logging.getLogger(__name__).warning(
                    "Progress spinner thread did not stop within %.1fs", timeout
                )

        self._thread = None
