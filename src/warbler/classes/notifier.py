from .entry import Entry


class Notifier:
    def __init__(self, name: str):
        self.name = name

    def send(self, entries: list[Entry]):
        pass
