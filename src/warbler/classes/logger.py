from ..models import Entry


class Logger:
    name: str

    def __init__(self, config: dict):
        self.name = config.get("name")
        self.source = config.get("source")

    def __str__(self):
        return f"{self.name} ({self.source})"

    def log_new_entries(self):
        for entry in self.entries:
            self.log(entry)

    def log(self, entry: Entry):
        pass
