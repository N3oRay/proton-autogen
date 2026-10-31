#!/usr/bin/env python3
# ux/text_engine.py
"""
Moteur de mise en forme de texte — SANS GTK.

Transforme un texte brut (aide, à propos, diagnostic, capteurs, changelog) en
LIGNES de « spans » : (texte, style sémantique). Aucun widget, aucune couleur :
seulement des rôles (« title », « ok », « temp_hot »...). Le rendu GTK
(ux/color_label.py) associe ensuite chaque rôle à une apparence (Look), claire ou
sombre selon le thème.

    parse_lines(texte, "generic") -> [[Span("Proton", "key"), Span(":", None), ...], ...]

Pourquoi cette séparation
-------------------------
- Les règles de reconnaissance (« cette ligne est un titre, un chemin, une
  température... ») sont déclaratives, listées dans l'ordre d'un PROFIL, et
  testables sans écran.
- Une seule palette pour toute l'application, avec une variante lisible sur
  fond clair (thèmes « cute » et « KDE »/givre, dont les dialogues sont clairs).
- Ajouter un type de texte = ajouter un profil, pas copier 150 lignes.

Les règles reprennent, dans le même ordre, celles des anciennes fonctions
insert_colored_text / insert_about_text / insert_sensor_text /
insert_changelog_text de color_label.py. Seuls changent : l'apparence (palette
unifiée et adaptée au fond), et la correction d'un défaut sur les lignes « ✓ »
indentées (voir _rule_about_check).
"""

import re
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Modèle
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Span:
    """Un morceau de ligne. style=None : texte non stylé (couleur de la vue)."""

    text: str
    style: Optional[str] = None


Line = List[Span]              # une ligne, sans son « \n » final
Rule = Callable[[str, str], Optional[Line]]   # (ligne, ligne.strip()) -> spans | None

_SEPARATOR_CHARS = {"─", "━"}


def _whole(style: Optional[str], test: Callable[[str], bool]) -> Rule:
    """Règle : si test(ligne_strippée), toute la ligne prend `style`."""

    def rule(line: str, stripped: str) -> Optional[Line]:
        return [Span(line, style)] if test(stripped) else None

    return rule


def _spans(*parts: Tuple[str, Optional[str]]) -> Line:
    """Construit une ligne en omettant les morceaux vides."""
    return [Span(text, style) for text, style in parts if text]


# ---------------------------------------------------------------------------
# Règles partagées
# ---------------------------------------------------------------------------

_is_separator = _whole("separator", lambda s: set(s) <= _SEPARATOR_CHARS)
_is_banner = _whole("accent", lambda s: re.match(r"^===.*===$", s) is not None)


def _temperature_rule(hot_at: float, warn_at: Optional[float], before: Optional[str],
                      after: Optional[str]) -> Rule:
    """Ligne contenant « 54.0 °C » : valeur colorée selon sa gravité."""

    def rule(line: str, stripped: str) -> Optional[Line]:
        match = re.search(r"(\d+\.\d+)\s*°C", line)
        if not match:
            return None

        value = float(match.group(1))
        if value >= hot_at:
            style = "temp_hot"
        elif warn_at is not None and value >= warn_at:
            style = "temp_warn"
        else:
            style = "temp_ok"

        return _spans(
            (line[:match.start()], before),
            (match.group(0), style),
            (line[match.end():], after),
        )

    return rule


# ---------------------------------------------------------------------------
# Profil « generic » (aide, diagnostic, prérequis, ProtonDB, MangoHud...)
# ---------------------------------------------------------------------------

_GENERIC_TITLES = ("PROTON-AUTOGEN", "PROTON-AUTOGEN - AIDE", "proton-autogen diagnostic")


def _rule_selected(line: str, stripped: str) -> Optional[Line]:
    if "[selected]" not in line:
        return None
    before, after = line.split("[selected]", 1)
    return _spans((before, None), ("[selected]", "selected"), (after, None))


def _rule_yes_no(line: str, stripped: str) -> Optional[Line]:
    if not re.search(r"\b(yes|no)\b", line):
        return None
    before, word, after = re.split(r"\b(yes|no)\b", line, maxsplit=1)
    return _spans((before, None), (word, "ok" if word == "yes" else "error"), (after, None))


def _rule_key_value(line: str, stripped: str) -> Optional[Line]:
    if ":" not in line:
        return None
    key, value = line.split(":", 1)
    return _spans((key, "key"), (":", None), (value, "value"))


_GENERIC_RULES: Tuple[Rule, ...] = (
    _is_separator,
    _whole("title", lambda s: s in _GENERIC_TITLES),
    _is_banner,
    _whole("section", lambda s: s.isupper() and len(s) > 2 and not s.startswith("PROTON")),
    _whole("env", lambda s: s in ("STEAM_COMPAT_DATA_PATH", "WINEPREFIX")),
    _temperature_rule(hot_at=70, warn_at=None, before=None, after="value"),
    _whole("link", lambda s: s.startswith(("http://", "https://"))),
    _whole("path", lambda s: s.startswith("/")),
    _rule_selected,
    _rule_yes_no,
    _whole("command", lambda s: s.startswith(("proton-autogen", "gamescope", "sudo "))),
    _whole("option", lambda s: s.startswith("--")),
    _whole("note", lambda s: s.startswith("- ")),
    _rule_key_value,
    _whole("proton", lambda s: False),     # remplacé ci-dessous (dépend de la ligne brute)
)


def _rule_proton(line: str, stripped: str) -> Optional[Line]:
    return [Span(line, "proton")] if ("Proton" in line or "GE-" in line) else None


_GENERIC_RULES = _GENERIC_RULES[:-1] + (_rule_proton,)


# ---------------------------------------------------------------------------
# Profil « about » (À propos)
# ---------------------------------------------------------------------------

_ABOUT_SECTIONS = {"POINTS FORTS", "AUTEUR", "LICENCE", "DÉPÔT GITHUB", "PPA"}


def _rule_about_check(line: str, stripped: str) -> Optional[Line]:
    """« ✓ texte » : coche en vert, texte normal.

    L'ancien code insérait « ✓ » puis line[1:] : sur une ligne indentée
    (« ␣␣✓ x »), il perdait l'indentation et dupliquait la coche. On découpe
    ici à la position réelle de la coche.
    """
    if not stripped.startswith("✓"):
        return None

    position = line.index("✓")
    return _spans((line[:position], None), ("✓", "check"), (line[position + 1:], "text"))


_ABOUT_RULES: Tuple[Rule, ...] = (
    _whole("title", lambda s: s == "PROTON-AUTOGEN"),
    _is_separator,
    _whole("section", lambda s: s in _ABOUT_SECTIONS),
    _rule_about_check,
    _whole("link", lambda s: s.startswith(("http://", "https://"))),
    _whole("command", lambda s: s.startswith("sudo ")),
    _whole("highlight", lambda s: s in ("N3oray", "MIT")),
)

# ---------------------------------------------------------------------------
# Profil « sensors » (capteurs)
# ---------------------------------------------------------------------------

_SENSORS_RULES: Tuple[Rule, ...] = (
    _is_banner,
    _is_separator,
    _temperature_rule(hot_at=80, warn_at=65, before="name", after="text"),
)

# ---------------------------------------------------------------------------
# Profil « changelog » (debian/changelog)
# ---------------------------------------------------------------------------

_IMPROVED = ("* Improved", "* Enhanced", "* Optimized", "* Refined")


def _rule_signature(line: str, stripped: str) -> Optional[Line]:
    if not stripped.startswith("--"):
        return None
    parts = line.split("  ", 1)
    if len(parts) > 1:
        return _spans((parts[0], "author"), ("  " + parts[1], "date"))
    return _spans((parts[0], "author"))


_CHANGELOG_RULES: Tuple[Rule, ...] = (
    _whole("title", lambda s: re.match(r"^proton-autogen\s+\([0-9.]+\)", s, re.IGNORECASE) is not None),
    _whole("added", lambda s: s.startswith("* Added")),
    _whole("text", lambda s: s.startswith(_IMPROVED)),
    _whole("fixed", lambda s: s.startswith("* Fixed")),
    _rule_signature,
)

# ---------------------------------------------------------------------------
# Profils
# ---------------------------------------------------------------------------

# profil -> (règles dans l'ordre, style des lignes qu'aucune règle ne reconnaît)
PROFILES: Dict[str, Tuple[Tuple[Rule, ...], Optional[str]]] = {
    "generic": (_GENERIC_RULES, None),
    "about": (_ABOUT_RULES, "text"),
    "sensors": (_SENSORS_RULES, None),
    "changelog": (_CHANGELOG_RULES, None),
}


def parse_line(line: str, profile: str) -> Line:
    """Spans d'UNE ligne (sans « \\n »). Ligne vide => liste vide."""
    rules, default_style = PROFILES[profile]
    stripped = line.strip()

    if not stripped:
        return []

    for rule in rules:
        spans = rule(line, stripped)
        if spans is not None:
            return spans

    return [Span(line, default_style)]


def parse_lines(text: str, profile: str) -> List[Line]:
    """Spans de chaque ligne de `text` (mêmes coupures que str.splitlines)."""
    return [parse_line(line, profile) for line in text.splitlines()]


def styles_used(profile: str) -> frozenset:
    """Rôles qu'un profil est susceptible d'émettre (pour créer les tags GTK)."""
    return PROFILE_STYLES[profile]


# ---------------------------------------------------------------------------
# Apparence : une palette pour toute l'application, claire et sombre
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Look:
    """Apparence d'un rôle. Les couleurs sont (sombre, clair) : celle à utiliser
    sur fond sombre, puis sur fond clair."""

    dark: str
    light: str
    bold: bool = False
    underline: bool = False
    monospace: bool = False
    scale: float = 1.0          # taille relative au texte de la vue
    above: int = 0              # pixels avant le paragraphe
    below: int = 0              # pixels après le paragraphe
    margin: int = 0             # marge gauche du paragraphe
    indent: int = 0             # retrait de la 1ʳᵉ ligne (négatif = retrait suspendu)

    def color(self, dark_background: bool) -> str:
        return self.dark if dark_background else self.light


# Couleurs « sombre » = celles historiques de l'application (aucun changement sur
# les thèmes sombres). Couleurs « clair » : même teinte, assombrie jusqu'à un
# contraste ≥ 4,5:1 sur blanc (vérifié par les tests).
_HANG = dict(margin=14, indent=-14)     # retrait suspendu : la suite d'une ligne longue s'aligne

LOOKS: Dict[str, Look] = {
    # Hiérarchie
    "title":     Look("#5fd7ff", "#007ba4", bold=True, scale=1.35, above=2, below=6),
    "section":   Look("#ffd75f", "#8f6c00", bold=True, scale=1.10, above=12, below=3),
    "accent":    Look("#c061cb", "#b23fbf", bold=True, above=8, below=2),
    "separator": Look("#77767b", "#77767b"),
    # Texte
    "text":      Look("#ffffff", "#1f2328"),
    "value":     Look("#ffffff", "#1f2328"),
    "key":       Look("#f9f06b", "#7c7405", bold=True, **_HANG),
    "highlight": Look("#f9f06b", "#7c7405"),
    "note":      Look("#f9f06b", "#7c7405", **_HANG),
    "name":      Look("#62a0ea", "#1c70d4"),
    # États
    "ok":        Look("#57e389", "#16833d"),
    "check":     Look("#57e389", "#16833d", bold=True, **_HANG),
    "error":     Look("#f66151", "#dd200b", bold=True),
    "selected":  Look("#ffbe6f", "#ac5e00", bold=True),
    "added":     Look("#57e389", "#16833d"),
    "fixed":     Look("#ffbe6f", "#ac5e00"),
    # Températures
    "temp_ok":   Look("#57e389", "#16833d", bold=True),
    "temp_warn": Look("#ffbe6f", "#ac5e00", bold=True),
    "temp_hot":  Look("#f66151", "#dd200b", bold=True),
    # Techniques
    "command":   Look("#57e389", "#16833d", monospace=True),
    "option":    Look("#62a0ea", "#1c70d4"),
    "link":      Look("#62a0ea", "#1c70d4", underline=True),
    "path":      Look("#99c1f1", "#1d70d4"),
    "proton":    Look("#33d17a", "#1d814a"),
    "env":       Look("#c061cb", "#b23fbf", bold=True),
    # Changelog
    "author":    Look("#c061cb", "#b23fbf"),
    "date":      Look("#99c1f1", "#1d70d4"),
}

# Rôles décoratifs : contraste minimal 3:1 (WCAG, éléments non textuels) ; les
# autres 4,5:1.
DECORATIVE_STYLES = frozenset({"separator"})

# Rôles émis par chaque profil (déduits des règles ci-dessus : un test vérifie
# que parse_lines n'émet jamais un rôle absent de cette table).
PROFILE_STYLES: Dict[str, frozenset] = {
    "generic": frozenset({
        "separator", "title", "accent", "section", "env", "temp_hot", "temp_ok", "value",
        "link", "path", "selected", "ok", "error", "command", "option", "note", "key", "proton",
    }),
    "about": frozenset({
        "title", "separator", "section", "check", "text", "link", "command", "highlight",
    }),
    "sensors": frozenset({"accent", "separator", "name", "temp_hot", "temp_warn", "temp_ok", "text"}),
    "changelog": frozenset({"title", "added", "text", "fixed", "author", "date"}),
}


# Fichiers CSS dont les dialogues ont un fond CLAIR (le fond de `.dialog-content`
# y est blanc ou presque). Un test relit les CSS et vérifie que cette liste est à jour.
LIGHT_THEME_FILES = frozenset({"style-cute.css", "style-givre.css"})


def is_light_theme_file(css_basename: str) -> bool:
    return css_basename in LIGHT_THEME_FILES


# ---------------------------------------------------------------------------
# Contraste (WCAG 2.x)
# ---------------------------------------------------------------------------

def relative_luminance(hex_color: str) -> float:
    value = hex_color.lstrip("#")
    r, g, b = (int(value[i:i + 2], 16) / 255 for i in (0, 2, 4))

    def linear(c: float) -> float:
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    return 0.2126 * linear(r) + 0.7152 * linear(g) + 0.0722 * linear(b)


def contrast_ratio(foreground: str, background: str) -> float:
    lighter, darker = sorted((relative_luminance(foreground), relative_luminance(background)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


# ---------------------------------------------------------------------------
# Sortie console (rich) — inchangée, déplacée ici pour s'importer sans Pango
# ---------------------------------------------------------------------------

def colorize(text: str):
    """Version rich (terminal) de la mise en forme « À propos ». Retourne un rich.Text."""
    from rich.text import Text

    t = Text()

    for line in text.splitlines():

        # Ligne vide
        if not line.strip():
            t.append("\n")
            continue

        # Titre principal
        if line == "PROTON-AUTOGEN":
            t.append(line, style="bold cyan")
            t.append("\n")
            continue

        # Séparateurs
        if set(line) == {"─"}:
            t.append(line, style="bright_black")
            t.append("\n")
            continue

        # Titres de section
        if line.isupper() and "─" not in line:
            t.append(line, style="bold yellow")
            t.append("\n")
            continue

        # URL
        if line.startswith("http"):
            t.append(line, style="underline blue")
            t.append("\n")
            continue

        # Commande
        if line.startswith("sudo "):
            t.append(line, style="green")
            t.append("\n")
            continue

        # Liste ✓
        if line.startswith("✓"):
            t.append("✓ ", style="green")
            t.append(line[2:])
            t.append("\n")
            continue

        # Texte normal
        t.append(line)
        t.append("\n")

    return t
