"""Tests avec le VRAI GTK4 du menu ⋮, d'« Ouvrir le dossier » et d'« Exporter vers Bottles ».

Widgets, popovers et clics réels (voir test_steam_gtk.py pour la même approche).
Ignorés sans GTK4 ou sans affichage :
    xvfb-run -a pytest tests/test_more_menu_gtk.py
"""

import importlib
import stat
import sys
import time

import pytest
import yaml

gi = pytest.importorskip("gi")
try:
    gi.require_version("Gtk", "4.0")
    gi.require_version("Gdk", "4.0")
    from gi.repository import Gio, GLib, Gtk
except (ValueError, ImportError):  # pragma: no cover - GTK4 absent
    pytest.skip("GTK 4 indisponible", allow_module_level=True)

from proton_autogen.i18n import tr
from proton_autogen.utils import bottles_export as be

UX_MODULES = (
    "proton_autogen.ux.widgets.game_more_menu", "proton_autogen.ux.game_list",
    "proton_autogen.ux.game_grid", "proton_autogen.ux.game_biblio",
    "proton_autogen.ux.dashboard_bottles", "proton_autogen.ux.dialogs",
    "proton_autogen.ux.dashboard_status", "proton_autogen.ux.dashboard_actions",
)


@pytest.fixture
def display():
    try:
        available = Gtk.init_check() and gi.repository.Gdk.Display.get_default() is not None
    except RuntimeError:
        available = False
    if not available:
        pytest.skip("pas d'affichage (utiliser xvfb-run)")


@pytest.fixture
def ux(display):
    for name in UX_MODULES:
        sys.modules.pop(name, None)
    modules = types = {
        "menu": importlib.import_module("proton_autogen.ux.widgets.game_more_menu"),
        "list": importlib.import_module("proton_autogen.ux.game_list"),
        "grid": importlib.import_module("proton_autogen.ux.game_grid"),
        "biblio": importlib.import_module("proton_autogen.ux.game_biblio"),
        "bottles": importlib.import_module("proton_autogen.ux.dashboard_bottles"),
    }
    yield modules
    for top in list(Gtk.Window.list_toplevels()):
        top.destroy()
    pump()
    for name in UX_MODULES:
        sys.modules.pop(name, None)


def pump(seconds=0.05):
    ctx = GLib.MainContext.default()
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        while ctx.iteration(False):
            pass


def pump_until(predicate, timeout=5.0):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        pump(0.05)
        if predicate():
            return True
    return False


def walk(widget):
    yield widget
    child = widget.get_first_child()
    while child is not None:
        yield from walk(child)
        child = child.get_next_sibling()


def by_name(root, name):
    return [w for w in walk(root) if w.get_name() == name]


def window_with(widget, width=900, height=500):
    win = Gtk.Window(default_width=width, default_height=height)
    win.set_child(widget)
    win.present()
    pump(0.3)
    return win


class Recorder:
    """Callbacks de la vue : mémorisent (action, nom du jeu)."""

    def __init__(self):
        self.calls = []

    def __getattr__(self, name):
        if not name.startswith("on_"):
            raise AttributeError(name)
        return lambda game: self.calls.append((name[3:], game["name"]))


def make_games(tmp_path, n=3):
    games = []
    for i in range(n):
        exe = tmp_path / f"game{i}" / f"G{i}.exe"
        exe.parent.mkdir(parents=True)
        exe.write_bytes(b"MZ")
        games.append({"name": f"Game {i}", "path": str(exe), "exe_type": "auto",
                      "proton": "", "prefix": {"name": "main"}, "features": {}, "env": {}})
    return games


ACTIONS = ("open_folder", "export_lutris", "export_bottles", "remove")


def view_kwargs(rec):
    return dict(on_launch=rec.on_launch, on_edit=rec.on_edit, on_delete=rec.on_delete,
                on_export_lutris=rec.on_export_lutris, on_open_folder=rec.on_open_folder,
                on_export_bottles=rec.on_export_bottles, lang="en")


# --- le popover ⋮ ------------------------------------------------------------------- #

def test_popover_has_the_four_items_in_order(ux):
    popover = ux["menu"].build_more_menu(lambda name: None)
    labels = [w.get_label() for w in walk(popover) if isinstance(w, Gtk.Button)]
    assert labels == [tr("open_folder"), tr("export_lutris"), tr("export_bottles"),
                      tr("remove_from_library")]


def test_lutris_entry_can_be_hidden(ux):
    popover = ux["menu"].build_more_menu(lambda name: None, lutris_enabled=False)
    labels = [w.get_label() for w in walk(popover) if isinstance(w, Gtk.Button)]
    assert tr("export_lutris") not in labels and len(labels) == 3


def test_clicking_an_item_reports_the_action_once_and_closes(ux, display):
    seen = []
    popover = ux["menu"].build_more_menu(seen.append)
    button = Gtk.MenuButton()
    button.set_popover(popover)
    window_with(button)
    for action in ACTIONS:
        by_name(popover, f"more-{action}")[0].emit("clicked")
    assert seen == ["open_folder", "export_lutris", "export_bottles", "remove"]
    assert not popover.is_visible()


def test_more_button_exposes_a_tooltip_and_an_icon_or_glyph(ux, display):
    popover = ux["menu"].build_more_menu(lambda name: None)
    button = ux["menu"].make_more_button(popover)
    assert button.get_tooltip_text() == tr("more_actions")
    assert button.get_icon_name() == "view-more-symbolic" or button.get_label() == "⋮"
    labeled = ux["menu"].make_more_button(popover, label=tr("more_actions"))
    assert labeled.get_label() == f"⋮  {tr('more_actions')}"


# --- vue liste ----------------------------------------------------------------------- #

def test_list_rows_have_one_more_button_and_no_old_buttons(ux, tmp_path):
    rec = Recorder()
    view = ux["list"].GameList(**view_kwargs(rec))
    view.set_games(make_games(tmp_path))
    window_with(view)

    more = [w for w in walk(view) if isinstance(w, Gtk.MenuButton)]
    assert len(more) >= 1
    assert not [w for w in walk(view) if w.has_css_class("btn-delete")]
    assert not [w for w in walk(view) if isinstance(w, Gtk.Button)
                and w.get_tooltip_text() == tr("remove_from_library")]


def test_list_menu_acts_on_its_own_row(ux, tmp_path):
    """Chaque ligne agit sur SON jeu, même après recyclage des widgets."""
    rec = Recorder()
    view = ux["list"].GameList(**view_kwargs(rec))
    view.set_games(make_games(tmp_path, n=3))
    window_with(view)

    menus = [w for w in walk(view) if isinstance(w, Gtk.MenuButton)]
    assert len(menus) >= 3
    for index, menu in enumerate(menus[:3]):
        for action in ACTIONS:
            by_name(menu.get_popover(), f"more-{action}")[0].emit("clicked")
        expected = [(a if a != "remove" else "delete", f"Game {index}") for a in ACTIONS]
        assert rec.calls[-4:] == expected, index


def test_list_menu_survives_a_refresh(ux, tmp_path):
    rec = Recorder()
    view = ux["list"].GameList(**view_kwargs(rec))
    games = make_games(tmp_path, n=2)
    view.set_games(games)
    window_with(view)
    view.set_games(list(reversed(games)))
    pump(0.3)
    menu = [w for w in walk(view) if isinstance(w, Gtk.MenuButton)][0]
    by_name(menu.get_popover(), "more-open_folder")[0].emit("clicked")
    assert rec.calls[-1] == ("open_folder", "Game 1")


# --- grille et bibliothèque ------------------------------------------------------------ #

@pytest.mark.parametrize("kind", ["grid", "biblio"])
def test_context_menu_puts_the_actions_in_the_more_submenu(ux, tmp_path, kind):
    rec = Recorder()
    cls = ux["grid"].GameGrid if kind == "grid" else ux["biblio"].GameBiblio
    view = cls(**view_kwargs(rec))
    games = make_games(tmp_path, n=1)
    view.set_games(games)
    window_with(view)

    card = Gtk.Box()
    window_with(card, 300, 200)
    view._show_context_menu(card, games[0], 10, 10)
    pump(0.2)
    popover = card._game_grid_popover
    assert popover is not None

    # Niveau 1 : plus de Lutris ni de suppression directement dans le menu contextuel…
    direct = [w.get_label() for w in walk(popover)
              if isinstance(w, Gtk.Button) and w.get_label()
              and not w.get_name().startswith("more-")]
    assert tr("export_lutris") not in direct
    assert tr("remove_from_library") not in direct
    # …mais une entrée ⋮ qui les contient.
    more = [w for w in walk(popover) if isinstance(w, Gtk.MenuButton)]
    assert len(more) == 1
    assert tr("more_actions") in more[0].get_label()

    for action in ACTIONS:
        by_name(more[0].get_popover(), f"more-{action}")[0].emit("clicked")
        assert not popover.is_visible()
    assert rec.calls == [("open_folder", "Game 0"), ("export_lutris", "Game 0"),
                         ("export_bottles", "Game 0"), ("delete", "Game 0")]


def test_context_menu_without_the_new_callbacks_does_not_crash(ux, tmp_path):
    """Les nouveaux callbacks sont facultatifs (compatibilité des appelants)."""
    view = ux["grid"].GameGrid(lang="en")
    games = make_games(tmp_path, n=1)
    view.set_games(games)
    window_with(view)
    card = Gtk.Box()
    window_with(card, 300, 200)
    view._show_context_menu(card, games[0], 5, 5)
    more = [w for w in walk(card._game_grid_popover) if isinstance(w, Gtk.MenuButton)][0]
    for action in ACTIONS:
        by_name(more.get_popover(), f"more-{action}")[0].emit("clicked")  # ne lève pas


# --- Exporter vers Bottles (dialogue réel) ---------------------------------------------- #

class FakeToast:
    def __init__(self):
        self.messages = []

    def __getattr__(self, kind):
        return lambda message, *a, **k: self.messages.append((kind, message))


@pytest.fixture
def bottles_env(tmp_path, monkeypatch):
    home = tmp_path / "home"
    data_home = home / ".local" / "share"
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("XDG_DATA_HOME", str(data_home))
    monkeypatch.setattr(be, "bottles_running", lambda: False)
    return data_home / "bottles" / "bottles", home / ".var/app/com.usebottles.bottles/data/bottles/bottles"


def write_bottle(root, dirname, name=None):
    directory = root / dirname
    directory.mkdir(parents=True)
    (directory / "bottle.yml").write_text(yaml.safe_dump({
        "Name": name or dirname, "Path": dirname, "Environment": "Gaming",
        "External_Programs": {}}, indent=4))
    return directory


@pytest.fixture
def host(ux, bottles_env):
    class Host(ux["bottles"].DashboardBottlesMixin, Gtk.ApplicationWindow):
        pass

    app = Gtk.Application(application_id="io.github.test.morebottles",
                          flags=Gio.ApplicationFlags.NON_UNIQUE)
    app.register(None)
    h = Host(application=app)
    h.toast = FakeToast()
    h.present()
    pump()
    return h


def chooser_of(host):
    for top in Gtk.Window.list_toplevels():
        if top is not host and top.has_css_class("bottles-export-window"):
            return top
    return None


def test_bottles_dialog_lists_bottles_and_exports_the_selection(host, bottles_env, tmp_path):
    native, flatpak = bottles_env
    gaming = write_bottle(native, "Gaming", name="Gaming")
    write_bottle(flatpak, "Office", name="Office")
    game = make_games(tmp_path, n=1)[0]

    host.export_bottles_handler(game)
    pump(0.2)
    win = chooser_of(host)
    assert win is not None, "la fenêtre de choix ne s'est pas ouverte"

    rows = [w for w in walk(win) if isinstance(w, Gtk.ListBoxRow)]
    assert len(rows) == 2
    export = [w for w in walk(win) if isinstance(w, Gtk.Button)
              and w.get_label() == tr("export_bottles_button")][0]

    def title(row):
        return [l.get_label() for l in walk(row) if isinstance(l, Gtk.Label)][0]

    listbox = rows[0].get_parent()
    assert [title(r) for r in rows] == ["Gaming", "Office"]      # triées par nom
    assert title(listbox.get_selected_row()) == "Gaming"          # première présélectionnée
    assert export.get_sensitive()

    # On choisit l'AUTRE bouteille : l'export doit aller là, et nulle part ailleurs.
    listbox.select_row(rows[1])
    pump()
    export.emit("clicked")
    pump(0.2)

    office = flatpak / "Office" / "bottle.yml"
    programs = yaml.safe_load(office.read_text())["External_Programs"]
    assert [p["path"] for p in programs.values()] == [game["path"]]
    assert yaml.safe_load((gaming / "bottle.yml").read_text())["External_Programs"] == {}
    assert chooser_of(host) is None            # fenêtre fermée
    kind, message = host.toast.messages[0]
    assert kind == "success"
    assert message == tr("export_bottles_done", game="Game 0", bottle="Office")


def test_bottles_dialog_exports_to_the_preselected_bottle(host, bottles_env, tmp_path):
    only = write_bottle(bottles_env[0], "Only")
    host.export_bottles_handler(make_games(tmp_path, n=1)[0])
    pump(0.2)
    win = chooser_of(host)
    export = [w for w in walk(win) if isinstance(w, Gtk.Button)
              and w.get_label() == tr("export_bottles_button")][0]
    assert export.get_sensitive()
    export.emit("clicked")                      # sans rien choisir : la présélection
    pump(0.2)
    assert yaml.safe_load((only / "bottle.yml").read_text())["External_Programs"]


def test_bottles_dialog_cancel_changes_nothing(host, bottles_env, tmp_path):
    directory = write_bottle(bottles_env[0], "Gaming")
    before = (directory / "bottle.yml").read_bytes()
    host.export_bottles_handler(make_games(tmp_path, n=1)[0])
    pump(0.2)
    cancel = [w for w in walk(chooser_of(host)) if isinstance(w, Gtk.Button)
              and w.get_label() == tr("cancel")][0]
    cancel.emit("clicked")
    pump(0.2)
    assert chooser_of(host) is None
    assert (directory / "bottle.yml").read_bytes() == before
    assert host.toast.messages == []


def test_bottles_second_export_reports_already_present(host, bottles_env, tmp_path):
    write_bottle(bottles_env[0], "Gaming")
    game = make_games(tmp_path, n=1)[0]
    for _ in range(2):
        host.export_bottles_handler(game)
        pump(0.2)
        win = chooser_of(host)
        [w for w in walk(win) if isinstance(w, Gtk.Button)
         and w.get_label() == tr("export_bottles_button")][0].emit("clicked")
        pump(0.2)
    assert [k for k, _m in host.toast.messages] == ["success", "info"]
    assert host.toast.messages[1][1] == tr("export_bottles_already", game="Game 0", bottle="Gaming")


def test_bottles_warnings_are_announced(host, bottles_env, tmp_path, monkeypatch):
    write_bottle(bottles_env[1], "Flat")            # Flatpak
    monkeypatch.setattr(be, "bottles_running", lambda: True)
    host.export_bottles_handler(make_games(tmp_path, n=1)[0])
    pump(0.2)
    [w for w in walk(chooser_of(host)) if isinstance(w, Gtk.Button)
     and w.get_label() == tr("export_bottles_button")][0].emit("clicked")
    pump(0.2)
    warnings = [m for k, m in host.toast.messages if k == "warning"]
    assert warnings == [tr("export_bottles_running"), tr("export_bottles_flatpak")]


def test_no_bottles_shows_a_message_instead_of_the_chooser(host, tmp_path):
    host.export_bottles_handler(make_games(tmp_path, n=1)[0])
    pump(0.2)
    assert chooser_of(host) is None
    dialogs = [t for t in Gtk.Window.list_toplevels()
               if t is not host and t.has_css_class("app-dialog")]
    assert dialogs, "le message « aucune bouteille » ne s'affiche pas"
    texts = [w.get_label() for w in walk(dialogs[0]) if isinstance(w, Gtk.Label)]
    assert tr("export_bottles_none") in texts


def test_missing_executable_is_reported_before_any_dialog(host, bottles_env, tmp_path):
    write_bottle(bottles_env[0], "Gaming")
    host.export_bottles_handler({"name": "Ghost", "path": "/nonexistent/ghost.exe"})
    pump(0.2)
    assert chooser_of(host) is None
    kind, message = host.toast.messages[0]
    assert kind == "error" and message.startswith(tr("export_bottles_failed", error="")[:10])


# --- Ouvrir le dossier (handler réel du dashboard) ---------------------------------------- #

@pytest.fixture
def actions_host(ux, tmp_path, monkeypatch):
    actions = importlib.import_module("proton_autogen.ux.dashboard_actions")

    class Host(actions.DashboardActionsMixin, Gtk.ApplicationWindow):
        pass

    app = Gtk.Application(application_id="io.github.test.openfolder",
                          flags=Gio.ApplicationFlags.NON_UNIQUE)
    app.register(None)
    h = Host(application=app)
    h.toast = FakeToast()
    h.present()
    pump()
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    monkeypatch.setattr("shutil.which", lambda cmd: str(bin_dir / cmd)
                        if (bin_dir / cmd).exists() else None)
    return h, bin_dir


def fake_opener(bin_dir, name, body):
    script = bin_dir / name
    script.write_text("#!/bin/sh\n" + body)
    script.chmod(script.stat().st_mode | stat.S_IXUSR)


def test_open_folder_handler_opens_the_executable_folder(actions_host, tmp_path):
    host, bin_dir = actions_host
    log = tmp_path / "opened"
    fake_opener(bin_dir, "xdg-open", f'printf "%s" "$1" > "{log}"\n')
    game = make_games(tmp_path, n=1)[0]

    host.open_folder_handler(game)
    assert pump_until(log.exists)
    assert log.read_text() == str(tmp_path / "game0")
    pump(0.2)
    assert host.toast.messages == []


def test_open_folder_handler_reports_a_missing_folder(actions_host):
    host, _bin = actions_host
    host.open_folder_handler({"name": "Ghost", "path": "/nonexistent/dir/ghost.exe"})
    assert pump_until(lambda: host.toast.messages)
    kind, message = host.toast.messages[0]
    assert kind == "error" and tr("open_folder_failed") in message


def test_open_folder_handler_does_not_block_the_interface(actions_host, tmp_path, monkeypatch):
    host, bin_dir = actions_host
    from proton_autogen.utils import open_folder as of
    monkeypatch.setattr(of, "LAUNCH_GRACE_SECONDS", 3.0)
    fake_opener(bin_dir, "xdg-open", "sleep 2\n")
    game = make_games(tmp_path, n=1)[0]
    start = time.monotonic()
    host.open_folder_handler(game)
    assert time.monotonic() - start < 0.5      # rend la main tout de suite
