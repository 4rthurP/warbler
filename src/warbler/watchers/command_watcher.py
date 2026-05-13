import logging
import re
from datetime import datetime

from warbler import LOCAL_TZ
from warbler.classes.entry import Entry
from warbler.classes.file import File
from warbler.classes.watcher import Watcher


class CommandWatcher(Watcher):