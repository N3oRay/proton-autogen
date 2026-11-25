"""Tests de l'outil de compatibilité Steam (install-steam + wrapper)."""

import importlib.util
import os
import stat
from pathlib import Path

import pytest

from proton_autogen import steam_compat as sc
from proton_autogen.cli import (
    EXIT_OK, EXIT_USAGE, CliError, build_parser, main, normalize_argv,
    split_game_args,
)

ASSETS = Path(sc.__file__).resolve().parent / "steam_assets"


@pytest.fixture
def launcher(tmp_path):
    path = tmp_path / "bin" / "proton-autogen"
    path.parent.mkdir()
    path.write_text("#!/bin/sh\necho RUN: $@\n")
    path.chmod(0o755)
    return path


@pytest.fixture
def tools_dir(tmp_path):
    return tmp_path / "steam" / "compatibilitytools.d"


def do_install(tools_dir, launcher, **kw):
    return sc.install(dest_root=tools_dir, launcher=str(launcher),
                      out=lambda _msg: None, **kw)


# --- assets ----------------------------------------------------------------- #

def test_assets_are_complete():
    for name in sc.ASSET_FILES + sc.MODULE_FILES:
        assert (ASSETS / name).is_file(), name


def test_toolmanifest_uses_verb_placeholder():
    text = (ASSETS / "toolmanifest.vdf").read_text()
    assert '"/proton %verb%"' in text
    assert "require_tool_appid" not in text  # doit tourner sur l'hôte


def test_compatibilitytool_vdf_declares_the_tool():
    text = (ASSETS / "compatibilitytool.vdf").read_text()
    assert '"compat_tools"' in text and f'"{sc.TOOL_NAME}"' in text
    assert '"install_path" "."' in text


# --- installation ------------------------------------------------------------ #

def test_install_creates_everything_and_verifies(tools_dir, launcher):
    dest = do_install(tools_dir, launcher)
    assert dest == tools_dir / "Proton-Autogen"
    for name in sc.MANAGED + (sc.MANIFEST_FILE,):
        assert (dest / name).is_file(), name
    assert os.access(dest / "proton", os.X_OK)
    assert not (dest / "toolmanifest.vdf").stat().st_mode & stat.S_IXUSR
    assert (dest / "launcher.path").read_text().strip() == str(launcher.resolve())
    assert sc.verify(dest) == []


def test_install_is_idempotent(tools_dir, launcher):
    do_install(tools_dir, launcher)
    messages = []
    sc.install(dest_root=tools_dir, launcher=str(launcher), out=messages.append)
    assert any("up to date" in m for m in messages)


def test_modified_file_needs_confirmation_outside_a_terminal(
        tools_dir, launcher, monkeypatch):
    dest = do_install(tools_dir, launcher)
    mine = dest / "toolmanifest.vdf"
    mine.write_text(mine.read_text() + "# mine\n")
    monkeypatch.setattr("sys.stdin.isatty", lambda: False, raising=False)
    with pytest.raises(sc.SteamInstallError) as exc:
        do_install(tools_dir, launcher)
    assert exc.value.code == sc.EXIT_ABORTED
    assert "# mine" in mine.read_text()  # rien d'écrasé


def test_yes_replaces_and_keeps_a_backup(tools_dir, launcher):
    dest = do_install(tools_dir, launcher)
    mine = dest / "toolmanifest.vdf"
    mine.write_text("custom\n")
    do_install(tools_dir, launcher, assume_yes=True)
    assert sc.verify(dest) == []
    backups = list(dest.glob("toolmanifest.vdf.bak-*"))
    assert len(backups) == 1 and backups[0].read_text() == "custom\n"


def test_refusal_at_prompt_changes_nothing(tools_dir, launcher, monkeypatch):
    dest = do_install(tools_dir, launcher)
    mine = dest / "proton"
    mine.write_text("#!/bin/sh\n# custom\n")
    monkeypatch.setattr("sys.stdin.isatty", lambda: True, raising=False)
    monkeypatch.setattr("builtins.input", lambda _prompt: "n")
    with pytest.raises(sc.SteamInstallError) as exc:
        do_install(tools_dir, launcher)
    assert exc.value.code == sc.EXIT_ABORTED
    assert "# custom" in mine.read_text()


def test_unknown_user_files_are_preserved(tools_dir, launcher):
    dest = do_install(tools_dir, launcher)
    (dest / "user_settings.py").write_text("X = 1\n")
    (dest / "proton").write_text("changed\n")
    do_install(tools_dir, launcher, assume_yes=True)
    assert (dest / "user_settings.py").read_text() == "X = 1\n"


def test_steam_missing_is_reported(tmp_path, launcher, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path / "nohome"))
    with pytest.raises(sc.SteamInstallError):
        sc.install(launcher=str(launcher), out=lambda _m: None)


# --- verification ------------------------------------------------------------ #

def test_verify_detects_permissions_and_tampering(tools_dir, launcher):
    dest = do_install(tools_dir, launcher)
    (dest / "proton").chmod(0o644)
    problems = sc.verify(dest)
    assert any("not executable" in p for p in problems)
    (dest / "proton").chmod(0o755)
    (dest / "autogen_wrapper.py").write_text("# tampered\n")
    assert any("checksum" in p for p in sc.verify(dest))
    (dest / "autogen_wrapper.py").unlink()
    assert any("missing file" in p for p in sc.verify(dest))


def test_verify_detects_world_writable(tools_dir, launcher):
    dest = do_install(tools_dir, launcher)
    (dest / "proton").chmod(0o757)
    assert any("world-writable" in p for p in sc.verify(dest))


def test_check_mode_reports_integrity_exit_code(tools_dir, launcher):
    dest = do_install(tools_dir, launcher)
    (dest / "proton").chmod(0o644)
    with pytest.raises(sc.SteamInstallError) as exc:
        sc.run_install_steam(dest=tools_dir, check=True, out=lambda _m: None)
    assert exc.value.code == sc.EXIT_INTEGRITY


# --- détection : le wrapper ne doit jamais être choisi comme Proton ---------- #

def test_is_wrapper_dir(tools_dir, launcher, tmp_path):
    dest = do_install(tools_dir, launcher)
    assert sc.is_wrapper_dir(dest)
    real = tmp_path / "GE-Proton10-34"
    real.mkdir()
    (real / "proton").write_text("#!/usr/bin/env python3\n")
    assert not sc.is_wrapper_dir(real)


def test_proton_detection_ignores_the_wrapper(tools_dir, launcher, monkeypatch):
    from proton_autogen import backend, diag

    do_install(tools_dir, launcher)
    real = tools_dir / "GE-Proton10-34"
    real.mkdir()
    (real / "proton").write_text("")
    for module in (diag, backend):
        monkeypatch.setattr(module, "load_proton_paths", lambda: [str(tools_dir)])
    monkeypatch.setattr(diag, "find_system_proton", lambda: None)

    assert [os.path.basename(p) for p in diag.find_all_protons()] == ["GE-Proton10-34"]
    assert diag.find_proton()["name"] == "GE-Proton10-34"
    assert backend.find_proton_by_name("Proton-Autogen") is None


# --- CLI ---------------------------------------------------------------------- #

@pytest.mark.parametrize("argv, head, game_args", [
    (["run", "--steam", "--", "g.exe", "-windowed"],
     ["run", "--steam", "--", "g.exe"], ["-windowed"]),
    (["run", "--steam", "--", "g.exe", "--help", "--v", "--ux"],
     ["run", "--steam", "--", "g.exe"], ["--help", "--v", "--ux"]),
    (["run", "--steam", "--", "g.exe"], ["run", "--steam", "--", "g.exe"], []),
    (["--", "add"], ["--", "add"], []),
    (["g.exe", "--wine"], ["g.exe", "--wine"], []),
])
def test_split_game_args(argv, head, game_args):
    assert split_game_args(argv) == (head, game_args)


def test_game_args_never_trigger_legacy_routing(monkeypatch):
    seen = {}

    def fake_run(file, launch_mode, prefix_mode, **kw):
        seen.update(file=file, **kw)
        return 0

    monkeypatch.setattr("proton_autogen.backend.run", fake_run)
    code = main(["run", "--steam", "--", "g.exe", "--help", "-windowed"])
    assert code == EXIT_OK
    assert seen == {"file": "g.exe", "game_args": ["--help", "-windowed"],
                    "from_steam": True}


def test_run_without_game_args_is_unchanged(monkeypatch):
    seen = {}
    monkeypatch.setattr(
        "proton_autogen.backend.run",
        lambda file, lm, pm, **kw: seen.update(file=file, **kw) or 0)
    assert main(["g.exe", "--wine"]) == EXIT_OK
    assert seen == {"file": "g.exe"}  # appel identique à l'ancien contrat


def test_game_args_rejected_for_other_commands():
    assert main(["add", "--", "g.exe", "extra"]) == EXIT_USAGE


def test_install_steam_is_a_command():
    assert "install-steam" in build_parser().command_names
    assert normalize_argv(["install-steam", "--check"],
                          build_parser().command_names) == ["install-steam", "--check"]


def test_install_steam_error_becomes_exit_code(monkeypatch, capsys):
    def boom(**_kw):
        raise sc.SteamInstallError("nope", sc.EXIT_INTEGRITY)

    monkeypatch.setattr(sc, "run_install_steam", boom)
    assert main(["install-steam", "--check"]) == sc.EXIT_INTEGRITY
    assert "nope" in capsys.readouterr().err


# --- wrapper ------------------------------------------------------------------ #

@pytest.fixture
def wrapper():
    spec = importlib.util.spec_from_file_location(
        "autogen_wrapper_under_test", ASSETS / "autogen_wrapper.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_wrapper_builds_the_expected_command(wrapper, launcher, monkeypatch):
    calls = []
    monkeypatch.setenv("PROTON_AUTOGEN_BIN", str(launcher))
    monkeypatch.delenv("PROTON_AUTOGEN_WRAPPER_ACTIVE", raising=False)
    monkeypatch.setattr(wrapper.os, "execv", lambda path, argv: calls.append((path, argv)))
    wrapper.main(["waitforexitandrun", "/g/foo.exe", "--help", "-windowed"])
    assert calls == [(str(launcher), [str(launcher), "run", "--steam", "--",
                                      "/g/foo.exe", "--help", "-windowed"])]
    assert os.environ["PROTON_AUTOGEN_FROM_STEAM"] == "1"
    monkeypatch.delenv("PROTON_AUTOGEN_FROM_STEAM")
    monkeypatch.delenv("PROTON_AUTOGEN_WRAPPER_ACTIVE")


def test_wrapper_refuses_recursion(wrapper, launcher, monkeypatch):
    monkeypatch.setenv("PROTON_AUTOGEN_BIN", str(launcher))
    monkeypatch.setenv("PROTON_AUTOGEN_WRAPPER_ACTIVE", "1")
    monkeypatch.setattr(wrapper.os, "execv",
                        lambda *_a: pytest.fail("must not exec"))
    assert wrapper.main(["run", "/g/foo.exe"]) == 1


def test_wrapper_misc_verbs(wrapper, capsys):
    assert wrapper.main([]) == wrapper.EXIT_USAGE
    assert wrapper.main(["bogus", "x"]) == wrapper.EXIT_USAGE
    assert wrapper.main(["run"]) == wrapper.EXIT_USAGE
    assert wrapper.main(["destroyprefix"]) == 0
    assert wrapper.main(["getcompatpath", "/x/y"]) == 0
    assert capsys.readouterr().out.strip() == "/x/y"


def test_wrapper_without_launcher(wrapper, monkeypatch):
    monkeypatch.delenv("PROTON_AUTOGEN_BIN", raising=False)
    monkeypatch.delenv("PROTON_AUTOGEN_WRAPPER_ACTIVE", raising=False)
    monkeypatch.setattr(wrapper.shutil, "which", lambda _n: None)
    monkeypatch.setattr(wrapper, "LAUNCHER_FILE", "/nonexistent/launcher.path")
    assert wrapper.main(["run", "/g/foo.exe"]) == wrapper.EXIT_LAUNCHER_MISSING
