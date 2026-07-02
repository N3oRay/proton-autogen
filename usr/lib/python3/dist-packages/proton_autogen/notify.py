from gi.repository import GLib


class NotificationCenter:
    def __init__(self):
        self.toast_callback = None

    def set_callback(self, cb):
        self.toast_callback = cb

    def notify(self, level, title, message, ui=True):
        print(f"[{level}] {title}: {message}")

        if ui and self.toast_callback:
            GLib.idle_add(
                self.toast_callback,
                {
                    "level": level,
                    "title": title,
                    "message": message,
                },
            )


notifications = NotificationCenter()
