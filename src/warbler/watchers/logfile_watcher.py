import logging
import re
from datetime import datetime

from .. import LOCAL_TZ
from ..classes.entry import Entry
from ..classes.file import File
from ..classes.watcher import Watcher


class LogFileWatcher(Watcher):
    source_file: File

    def find_new_entries(self, start_date: datetime) -> list[Entry]:
        self.source_file = File(self.config.get("source"))

        if not self.source_file.exists():
            logging.warning(
                f"LogFileWatcher: File {self.source_file.path} does not exist"
            )
            return [
                Entry(
                    "self",
                    self.__class__.__name__,
                    "log",
                    datetime.now(LOCAL_TZ),
                    "LogFileWatcher: File not found",
                    f"File {self.source_file.path} does not exist",
                )
            ]

        jobs: list[Entry] = []
        current_job = None

        with open(self.source_file.path) as file:
            lines = file.readlines()

        for line in lines:
            if " - START - " in line:
                # If we are already in a job, save it before starting a new one
                # This can happen if the previous job was not closed properly in the log file
                if current_job is not None:
                    jobs.append(current_job)
                    current_job = None

                timestamp, script, pid, user = self.parseStartLine(line.strip())

                # Handle timestamp and check it is after the start date
                timestamp = datetime.strptime(
                    timestamp, "%Y-%m-%d %H:%M:%S"
                ).astimezone(LOCAL_TZ)
                logging.debug(f"LogFileWatcher: Found START line: {line.strip()}")
                if timestamp <= start_date:
                    current_job = None
                    continue

                script = self.cleanScriptName(script)
                # Create a new job entry
                current_job = Entry("log", self.source_file.path, script, timestamp)

                current_job.set("start_timestamp", timestamp)
                current_job.set("script", script)
                current_job.set("pid", int(pid))
                current_job.set("user", user)

            # If we are not in a job, skip the line until we find a START line
            if current_job is None:
                continue

            current_job.content.append(line.strip())

            # Check for END line
            if " - END - " in line:
                timestamp, script, pid, exit_code, load_avg, mem_usage = (
                    self.parseEndLine(line.strip())
                )
                script = self.cleanScriptName(script)
                if script != current_job.get("script") or int(pid) != current_job.get(
                    "pid"
                ):
                    # If the script or pid does not match, we have an unexpected END line
                    logging.error(
                        f"LogFileWatcher: Unexpected END line: {line.strip()}, expected script: -{current_job.get('script')}-, got -{script}-, expected pid: -{current_job.get('pid')}-, got -{pid}-"
                    )
                    jobs.append(
                        Entry(
                            "self",
                            self.__class__.__name__,
                            "log",
                            datetime.now(LOCAL_TZ),
                            "LogFileWatcher: Unexpected END line",
                            f"Mismatch between the START line ({current_job.content[0]}) and the END line ({line.strip()})",
                        )
                    )
                    current_job = None
                    continue

                current_job.set("exit_code", int(exit_code))
                current_job.set("load_avg", load_avg)
                current_job.set("mem_usage", mem_usage)
                current_job.set(
                    "end_timestamp",
                    datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").astimezone(
                        LOCAL_TZ
                    ),
                )
                current_job.set(
                    "duration",
                    (
                        current_job.get("end_timestamp")
                        - current_job.get("start_timestamp")
                    ).total_seconds(),
                )

                current_job.status = (
                    "success" if current_job.get("exit_code") == 0 else "failure"
                )
                current_job.title = f"{current_job.status if current_job.status == 'success' else current_job.status + '(' + exit_code + ')'}: Job {current_job.get('script')} (PID: {current_job.get('pid')}) on {current_job.get('end_timestamp').strftime('%Y-%m-%d %H:%M:%S')}"

                logging.debug(f"LogFileWatcher: Found END line: {line.strip()}")
                logging.debug(
                    f"LogFileWatcher: Job {current_job.get('script')} (PID: {current_job.get('pid')}) ended with exit code {exit_code} and duration {current_job.get('duration')} seconds"
                )

                jobs.append(current_job)
                current_job = None

        return jobs

    def parseStartLine(self, start_line):
        """
        Parses a START log line and extracts:
        - Timestamp
        - Script path
        - PID
        - User
        """
        pattern = re.compile(r"^(.*?) - START - (.*?) - PID: (\d+) - User: (.*)$")
        match = pattern.match(start_line)

        if match:
            return match.groups()

        return None, None, None, None

    def parseEndLine(self, end_line):
        """
        Parses an END log line and extracts:
        - Timestamp
        - Script path
        - PID
        - Exit Code
        - Load Average
        - Memory Usage
        """
        pattern = re.compile(
            r"^(.*?) - END - (.*?) - PID: (\d+) - Exit Code: (\d+) - Load Avg: (.*?) - Mem Usage: (.*?)$"
        )
        match = pattern.match(end_line)

        if match:
            return match.groups()

        logging.error(f"LogFileWatcher: Failed to parse END line: {end_line}")
        return None, None, None, None, None, None

    def cleanScriptName(self, script_name):
        """
        Cleans the script name by removing the path and keeping only the file name.
        """
        if not script_name:
            return ""

        last_slash_index = script_name.rfind("/")
        if last_slash_index == -1:
            return script_name

        return script_name[last_slash_index + 1 :]
