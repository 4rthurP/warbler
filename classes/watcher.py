import logging 
from typing import List
from datetime import datetime
from sqlalchemy.orm import Session

from notifier import Notifier
from config import Config
from entry import Entry

from . import database, local_tz
from models import WatcherRun, EntryModel

class Watcher:
    name: str
    notifiers: List[Notifier] = []
    config: Config
    source: str

    entries: dict[str, List[Entry]]

    def __init__(
            self, 
            config: Config
    ):
        self.config = config
        self.name = config.get("name")
        self.source = config.get("source")

    def load(self):
        notifiers = self.config.get('notifiers')
        for notifier in notifiers:
            self.add_notifier(notifier)

    def run(self):
        run = WatcherRun(
            name = self.name,
            run_start = datetime.now(),
            run_status = 'running',
        )

        start_date = self.find_latest_entry_date()
        self.find_new_logs(start_date)
        self.save_new_entries(run)
        self.send_new_entries(run)
        self.save_run(run)

    def find_latest_run_date(self):
        session = Session(database)
        latest_entry = (
            session
            .query(WatcherRun)
            .where(WatcherRun.name == self.name)
            .order_by(WatcherRun.run_start.desc())
            .first()
        )
        session.close()

        if latest_entry:
            return latest_entry.entry_date
        return datetime.now(tz = local_tz)
    
    def find_new_logs(self, start_date: datetime) -> List:
        pass

    def parse_entries_from_logs(self):
        for log in self.logs:
            service = self.find_service(log.source)
            if service:
                entries = service.parse_entries(log)
                self.entries.extend(entries)

    def save_new_entries(self, run: WatcherRun):
        session = Session(database)
        for entry in self.entries:
            session.add(entry.get_model(run.id))
        session.commit()
        session.close()

    def send_new_entries(self, run: WatcherRun):
        for notifier in self.notifiers:
            notifier.send(run, self.entries)

    def save_run(self, run: WatcherRun):
        run.run_end = datetime.now()
        run.run_status = 'complete'
        session = Session(database)
        session.add(run)
        session.commit()
        session.close()

    def add_notifier(self, notifier):
        self.notifiers.append(Notifier(**notifier))

    def find_service(self, source: str):
        if source in self.services:
            return self.services[source]
        
        logging.error(f'No service found for source {source}')
        return None
    