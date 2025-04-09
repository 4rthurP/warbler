import logging
from datetime import datetime
from typing import List

from ..models import EntryModel
from .. import LOCAL_TZ

class EntryStatus:
    SUCCESS = "success"
    FAILURE = "failure"
    WARNING = "warning"
    INFO = "info"
    UNKNOWN = "unknown"

class Entry:
    properties: dict = {}
    json_properties: dict[str, str] = {}
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
        self.status = status

        if title is not None:
            self.title = title
            
        self.content = []
        if isinstance(content, str):
            self.content.append(content)
        elif isinstance(content, list):
            self.content = content

    def get_model(self, watcher, run_id):
        return EntryModel(
            title = self.title,
            service = self.service,
            status = self.status,
            watcher_name = watcher,
            watcher_run_id = run_id,
            source_name = self.source_name,
            source_type = self.source_type,
            timestamp = self.timestamp,
            created_at = datetime.now(tz=LOCAL_TZ),
            additional_info = self.json_properties
        )
    
    def set(self, key: str, value):
        # Store the value as is for internal use
        self.properties[key] = value

        # Convert the value to a string for JSON serialization
        if isinstance(value, str):
            self.json_properties[key] = value
        elif isinstance(value, datetime):
            self.json_properties[key] = value.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(value, int) or isinstance(value, float):
            self.json_properties[key] = str(value)
        else:
            logging.warning(f"Unsupported type for key {key}: {type(value)}, storing as string")
            self.json_properties[key] = str(value)

    def get(self, key: str):
        if key in self.properties:
            return self.properties[key]
        
        logging.warning(f"Key {key} not found in entry properties")
        return None