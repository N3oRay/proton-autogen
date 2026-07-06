import subprocess
import pytest


# ----------------------------
# CONFIGURATION
# ----------------------------

CLI_CMD = ["proton-autogen"]  # ou ["python", "-m", "proton_autogen"]


# ----------------------------
# CORE HELPER
# ----------------------------

def run_cli(args, timeout=5):
    """
    Exécute la commande CLI et retourne le résultat.
    """
    return subprocess.run(
        CLI_CMD + args,
        capture_output=True,
        text=True,
        timeout=timeout
    )


# ----------------------------
# HELPERS ASSERTIONS
# ----------------------------

def assert_success(result):
    assert result.returncode == 0, (
        f"Command failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )


def assert_no_crash(result):
    assert result.returncode is not None


def assert_clean_stderr(result):
    # On autorise stderr vide par défaut (modifiable si warnings attendus)
    assert result.stderr.strip() == ""


# ----------------------------
# TESTS CLI
# ----------------------------

def test_help():
    result = run_cli(["--help"])

    assert_success(result)
    assert_no_crash(result)

    # Indices classiques d'un help CLI
    assert "usage" in result.stdout.lower() or "help" in result.stdout.lower()


def test_help_env():
    result = run_cli(["--help-env"])

    assert_success(result)
    assert_no_crash(result)

    # On vérifie qu'il y a du contenu
    assert len(result.stdout.strip()) > 0

    # Optionnel : mots clés attendus
    # adapte selon ton projet
    keywords = ["PROTON", "WINE", "STEAM"]
    assert any(k in result.stdout.upper() for k in keywords)


def test_diag():
    result = run_cli(["--diag"])

    assert_success(result)
    assert_no_crash(result)

    # Diagnostic ne doit jamais être vide
    assert len(result.stdout.strip()) > 0

    # Optionnel : éviter les erreurs visibles
    assert "error" not in result.stdout.lower()


def test_diag_does_not_crash():
    """
    Test de robustesse : juste vérifier qu'on ne crash pas.
    """
    result = run_cli(["--diag"])
    assert_success(result)
    stdout = result.stdout.lower()

    expected = [
        "wine",
        "gamemode",
        "mangohud",
        "python",
        "recommended",
        "steam",
        "session",
    ]

    for item in expected:
        assert item in stdout

    #assert result.returncode == 0


def test_help_structure():
    result = run_cli(["--help"])
    assert_success(result)

    stdout = result.stdout.lower()

    expected = [
        "proton-autogen",
        "gamescope",
        "mangohud",
        "--ux",
        "--diag",
        "--help-env",
        "--debug",
        "--verbose",
        "--gamemode",
        "--wine",
        "--proton",
    ]

    for item in expected:
        assert item in stdout


def test_about_structure():
    result = run_cli(["--about"])
    assert_success(result)

    stdout = result.stdout.lower()

    expected = [
        "proton-autogen",
        "proton",
        "mangohud",
        "gamemode",
        "steam",
        "n3oray",
        "add-apt-repository",
        "https://github.com/n3oray/proton-autogen",
    ]

    for item in expected:
        assert item in stdout


def test_about_list_protons():
    result = run_cli(["--list_protons"])
    assert_success(result)

    stdout = result.stdout.lower()
    #No Proton installation found
    expected = [
        "found",
        "proton",
        "installation",
    ]

    for item in expected:
        assert item in stdout


def test_about_version():
    result = run_cli(["--v"])
    assert_success(result)

    stdout = result.stdout.lower()

    expected = [
        "proton-autogen",
    ]

    for item in expected:
        assert item in stdout

def test_about_json():
    result = run_cli(["--json-profile"])
    assert_success(result)

    stdout = result.stdout.lower()

    expected = [
        "proton-autogen",
        "export",
    ]

    for item in expected:
        assert item in stdout


def test_about_gamemode():
    result = run_cli(["--gamemode"])

    print("EXIT:", result.exit_code)
    print("STDOUT:")
    print(result.stdout)
    print("STDERR:")
    print(result.stderr)

    assert_success(result)


def test_about_mangohud():
    result = run_cli(["--mangohud"])

    print("EXIT:", result.exit_code)
    print("STDOUT:")
    print(result.stdout)
    print("STDERR:")
    print(result.stderr)

    assert_success(result)


def test_about_call():
    result = run_cli(["--call"])

    print("EXIT:", result.exit_code)
    print("STDOUT:")
    print(result.stdout)
    print("STDERR:")
    print(result.stderr)

    assert_success(result)


def test_missing_file():
    result = run_cli(["missing.exe"])

    output = (result.stdout + result.stderr).lower()

    assert "warning" in output
    assert "file" in output
