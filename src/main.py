from typing import Union
from fastapi import FastAPI

from .config import config
from .classes.config import Config


WATCHERS_CONFIG = Config(config)

app = FastAPI()


@app.get("/run_watchers")
def run_watchers():
    for watcher_config in WATCHERS_CONFIG.get('watchers'):
        watcher_class = watcher_config.get('class')
        watcher = watcher_class(watcher_config)
        watcher.run()

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}