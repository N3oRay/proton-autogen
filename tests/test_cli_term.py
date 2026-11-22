"""Tests de la couche CLI (aucun GTK requis : les handlers sont simulés)."""

import pytest

from proton_autogen import cli
from proton_autogen.cli import (
    EXIT_ERROR, EXIT_INTERRUPTED, EXIT_NOT_FOUND, EXIT_OK, EXIT_USAGE,
    CliError, build_parser, main, normalize_argv,
)

NAMES = build_parser().command_names


def norm(*argv):
    return normalize_argv(list(argv), NAMES)


# --- normalisation des anciennes formes ------------------------------------ #

@pytest.mark.parametrize("argv, expected", [
    (["game.exe"], ["run", "game.exe"]),
    (["--wine", "game.exe"], ["run", "--wine", "game.exe"]),
    (["game.exe", "--wine"], ["run", "game.exe", "--wine"]),
    (["run", "game.exe"], ["run", "game.exe"]),
    (["--profile", "p", "add", "g.exe"], ["add", "--profile", "p", "g.exe"]),
    (["--profile", "p", "g.exe"], ["run", "--profile", "p", "g.exe"]),
    (["--ux"], ["ux"]),
    (["--UX"], ["ux"]),
    (["--lp"], ["list-protons"]),
    (["--v"], ["version"]),
    (["-h"], ["help"]),
    (["--", "add"], ["run", "--", "add"]),
    (["game.exe", "--import"], ["import"]),
])
def test_normalize_argv(argv, expected):
    assert norm(*argv) == expected


def test_every_legacy_flag_targets_a_real_command():
    for _flags, command in cli._LEGACY_FLAGS:
        assert command in NAMES


# --- parsing ---------------------------------------------------------------- #

def parse(*argv):
    return build_parser().parse_args(norm(*argv))


def test_run_defaults():
    args = parse("game.exe")
    assert (args.launch_mode, args.prefix_mode) == ("proton", "main")


def test_run_modes():
    args = parse("game.exe", "--call", "--pa")
    assert (args.launch_mode, args.prefix_mode) == ("proton-call", "auto")


def test_conflicting_modes_are_a_usage_error():
    assert main(["game.exe", "--wine", "--call"]) == EXIT_USAGE


# --- codes de sortie et gestion d'erreurs ----------------------------------- #

def test_no_arguments_is_a_usage_error(capsys):
    assert main([]) == EXIT_USAGE
    assert "usage" in capsys.readouterr().err.lower()


def test_unknown_option_is_a_usage_error(capsys):
    assert main(["run", "--nope", "game.exe"]) == EXIT_USAGE
    assert "--help" in capsys.readouterr().err


def test_missing_file_argument(capsys):
    assert main(["add"]) == EXIT_USAGE


def test_run_dispatch(monkeypatch):
    calls = []
    monkeypatch.setattr("proton_autogen.backend.run", lambda *a: calls.append(a))
    assert main(["game.exe", "--wine", "--ps"]) == EXIT_OK
    assert calls == [("game.exe", "wine", "shared")]


def test_handler_int_result_is_the_exit_code(monkeypatch):
    monkeypatch.setattr("proton_autogen.backend.run", lambda *a: 7)
    assert main(["run", "game.exe"]) == 7


def test_add_missing_file(tmp_path, capsys):
    assert main(["add", str(tmp_path / "absent.exe")]) == EXIT_NOT_FOUND
    assert "file not found" in capsys.readouterr().err


def test_add_existing_file(tmp_path, monkeypatch):
    exe = tmp_path / "game.exe"
    exe.write_text("")
    calls = []
    monkeypatch.setattr("proton_autogen.editor.add_game", lambda p: calls.append(p))
    assert main(["add", str(exe)]) == EXIT_OK
    assert calls == [str(exe)]


@pytest.mark.parametrize("exc, code", [
    (CliError("boom", 5), 5),
    (KeyboardInterrupt(), EXIT_INTERRUPTED),
    (SystemExit(4), 4),
    (SystemExit(None), EXIT_OK),
    (RuntimeError("kaboom"), EXIT_ERROR),
])
def test_central_error_handling(monkeypatch, exc, code):
    def boom(args):
        raise exc
    monkeypatch.setattr(cli, "_cmd_list_programs", boom)
    assert main(["list-programs"]) == code


def test_unexpected_error_hides_traceback_unless_debug(monkeypatch, capsys):
    def boom(args):
        raise RuntimeError("kaboom")
    monkeypatch.setattr(cli, "_cmd_list_programs", boom)

    main(["list-programs"])
    err = capsys.readouterr().err
    assert "kaboom" in err and "Traceback" not in err

    main(["list-programs", "--debug"])
    assert "Traceback" in capsys.readouterr().err


def test_version(capsys):
    assert main(["--version"]) == EXIT_OK
    assert capsys.readouterr().out.startswith("proton-autogen ")
