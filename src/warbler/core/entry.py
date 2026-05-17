import logging
from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, PrivateAttr

from warbler import LOCAL_TZ
from warbler.models import EntryModel


class EntryStatus(StrEnum):
    SUCCESS = "success"
    FAILURE = "failure"
    WARNING = "warning"
    INFO = "info"
    UNKNOWN = "unknown"


class Entry(BaseModel):
    title: str | None = None
    source_type: str
    source_name: str
    service: str
    timestamp: datetime | str
    content: list[str] | str | None = None
    status: EntryStatus | str = EntryStatus.UNKNOWN

    _content: list[str] = PrivateAttr()
    _status: EntryStatus = PrivateAttr()
    _properties: dict[str, Any] = PrivateAttr()
    _json_properties: dict[str, str] = PrivateAttr()


    def model_post_init(self, context: Any) -> None:
        self._properties = {}
        self._json_properties = {}

        self._status = EntryStatus(self.status)

        if isinstance(self.content, str):
            self._content = [self.content]
        elif isinstance(self.content, list):
            self._content = self.content

    def get_model(self, watcher: str, run_id: str) -> EntryModel:
        return EntryModel(
            title=self.title,
            service=self.service,
            status=self._status,
            watcher_name=watcher,
            watcher_run_id=run_id,
            source_name=self.source_name,
            source_type=self.source_type,
            timestamp=self.timestamp,
            created_at=datetime.now(tz=LOCAL_TZ),
            additional_info=self._json_properties,
        )

    def set(self, key: str, value: Any):
        # Store the value as is for internal use
        self._properties[key] = value

        # Convert the value to a string for JSON serialization
        if isinstance(value, str):
            self._json_properties[key] = value
        elif isinstance(value, datetime):
            self._json_properties[key] = value.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(value, (int, float)):
            self._json_properties[key] = str(value)
        else:
            logging.warning(
                f"Unsupported type for key {key}: {type(value)}, storing as string"
            )
            self._json_properties[key] = str(value)

    def get(self, key: str):
        if key in self._properties:
            return self._properties[key]

        logging.warning(f"Key {key} not found in entry properties")
        return None

    def add_content(self, content: str):
        self._content.append(content)
    
    def get_content(self, line: int | None = None) -> list[str] | str | None:
        if line is not None:
            if line < len(self._content):
                return self._content[line]
            logging.warning(f"Requested line {line} is out of range for content")
            return None
        return self._content
