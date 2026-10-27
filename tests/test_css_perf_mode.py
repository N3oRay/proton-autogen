"""Mode « effets visuels réduits » (ux/css_perf.py) — sans GTK."""

import re
from pathlib import Path

import pytest

from proton_autogen.ux import css_perf
from proton_autogen.ux.css_perf import (
    MAX_BOX_BLUR,
    MAX_TEXT_BLUR,
    REPEATED_BOX_SELECTORS,
    REPEATED_TEXT_SELECTORS,
    clamp_shadow_blur,
    load_css_text,
    load_reduced_effects,
    max_blur,
    optimize_css,
    save_reduced_effects,
)

pytestmark = pytest.mark.unit

ASSETS_DIR = (
    Path(__file__).resolve().parents[1]
    / "usr/lib/python3/dist-packages/proton_autogen/ux/assets"
)


# --- clamp_shadow_blur / max_blur -------------------------------------------

@pytest.mark.parametrize("value,expected", [
    ("0 0 12px rgba(255,43,214,0.35)", "0 0 6px rgba(255,43,214,0.35)"),
    ("0 0 6px red", "0 0 6px red"),                                  # déjà ≤ limite
    ("0 0 3px red", "0 0 3px red"),
    ("none", "none"),
    ("0 4px 12px rgba(0,0,0,0.30)", "0 4px 6px rgba(0,0,0,0.30)"),   # décalage conservé
    ("2px 3px 20px 4px #fff", "2px 3px 6px 4px #fff"),               # étalement conservé
    ("inset 0 0 18px rgba(1,2,3,0.5)", "inset 0 0 6px rgba(1,2,3,0.5)"),
    ("0 0 12px @accent", "0 0 6px @accent"),                          # variable GTK
    ("0 0 12 red", "0 0 6 red"),                                      # sans unité
])
def test_clamp_une_ombre(value, expected):
    assert clamp_shadow_blur(value) == expected


def test_clamp_plusieurs_ombres_chacune_independamment():
    value = "0 0 20px rgba(1,2,3,0.5), 0 0 4px rgba(4,5,6,0.5), inset 0 0 10px #000"
    assert clamp_shadow_blur(value) == (
        "0 0 6px rgba(1,2,3,0.5), 0 0 4px rgba(4,5,6,0.5), inset 0 0 6px #000"
    )


def test_clamp_conserve_les_sauts_de_ligne_et_l_indentation():
    value = "\n        0 4px 12px rgba(0,0,0,0.30),\n        0 0 10px rgba(255,60,120,0.15)"
    assert clamp_shadow_blur(value) == (
        "\n        0 4px 6px rgba(0,0,0,0.30),\n        0 0 6px rgba(255,60,120,0.15)"
    )


def test_clamp_respecte_la_limite_demandee():
    assert clamp_shadow_blur("0 0 20px red", 10) == "0 0 10px red"


def test_max_blur():
    assert max_blur("0 0 12px red, 0 0 30px blue") == 30
    assert max_blur("0 0 0 1px red") == 0
    assert max_blur("none") == 0


# --- optimize_css : règles ciblées ------------------------------------------

def _opt(selector, declaration):
    css = f"{selector} {{\n    color: red;\n    {declaration}\n}}\n"
    return css, optimize_css(css)


def test_box_shadow_des_lignes_est_attenue():
    old, new = _opt(".game-container", "box-shadow: 0 0 24px rgba(0,240,255,0.4);")
    assert "box-shadow: 0 0 6px rgba(0,240,255,0.4);" in new
    assert "color: red;" in new


def test_text_shadow_flou_des_titres_est_supprime():
    _, new = _opt(".title-4", "text-shadow: 0 0 8px rgba(255,43,214,0.45);")
    assert "text-shadow: none;" in new


def test_text_shadow_leger_est_conserve():
    old, new = _opt(".game-grid-title", f"text-shadow: 0 1px {MAX_TEXT_BLUR}px #000;")
    assert new == old


@pytest.mark.parametrize("selector", [
    ".game-container:hover", ".game-container:active", ".game-grid-card:hover",
    ".game-container:focus-visible", ".btn-launch:hover label",
])
def test_les_etats_transitoires_ne_sont_jamais_modifies(selector):
    old, new = _opt(selector, "box-shadow: 0 0 28px red; text-shadow: 0 0 9px red;")
    assert new == old


@pytest.mark.parametrize("selector", [
    ".dialog-content", ".launch-dialog", ".toast-container", "popover contents",
    ".game-grid-context-popover", "entry:focus", ".main-header",
])
def test_fenetres_et_widgets_uniques_ne_sont_jamais_modifies(selector):
    old, new = _opt(selector, "box-shadow: 0 0 32px red;")
    assert new == old


def test_liste_de_selecteurs_toute_ciblee_est_modifiee():
    old, new = _opt(".btn-launch label,\n.btn-edit label", "text-shadow: 0 0 6px red;")
    assert "text-shadow: none;" in new


def test_liste_de_selecteurs_melangee_n_est_pas_modifiee():
    # Modifier la règle toucherait aussi `.dialog-content`, qui n'est pas ciblé.
    old, new = _opt(".game-container, .dialog-content", "box-shadow: 0 0 30px red;")
    assert new == old


def test_declaration_sans_point_virgule_final():
    css = ".game-container { box-shadow: 0 0 30px red }"
    assert optimize_css(css) == ".game-container { box-shadow: 0 0 6px red }"


def test_commentaire_avant_le_selecteur():
    css = "/* lignes */\n.game-container { box-shadow: 0 0 30px red; }"
    assert "0 0 6px red" in optimize_css(css)


def test_keyframes_et_define_color_intacts():
    css = (
        "@define-color accent #ff00aa;\n"
        "@keyframes pa-pulse {\n    0% { opacity: 0.70; }\n    100% { opacity: 1.00; }\n}\n"
        ".game-container { box-shadow: 0 0 30px @accent; }\n"
    )
    new = optimize_css(css)

    assert new.startswith(css.split(".game-container")[0])
    assert "0 0 6px @accent" in new


def test_idempotence():
    css = ".game-container { box-shadow: 0 0 30px red; }\n.title-4 { text-shadow: 0 0 9px red; }"
    once = optimize_css(css)
    assert optimize_css(once) == once


def test_css_sans_cible_ressort_identique():
    css = ".foo { box-shadow: 0 0 40px red; }\n@define-color a #fff;\n"
    assert optimize_css(css) == css


# --- sur les vrais thèmes ----------------------------------------------------

def _themes():
    files = sorted(ASSETS_DIR.glob("*.css"))
    assert files, f"Aucun thème dans {ASSETS_DIR}"
    return files


def _rules(text):
    return re.findall(r"[^{}]*\{[^{}]*\}", text)


def _selector_fragments(rule):
    selector = re.sub(r"/\*.*?\*/", "", rule.split("{")[0], flags=re.S)
    return {re.sub(r"\s+", " ", f).strip() for f in selector.split(",")}


@pytest.mark.parametrize("theme", _themes(), ids=lambda p: p.name)
class TestThemesReels:

    def test_idempotent_et_accolades_equilibrees(self, theme):
        css = theme.read_text(encoding="utf-8")
        once = optimize_css(css)

        assert optimize_css(once) == once
        assert once.count("{") == once.count("}") == css.count("{")

    def test_seules_les_regles_ciblees_changent(self, theme):
        css = theme.read_text(encoding="utf-8")
        before, after = _rules(css), _rules(optimize_css(css))

        assert len(before) == len(after)

        allowed = REPEATED_BOX_SELECTORS | REPEATED_TEXT_SELECTORS
        for old, new in zip(before, after):
            if old != new:
                assert _selector_fragments(old) <= allowed, old.strip()[:60]

    def test_apres_optimisation_plus_de_flou_excessif_sur_les_cibles(self, theme):
        for rule in _rules(optimize_css(theme.read_text(encoding="utf-8"))):
            fragments = _selector_fragments(rule)
            for prop, value in re.findall(
                r"(?<![-\w])(box-shadow|text-shadow)\s*:\s*([^;}]+)", rule
            ):
                if prop == "box-shadow" and fragments <= REPEATED_BOX_SELECTORS:
                    assert max_blur(value) <= MAX_BOX_BLUR, rule.strip()[:60]
                if prop == "text-shadow" and fragments <= REPEATED_TEXT_SELECTORS:
                    assert max_blur(value) <= MAX_TEXT_BLUR, rule.strip()[:60]

    def test_couleurs_definies_et_etats_hover_inchanges(self, theme):
        css = theme.read_text(encoding="utf-8")
        new = optimize_css(css)

        assert re.findall(r"@define-color[^;]+;", new) == re.findall(r"@define-color[^;]+;", css)
        assert [r for r in _rules(new) if ":hover" in r.split("{")[0]] == \
               [r for r in _rules(css) if ":hover" in r.split("{")[0]]

    def test_ne_grossit_jamais_le_fichier(self, theme):
        css = theme.read_text(encoding="utf-8")
        assert len(optimize_css(css).encode()) <= len(css.encode())


# --- chargement dans un provider --------------------------------------------

def test_load_css_text_utilise_load_from_string_si_disponible():
    calls = []

    class Modern:
        def load_from_string(self, text):
            calls.append(("string", text))

    load_css_text(Modern(), "a{}")
    assert calls == [("string", "a{}")]


def test_load_css_text_repli_sur_load_from_data():
    calls = []

    class Legacy:
        def load_from_data(self, data):
            calls.append(("data", data))

    load_css_text(Legacy(), "é{}")
    assert calls == [("data", "é{}".encode("utf-8"))]


# --- préférence --------------------------------------------------------------

@pytest.fixture
def conf(tmp_path, monkeypatch):
    path = tmp_path / "proton-autogen-ux.conf"
    monkeypatch.setattr(css_perf, "CONFIG_PATH", path)
    return path


def test_desactive_par_defaut(conf):
    assert load_reduced_effects() is False
    assert load_reduced_effects(default=True) is True


def test_aller_retour(conf):
    save_reduced_effects(True)
    assert load_reduced_effects() is True
    save_reduced_effects(False)
    assert load_reduced_effects() is False


def test_conserve_les_autres_reglages(conf):
    conf.write_text("[ui]\ntheme = gta\n[window]\nwidth = 900\n", encoding="utf-8")

    save_reduced_effects(True)

    content = conf.read_text(encoding="utf-8")
    assert "theme = gta" in content and "width = 900" in content
    assert load_reduced_effects() is True


def test_fichier_corrompu_renvoie_le_defaut(conf):
    conf.write_text("[ui\nreduced_effects = ???", encoding="utf-8")
    assert load_reduced_effects() is False
