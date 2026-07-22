import threading
import time

class Progress:
    _spinner = ("|", "/", "-", "\\")

    def __init__(self, callback=None):
        self.callback = callback
        self.current = {"percent": 0, "message": ""}
        self._running = False
        self._thread = None
        self._spin = 0

    def update(self, percent, message):
        self.current["percent"] = percent
        self.current["message"] = message

        if self.callback:
            self.callback(percent, message)

    def start_spinner(self, percent=90, message="Launching"):
        self._running = True

        def worker():
            while self._running:
                frame = self._spinner[self._spin]
                self._spin = (self._spin + 1) % len(self._spinner)
                self.update(percent, f"{frame} {message}")
                time.sleep(0.1)

        self._thread = threading.Thread(target=worker, daemon=True)
        self._thread.start()

    def stop_spinner(self):
        self._running = False
        if self._thread:
            self._thread.join()
