
from proton_autogen.utils import gamescope


def run_gamescope_check() -> bool:
    """
    Run Gamescope diagnostic tests.

    Returns:
        True if all tests pass.
    """

    results = []

    def check(name, callback):
        try:
            success, message = callback()
        except Exception as exc:
            success = False
            message = str(exc)

        results.append((name, success, message))

        status = "OK" if success else "FAIL"

        print(f"[ {status} ] {name}")

        if message:
            print(f"        {message}")

    print()
    print("=" * 52)
    print("          PROTON AUTOGEN - GAMESCOPE")
    print("=" * 52)

    # -------------------------------------------------
    # Detection
    # -------------------------------------------------

    def check_gamescope():
        available = gamescope.has_gamescope()
        return available, (
            "Gamescope detected"
            if available else
            "Gamescope not found"
        )

    def check_xrandr():
        available = gamescope.has_xrandr()
        return available, (
            "xrandr detected"
            if available else
            "xrandr not found"
        )

    def check_flatpak():
        flatpak = gamescope.is_flatpak()
        return True, (
            "Running inside Flatpak"
            if flatpak else
            "Running outside Flatpak"
        )

    print("\n[ SYSTEM ]")

    check("Gamescope detection", check_gamescope)
    check("xrandr detection", check_xrandr)
    check("Flatpak detection", check_flatpak)

    # -------------------------------------------------
    # Resolution
    # -------------------------------------------------

    print("\n[ DISPLAY ]")

    def check_resolution():
        width, height = gamescope.detect_screen_resolution()

        valid = width > 0 and height > 0

        return valid, f"{width}x{height}"

    check("Screen resolution", check_resolution)

    # -------------------------------------------------
    # Environment
    # -------------------------------------------------

    print("\n[ ENVIRONMENT ]")

    def check_init():
        env = gamescope.init_gamescope_env(
            enabled=True,
            width=1920,
            height=1080,
            refresh=60,
            fullscreen=True,
            cursor=True,
            internal_width=1280,
            internal_height=720,
            output_width=1920,
            output_height=1080,
            mode="custom",
        )

        valid = (
            env.get("USE_GAMESCOPE") == "1"
            and env.get("GAMESCOPE_INTERNAL_WIDTH") == "1280"
            and env.get("GAMESCOPE_INTERNAL_HEIGHT") == "720"
            and env.get("GAMESCOPE_OUTPUT_WIDTH") == "1920"
            and env.get("GAMESCOPE_OUTPUT_HEIGHT") == "1080"
        )

        return valid, str(env)

    check("Environment initialization", check_init)

    def check_cleanup():
        env = {
            "USE_GAMESCOPE": "1",
            "GAMESCOPE_WIDTH": "1920",
            "GAMESCOPE_HEIGHT": "1080",
            "OTHER_VARIABLE": "keep",
        }

        gamescope.clear_gamescope_env(env)

        valid = (
            "USE_GAMESCOPE" not in env
            and "GAMESCOPE_WIDTH" not in env
            and env.get("OTHER_VARIABLE") == "keep"
        )

        return valid, str(env)

    check("Environment cleanup", check_cleanup)

    def check_activation():
        enabled = gamescope.gamescope_enabled(
            {"USE_GAMESCOPE": "1"}
        )

        disabled = gamescope.gamescope_enabled(
            {"USE_GAMESCOPE": "0"}
        )

        valid = enabled and not disabled

        return valid, "Enabled/disabled states verified"

    check("Gamescope activation", check_activation)

    # -------------------------------------------------
    # Command builder
    # -------------------------------------------------

    print("\n[ COMMAND BUILDER ]")

    def check_command():
        env = gamescope.init_gamescope_env(
            enabled=True,
            width=1920,
            height=1080,
            refresh=60,
            fullscreen=True,
            cursor=True,
            internal_width=1280,
            internal_height=720,
            output_width=1920,
            output_height=1080,
            mode="custom",
        )

        command = gamescope.build_gamescope_command(env)

        valid = (
            command[:1] == ["gamescope"]
            and command[command.index("-W") + 1] == "1920"
            and command[command.index("-H") + 1] == "1080"
            and command[command.index("-w") + 1] == "1280"
            and command[command.index("-h") + 1] == "720"
            and "--fullscreen" in command
            and "--force-grab-cursor" in command
            and command[-1] == "--"
        )

        return valid, " ".join(command)

    check("Command generation (custom)", check_command)

    def check_command_output_only():
        env = gamescope.init_gamescope_env(
            enabled=True,
            width=1920,
            height=1080,
            mode="output",
        )

        command = gamescope.build_gamescope_command(env)

        # Mode « output » : -W/-H uniquement, aucun -w/-h.
        valid = (
            "-W" in command
            and "-H" in command
            and "-w" not in command
            and "-h" not in command
        )

        return valid, " ".join(command)

    check("Command generation (output only)", check_command_output_only)

    # -------------------------------------------------
    # Results
    # -------------------------------------------------

    passed = sum(
        1 for _, success, _ in results if success
    )

    total = len(results)

    print()
    print("=" * 52)
    print(f"RESULT: {passed}/{total} TESTS PASSED")
    print("=" * 52)

    return passed == total
