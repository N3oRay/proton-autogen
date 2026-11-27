"""Tests de utils/open_folder.py (« Ouvrir Dossier »)."""

import stat

import pytest

from proton_autogen.utils import open_folder as of


def make_opener(directory, name, body):
    """Crée un faux exécutable `name` dans `directory` (script shell)."""
    directory.mkdir(exist_ok=True)
    script = directory / name
    script.write_text("#!/bin/sh\n" + body)
    script.chmod(script.stat().st_mode | stat.S_IXUSR)
    return script


@pytest.fixture
def game(tmp_path):
    exe = tmp_path / "Games" / "Alerte Rouge" / "RA.EXE"
    exe.parent.mkdir(parents=True)
    exe.write_bytes(b"MZ")
    return {"name": "Alerte Rouge", "path": str(exe)}


@pytest.fixture
def only_fakes_on_path(tmp_path, monkeypatch):
    """PATH réduit à un dossier de faux outils (et aux commandes de base)."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    monkeypatch.setenv("PATH", f"{bin_dir}:/usr/bin:/bin")
    # Les vrais xdg-open / gio du système ne doivent jamais être lancés.
    monkeypatch.setattr(of.shutil, "which",
                        lambda cmd: str(bin_dir / cmd) if (bin_dir / cmd).exists() else None)
    return bin_dir


# --- game_folder -------------------------------------------------------------------- #

def test_game_folder_is_the_directory_of_the_executable(game):
    assert of.game_folder(game) == of.Path(game["path"]).parent


def test_game_folder_accepts_a_plain_path_and_a_directory(game, tmp_path):
    assert of.game_folder(game["path"]) == of.Path(game["path"]).parent
    assert of.game_folder(tmp_path / "Games") == tmp_path / "Games"


def test_game_folder_when_the_executable_is_gone_but_the_folder_exists(game):
    of.Path(game["path"]).unlink()
    assert of.game_folder(game) == of.Path(game["path"]).parent


def test_game_folder_expands_home_and_variables(game, tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("GAMES_DIR", str(tmp_path / "Games"))
    assert of.game_folder("~/Games/Alerte Rouge/RA.EXE") == of.Path(game["path"]).parent
    assert of.game_folder("$GAMES_DIR/Alerte Rouge/RA.EXE") == of.Path(game["path"]).parent


@pytest.mark.parametrize("value", [None, ""])
def test_game_folder_without_path(value):
    with pytest.raises(of.OpenFolderError):
        of.game_folder({"name": "x", "path": value})


def test_game_folder_missing_directory(tmp_path):
    with pytest.raises(of.OpenFolderError, match="folder not found"):
        of.game_folder(tmp_path / "gone" / "game.exe")


# --- open_folder -------------------------------------------------------------------- #

def test_open_folder_runs_xdg_open_with_the_folder(game, tmp_path, only_fakes_on_path):
    log = tmp_path / "log"
    make_opener(only_fakes_on_path, "xdg-open", f'printf "%s" "$1" > "{log}"\n')
    folder = of.game_folder(game)
    assert of.open_folder(folder) == "xdg-open"
    assert log.read_text() == str(folder)   # espaces dans le chemin conservés


def test_falls_back_to_gio_when_xdg_open_fails(game, tmp_path, only_fakes_on_path):
    log = tmp_path / "log"
    make_opener(only_fakes_on_path, "xdg-open", "exit 3\n")
    make_opener(only_fakes_on_path, "gio", f'printf "%s %s" "$1" "$2" > "{log}"\n')
    folder = of.game_folder(game)
    assert of.open_folder(folder) == "gio open"
    assert log.read_text() == f"open {folder}"


def test_a_file_manager_that_keeps_running_is_a_success(game, only_fakes_on_path, monkeypatch):
    monkeypatch.setattr(of, "LAUNCH_GRACE_SECONDS", 0.2)
    make_opener(only_fakes_on_path, "xdg-open", "sleep 3\n")
    assert of.open_folder(of.game_folder(game)) == "xdg-open"


def test_no_opener_available(game, only_fakes_on_path):
    with pytest.raises(of.OpenFolderError, match="xdg-utils"):
        of.open_folder(of.game_folder(game))


def test_every_opener_failing_reports_each_attempt(game, only_fakes_on_path):
    make_opener(only_fakes_on_path, "xdg-open", "exit 3\n")
    make_opener(only_fakes_on_path, "gio", "exit 1\n")
    with pytest.raises(of.OpenFolderError) as exc:
        of.open_folder(of.game_folder(game))
    assert "xdg-open: exit code 3" in str(exc.value) and "gio: exit code 1" in str(exc.value)


def test_unlaunchable_opener_is_skipped(game, tmp_path, only_fakes_on_path):
    log = tmp_path / "log"
    broken = only_fakes_on_path / "xdg-open"
    broken.write_text("not executable")        # which() le trouve, Popen échoue
    make_opener(only_fakes_on_path, "gio", f'printf ok > "{log}"\n')
    assert of.open_folder(of.game_folder(game)) == "gio open"


def test_open_folder_rejects_a_missing_folder(tmp_path):
    with pytest.raises(of.OpenFolderError):
        of.open_folder(tmp_path / "gone")


def test_open_game_folder_end_to_end(game, tmp_path, only_fakes_on_path):
    log = tmp_path / "log"
    make_opener(only_fakes_on_path, "xdg-open", f'printf "%s" "$1" > "{log}"\n')
    folder = of.open_game_folder(game)
    assert folder == of.Path(game["path"]).parent and log.read_text() == str(folder)
