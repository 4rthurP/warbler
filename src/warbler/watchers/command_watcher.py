import logging
import re
from datetime import datetime
from subprocess import run

from warbler import LOCAL_TZ
from warbler.core.entry import Entry, EntryStatus
from warbler.core.watcher import Watcher


class CommandWatcher(Watcher):
    command: str
    title: str
    success_match_pattern: str | None
    timeout: int | None

    def find_new_entries(self, start_date: datetime) -> list[Entry]:
        configured_command = self.config.get("command")
        if configured_command and isinstance(configured_command, str):
            self.command = configured_command
        elif not hasattr(self, "command"):
            raise RuntimeError("CommandWatcher: No command specified in the class")

        self.success_match_pattern = self.config.get("success_match_pattern")

        # Run the command and get the output
        logging.debug(f"CommandWatcher: Running command: {self.command}")
        cmd_entry = self.run_command(self.command)
        logging.debug(f"CommandWatcher: Command output: {cmd_entry}")

        return [cmd_entry]


    def run_command(self, command: str) -> Entry:
        """
        Run the command using subprocess and return the output as a dictionary.
        """
        timeout = self.config.get("timeout", 60)  # Default timeout of 60 seconds

        result = run(command, shell=True, capture_output=True, text=True, timeout=timeout)
        if result.returncode != 0:
            status = EntryStatus.FAILURE
        elif self.success_match_pattern:
            if re.search(self.success_match_pattern, result.stdout):
                status = EntryStatus.SUCCESS
            else:
                status = EntryStatus.FAILURE
        else:
            status = EntryStatus.SUCCESS

        content = [f"Running command: '{command}'", f"Output: {result.stdout}"]
        if result.returncode != 0 and result.stderr:
            content.append(f"Error: {result.stderr}")
            
        return Entry(
            source_type="command",
            source_name=self.name,
            service="command",
            timestamp=datetime.now(LOCAL_TZ),
            title=self.config.get("title", f"Command '{command}' executed"),
            content=content,
            status=status,
        )