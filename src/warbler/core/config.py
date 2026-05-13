import logging
from typing import Any


class Config:
    def __init__(self, config: dict):
        self.config = config

    def get(self, key: str, default: Any | None = None, raise_exception: bool = True):
        if key in self.config:
            return self.config[key]

        logging.warning(f"Key {key} not found in config")
        if raise_exception:
            raise KeyError(f"Key {key} not found in config")

        return default
