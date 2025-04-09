from datetime import datetime
from ..classes.entry import Entry

class LogEntry(Entry):
    end_date: datetime
    duration: float
    status: str
    pid: str
    user: str
    load: str
    mem_usage: str

    def __init__(
            self,
            source: str,
            content: str,
            date: datetime,
            end_date: datetime,
            status: str,
            pid: str,
            user: str,
            load: str,
            mem_usage: str
    ):
        self.source = source
        self.content = content
        self.date = date
        self.end_date = end_date
        self.duration = (end_date - date).total_seconds()
        self.status = status
        self.pid = pid
        self.user = user
        self.load = load
        self.mem_usage = mem_usage