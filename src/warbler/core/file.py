from pathlib import Path

from warbler import APP_ROOT


class File:
    def __init__(self, path: str):
        self.path = Path(APP_ROOT) / path

    def read(self):
        if not self.exists():
            raise FileNotFoundError(f"File {self.path} not found")

        with self.path.open() as f:
            return f.read()

    def write(self, data: str):
        with self.path.open("w") as f:
            f.write(data)

    def exists(self):
        return self.path.exists()
