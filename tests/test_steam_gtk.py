"""Tests du menu « Configuration Steam » avec le VRAI GTK4.

Les tests de test_steam_ux.py remplacent `gi` par un faux : ils ne voient pas les
erreurs d'API GTK (par ex. le crash `AlertDialog has no attribute set_title`).
Ici on utilise les vrais widgets, les vraies boîtes de dialogue et de vrais clics.

Ignorés sans GTK4 ; ceux qui ouvrent des fenêtres demandent un affichage
(`xvfb-run -a pytest tests/test_steam_gtk.py` sur un serveur sans écran).
"""

import importlib
import sys
import time

import pytest

gi = pytest.importorskip("gi")
try:
    gi.require_version("Gtk", "4.0")
    gi.require_version("Gdk", "4.0")
    from gi.repository import Gdk, Gio, GLib, Gtk
except (ValueError, ImportError):  # pragma: no cover - GTK4 absent
    pytest.skip("GTK 4 indisponible", allow_module_level=True)

from proton_autogen import steam_compat as sc
from proton_autogen.i18n import tr

UX_MODULES = (
    "proton_autogen.ux.dashboard_steam", "proton_autogen.ux.dialogs",
    "proton_autogen.ux.dashboard_status", "proton_autogen.ux.menu",
    "proton_autogen.ux.dashboard_proton_update",
)


@pytest.fixture
def real_ux():
    """Modules UX importés avec le vrai gi (sans trace d'un faux gi précédent)."""
    for name in UX_MODULES:
        sys.modules.pop(name, None)
    steam = importlib.import_module("proton_autogen.ux.dashboard_steam")
    dialogs = importlib.import_module("proton_autogen.ux.dialogs")
    menu = importlib.import_module("proton_autogen.ux.menu")
    yield steam, dialogs, menu
    for name in UX_MODULES:
        sys.modules.pop(name, None)


@pytest.fixture
def display():
    try:
        available = Gtk.init_check() and Gdk.Display.get_default() is not None
    except RuntimeError:  # sans écran, PyGObject lève au lieu de renvoyer False
        available = False
    if not available:
        pytest.skip("pas d'affichage (utiliser xvfb-run)")


def pump(seconds=0.05):
    """Traite les événements GTK en attente."""
    ctx = GLib.MainContext.default()
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        while ctx.iteration(False):
            pass


def walk(widget):
    yield widget
    child = widget.get_first_child()
    while child is not None:
        yield from walk(child)
        child = child.get_next_sibling()


def buttons(widget):
    return {w.get_label(): w for w in walk(widget)
            if isinstance(w, Gtk.Button) and w.get_label()}


def find_toplevel(exclude, label):
    """Fenêtre de premier niveau (hors `exclude`) contenant un bouton `label`."""
    for top in Gtk.Window.list_toplevels():
        if top in exclude:
            continue
        if label in buttons(top):
            return top
    return None


def find_dialog(exclude):
    """Boîte de dialogue de l'application (classe CSS `app-dialog`)."""
    for top in Gtk.Window.list_toplevels():
        if top not in exclude and top.has_css_class("app-dialog"):
            return top
    return None


def click_ok(dialog):
    """Clique le bouton principal (`suggested-action`) d'une boîte de dialogue."""
    [ok] = [b for b in walk(dialog) if isinstance(b, Gtk.Button)
            and b.has_css_class("suggested-action")]
    ok.emit("clicked")
    pump()


def click_cancel(dialog):
    """Clique l'autre bouton de la boîte de dialogue."""
    [cancel] = [b for b in walk(dialog) if isinstance(b, Gtk.Button)
                and not b.has_css_class("suggested-action")]
    cancel.emit("clicked")
    pump()


@pytest.fixture
def steam_home(tmp_path, monkeypatch):
    home = tmp_path / "home"
    (home / ".steam" / "root").mkdir(parents=True)
    monkeypatch.setenv("HOME", str(home))
    launcher = tmp_path / "proton-autogen"
    launcher.write_text("#!/bin/sh\n")
    launcher.chmod(0o755)
    monkeypatch.setenv("PROTON_AUTOGEN_BIN", str(launcher))
    return home


@pytest.fixture
def app_and_host(real_ux, display, steam_home):
    steam, _dialogs, _menu = real_ux

    class Host(steam.DashboardSteamMixin, Gtk.ApplicationWindow):
        pass

    app = Gtk.Application(application_id="io.github.test.steamconfig",
                          flags=Gio.ApplicationFlags.NON_UNIQUE)
    app.register(None)
    steam.register_steam_action(app)
    host = Host(application=app)
    host.status = Gtk.Label()  # barre d'état du tableau de bord
    host.present()
    pump()
    yield app, host
    for top in list(Gtk.Window.list_toplevels()):
        top.destroy()
    pump()


def open_steam_window(host, exclude):
    host.show_steam_window()
    pump()
    win = find_toplevel(exclude, tr("steam_uninstall"))
    assert win is not None, "la fenêtre Configuration Steam ne s'est pas ouverte"
    return win


# --- boîtes de dialogue réelles ---------------------------------------------------- #

@pytest.fixture
def parent(real_ux, display):
    win = Gtk.Window()
    win.present()
    pump()
    yield win
    for top in list(Gtk.Window.list_toplevels()):
        top.destroy()
    pump()


def test_show_confirm_answers_exactly_once(real_ux, parent):
    _steam, dialogs, _menu = real_ux
    for action, expected in (("ok", True), ("cancel", False), ("close", False)):
        answers = []
        dialogs.show_confirm(parent, "Titre", "Texte", answers.append)
        pump()
        dialog = find_dialog({parent})
        assert dialog is not None, "la boîte de confirmation ne s'est pas ouverte"
        assert dialog.get_title() == "Titre"
        if action == "ok":
            click_ok(dialog)
        elif action == "cancel":
            click_cancel(dialog)
        else:
            dialog.close()  # fermer la fenêtre = annuler
            pump()
        assert answers == [expected], action
        assert find_dialog({parent}) is None  # et la fenêtre est bien fermée


@pytest.mark.parametrize("helper", ["show_message", "show_error"])
def test_message_and_error_dialogs_open(real_ux, parent, helper):
    _steam, dialogs, _menu = real_ux
    getattr(dialogs, helper)(parent, "Titre", "Texte du message")
    pump()
    dialog = find_dialog({parent})
    assert dialog is not None and dialog.get_title() == "Titre"
    texts = [w.get_label() for w in walk(dialog) if isinstance(w, Gtk.Label)]
    assert "Texte du message" in texts


# --- menu ------------------------------------------------------------------------- #

def _menu_entries(model):
    """(libellé, action) de toutes les entrées, sections comprises."""
    for i in range(model.get_n_items()):
        section = model.get_item_link(i, "section")
        if section is not None:
            yield from _menu_entries(section)
            continue
        label = model.get_item_attribute_value(i, "label", None)
        action = model.get_item_attribute_value(i, "action", None)
        yield (label.get_string() if label else None,
               action.get_string() if action else None)


def test_menu_model_contains_the_steam_entry(real_ux):
    _steam, _dialogs, menu = real_ux
    entries = list(_menu_entries(menu.build_app_menu(None)))
    assert (tr("menu_steam_config"), "app.steam_config") in entries


# --- fenêtre réelle ---------------------------------------------------------------- #

def test_menu_action_opens_the_window(app_and_host):
    app, host = app_and_host
    before = set(Gtk.Window.list_toplevels())
    app.lookup_action("steam_config").activate(None)
    pump()
    assert find_toplevel(before, tr("steam_uninstall")) is not None


def test_window_reflects_the_state(app_and_host):
    _app, host = app_and_host
    win = open_steam_window(host, {host})
    btns = buttons(win)
    assert tr("steam_install") in btns                      # pas encore installé
    assert btns[tr("steam_install")].get_sensitive()
    assert not btns[tr("steam_uninstall")].get_sensitive()  # rien à désinstaller


def test_install_then_uninstall_with_real_clicks_and_dialog(app_and_host):
    _app, host = app_and_host
    win = open_steam_window(host, {host})
    btns = buttons(win)

    btns[tr("steam_install")].emit("clicked")
    pump()
    assert sc.get_status().healthy
    assert tr("steam_reinstall") in buttons(win)
    assert buttons(win)[tr("steam_uninstall")].get_sensitive()

    # Désinstaller : vraie boîte de confirmation, d'abord on annule...
    buttons(win)[tr("steam_uninstall")].emit("clicked")
    pump()
    dialog = find_dialog({host, win})
    assert dialog is not None, "la boîte de confirmation ne s'est pas ouverte"
    click_cancel(dialog)
    assert sc.get_status().healthy

    # ...puis on confirme.
    buttons(win)[tr("steam_uninstall")].emit("clicked")
    pump()
    dialog = find_dialog({host, win})
    assert dialog is not None
    click_ok(dialog)
    assert not sc.get_status().installed
    assert tr("steam_install") in buttons(win)
    assert not buttons(win)[tr("steam_uninstall")].get_sensitive()


def test_reinstall_over_a_modified_file_asks_with_a_real_dialog(app_and_host):
    _app, host = app_and_host
    win = open_steam_window(host, {host})
    buttons(win)[tr("steam_install")].emit("clicked")
    pump()
    manifest = sc.get_status().dest / "toolmanifest.vdf"
    manifest.write_text("custom\n")

    buttons(win)[tr("steam_reinstall")].emit("clicked")
    pump()
    dialog = find_dialog({host, win})
    assert dialog is not None
    click_cancel(dialog)
    assert manifest.read_text() == "custom\n"  # refus : rien n'est écrasé

    buttons(win)[tr("steam_reinstall")].emit("clicked")
    pump()
    click_ok(find_dialog({host, win}))
    assert sc.get_status().healthy
    assert list(manifest.parent.glob("toolmanifest.vdf.bak-*"))  # sauvegarde conservée
