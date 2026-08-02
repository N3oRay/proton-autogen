import subprocess
import os
import re

from proton_autogen.profiles.base import init_env
from proton_autogen.utils.dotnet import ensure_dotnet48
from proton_autogen.utils.logger import StructuredLogger

#-------------------------- Init Log -------------------
logger = StructuredLogger("proton-autogen.profiles.dotnet")

DOTNET_NATIVE = "framework"
DOTNET_MONO = "mono"
DOTNET_NONE = "none"


def normalize_prefix(prefix):
    """
    Retourne le vrai Wine prefix contenant system.reg.
    """

    if not prefix:
        return None

    # Cas standard Proton
    if os.path.exists(
        os.path.join(prefix, "system.reg")
    ):
        return prefix


    # Cas Steam compatdata
    pfx = os.path.join(prefix, "pfx")

    if os.path.exists(
        os.path.join(pfx, "system.reg")
    ):
        return pfx


    return prefix


def wine_reg_value(prefix, key, value):
    """
    Lecture autonome du registre Wine.
    Aucun appel à wine/proton.
    """

    if not prefix:
        return None

    reg_files = [
        os.path.join(prefix, "system.reg"),
        os.path.join(prefix, "user.reg"),
        os.path.join(prefix, "userdef.reg"),
    ]

    # Format Wine : double antislash dans les fichiers
    key = key.strip("\\")
    key = key.replace("\\", "\\\\")

    section_pattern = re.compile(
        r"^\[" + re.escape(key) + r"\].*?\n(.*?)(?=^\[|\Z)",
        re.MULTILINE | re.DOTALL
    )

    value_pattern = re.compile(
        r'^"' + re.escape(value) + r'"=(.+)$',
        re.MULTILINE
    )

    for reg_file in reg_files:

        if not os.path.exists(reg_file):
            continue

        try:
            with open(
                reg_file,
                "r",
                encoding="utf-8",
                errors="ignore"
            ) as f:
                data = f.read()

            section = section_pattern.search(data)

            if not section:
                continue

            value_match = value_pattern.search(
                section.group(1)
            )

            if value_match:
                return value_match.group(1).strip()

        except OSError:
            continue

    return None

def get_dotnet_release(prefix):

    value = wine_reg_value(
        prefix,
        r"Software\Microsoft\NET Framework Setup\NDP\v4\Full",
        "Release"
    )

    if not value:
        return None


    match = re.search(
        r"dword:([0-9a-fA-F]+)",
        value
    )

    if not match:
        return None


    return int(
        match.group(1),
        16
    )

def has_wine_mono(prefix):

    paths = [
        os.path.join(
            prefix,
            "drive_c",
            "windows",
            "mono",
            "mono-2.0"
        ),
        os.path.join(
            prefix,
            "drive_c",
            "Program Files",
            "Mono"
        )
    ]

    return any(os.path.exists(p) for p in paths)

def wine_reg_value_basic(prefix, key, value):
    """
    Lit une valeur du registre Wine.
    Retourne None si absente.
    """

    env = os.environ.copy()
    env["WINEPREFIX"] = prefix

    try:
        result = subprocess.run(
            [
                "wine",
                "reg",
                "query",
                key,
                "/v",
                value
            ],
            env=env,
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            return None

        return result.stdout

    except Exception:
        return None


def has_dotnet48(prefix):

    release = get_dotnet_release(prefix)

    return (
        release is not None
        and release >= 528040
    )


def detect_dotnet_mode(prefix):

    if not prefix:
        return DOTNET_NONE

    # Toujours travailler sur le vrai Wine prefix
    if os.path.exists(
        os.path.join(prefix, "pfx", "system.reg")
    ):
        prefix = os.path.join(prefix, "pfx")


    logger.info(
        f"[proton-autogen] Registry prefix: {prefix}"
    )


    if has_dotnet48(prefix):
        return DOTNET_NATIVE


    if has_wine_mono(prefix):
        return DOTNET_MONO


    return DOTNET_NONE


def env_dotnet(prefix=None, proton_path=None, exe_path=None):

    env = init_env()

    logger.info("[proton-autogen] PROFILE: DOTNET")





    env.update({
        "PROTON_USE_XALIA": "0",

        "PROTON_NO_ESYNC": "1",
        "PROTON_NO_FSYNC": "1",

        "WINEESYNC": "0",
        "WINEFSYNC": "0",

        "WINE_SIMULATE_WRITECOPY": "0",
    })


    for var in (
        "DXVK_HUD",
        "DXVK_ASYNC",
        "VKD3D_CONFIG",
        "PROTON_USE_WINED3D",
        "MANGOHUD",
    ):
        env.pop(var, None)


    # ----------------------------------------------
    # Choix CLR automatique
    # ----------------------------------------------

    dotnet_mode = detect_dotnet_mode(prefix)

    logger.info(
        f"[proton-autogen] CLR detection: {dotnet_mode}"
    )

    if dotnet_mode == DOTNET_NONE and prefix and proton_path:

        installed = ensure_dotnet48(
            prefix=prefix,
            proton_path=proton_path
        )

        if not installed:
            logger.info(
                "[proton-autogen] Warning: .NET installation failed"
            )

        dotnet_mode = detect_dotnet_mode(prefix)


    if dotnet_mode in (DOTNET_NATIVE, DOTNET_MONO):
        logger.info(
            f"[proton-autogen] CLR available ({dotnet_mode}) -> using Wine mscoree"
        )
        env["WINEDLLOVERRIDES"] = "mscoree=b"
    else:
        logger.info(
            "[proton-autogen] No CLR detected"
        )
        env.pop("WINEDLLOVERRIDES", None)

    return env
