# proton_autogen/integrations/lutris_validate.py

from typing import Dict, Any


class LutrisValidationError(Exception):
    pass


def validate_lutris_export(data: Dict[str, Any]) -> None:
    if not isinstance(data, dict):
        raise LutrisValidationError("Root must be dict")

    # -------------------------
    # ROOT FIELDS
    # -------------------------
    if not data.get("name"):
        raise LutrisValidationError("Missing name")

    if not data.get("game_slug"):
        raise LutrisValidationError("Missing game_slug")

    script = data.get("script")
    if not isinstance(script, dict):
        raise LutrisValidationError("Missing script block")

    # -------------------------
    # RUNNER CHECK (CRITICAL)
    # -------------------------
    runner = script.get("runner")
    if not runner:
        raise LutrisValidationError("Missing script.runner")

    if runner not in {"wine", "proton"}:
        raise LutrisValidationError(f"Invalid runner: {runner}")

    # -------------------------
    # GAME BLOCK
    # -------------------------
    game = script.get("game")
    if not isinstance(game, dict):
        raise LutrisValidationError("Missing script.game")

    if not game.get("exe"):
        raise LutrisValidationError("Missing script.game.exe")

    if not game.get("working_dir"):
        raise LutrisValidationError("Missing script.game.working_dir")

    # -------------------------
    # INSTALLER CHECK (minimal safe)
    # -------------------------
    installer = script.get("installer")
    if not isinstance(installer, list):
        raise LutrisValidationError("Missing script.installer list")

    for step in installer:
        if not isinstance(step, dict):
            raise LutrisValidationError("Invalid installer step")

    return None
