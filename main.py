import base64
import json
from tracemalloc import start
import requests
from datetime import datetime, timedelta
from settings import SLACK_INCOMING_WEBHOOK_URL


def cloud_build_notifier(event, context):
    build_message = base64.b64decode(event['data']).decode('utf-8')
    build = json.loads(build_message)
    print(build)

    if build['status'] == 'WORKING':
        return

    color = {
        "SUCCESS": "#28a745",
        "FAILURE": "#cb2431"
    }

    start_time = datetime.strptime(build['startTime'][:build['startTime'].find('.')], '%Y-%m-%dT%H:%M:%S') + timedelta(hours=9)
    finish_time = datetime.strptime(build['finishTime'][:build['finishTime'].find('.')], '%Y-%m-%dT%H:%M:%S') + timedelta(hours=9)

    data = {
        "attachments": [
            {
                "color": color[build['status']],
                "blocks": [
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": "*Status:*\n{}".format(build['status'])
                            },
                            {
                                "type": "mrkdwn",
                                "text": "*Start:*\n{}".format(str(start_time))
                            },
                            {
                                "type": "mrkdwn",
                                "text": "*Trigger Name:*\n{}".format(build['substitutions']['TRIGGER_NAME'])
                            },
                            {
                                "type": "mrkdwn",
                                "text": "*Finish:*\n{}".format(str(finish_time))
                            },
                            {
                                "type": "mrkdwn",
                                "text": "*ID:*\n{}".format(build['id'])
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
                                "url": build['logUrl'],
                            },
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "View repo"
                                },
                                "style": "default",
                                "url": "https://github.com/NekoSarada1101/{}".format(build['substitutions']['REPO_NAME']),
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
