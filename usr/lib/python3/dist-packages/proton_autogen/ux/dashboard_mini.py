#!/usr/bin/env python3

# dashboard_mini.py
"""
Réduction automatique de l'interface pendant l'exécution d'un jeu.

Quand un jeu est lancé, la fenêtre principale est minimisée et une
notification desktop persistante (icône + nom du jeu) prend le relais :
cliquer dessus restaure la fenêtre. Quand le jeu s'arrête, la
notification est retirée et la fenêtre restaurée automatiquement.

Pourquoi Gio.Notification et pas une "vraie" icône de zone de
notification (system tray) ?

  GTK4 a retiré Gtk.StatusIcon, son ancienne API de tray icon. Les
  bibliothèques de remplacement historiques (AppIndicator3,
  AyatanaAppIndicator3) dépendent en interne de GTK3 — et GObject
  Introspection n'autorise qu'UNE SEULE version d'un même namespace par
  processus. Comme cette application charge déjà Gtk 4.0
  (gi.require_version("Gtk", "4.0") dans dashboard.py), charger
  AppIndicator3 dans le même processus est en pratique cassé ou
  instable, quelle que soit la distribution. Une véritable icône
  system tray sous GTK4 nécessiterait d'implémenter soi-même le
  protocole D-Bus StatusNotifierItem (freedesktop), qui dépend en plus
  du support de l'extension correspondante côté environnement de
  bureau (natif sous KDE/XFCE, nécessite une extension GNOME Shell) —
  hors périmètre ici pour rester fiable partout sans configuration
  utilisateur supplémentaire.

  Gio.Notification, lui, fait déjà exactement ce qui est demandé
  ("réduire l'UX, afficher une icône dans la barre de notification") :
  il s'appuie sur le service de notifications standard du bureau
  (GNOME Shell, Plasma, xfce4-notifyd...), inclus nativement dans
  GLib/GTK4, sans dépendance ni configuration supplémentaire.

Intégration requise dans dashboard.py (une seule ligne, même pattern
que tous les autres mixins de ce module) :

    from proton_autogen.ux.dashboard_mini import DashboardMiniMixin

    class Dashboard(DashboardMiniMixin, DashboardUIMixin, DashboardDialogsMixin,
                     DashboardActionsMixin, DashboardMangoHudMixin,
                     DashboardCreateShortcutMixin, Gtk.ApplicationWindow):
        ...

DashboardMiniMixin DOIT être placé AVANT DashboardUIMixin dans la liste
des classes de base : il surcharge _update_stop_button_state() pour
s'intercaler avant l'implémentation d'origine (définie dans
dashboard_ui.py), tout en la préservant via super(). Aucune autre
modification n'est nécessaire : DashboardActionsMixin continue
d'appeler self._update_stop_button_state(is_running, game_name)
exactement comme avant — c'est ce hook déjà existant qui déclenche le
mode réduit, sans avoir à toucher au reste du code.
"""

import configparser
import os

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio

from proton_autogen.i18n import tr
from proton_autogen.ux.themes import CONFIG_PATH
from proton_autogen.utils.logger import StructuredLogger

logger = StructuredLogger("proton-autogen.ux.dashboard_mini")

# Identifiant stable de la notification : la réutiliser (plutôt qu'en
# créer une nouvelle à chaque jeu) permet de la mettre à jour en place
# et de la retirer proprement via withdraw_notification().
MINI_NOTIFICATION_ID = "proton-autogen-running"

# ID distinct de MINI_NOTIFICATION_ID : une notification de crash ne
# doit PAS disparaître quand _exit_mini_mode() retire la notification
# "en cours" juste après (ce qui arrive systématiquement à la fin d'un
# jeu, crash ou non — les deux notifications ont un cycle de vie
# indépendant).
MINI_CRASH_NOTIFICATION_ID = "proton-autogen-crashed"

# Nom de l'action GAction enregistrée sur l'application, déclenchée par
# un clic sur la notification (voir set_default_action ci-dessous).
RESTORE_ACTION_NAME = "restore-window"


# ------------------------------------------------------------------------------------
# DÉTECTION DE SUPPORT DE minimize() (pure, sans GTK — testable isolément)
# ------------------------------------------------------------------------------------

# Environnements de bureau Wayland "complets" connus pour honorer
# correctement xdg_toplevel.set_minimized (testé via KWin/Mutter). Tout
# ce qui n'y figure pas est traité comme non fiable par défaut : les
# compositeurs tiling (Hyprland, Sway, river, wayfire, labwc...) n'ont
# généralement pas de notion de fenêtre "minimisée" faute de barre des
# tâches vers laquelle réduire, et ignorent silencieusement la requête.
# Volontairement une liste blanche (opt-in) plutôt qu'une liste noire :
# en cas de doute sur un compositeur inconnu, on préfère ne pas
# prétendre à un mode réduit qui n'aurait aucun effet visible.
_WAYLAND_MINIMIZE_SUPPORTED = {
    "kde", "plasma", "gnome", "gnome-shell", "cinnamon", "mate", "xfce", "budgie",
}

# Compositeurs Wayland tiling connus pour NE PAS honorer la requête.
# Cette liste sert uniquement à enrichir le message de log (nommer
# explicitement le compositeur détecté) — la décision elle-même repose
# sur l'absence de _WAYLAND_MINIMIZE_SUPPORTED, pas sur cette liste.
_WAYLAND_MINIMIZE_KNOWN_UNSUPPORTED = {
    "hyprland", "sway", "river", "wayfire", "labwc", "dwl",
}


def _detect_session_info() -> tuple[str, str]:
    """Retourne (type_session, id_bureau) en minuscules, d'après les
    variables d'environnement standard XDG."""
    session_type = os.environ.get("XDG_SESSION_TYPE", "").strip().lower()

    desktop = (
        os.environ.get("XDG_CURRENT_DESKTOP", "")
        or os.environ.get("XDG_SESSION_DESKTOP", "")
        or os.environ.get("DESKTOP_SESSION", "")
    ).strip().lower()

    return session_type, desktop


def detect_minimize_support() -> tuple[bool, str]:
    """
    Détermine si Gtk.Window.minimize() a une chance raisonnable de
    fonctionner sur la session courante.

    Retourne (supporté, raison) — la raison est uniquement destinée au
    logging/diagnostic, jamais affichée à l'utilisateur.

      - X11 : toujours supporté (iconify est un mécanisme ICCCM
        standard, indépendant du gestionnaire de fenêtres).
      - Hyprland : détecté explicitement via la variable
        HYPRLAND_INSTANCE_SIGNATURE, posée par Hyprland lui-même — plus
        fiable que XDG_CURRENT_DESKTOP, qui peut varier selon la
        méthode de lancement de la session.
      - Wayland, autre bureau : supporté uniquement si l'identifiant de
        bureau figure dans la liste blanche _WAYLAND_MINIMIZE_SUPPORTED
        (KDE, GNOME, XFCE...). Non supporté par défaut sinon.
      - Type de session inconnu (rare) : posture prudente, non supporté.
    """
    if "HYPRLAND_INSTANCE_SIGNATURE" in os.environ:
        return False, "hyprland (HYPRLAND_INSTANCE_SIGNATURE détectée)"

    session_type, desktop = _detect_session_info()

    if session_type == "x11":
        return True, "x11"

    if session_type == "wayland":
        # XDG_CURRENT_DESKTOP peut contenir plusieurs valeurs séparées
        # par ':' (ex: "ubuntu:GNOME") -> on teste chaque segment.
        segments = [d for d in desktop.split(":") if d]

        for seg in segments:
            if seg in _WAYLAND_MINIMIZE_SUPPORTED:
                return True, f"wayland/{seg}"

        for seg in segments:
            if seg in _WAYLAND_MINIMIZE_KNOWN_UNSUPPORTED:
                return False, f"wayland/{seg} (compositeur tiling connu)"

        return False, f"wayland/{desktop or 'inconnu'} (hors liste blanche)"

    return False, f"type de session inconnu ({session_type or 'non défini'})"


# ------------------------------------------------------------------------------------
# CONFIGURATION (pure, sans GTK) — réutilise le même fichier que themes.py
# ------------------------------------------------------------------------------------

def load_mini_mode_enabled(default: bool = True) -> bool:
    """Lit la préférence utilisateur [mini] mini_mode dans le même
    fichier de config que le thème (proton-autogen-ux.conf). Activé par
    défaut ; peut être désactivé sans toucher au reste de la config."""
    cfg = configparser.ConfigParser()

    if CONFIG_PATH.exists():
        try:
            cfg.read(CONFIG_PATH)
            return cfg.getboolean("mini", "mini_mode", fallback=default)
        except Exception:
            return default

    return default


def save_mini_mode_enabled(enabled: bool):
    cfg = configparser.ConfigParser()

    if CONFIG_PATH.exists():
        try:
            cfg.read(CONFIG_PATH)
        except Exception:
            pass

    if "mini" not in cfg:
        cfg["mini"] = {}

    cfg["mini"]["mini_mode"] = "true" if enabled else "false"

    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        cfg.write(f)


_VALID_MINIMIZE_MODES = ("auto", "on", "off")


def load_minimize_mode(default: str = "auto") -> str:
    """Lit [mini] minimize dans proton-autogen-ux.conf :
      - "auto" (défaut) : suit detect_minimize_support().
      - "on"  : force minimize() même hors liste blanche (utile si la
        détection se trompe sur un compositeur non répertorié qui
        honore en fait la requête).
      - "off" : désactive minimize() quel que soit le résultat de la
        détection, sans affecter le reste du mode réduit (notification
        toujours active).
    """
    cfg = configparser.ConfigParser()

    if CONFIG_PATH.exists():
        try:
            cfg.read(CONFIG_PATH)
            value = cfg.get("mini", "minimize", fallback=default).strip().lower()
            if value in _VALID_MINIMIZE_MODES:
                return value
        except Exception:
            pass

    return default


def save_minimize_mode(mode: str):
    if mode not in _VALID_MINIMIZE_MODES:
        raise ValueError(f"mode invalide: {mode!r} (attendu: {_VALID_MINIMIZE_MODES})")

    cfg = configparser.ConfigParser()

    if CONFIG_PATH.exists():
        try:
            cfg.read(CONFIG_PATH)
        except Exception:
            pass

    if "mini" not in cfg:
        cfg["mini"] = {}

    cfg["mini"]["minimize"] = mode

    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        cfg.write(f)


def resolve_minimize_enabled() -> tuple[bool, str]:
    """Résout la décision finale minimize() oui/non, dans cet ordre de
    priorité :

      1. Variable d'environnement PROTON_AUTOGEN_FORCE_MINIMIZE (1/0),
         utile pour tester sans toucher au fichier de config.
      2. Préférence persistée [mini] minimize ("on"/"off").
      3. Détection automatique (detect_minimize_support()).

    Retourne (activé, raison) pour le logging.
    """
    env_override = os.environ.get("PROTON_AUTOGEN_FORCE_MINIMIZE")
    if env_override is not None:
        enabled = env_override.strip().lower() not in ("0", "false", "no", "off")
        return enabled, f"variable d'environnement PROTON_AUTOGEN_FORCE_MINIMIZE={env_override!r}"

    mode = load_minimize_mode()

    if mode == "on":
        return True, "forcé via config ([mini] minimize = on)"

    if mode == "off":
        return False, "désactivé via config ([mini] minimize = off)"

    return detect_minimize_support()


# ------------------------------------------------------------------------------------
# PARTIE GTK
# ------------------------------------------------------------------------------------

class DashboardMiniMixin:
    """Minimise la fenêtre et affiche une notification desktop pendant
    qu'un jeu tourne. Voir la docstring du module pour l'ordre de
    déclaration requis dans la classe Dashboard."""

    # -------------------------
    # Hook principal (voir _update_stop_button_state dans dashboard_ui.py)
    # -------------------------
    def _update_stop_button_state(self, is_running: bool, game_name: str = None):
        # Comportement d'origine (visibilité/label du bouton Stop)
        # entièrement préservé, inchangé.
        super()._update_stop_button_state(is_running, game_name)

        if not getattr(self, "_mini_mode_enabled", None):
            self._mini_mode_enabled = load_mini_mode_enabled()

        if not self._mini_mode_enabled:
            return

        if is_running:
            self._enter_mini_mode(game_name)
        else:
            self._exit_mini_mode()

    # -------------------------
    # API publique (extension point pour un futur réglage utilisateur)
    # -------------------------
    def set_mini_mode_enabled(self, enabled: bool):
        """Active/désactive la réduction automatique et persiste le
        choix. Pensé pour être branché plus tard sur une case à cocher
        dans les préférences ; fonctionne dès maintenant tel quel."""
        self._mini_mode_enabled = enabled
        save_mini_mode_enabled(enabled)

    def set_minimize_mode(self, mode: str):
        """mode: "auto" | "on" | "off" — voir load_minimize_mode()."""
        save_minimize_mode(mode)
        # Invalide le cache pour que la prochaine minimisation
        # re-résolve immédiatement, sans attendre un redémarrage.
        self._minimize_enabled = None

    # -------------------------
    # Mode réduit
    # -------------------------
    def _enter_mini_mode(self, game_name: str = None):
        self._ensure_restore_action_registered()

        label = game_name or tr("mini_running_generic")
        self._show_running_notification(label)

        if getattr(self, "_minimize_enabled", None) is None:
            enabled, reason = resolve_minimize_enabled()
            self._minimize_enabled = enabled
            logger.info(
                "Mini mode: minimize() %s (%s)",
                "activé" if enabled else "désactivé",
                reason,
            )

        if not self._minimize_enabled:
            return

        # minimize() : demande de minimisation au gestionnaire de
        # fenêtres. Fiable sous X11 et sous les bureaux Wayland
        # complets détectés (KDE, GNOME...). Sous les compositeurs
        # tiling connus pour l'ignorer (Hyprland, Sway...), la
        # détection ci-dessus court-circuite déjà cet appel — on ne
        # l'atteint donc que sur les environnements où il a une réelle
        # chance de fonctionner.
        self.minimize()

    def _exit_mini_mode(self):
        self._withdraw_running_notification()

        # unminimize() + present() : sans effet si la fenêtre était
        # déjà visible (l'utilisateur l'a peut-être restaurée
        # lui-même entre-temps) — aucun risque de lui "voler" le focus
        # de façon intrusive au-delà d'une restauration normale.
        self.unminimize()
        self.present()

    # -------------------------
    # Notification desktop
    # -------------------------
    def _show_running_notification(self, game_name: str):
        app = self.get_application()
        if app is None:
            return

        notif = Gio.Notification.new(tr("mini_notification_title"))
        notif.set_body(tr("mini_notification_body").format(name=game_name))
        notif.set_icon(Gio.ThemedIcon.new("proton-autogen"))
        notif.set_priority(Gio.NotificationPriority.LOW)
        notif.set_default_action(f"app.{RESTORE_ACTION_NAME}")

        app.send_notification(MINI_NOTIFICATION_ID, notif)

    def _withdraw_running_notification(self):
        app = self.get_application()
        if app is not None:
            app.withdraw_notification(MINI_NOTIFICATION_ID)

    # -------------------------
    # Notification de crash
    # -------------------------
    def notify_game_crashed(self, game_name: str, detail):
        """Affiche une notification d'erreur distincte de la
        notification "en cours" — indépendante de son cycle de vie
        (voir MINI_CRASH_NOTIFICATION_ID) et de priorité plus élevée,
        pour rester visible même si l'utilisateur n'a pas vu passer la
        notification "en cours" pendant que la fenêtre était minimisée.

        game_name : nom du jeu concerné.
        detail    : code de sortie non nul (int) OU message d'exception
            (str) — les deux cas sont mis en forme via la même clé
            i18n, aucune distinction nécessaire côté appelant.

        Appelé depuis dashboard_actions.py::launch_game() (via
        hasattr(self, "notify_game_crashed"), donc sans dépendance dure
        à ce mixin) chaque fois que le jeu se termine avec un code de
        sortie non nul ou qu'une exception a empêché son lancement.

        Respecte le même interrupteur global que le reste du mode
        réduit ([mini] mini_mode) : si l'utilisateur a désactivé la
        réduction automatique, aucune notification n'est envoyée par ce
        module, y compris celle-ci — un seul réglage, un seul mental
        model.
        """
        if not getattr(self, "_mini_mode_enabled", None):
            self._mini_mode_enabled = load_mini_mode_enabled()

        if not self._mini_mode_enabled:
            return

        app = self.get_application()
        if app is None:
            return

        self._ensure_restore_action_registered()

        notif = Gio.Notification.new(tr("mini_crash_notification_title"))
        notif.set_body(tr("game_crashed", name=game_name, code=detail))
        notif.set_icon(Gio.ThemedIcon.new("dialog-error-symbolic"))
        notif.set_priority(Gio.NotificationPriority.HIGH)
        notif.set_default_action(f"app.{RESTORE_ACTION_NAME}")

        app.send_notification(MINI_CRASH_NOTIFICATION_ID, notif)

        logger.info(f"Crash notification shown for {game_name}: {detail}")

    # -------------------------
    # Action "restaurer la fenêtre" (clic sur la notification)
    # -------------------------
    def _ensure_restore_action_registered(self):
        """Enregistre app.restore-window au premier lancement de jeu
        plutôt qu'à l'initialisation de la fenêtre : évite de devoir
        toucher à Dashboard.__init__ ou à
        ProtonAutogenApp._create_actions() dans dashboard.py — toute la
        fonctionnalité reste isolée dans ce fichier."""
        if getattr(self, "_mini_restore_action_registered", False):
            return

        app = self.get_application()
        if app is None:
            return

        action = Gio.SimpleAction.new(RESTORE_ACTION_NAME, None)
        action.connect("activate", lambda *_: self._exit_mini_mode())
        app.add_action(action)

        self._mini_restore_action_registered = True
