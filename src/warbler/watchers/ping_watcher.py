import logging
from datetime import datetime

from warbler.core.config import Config
from warbler.core.entry import Entry, EntryStatus
from warbler.watchers.command_watcher import CommandWatcher


class PingWatcher(CommandWatcher):
    """
    A watcher that pings a specified host to check its availability.
    Only returns an entry if the ping command fails, indicating the host is down.
    """

    return_on_success: bool = False

    def __init__(self, config: Config):
        super().__init__(config)
        if not self.config.get("command"):
            self.command = self.get_command()

    def get_command(self):
        return f"ping -c {self.source}"

    def find_new_entries(self, start_date: datetime) -> list[Entry]:
        entry = super().find_new_entries(start_date)[0]  # Get the command entry

        if entry.status == EntryStatus.FAILURE or self.return_on_success:
            return [entry]
        
        logging.debug(f"PingWatcher: Host {self.source} is up, no entry returned")
        return []