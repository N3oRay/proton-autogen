# color_label.py — module déplacé vers proton_autogen/ux/color_label.py
"""
Compatibilité : la coloration de texte (Gtk.TextBuffer / Pango) est de
l'interface et vit désormais dans proton_autogen.ux.color_label. Ce relais
ré-exporte les mêmes fonctions sous les mêmes noms, pour ne casser aucun
import existant (y compris externe).

Nouveau code : importer depuis proton_autogen.ux.color_label.
"""

from proton_autogen.ux.color_label import (  # noqa: F401
    insert_changelog_text,
    insert_about_text,
    insert_sensor_text,
    insert_colored_text,
    colorize,
)
