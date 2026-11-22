import pytest

from proton_autogen import cli_import
from proton_autogen.cli import EXIT_ERROR, EXIT_OK, CliError

RESULTS = {"lutris": {"items": [{"name": "Zelda"}, {"name": "alpha", "needs_manual_exe": True}]}}


@pytest.fixture
def patched(monkeypatch):
    imported = []
    monkeypatch.setattr(cli_import, "scan_all", lambda: dict(RESULTS))
    monkeypatch.setattr(cli_import, "any_source_available", lambda r: True)
    monkeypatch.setattr(cli_import, "total_count", lambda r: 2)
    monkeypatch.setattr(
        cli_import, "import_selected",
        lambda r, enabled: imported.append(enabled) or {"imported": 2, "skipped": 0, "errors": []},
    )
    return imported


def test_confirmation_declined(patched):
    out = []
    assert cli_import.run_import(input_fn=lambda p: "n", print_fn=out.append) == EXIT_OK
    assert patched == [] and "Cancelled." in out


def test_confirmation_accepted(patched):
    assert cli_import.run_import(input_fn=lambda p: "oui", print_fn=lambda *_: None) == EXIT_OK
    assert patched == [{"lutris"}]


def test_yes_flag_never_prompts(patched):
    def no_prompt(_):
        raise AssertionError("prompted")
    assert cli_import.run_import(assume_yes=True, input_fn=no_prompt, print_fn=lambda *_: None) == EXIT_OK


def test_errors_give_nonzero_exit(patched, monkeypatch):
    monkeypatch.setattr(
        cli_import, "import_selected",
        lambda r, e: {"imported": 1, "skipped": 0, "errors": [{"exe": "a.exe", "error": "x"}]},
    )
    assert cli_import.run_import(assume_yes=True, print_fn=lambda *_: None) == EXIT_ERROR


def test_no_terminal(patched):
    def eof(_):
        raise EOFError
    with pytest.raises(CliError):
        cli_import.run_import(input_fn=eof, print_fn=lambda *_: None)
