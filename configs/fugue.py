import os

from .notifiers.slack_notifier import SlackNotifier
from .watchers.ping_watcher import PingWatcher

config = {
    "watchers": [
        {
            "class": PingWatcher,
            "name": "Concerto Uptime",
            "command": "tailscale ping --c 3 Concerto",
            "success_match_pattern": "pong",
            "on_error_retry_interval": "5m",
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