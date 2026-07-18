# proton_autogen/utils/dotnet.py

import os
import subprocess
import urllib.request
import tempfile
from pathlib import Path


DOTNET_CACHE = (
    Path.home()
    / "Documents"
    / "Proton"
    / "cache"
    / "dotnet"
)


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
    dotnet_marker = compat_data / ".dotnet48_installed"

    # Proton prefix réel
    wine_prefix = compat_data / "pfx"

    print(
        f"[proton-autogen] Checking .NET Framework 4.8 in {wine_prefix}"
    )


    # --------------------------------------------------
    # Check registry
    # --------------------------------------------------

    if dotnet_marker.exists():

        print(
            "[proton-autogen] .NET Framework 4.8 cache hit"
        )

        if check_dotnet48(compat_data, proton_path):
            print(
                "[proton-autogen] .NET Framework 4.8 already installed"
            )
            return True

        else:
            print(
                "[proton-autogen] Cache invalid, removing marker"
            )
            dotnet_marker.unlink()


    print("[proton-autogen] .NET Framework 4.8 missing")


    # --------------------------------------------------
    # Download installer
    # --------------------------------------------------

    DOTNET_CACHE.mkdir(
        parents=True,
        exist_ok=True
    )

    installer = (
        DOTNET_CACHE
        / "NDP48-x86-x64-AllOS-ENU.exe"
    )

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

    # nécessaire pour certains Proton non-Steam
    env["STEAM_COMPAT_CLIENT_INSTALL_PATH"] = os.path.expanduser(
        "~/.steam/steam"
    )

    # éviter un ancien WINEPREFIX pollué
    env.pop("WINEPREFIX", None)


    result = subprocess.run(
        [
            str(Path(proton_path) / "proton"),
            "run",
            str(installer),
            "/passive",
            "/norestart",
            "/log",
            "C:\\dotnet48_install.log"
        ],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )

    if result.stdout:
        print(result.stdout)


    if result.returncode != 0:
        print(
            f"[proton-autogen] Installer returned {result.returncode}"
        )


    # --------------------------------------------------
    # Verify
    # --------------------------------------------------

    if check_dotnet48(compat_data, proton_path):

        dotnet_marker.touch()

        print(
            "[proton-autogen] .NET Framework 4.8 installed successfully"
        )

        return True


    print("[proton-autogen] .NET Framework 4.8 installation failed")

    return False



def check_dotnet48(compat_data, proton_path):

    env = os.environ.copy()
    env["STEAM_COMPAT_DATA_PATH"] = str(compat_data)
    env["PROTONPATH"] = str(proton_path)
    env.pop("WINEPREFIX", None)

    keys = [
        r"HKLM\Software\Microsoft\NET Framework Setup\NDP\v4\Full",
        r"HKLM\Software\Wow6432Node\Microsoft\NET Framework Setup\NDP\v4\Full",
    ]

    for key in keys:

        cmd = [
            str(Path(proton_path) / "proton"),
            "run",
            "reg.exe",
            "query",
            key,
            "/v",
            "Release"
        ]

        result = subprocess.run(
            cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        print(
            f"[proton-autogen] Registry check {key}"
        )

        print(result.stdout)

        for line in result.stdout.splitlines():

            if "Release" not in line:
                continue

            for part in line.split():

                try:
                    if part.startswith("0x"):
                        value = int(part, 16)

                    else:
                        value = int(part)

                    if value >= 528040:
                        return True

                except ValueError:
                    continue

    return False
