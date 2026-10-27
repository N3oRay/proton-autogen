#!/usr/bin/env python3
# ux/css_perf.py
"""
« Effets visuels réduits » : allège un thème CSS au chargement — SANS GTK.

Les thèmes posent des ombres floues sur chaque ligne / carte de la liste de
jeux (`.game-container`, `.game-grid-card`...) et du texte lumineux sur chaque
titre et bouton de ligne (`text-shadow` flou). Ces effets sont recalculés pour
CHAQUE élément visible, et à chaque défilement ou zoom. Ce module les atténue,
uniquement quand l'utilisateur active « Effets visuels réduits » :

    - box-shadow des éléments répétés au repos : rayon de flou ramené à 6 px
      (décalage, étalement, couleur et `inset` conservés) ;
    - text-shadow flou (> 2 px) des titres / libellés répétés : supprimé.

Ce qui n'est JAMAIS modifié : les états transitoires (:hover, :active, :focus,
:checked — l'interaction garde son retour visuel), les fenêtres uniques
(dialogues, popovers, toasts : un seul exemplaire à l'écran), les @keyframes,
les @define-color, les commentaires et tout le reste du fichier (octet pour
octet). Les fichiers .css sur disque ne sont pas touchés : la transformation
se fait en mémoire, au chargement.

Un thème sans sélecteur ciblé (ex. cyberpunk-pro) ressort strictement identique.
"""

import configparser
import re
from typing import Iterable, List

from proton_autogen.ux.themes import CONFIG_PATH

# Rayon de flou maximal conservé pour les ombres de boîte ciblées (px).
MAX_BOX_BLUR = 6

# Au-delà de ce rayon (px), l'ombre de texte ciblée est supprimée. En dessous
# (1-2 px, simple détourage) elle reste : coût négligeable.
MAX_TEXT_BLUR = 2

# Sélecteurs EXACTS (un fragment de liste « a, b, c » à la fois) concernés.
# Choisis parce qu'ils existent en un exemplaire par jeu visible.
REPEATED_BOX_SELECTORS = frozenset({
    ".game-container",
    ".game-grid-card",
    ".game-grid-icon",
    ".recent-card",
    ".badge.addict",
    ".badge.favorite",
})

REPEATED_TEXT_SELECTORS = frozenset({
    ".title-4",
    ".dim-label2",
    "label.dim-label2",
    ".game-grid-title",
    ".btn-launch label",
    ".btn-edit label",
    ".btn-install label",
    ".btn-export label",
})

_RULE_RE = re.compile(r"(?P<selector>[^{}]*)\{(?P<body>[^{}]*)\}")
_COMMENT_RE = re.compile(r"/\*.*?\*/", re.S)
_DECL_RE = re.compile(
    r"(?<![-\w])(?P<prop>box-shadow|text-shadow)(?P<sep>\s*:\s*)(?P<value>[^;]+)",
)
_NUMBER_RE = re.compile(r"^-?\d+(?:\.\d+)?(?:px)?$")


# ---------------------------------------------------------------------------
# Ombres
# ---------------------------------------------------------------------------

def _split_top_level(text: str, separator: str) -> List[str]:
    """Découpe `text` sur `separator` en dehors des parenthèses."""
    parts, depth, current = [], 0, []

    for char in text:
        if char == "(":
            depth += 1
        elif char == ")":
            depth = max(0, depth - 1)

        if char == separator and depth == 0:
            parts.append("".join(current))
            current = []
        else:
            current.append(char)

    parts.append("".join(current))
    return parts


def _tokens(shadow: str):
    """(texte, début, fin) de chaque jeton séparé par des espaces, hors parenthèses."""
    result, depth, start = [], 0, None

    for index, char in enumerate(shadow):
        if char == "(":
            depth += 1
        elif char == ")":
            depth = max(0, depth - 1)

        if char.isspace() and depth == 0:
            if start is not None:
                result.append((shadow[start:index], start, index))
                start = None
        elif start is None:
            start = index

    if start is not None:
        result.append((shadow[start:], start, len(shadow)))

    return result


def _blur_token(shadow: str):
    """Jeton du rayon de flou : la 3ᵉ longueur (x, y, flou, [étalement])."""
    lengths = [t for t in _tokens(shadow) if _NUMBER_RE.match(t[0])]
    return lengths[2] if len(lengths) >= 3 else None


def _blur_value(shadow: str) -> float:
    token = _blur_token(shadow)
    return float(token[0].replace("px", "")) if token else 0.0


def max_blur(value: str) -> float:
    """Plus grand rayon de flou d'une valeur box-shadow / text-shadow."""
    if value.strip() in ("none", "inherit", "initial", "unset"):
        return 0.0
    return max((_blur_value(p) for p in _split_top_level(value, ",")), default=0.0)


def clamp_shadow_blur(value: str, limit: float = MAX_BOX_BLUR) -> str:
    """Ramène à `limit` px le flou de chaque ombre de `value`, sans toucher au
    reste (ordre, décalages, étalement, couleur, `inset`, espaces)."""
    if value.strip() in ("none", "inherit", "initial", "unset"):
        return value

    rewritten = []
    for shadow in _split_top_level(value, ","):
        token = _blur_token(shadow)

        if token and _blur_value(shadow) > limit:
            text, start, end = token
            number = f"{limit:g}"
            shadow = shadow[:start] + (number + "px" if text.endswith("px") else number) + shadow[end:]

        rewritten.append(shadow)

    return ",".join(rewritten)


# ---------------------------------------------------------------------------
# Thème
# ---------------------------------------------------------------------------

def _fragments(selector: str) -> List[str]:
    cleaned = _COMMENT_RE.sub("", selector)
    return [re.sub(r"\s+", " ", f).strip() for f in cleaned.split(",")]


def _rewrite_body(body: str, selectors: Iterable[str]) -> str:
    fragments = set(selectors)
    box = bool(fragments) and fragments <= REPEATED_BOX_SELECTORS
    text = bool(fragments) and fragments <= REPEATED_TEXT_SELECTORS

    if not (box or text):
        return body

    def replace(match):
        prop, value = match.group("prop"), match.group("value")

        if prop == "box-shadow" and box and max_blur(value) > MAX_BOX_BLUR:
            value = clamp_shadow_blur(value, MAX_BOX_BLUR)
        elif prop == "text-shadow" and text and max_blur(value) > MAX_TEXT_BLUR:
            value = "none"
        else:
            return match.group(0)

        trailing = match.group("value")[len(match.group("value").rstrip()):]
        return f"{prop}{match.group('sep')}{value.rstrip()}{trailing}"

    return _DECL_RE.sub(replace, body)


def optimize_css(css: str) -> str:
    """Retourne `css` avec les ombres coûteuses des éléments répétés allégées.

    Une règle dont la liste de sélecteurs mélange cibles et non-cibles n'est
    PAS modifiée (le changement toucherait aussi les non-cibles).
    """
    def rewrite(match):
        selector = match.group("selector")

        # @keyframes, @media... : leurs blocs imbriqués ne sont jamais ciblés.
        if "@" in _COMMENT_RE.sub("", selector):
            return match.group(0)

        body = _rewrite_body(match.group("body"), _fragments(selector))
        return f"{selector}{{{body}}}"

    return _RULE_RE.sub(rewrite, css)


def load_css_text(provider, css: str) -> None:
    """Charge `css` dans un Gtk.CssProvider (GTK >= 4.12 : load_from_string)."""
    try:
        provider.load_from_string(css)
    except AttributeError:
        provider.load_from_data(css.encode("utf-8"))


# ---------------------------------------------------------------------------
# Préférence [ui] reduced_effects (proton-autogen-ux.conf)
# ---------------------------------------------------------------------------

def load_reduced_effects(default: bool = False) -> bool:
    cfg = configparser.ConfigParser()

    if not CONFIG_PATH.exists():
        return default

    try:
        cfg.read(CONFIG_PATH)
        return cfg.getboolean("ui", "reduced_effects", fallback=default)
    except Exception:
        return default


def save_reduced_effects(enabled: bool) -> None:
    cfg = configparser.ConfigParser()

    if CONFIG_PATH.exists():
        try:
            cfg.read(CONFIG_PATH)
        except Exception:
            pass

    if "ui" not in cfg:
        cfg["ui"] = {}

    cfg["ui"]["reduced_effects"] = "true" if enabled else "false"

    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        cfg.write(f)
