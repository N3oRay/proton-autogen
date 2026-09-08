#!/usr/bin/env python3
"""
Dashboard Import Mixin - Importation graphique Lutris/Bottles/Heroic/Wine
Réutilise la logique de scan_all() et import_selected() depuis import_scan.py
"""

import os
import gi
import threading

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib

from proton_autogen.import_scan import (
    scan_all,
    scan_wine_prefixes,
    any_source_available,
    total_count,
    import_selected,
)
from proton_autogen.i18n import tr
from proton_autogen.utils.logger import StructuredLogger

logger = StructuredLogger("proton-autogen.dashboard.import")

# Mapping des clés de source vers des labels affichables
_IMPORT_LABELS = {
    "lutris": "Lutris",
    "bottles": "Bottles",
    "heroic": "Heroic",
    "wine": "Wine Prefixes",
}

_IMPORT_ICONS = {
    "lutris": "🎮",
    "bottles": "🍾",
    "heroic": "⚡",
    "wine": "🍷",
}


class DashboardImportMixin:
    """Boîte de dialogue d'import pour le Dashboard (Lutris/Bottles/Heroic/Wine).
    Doit être mixé avec une classe Gtk.ApplicationWindow.
    """

    def show_import_dialog(self):
        """Lance le dialog d'import avec spinner initial."""
        win = Gtk.Window(
            transient_for=self,
            modal=True,
            title=tr("import_dialog_title") or "Import Applications",
        )
        win.set_default_size(600, 500)
        win.add_css_class("import-dialog")

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        box.set_margin_start(12)
        box.set_margin_end(12)

        # ===== HEADER =====
        header_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        title_label = Gtk.Label(label=tr("import_title") or "Import Applications")
        title_label.add_css_class("title-2")
        title_label.set_xalign(0)
        header_box.append(title_label)

        subtitle = Gtk.Label(
            label=tr("import_subtitle")
            or "Scanning for installed applications..."
        )
        subtitle.add_css_class("dim-label")
        subtitle.set_xalign(0)
        subtitle.set_wrap(True)
        header_box.append(subtitle)
        box.append(header_box)

        # ===== CONTENT STACK (Spinner | Results) =====
        self.import_stack = Gtk.Stack()
        self.import_stack.set_transition_type(
            Gtk.StackTransitionType.CROSSFADE
        )
        self.import_stack.set_vexpand(True)
        self.import_stack.set_hexpand(True)

        # Page 1 : Spinner (en cours de scan)
        spinner_page = self._build_import_spinner_page()
        self.import_stack.add_named(spinner_page, "spinner")

        # Page 2 : Résultats (checkboxes + liste)
        results_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.import_stack.add_named(results_page, "results")

        self.import_stack.set_visible_child_name("spinner")
        box.append(self.import_stack)

        # ===== BUTTONS =====
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        self.import_cancel_btn = Gtk.Button(label=tr("cancel") or "Cancel")
        self.import_cancel_btn.add_css_class("alternative-action")
        self.import_cancel_btn.connect("clicked", lambda *_: win.close())

        self.import_start_btn = Gtk.Button(label=tr("import_start") or "Import")
        self.import_start_btn.add_css_class("suggested-action")
        self.import_start_btn.set_sensitive(False)
        self.import_start_btn.connect(
            "clicked", self._on_import_start_clicked, win, results_page
        )

        button_box.append(Gtk.Box(hexpand=True))  # spacer
        button_box.append(self.import_cancel_btn)
        button_box.append(self.import_start_btn)
        box.append(button_box)

        win.set_child(box)
        win.present()

        # Lance le scan en thread
        self._perform_import_scan(results_page)

    def _build_import_spinner_page(self):
        """Construit la page "en cours de scan"."""
        page = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=12,
            hexpand=True,
            vexpand=True,
        )
        page.set_halign(Gtk.Align.CENTER)
        page.set_valign(Gtk.Align.CENTER)

        spinner = Gtk.Spinner()
        spinner.set_size_request(48, 48)
        spinner.start()
        page.append(spinner)

        status = Gtk.Label(label=tr("scanning_apps") or "Scanning for applications...")
        status.add_css_class("dim-label")
        page.append(status)

        return page

    def _perform_import_scan(self, results_page):
        """Lance scan_all() en thread worker."""

        def worker():
            try:
                results = scan_all()
                GLib.idle_add(self._on_import_scan_complete, results, results_page)
            except Exception as e:
                logger.error(f"Import scan failed: {e}")
                GLib.idle_add(self._on_import_scan_error, str(e))

        threading.Thread(target=worker, daemon=True).start()

    def _on_import_scan_complete(self, results, results_page):
        """Remplit results_page avec les sources trouvées."""

        # Vérifier si au moins une source est disponible
        if not any_source_available(results):
            # Aucune source trouvée → dialog pour chemin personnalisé
            self._show_import_custom_path_dialog(results, results_page)
            return

        # Construire la liste des sources avec checkboxes
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_hexpand(True)
        scroll.set_min_content_height(250)

        list_box = Gtk.ListBox()
        list_box.set_selection_mode(Gtk.SelectionMode.NONE)
        list_box.add_css_class("import-results-list")

        self.import_checkboxes = {}  # {source_key: checkbox}

        for source, data in sorted(results.items()):
            items = data.get("items", [])
            if not items:
                continue

            # Créer une ligne pour cette source
            row = Gtk.ListBoxRow()
            row.set_activatable(False)

            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
            box.set_margin_top(8)
            box.set_margin_bottom(8)
            box.set_margin_start(12)
            box.set_margin_end(12)

            # Header : checkbox + label + count
            header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

            checkbox = Gtk.CheckButton()
            checkbox.set_active(True)  # coché par défaut
            self.import_checkboxes[source] = checkbox
            header.append(checkbox)

            icon = _IMPORT_ICONS.get(source, "📦")
            label_text = _IMPORT_LABELS.get(source, source)
            count = len(items)
            unit = "application" if count == 1 else "applications"

            label = Gtk.Label(label=f"{icon} {label_text}")
            label.set_xalign(0)
            label.add_css_class("import-source-title")
            label.set_hexpand(True)
            header.append(label)

            count_label = Gtk.Label(label=f"{count} {unit}")
            count_label.add_css_class("dim-label")
            header.append(count_label)

            box.append(header)

            # Liste des items pour cette source (petit texte gris)
            items_list = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            items_list.set_margin_start(32)  # indent sous le checkbox

            for item in sorted(items, key=lambda i: (i.get("name") or "").lower()):
                name = item.get("name") or "(unknown)"
                if item.get("needs_manual_exe"):
                    item_label = Gtk.Label(
                        label=f"  ⚠ {name}  (exe not detected)", xalign=0
                    )
                    item_label.add_css_class("dim-label")
                else:
                    item_label = Gtk.Label(label=f"  • {name}", xalign=0)
                    item_label.add_css_class("dim-label")
                item_label.set_wrap(True)
                items_list.append(item_label)

            box.append(items_list)
            row.set_child(box)
            list_box.append(row)

        scroll.set_child(list_box)

        # Vider results_page et ajouter le contenu
        for child in list(results_page.observe_children()):
            results_page.remove(child)

        results_page.append(scroll)
        results_page.show()

        # Passer au stack "results" et activer le bouton Import
        self.import_stack.set_visible_child_name("results")
        self.import_start_btn.set_sensitive(True)

        # Stocker les résultats pour utilisation dans _on_import_start_clicked
        self.import_scan_results = results

        return False

    def _show_import_custom_path_dialog(self, results, results_page):
        """Affiche un dialog pour entrer un chemin personnalisé de scan Wine."""

        dialog = Gtk.Window(
            transient_for=self.import_stack.get_root(),
            modal=True,
            title=tr("import_custom_path_title") or "Scan Custom Path",
        )
        dialog.set_default_size(400, 150)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        box.set_margin_start(12)
        box.set_margin_end(12)

        label = Gtk.Label(
            label=tr("import_custom_path_message")
            or "No applications found. Enter a path to scan:"
        )
        label.set_wrap(True)
        label.set_xalign(0)
        box.append(label)

        entry = Gtk.Entry()
        entry.set_placeholder_text(tr("import_path_placeholder") or "e.g., ~/Games")
        box.append(entry)

        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        btn_cancel = Gtk.Button(label=tr("cancel") or "Cancel")
        btn_cancel.connect("clicked", lambda *_: dialog.close())

        btn_scan = Gtk.Button(label=tr("import_scan") or "Scan")
        btn_scan.add_css_class("suggested-action")

        def on_scan_custom(*_):
            path = entry.get_text().strip()
            if not path:
                return
            dialog.close()
            # Relancer scan avec chemin perso
            self._perform_import_scan_custom(path, results_page)

        btn_scan.connect("clicked", on_scan_custom)

        button_box.append(Gtk.Box(hexpand=True))
        button_box.append(btn_cancel)
        button_box.append(btn_scan)
        box.append(button_box)

        dialog.set_child(box)
        dialog.present()

    def _perform_import_scan_custom(self, path, results_page):
        """Lance scan_wine_prefixes avec chemin perso."""

        def worker():
            try:
                # Relancer scan complet + chemin custom
                custom_results = scan_all(extra_paths={"wine": [path]})
                GLib.idle_add(
                    self._on_import_scan_complete, custom_results, results_page
                )
            except Exception as e:
                logger.error(f"Custom path scan failed: {e}")
                GLib.idle_add(self._on_import_scan_error, str(e))

        threading.Thread(target=worker, daemon=True).start()

    def _on_import_scan_error(self, error_msg):
        """Gère erreur de scan."""
        self.toast.error(
            tr("import_scan_error").format(error=error_msg)
            or f"Scan failed: {error_msg}"
        )
        return False

    def _on_import_start_clicked(self, btn, win, results_page):
        """Lance l'import des sources cochées."""

        # Collecter les sources cochées
        enabled_sources = {
            source for source, checkbox in self.import_checkboxes.items()
            if checkbox.get_active()
        }

        if not enabled_sources:
            self.toast.warning(
                tr("import_nothing_selected") or "Nothing selected to import"
            )
            return

        # Afficher spinner et lancer import en thread
        self.import_stack.set_visible_child_name("spinner")
        self.import_start_btn.set_sensitive(False)
        self.import_cancel_btn.set_sensitive(False)

        def worker():
            try:
                summary = import_selected(self.import_scan_results, enabled_sources)
                GLib.idle_add(
                    self._on_import_complete,
                    summary,
                    win,
                )
            except Exception as e:
                logger.error(f"Import failed: {e}")
                GLib.idle_add(self._on_import_error, str(e), win)

        threading.Thread(target=worker, daemon=True).start()

    def _on_import_complete(self, summary, win):
        """Affiche résultat et ferme dialog."""

        imported = summary.get("imported", 0)
        skipped = summary.get("skipped", 0)
        errors = summary.get("errors", [])

        message = (
            f"✓ {tr('import_result') or 'Import complete'}\n\n"
            f"  {tr('imported') or 'Imported'}: {imported}\n"
            f"  {tr('skipped') or 'Skipped'}: {skipped}\n"
        )

        if errors:
            message += f"\n  Errors: {len(errors)}\n"
            for err in errors[:3]:  # Show first 3 errors
                message += f"    • {err['exe']}\n"

        self.toast.info(message)
        logger.info(
            f"Import complete: {imported} imported, {skipped} skipped, {len(errors)} errors"
        )

        # Refersh the game list
        self.refresh_games()

        # Fermer le dialog
        win.close()

        return False

    def _on_import_error(self, error_msg, win):
        """Gère erreur d'import."""
        self.toast.error(
            tr("import_error").format(error=error_msg)
            or f"Import failed: {error_msg}"
        )
        logger.error(f"Import error: {error_msg}")

        # Revenir aux résultats
        self.import_stack.set_visible_child_name("results")
        self.import_start_btn.set_sensitive(True)
        self.import_cancel_btn.set_sensitive(True)

        return False
