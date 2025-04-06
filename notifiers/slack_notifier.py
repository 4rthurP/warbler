import requests

from ..classes.notifier import Notifier
from ..classes.entry import Entry

class SlackNotifier(Notifier):
    def __init__(self, name: str, webhook_url: str):
        super().__init__(name)
        self.webhook_url = webhook_url

    def send(self, entries: list[Entry]):
        for entry in entries:
            payload = {
                "text": f"New entry: {entry.title}\n{entry.url}"
            }
            response = requests.post(self.webhook_url, json=payload)
            if response.status_code != 200:
                print(f"Failed to send notification: {response.status_code}, {response.text}")