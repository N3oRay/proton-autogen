# proton_autogen/utils/dotnet.py

import os
import subprocess
import urllib.request
import tempfile
from pathlib import Path


DOTNET48_URL = (
    "https://go.microsoft.com/fwlink/?linkid=2088631"
)


def ensure_dotnet48(prefix, proton_path):
    """
    Ensure Microsoft .NET Framework 4.8 is installed in a Proton prefix.

    Args:
        prefix: Path to STEAM_COMPAT_DATA_PATH
        proton_path: Path to Proton installation

    Returns:
        True if .NET 4.8 is available, False otherwise
    """

    compat_data = Path(prefix)

    # Proton prefix réel
    wine_prefix = compat_data / "pfx"

    print(
        f"[proton-autogen] Checking .NET Framework 4.8 in {wine_prefix}"
    )


    # --------------------------------------------------
    # Check registry
    # --------------------------------------------------

    if check_dotnet48(wine_prefix, proton_path):
        print("[proton-autogen] .NET Framework 4.8 already installed")
        return True


    print("[proton-autogen] .NET Framework 4.8 missing")


    # --------------------------------------------------
    # Download installer
    # --------------------------------------------------

    installer = Path(tempfile.gettempdir()) / "NDP48-x86-x64-AllOS-ENU.exe"

    if not installer.exists():

        print("[proton-autogen] Downloading .NET Framework 4.8...")

        urllib.request.urlretrieve(
            DOTNET48_URL,
            installer
        )


    # --------------------------------------------------
    # Install inside Proton prefix
    # --------------------------------------------------

    print("[proton-autogen] Installing .NET Framework 4.8...")


    env = os.environ.copy()

    # IMPORTANT :
    # Proton attend STEAM_COMPAT_DATA_PATH,
    # pas STEAM_COMPAT_DATA_PATH/pfx
    env["STEAM_COMPAT_DATA_PATH"] = str(compat_data)

    env["PROTONPATH"] = str(proton_path)


    result = subprocess.run(
        [
            str(Path(proton_path) / "proton"),
            "run",
            str(installer),
            "/quiet",
            "/norestart",
        ],
        env=env,
        check=False,
    )


    if result.returncode != 0:
        print(
            f"[proton-autogen] Installer returned {result.returncode}"
        )


    # --------------------------------------------------
    # Verify
    # --------------------------------------------------

    if check_dotnet48(wine_prefix, proton_path):

        print("[proton-autogen] .NET Framework 4.8 installed successfully")
        return True


    print("[proton-autogen] .NET Framework 4.8 installation failed")

    return False



def check_dotnet48(prefix, proton_path):

    env = os.environ.copy()

    env["STEAM_COMPAT_DATA_PATH"] = str(prefix)

    cmd = [
        str(Path(proton_path) / "proton"),
        "run",
        "reg",
        "query",
        r"HKLM\Software\Microsoft\NET Framework Setup\NDP\v4\Full",
        "/v",
        "Release"
    ]

    result = subprocess.run(
        cmd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode != 0:
        return False


    for line in result.stdout.splitlines():

        if "Release" in line:

            try:
                value = int(line.split()[-1], 16)

                if value >= 528040:
                    return True

            except ValueError:
                pass

    return False
