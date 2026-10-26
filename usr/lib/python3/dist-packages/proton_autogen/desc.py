# desc.py — module déplacé vers proton_autogen/ux/desc.py
"""
Compatibilité : les info-bulles (descriptions) sont de l'interface et vivent
désormais dans proton_autogen.ux.desc. Ce relais ré-exporte les mêmes objets
sous les mêmes noms, pour ne casser aucun import existant (y compris externe).

Nouveau code : importer depuis proton_autogen.ux.desc.
"""

from proton_autogen.ux.desc import (  # noqa: F401
    _DESC_DIR,
    _DESC_PREFIX,
    _DESC_CACHE,
    _discover_available_desc_langs,
    AVAILABLE_DESC_LANGS,
    _load_desc_file,
    _get_desc_table,
    get_description,
    set_tooltip,
    set_tooltip_from_text,
    set_tooltip_if_available,
    apply_tooltips,
    has_description,
    list_keys,
    attach_tooltip,
    attach_tooltips,
)
