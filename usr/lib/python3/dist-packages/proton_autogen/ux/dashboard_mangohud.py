#!/usr/bin/env python3

#dashboard_mangohud.py
"""
Fonctionnalités MangoHud du Dashboard :

  - Application de la configuration recommandée (proton_autogen.info.
    get_mangohud_model_text(), qui résout déjà docs/mangohud_<lang>.txt
    avec repli sur l'anglais) vers ~/.config/MangoHud/MangoHud.conf
  - Sauvegarde automatique de la configuration existante vers
    ~/.config/MangoHud.bak avant application
  - Restauration de la sauvegarde en un clic

Toute la logique fichiers (pure, sans GTK) est en haut du module pour
être testable indépendamment de l'interface. La partie GTK
(DashboardMangoHudMixin) en bas se limite à une rangée de deux boutons
et à leur câblage — le texte de la configuration recommandée est déjà
affiché par show_mangohud_advice_dialog() dans dashboard_dialogs.py, ce
module n'a donc pas à le réafficher.
"""

import shutil
from pathlib import Path

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

from proton_autogen.i18n import tr, detect_help_env_lang
from proton_autogen.info import get_docs_root, get_mangohud_model_text
from proton_autogen.utils.logger import StructuredLogger

logger = StructuredLogger("proton-autogen.ux.dashboard_mangohud")


# ------------------------------------------------------------------------------------
# CHEMINS
# ------------------------------------------------------------------------------------

# Emplacement standard lu par MangoHud lui-même.
MANGOHUD_CONFIG_DIR = Path.home() / ".config" / "MangoHud"
MANGOHUD_CONFIG_FILE = MANGOHUD_CONFIG_DIR / "MangoHud.conf"

# Sauvegarde : le dossier MangoHud entier est renommé tel quel, pas
# seulement le fichier .conf, pour ne perdre aucun réglage annexe
# (presets, etc.) que l'utilisateur aurait pu y placer.
MANGOHUD_BACKUP_DIR = Path.home() / ".config" / "MangoHud.bak"


# ------------------------------------------------------------------------------------
# LOGIQUE PURE (sans GTK)
# ------------------------------------------------------------------------------------

def has_mangohud_backup() -> bool:
    return MANGOHUD_BACKUP_DIR.exists()


def _mangohud_model_file_exists() -> bool:
    """Vérifie qu'un fichier docs/mangohud_<lang>.txt ou mangohud_en.txt
    existe réellement, sans dépendre du texte de repli renvoyé par
    get_mangohud_model_text() en cas d'absence (qui est un texte
    d'affichage, pas un signal fiable pour la logique)."""
    root = get_docs_root()
    lang = detect_help_env_lang()

    for filename in (f"mangohud_{lang}.txt", "mangohud_en.txt"):
        if (root / filename).exists():
            return True

    return False


def _remove_path(path: Path):
    """Supprime un fichier, un lien symbolique ou un dossier, quel que
    soit son type."""
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def apply_mangohud_config() -> tuple[bool, str]:
    """
    Applique la configuration MangoHud recommandée (proton_autogen.info.
    get_mangohud_model_text()) pour la langue courante.

    Retourne (succès, code_erreur). code_erreur est une chaîne vide en
    cas de succès, sinon :
      - "config_not_found" : aucun fichier docs/mangohud_<lang>.txt ni
        mangohud_en.txt disponible
      - un message d'exception OSError brut, pour le logging

    Comportement :
      1. Si ~/.config/MangoHud existe déjà, il est renommé en
         ~/.config/MangoHud.bak. Un seul niveau de sauvegarde est
         conservé : un .bak déjà présent est écrasé (cf.
         restore_mangohud_config() pour le bouton "retour arrière").
      2. Le nouveau contenu est écrit dans
         ~/.config/MangoHud/MangoHud.conf.
    """
    if not _mangohud_model_file_exists():
        return False, "config_not_found"

    text = get_mangohud_model_text()

    try:
        if MANGOHUD_CONFIG_DIR.exists() or MANGOHUD_CONFIG_DIR.is_symlink():
            if MANGOHUD_BACKUP_DIR.exists() or MANGOHUD_BACKUP_DIR.is_symlink():
                _remove_path(MANGOHUD_BACKUP_DIR)

            shutil.move(str(MANGOHUD_CONFIG_DIR), str(MANGOHUD_BACKUP_DIR))

        MANGOHUD_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        MANGOHUD_CONFIG_FILE.write_text(text, encoding="utf-8")

        return True, ""

    except OSError as e:
        return False, str(e)


def restore_mangohud_config() -> tuple[bool, str]:
    """
    Restaure ~/.config/MangoHud depuis ~/.config/MangoHud.bak.

    La configuration courante (issue du dernier apply_mangohud_config())
    est écrasée par la sauvegarde — comportement volontaire d'un "retour
    en arrière" simple à un seul niveau.

    Retourne (succès, code_erreur) ; code_erreur == "no_backup" si aucune
    sauvegarde n'existe.
    """
    if not MANGOHUD_BACKUP_DIR.exists():
        return False, "no_backup"

    try:
        if MANGOHUD_CONFIG_DIR.exists() or MANGOHUD_CONFIG_DIR.is_symlink():
            _remove_path(MANGOHUD_CONFIG_DIR)

        shutil.move(str(MANGOHUD_BACKUP_DIR), str(MANGOHUD_CONFIG_DIR))

        return True, ""

    except OSError as e:
        return False, str(e)


# ------------------------------------------------------------------------------------
# PARTIE GTK
# ------------------------------------------------------------------------------------

class DashboardMangoHudMixin:
    """Rangée de boutons Appliquer / Revenir en arrière pour la
    configuration MangoHud recommandée.

    Doit être mixé avec une classe qui expose self.toast et self.status
    (Dashboard, via DashboardDialogsMixin déjà mixé — le texte de la
    configuration est affiché par show_mangohud_advice_dialog()).
    """

    def _build_mangohud_action_buttons(self):
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        box.set_margin_top(8)

        apply_btn = Gtk.Button(label=tr("mangohud_apply_button"))
        apply_btn.add_css_class("section-toggle")
        apply_btn.connect("clicked", self._on_apply_mangohud_config)
        box.append(apply_btn)

        restore_btn = Gtk.Button(label=tr("mangohud_restore_button"))
        restore_btn.add_css_class("section-toggle")
        restore_btn.set_sensitive(has_mangohud_backup())
        restore_btn.connect("clicked", self._on_restore_mangohud_config)
        box.append(restore_btn)

        # Conservé pour réactiver/désactiver le bouton Restaurer après un
        # clic, sans reconstruire toute la boîte de dialogue.
        self._mangohud_restore_btn = restore_btn

        return box

    def _on_apply_mangohud_config(self, _btn):
        success, error = apply_mangohud_config()

        if success:
            self.toast.success(tr("mangohud_apply_success"))
            self.status.set_text(tr("mangohud_apply_success"))
            logger.info("MangoHud config applied")
        else:
            if error == "config_not_found":
                self.toast.error(tr("mangohud_config_not_found"))
            else:
                self.toast.error(tr("mangohud_apply_failed"))
            logger.error(f"MangoHud config apply failed: {error}")

        if hasattr(self, "_mangohud_restore_btn"):
            self._mangohud_restore_btn.set_sensitive(has_mangohud_backup())

    def _on_restore_mangohud_config(self, _btn):
        success, error = restore_mangohud_config()

        if success:
            self.toast.success(tr("mangohud_restore_success"))
            self.status.set_text(tr("mangohud_restore_success"))
            logger.info("MangoHud config restored from backup")
        else:
            if error == "no_backup":
                self.toast.error(tr("mangohud_no_backup"))
            else:
                self.toast.error(tr("mangohud_restore_failed"))
            logger.error(f"MangoHud config restore failed: {error}")

        if hasattr(self, "_mangohud_restore_btn"):
            self._mangohud_restore_btn.set_sensitive(has_mangohud_backup())
