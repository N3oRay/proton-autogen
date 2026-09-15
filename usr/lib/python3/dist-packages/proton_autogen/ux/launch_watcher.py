#!/usr/bin/env python3

# launch_watcher.py
"""
Détection du vrai moment où une application lancée est "prête", pour
remplacer le délai fixe historique (GLib.timeout_add_seconds(3, ...))
de la popup de lancement.

Principe :
    1. Dès que process_manager a enregistré le Popen (fait par
       core.run_process()), on connaît un PID racine + l'exe_path.
    2. On surveille l'arbre de process (le PID racine + ses enfants —
       Proton/Wine en génèrent plusieurs) jusqu'à ce qu'une fenêtre X11
       mappée appartienne à l'un d'eux : c'est le signal le plus fiable
       que l'application a fini de démarrer et affiche quelque chose.
    3. Fallback si python-xlib est absent, ou sous Wayland natif (pas
       de XWayland) : on retombe sur une heuristique d'activité CPU
       (une grosse charge initiale qui retombe = chargement terminé),
       dans le même esprit que le watchdog déjà présent dans Progress
       (progress.py : watchdog_timeout / stale_message_timeout).
    4. Timeout de sécurité dans tous les cas : certains outils (petits
       installeurs, utilitaires CLI) ne créent jamais de fenêtre et ne
       doivent pas bloquer la popup indéfiniment.

Dépendances optionnelles (comme gamemode/mangohud dans le reste du
projet) : python-xlib et psutil. Le watcher se dégrade proprement en
leur absence, jusqu'au simple timeout final.
"""

import time
from typing import Callable, Optional

from gi.repository import GLib

from proton_autogen import process_manager
from proton_autogen.utils.logger import StructuredLogger

logger = StructuredLogger("proton-autogen.ux.launch_watcher")

try:
    import psutil
except ImportError:
    psutil = None

try:
    from Xlib import display, X
    from Xlib.error import XError
    _HAS_XLIB = True
except ImportError:
    _HAS_XLIB = False


# Intervalle de poll : suffisamment bas en fréquence pour ne quasiment
# rien coûter (GLib.timeout_add ne consomme rien entre deux appels),
# suffisamment court pour rester imperceptible côté utilisateur.
DEFAULT_POLL_INTERVAL_MS = 300

# Avant que process_manager n'ait enregistré de PID (le worker thread de
# launch_game() n'a pas encore atteint run_process()), on repoll cette
# phase à part — généralement quelques dizaines de ms, jamais très long.
DEFAULT_PID_WAIT_TIMEOUT_S = 10.0

# Délai de sécurité total avant abandon (installeurs / outils sans
# fenêtre). Volontairement généreux : un GE-Proton qui décompresse un
# shader cache au premier lancement peut légitimement prendre 20-30s.
DEFAULT_MAX_WAIT_S = 40.0

# Repli CPU : après ce délai sans fenêtre détectée, on regarde si le
# process s'est calmé (fin probable du chargement).
CPU_FALLBACK_AFTER_S = 8.0
CPU_FALLBACK_THRESHOLD_PERCENT = 3.0


class LaunchReadyWatcher:
    """
    Surveille le lancement identifié par `game_id` (déjà utilisé par
    process_manager) et appelle `on_ready(elapsed_s)` dès qu'une fenêtre
    est détectée, ou `on_timeout(elapsed_s)` si rien n'arrive avant
    `max_wait_s`.

    Usage typique (dans dashboard_actions.launch_game) :

        watcher = LaunchReadyWatcher(
            game_id=game_id,
            on_ready=lambda elapsed: self._close_launch_dialog(),
            on_timeout=lambda elapsed: self._close_launch_dialog(),
        )
        watcher.start()

    Entièrement piloté par GLib.timeout_add : aucun thread supplémentaire,
    aucune boucle bloquante, coût nul entre deux polls.
    """

    def __init__(
        self,
        game_id: str,
        on_ready: Callable[[float], None],
        on_timeout: Optional[Callable[[float], None]] = None,
        on_status: Optional[Callable[[str], None]] = None,
        poll_interval_ms: int = DEFAULT_POLL_INTERVAL_MS,
        pid_wait_timeout_s: float = DEFAULT_PID_WAIT_TIMEOUT_S,
        max_wait_s: float = DEFAULT_MAX_WAIT_S,
    ):
        self.game_id = game_id
        self.on_ready = on_ready
        self.on_timeout = on_timeout
        self.on_status = on_status  # callback optionnel pour texte live
        self.poll_interval_ms = poll_interval_ms
        self.pid_wait_timeout_s = pid_wait_timeout_s
        self.max_wait_s = max_wait_s

        self._start_time = time.monotonic()
        self._source_id: Optional[int] = None
        self._root_pid: Optional[int] = None
        self._xdisplay = None
        self._finished = False

        if _HAS_XLIB:
            try:
                self._xdisplay = display.Display()
            except XError:
                self._xdisplay = None

    # -- API publique ---------------------------------------------------

    def start(self):
        if self._source_id is None:
            self._source_id = GLib.timeout_add(self.poll_interval_ms, self._poll)

    def stop(self):
        if self._source_id is not None:
            GLib.source_remove(self._source_id)
            self._source_id = None

    # -- internals --------------------------------------------------------

    def _elapsed(self) -> float:
        return time.monotonic() - self._start_time

    def _finish(self, ready: bool):
        if self._finished:
            return
        self._finished = True
        self.stop()
        elapsed = self._elapsed()
        if ready:
            logger.info(f"Launch ready detected for {self.game_id} after {elapsed:.1f}s")
            self.on_ready(elapsed)
        else:
            logger.info(f"Launch watcher timeout for {self.game_id} after {elapsed:.1f}s")
            if self.on_timeout:
                self.on_timeout(elapsed)

    def _descendant_pids(self, root_pid: int) -> set:
        pids = {root_pid}
        if psutil is None:
            return pids
        try:
            root = psutil.Process(root_pid)
            pids.update(c.pid for c in root.children(recursive=True))
        except psutil.NoSuchProcess:
            pass
        return pids

    def _has_mapped_window(self, pids: set) -> bool:
        if not self._xdisplay:
            return False
        try:
            root = self._xdisplay.screen().root
            net_client_list = self._xdisplay.intern_atom("_NET_CLIENT_LIST")
            net_wm_pid = self._xdisplay.intern_atom("_NET_WM_PID")
            prop = root.get_full_property(net_client_list, X.AnyPropertyType)
            if not prop:
                return False
            for win_id in prop.value:
                try:
                    win = self._xdisplay.create_resource_object("window", win_id)
                    pid_prop = win.get_full_property(net_wm_pid, X.AnyPropertyType)
                    if pid_prop and pid_prop.value[0] in pids:
                        return True
                except XError:
                    continue
        except XError:
            return False
        return False

    def _cpu_settled(self, pids: set) -> bool:
        """Repli utilisé quand aucune fenêtre n'est détectable (pas de
        python-xlib, Wayland natif, ou app réellement sans fenêtre)."""
        if psutil is None:
            return False
        if self._elapsed() < CPU_FALLBACK_AFTER_S:
            return False
        total = 0.0
        for pid in pids:
            try:
                total += psutil.Process(pid).cpu_percent(interval=0)
            except psutil.NoSuchProcess:
                continue
        return total < CPU_FALLBACK_THRESHOLD_PERCENT

    def _poll(self) -> bool:
        if self._elapsed() > self.max_wait_s:
            self._finish(ready=False)
            return False  # désenregistre la source GLib

        # Phase 1 : attendre que process_manager connaisse le PID
        # (le worker thread de launch_game() doit avoir atteint
        # run_process() et appelé process_manager.register()).
        if self._root_pid is None:
            info = process_manager.get_info(self.game_id)
            if info and info.get("pid"):
                self._root_pid = info["pid"]
                if self.on_status:
                    self.on_status(str(info.get("exe_path") or ""))
            elif self._elapsed() > self.pid_wait_timeout_s:
                # Le lancement a peut-être échoué avant même d'atteindre
                # run_process() (chemin invalide, etc.) — pas la peine
                # d'attendre max_wait_s dans ce cas.
                self._finish(ready=False)
                return False
            return True  # on continue le polling au prochain tick

        # Phase 2 : chercher un signal de "prêt"
        if not process_manager.is_running(self.game_id):
            # Le process a déjà disparu (crash très rapide, ou
            # application déjà fermée) : pas la peine d'attendre plus.
            self._finish(ready=True)
            return False

        pids = self._descendant_pids(self._root_pid)

        if self._has_mapped_window(pids) or self._cpu_settled(pids):
            self._finish(ready=True)
            return False

        return True
