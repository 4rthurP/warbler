import logging
from datetime import datetime

from pydantic import BaseModel, ConfigDict, PrivateAttr
from sqlalchemy.orm import Session

from warbler import LOCAL_TZ, engine
from warbler.core.entry import Entry
from warbler.core.notifier import Notifier
from warbler.models import EntryModel, WatcherRun


class Watcher(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    notifiers: list[Notifier]
    name: str
    source: str
    save_if_empty: bool = True

    _entries: list[Entry] = PrivateAttr(default_factory=list)
    _notifiers: list[Notifier] = PrivateAttr()

    def load(self):
        """Load the watcher configuration"""
        self._notifiers = []
        for notifier in self.notifiers:
            self.add_notifier(notifier)

    def run(self):
        """
        Run the watcher. This method will be called by the main loop.
        It will load the watcher, find the new entries, save them to the database
        and send them to the notifiers.
        The watcher will also save the run to the database.
        """
        # Load the watcher configuration
        self.load()

        # Saves the watcher's infos in a ORM model
        run = WatcherRun(
            name=self.name,
            run_start=datetime.now(),
            run_status="running",
        )

        start_date = self.find_latest_run_date()  # Get the latest run date
        self._entries = self.find_new_entries(
            start_date
        )  # Find the new entries since this date
        self.save_new_entries(run)  # Save the new entries to the database
        self.send_new_entries()  # Send the new entries to the notifiers
        self.save_run(run)  # Save the watcher's run to the database

    def find_latest_run_date(self):
        """Find the latest run date for this watcher"""

        # Get the latest run from the database
        session = Session(engine)
        latest_run: WatcherRun = (
            session.query(WatcherRun)
            .where(WatcherRun.name == self.name)
            .order_by(WatcherRun.run_start.desc())
            .first()
        )
        session.close()

        if latest_run:
            return latest_run.run_start.astimezone(LOCAL_TZ)

        # If there is no run, return the epoch
        return datetime(1970, 1, 1, tzinfo=LOCAL_TZ)

    def find_new_entries(self, start_date: datetime) -> list[Entry]:
        return []

    def save_new_entries(self, run: WatcherRun):
        """Save the new entries to the database"""
        session = Session(engine)
        for entry in self._entries:
            logging.info(f"Saving entry {entry} for run {run.id}")
            session.add(entry.get_model(run.name, run.id))
        session.commit()
        session.close()

    def send_new_entries(self):
        """Send the new entries to all notifiers"""
        for notifier in self._notifiers:
            notifier.send(self._entries)

    def get_latest_entry(self) -> Entry | None:
        """Get the latest entry for this watcher"""

        # Get the latest entry from the database
        session = Session(engine)
        latest_entry = (
            session.query(EntryModel)
            .where(EntryModel.source_name == self.name)
            .order_by(EntryModel.created_at.desc())
            .first()
        )
        session.close()

        return latest_entry

    def save_run(self, run: WatcherRun):
        """Save the run to the database"""

        # Check if there are no new entries and save the run if configured to do so
        if len(self._entries) == 0 and not self.save_if_empty:
            logging.info(
                f"Watcher {self.name} has no new entries and will not save the run"
            )
            return

        # Update the run's infos
        run.run_end = datetime.now()
        run.run_status = "complete"

        # Save the run to the database
        session = Session(engine)
        session.add(run)
        session.commit()
        session.close()

    def add_notifier(self, notifier: Notifier):
        """Add a notifier to the watcher"""
        self._notifiers.append(notifier)
