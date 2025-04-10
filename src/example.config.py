from .watchers.logfile_watcher import LogFileWatcher
from .notifiers.slack_notifier import SlackNotifier

config = {
    'watchers': [
        {
            'class': LogFileWatcher,
            'name': 'test',
            'source': "/var/log/cron.log",
            'notifiers': [
                    SlackNotifier(
                    name='slack_cron',
                    webhook_url=SLACK_WEBHOOK_URL,
                )
            ]
        }
    ]
}