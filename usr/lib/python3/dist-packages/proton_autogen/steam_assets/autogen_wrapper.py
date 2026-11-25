"""Steam -> Proton-Autogen wrapper (standard library only).

Steam provides the environment (STEAM_COMPAT_DATA_PATH, SteamAppId,
STEAM_COMPAT_CLIENT_INSTALL_PATH, ...). It is passed unchanged to
Proton-Autogen, whose behaviour stays the same.
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.realpath(__file__))
LAUNCHER_FILE = os.path.join(HERE, "launcher.path")

RUN_VERBS = {"run", "waitforexitandrun"}
NOOP_VERBS = {"destroyprefix"}  # Proton-Autogen manages its own prefixes
PATH_VERBS = {"getcompatpath", "getnativepath"}

EXIT_USAGE = 2
EXIT_LAUNCHER_MISSING = 127


def _err(msg):
    print(f"[Proton-Autogen/Steam] {msg}", file=sys.stderr)


def find_launcher():
    """Return the proton-autogen launcher path, or None."""
    candidates = [os.environ.get("PROTON_AUTOGEN_BIN")]
    try:
        with open(LAUNCHER_FILE, encoding="utf-8") as fh:
            candidates.append(fh.read().strip())
    except OSError:
        pass
    candidates.append(shutil.which("proton-autogen"))
    for cand in candidates:
        if cand and os.path.isfile(cand) and os.access(cand, os.X_OK):
            return cand
    return None


def main(argv):
    if not argv:
        _err("usage: proton <verb> <executable> [arguments...]")
        return EXIT_USAGE

    verb, rest = argv[0], argv[1:]

    if verb in PATH_VERBS:
        # No path conversion: the path is returned unchanged.
        if rest:
            print(rest[0])
        return 0

    if verb in NOOP_VERBS:
        return 0

    if verb not in RUN_VERBS:
        _err(f"unsupported verb: {verb}")
        return EXIT_USAGE

    if not rest:
        _err("no executable to run")
        return EXIT_USAGE

    launcher = find_launcher()
    if launcher is None:
        _err("proton-autogen not found. Run again: proton-autogen install-steam")
        return EXIT_LAUNCHER_MISSING

    # Loop guard: if Proton-Autogen ever selects this wrapper as its Proton,
    # stop instead of re-launching itself forever.
    if os.environ.get("PROTON_AUTOGEN_WRAPPER_ACTIVE") == "1":
        _err("recursive call detected: Proton-Autogen selected this wrapper "
             "as its Proton version.")
        return 1
    os.environ["PROTON_AUTOGEN_WRAPPER_ACTIVE"] = "1"
    os.environ["PROTON_AUTOGEN_FROM_STEAM"] = "1"
    # "--" shields the game arguments (--help, --v...) from the legacy routing.
    # exec: Steam follows the process directly and sends it its signals.
    os.execv(launcher, [launcher, "run", "--steam", "--", *rest])
    return 0  # never reached
