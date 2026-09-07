import re
from pathlib import Path

ASSETS_DIR = Path("usr/lib/python3/dist-packages/proton_autogen/ux/assets")


HEX_RE = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")
RGBA_RE = re.compile(
    r"^rgba\(\s*(?:\d{1,3})\s*,\s*(?:\d{1,3})\s*,\s*(?:\d{1,3})\s*,\s*(?:0|1|0?\.\d+)\s*\)$",
    re.IGNORECASE,
)
DEFINE_RE = re.compile(r"@define-color\s+([A-Za-z0-9_-]+)\s+([^;]+);")
REFERENCE_RE = re.compile(r"@(?!define-color\b)([A-Za-z0-9_-]+)")

def find_css_files():
    if not ASSETS_DIR.exists():
        # Fail fast with helpful message in CI when path changed
        raise FileNotFoundError(f"Assets directory not found: {ASSETS_DIR}")
    return sorted(ASSETS_DIR.rglob("*.css"))

def parse_defines(text):
    defines = {}
    for m in DEFINE_RE.finditer(text):
        name = m.group(1)
        value = m.group(2).strip()
        defines.setdefault(name, []).append(value)
    return defines

def all_references(text):
    return set(m.group(1) for m in REFERENCE_RE.finditer(text))

def is_valid_value(value):
    # value can be an alias beginning with @, hex, rgba, or a color name (allow common keywords)
    if value.startswith("@"):
        return True
    if HEX_RE.match(value):
        return True
    if RGBA_RE.match(value):
        return True
    # allow simple css keywords like 'transparent' or 'none'
    if value.lower() in {"transparent", "none", "white", "black"}:
        return True
    # sometimes values include calc() or gradients: accept them conservatively
    if "(" in value or "gradient" in value.lower():
        return True
    return False

def test_define_color_values_and_no_duplicates():
    css_files = find_css_files()
    assert css_files, f"Aucun fichier .css trouvé dans {ASSETS_DIR}"
    errors = []
    for f in css_files:
        text = f.read_text(encoding="utf-8")
        defines = parse_defines(text)
        # duplicate detection: same name defined more than once in file
        for name, vals in defines.items():
            if len(vals) > 1:
                errors.append(f"Duplicate @define-color '{name}' in {f} (values: {vals})")
            else:
                val = vals[0]
                if not is_valid_value(val):
                    errors.append(f"Invalid value for @define-color '{name}' in {f}: '{val}'")
    if errors:
        raise AssertionError("\n".join(errors))

def test_references_resolve_to_defined_colors():
    css_files = find_css_files()

    # References that are intentionally allowed to be undefined
    ignored_refs = {"theme_fg_color"}

    # Build global set of defined names across all files
    global_defs = set()
    for f in css_files:
        text = f.read_text(encoding="utf-8")
        defines = parse_defines(text)
        global_defs.update(defines.keys())

    missing = []
    for f in css_files:
        text = f.read_text(encoding="utf-8")
        refs = all_references(text)
        for r in refs:
            if r in ignored_refs:
                continue
            if r not in global_defs:
                missing.append(f"Undefined color reference '@{r}' in {f}")

    if missing:
        raise AssertionError("\n".join(missing))


def test_basic_syntax_balanced_parentheses_and_quotes():
    css_files = find_css_files()
    bad = []
    for f in css_files:
        text = f.read_text(encoding="utf-8")
        if text.count("(") != text.count(")"):
            bad.append(f"Unbalanced parentheses in {f}")
        if text.count('"') % 2 != 0:
            bad.append(f"Unbalanced double quotes (\") in {f}")
        #if text.count("'") % 2 != 0:
        #    bad.append(f"Unbalanced single quotes (') in {f}")
    if bad:
        raise AssertionError("\n".join(bad))
