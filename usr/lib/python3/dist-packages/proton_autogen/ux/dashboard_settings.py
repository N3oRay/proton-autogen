#!/usr/bin/env python3

# dashboard_settings.py
"""
Panneau de réglages unique (pas un assistant multi-étapes), accessible
à tout moment via le menu de l'application (app.settings). Regroupe :

  - Apparence : thème, langue (appliquée au prochain lancement),
    mémorisation de la taille de fenêtre
  - Proton : chemins personnalisés, dossier racine des préfixes

DashboardSettingsMixin doit être mixé avec Dashboard : il utilise
self.toast, self.status, self.lang, self.get_application(),
self.get_width()/get_height() et self.update_background() (déjà
fournis par Dashboard / les autres mixins).
"""

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

from proton_autogen.i18n import tr, AVAILABLE_LANGS
from proton_autogen.ux.themes import (
    AVAILABLE_THEMES,
    load_saved_theme,
    load_saved_language,
    save_language,
    load_remember_window_size,
    save_remember_window_size,
    save_window_size,
)
from proton_autogen.config import (
    load_proton_paths_raw,
    save_proton_paths,
    load_prefix_dir,
    save_prefix_dir,
)


# Noms affichés pour les langues disponibles (repli sur le code brut
# si une langue n'a pas d'entrée ici — n'empêche jamais l'affichage).
_LANG_LABELS = {
    "en": "English",
    "fr": "Français",
    "de": "Deutsch",
    "es": "Español",
    "it": "Italiano",
    "pt": "Português",
    "nl": "Nederlands",
    "pl": "Polski",
    "ru": "Русский",
    "uk": "Українська",
    "ja": "日本語",
    "ko": "한국어",
    "zh": "中文",
    "hi": "हिन्दी",
    "el": "Ελληνικά",
    "fi": "Suomi",
    "vi": "Tiếng Việt",
    "bg": "Български",
}


class DashboardSettingsMixin:

    # -------------------------
    # DIALOG
    # -------------------------
    def show_settings_dialog(self):
        win = Gtk.Window(
            title=tr("settings_title"),
            transient_for=self,
            modal=True,
        )
        win.set_default_size(560, 520)
        win.add_css_class("settings-dialog")

        root = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=14,
            margin_top=20,
            margin_bottom=20,
            margin_start=20,
            margin_end=20,
        )

        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_child(root)

        # -------------------------
        # APPARENCE
        # -------------------------
        root.append(self._settings_section_title(tr("settings_section_appearance")))

        theme_dropdown = Gtk.DropDown.new_from_strings(AVAILABLE_THEMES)
        current_theme = load_saved_theme()
        if current_theme in AVAILABLE_THEMES:
            theme_dropdown.set_selected(AVAILABLE_THEMES.index(current_theme))
        root.append(self._settings_row(tr("settings_theme"), theme_dropdown))

        #lang_codes = sorted(AVAILABLE_LANGS)

        lang_codes = sorted(
                    code for code in AVAILABLE_LANGS
                    if (
                        isinstance(code, str)
                        and len(code) == 2
                        and code.isalpha()
                    )
                )

        lang_labels = [_LANG_LABELS.get(code, code) for code in lang_codes]
        lang_dropdown = Gtk.DropDown.new_from_strings(lang_labels)
        current_lang = load_saved_language() or self.lang
        if current_lang in lang_codes:
            lang_dropdown.set_selected(lang_codes.index(current_lang))
        root.append(self._settings_row(tr("settings_language"), lang_dropdown))

        remember_size_check = Gtk.CheckButton(label=tr("settings_remember_window_size"))
        remember_size_check.add_css_class("feature-toggle")
        remember_size_check.set_active(load_remember_window_size())
        root.append(remember_size_check)

        # -------------------------
        # PROTON
        # -------------------------
        root.append(self._settings_section_title(tr("settings_section_proton")))

        paths_label = Gtk.Label(label=tr("settings_proton_paths"), xalign=0)
        paths_label.add_css_class("form-label")
        root.append(paths_label)

        existing_paths = load_proton_paths_raw()
        paths_buffer = Gtk.TextBuffer()
        paths_buffer.set_text("\n".join(existing_paths))

        paths_view = Gtk.TextView(buffer=paths_buffer)
        paths_view.set_monospace(True)
        paths_view.add_css_class("editor-env-view")

        paths_scroll = Gtk.ScrolledWindow()
        paths_scroll.set_min_content_height(90)
        paths_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        paths_scroll.set_child(paths_view)
        root.append(paths_scroll)

        prefix_entry = Gtk.Entry()
        prefix_entry.set_hexpand(True)
        prefix_entry.set_text(load_prefix_dir())
        root.append(self._settings_row(tr("settings_prefix_dir"), prefix_entry))

        # -------------------------
        # BOUTONS
        # -------------------------
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        btn_box.set_halign(Gtk.Align.END)

        cancel_btn = Gtk.Button(label=tr("cancel"))
        cancel_btn.add_css_class("alternative-action")
        cancel_btn.connect("clicked", lambda *_: win.close())

        save_btn = Gtk.Button(label=tr("save_configuration"))
        save_btn.add_css_class("suggested-action")
        save_btn.connect(
            "clicked",
            lambda *_: self._on_settings_save(
                win,
                AVAILABLE_THEMES[theme_dropdown.get_selected()],
                lang_codes[lang_dropdown.get_selected()],
                remember_size_check.get_active(),
                paths_buffer.get_text(
                    paths_buffer.get_start_iter(),
                    paths_buffer.get_end_iter(),
                    False,
                ),
                prefix_entry.get_text(),
            ),
        )

        btn_box.append(cancel_btn)
        btn_box.append(save_btn)

        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        container.append(scroll)
        container.append(btn_box)

        win.set_child(container)
        win.present()

    # -------------------------
    # HELPERS UI
    # -------------------------
    def _settings_section_title(self, text):
        label = Gtk.Label(label=text, xalign=0)
        label.add_css_class("title-4")
        return label

    def _settings_row(self, label_text, widget):
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        label = Gtk.Label(label=label_text, xalign=0)
        label.set_width_chars(16)
        label.add_css_class("form-label")
        row.append(label)
        row.append(widget)
        return row

    # -------------------------
    # SAVE
    # -------------------------
    def _on_settings_save(self, win, theme, lang, remember_size, raw_paths, prefix_dir):
        # Thème : application immédiate (CSS + fond), même mécanisme que
        # ProtonAutogenApp.cycle_style() déjà existant.
        app = self.get_application()
        if app is not None and hasattr(app, "apply_style"):
            app.apply_style(theme)
        if hasattr(self, "update_background"):
            self.update_background(theme)

        # Langue : sauvegardée, mais appliquée seulement au prochain
        # lancement de l'application — retraduire à chaud l'ensemble des
        # widgets déjà construits (menus, labels, tooltips...) impliquerait
        # de reconstruire toute l'UI, hors périmètre de ce panneau.
        previous_lang = load_saved_language() or self.lang
        lang_changed = lang != previous_lang
        save_language(lang)

        # Taille de fenêtre mémorisée
        save_remember_window_size(remember_size)
        if remember_size:
            save_window_size(self.get_width(), self.get_height())

        # Chemins Proton personnalisés (un par ligne dans le champ)
        save_proton_paths(raw_paths.splitlines())

        # Dossier racine des préfixes
        save_prefix_dir(prefix_dir)

        win.close()

        if lang_changed:
            self.toast.info(tr("settings_restart_required"))
            self.status.set_text(tr("settings_restart_required"))
        else:
            self.toast.success(tr("settings_saved"))
            self.status.set_text(tr("settings_saved"))
