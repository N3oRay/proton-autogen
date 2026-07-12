#!/usr/bin/env python3

import gi
gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GLib


class ToastOverlay(Gtk.Box):
    def __init__(self, max_toasts=5):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

        self.max_toasts = max_toasts

        self.set_halign(Gtk.Align.CENTER)
        self.set_valign(Gtk.Align.START)
        self.set_margin_top(12)
        self.set_spacing(6)

    def _limit(self):
        children = []

        child = self.get_first_child()

        while child:
            children.append(child)
            child = child.get_next_sibling()

        while len(children) > self.max_toasts:
            children.pop(0).unparent()

    def show(self, title="", message="", timeout=3):

        text = f"{title} — {message}" if title else message

        label = Gtk.Label(label=text)
        label.set_wrap(True)
        label.set_xalign(0)
        label.add_css_class("toast")

        frame = Gtk.Frame()
        frame.set_child(label)
        frame.add_css_class("toast-container")

        revealer = Gtk.Revealer()
        revealer.set_transition_type(
            Gtk.RevealerTransitionType.SLIDE_DOWN
        )
        revealer.set_transition_duration(250)
        revealer.set_child(frame)

        self.append(revealer)
        self._limit()

        GLib.idle_add(
            lambda: revealer.set_reveal_child(True)
        )

        def destroy():

            revealer.set_reveal_child(False)

            def remove():

                if revealer.get_parent():
                    revealer.unparent()

                return False

            GLib.timeout_add(250, remove)

            return False

        GLib.timeout_add_seconds(timeout, destroy)


    def success(self, message, timeout=3):
        self.show(
            title="✔",
            message=message,
            timeout=timeout,
        )

    def error(self, message, timeout=5):
        self.show(
            title="✖",
            message=message,
            timeout=timeout,
        )

    def warning(self, message, timeout=4):
        self.show(
            title="⚠",
            message=message,
            timeout=timeout,
        )

    def info(self, message, timeout=3):
        self.show(
            title="ℹ",
            message=message,
            timeout=timeout,
        )
