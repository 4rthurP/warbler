import logging
from datetime import datetime
from typing import Any

from pydantic import PrivateAttr

from warbler import LOCAL_TZ
from warbler.core.entry import Entry, EntryStatus
from warbler.watchers.command_watcher import CommandWatcher


class PingWatcher(CommandWatcher):
    """
    A watcher that pings a specified host to check its availability.
    Only returns an entry if the ping command fails, indicating the host is down.
    """
    # Override parent's save_if_empty. By default, don't save an entry if the ping is successful and there are no changes
    save_if_empty: bool = False  
    
    return_on_success: bool = False
    command: str = ""
    retry_interval: str | None = "5m"  # Notify every 5 minutes the host status
    on_error_retry_interval: str | None = None  # Custom retry interval when the last ping failed, if not set it will use the default notification_retry_interval
    on_success_retry_interval: str | None = None  # Custom retry interval when the last ping succeeded, if not set it will use the default notification_retry_interval

    _error_retry_interval_seconds: int | None = PrivateAttr()
    _success_retry_interval_seconds: int | None = PrivateAttr()


    def model_post_init(self, context: Any) -> None:
        super().model_post_init(context)

        if self.command == "":
            self.command = f"ping -c 1 {self.source}"

        self._error_retry_interval_seconds = self.parse_time_interval(self.on_error_retry_interval or self.retry_interval)
        self._success_retry_interval_seconds = self.parse_time_interval(self.on_success_retry_interval or self.retry_interval)

    def parse_time_interval(self, interval: str | None) -> int | None:
        """
        Parse a time interval string (e.g. "5m", "1h", "1d3h") and return the interval in seconds.
        """
        if interval is None:
            return None

        total_seconds = 0
        time_units = {
            "s": 1,
            "m": 60,
            "h": 3600,
            "d": 86400,
        }

        current_number = ""
        for char in interval:
            if char.isdigit():
                current_number += char
            elif char in time_units and current_number:
                total_seconds += int(current_number) * time_units[char]
                current_number = ""
            else:
                logging.warning(f"Invalid character in time interval: {char}")

        if current_number:
            logging.warning(f"Trailing number in time interval without unit: {current_number}")

        return total_seconds
        

    def get_command(self):
        return f"ping -c 1 {self.source}"

    def find_new_entries(self, start_date: datetime) -> list[Entry]:

        entry = super().find_new_entries(start_date)[0]  # Get the command entry

        # Check the last ping result to determine the retry interval
        latest_entry = self.get_latest_entry()

        if not latest_entry:
            return [entry]  

        # If the status changed, notify immediately regardless of the retry interval 
        last_ping_failed = latest_entry.status == EntryStatus.FAILURE
        if not last_ping_failed and entry.status == EntryStatus.FAILURE:
            logging.info(f"PingWatcher: Host {self.source} is down, ping command failed.")
            return [entry]
        if last_ping_failed and entry.status == EntryStatus.SUCCESS:
            logging.info(f"PingWatcher: Host {self.source} is up, ping command succeeded.")
            entry.set_content(f"Host {self.source} is back up after being down.")  # Update the content for a successful ping after a failure
            return [entry]

        # Else compare the time since the last ping to the retry interval
        if last_ping_failed:
            time_since_last_ping = (datetime.now(LOCAL_TZ) - latest_entry.created_at).total_seconds()
            if time_since_last_ping >= self._error_retry_interval_seconds or self._error_retry_interval_seconds is None:
                # Delay is over or no delay set, return the entry
                return [entry]  

            logging.debug(f"PingWatcher: Last ping failed {time_since_last_ping} seconds ago, which is less than the error retry interval of {self._error_retry_interval_seconds} seconds. Skipping ping.")
            return []
        
        if self._success_retry_interval_seconds is None:
            if self.return_on_success:
                return [entry]  # No retry interval set, return the entry if configured to do so
            logging.debug(f"PingWatcher: Host {self.source} is up, no entry returned")
            return []  # No retry interval set and not configured to return on success, skip the entry

        time_since_last_ping = (datetime.now(LOCAL_TZ) - latest_entry.created_at).total_seconds()
        if time_since_last_ping >= self._success_retry_interval_seconds:
            # Delay is over, return the entry
            return [entry]

        logging.debug(f"PingWatcher: Last ping succeeded {time_since_last_ping} seconds ago, which is less than the success retry interval of {self._success_retry_interval_seconds} seconds. Skipping ping.")
        return []