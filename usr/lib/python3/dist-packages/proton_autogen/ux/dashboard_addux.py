"""Ouverture de l'éditeur d'un jeu à la demande de `proton-autogen addux`.

Deux morceaux, volontairement séparés de dashboard.py :
 - DashboardAddUxMixin : côté fenêtre (attend la liste des jeux, puis ouvre
   l'éditeur du jeu demandé) ;
 - register_addux_action : côté application, action `app.addux` (paramètre :
   chemin du programme). C'est ce que la commande CLI appelle par D-Bus quand
   l'UX tourne déjà, afin de ne pas ouvrir une seconde fenêtre.
"""
import os

from gi.repository import Gio, GLib

from proton_autogen.i18n import tr

ACTION_NAME = "addux"

# Nombre de rechargements de la liste tolérés avant d'abandonner : un
# rechargement déjà en cours au moment de la demande peut se terminer sans
# connaître le jeu qui vient d'être ajouté.
_MAX_ATTEMPTS = 2


class DashboardAddUxMixin:
    # Ouvre l'éditeur du jeu après `addux`. Mettre False pour n'afficher que
    # le tableau de bord (le jeu apparaît alors simplement dans la liste).
    ADDUX_OPEN_EDITOR = True

    def addux_open(self, exe_path, refresh=True):
        """Demande l'ouverture du jeu `exe_path` (déjà enregistré par la CLI).

        refresh=False : à la création de la fenêtre, refresh_games() a déjà
        été lancé par __init__, inutile de le doubler.
        """
        self._addux_pending = os.path.abspath(exe_path)
        self._addux_attempts = 0
        self.present()
        if refresh:
            self.refresh_games()

    def _addux_after_load(self):
        """Appelé à la fin de _on_games_loaded : traite la demande en attente."""
        pending = getattr(self, "_addux_pending", None)
        if not pending:
            return

        game = next(
            (
                g for g in self.games
                if os.path.abspath(g.get("path") or "") == pending
            ),
            None,
        )

        if game is None:
            self._addux_attempts = getattr(self, "_addux_attempts", 0) + 1
            if self._addux_attempts >= _MAX_ATTEMPTS:
                self._addux_pending = None
                self.toast.error(os.path.basename(pending))
            return

        self._addux_pending = None
        if self.ADDUX_OPEN_EDITOR and hasattr(self, "edit_game"):
            self.edit_game(game)
        else:
            self.status.set_text(tr("apps_count").format(count=len(self.games)))


def register_addux_action(app):
    """Enregistre `app.addux(s)` ; à appeler depuis _create_actions."""
    action = Gio.SimpleAction.new(ACTION_NAME, GLib.VariantType.new("s"))

    def on_addux(_action, param):
        path = param.get_string()
        # get_active_window() peut renvoyer l'éditeur : on cherche le tableau
        # de bord lui-même.
        for win in app.get_windows():
            if hasattr(win, "addux_open"):
                win.addux_open(path)
                return

    action.connect("activate", on_addux)
    app.add_action(action)
