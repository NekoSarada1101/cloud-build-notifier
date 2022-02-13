import base64
import json
import requests
from email.mime import base
from settings import SLACK_INCOMING_WEBHOOK_URL


def cloud_build_notifier(event, context):
    build_message = base64.b64decode(event['data']).decode('utf-8')
    build = json.loads(build_message)

    color = {
        "SUCCESS": "#28a745",
        "FAILURE": "#cb2431"
    }

    data = {
        "attachments": [
            {
                "color": color[build.status],
                "blocks": [
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": "*status:*\n{}".format(build.status)
                            },
                            {
                                "type": "mrkdwn",
                                "text": "*id:*\n{}".format(build.id)
                            },
                            {
                                "type": "mrkdwn",
                                "text": "*start:*\n{}".format(build.startTime)
                            },
                            {
                                "type": "mrkdwn",
                                "text": "*finish:*\n{}".format(build.finishTime)
                            },
                        ]
                    },
                    {
                        "type": "actions",
                        "elements": [
                                {
                                    "type": "button",
                                    "text": {
                                            "type": "plain_text",
                                        "text": "View log"
                                    },
                                    "style": "primary",
                                    "url": build.logUrl,
                                },
                        ]
                    }
                ]
            }
        ]
    }
    json_data = json.dumps(data).encode("utf-8")
    response = requests.post(SLACK_INCOMING_WEBHOOK_URL, json_data)
    print(response)
    print(response.text)


if __name__ == '__main__':
    cloud_build_notifier('event', 'context')
