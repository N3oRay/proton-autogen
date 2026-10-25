"""La couche métier et la CLI doivent fonctionner sans GTK.

On simule une machine sans GTK en rendant `gi.repository.Gtk` (et Gdk, Pango)
inimportables DANS UN SOUS-PROCESSUS : si un module du chemin CLI importe
encore GTK, l'import échoue ici, même sur une CI où GTK est installé.
"""

import os
import shutil
import subprocess
import sys
import textwrap

import pytest

pytestmark = pytest.mark.unit

_BLOCK_GTK = textwrap.dedent("""
    import sys
    for name in ("Gtk", "Gdk", "Pango"):
        sys.modules["gi.repository." + name] = None
""")

CORE_MODULES = (
    "config", "i18n", "loader", "core", "backend", "proton_call", "editor",
    "info", "diag", "import_scan", "pa_log", "notify", "desc", "stats",
    "session", "library", "status_text",
)


def _run(code, args=()):
    return subprocess.run(
        [sys.executable, "-c", _BLOCK_GTK + textwrap.dedent(code), *args],
        capture_output=True, text=True, timeout=60, env=os.environ.copy(),
    )


@pytest.mark.parametrize("module", CORE_MODULES)
def test_module_metier_s_importe_sans_gtk(module):
    result = _run(f"""
        import importlib, sys
        importlib.import_module("proton_autogen.{module}")
        loaded = [m for m in ("gi.repository.Gtk", "gi.repository.Gdk")
                  if sys.modules.get(m) is not None]
        assert not loaded, loaded
    """)
    assert result.returncode == 0, result.stderr


def test_pa_log_toast_importe_gtk_a_la_demande():
    # La seule fonction qui a besoin de GTK le fait elle-même : sans GTK,
    # elle échoue à l'appel, pas à l'import du module.
    result = _run("""
        from proton_autogen import pa_log
        try:
            pa_log._notify_toast({"title": "t", "message": "m"})
        except (ImportError, ValueError):
            # ImportError si GTK est installé mais bloqué ici, ValueError
            # (« Namespace Gtk not available ») s'il n'est pas installé.
            print("ImportError attendu")
    """)
    assert result.returncode == 0, result.stderr
    assert "ImportError attendu" in result.stdout


def test_notification_sans_callback_n_a_pas_besoin_de_glib():
    result = _run("""
        from proton_autogen.notify import NotificationCenter
        NotificationCenter().notify("info", "titre", "message")
    """)
    assert result.returncode == 0, result.stderr


@pytest.mark.skipif(shutil.which("proton-autogen") is None,
                    reason="commande proton-autogen non installée")
@pytest.mark.parametrize("flag", ["--help", "--about"])
def test_cli_demarre_sans_gtk(flag):
    cli = shutil.which("proton-autogen")
    result = _run("""
        import runpy, sys
        sys.argv = [sys.argv[1], sys.argv[2]]
        runpy.run_path(sys.argv[0], run_name="__main__")
    """, args=(cli, flag))
    assert result.returncode == 0, result.stderr
    assert "Traceback" not in result.stderr
