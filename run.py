from  classes.watcher import Watcher
from classes.config import Config

from config import config

config = Config(config)
for watcher_config in config.get('watchers'):
    watcher_class = watcher_config.get('class')
    watcher = watcher_class(watcher_config)
    watcher.load()
    watcher.run()