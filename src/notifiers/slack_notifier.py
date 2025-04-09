import requests
import logging

from ..classes.notifier import Notifier
from ..classes.entry import Entry, EntryStatus
import json

class SlackNotifier(Notifier):
    def __init__(self, name: str, webhook_url: str):
        super().__init__(name)
        self.webhook_url = webhook_url

    def send(self, entries: list[Entry]):
        # Check if there are any entries to send
        if not entries or len(entries) == 0:
            logging.debug("No entries to send to Slack.")
            return
        
        # Create the payload for the Slack message
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
                                        "bold": True
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
                        "text": f"{len(entries)} new tasks ran since last time."
                    }
                }                
            ]
        }
        
        # Iterate over the entries and add them to the payload as "overflow" blocks
        for entry in entries:
            # Display key information about the entry
            payload["blocks"].append(
                {
                    "type": "divider"
                }
            )
            payload["blocks"].append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": ":white_check_mark:" if entry.status == EntryStatus.SUCCESS else ":x:" + f"*{entry.title}*"
                    }
                }
            )

            # If the entry was not successful, add the content as a context block
            if entry.status == EntryStatus.FAILURE:
                payload["blocks"].append(
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "plain_text",
                                "text": f"Error: {"\n".join(entry.content)}",
                                "emoji": True
                            }
                        ]
                    }
                )
        
        # Send the payload to the Slack webhook URL
        logging.info(f"Sending {len(entries)} entries to Slack")
        logging.debug(f"Payload: {json.dumps(payload)}")
        response = requests.post(
            self.webhook_url, 
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"}
        )

        # Check the response from Slack
        if response.status_code != 200:
            logging.error(f"Failed to send notification: {response.status_code}, {response.text}")
            logging.error(f"Webhook URL: {self.webhook_url}")
        else:
            logging.info(f"Notification sent successfully to Slack: {response.status_code}")