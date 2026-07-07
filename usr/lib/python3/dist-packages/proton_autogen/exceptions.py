# proton_autogen/exceptions.py (NOUVEAU)

from __future__ import annotations

from pathlib import Path


class ProtonAutogenError(Exception):
    """Base exception for proton-autogen."""


class ProtonNotFoundError(ProtonAutogenError):
    """Raised when no compatible Proton installation can be found."""

    def __init__(self, searched_paths: list[Path]):
        self.searched_paths = searched_paths

        paths = "\n".join(f"  - {p}" for p in searched_paths)

        super().__init__(
            "No Proton installation was found.\n"
            "Searched locations:\n"
            f"{paths}\n\n"
            "Install a Proton version or specify its location explicitly."
        )


class GameConfigError(ProtonAutogenError):
    """Raised when the game configuration is invalid."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class ExecutableNotFoundError(ProtonAutogenError):
    """Raised when the game executable cannot be found."""

    def __init__(self, path: Path):
        self.path = path
        super().__init__(f"Executable not found: {path}")


class PrefixError(ProtonAutogenError):
    """Raised when a Wine/Proton prefix operation fails."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)
