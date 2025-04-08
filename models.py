from sqlalchemy import (
    String,
    Integer,
    ForeignKey,
    DateTime,
    JSON,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    mapped_column,
    relationship,
)

class Base(DeclarativeBase):
    pass
    

class WatcherRun(Base):
    __tablename__ = "watcher_runs"
    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String(255))
    run_start = mapped_column(DateTime)
    run_end = mapped_column(DateTime, default=None, nullable=True)
    run_status = mapped_column(String(50))
    entries = relationship("EntryModel")
    def __repr__(self) -> str:
        return f"{self.run_start} - {self.name} run status: {self.run_status} (in {self.run_end - self.run_start}s)"

class EntryModel(Base):
    __tablename__ = "entries"
    id = mapped_column(Integer, primary_key=True)
    title = mapped_column(String(255))
    service = mapped_column(String(255))
    status = mapped_column(String(255))
    watcher_name = mapped_column(String(255))
    watcher_run_id = mapped_column(ForeignKey("watcher_runs.id"))
    source_name = mapped_column(String(255))
    source_type = mapped_column(String(255))
    timestamp = mapped_column(DateTime)
    created_at = mapped_column(DateTime)
    additional_info = mapped_column(JSON)

    def __repr__(self) -> str:
        return f"{self.entry_date} - New entry from {self.source_name}: {self.title} - Watched by {self.watcher_name}"