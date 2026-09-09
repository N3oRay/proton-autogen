# data_paths.py
# Centralized data paths for proton-autogen

from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parent


def get_data_roots():
    """
    Return possible installation data roots in priority order.

    Supports:
      - development/source tree
      - Flatpak (/app)
      - standard Linux installation
    """

    roots = []

    # ------------------------------------------------------------------
    # Development / source tree
    # ------------------------------------------------------------------
    roots.append(
        PACKAGE_ROOT / "data"
    )

    # ------------------------------------------------------------------
    # Flatpak
    #
    # Example:
    #   PACKAGE_ROOT =
    #   /app/lib/python3.13/site-packages/proton_autogen
    #
    # Data:
    #   /app/share/proton-autogen
    # ------------------------------------------------------------------
    flatpak_root = Path("/app/share/proton-autogen")

    if Path("/app").is_dir():
        roots.append(flatpak_root)

    # ------------------------------------------------------------------
    # Standard Linux installation
    # ------------------------------------------------------------------
    roots.append(
        Path("/usr/share/proton-autogen")
    )

    # Remove duplicates while preserving order
    result = []
    seen = set()

    for root in roots:
        root = root.resolve()

        if root not in seen:
            seen.add(root)
            result.append(root)

    return result


DATA_ROOTS = get_data_roots()


def get_data_root():
    """
    Return the first existing proton-autogen data directory.
    """

    for root in DATA_ROOTS:
        if root.is_dir():
            return root

    # Fallback
    return DATA_ROOTS[0]


DATA_ROOT = get_data_root()


DOCS_ROOT = DATA_ROOT / "docs"
PROFILES_FILE = DATA_ROOT / "profiles.csv"


def get_docs_root():
    """
    Return the documentation directory.
    """
    return DOCS_ROOT


def get_profiles_file():
    """
    Return the profiles database file.
    """
    return PROFILES_FILE
