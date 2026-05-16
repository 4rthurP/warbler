from fastapi import FastAPI

from warbler.config import config
from warbler.core.config import Config

WATCHERS_CONFIG = Config(config)

app = FastAPI()


@app.get("/run_watchers")
def run_watchers():
    for watcher_config in WATCHERS_CONFIG.get("watchers"):
        # Remove extra args to avoid pydantic extra args exception
        config = watcher_config.copy()
        config.pop("class", None)

        # Get the watcher class and run it
        watcher_class = watcher_config.get("class")
        watcher = watcher_class(**config)
        watcher.run()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}
