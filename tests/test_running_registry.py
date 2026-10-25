"""
Tests du suivi inter-processus (running_registry + process_manager).

Les tests utilisent de VRAIS processus (sleep) et un second interpréteur
Python qui joue le rôle du « CLI » : il enregistre un jeu puis meurt sans
le terminer, exactement comme un Ctrl+C sur `proton-autogen game.exe`.
Aucune dépendance GTK.
"""

import hashlib
import os
import signal
import subprocess
import sys
import textwrap
import time

import pytest

from proton_autogen import process_manager, running_registry

pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# Outils
# ---------------------------------------------------------------------------

def gid(path):
    return hashlib.md5(path.encode()).hexdigest()


def wait_until(predicate, timeout=5.0):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(0.05)
    return predicate()


def pid_alive(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    # un zombie répond encore : on regarde l'état
    try:
        with open(f"/proc/{pid}/stat") as f:
            return f.read().rsplit(")", 1)[1].split()[0] != "Z"
    except OSError:
        return False


@pytest.fixture(autouse=True)
def isolated_registry(tmp_path, monkeypatch):
    """Chaque test a son propre dossier de données (jamais le vrai)."""
    monkeypatch.setenv("PROTON_AUTOGEN_STATE_DIR", str(tmp_path / "state"))
    process_manager._pgrep_cache.clear()
    yield


@pytest.fixture
def spawned():
    """Lance des sleep dans leur propre session ; nettoyage garanti."""
    procs = []

    def _spawn(*extra):
        p = subprocess.Popen(
            ["sleep", "60"] + list(extra), start_new_session=True,
        )
        procs.append(p)
        return p

    yield _spawn

    for p in procs:
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except OSError:
            pass
        try:
            p.wait(timeout=2)
        except Exception:
            pass


def run_fake_cli(exe_path, extra_code=""):
    """
    Simule `proton-autogen game.exe` : un AUTRE processus Python lance un
    jeu (sleep), l'enregistre via process_manager, puis meurt brutalement
    sans le terminer. Retourne le PID du « jeu ».
    """
    code = textwrap.dedent(f"""
        import os, subprocess, sys
        from proton_autogen import process_manager
        p = subprocess.Popen(["sleep", "60"], start_new_session=True,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        ok = process_manager.register({gid(exe_path)!r}, p, exe_path={exe_path!r})
        {extra_code}
        print(p.pid, flush=True)
        os._exit(0)   # mort brutale : ni finally, ni unregister
    """)
    out = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, timeout=15, env=os.environ.copy(),
    )
    assert out.returncode == 0, out.stderr
    return int(out.stdout.strip().splitlines()[-1])


# ---------------------------------------------------------------------------
# running_registry : fichiers
# ---------------------------------------------------------------------------

def test_write_read_remove_roundtrip(spawned):
    p = spawned()
    assert running_registry.write("abc123", pid=p.pid, exe_path="/g/game.exe", name="game")

    rec = running_registry.read("abc123")
    assert rec.pid == p.pid
    assert rec.pgid == p.pid            # start_new_session
    assert rec.exe_path == "/g/game.exe"
    assert rec.owner_pid == os.getpid()

    assert running_registry.remove("abc123") is True
    assert running_registry.read("abc123") is None


def test_file_permissions_are_private(spawned):
    p = spawned()
    running_registry.write("perm1", pid=p.pid)
    path = running_registry.registry_dir() / "running-perm1.json"
    assert (path.stat().st_mode & 0o777) == 0o600


def test_no_new_directory_is_created(spawned):
    """Fichiers à plat : aucun sous-dossier (pas de « running/ »)."""
    directory = running_registry.registry_dir()
    p = spawned()
    running_registry.write("flat1", pid=p.pid)
    running_registry.write("flat2", pid=p.pid)

    entries = sorted(e.name for e in directory.iterdir())
    assert entries == ["running-flat1.json", "running-flat2.json"]
    assert all(e.is_file() for e in directory.iterdir())

    running_registry.remove("flat1")
    running_registry.remove("flat2")
    assert list(directory.iterdir()) == []      # aucun fichier temporaire résiduel


def test_default_location_is_existing_data_dir(monkeypatch, tmp_path):
    """Sans surcharge : ~/.local/share/proton-autogen (même racine que logs/)."""
    monkeypatch.delenv("PROTON_AUTOGEN_STATE_DIR")
    monkeypatch.setenv("HOME", str(tmp_path))
    assert running_registry.registry_dir() == tmp_path / ".local/share/proton-autogen"


def test_other_files_in_data_dir_are_left_alone(spawned):
    """logs/, backups/ et fichiers étrangers ne sont ni lus ni supprimés."""
    directory = running_registry.registry_dir()
    (directory / "logs").mkdir(parents=True)
    (directory / "backups").mkdir()
    (directory / "autre.json").write_text('{"game_id": "autre", "pid": 1}')

    p = spawned()
    running_registry.write("mine", pid=p.pid)
    os.killpg(p.pid, signal.SIGKILL)
    p.wait()

    assert running_registry.purge_stale() == 1
    assert (directory / "logs").is_dir()
    assert (directory / "backups").is_dir()
    assert (directory / "autre.json").exists()
    assert set(running_registry.list_records()) == set()


@pytest.mark.parametrize("bad_id", ["", "../evil", "a/b", "x" * 200, "has space", None])
def test_invalid_game_id_is_rejected(bad_id):
    assert running_registry.write(bad_id, pid=os.getpid()) is False
    assert running_registry.read(bad_id) is None
    assert running_registry.remove(bad_id) is False


def test_corrupted_files_are_ignored():
    d = running_registry.registry_dir()
    d.mkdir(parents=True)
    (d / "running-broken.json").write_text("{pas du json")
    (d / "running-wrongtype.json").write_text('["liste"]')
    (d / "running-mismatch.json").write_text('{"game_id": "autre", "pid": 1}')
    (d / "running-nopid.json").write_text('{"game_id": "nopid"}')
    (d / "running-bad id.json").write_text('{"game_id": "bad id", "pid": 1}')
    assert running_registry.list_records() == {}


# ---------------------------------------------------------------------------
# running_registry : vivacité
# ---------------------------------------------------------------------------

def test_alive_then_dead(spawned):
    p = spawned()
    running_registry.write("live1", pid=p.pid)
    rec = running_registry.read("live1")
    assert running_registry.is_alive(rec)

    os.killpg(p.pid, signal.SIGKILL)
    p.wait()
    assert not running_registry.is_alive(rec)


def test_pid_reuse_is_detected(spawned):
    p = spawned()
    running_registry.write("reuse1", pid=p.pid)
    rec = running_registry.read("reuse1")
    rec.start_time = (rec.start_time or time.time()) - 3600   # « autre » processus

    assert running_registry.pid_was_reused(rec)
    assert not running_registry.is_alive(rec)


def test_group_alive_when_main_pid_dead(spawned):
    """Le Popen local meurt avant le vrai jeu (cas flatpak-spawn/gamescope)."""
    leader = subprocess.Popen(
        ["bash", "-c", "sleep 60 & echo $!; exit 0"],
        start_new_session=True, stdout=subprocess.PIPE, text=True,
    )
    child_pid = int(leader.stdout.readline())
    leader.wait()
    try:
        running_registry.write("grp1", pid=leader.pid, pgid=leader.pid)
        rec = running_registry.read("grp1")
        assert not running_registry._pid_exists(leader.pid)
        assert running_registry.is_alive(rec)       # le groupe a encore sleep
    finally:
        os.kill(child_pid, signal.SIGKILL)


def test_purge_stale_removes_dead_records(spawned):
    alive = spawned()
    dead = spawned()
    running_registry.write("alive1", pid=alive.pid)
    running_registry.write("dead1", pid=dead.pid)
    os.killpg(dead.pid, signal.SIGKILL)
    dead.wait()

    assert running_registry.purge_stale() == 1
    assert set(running_registry.list_records()) == {"alive1"}


# ---------------------------------------------------------------------------
# process_manager : le scénario du bug (CLI -> UX)
# ---------------------------------------------------------------------------

def test_game_launched_by_other_process_is_visible():
    exe = "/games/FakeGame/game.exe"
    pid = run_fake_cli(exe)
    try:
        # Mémoire locale vide : c'est ce que voyait l'UX avant le correctif
        assert process_manager.get(gid(exe)) is None

        external = process_manager.list_external()
        assert gid(exe) in external
        info = external[gid(exe)]
        assert info["pid"] == pid
        assert info["external"] is True
        assert info["name"] == "game"

        assert process_manager.is_running(gid(exe)) is True
        assert process_manager.get_info(gid(exe))["pid"] == pid
    finally:
        try:
            os.killpg(pid, signal.SIGKILL)
        except OSError:
            pass


def test_stop_from_other_process_kills_game_and_cleans_registry():
    exe = "/games/FakeGame/stopme.exe"
    pid = run_fake_cli(exe)

    assert pid_alive(pid)
    assert process_manager.stop(gid(exe), timeout=3.0) is True

    assert wait_until(lambda: not pid_alive(pid))
    assert running_registry.read(gid(exe)) is None
    assert gid(exe) not in process_manager.list_external()
    assert process_manager.is_running(gid(exe)) is False


def test_force_stop_external():
    exe = "/games/FakeGame/force.exe"
    pid = run_fake_cli(exe)

    assert process_manager.force_stop(gid(exe)) is True
    assert wait_until(lambda: not pid_alive(pid))
    assert running_registry.read(gid(exe)) is None


def test_finished_game_disappears_from_external_list():
    exe = "/games/FakeGame/short.exe"
    pid = run_fake_cli(exe)
    os.killpg(pid, signal.SIGKILL)
    assert wait_until(lambda: not pid_alive(pid))

    assert process_manager.list_external() == {}
    assert running_registry.read(gid(exe)) is None   # purgé à la lecture


def test_own_games_are_not_reported_as_external(spawned):
    """Un jeu lancé par CE processus relève du registre mémoire."""
    p = spawned()
    exe = "/games/FakeGame/mine.exe"
    assert process_manager.register(gid(exe), p, exe_path=exe) is True
    try:
        assert gid(exe) not in process_manager.list_external()
        assert process_manager.is_running(gid(exe)) is True
        assert running_registry.read(gid(exe)) is not None   # visible des autres
    finally:
        process_manager.stop(gid(exe), timeout=2.0)

    assert running_registry.read(gid(exe)) is None


def test_unregister_keeps_record_if_game_still_runs(spawned):
    """CLI interrompu (Ctrl+C) alors que le jeu continue : il reste visible."""
    p = spawned()
    exe = "/games/FakeGame/orphan.exe"
    process_manager.register(gid(exe), p, exe_path=exe)

    process_manager.unregister(gid(exe), p)          # le finally du CLI
    assert process_manager.get(gid(exe)) is None
    assert running_registry.read(gid(exe)) is not None   # conservé

    os.killpg(p.pid, signal.SIGKILL)
    p.wait()


def test_unregister_removes_record_when_game_ended(spawned):
    p = spawned()
    exe = "/games/FakeGame/normal.exe"
    process_manager.register(gid(exe), p, exe_path=exe)

    os.killpg(p.pid, signal.SIGKILL)
    p.wait()
    process_manager.unregister(gid(exe), p)

    assert running_registry.read(gid(exe)) is None


# ---------------------------------------------------------------------------
# Garde-fous
# ---------------------------------------------------------------------------

def test_stop_never_signals_own_process_group(monkeypatch):
    """Un enregistrement avec notre propre pgid ne doit rien tuer."""
    exe = "/games/FakeGame/selfgroup.exe"
    running_registry.write(
        gid(exe), pid=os.getpid(), pgid=os.getpgrp(),
        owner_pid=os.getpid() + 100000, exe_path=None,
    )

    sent = []
    monkeypatch.setattr(os, "killpg", lambda *a: sent.append(a))

    assert process_manager.stop(gid(exe), timeout=0.1) is True
    assert sent == []    # killpg jamais appelé


@pytest.mark.parametrize("pgid", [0, 1, -5])
def test_safe_pgid_refuses_system_groups(pgid):
    rec = running_registry.RegistryRecord(game_id="x", pid=123, pgid=pgid)
    assert process_manager._safe_external_pgid(rec) is None


def test_stray_kill_ignores_proton_autogen_itself(tmp_path):
    """
    `proton-autogen game.exe` contient le nom de l'exe : pgrep -f le trouve,
    il ne doit jamais être tué comme « reste » du jeu.
    """
    launcher = tmp_path / "proton-autogen"
    launcher.write_text("import time; time.sleep(60)\n")
    other = tmp_path / "unrelated-tool"
    other.write_text("import time; time.sleep(60)\n")

    exe_name = "uniquegame_xyz.exe"
    p_launcher = subprocess.Popen([sys.executable, str(launcher), exe_name])
    p_other = subprocess.Popen([sys.executable, str(other), exe_name])
    try:
        time.sleep(0.4)
        pids = process_manager._find_pids_by_exe(f"/g/{exe_name}", use_cache=False)
        assert p_launcher.pid not in pids
        assert p_other.pid in pids
    finally:
        for p in (p_launcher, p_other):
            p.kill()
            p.wait()
