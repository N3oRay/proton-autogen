#!/usr/bin/env python3

"""
dashboard_running
Mixin du Dashboard : suivi des jeux lancés HORS de cette fenêtre.

Problème résolu :
    Un jeu lancé depuis le CLI (`proton-autogen game.exe`) tourne dans un
    autre processus que l'UX. Le Dashboard ne connaissait que les jeux
    lancés par launch_game() (self._running_games) : le jeu CLI n'apparaissait
    ni dans le bouton « Stop », ni dans le sélecteur multi-jeux.

Fonctionnement :
    - toutes les RUNNING_POLL_SECONDS secondes, un thread de travail lit le
      registre partagé (process_manager.list_external()) ; le travail est
      fait hors du thread GTK car la vérification peut lancer pgrep
    - le résultat revient sur le thread principal via GLib.idle_add
    - les jeux externes sont ajoutés à self._running_games, donc réutilisés
      tels quels par le bouton Stop, le sélecteur et stop_running_game()
      (qui appelle process_manager.stop(), désormais capable d'arrêter un
      jeu externe)
    - self._external_games mémorise les identifiants ajoutés ici, pour ne
      jamais retirer un jeu lancé par launch_game()

Câblage minimal dans dashboard.py :
    - importer DashboardRunningMixin et l'ajouter aux classes de base
    - appeler self._init_running_watch() à la fin de __init__
"""

import os
import threading

from gi.repository import GLib

from proton_autogen import process_manager
from proton_autogen.i18n import tr
from proton_autogen.utils.logger import StructuredLogger

logger = StructuredLogger("proton-autogen.dashboard_running")


class DashboardRunningMixin:

    RUNNING_POLL_SECONDS = 3

    # -------------------------
    # Cycle de vie
    # -------------------------
    def _init_running_watch(self):
        """À appeler une fois, après build_ui()."""
        self._external_games = {}          # game_id -> nom affiché
        self._running_watch_busy = False   # un seul scan à la fois
        self._running_watch_source = GLib.timeout_add_seconds(
            self.RUNNING_POLL_SECONDS,
            self._running_watch_tick,
        )
        # Arrête le minuteur à la fermeture de la fenêtre. Retourne False :
        # ne jamais empêcher la fermeture.
        self.connect("close-request", self._stop_running_watch)

    def _stop_running_watch(self, *_):
        source = getattr(self, "_running_watch_source", None)
        if source:
            GLib.source_remove(source)
            self._running_watch_source = None
        return False

    # -------------------------
    # Scan périodique
    # -------------------------
    def _running_watch_tick(self):
        """Exécuté sur le thread GTK (GLib.timeout_add) : ne bloque jamais."""
        if self._running_watch_busy:
            return True   # le scan précédent n'est pas fini, on réessaie

        self._running_watch_busy = True
        threading.Thread(target=self._running_watch_scan, daemon=True).start()
        return True       # garde le minuteur actif

    def _running_watch_scan(self):
        """Thread de travail : lecture du registre (peut lancer pgrep)."""
        try:
            external = process_manager.list_external()
        except Exception as e:
            logger.warning(f"external game scan failed: {e}")
            external = None

        GLib.idle_add(self._apply_external_games, external)

    # -------------------------
    # Application du résultat (thread GTK)
    # -------------------------
    def _apply_external_games(self, external):
        self._running_watch_busy = False

        if external is None:   # échec du scan : on ne change rien
            return False

        if not hasattr(self, "_running_games"):
            self._running_games = {}   # game_id -> name

        running = self._running_games
        known = self._external_games
        added = []
        changed = False

        # Nouveaux jeux externes
        for game_id, info in external.items():
            if game_id in running and game_id not in known:
                continue   # lancé par cette fenêtre : launch_game() s'en occupe
            if game_id in known:
                continue

            name = info.get("name") or self._external_game_name(info, game_id)
            known[game_id] = name
            running[game_id] = name
            added.append(name)
            changed = True

        # Jeux externes terminés
        for game_id in [g for g in known if g not in external]:
            known.pop(game_id, None)
            running.pop(game_id, None)
            changed = True

        if changed:
            only_name = None
            if len(running) == 1:
                only_name = next(iter(running.values()))
            self._update_stop_button_state(bool(running), only_name)

        if added:
            self.status.set_text(tr("running_game", name=added[-1]))

        return False   # GLib.idle_add : ne pas se répéter

    @staticmethod
    def _external_game_name(info, game_id):
        exe_path = info.get("exe_path")
        if exe_path:
            return os.path.splitext(os.path.basename(exe_path))[0]
        return game_id[:8]
