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

    assert result.returncode == 0


def test_help_is_fast():
    """
    Vérifie que le CLI répond rapidement.
    """
    result = run_cli(["--help"], timeout=2)

    assert_success(result)
  
