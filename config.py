from .watchers.logfile_watcher import LogFileWatcher
from .notifiers.slack_notifier import SlackNotifier

from . import CRON_LOG_FILE

config = {
    'watchers': [
        {
            'class': LogFileWatcher,
            'name': 'test',
            'source': CRON_LOG_FILE,
            'notifiers': SlackNotifier(
                name='slack_cron',
                webhook_url='https://hooks.slack.com/services/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'
            )
        }
    ]
}