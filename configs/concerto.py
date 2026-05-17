import os

from .notifiers.slack_notifier import SlackNotifier
from .watchers.logfile_watcher import LogFileWatcher
from .watchers.ping_watcher import PingWatcher

config = {
    "watchers": [
        {
            "class": LogFileWatcher,
            "name": "CronWacther",
            "source": os.getenv("CRON_LOG_FILE", "/var/log/cron.log"),
            "notifiers": [
                SlackNotifier(
                    name="slack_cron",
                    webhook_url=os.getenv("SLACK_WEBHOOK_URL_INFOS"),
                )
            ],
        },
        {
            "class": PingWatcher,
            "name": "Fugue Uptime",
            "command": "tailscale ping --c 3 fugue",
            "success_match_pattern": "pong",
            "on_error_retry_interval": "30m",
            "on_success_retry_interval": None,
            "notifiers": [
                SlackNotifier(
                    name="slack_cron",
                    webhook_url=os.getenv("SLACK_WEBHOOK_URL_INFOS"),
                )
            ],
        },
    ]
}
