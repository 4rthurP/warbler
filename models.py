from datetime import datetime
import json

from sqlalchemy import (
    String,
    Integer,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    ForeignKey,
    mapped_column,
    relationship,
)

class Base(DeclarativeBase):
    pass
    

class WatcherRun(Base):
    __tablename__ = "watcher_runs"
    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String)
    run_start = mapped_column(datetime)
    run_end = mapped_column(datetime, default=None, nullable=True)
    run_status = mapped_column(String(50))
    entries = relationship("Entry")
    def __repr__(self) -> str:
        return f"{self.run_start} - {self.name} run status: {self.run_status} (in {self.run_end - self.run_start}s)"

class EntryModel(Base):
    __tablename__ = "entries"
    id = mapped_column(Integer, primary_key=True)
    source = mapped_column(String)
    title = mapped_column(String)
    service = mapped_column(String)
    status = mapped_column(String)
    watcher_name = mapped_column(String)
    watcher_run_id = mapped_column(ForeignKey("watcher_runs.id"))
    source_name = mapped_column(String)
    source_type = mapped_column(String)
    timestamp = mapped_column(datetime)
    created_at = mapped_column(datetime)
    additional_info = mapped_column(json)

    def __repr__(self) -> str:
        return f"{self.entry_date} - New entry from {self.source}: {self.message} - Watched by {self.watcher_name} - Logged by {self.logger_name} ({self.logger_source})"