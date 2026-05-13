from warbler.models import EntryModel


class Logger:
    name: str
    entries: list[EntryModel]

    def __init__(self, config: dict):
        name = config.get("name")
        if name is None:
            raise ValueError("Logger config must include a name")

        self.name = name
        self.source = config.get("source")

    def __str__(self):
        return f"{self.name} ({self.source})"

    def log_new_entries(self):
        for entry in self.entries:
            self.log(entry)

    def log(self, entry:   EntryModel):
        pass
