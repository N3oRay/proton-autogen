#!/usr/bin/env python3
# dashboard_shortcuts.py
"""
Fenêtre récapitulative des raccourcis clavier.

Objectif : rendre les raccourcis clavier de l'application découvrables
sans avoir à lire le code source ou à deviner. Ouverture via le menu
("Raccourcis clavier") ou Ctrl+?/Ctrl+/.

On construit une fenêtre "maison" (ScrolledWindow + ListBox) plutôt
qu'un Gtk.ShortcutsWindow : ce dernier est prévu pour être défini via
Gtk.Builder/XML et se comporte de façon peu prévisible construit à la
main en Python — une simple liste est plus robuste et plus facile à
maintenir au fil des ajouts de raccourcis.

Chaque nouveau raccourci ajouté ailleurs dans l'app (dashboard.py,
game_grid.py, recent_carousel.py...) doit être répercuté dans
SHORTCUTS_SECTIONS ci-dessous pour rester découvrable.
"""

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk
from proton_autogen.i18n import tr


# (clé de section, [(raccourci affiché, clé de description ou texte brut), ...])
#
# Les clés `tr(...)` utilisées ici sont nouvelles et doivent être
# ajoutées aux 16 fichiers de locale pour une traduction complète.
# En attendant, `tr(key) or fallback` retombe sur un texte français
# lisible plutôt que de planter ou d'afficher la clé brute.
SHORTCUTS_SECTIONS = [
    ("shortcuts_group_general", [
        ("Ctrl+,", "menu_settings", "Réglages"),
        ("F1", "menu_help", "Aide"),
        ("F2", "menu_sensors", "Capteurs"),
        ("F3", "menu_help_mangohud", "Aide MangoHud"),
        ("F4", "menu_requirements", "Prérequis"),
        ("F5", "menu_about_proton", "À propos de Proton"),
        ("F6", "menu_about", "À propos"),
        ("Ctrl+D", "menu_diagnostics", "Diagnostic"),
        ("Ctrl+? ou Ctrl+/", "menu_shortcuts", "Cette fenêtre"),
    ]),
    ("shortcuts_group_grid", [
        ("Ctrl+ + (ou Ctrl+=)", "shortcuts_grid_zoom_in", "Agrandir les icônes"),
        ("Ctrl+ -", "shortcuts_grid_zoom_out", "Réduire les icônes"),
        ("Tab / Maj+Tab", "shortcuts_grid_tab", "Passer d'un jeu au suivant/précédent"),
        ("Entrée ou Espace", "shortcuts_grid_launch", "Lancer le jeu sélectionné"),
        ("Touche Menu ou Maj+F10", "shortcuts_grid_menu", "Ouvrir le menu du jeu (Modifier, ProtonDB, Supprimer…)"),
    ]),
    ("shortcuts_group_carousel", [
        ("← / →", "shortcuts_carousel_move", "Page précédente / suivante"),
        ("Origine / Fin", "shortcuts_carousel_first_last", "Première / dernière page"),
        ("Page préc. / Page suiv.", "shortcuts_carousel_page", "Reculer / avancer de plusieurs cartes"),
    ]),
]


class DashboardShortcutsMixin:

    def show_shortcuts_window(self):
        """Affiche un aperçu de tous les raccourcis clavier de
        l'application. Reconstruite à chaque ouverture (pas de cache)
        pour refléter la langue courante si elle a changé entre-temps."""

        window = Gtk.Window(
            title=tr("shortcuts_title") or "Raccourcis clavier",
            transient_for=self,
            modal=True,
            default_width=460,
            default_height=520,
        )
        window.add_css_class("shortcuts-window")

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_vexpand(True)

        root = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=18,
            margin_top=18,
            margin_bottom=18,
            margin_start=18,
            margin_end=18,
        )

        for section_key, rows in SHORTCUTS_SECTIONS:
            root.append(self._build_shortcuts_section(section_key, rows))

        scroll.set_child(root)
        window.set_child(scroll)
        window.present()

    # -------------------------
    # UI HELPERS
    # -------------------------
    def _build_shortcuts_section(self, section_key, rows):
        default_titles = {
            "shortcuts_group_general": "Général",
            "shortcuts_group_grid": "Vue grille",
            "shortcuts_group_carousel": "Carrousels (récents / favoris)",
        }

        section_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=6,
        )

        title = Gtk.Label(
            label=tr(section_key) or default_titles.get(section_key, section_key),
            xalign=0,
        )
        title.add_css_class("title-4")
        section_box.append(title)

        listbox = Gtk.ListBox()
        listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        listbox.add_css_class("shortcuts-list")

        for accel_display, desc_key, desc_fallback in rows:
            listbox.append(
                self._build_shortcut_row(accel_display, desc_key, desc_fallback)
            )

        section_box.append(listbox)
        return section_box

    @staticmethod
    def _build_shortcut_row(accel_display, desc_key, desc_fallback):
        description_text = tr(desc_key) or desc_fallback

        row_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=12,
            margin_top=6,
            margin_bottom=6,
            margin_start=10,
            margin_end=10,
        )

        description = Gtk.Label(label=description_text, xalign=0)
        description.set_hexpand(True)
        description.set_wrap(True)

        accel_label = Gtk.Label(label=accel_display)
        accel_label.add_css_class("shortcut-key")
        accel_label.set_halign(Gtk.Align.END)

        row_box.append(description)
        row_box.append(accel_label)

        # Accessibilité : la ligne entière est lue d'une traite par un
        # lecteur d'écran ("Réglages : Ctrl+virgule") plutôt que deux
        # labels indépendants sans lien explicite entre eux.
        row_box.update_property(
            [Gtk.AccessibleProperty.LABEL],
            [f"{description_text} : {accel_display}"],
        )

        return row_box
