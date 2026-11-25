#!/usr/bin/env python3

# dashboard_steam.py
"""
Entrée de menu « Configuration Steam ».

Fenêtre qui affiche l'état de l'outil de compatibilité Steam « Proton-Autogen »
et permet de l'installer / le réinstaller / le désinstaller (mêmes fonctions que
`proton-autogen install-steam` et `uninstall-steam`, voir steam_compat.py).

  - Steam introuvable      -> message, boutons désactivés
  - non installé           -> bouton « Installer dans Steam »
  - installé               -> « Réinstaller / réparer » et « Désinstaller »
  - installé mais invalide -> problèmes listés, « Réinstaller / réparer » conseillé

Les remplacements et la désinstallation demandent toujours une confirmation.

Trois morceaux, sur le modèle de dashboard_proton_update.py :
 - status_view : logique pure (sans fenêtre) ;
 - DashboardSteamMixin : côté fenêtre (Dashboard) ;
 - register_steam_action : côté application, action `app.steam_config`
   (à appeler depuis _create_actions).
"""

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gio, Gtk

from proton_autogen import steam_compat
from proton_autogen.i18n import tr
from proton_autogen.ux.dialogs import show_confirm
from proton_autogen.utils.logger import StructuredLogger

logger = StructuredLogger("proton-autogen.ux.dashboard_steam")

ACTION_NAME = "steam_config"
STATUS_CLASSES = ("success", "warning", "error")


# ------------------------------------------------------------------------------------
# LOGIQUE PURE (sans GTK, testable indépendamment)
# ------------------------------------------------------------------------------------

def status_view(status):
    """(classe CSS, message traduit) pour un steam_compat.SteamStatus."""
    if not status.steam_found:
        return "error", tr("steam_status_no_steam")
    if not status.installed:
        return "warning", tr("steam_status_not_installed")
    if status.problems:
        details = "\n".join(f"- {p}" for p in status.problems)
        return "error", f"{tr('steam_status_invalid')}\n{details}"
    return "success", tr("steam_status_installed")


# ------------------------------------------------------------------------------------
# PARTIE GTK
# ------------------------------------------------------------------------------------

class DashboardSteamMixin:
    """Fenêtre « Configuration Steam ».

    Doit être mixé avec Dashboard (utilise self.status s'il existe)."""

    def show_steam_window(self):
        window = Gtk.Window(
            title=tr("steam_title"),
            transient_for=self,
            modal=True,
            default_width=480,
            resizable=False,
        )
        window.add_css_class("steam-config-window")

        root = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=14,
            margin_top=24,
            margin_bottom=24,
            margin_start=24,
            margin_end=24,
        )

        root.append(Gtk.Label(
            label=tr("steam_intro"),
            wrap=True,
            justify=Gtk.Justification.CENTER,
        ))

        status_label = Gtk.Label(wrap=True, justify=Gtk.Justification.CENTER)
        root.append(status_label)

        path_label = Gtk.Label(wrap=True, selectable=True)
        path_label.add_css_class("dim-label")
        root.append(path_label)

        result_label = Gtk.Label(wrap=True, justify=Gtk.Justification.CENTER)
        result_label.add_css_class("dim-label")
        root.append(result_label)

        buttons = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=12,
            halign=Gtk.Align.CENTER,
        )
        install_button = Gtk.Button()
        install_button.add_css_class("suggested-action")
        uninstall_button = Gtk.Button(label=tr("steam_uninstall"))
        uninstall_button.add_css_class("destructive-action")
        buttons.append(install_button)
        buttons.append(uninstall_button)
        root.append(buttons)

        ctx = {
            "window": window,
            "status_label": status_label,
            "path_label": path_label,
            "result_label": result_label,
            "install_button": install_button,
            "uninstall_button": uninstall_button,
        }
        install_button.connect("clicked", lambda _b: self._steam_on_install(ctx))
        uninstall_button.connect("clicked", lambda _b: self._steam_on_uninstall(ctx))

        self._steam_refresh(ctx)
        window.set_child(root)
        window.present()

    # -- état -------------------------------------------------------------------

    def _steam_refresh(self, ctx):
        status = steam_compat.get_status()
        css, message = status_view(status)

        label = ctx["status_label"]
        for name in STATUS_CLASSES:
            label.remove_css_class(name)
        label.add_css_class(css)
        label.set_text(message)

        ctx["path_label"].set_text(str(status.dest))
        ctx["install_button"].set_label(
            tr("steam_reinstall") if status.installed else tr("steam_install"))
        ctx["install_button"].set_sensitive(status.steam_found)
        ctx["uninstall_button"].set_sensitive(status.installed)

    def _steam_report(self, ctx, text, is_error=False):
        ctx["result_label"].set_text(text)
        if is_error:
            logger.error(f"Configuration Steam : {text}")
        elif hasattr(self, "status"):
            self.status.set_text(text)

    # -- installation -----------------------------------------------------------

    def _steam_on_install(self, ctx):
        try:
            conflicts = steam_compat.install_conflicts()
        except steam_compat.SteamInstallError as exc:
            self._steam_report(ctx, tr("steam_error", error=str(exc)), True)
            return

        if not conflicts:
            self._steam_do_install(ctx)
            return

        show_confirm(
            ctx["window"],
            tr("steam_title"),
            tr("steam_confirm_replace", files=", ".join(conflicts)),
            lambda ok: self._steam_do_install(ctx) if ok else None,
        )

    def _steam_do_install(self, ctx):
        try:
            # La confirmation éventuelle a déjà été demandée dans la fenêtre.
            steam_compat.install(assume_yes=True, out=lambda _m: None)
        except steam_compat.SteamInstallError as exc:
            self._steam_report(ctx, tr("steam_error", error=str(exc)), True)
        else:
            self._steam_report(ctx, tr("steam_installed_ok"))
        self._steam_refresh(ctx)

    # -- désinstallation --------------------------------------------------------

    def _steam_on_uninstall(self, ctx):
        show_confirm(
            ctx["window"],
            tr("steam_title"),
            tr("steam_confirm_uninstall"),
            lambda ok: self._steam_do_uninstall(ctx) if ok else None,
        )

    def _steam_do_uninstall(self, ctx):
        try:
            result = steam_compat.uninstall(assume_yes=True, out=lambda _m: None)
        except steam_compat.SteamInstallError as exc:
            self._steam_report(ctx, tr("steam_error", error=str(exc)), True)
        else:
            if result.kept:
                text = tr("steam_uninstalled_kept", files=", ".join(result.kept))
            else:
                text = tr("steam_uninstalled_ok")
            self._steam_report(ctx, text)
        self._steam_refresh(ctx)


# ------------------------------------------------------------------------------------
# ACTION (application)
# ------------------------------------------------------------------------------------

def register_steam_action(app):
    """Enregistre `app.steam_config` ; à appeler depuis _create_actions."""
    action = Gio.SimpleAction.new(ACTION_NAME, None)

    def on_activate(_action, _param):
        # get_active_window() peut renvoyer une boîte de dialogue :
        # on cherche le tableau de bord lui-même.
        for win in app.get_windows():
            if hasattr(win, "show_steam_window"):
                win.show_steam_window()
                return

    action.connect("activate", on_activate)
    app.add_action(action)
