"""Tests de utils/bottles_export.py (export d'un jeu vers une bouteille Bottles)."""

import os
import stat

import pytest
import yaml

from proton_autogen.utils import bottles_export as be


# --- fabrique de bouteilles ------------------------------------------------------- #

def write_bottle(root, dirname, name=None, environment="Gaming", programs=None, **extra):
    """Crée <root>/<dirname>/bottle.yml comme Bottles l'écrit (yaml safe, indent 4)."""
    directory = root / dirname
    directory.mkdir(parents=True)
    data = {
        "Name": name or dirname,
        "Path": dirname,
        "Environment": environment,
        "Runner": "soda-9.0-1",
        "Parameters": {"dxvk": True, "vkd3d": False, "sync": "fsync"},
        "DLL_Overrides": {"d3d9": "n,b"},
        "Creation_Date": "2024-05-01 10:00:00.000000",
        "External_Programs": programs if programs is not None else {},
    }
    data.update(extra)
    (directory / "bottle.yml").write_text(yaml.safe_dump(data, indent=4), encoding="utf-8")
    return directory


@pytest.fixture
def env(tmp_path, monkeypatch):
    home = tmp_path / "home"
    data_home = home / ".local" / "share"
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("XDG_DATA_HOME", str(data_home))
    native = data_home / "bottles" / "bottles"
    flatpak = home / ".var/app/com.usebottles.bottles/data/bottles/bottles"
    monkeypatch.setattr(be, "bottles_running", lambda: False)
    return native, flatpak


@pytest.fixture
def game(tmp_path):
    exe = tmp_path / "Games" / "Alerte Rouge" / "RA.EXE"
    exe.parent.mkdir(parents=True)
    exe.write_bytes(b"MZ")
    return {
        "name": "Alerte Rouge",
        "path": str(exe),
        "env": {"DXVK_HUD": "fps", "PROTON_USE_WINED3D": "1", "WINEPREFIX": "/x",
                "STEAM_COMPAT_DATA_PATH": "/y", "SteamAppId": "1", "MANGOHUD": "1"},
        "features": {"gamemode": True, "mangohud": True},
    }


def bottle_of(directory, source="native"):
    return be.Bottle(name=directory.name, directory=directory, source=source)


# --- découverte --------------------------------------------------------------------- #

def test_roots_follow_xdg_data_home_and_flatpak(env):
    native, flatpak = env
    assert be.bottles_roots() == [("native", native), ("flatpak", flatpak)]


def test_roots_fall_back_to_local_share(env, monkeypatch):
    monkeypatch.delenv("XDG_DATA_HOME")
    assert be.bottles_roots()[0][1] == (
        be.Path.home() / ".local/share/bottles/bottles")


def test_list_bottles(env):
    native, flatpak = env
    write_bottle(native, "zeta", name="Zeta")
    write_bottle(native, "alpha", name="alpha")
    write_bottle(flatpak, "fp1", name="Flat")
    write_bottle(native, "steamy", environment="Steam")           # ignorée
    (native / "no_config").mkdir()                                # pas de bottle.yml
    broken = native / "broken"
    broken.mkdir()
    (broken / "bottle.yml").write_text("- not\n- a mapping\n")    # illisible
    (native / "stray-file").write_text("x")

    found = [(b.name, b.source) for b in be.list_bottles()]
    assert found == [("alpha", "native"), ("Flat", "flatpak"), ("Zeta", "native")]


def test_list_bottles_without_bottles_installed(env):
    assert be.list_bottles() == []


def test_bottle_name_falls_back_to_directory(env):
    native, _ = env
    directory = write_bottle(native, "mydir")
    data = yaml.safe_load((directory / "bottle.yml").read_text())
    del data["Name"]
    (directory / "bottle.yml").write_text(yaml.safe_dump(data))
    assert [b.name for b in be.list_bottles()] == ["mydir"]


# --- construction du programme -------------------------------------------------------- #

def test_build_program_has_the_keys_bottles_expects(game):
    program, ignored = be.build_program(game, program_id="fixed-id")
    assert program["id"] == "fixed-id"
    assert program["name"] == "Alerte Rouge"
    assert program["executable"] == "RA.EXE"
    assert program["path"] == game["path"]
    assert program["folder"] == os.path.dirname(game["path"])
    assert program["arguments"] == "" and program["icon"] == ""


def test_proton_specific_env_is_not_exported(game):
    program, ignored = be.build_program(game)
    assert program["environment"] == {"DXVK_HUD": "fps", "MANGOHUD": "1"}
    assert sorted(ignored) == ["PROTON_USE_WINED3D", "STEAM_COMPAT_DATA_PATH",
                               "SteamAppId", "WINEPREFIX"]


def test_gamemode_only_when_enabled(game):
    assert be.build_program(game)[0]["gamemode"] is True
    game["features"] = {"gamemode": False}
    assert "gamemode" not in be.build_program(game)[0]
    game.pop("features")
    assert "gamemode" not in be.build_program(game)[0]


def test_no_environment_key_when_nothing_to_export(game):
    game["env"] = {"PROTON_LOG": "1"}
    assert "environment" not in be.build_program(game)[0]
    game["env"] = None
    assert "environment" not in be.build_program(game)[0]


def test_non_string_env_values_are_ignored(game):
    game["env"] = {"A": 1, "B": "ok"}
    program, ignored = be.build_program(game)
    assert program["environment"] == {"B": "ok"} and ignored == ["A"]


def test_name_defaults_to_executable_stem(game):
    del game["name"]
    assert be.build_program(game)[0]["name"] == "RA"


@pytest.mark.parametrize("path", [None, "", "/nonexistent/game.exe"])
def test_missing_executable_is_an_error(game, path):
    game["path"] = path
    with pytest.raises(be.BottlesExportError):
        be.build_program(game)


# --- export ------------------------------------------------------------------------ #

def test_export_adds_the_program_and_keeps_everything_else(env, game):
    native, _ = env
    directory = write_bottle(native, "Gaming")
    config = directory / "bottle.yml"
    before = yaml.safe_load(config.read_text())
    original_bytes = config.read_bytes()

    result = be.export_game_to_bottle(game, bottle_of(directory))

    assert result.status == "added"
    after = yaml.safe_load(config.read_text())
    programs = after.pop("External_Programs")
    before.pop("External_Programs")
    assert after == before                      # le reste de la config est intact
    assert list(programs) == [result.program_id]
    entry = programs[result.program_id]
    assert entry["id"] == result.program_id
    assert entry["path"] == game["path"] and entry["executable"] == "RA.EXE"
    assert entry["environment"] == {"DXVK_HUD": "fps", "MANGOHUD": "1"}
    assert sorted(result.ignored_env) == ["PROTON_USE_WINED3D", "STEAM_COMPAT_DATA_PATH",
                                          "SteamAppId", "WINEPREFIX"]
    # sauvegarde de l'état précédent
    assert result.backup == directory / be.BACKUP_NAME
    assert result.backup.read_bytes() == original_bytes
    assert not list(directory.glob(".bottle-*.tmp"))  # pas de fichier temporaire


def test_export_keeps_other_programs_untouched(env, game):
    native, _ = env
    mine = {"p1": {"id": "p1", "name": "Other", "path": "/opt/other.exe",
                   "executable": "other.exe", "folder": "/opt", "dxvk": False}}
    directory = write_bottle(native, "Gaming", programs=mine)
    result = be.export_game_to_bottle(game, bottle_of(directory))
    programs = yaml.safe_load((directory / "bottle.yml").read_text())["External_Programs"]
    assert programs["p1"] == mine["p1"]
    assert set(programs) == {"p1", result.program_id}


def test_export_is_idempotent_and_does_not_rewrite(env, game):
    native, _ = env
    directory = write_bottle(native, "Gaming")
    first = be.export_game_to_bottle(game, bottle_of(directory))
    config = directory / "bottle.yml"
    content = config.read_bytes()
    (directory / be.BACKUP_NAME).unlink()

    second = be.export_game_to_bottle(game, bottle_of(directory))
    assert second.status == "already_present"
    assert second.program_id == first.program_id
    assert config.read_bytes() == content
    assert not (directory / be.BACKUP_NAME).exists()  # rien d'écrit, pas de sauvegarde


@pytest.mark.parametrize("section", [None, "absent"])
def test_export_creates_the_programs_section(env, game, section):
    native, _ = env
    directory = write_bottle(native, "Gaming")
    config = directory / "bottle.yml"
    data = yaml.safe_load(config.read_text())
    if section == "absent":
        del data["External_Programs"]
    else:
        data["External_Programs"] = None
    config.write_text(yaml.safe_dump(data, indent=4))
    result = be.export_game_to_bottle(game, bottle_of(directory))
    assert result.program_id in yaml.safe_load(config.read_text())["External_Programs"]


def test_export_preserves_file_mode(env, game):
    native, _ = env
    directory = write_bottle(native, "Gaming")
    config = directory / "bottle.yml"
    config.chmod(0o600)
    be.export_game_to_bottle(game, bottle_of(directory))
    assert stat.S_IMODE(config.stat().st_mode) == 0o600


def test_export_handles_accents(env, game):
    native, _ = env
    directory = write_bottle(native, "Gaming", name="Bouteille é")
    game["name"] = "Très Bon Jeu ™"
    result = be.export_game_to_bottle(game, bottle_of(directory))
    data = yaml.safe_load((directory / "bottle.yml").read_text(encoding="utf-8"))
    assert data["Name"] == "Bouteille é"
    assert data["External_Programs"][result.program_id]["name"] == "Très Bon Jeu ™"


def test_unexpected_programs_section_leaves_the_file_untouched(env, game):
    native, _ = env
    directory = write_bottle(native, "Gaming", programs=["not", "a", "dict"])
    config = directory / "bottle.yml"
    content = config.read_bytes()
    with pytest.raises(be.BottlesExportError):
        be.export_game_to_bottle(game, bottle_of(directory))
    assert config.read_bytes() == content
    assert not (directory / be.BACKUP_NAME).exists()


def test_missing_config_is_an_error(env, game, tmp_path):
    with pytest.raises(be.BottlesExportError):
        be.export_game_to_bottle(game, bottle_of(tmp_path / "nowhere"))


def test_missing_executable_leaves_the_bottle_untouched(env, game):
    native, _ = env
    directory = write_bottle(native, "Gaming")
    content = (directory / "bottle.yml").read_bytes()
    game["path"] = "/nonexistent.exe"
    with pytest.raises(be.BottlesExportError):
        be.export_game_to_bottle(game, bottle_of(directory))
    assert (directory / "bottle.yml").read_bytes() == content


def test_failed_verification_restores_the_backup(env, game, monkeypatch):
    native, _ = env
    directory = write_bottle(native, "Gaming")
    config = directory / "bottle.yml"
    content = config.read_bytes()
    monkeypatch.setattr(be, "_write_config_atomic",
                        lambda path, data: path.write_text("Name: broken\n"))
    with pytest.raises(be.BottlesExportError):
        be.export_game_to_bottle(game, bottle_of(directory))
    assert config.read_bytes() == content


def test_write_failure_restores_and_reports(env, game, monkeypatch):
    native, _ = env
    directory = write_bottle(native, "Gaming")
    config = directory / "bottle.yml"
    content = config.read_bytes()

    def boom(path, data):
        path.write_text("partial")
        raise OSError("disk full")

    monkeypatch.setattr(be, "_write_config_atomic", boom)
    with pytest.raises(be.BottlesExportError, match="disk full"):
        be.export_game_to_bottle(game, bottle_of(directory))
    assert config.read_bytes() == content


# --- avertissements ------------------------------------------------------------------ #

def test_flatpak_bottle_warns_about_the_sandbox(env, game):
    _, flatpak = env
    directory = write_bottle(flatpak, "fp")
    result = be.export_game_to_bottle(game, bottle_of(directory, source="flatpak"))
    assert be.WARNING_FLATPAK_SANDBOX in result.warnings
    assert be.WARNING_BOTTLES_RUNNING not in result.warnings


def test_warnings_come_in_order_of_importance(env, game, monkeypatch):
    _, flatpak = env
    directory = write_bottle(flatpak, "fp")
    monkeypatch.setattr(be, "bottles_running", lambda: True)
    result = be.export_game_to_bottle(game, bottle_of(directory, source="flatpak"))
    assert result.warnings == [be.WARNING_BOTTLES_RUNNING, be.WARNING_FLATPAK_SANDBOX]


def test_running_bottles_warns(env, game, monkeypatch):
    native, _ = env
    directory = write_bottle(native, "Gaming")
    monkeypatch.setattr(be, "bottles_running", lambda: True)
    result = be.export_game_to_bottle(game, bottle_of(directory))
    assert result.warnings == [be.WARNING_BOTTLES_RUNNING]
    # y compris quand le programme existait déjà
    again = be.export_game_to_bottle(game, bottle_of(directory))
    assert again.status == "already_present" and be.WARNING_BOTTLES_RUNNING in again.warnings


def test_bottles_running_detects_the_process(monkeypatch):
    psutil = pytest.importorskip("psutil")
    be_running = be.bottles_running.__wrapped__ if hasattr(be.bottles_running, "__wrapped__") \
        else be.bottles_running

    class P:
        def __init__(self, pid, name, cmdline):
            self.info = {"pid": pid, "name": name, "cmdline": cmdline}

    monkeypatch.setattr(psutil, "process_iter", lambda _attrs: iter([
        P(1, "systemd", ["/sbin/init"]), P(2, "python3", ["python3", "x.py"])]))
    assert be_running() is False
    monkeypatch.setattr(psutil, "process_iter", lambda _attrs: iter([
        P(1, "systemd", []), P(3, "bottles", ["bottles"])]))
    assert be_running() is True
    monkeypatch.setattr(psutil, "process_iter", lambda _attrs: iter([
        P(4, "python3", ["python3", "/app/bin/bottles"])]))
    assert be_running() is True
