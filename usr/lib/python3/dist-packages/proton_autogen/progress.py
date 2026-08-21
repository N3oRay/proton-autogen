"""proton_autogen.progress

Fournit une classe utilitaire pour reporter la progression d'une tâche
longue (ex. lancement d'un jeu via Proton) à un callback, avec un spinner
optionnel pour les phases sans progression mesurable.
"""

import logging
import threading
import time
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class Progress:
    """Reporte la progression d'une opération longue à un callback.

    Thread-safe : `update()` peut être appelé depuis n'importe quel thread,
    y compris pendant qu'un spinner tourne en arrière-plan.

    Le spinner s'arrête automatiquement dans deux cas :
      1. Aucune mise à jour externe reçue pendant `watchdog_timeout`
         secondes -> on considère le traitement bloqué (log warning).
      2. Des mises à jour externes arrivent, mais le message reste
         identique pendant `stale_message_timeout` secondes -> on
         considère que le traitement se déroule normalement mais n'a
         plus besoin d'affichage animé (log info, arrêt silencieux,
         pas d'alerte).

    Note importante (UI) :
        Le callback est invoqué depuis le thread appelant de `update()`,
        y compris le thread interne du spinner. Si le callback touche une
        UI (GTK, Qt...), l'appelant DOIT relayer l'appel vers le thread
        principal (ex. `GLib.idle_add`) — `Progress` ne le fait pas lui-même.

    Note importante (performance) :
        Le callback est aussi invoqué à chaque frame du spinner (par
        défaut 10x/seconde). Il reçoit maintenant un troisième argument,
        `is_spinner_tick`, qui vaut True pour ces frames internes et False
        pour les appels externes réels. Un callback qui répercute chaque
        update sur un widget "lourd" (ex. reconstruction d'une liste
        d'historique) DOIT utiliser ce flag pour éviter ce traitement
        coûteux sur les simples frames d'animation — sans quoi un
        spinner de 10-40 secondes peut suffire à saturer un cœur CPU.
        Rétrocompatible : les callbacks à 2 arguments existants
        continuent de fonctionner sans modification.
    """

    _spinner = ("⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏")

    def __init__(self, callback: Optional[Callable[..., None]] = None):
        self.callback = callback
        self._lock = threading.Lock()
        self.current = {"percent": 0, "message": ""}

        self._running = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._spin = 0

        now = time.monotonic()
        self._last_activity = now       # dernier update() externe reçu
        self._last_message = ""         # dernier message externe reçu
        self._last_message_change = now # dernière fois que le message a changé

    def update(self, percent: int, message: str, _internal: bool = False) -> None:
        """Met à jour l'état de progression et notifie le callback.

        Args:
            percent: valeur clampée automatiquement entre 0 et 100.
            message: texte de statut associé.
            _internal: usage réservé au spinner lui-même — ne pas utiliser
                depuis du code appelant (n'actualise pas les watchdogs).
                Répercuté au callback comme `is_spinner_tick`.
        """
        percent = max(0, min(100, percent))

        with self._lock:
            self.current["percent"] = percent
            self.current["message"] = message

            if not _internal:
                now = time.monotonic()
                self._last_activity = now

                if message != self._last_message:
                    self._last_message = message
                    self._last_message_change = now

        if self.callback:
            try:
                # Signature étendue : (percent, message, is_spinner_tick)
                self.callback(percent, message, _internal)
            except TypeError:
                # Rétrocompatibilité avec un callback à 2 arguments
                # (percent, message) qui ne connaît pas encore le flag.
                self.callback(percent, message)

    def get_current(self) -> dict:
        """Retourne une copie thread-safe de l'état courant."""
        with self._lock:
            return dict(self.current)

    def start_spinner(
        self,
        percent: int = 90,
        message: str = "Launching",
        interval: float = 2.0,
        watchdog_timeout: Optional[float] = 30.0,
        stale_message_timeout: Optional[float] = 10.0,
    ) -> None:
        """Démarre un spinner animé en arrière-plan.

        Sans effet si un spinner est déjà en cours (vérification et
        activation protégées par verrou pour éviter tout démarrage
        concurrent en cas d'appels simultanés).

        Args:
            watchdog_timeout: délai en secondes sans aucun update() externe
                au-delà duquel le spinner s'arrête automatiquement
                (considéré comme un blocage). None désactive ce watchdog.
            stale_message_timeout: délai en secondes pendant lequel le
                message externe peut rester identique avant d'arrêter le
                spinner (considéré comme un traitement normal qui n'a
                plus besoin d'affichage animé). None désactive ce check.
        """
        with self._lock:
            if self._running.is_set():
                return

            self._running.set()
            now = time.monotonic()
            self._last_activity = now
            self._last_message_change = now

        def worker():
            stop_reason = None

            while self._running.is_set():
                with self._lock:
                    now = time.monotonic()
                    inactivity_elapsed = now - self._last_activity
                    stale_elapsed = now - self._last_message_change

                if watchdog_timeout is not None and inactivity_elapsed >= watchdog_timeout:
                    stop_reason = "stalled"
                    self._running.clear()
                    break

                if stale_message_timeout is not None and stale_elapsed >= stale_message_timeout:
                    stop_reason = "stale"
                    self._running.clear()
                    break

                frame = self._spinner[self._spin]
                self._spin = (self._spin + 1) % len(self._spinner)
                self.update(percent, f"{frame} {message}", _internal=True)
                time.sleep(interval)

            # -----------------------------------------------------
            # Nettoyage final : on notifie l'appelant avec un état
            # propre (sans glyphe figé), quelle que soit la raison
            # de l'arrêt (externe via stop_spinner, ou automatique
            # via l'un des deux watchdogs).
            # -----------------------------------------------------
            if stop_reason == "stalled":
                logger.warning(
                    "Progress spinner auto-stopped: no update for %.0fs (possible stall)",
                    watchdog_timeout,
                )
                self.update(percent, f"{message} (stalled)", _internal=True)

            elif stop_reason == "stale":
                logger.info(
                    "Progress spinner auto-stopped: message unchanged for %.0fs "
                    "(assumed normal, disabling animation)",
                    stale_message_timeout,
                )
                self.update(percent, message, _internal=True)

            self._thread = None

        self._thread = threading.Thread(target=worker, daemon=True)
        self._thread.start()

    def stop_spinner(self, timeout: float = 1.0) -> None:
        """Arrête le spinner et attend la fin du thread (best-effort)."""
        self._running.clear()

        thread = self._thread  # capture unique, évite la relecture concurrente

        if thread and thread.is_alive():
            thread.join(timeout=timeout)

            if thread.is_alive():
                logger.warning(
                    "Progress spinner thread did not stop within %.1fs", timeout
                )

        self._thread = None
