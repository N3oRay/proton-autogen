#!/usr/bin/env python3

# dashboard_bottles.py
"""
« Exporter vers Bottles » : fenêtre de choix de la bouteille, puis ajout du jeu
à ses programmes (la logique est dans utils/bottles_export.py).

  - aucune bouteille trouvée -> message
  - sinon -> liste des bouteilles (natives et Flatpak, la première est
    présélectionnée), « Exporter » / « Annuler »

Le résultat est annoncé par un toast : ajouté, déjà présent, ou erreur, avec
les avertissements utiles (Bottles ouvert, Flatpak).
"""

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Pango

from proton_autogen.i18n import tr
from proton_autogen.ux.dialogs import show_message
from proton_autogen.utils import bottles_export
from proton_autogen.utils.logger import StructuredLogger

logger = StructuredLogger("proton-autogen.ux.dashboard_bottles")

_WARNING_KEYS = {
    bottles_export.WARNING_BOTTLES_RUNNING: "export_bottles_running",
    bottles_export.WARNING_FLATPAK_SANDBOX: "export_bottles_flatpak",
}


def describe_result(result, game_name):
    """(type de toast, message, avertissements traduits) pour un ExportResult."""
    params = {"game": game_name, "bottle": result.bottle.name}
    if result.status == "added":
        kind, message = "success", tr("export_bottles_done", **params)
    else:
        kind, message = "info", tr("export_bottles_already", **params)
    warnings = [tr(_WARNING_KEYS[code]) for code in result.warnings if code in _WARNING_KEYS]
    return kind, message, warnings


class DashboardBottlesMixin:
    """Action « Exporter vers Bottles » du Dashboard (utilise self.toast)."""

    def export_bottles_handler(self, game):
        name = game.get("name", "?")
        try:
            bottles_export.build_program(game)   # échoue tôt si l'exécutable manque
            bottles = bottles_export.list_bottles()
        except bottles_export.BottlesExportError as exc:
            self._bottles_report_error(exc)
            return

        if not bottles:
            show_message(self, tr("export_bottles"), tr("export_bottles_none"))
            return
        self._show_bottles_chooser(game, name, bottles)

    # -- fenêtre de choix ---------------------------------------------------------

    def _show_bottles_chooser(self, game, name, bottles):
        window = Gtk.Window(
            title=tr("export_bottles"),
            transient_for=self,
            modal=True,
            default_width=460,
            resizable=False,
        )
        window.add_css_class("bottles-export-window")

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12,
                       margin_top=20, margin_bottom=20, margin_start=20, margin_end=20)
        root.append(Gtk.Label(label=tr("export_bottles_intro", game=name),
                              wrap=True, xalign=0))

        listbox = Gtk.ListBox()
        listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        listbox.add_css_class("boxed-list")
        rows = {}
        for bottle in bottles:
            row = Gtk.ListBoxRow()
            row_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2,
                              margin_top=8, margin_bottom=8, margin_start=12, margin_end=12)
            title = Gtk.Label(label=bottle.name, xalign=0)
            title.add_css_class("heading")
            detail = Gtk.Label(label=f"{bottle.source} — {bottle.directory}",
                               xalign=0, ellipsize=Pango.EllipsizeMode.MIDDLE)
            detail.add_css_class("dim-label")
            row_box.append(title)
            row_box.append(detail)
            row.set_child(row_box)
            listbox.append(row)
            rows[row] = bottle
        root.append(listbox)

        buttons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12,
                          halign=Gtk.Align.END)
        cancel = Gtk.Button(label=tr("cancel"))
        export = Gtk.Button(label=tr("export_bottles_button"))
        export.add_css_class("suggested-action")
        export.set_sensitive(False)
        buttons.append(cancel)
        buttons.append(export)
        root.append(buttons)

        def on_selected(_listbox, row):
            export.set_sensitive(row is not None)

        listbox.connect("row-selected", on_selected)
        cancel.connect("clicked", lambda _b: window.close())
        export.connect("clicked", lambda _b: self._bottles_do_export(
            window, game, name, rows.get(listbox.get_selected_row())))

        # Première bouteille présélectionnée : GTK sélectionnerait de toute façon la
        # première ligne au focus, autant que ce soit explicite (et prévisible).
        listbox.select_row(next(iter(rows)))

        window.set_child(root)
        window.present()

    # -- export ---------------------------------------------------------------------

    def _bottles_do_export(self, window, game, name, bottle):
        if bottle is None:
            return
        try:
            result = bottles_export.export_game_to_bottle(game, bottle)
        except bottles_export.BottlesExportError as exc:
            window.close()
            self._bottles_report_error(exc)
            return

        window.close()
        kind, message, warnings = describe_result(result, name)
        logger.info(f"Export Bottles : {message}")
        getattr(self.toast, kind)(message)
        for warning in warnings:
            self.toast.warning(warning)

    def _bottles_report_error(self, exc):
        message = tr("export_bottles_failed", error=str(exc))
        logger.error(message)
        self.toast.error(message)
