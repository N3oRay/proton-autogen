#!/usr/bin/env python3

# dashboard_creatshortcut.py
"""
Création de raccourcis .desktop pour un jeu Proton-Autogen :

  - Raccourci "application" : ~/.local/share/applications/proton-autogen-<slug>.desktop
    (apparaît dans le menu des applications du bureau)
  - Raccourci "bureau" : <XDG Desktop>/proton-autogen-<slug>.desktop
    (icône double-cliquable sur le bureau, marquée "trusted" quand possible)

La logique fichiers (pure, sans GTK) est en haut du module pour être
testable indépendamment de l'interface. La partie GTK
(DashboardCreateShortcutMixin) en bas se limite à la boîte de dialogue
de confirmation et à son câblage.
"""

import re
import stat
import subprocess
from pathlib import Path

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

from proton_autogen.i18n import tr
from proton_autogen.ux.icon_manager import find_game_icon, find_internal_icon, DEFAULT_ICON
from proton_autogen.utils.logger import StructuredLogger

logger = StructuredLogger("proton-autogen.ux.dashboard_creatshortcut")


# ------------------------------------------------------------------------------------
# CHEMINS
# ------------------------------------------------------------------------------------

APPLICATIONS_DIR = Path.home() / ".local" / "share" / "applications"


def _get_desktop_dir() -> Path:
    """Résout le dossier Bureau via xdg-user-dir (respecte les dossiers
    localisés/déplacés par l'utilisateur), avec repli sur ~/Desktop."""
    try:
        result = subprocess.run(
            ["xdg-user-dir", "DESKTOP"],
            capture_output=True,
            text=True,
            timeout=2,
        )
        if result.returncode == 0:
            out = result.stdout.strip()
            if out:
                return Path(out)
    except Exception:
        pass

    return Path.home() / "Desktop"


# ------------------------------------------------------------------------------------
# ICÔNE (même résolution que la game list, sans le cache Gtk.Image)
# ------------------------------------------------------------------------------------

def resolve_shortcut_icon_path(game: dict) -> str:
    """Retourne le chemin absolu de l'icône telle qu'affichée dans la
    game list : icône trouvée à côté de l'exécutable, sinon icône
    interne mappée sur le nom du jeu, sinon icône par défaut."""
    icon_path = find_game_icon(game)
    if icon_path is None:
        icon_path = find_internal_icon(game)
    if icon_path is None:
        icon_path = DEFAULT_ICON

    return str(icon_path)


# ------------------------------------------------------------------------------------
# GÉNÉRATION DU .desktop
# ------------------------------------------------------------------------------------

def _sanitize_slug(name: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", (name or "").strip().lower())
    slug = slug.strip("-")
    return slug or "game"


def _desktop_escape(value: str) -> str:
    """Un champ .desktop est une seule ligne : on neutralise les retours
    à la ligne éventuels dans le nom du jeu."""
    return (value or "").replace("\n", " ").replace("\r", " ").strip()


def _shortcut_filename(game: dict) -> str:
    return f"proton-autogen-{_sanitize_slug(game.get('name', ''))}.desktop"


def build_desktop_entry_content(game: dict, icon_path: str) -> str:
    name = _desktop_escape(game.get("name") or "Unknown Game")
    path = game.get("path") or ""

    # Exec attendu : proton-autogen "path/to/app" %U
    exec_line = f'proton-autogen "{path}" %U'

    lines = [
        "[Desktop Entry]",
        "Type=Application",
        "Version=1.0",
        f"Name={name}",
        f"Exec={exec_line}",
        f"Icon={icon_path}",
        "Terminal=false",
        "Categories=Game;",
        "StartupNotify=true",
    ]
    return "\n".join(lines) + "\n"


# ------------------------------------------------------------------------------------
# ÉCRITURE FICHIER
# ------------------------------------------------------------------------------------

def _write_desktop_file(directory: Path, filename: str, content: str, make_executable: bool) -> tuple[bool, str]:
    try:
        directory.mkdir(parents=True, exist_ok=True)
        target = directory / filename
        target.write_text(content, encoding="utf-8")

        if make_executable:
            # Nécessaire pour que l'icône soit lancable en double-clic
            mode = target.stat().st_mode
            target.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

            # GNOME/Nautilus exige en plus le flag "trusted", sinon le
            # raccourci reste affiché comme "non fiable" tant qu'on ne
            # clique pas sur "Autoriser le lancement". Best-effort : si
            # gio est absent ou échoue, le fichier reste valide, juste
            # pas encore marqué "trusted".
            try:
                subprocess.run(
                    ["gio", "set", str(target), "metadata::trusted", "true"],
                    capture_output=True,
                    timeout=2,
                )
            except Exception:
                pass

        return True, str(target)

    except OSError as e:
        return False, str(e)


def install_application_shortcut(game: dict) -> tuple[bool, str]:
    """Crée l'entrée dans le menu des applications
    (~/.local/share/applications)."""
    icon_path = resolve_shortcut_icon_path(game)
    content = build_desktop_entry_content(game, icon_path)
    filename = _shortcut_filename(game)
    return _write_desktop_file(APPLICATIONS_DIR, filename, content, make_executable=False)


def install_desktop_shortcut(game: dict) -> tuple[bool, str]:
    """Crée l'icône sur le Bureau."""
    icon_path = resolve_shortcut_icon_path(game)
    content = build_desktop_entry_content(game, icon_path)
    filename = _shortcut_filename(game)
    return _write_desktop_file(_get_desktop_dir(), filename, content, make_executable=True)


# ------------------------------------------------------------------------------------
# PARTIE GTK
# ------------------------------------------------------------------------------------

class DashboardCreateShortcutMixin:
    """Boîte de dialogue de confirmation pour la création de raccourcis.

    Doit être mixé avec une classe qui expose self.toast et self.status
    (Dashboard).
    """

    def show_create_shortcut_dialog(self, game):
        win = Gtk.Window(
            title=tr("shortcut_dialog_title"),
            transient_for=self,
            modal=True,
            resizable=False,
        )
        win.set_default_size(400, 220)
        win.add_css_class("shortcut-dialog")

        box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=14,
            margin_top=20,
            margin_bottom=20,
            margin_start=20,
            margin_end=20,
        )

        title = Gtk.Label(label=game.get("name", ""))
        title.add_css_class("title-4")
        title.set_halign(Gtk.Align.START)
        box.append(title)

        # Application shortcut : coché par défaut (Y/n)
        app_check = Gtk.CheckButton(label=tr("shortcut_create_app"))
        app_check.add_css_class("feature-toggle")
        app_check.set_active(True)
        box.append(app_check)

        # Desktop shortcut : décoché par défaut (y/N)
        desktop_check = Gtk.CheckButton(label=tr("shortcut_create_desktop"))
        desktop_check.add_css_class("feature-toggle")
        desktop_check.set_active(False)
        box.append(desktop_check)

        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        btn_box.set_halign(Gtk.Align.END)

        cancel_btn = Gtk.Button(label=tr("cancel"))
        cancel_btn.add_css_class("alternative-action")
        cancel_btn.connect("clicked", lambda *_: win.close())

        create_btn = Gtk.Button(label=tr("shortcut_create_button"))
        create_btn.add_css_class("suggested-action")
        create_btn.connect(
            "clicked",
            lambda *_: self._on_confirm_create_shortcut(
                win, game, app_check.get_active(), desktop_check.get_active()
            ),
        )

        btn_box.append(cancel_btn)
        btn_box.append(create_btn)
        box.append(btn_box)

        win.set_child(box)
        win.present()

    def _on_confirm_create_shortcut(self, win, game, create_app, create_desktop):
        messages = []
        all_ok = True

        if create_app:
            success, result = install_application_shortcut(game)
            all_ok = all_ok and success
            if success:
                messages.append(tr("shortcut_app_success"))
                logger.info(f"Application shortcut created: {result}")
            else:
                messages.append(f"{tr('shortcut_app_failed')}: {result}")
                logger.error(f"Application shortcut failed: {result}")

        if create_desktop:
            success, result = install_desktop_shortcut(game)
            all_ok = all_ok and success
            if success:
                messages.append(tr("shortcut_desktop_success"))
                logger.info(f"Desktop shortcut created: {result}")
            else:
                messages.append(f"{tr('shortcut_desktop_failed')}: {result}")
                logger.error(f"Desktop shortcut failed: {result}")

        if not create_app and not create_desktop:
            messages.append(tr("shortcut_nothing_selected"))
            all_ok = False

        text = " — ".join(messages)

        if hasattr(self, "toast"):
            (self.toast.success if all_ok else self.toast.error)(text)
        if hasattr(self, "status"):
            self.status.set_text(text)

        win.close()
