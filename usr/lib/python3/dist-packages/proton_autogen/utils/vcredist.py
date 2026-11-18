# proton_autogen/utils/vcredist.py
"""
Installation et détection de Visual C++ Redistributable 2015-2022
(x64 + x86) dans un préfixe Proton / Wine.

Même approche que utils/dotnet.py :
  - installeurs officiels Microsoft
  - cache local ~/Documents/Proton/cache/vcredist
  - marqueurs + vérifications (registre, DLL réelles)
  - installation via `proton run`

Différences notables avec le prototype :
  - une DLL « Wine builtin » (fournie par Wine dans chaque préfixe) n'est PAS
    considérée comme un runtime Microsoft installé ;
  - détection par le registre (HKLM\\Software\\Microsoft\\VisualStudio\\14.0\\VC\\Runtimes) ;
  - échec mémorisé (cooldown) pour ne pas re-télécharger à chaque lancement ;
  - verrou pour deux lancements simultanés sur le même préfixe ;
  - téléchargement atomique (fichier .part) avec timeout ;
  - surcharges WINEDLLOVERRIDES (native,builtin) exposées pour le profil.
"""

from __future__ import annotations

import fcntl
import os
import re
import subprocess
import time
import urllib.request
from contextlib import contextmanager
from pathlib import Path

from proton_autogen.utils.logger import StructuredLogger

logger = StructuredLogger("proton-autogen.utils.vcredist")


VCREDIST_CACHE = (
    Path.home()
    / "Documents"
    / "Proton"
    / "cache"
    / "vcredist"
)

# Redistributable officiel Microsoft Visual C++ 2015-2022
VCREDIST_X64_URL = "https://aka.ms/vs/17/release/vc_redist.x64.exe"
VCREDIST_X86_URL = "https://aka.ms/vs/17/release/vc_redist.x86.exe"

VCREDIST_X64_NAME = "vc_redist.x64.exe"
VCREDIST_X86_NAME = "vc_redist.x86.exe"

MIN_INSTALLER_SIZE = 1_000_000
DOWNLOAD_TIMEOUT = 60

# Après un échec, ne pas retenter avant ce délai (secondes)
FAILURE_COOLDOWN = 24 * 3600

# Codes de retour acceptés (MSI/Burn)
#   0    = succès
#   1638 = une version identique ou plus récente est déjà installée
#   3010 = succès, redémarrage demandé (ignoré sous Wine)
_OK_CODES = (0, 1638, 3010)

# DLL clés d'un runtime VC++ 2015-2022 fonctionnel
_DLL_CHECKS = {
    "x64": [
        "drive_c/windows/system32/vcruntime140.dll",
        "drive_c/windows/system32/msvcp140.dll",
        "drive_c/windows/system32/vcruntime140_1.dll",
    ],
    "x86": [
        "drive_c/windows/syswow64/vcruntime140.dll",
        "drive_c/windows/syswow64/msvcp140.dll",
    ],
}

# Signatures placées par Wine dans l'en-tête DOS (offset 0x40) de ses DLL
# internes : « builtin » (PE complet) ou « placeholder » (fake dll).
_WINE_SIGNATURES = (b"Wine builtin DLL", b"Wine placeholder DLL")

# Clés du registre écrites par l'installeur Microsoft.
# x86 vit sous Wow6432Node dans un préfixe 64 bits.
_REG_SECTIONS = {
    "x64": r"Software\\\\Microsoft\\\\VisualStudio\\\\14\.0\\\\VC\\\\Runtimes\\\\x64",
    "x86": r"Software\\\\(?:Wow6432Node\\\\)?Microsoft\\\\VisualStudio\\\\14\.0\\\\VC\\\\Runtimes\\\\x86",
}

# Même liste que `winetricks vcrun2022` : Wine charge sinon sa propre DLL
# interne en priorité, même si la DLL Microsoft est présente dans system32.
VCREDIST_DLL_OVERRIDES = (
    "vcruntime140,vcruntime140_1,msvcp140,msvcp140_1,msvcp140_2,"
    "msvcp140_atomic_wait,msvcp140_codecvt_ids,concrt140,vcomp140,"
    "vccorlib140,vcamp140=n,b"
)


# ---------------------------------------------------------------------------
# Chemins / marqueurs
# ---------------------------------------------------------------------------

def _wine_prefix(compat_data: Path) -> Path:
    """Retourne le vrai préfixe Wine (…/pfx) depuis STEAM_COMPAT_DATA_PATH."""
    pfx = compat_data / "pfx"
    if pfx.is_dir():
        return pfx
    return compat_data


def _marker_path(compat_data: Path, arch: str) -> Path:
    return compat_data / f".vcredist_{arch}_installed"


def _failure_marker(compat_data: Path) -> Path:
    return compat_data / ".vcredist_failed"


def _lock_path(compat_data: Path) -> Path:
    return compat_data / ".vcredist.lock"


# ---------------------------------------------------------------------------
# Détection
# ---------------------------------------------------------------------------

def _is_wine_builtin(dll: Path) -> bool:
    """True si la DLL est une DLL interne de Wine (et non celle de Microsoft)."""
    try:
        with open(dll, "rb") as f:
            header = f.read(128)
    except OSError:
        return True
    return any(sig in header for sig in _WINE_SIGNATURES)


def _dlls_present(wine_prefix: Path, arch: str) -> bool:
    """True si les DLL VC++ Microsoft (pas Wine) de l'architecture existent."""
    for rel in _DLL_CHECKS.get(arch, []):
        dll = wine_prefix / rel
        if not dll.is_file() or _is_wine_builtin(dll):
            return False
    return True


def _registry_installed(wine_prefix: Path, arch: str) -> bool:
    """True si system.reg contient Runtimes\\<arch> avec Installed=1."""
    reg = wine_prefix / "system.reg"
    if not reg.is_file():
        return False

    section = re.compile(
        r"^\[" + _REG_SECTIONS[arch] + r"\][^\n]*\n(.*?)(?=^\[|\Z)",
        re.IGNORECASE | re.MULTILINE | re.DOTALL,
    )
    try:
        data = reg.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return False

    match = section.search(data)
    if not match:
        return False

    return re.search(
        r'^"Installed"=dword:0*1\s*$', match.group(1), re.MULTILINE
    ) is not None


def _arch_installed(wine_prefix: Path, arch: str) -> bool:
    return _registry_installed(wine_prefix, arch) or _dlls_present(wine_prefix, arch)


def check_vcredist(prefix, arch: str = "both") -> bool:
    """
    True si les runtimes Visual C++ demandés sont réellement installés.

    Args:
        prefix: STEAM_COMPAT_DATA_PATH (ou directement un préfixe Wine)
        arch: "x64", "x86" ou "both"
    """
    wine_prefix = _wine_prefix(Path(prefix))
    arches = ["x64", "x86"] if arch == "both" else [arch]
    return all(_arch_installed(wine_prefix, a) for a in arches)


def has_vcredist(prefix) -> bool:
    """Alias court, même style que le module .NET."""
    return check_vcredist(prefix, arch="both")


def vcredist_dll_overrides() -> str:
    """Valeur WINEDLLOVERRIDES à fusionner quand les runtimes MS sont là."""
    return VCREDIST_DLL_OVERRIDES


# ---------------------------------------------------------------------------
# Téléchargement / installation
# ---------------------------------------------------------------------------

def _download_if_needed(url: str, dest: Path) -> bool:
    """Télécharge l'installeur s'il n'est pas en cache. Retourne le succès."""
    if dest.is_file() and dest.stat().st_size > MIN_INSTALLER_SIZE:
        logger.info(f"[proton-autogen] Cache hit: {dest.name}")
        return True

    dest.parent.mkdir(parents=True, exist_ok=True)
    part = dest.with_suffix(dest.suffix + ".part")

    logger.info(f"[proton-autogen] Downloading {dest.name}...")
    try:
        with urllib.request.urlopen(url, timeout=DOWNLOAD_TIMEOUT) as resp, \
                open(part, "wb") as out:
            while True:
                chunk = resp.read(1 << 20)
                if not chunk:
                    break
                out.write(chunk)

        if part.stat().st_size <= MIN_INSTALLER_SIZE:
            logger.error(f"[proton-autogen] Download incomplete: {dest.name}")
            part.unlink(missing_ok=True)
            return False

        part.replace(dest)  # atomique : jamais d'installeur tronqué en cache
        logger.info(f"[proton-autogen] Downloaded {dest.name}")
        return True

    except Exception as exc:
        logger.error(f"[proton-autogen] Download failed: {exc}")
        part.unlink(missing_ok=True)
        return False


def _install_one(installer: Path, compat_data: Path, proton_path, arch: str) -> bool:
    """Lance un installeur VC++ dans le préfixe via Proton."""
    wine_prefix = _wine_prefix(compat_data)
    marker = _marker_path(compat_data, arch)

    proton_bin = Path(proton_path) / "proton"
    if not proton_bin.is_file():
        logger.error(f"[proton-autogen] Proton binary not found: {proton_bin}")
        return False

    logger.info(f"[proton-autogen] Installing VC++ Redistributable ({arch})...")

    env = os.environ.copy()
    env["STEAM_COMPAT_DATA_PATH"] = str(compat_data)
    env["PROTONPATH"] = str(proton_path)
    env.setdefault(
        "STEAM_COMPAT_CLIENT_INSTALL_PATH",
        os.path.expanduser("~/.steam/steam"),
    )
    env.pop("WINEPREFIX", None)

    try:
        result = subprocess.run(
            [str(proton_bin), "run", str(installer),
             "/install", "/quiet", "/norestart"],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
            timeout=600,
        )
    except subprocess.TimeoutExpired:
        logger.error(f"[proton-autogen] Installer ({arch}) timed out")
        return False

    if result.stdout:
        for line in result.stdout.splitlines()[-15:]:
            logger.debug(f"  {line}")

    if result.returncode not in _OK_CODES:
        logger.info(
            f"[proton-autogen] Installer ({arch}) returned {result.returncode}"
        )

    if _arch_installed(wine_prefix, arch):
        marker.touch()
        logger.info(f"[proton-autogen] VC++ Redistributable ({arch}) OK")
        return True

    logger.error(f"[proton-autogen] VC++ Redistributable ({arch}) installation failed")
    return False


@contextmanager
def _prefix_lock(compat_data: Path):
    """Verrou exclusif : deux lancements ne doivent pas installer en même temps."""
    compat_data.mkdir(parents=True, exist_ok=True)
    with open(_lock_path(compat_data), "w") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)


def _recently_failed(compat_data: Path) -> bool:
    marker = _failure_marker(compat_data)
    try:
        return (time.time() - marker.stat().st_mtime) < FAILURE_COOLDOWN
    except OSError:
        return False


def ensure_vcredist(prefix, proton_path, progress=None, force: bool = False) -> bool:
    """
    S'assure que Visual C++ 2015-2022 (x64 + x86) est présent dans le préfixe.

    Args:
        prefix: STEAM_COMPAT_DATA_PATH
        proton_path: dossier de l'installation Proton
        progress: instance Progress optionnelle (pourcentage + message)
        force: réinstalle même si tout semble présent (ignore aussi le cooldown)

    Returns:
        True si les deux architectures sont disponibles, False sinon.
        Ne lève jamais : les échecs sont journalisés et l'appelant continue
        le lancement du jeu.
    """
    compat_data = Path(prefix)
    wine_prefix = _wine_prefix(compat_data)

    def _progress(pct, msg):
        if progress is not None:
            progress.update(pct, msg)

    logger.info(f"[proton-autogen] Checking Visual C++ Redistributables in {wine_prefix}")
    _progress(10, "Checking Visual C++ Redistributables")

    # Chemin rapide (sans verrou, sans réseau)
    if not force and check_vcredist(compat_data, arch="both"):
        logger.info("[proton-autogen] Visual C++ Redistributables already present")
        _progress(100, "Visual C++ Redistributables OK")
        return True

    if not force and _recently_failed(compat_data):
        logger.info(
            "[proton-autogen] VC++ install failed recently, skipping "
            f"(retry in <{FAILURE_COOLDOWN // 3600}h)"
        )
        return False

    try:
        with _prefix_lock(compat_data):
            # Un autre processus a pu terminer l'installation pendant l'attente
            if not force and check_vcredist(compat_data, arch="both"):
                _progress(100, "Visual C++ Redistributables OK")
                return True
            return _install_missing(compat_data, wine_prefix, proton_path, progress, force)
    except OSError as exc:
        logger.error(f"[proton-autogen] VC++ lock/install error: {exc}")
        return False


def _install_missing(compat_data, wine_prefix, proton_path, progress, force) -> bool:
    def _progress(pct, msg):
        if progress is not None:
            progress.update(pct, msg)

    # Marqueurs périmés
    for arch in ("x64", "x86"):
        marker = _marker_path(compat_data, arch)
        if marker.exists() and not _arch_installed(wine_prefix, arch):
            logger.info(f"[proton-autogen] Stale marker for {arch}, removing")
            marker.unlink(missing_ok=True)

    VCREDIST_CACHE.mkdir(parents=True, exist_ok=True)

    targets = [
        ("x64", VCREDIST_X64_URL, VCREDIST_X64_NAME),
        ("x86", VCREDIST_X86_URL, VCREDIST_X86_NAME),
    ]
    total = len(targets)

    for idx, (arch, url, filename) in enumerate(targets):
        if not force and check_vcredist(compat_data, arch=arch):
            logger.info(f"[proton-autogen] VC++ ({arch}) already present, skipping")
            continue

        _progress(20 + int(60 * idx / total), f"Downloading VC++ Redistributable ({arch})")
        installer = VCREDIST_CACHE / filename
        if not _download_if_needed(url, installer):
            continue

        _progress(40 + int(40 * idx / total), f"Installing VC++ Redistributable ({arch})")
        _install_one(installer, compat_data, proton_path, arch)

    final_ok = check_vcredist(compat_data, arch="both")
    failure = _failure_marker(compat_data)

    if final_ok:
        failure.unlink(missing_ok=True)
        _progress(100, "Visual C++ Redistributables installed")
        logger.info("[proton-autogen] Visual C++ Redistributables ready")
    else:
        failure.touch()
        _progress(100, "Visual C++ installation incomplete")
        logger.info(
            "[proton-autogen] Visual C++ Redistributables incomplete "
            "(launch will still be attempted)"
        )

    return final_ok
