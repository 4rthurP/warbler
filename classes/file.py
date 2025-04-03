import os
from . import app_root

class File:
    def __init__(self, path):
        self.path = os.path.join(app_root, path)

    def read(self):
        if not self.exists():
            raise FileNotFoundError(f'File {self.path} not found')
        
        with open(self.path) as f:
            return f.read()

    def write(self, data):
        with open(self.path, 'w') as f:
            f.write(data)

    def exists(self):
        return os.path.exists(self.path)