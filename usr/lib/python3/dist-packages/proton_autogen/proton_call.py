#proton_call.py

import sys
import subprocess
from pathlib import Path

from proton_autogen.core import (
    base_env,
    has_mangohud,
    has_gamemode,
    has_gamescope,
    DEBUG,
    VERBOSE,
)
from proton_autogen.utils.gamescope import build_gamescope_command
from proton_autogen.dector import resolve_game_features, gpu_env
from proton_autogen.util_path import proton_path, proton_name
from proton_autogen.pa_log import handle_result, result_to_line
from proton_autogen.session import finalize_session
from proton_autogen.notify import notifications
from proton_autogen.util_path import proton_path, proton_name
from proton_autogen.core import get_prefix_path
from proton_autogen.progress import Progress


def launch_proton_call(
    exe_path,
    proton,
    system,
    features,
    enable_mangohud,
    enable_gamemode,
    enable_gamescope,
    start_time,
    extra_args=None,
    progress=None,
):

    # -------------------------
    # Proton Path & Prefix Path
    # -------------------------
    prefix_path = get_prefix_path("main", exe_path)
    proton_dir = proton_path(proton)
    env = base_env(
        enable_mangohud=enable_mangohud,
        enable_gamemode=enable_gamemode,
        enable_gamescope=enable_gamescope,
        exe_path=exe_path,
        exe_type=features.get("exe_type")
    )

    # -------------------------
    # GPU layer (UX + system merge)
    # -------------------------
    env.update(gpu_env(system, features))

    env["GE_PROTON"] = proton_path(proton)
    env["GAME_EXE"] = exe_path

    name = Path(exe_path).stem

    # -------------------------
    # MangoHud
    # -------------------------
    if enable_mangohud:
        if has_mangohud():
            notifications.notify(
                "info",
                "proton-autogen",
                f"MangoHud : enabled for {name}",
                ui=False
            )
            env["MANGOHUD"] = "1"
            env["MANGOHUD_DLSYM"] = "1"
            env["DXVK_HUD"] = "0"
            env.pop("LD_PRELOAD", None)
        else:
            notifications.notify(
                "warning",
                "[proton-autogen] MangoHud requested but not installed",
                ui=False
            )

    # -------------------------
    # GameMode
    # -------------------------
    if enable_gamemode and has_gamemode():
        notifications.notify(
            "info",
            "proton-autogen",
            f"GameMode : enabled for {name}",
            ui=False
        )
        env["GAMEMODE"] = "1"
    elif DEBUG or VERBOSE:
        print("[proton-autogen] GameMode not found")

    # -------------------------
    # Gamescope
    # -------------------------
    gamescope_cmd = []

    if enable_gamescope:
        if has_gamescope():
            notifications.notify(
                "info",
                "proton-autogen",
                f"Gamescope : enabled for {name}",
                ui=False
            )

            gamescope_cmd = build_gamescope_command(env)

        else:
            notifications.notify(
                "warning",
                "proton-autogen",
                "Gamescope requested but not installed",
                ui=False
            )

    # -------------------------
    # Command build
    # -------------------------
    extra_args = extra_args or []

    cmd = (
        gamescope_cmd
        + [
            "proton-call",
            "-c", proton_path(proton),
            "-r", exe_path,
            "--",
            exe_path,
        ]
        + extra_args
        + sys.argv[2:]
    )

    print(f"[proton-autogen] Launching with {proton_name(proton)}")

    # -------------------------
    # Debug
    # -------------------------
    if DEBUG or VERBOSE:
        print("================================")
        print("COMMAND:")
        print(" ".join(cmd))
        print("================================")

        print("ENV:")
        for k in (
            "STEAM_COMPAT_DATA_PATH",
            "STEAM_COMPAT_CLIENT_INSTALL_PATH",
            "WINEPREFIX",
            "PROTONPATH",
            "MANGOHUD",
            "LD_PRELOAD",
        ):
            print(f"{k}={env.get(k)}")

    # -------------------------
    # Run
    # -------------------------
    result_code = subprocess.run(cmd, env=env)

    status = handle_result(result_code)
    # Update Stats
    finalize_session(exe_path, start_time, result_code)
    #show_result !
    if progress is not None:
        progress.update( 100, result_to_line(status) )

    sys.exit(status["code"])
