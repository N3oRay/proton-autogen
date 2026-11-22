"""Commande ``proton-autogen import`` (ex ``--import``).

Logique extraite du lanceur. Les entrées/sorties sont injectables
(``input_fn`` / ``print_fn``) pour pouvoir la tester sans terminal.
"""

from __future__ import annotations

from proton_autogen.cli import EXIT_ERROR, EXIT_OK, CliError
from proton_autogen.import_scan import (
    any_source_available,
    import_selected,
    scan_all,
    scan_wine_prefixes,
    total_count,
)

_IMPORT_LABELS = {
    "lutris": "Lutris",
    "bottles": "Bottles",
    "heroic": "Heroic",
    "wine": "Wine prefixes",
}

_YES = ("y", "yes", "o", "oui")


def _unit(count: int) -> str:
    return "application" if count == 1 else "applications"


def _ask(prompt: str, input_fn) -> str:
    try:
        return input_fn(prompt).strip()
    except EOFError as exc:
        raise CliError(
            "no terminal available to answer the prompt (use --yes to skip it)"
        ) from exc


def run_import(*, assume_yes: bool = False, input_fn=input, print_fn=print) -> int:
    print_fn("Import existing applications\n")

    results = scan_all()

    # Scan par défaut infructueux -> on demande un chemin à parcourir
    if not any_source_available(results):
        path = _ask(
            "No existing installation detected automatically.\n"
            "Folder to scan (leave empty to cancel): ",
            input_fn,
        )
        if not path:
            print_fn("Cancelled.")
            return EXIT_OK

        results["wine"] = scan_wine_prefixes(extra_paths=[path])

        if not any_source_available(results):
            print_fn("Nothing to import.")
            return EXIT_OK

    enabled = set()
    for source, data in results.items():
        items = data.get("items", [])
        if not items:
            continue

        enabled.add(source)
        label = _IMPORT_LABELS.get(source, source)
        print_fn(f"  [x] {label:<14} {len(items)} {_unit(len(items))}")

        for item in sorted(items, key=lambda i: (i.get("name") or "").lower()):
            name = item.get("name") or "(unknown)"
            if item.get("needs_manual_exe"):
                print_fn(f"        - {name}  (exe not detected, will be skipped)")
            else:
                print_fn(f"        - {name}")

        print_fn("")

    total = total_count(results)
    if total == 0:
        print_fn("Nothing to import.")
        return EXIT_OK

    if not assume_yes:
        answer = _ask(f"Import {total} {_unit(total)}? [y/N]: ", input_fn).lower()
        if answer not in _YES:
            print_fn("Cancelled.")
            return EXIT_OK

    summary = import_selected(results, enabled)

    print_fn(
        f"\n{summary['imported']} imported, {summary['skipped']} skipped "
        f"(already present), {len(summary['errors'])} errors."
    )

    if summary["errors"]:
        print_fn("\nErrors:")
        for err in summary["errors"]:
            print_fn(f"  - {err['exe']}: {err['error']}")
        return EXIT_ERROR  # import partiel : les scripts doivent pouvoir le détecter

    return EXIT_OK
