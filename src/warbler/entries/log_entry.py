from datetime import datetime
from typing import Any

from pydantic import PrivateAttr

from warbler.core.entry import Entry


class LogEntry(Entry):
    end_date: datetime
    status: str
    pid: str
    user: str
    load: str
    mem_usage: str

    _duration: float | None = PrivateAttr()

    def model_post_init(self, context: Any) -> None:
        super().model_post_init(context)

        # Calculate the duration if end_date and date are available
        if self.end_date and self.date:
            self._duration = (self.end_date - self.date).total_seconds()
        else:
            self._duration = None
