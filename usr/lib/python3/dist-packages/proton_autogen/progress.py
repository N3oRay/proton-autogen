class Progress:

    def __init__(self, callback=None):
        self.callback = callback
        self.current = {
            "percent": 0,
            "message": ""
        }

    def update(self, percent, message):
        self.current["percent"] = percent
        self.current["message"] = message

        if self.callback:
            self.callback(percent, message)
