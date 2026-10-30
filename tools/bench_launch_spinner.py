#!/usr/bin/env python3
# tools/bench_launch_spinner.py
"""
Mesure le CPU consommé par le spinner de la popup de lancement avec un thème CSS.

Usage :
    python3 tools/bench_launch_spinner.py CHEMIN/theme.css [secondes]

Comparer l'ancienne et la nouvelle version d'un thème, sur la même machine, dans
les mêmes conditions (rien d'autre d'ouvert). Pour amplifier l'écart (et simuler
une machine sans accélération graphique ou une VM) :

    GSK_RENDERER=cairo python3 tools/bench_launch_spinner.py theme.css 15

Affiche le temps CPU du processus (utilisateur + système) en % d'un cœur, sur la
durée mesurée (la première seconde et demie, le temps d'afficher la fenêtre, est
exclue). Utilise psutil, déjà une dépendance du projet.
"""

import sys
import time

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gdk, GLib, Gtk  # noqa: E402

import psutil  # noqa: E402

WARMUP_MS = 1500


def _load_css(path):
    provider = Gtk.CssProvider()
    text = open(path, encoding="utf-8").read()

    try:
        provider.load_from_string(text)         # GTK >= 4.12
    except AttributeError:
        provider.load_from_data(text.encode())  # GTK 4.0 - 4.10

    Gtk.StyleContext.add_provider_for_display(
        Gdk.Display.get_default(),
        provider,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
    )


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1

    css_path = sys.argv[1]
    duration = float(sys.argv[2]) if len(sys.argv) > 2 else 10.0

    app = Gtk.Application(application_id="io.github.N3oRay.ProtonAutogen.Bench")
    process = psutil.Process()
    state = {}

    def cpu_seconds():
        times = process.cpu_times()
        return times.user + times.system

    def on_activate(application):
        _load_css(css_path)

        window = Gtk.ApplicationWindow(
            application=application, default_width=280, default_height=220
        )
        window.add_css_class("launch-dialog")

        spinner = Gtk.Spinner()
        spinner.set_size_request(48, 48)
        spinner.set_halign(Gtk.Align.CENTER)
        spinner.set_valign(Gtk.Align.CENTER)
        spinner.start()

        window.set_child(spinner)
        window.present()

        def begin():
            state["t0"] = time.perf_counter()
            state["c0"] = cpu_seconds()
            return False

        def finish():
            wall = time.perf_counter() - state["t0"]
            cpu = cpu_seconds() - state["c0"]
            renderer = window.get_native().get_renderer()
            name = type(renderer).__name__ if renderer else "?"
            print(f"{css_path}\n  CPU : {cpu / wall * 100:5.1f} % d'un cœur "
                  f"({cpu:.2f} s CPU / {wall:.1f} s) — rendu : {name}")
            application.quit()
            return False

        GLib.timeout_add(WARMUP_MS, begin)
        GLib.timeout_add(int(WARMUP_MS + duration * 1000), finish)

    app.connect("activate", on_activate)
    return app.run(None)


if __name__ == "__main__":
    sys.exit(main())
