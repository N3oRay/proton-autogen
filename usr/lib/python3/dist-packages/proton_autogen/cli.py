"""Couche CLI de proton-autogen.

Point d'entrée unique : ``main(argv) -> int`` (code de sortie).

Principes :
  * le lanceur ``usr/bin/proton-autogen`` ne fait plus que ``sys.exit(main())`` ;
  * le routage est déclaratif (sous-commandes argparse) ;
  * les imports lourds (backend, editor, GTK...) sont différés dans les
    handlers : ``--help``, ``--version``... restent instantanés, même sans GTK ;
  * un handler retourne un code (ou None = succès) ou lève ``CliError`` ;
    aucun handler n'appelle ``sys.exit()`` ;
  * toutes les erreurs sont converties en code de sortie ici, et seulement ici.

Compatibilité : les anciennes formes restent acceptées (voir ``normalize_argv``) :
``proton-autogen game.exe``, ``proton-autogen --wine game.exe``,
``proton-autogen --list-protons``, ``proton-autogen --ux``, etc.
"""

from __future__ import annotations

import argparse
import os
import sys
import traceback
from typing import Optional, Sequence

PROG = "proton-autogen"

# Codes de sortie (contrat stable pour les scripts et les gestionnaires de fichiers)
EXIT_OK = 0
EXIT_ERROR = 1          # erreur d'exécution
EXIT_USAGE = 2          # arguments invalides (code historique d'argparse)
EXIT_NOT_FOUND = 3      # fichier introuvable
EXIT_INTERRUPTED = 130  # Ctrl+C (128 + SIGINT)


class CliError(Exception):
    """Erreur « attendue » : message propre pour l'utilisateur, pas de traceback."""

    def __init__(self, message: str, code: int = EXIT_ERROR):
        super().__init__(message)
        self.message = message
        self.code = code


# --------------------------------------------------------------------------- #
# Compatibilité avec les anciennes options (--xxx) -> sous-commandes
# --------------------------------------------------------------------------- #

# L'ordre est celui de l'ancien lanceur : la première option reconnue l'emporte.
_LEGACY_FLAGS = (
    (("--ux", "--UX"), "ux"),
    (("--check-translations", "--check-tr"), "check-translations"),
    (("--check-gamescope", "--check-gs"), "check-gamescope"),
    (("--about",), "about"),
    (("--v", "--version"), "version"),
    (("--list-protons", "--lp"), "list-protons"),
    (("--proton-paths",), "proton-paths"),
    (("--diag", "--diagnostic"), "diag"),
    (("--import",), "import"),
    (("--list-programs",), "list-programs"),
    (("--help", "-h"), "help"),
    (("--help-env",), "help-env"),
    (("--json-profile",), "json-profile"),
)

# Options qui consomment l'argument suivant (utile pour repérer la sous-commande).
_VALUE_OPTIONS = frozenset({"--profile"})


def normalize_argv(argv: Sequence[str], command_names: frozenset) -> list:
    """Traduit les anciennes formes de la ligne de commande vers la forme argparse.

    * ``--list-protons``              -> ``list-protons``
    * ``game.exe`` / ``--wine game.exe`` -> ``run [--wine] game.exe`` (« run » implicite)
    * ``--profile p add g.exe``       -> ``add --profile p g.exe`` (la sous-commande passe
      en tête : toutes les options sont ainsi acceptées avant OU après elle)
    * ``--`` : tout ce qui suit est un fichier (ex. ``-- add`` lance un jeu nommé « add »).
    """
    argv = list(argv)
    sep = argv.index("--") if "--" in argv else len(argv)
    head = argv[:sep]

    for flags, command in _LEGACY_FLAGS:
        if any(flag in head for flag in flags):
            return [command]

    i = 0
    while i < sep:
        token = argv[i]
        if token in _VALUE_OPTIONS:
            i += 2
            continue
        if token.startswith("-"):
            i += 1
            continue
        if token in command_names:
            return [token] + argv[:i] + argv[i + 1:]
        break

    return ["run"] + argv


# --------------------------------------------------------------------------- #
# Construction du parseur
# --------------------------------------------------------------------------- #

class _Parser(argparse.ArgumentParser):
    """argparse qui ne quitte qu'avec nos codes et pointe vers l'aide du projet."""

    def error(self, message):
        self.print_usage(sys.stderr)
        self.exit(
            EXIT_USAGE,
            f"{self.prog}: error: {message}\n"
            f"Try '{PROG} --help' for more information.\n",
        )


def split_game_args(argv: Sequence[str]) -> tuple:
    """``... -- FILE.exe ARGS...`` -> (``... -- FILE.exe``, ``ARGS...``).

    Everything after the program following ``--`` belongs to the program, so it
    never reaches the routing above (a game argument like ``--help`` must not
    open the project help). ``-- FILE`` alone is unchanged.
    """
    argv = list(argv)
    if "--" in argv:
        i = argv.index("--")
        if len(argv) > i + 2:
            return argv[: i + 2], argv[i + 2:]
    return argv, []


def build_parser() -> _Parser:
    debug_opt = argparse.ArgumentParser(add_help=False)
    debug_opt.add_argument(
        "--debug",
        action="store_true",
        help="print the full traceback on unexpected errors "
             "(or set PROTON_AUTOGEN_DEBUG=1)",
    )

    profile_opt = argparse.ArgumentParser(add_help=False)
    profile_opt.add_argument(
        "--profile", metavar="NAME", help="apply a user profile before running"
    )

    parser = _Parser(
        prog=PROG,
        description="Launch Windows programs through Proton/Wine.",
        add_help=False,
        allow_abbrev=False,
    )
    sub = parser.add_subparsers(
        dest="command", metavar="<command>", required=True, parser_class=_Parser
    )

    def add(name, handler, help_, *, aliases=(), profile=False):
        parents = [debug_opt] + ([profile_opt] if profile else [])
        p = sub.add_parser(
            name,
            aliases=list(aliases),
            help=help_,
            parents=parents,
            add_help=False,
            allow_abbrev=False,
        )
        p.set_defaults(handler=handler, needs_profile=profile)
        return p

    # -- exécution ---------------------------------------------------------- #
    p = add("run", _cmd_run, "run a program (default when only a file is given)",
            profile=True)
    p.add_argument("file", metavar="FILE.exe")
    launch = p.add_mutually_exclusive_group()
    launch.add_argument("--proton", dest="launch_mode", action="store_const",
                        const="proton", help="launch with Proton (default)")
    launch.add_argument("--call", dest="launch_mode", action="store_const",
                        const="proton-call", help="launch with proton-call")
    launch.add_argument("--wine", dest="launch_mode", action="store_const",
                        const="wine", help="launch with Wine")
    prefix = p.add_mutually_exclusive_group()
    prefix.add_argument("--ps", dest="prefix_mode", action="store_const",
                        const="shared", help="shared prefix")
    prefix.add_argument("--pa", dest="prefix_mode", action="store_const",
                        const="auto", help="automatic prefix")
    prefix.add_argument("--pc", dest="prefix_mode", action="store_const",
                        const="custom", help="custom prefix")
    p.set_defaults(launch_mode="proton", prefix_mode="main")
    p.add_argument("--steam", action="store_true",
                   help="started by Steam (see 'install-steam'): reuse Steam's environment; "
                        "arguments after '-- FILE.exe' are passed to the program")

    # -- bibliothèque ------------------------------------------------------- #
    p = add("add", _cmd_add, "register a program", profile=True)
    p.add_argument("file", metavar="FILE.exe")

    p = add("addux", _cmd_addux,
            "register a program and open the UX (file-manager integration)",
            profile=True)
    p.add_argument("file", metavar="FILE.exe")

    p = add("edit", _cmd_edit, "edit a program's settings", profile=True)
    p.add_argument("file", metavar="FILE.exe")

    p = add("import", _cmd_import,
            "import existing applications (Lutris, Bottles, Heroic, Wine)")
    p.add_argument("-y", "--yes", action="store_true",
                   help="do not ask for confirmation")

    p = add("install-steam", _cmd_install_steam,
            "install Proton-Autogen as a Steam compatibility tool")
    p.add_argument("--dest", metavar="DIR",
                   help="compatibilitytools.d directory "
                        "(default: ~/.steam/root/compatibilitytools.d)")
    p.add_argument("--launcher", metavar="PATH",
                   help="path of the proton-autogen launcher (default: found in PATH)")
    p.add_argument("-y", "--yes", action="store_true",
                   help="do not ask before replacing an existing installation")
    p.add_argument("--check", action="store_true",
                   help="only verify permissions and integrity; change nothing")

    # -- interface, informations, diagnostics ------------------------------ #
    add("ux", _cmd_ux, "open the graphical dashboard")
    add("list-protons", _cmd_list_protons, "list detected Proton versions",
        aliases=("lp",))
    add("list-programs", _cmd_list_programs, "list registered programs")
    add("proton-paths", _cmd_proton_paths, "show the Proton search paths")
    add("diag", _cmd_diag, "print a diagnostic report", aliases=("diagnostic",))
    add("check-gamescope", _cmd_check_gamescope, "check gamescope support",
        aliases=("check-gs",))
    add("check-translations", _cmd_check_translations,
        "check translation completeness", aliases=("check-tr",))
    add("json-profile", _cmd_json_profile, "export the default profiles")
    add("about", _cmd_about, "about the project")
    add("version", _cmd_version, "print the version")
    add("help", _cmd_help, "show the help")
    add("help-env", _cmd_help_env, "help about environment variables")

    # alias inclus : sert à repérer la sous-commande dans normalize_argv()
    parser.command_names = frozenset(sub.choices)
    return parser


# --------------------------------------------------------------------------- #
# Handlers : imports différés, retournent un code ou None, lèvent CliError
# --------------------------------------------------------------------------- #

def _require_file(path: str) -> str:
    if not os.path.exists(os.path.expanduser(path)):
        raise CliError(f"file not found: {path}", EXIT_NOT_FOUND)
    return path


def _cmd_run(args):
    from proton_autogen.backend import run
    # Les paramètres Steam ne sont transmis que lorsqu'ils servent : un
    # lancement classique appelle run() exactement comme avant.
    extra = {}
    if getattr(args, "game_args", None):
        extra["game_args"] = args.game_args
    if getattr(args, "steam", False):
        extra["from_steam"] = True
    return run(args.file, args.launch_mode, args.prefix_mode, **extra)


def _cmd_install_steam(args):
    from proton_autogen.steam_compat import SteamInstallError, run_install_steam
    try:
        return run_install_steam(dest=args.dest, launcher=args.launcher,
                                 assume_yes=args.yes, check=args.check)
    except SteamInstallError as exc:
        raise CliError(str(exc), exc.code) from exc


def _cmd_add(args):
    from proton_autogen.editor import add_game
    return add_game(_require_file(args.file))


def _cmd_addux(args):
    from proton_autogen.cli_addux import run_addux
    return run_addux(_require_file(args.file))


def _cmd_edit(args):
    from proton_autogen.editor import edit_game_ui
    return edit_game_ui(args.file)


def _cmd_import(args):
    from proton_autogen.cli_import import run_import
    return run_import(assume_yes=args.yes)


def _cmd_ux(args):
    # Import différé : le tableau de bord tire GTK 4.
    try:
        from proton_autogen.ux.dashboard import start_dashboard
    except (ImportError, ValueError) as exc:  # ValueError : gi.require_version()
        raise CliError(f"cannot start the UX (is GTK 4 installed?): {exc}") from exc
    return start_dashboard()


def _cmd_list_protons(args):
    from proton_autogen.backend import list_protons
    return list_protons()


def _cmd_list_programs(args):
    from proton_autogen.backend import list_programs
    return list_programs()


def _cmd_proton_paths(args):
    from proton_autogen.core import print_proton_paths
    return print_proton_paths()


def _cmd_diag(args):
    from proton_autogen.diag import print_diagnostic
    return print_diagnostic()


def _cmd_check_gamescope(args):
    from proton_autogen.utils.diag_gamescope import run_gamescope_check
    return run_gamescope_check()


def _cmd_check_translations(args):
    from proton_autogen.i18n import check_translations_cli
    return check_translations_cli()


def _cmd_json_profile(args):
    from proton_autogen.core import export_default_profiles
    return export_default_profiles()


def _cmd_about(args):
    from proton_autogen.core import print_about
    return print_about()


def _cmd_version(args):
    from proton_autogen.config import VERSION
    print(f"{PROG} {VERSION}")


def _cmd_help(args):
    from proton_autogen.i18n import detect_help_env_lang
    from proton_autogen.info import print_help
    return print_help(detect_help_env_lang())


def _cmd_help_env(args):
    from proton_autogen.core import print_help_env
    from proton_autogen.i18n import detect_help_env_lang
    return print_help_env(detect_help_env_lang())


# --------------------------------------------------------------------------- #
# Orchestration
# --------------------------------------------------------------------------- #

def _load_profile(raw_argv: Sequence[str]) -> None:
    # Le mode --profile affecte core.USER_PROFILE / core.USER_PROFILE_DATA : il faut le
    # MODULE (un `from core import USER_PROFILE` ne ferait qu'une copie figée à None).
    from proton_autogen import core
    from proton_autogen.core import load_profile_from_cli

    core.USER_PROFILE, core.USER_PROFILE_DATA = load_profile_from_cli(
        [PROG, *raw_argv]
    )


def _dispatch(args: argparse.Namespace, raw_argv: Sequence[str]) -> int:
    if args.needs_profile and getattr(args, "profile", None):
        _load_profile(raw_argv)
    result = args.handler(args)
    # Seuls de vrais entiers sont propagés (un bool/None/objet = succès).
    if isinstance(result, int) and not isinstance(result, bool):
        return result
    return EXIT_OK


def _exit_code(code) -> int:
    """Interprète l'argument d'un SystemExit comme le fait Python."""
    if code is None:
        return EXIT_OK
    if isinstance(code, int):
        return code
    print(code, file=sys.stderr)  # sys.exit("message")
    return EXIT_ERROR


def _silence_stdout() -> None:
    """`proton-autogen --list-programs | head` : évite le BrokenPipe à la sortie."""
    try:
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
    except Exception:
        pass


def main(argv: Optional[Sequence[str]] = None) -> int:
    raw = list(sys.argv[1:] if argv is None else argv)
    debug = "--debug" in raw or bool(os.environ.get("PROTON_AUTOGEN_DEBUG"))

    try:
        parser = build_parser()
        if not raw:
            print(
                f"usage: {PROG} <command> [options]\n"
                f"       {PROG} [options] <file.exe>\n"
                f"Try '{PROG} --help' for more information.",
                file=sys.stderr,
            )
            return EXIT_USAGE
        head, game_args = split_game_args(raw)
        args = parser.parse_args(normalize_argv(head, parser.command_names))
        if game_args and args.command != "run":
            raise CliError(f"unexpected arguments: {' '.join(game_args)}", EXIT_USAGE)
        args.game_args = game_args
        return _dispatch(args, head)
    except CliError as exc:
        print(f"{PROG}: {exc.message}", file=sys.stderr)
        return exc.code
    except SystemExit as exc:  # argparse, ou un sys.exit() resté dans un module
        return _exit_code(exc.code)
    except KeyboardInterrupt:
        print("", file=sys.stderr)
        return EXIT_INTERRUPTED
    except BrokenPipeError:
        _silence_stdout()
        return EXIT_OK
    except Exception as exc:
        if debug:
            traceback.print_exc()
        print(
            f"{PROG}: unexpected error: {exc.__class__.__name__}: {exc}"
            + ("" if debug else "\n(re-run with --debug for the traceback)"),
            file=sys.stderr,
        )
        return EXIT_ERROR
