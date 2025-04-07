import requests

from ..classes.notifier import Notifier
from ..classes.entry import Entry, EntryStatus

class SlackNotifier(Notifier):
    def __init__(self, name: str, webhook_url: str):
        super().__init__(name)
        self.webhook_url = webhook_url

    def send(self, entries: list[Entry]):
        payload = {
            "blocks": [
                {
                    "type": "rich_text",
                    "elements": [
                        {
                            "type": "rich_text_section",
                            "elements": [
                                {
                                    "type": "text",
                                    "text": "Warbler - Cron Tasks",
                                    "style": {
                                        "bold": "true"
                                    }
                                }
                            ]
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        f"text": f"{len(entries)} new tasks ran this last time."
                    }
                },
                {
                    "type": "divider"
                },
            ]
        }
        
        # Iterate over the entries and add them to the payload as "overflow" blocks
        for entry in entries:
            # Converts each line of the content to a separate option in the overflow menu
            overflow_options = []
            for i, content in enumerate(entry.content):
                overflow_options.append(
                    {
                        "text": {
                            "type": "plain_text",
                            "text": f"{content}",
                            "emoji": "true"
                        },
                        "value": f"value-{i}"
                    }
                )

            payload["blocks"].append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": ":white_check_mark:" if entry.status == EntryStatus.SUCCESS else ":x:" + f"*{entry.title}*"
                    },
                    "accessory": {
                        "type": "overflow",
                        "options": overflow_options,
                        "action_id": "overflow-action"
                    }
                }
            )

        # Send the payload to the Slack webhook URL
        response = requests.post(self.webhook_url, json=payload)
        if response.status_code != 200:
            print(f"Failed to send notification: {response.status_code}, {response.text}")