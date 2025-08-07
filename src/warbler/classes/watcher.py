import logging
from datetime import datetime

from sqlalchemy.orm import Session

from .. import LOCAL_TZ, engine
from ..models import WatcherRun
from .config import Config
from .entry import Entry
from .notifier import Notifier


class Watcher:
    notifiers: list[Notifier] = []
    entries: dict[str, list[Entry]]

    def __init__(self, config: Config):
        self.config: Config = config
        self.name: str = config.get("name")
        self.source: str = config.get("source")
        self.save_if_empty: bool = config.get("save_if_empty", True)

    def load(self):
        """Load the watcher configuration"""
        notifiers = self.config.get("notifiers")
        for notifier in notifiers:
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
        self.entries = self.find_new_entries(
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

    def find_new_entries(self, start_date: datetime) -> list:
        pass

    def save_new_entries(self, run: WatcherRun):
        """Save the new entries to the database"""
        session = Session(engine)
        for entry in self.entries:
            logging.info(f"Saving entry {entry} for run {run.id}")
            session.add(entry.get_model(run.name, run.id))
        session.commit()
        session.close()

    def send_new_entries(self):
        """Send the new entries to all notifiers"""
        for notifier in self.notifiers:
            notifier.send(self.entries)

    def save_run(self, run: WatcherRun):
        """Save the run to the database"""

        # Check if there are no new entries and save the run if configured to do so
        if len(self.entries) == 0 and not self.save_if_empty:
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
        self.notifiers.append(notifier)
