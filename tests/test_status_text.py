"""Tests de proton_autogen.status_text — purs, sans GTK."""

import pytest

from proton_autogen import status_text
from proton_autogen.status_text import cap_lines, clean_message, strip_ansi

pytestmark = pytest.mark.unit


def test_strip_ansi_retire_couleurs_curseur_et_titre_de_fenetre():
    raw = "\x1b[38;5;208mgamescope\x1b[0m \x1b]0;titre\x07ok\x1b[2K"
    assert strip_ansi(raw) == "gamescope ok"


def test_strip_ansi_garde_retours_ligne_et_tabulations():
    assert strip_ansi("a\tb\nc") == "a\tb\nc"


def test_strip_ansi_retire_les_caracteres_de_controle():
    assert strip_ansi("a\x00b\x07c") == "abc"


def test_clean_message_vide_ou_none():
    assert clean_message(None) == ("", "info")
    assert clean_message("   \n ") == ("", "info")
    assert clean_message("", level="warning") == ("", "warning")


def test_clean_message_normalise_fins_de_ligne_et_espaces():
    text, level = clean_message("\n\nligne 1  \r\nligne 2\rligne 3\n\n")
    assert text == "ligne 1\nligne 2\nligne 3"
    assert level == "info"


@pytest.mark.parametrize("message", [
    "error: boom", "Error something", "FATAL crash", "failed to start",
    "failure in module", "Traceback (most recent call last):",
    "stderr: oops",
])
def test_clean_message_detecte_le_niveau_error(message):
    assert clean_message(message)[1] == "error"


def test_clean_message_ne_detecte_que_le_debut_du_message():
    assert clean_message("tout va bien\nerror: plus loin")[1] == "info"


def test_clean_message_respecte_un_niveau_deja_fourni():
    assert clean_message("error: x", level="warning")[1] == "warning"


def test_clean_message_retire_le_prefixe_stderr():
    text, level = clean_message("stderr: wine: cannot find")
    assert text == "wine: cannot find"
    assert level == "error"
    assert clean_message("  STDERR :  x")[0] == "x"


def test_clean_message_ne_retire_pas_stderr_sans_deux_points():
    assert clean_message("stderrlog is fine")[0] == "stderrlog is fine"


def test_clean_message_supprime_l_ansi_avant_la_detection():
    text, level = clean_message("\x1b[31merror: rouge\x1b[0m")
    assert text == "error: rouge"
    assert level == "error"


def test_cap_lines_ne_touche_pas_un_texte_court():
    assert cap_lines("a\nb\nc", max_lines=3) == "a\nb\nc"


def test_cap_lines_plafonne_et_indique_le_nombre_de_lignes_masquees():
    result = cap_lines("\n".join(str(i) for i in range(10)), max_lines=4)
    lines = result.split("\n")
    assert lines[:4] == ["0", "1", "2", "3"]
    assert len(lines) == 5
    assert "6" in lines[4]          # 10 - 4 lignes masquées


def test_cap_lines_valeur_par_defaut():
    assert status_text.MAX_DISPLAY_LINES == 6
    long_text = "\n".join(str(i) for i in range(20))
    assert len(cap_lines(long_text).split("\n")) == status_text.MAX_DISPLAY_LINES + 1
