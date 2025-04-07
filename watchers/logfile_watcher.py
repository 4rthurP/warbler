import re 
from datetime import datetime

from ..classes.watcher import Watcher
from ..classes.file import File
from ..classes.entry import Entry, EntryStatus

from .. import LOCAL_TZ

class LogFileWatcher(Watcher):

    source_file: File

    def find_new_logs(self, start_date: datetime) -> list[Entry]:
        if not self.source_file.exists():
            return [
                Entry(
                    'self', 
                    self.__class__.__name__,
                    'log',
                    datetime.now(LOCAL_TZ),
                    "LogFileWatcher: File not found",
                    f"File {self.source_file.path} does not exist"
                )
            ]
        
        jobs: list[Entry] = []   
        current_job = None

        with open(self.source_file.path, "r") as file:
            lines = file.readlines()

        for line in lines:
            if " - START - " in line:
                # If we are already in a job, save it before starting a new one
                # This can happen if the previous job was not closed properly in the log file   
                if current_job is not None: 
                    jobs.append(current_job)
                    current_job = None

                timestamp, script, pid, user = self.parseStartLine(line.strip())
                timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")

                # Check if the timestamp is after the start date
                if timestamp >= start_date:
                    current_job = None
                    continue
                
                current_job = Entry(
                    'log',
                    self.source_file.path, 
                    script, 
                    timestamp
                )

                current_job.properties['start_timestamp'] = timestamp
                current_job.properties['script'] = script
                current_job.properties['pid'] = int(pid)
                current_job.properties['user'] = user
            
            # If we are not in a job, skip the line until we find a START line
            if current_job is None:
                continue

            current_job.content.append(line.strip())

            # Check for END line
            if " - END - " in line:
                timestamp, script, pid, exit_code, load_avg, mem_usage = self.parseEndLine(line.strip())
                if script != current_job.get("script") or pid != current_job.get("pid"):
                    current_job = None
                    jobs.append(
                        Entry(
                        'self', 
                        self.__class__.__name__,
                        'log',
                        datetime.now(LOCAL_TZ),
                        "LogFileWatcher: Unexpected END line",
                        f"Mismatch between the START line ({current_job.content[0]}) and the END line ({line.strip()})"
                        )
                    )
                    continue
                
                current_job.properties['exit_code'] = int(exit_code)
                current_job.properties['load_avg'] = load_avg
                current_job.properties['mem_usage'] = mem_usage
                current_job.properties['end_timestamp'] = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                current_job.properties['duration'] = (current_job['end_timestamp'] - current_job['start_timestamp']).total_seconds()
                current_job.status = 'success' if current_job['exit_code'] == 0 else 'failure'
                current_job.title = f"{current_job.status if current_job.status == 'success' else current_job.status+'('+exit_code+')'}: Job {current_job['script']} (PID: {current_job['pid']}) on {current_job.properties['end_timestamp'].strftime('%Y-%m-%d %H:%M:%S')}"

                jobs.append(current_job)
                current_job = None

        return jobs

    def parseStartLine(start_line):
        """
        Parses a START log line and extracts:
        - Timestamp
        - Script path
        - PID
        - User
        """
        pattern = re.compile(
            r"^(.*?) - START - (.*?) - PID: (\d+) - User: (.*)$"
        )
        match = pattern.match(start_line)

        if match:
            return match.groups()
        
        return None, None, None, None 

    def parseEndLine(end_line):
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
            r"^(.*?) - END - (.*?) - PID: (\d+) - Exit Code: (\d+) - Load Avg: ([\d.]+ [\d.]+ [\d.]+) - Mem Usage: ([\d.]+%)$"
        )
        match = pattern.match(end_line)

        if match:
            return match.groups()
        
        return None, None, None, None, None, None