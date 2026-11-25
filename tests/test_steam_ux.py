"""Tests du menu UX « Configuration Steam » (dashboard_steam.py).

GTK n'est pas nécessaire : `gi` est simulé pour importer le module, puis on
exerce la vraie logique du mixin (statut, installation, confirmations,
désinstallation, action de menu) avec de faux widgets.
"""

import ast
import importlib
import json
import re
import sys
from pathlib import Path
from unittest import mock

import pytest

from proton_autogen import steam_compat as sc
from proton_autogen.i18n import tr

PKG = Path(sc.__file__).resolve().parent
UX_MODULES = ("proton_autogen.ux.dashboard_steam", "proton_autogen.ux.dialogs",
              "proton_autogen.ux.dashboard_status")


@pytest.fixture
def ux(monkeypatch):
    """Importe dashboard_steam avec un `gi` simulé, puis nettoie sys.modules."""
    monkeypatch.setitem(sys.modules, "gi", mock.MagicMock())
    monkeypatch.setitem(sys.modules, "gi.repository", mock.MagicMock())
    for name in UX_MODULES:
        sys.modules.pop(name, None)
    module = importlib.import_module("proton_autogen.ux.dashboard_steam")
    yield module
    for name in UX_MODULES:
        sys.modules.pop(name, None)


@pytest.fixture
def steam_home(tmp_path, monkeypatch):
    """HOME factice avec Steam présent et un lanceur proton-autogen."""
    home = tmp_path / "home"
    (home / ".steam" / "root").mkdir(parents=True)
    monkeypatch.setenv("HOME", str(home))
    launcher = tmp_path / "proton-autogen"
    launcher.write_text("#!/bin/sh\n")
    launcher.chmod(0o755)
    monkeypatch.setenv("PROTON_AUTOGEN_BIN", str(launcher))
    return home


@pytest.fixture
def host(ux, steam_home):
    class Host(ux.DashboardSteamMixin):
        pass

    h = Host()
    h.status = mock.MagicMock()
    h.ctx = {name: mock.MagicMock() for name in (
        "window", "status_label", "path_label", "result_label",
        "install_button", "uninstall_button")}
    return h


def answer_confirm(ux, monkeypatch, ok):
    """Remplace show_confirm : répond ok/non et mémorise le message affiché."""
    asked = []

    def fake(_parent, _title, message, callback):
        asked.append(message)
        callback(ok)

    monkeypatch.setattr(ux, "show_confirm", fake)
    return asked


def last_text(label):
    return label.set_text.call_args[0][0]


# --- logique pure ----------------------------------------------------------------- #

def make_status(**kw):
    base = dict(steam_found=True, tools_dir=Path("/t"), dest=Path("/t/Proton-Autogen"),
                installed=False, problems=[])
    base.update(kw)
    return sc.SteamStatus(**base)


def test_status_view_covers_every_state(ux):
    assert ux.status_view(make_status(steam_found=False)) == (
        "error", tr("steam_status_no_steam"))
    assert ux.status_view(make_status()) == ("warning", tr("steam_status_not_installed"))
    assert ux.status_view(make_status(installed=True)) == (
        "success", tr("steam_status_installed"))
    css, text = ux.status_view(make_status(installed=True, problems=["not executable: proton"]))
    assert css == "error"
    assert tr("steam_status_invalid") in text and "not executable: proton" in text


# --- installation ------------------------------------------------------------------ #

def test_install_from_the_menu(host, ux, monkeypatch):
    asked = answer_confirm(ux, monkeypatch, True)
    host._steam_on_install(host.ctx)
    assert asked == []  # rien à confirmer pour une première installation
    assert sc.get_status().healthy
    assert last_text(host.ctx["result_label"]) == tr("steam_installed_ok")
    host.ctx["install_button"].set_label.assert_called_with(tr("steam_reinstall"))
    host.ctx["uninstall_button"].set_sensitive.assert_called_with(True)
    host.status.set_text.assert_called_with(tr("steam_installed_ok"))


def test_reinstall_over_a_modified_file_asks_first(host, ux, monkeypatch):
    host._steam_on_install(host.ctx)
    manifest = sc.get_status().dest / "toolmanifest.vdf"
    manifest.write_text("custom\n")

    asked = answer_confirm(ux, monkeypatch, False)
    host._steam_on_install(host.ctx)
    assert len(asked) == 1 and "toolmanifest.vdf" in asked[0]
    assert manifest.read_text() == "custom\n"  # refus : rien n'est écrasé

    answer_confirm(ux, monkeypatch, True)
    host._steam_on_install(host.ctx)
    assert sc.get_status().healthy
    assert list(manifest.parent.glob("toolmanifest.vdf.bak-*"))  # sauvegarde


def test_install_error_is_reported_not_raised(host, ux, steam_home, monkeypatch):
    monkeypatch.delenv("PROTON_AUTOGEN_BIN")
    monkeypatch.setattr(sc.shutil, "which", lambda _n: None)
    monkeypatch.setattr(sc.sys, "argv", ["not-the-launcher"])
    host._steam_on_install(host.ctx)
    text = last_text(host.ctx["result_label"])
    assert text.startswith(tr("steam_error", error="").split(":")[0])
    assert not sc.get_status().installed
    host.status.set_text.assert_not_called()  # une erreur ne passe pas par la barre d'état


def test_buttons_disabled_when_steam_is_missing(host, tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path / "nohome"))
    host._steam_refresh(host.ctx)
    host.ctx["install_button"].set_sensitive.assert_called_with(False)
    host.ctx["uninstall_button"].set_sensitive.assert_called_with(False)


# --- désinstallation --------------------------------------------------------------- #

def test_uninstall_from_the_menu(host, ux, monkeypatch):
    host._steam_on_install(host.ctx)
    dest = sc.get_status().dest

    asked = answer_confirm(ux, monkeypatch, False)
    host._steam_on_uninstall(host.ctx)
    assert asked == [tr("steam_confirm_uninstall")]
    assert sc.get_status().healthy  # refus : toujours installé

    answer_confirm(ux, monkeypatch, True)
    host._steam_on_uninstall(host.ctx)
    assert not dest.exists()
    assert last_text(host.ctx["result_label"]) == tr("steam_uninstalled_ok")
    host.ctx["uninstall_button"].set_sensitive.assert_called_with(False)
    host.ctx["install_button"].set_label.assert_called_with(tr("steam_install"))


def test_uninstall_reports_what_was_kept(host, ux, monkeypatch):
    host._steam_on_install(host.ctx)
    (sc.get_status().dest / "user_settings.py").write_text("X = 1\n")
    answer_confirm(ux, monkeypatch, True)
    host._steam_on_uninstall(host.ctx)
    assert last_text(host.ctx["result_label"]) == tr(
        "steam_uninstalled_kept", files="user_settings.py")


def test_uninstall_error_is_reported_not_raised(host, ux, monkeypatch):
    foreign = sc.default_tools_dir() / sc.TOOL_NAME
    foreign.mkdir(parents=True)
    (foreign / "precious.txt").write_text("keep me")
    answer_confirm(ux, monkeypatch, True)
    host._steam_do_uninstall(host.ctx)  # ne doit pas lever
    assert (foreign / "precious.txt").exists()
    assert "refusing" in last_text(host.ctx["result_label"])


# --- action de menu ---------------------------------------------------------------- #

def test_menu_action_opens_the_dashboard_window(ux):
    app = mock.MagicMock()
    ux.register_steam_action(app)
    app.add_action.assert_called_once()

    action = ux.Gio.SimpleAction.new.return_value
    ux.Gio.SimpleAction.new.assert_called_with("steam_config", None)
    on_activate = action.connect.call_args[0][1]

    dialog = mock.MagicMock(spec=[])  # une boîte de dialogue : pas de show_steam_window
    dashboard = mock.MagicMock()
    app.get_windows.return_value = [dialog, dashboard]
    on_activate(None, None)
    dashboard.show_steam_window.assert_called_once()


# --- câblage et traductions (sans exécuter GTK) ------------------------------------- #

def _source(rel):
    return (PKG / rel).read_text(encoding="utf-8")


def test_dashboard_is_wired():
    tree = ast.parse(_source("ux/dashboard.py"))
    dashboard = next(n for n in ast.walk(tree)
                     if isinstance(n, ast.ClassDef) and n.name == "Dashboard")
    bases = [b.id for b in dashboard.bases if isinstance(b, ast.Name)]
    assert "DashboardSteamMixin" in bases
    assert bases.index("DashboardSteamMixin") < bases.index("ApplicationWindow") \
        if "ApplicationWindow" in bases else True
    assert "register_steam_action(self)" in _source("ux/dashboard.py")


def test_menu_has_the_entry():
    source = _source("ux/menu.py")
    # Normalize whitespace to support multiline calls
    source = " ".join(source.split())
    # Steam configuration action
    assert 'tr("menu_steam_config"), "app.steam_config"' in source
    # Steam menu icon
    assert '"applications-games-symbolic"' in source
    # Fallback menu action
    assert 'actions.get("steam_config"' in source

def test_menu_items_have_themed_icons():
    source = _source("ux/menu.py")

    # Vérifie la présence du mécanisme d'icônes GTK
    assert "Gio.ThemedIcon" in source
    assert ".set_icon(" in source

    # Vérifie l'organisation du menu
    assert "append_section(" in source

def test_steam_menu_action_is_preserved():
    source = _source("ux/menu.py")
    source = " ".join(source.split())

    assert '"app.steam_config"' in source
    assert 'tr("menu_steam_config")' in source
    assert '"applications-games-symbolic"' in source


def test_every_steam_key_used_in_the_ux_exists_in_all_locales():
    used = set(re.findall(r'tr\(\s*"((?:menu_)?steam_[a-z_]+)"',
                          _source("ux/dashboard_steam.py") + _source("ux/menu.py")))
    assert {"menu_steam_config", "steam_title", "steam_install",
            "steam_uninstall"} <= used
    for locale in sorted((PKG / "locales").glob("??.json")):
        table = json.loads(locale.read_text(encoding="utf-8"))
        missing = used - set(table)
        assert not missing, f"{locale.name}: {sorted(missing)}"


@pytest.mark.parametrize("key", ["steam_confirm_replace", "steam_uninstalled_kept"])
def test_files_placeholder_is_kept_in_every_translation(key):
    for locale in sorted((PKG / "locales").glob("??.json")):
        assert "{files}" in json.loads(locale.read_text(encoding="utf-8"))[key], locale.name


def test_error_placeholder_is_kept_in_every_translation():
    for locale in sorted((PKG / "locales").glob("??.json")):
        assert "{error}" in json.loads(locale.read_text(encoding="utf-8"))["steam_error"], locale.name
