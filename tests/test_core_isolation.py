"""La couche métier ne dépend pas de l'interface — garde-fous d'architecture.

Importer proton_autogen.backend (donc aussi la CLI et les tests) ne doit :
  - ni importer un module de ux/ (couche interface) ;
  - ni créer / migrer le fichier de configuration de l'interface : cet effet de
    bord n'appartient qu'à ux/themes.py, chargé au démarrage de l'interface.
"""

import ast
import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

import proton_autogen

pytestmark = pytest.mark.unit

PACKAGE_DIR = Path(proton_autogen.__file__).resolve().parent

# Relais de compatibilité volontaires (anciens emplacements de modules déplacés
# dans ux/). Ils ne sont importés par aucun module métier.
COMPAT_SHIMS = {"color_label.py", "desc.py"}


def _ux_imports(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and (node.module or "").startswith("proton_autogen.ux"):
            found.append((node.lineno, node.module))
        elif isinstance(node, ast.Import):
            found += [(node.lineno, a.name) for a in node.names if a.name.startswith("proton_autogen.ux")]
    return found


def test_aucun_module_metier_n_importe_ux():
    violations = []

    for path in sorted(PACKAGE_DIR.rglob("*.py")):
        relative = path.relative_to(PACKAGE_DIR)

        if relative.parts[0] in ("ux", "locales") or relative.name in COMPAT_SHIMS and len(relative.parts) == 1:
            continue

        violations += [f"{relative}:{line} importe {module}" for line, module in _ux_imports(path)]

    assert violations == []


def test_importer_le_backend_ne_cree_pas_la_config_de_l_interface(tmp_path):
    code = textwrap.dedent("""
        import proton_autogen.backend  # noqa: F401
    """)
    env = {**os.environ, "HOME": str(tmp_path)}

    result = subprocess.run([sys.executable, "-c", code], env=env,
                            capture_output=True, text=True, timeout=60)

    assert result.returncode == 0, result.stderr
    ux_conf = tmp_path / ".config" / "proton-autogen" / "proton-autogen-ux.conf"
    assert not ux_conf.exists(), "importer backend a créé proton-autogen-ux.conf"
