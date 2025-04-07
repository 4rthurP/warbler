from datetime import datetime
from typing import List

from ..models import EntryModel

class EntryStatus:
    SUCCESS = "success"
    FAILURE = "failure"
    WARNING = "warning"
    INFO = "info"
    UNKNOWN = "unknown"

class Entry:
    properties: dict[str, str] = {}
    title: str
    source_type: str
    source_name: str
    service: str
    timestamp: datetime
    content: List[str]
    status: EntryStatus

    def __init__(
            self, 
            source_type: str, 
            source_name: str, 
            service: str, 
            timestamp: datetime, 
            title: str|None = None, 
            content: List[str]|str|None = None, 
            status: EntryStatus = EntryStatus.UNKNOWN
        ):
        self.source_type = source_type
        self.source_name = source_name
        self.service = service
        self.timestamp = timestamp
        self.properties = {}
        self.status = status

        if title is not None:
            self.title = title
            
        if isinstance(content, str):
            self.content.append(content)
        elif isinstance(content, list):
            self.content = content
        else:
            self.content = []

    def getModel(self, watcher, run_id):
        return EntryModel(
            source = self.source,
            title = self.title,
            service = self.service,
            status = self.status,
            watcher_name = watcher,
            watcher_run_id = run_id,
            source_name = self.source_name,
            source_type = self.source_type,
            timestamp = self.timestamp,
            created_at = datetime.now(),
            additional_info = self.properties
        )