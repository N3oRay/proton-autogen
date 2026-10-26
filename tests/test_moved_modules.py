"""desc.py et color_label.py ont été déplacés dans ux/.

Les anciens emplacements (proton_autogen.desc / proton_autogen.color_label)
doivent rester utilisables : mêmes objets, mêmes noms.
"""

import os

import pytest

pytestmark = pytest.mark.unit

DESC_API = (
    "_DESC_DIR", "_DESC_PREFIX", "_DESC_CACHE", "_discover_available_desc_langs",
    "AVAILABLE_DESC_LANGS", "_load_desc_file", "_get_desc_table",
    "get_description", "set_tooltip", "set_tooltip_from_text",
    "set_tooltip_if_available", "apply_tooltips", "has_description",
    "list_keys", "attach_tooltip", "attach_tooltips",
)

COLOR_LABEL_API = (
    "insert_changelog_text", "insert_about_text", "insert_sensor_text",
    "insert_colored_text", "colorize",
)


# --- desc ------------------------------------------------------------------

def test_desc_relais_expose_les_memes_objets():
    from proton_autogen import desc as old
    from proton_autogen.ux import desc as new

    for name in DESC_API:
        assert getattr(old, name) is getattr(new, name), name


def test_desc_trouve_toujours_ses_fichiers_de_langue():
    # Garde-fou du déplacement : _DESC_DIR est calculé depuis __file__, il doit
    # pointer vers locales/ à la racine du paquet, pas vers ux/locales/.
    from proton_autogen.ux import desc

    assert os.path.isdir(desc._DESC_DIR)
    assert os.path.basename(os.path.dirname(desc._DESC_DIR)) == "proton_autogen"
    assert os.path.isfile(os.path.join(desc._DESC_DIR, "desc_en.json"))
    assert "en" in desc.AVAILABLE_DESC_LANGS


def test_desc_retourne_une_description_reelle():
    from proton_autogen.ux import desc

    keys = desc.list_keys("en")
    assert keys, "desc_en.json ne doit pas être vide"
    assert desc.has_description(keys[0], "en")
    assert desc.get_description(keys[0], "en")


def test_desc_ne_depend_pas_de_gtk():
    from proton_autogen.ux import desc

    assert not hasattr(desc, "Gtk")


# --- color_label (nécessite Pango) ------------------------------------------

@pytest.fixture
def color_modules():
    gi = pytest.importorskip("gi")
    try:
        import gi

        gi.require_version("Pango", "1.0")
        from gi.repository import Pango  # noqa: F401
    except ImportError:
        pytest.skip("Pango non disponible")

    from proton_autogen import color_label as old
    from proton_autogen.ux import color_label as new
    return old, new


def test_color_label_relais_expose_les_memes_fonctions(color_modules):
    old, new = color_modules
    for name in COLOR_LABEL_API:
        assert getattr(old, name) is getattr(new, name), name


def test_colorize_retourne_un_texte_rich(color_modules):
    from rich.text import Text

    _, new = color_modules
    assert isinstance(new.colorize("bonjour"), Text)
