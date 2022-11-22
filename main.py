import base64
import json
import logging
import os
import sys
from datetime import datetime, timedelta

from google.cloud import secretmanager
from slack_sdk import WebClient

# constant ============================================
secret_client = secretmanager.SecretManagerServiceClient()
SLACK_BOT_USER_TOKEN = secret_client.access_secret_version(request={'name': 'projects/slackbot-288310/secrets/SECRETARY_BOT_V2_SLACK_BOT_TOKEN/versions/latest'}).payload.data.decode('UTF-8')

client = WebClient(SLACK_BOT_USER_TOKEN)

CHANNEL_ID = os.environ.get('CHANNEL_ID')


# logger ===============================================
class JsonFormatter(logging.Formatter):
    def format(self, log):
        return json.dumps({
            'level': log.levelname,
            'message': log.getMessage(),
        })


formatter = JsonFormatter()
stream = logging.StreamHandler(stream=sys.stdout)
stream.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(stream)


# functions ==========================================
def cloud_build_notifier(event, context):
    logger.info('===== START cloud build notifier =====')
    logger.info('event={}'.format(event))

    build_message = base64.b64decode(event['data']).decode('utf-8')
    build = json.loads(build_message)
    logger.info('build_info={}'.format(build))

    exclude = ['WORKING', 'QUEUED', 'STATUS_UNKNOWN', 'PENDING', 'EXPIRED']
    if build['status'] in exclude:
        return

    color = None
    if build['status'] == 'SUCCESS':
        color = '#28a745'
    elif build['status'] == 'FAILURE':
        color = '#cb2431'
    else:
        color = '#cb6124'

    start_time = datetime.strptime(build['startTime'][:build['startTime'].find('.')], '%Y-%m-%dT%H:%M:%S') + timedelta(hours=9)
    finish_time = datetime.strptime(build['finishTime'][:build['finishTime'].find('.')], '%Y-%m-%dT%H:%M:%S') + timedelta(hours=9)

    data = None
    try:
        data = [
            {
                'color': color,
                'blocks': [
                    {
                        'type': 'section',
                        'fields': [
                                {
                                    'type': 'mrkdwn',
                                    'text': '*Status:*\n{}'.format(build['status'])
                                },
                            {
                                    'type': 'mrkdwn',
                                    'text': '*Start:*\n{}'.format(str(start_time))
                                    },
                            {
                                    'type': 'mrkdwn',
                                    'text': '*Trigger Name:*\n{}'.format(build['substitutions']['TRIGGER_NAME'])
                                    },
                            {
                                    'type': 'mrkdwn',
                                    'text': '*Finish:*\n{}'.format(str(finish_time))
                                    },
                            {
                                    'type': 'mrkdwn',
                                    'text': '*ID:*\n{}'.format(build['id'])
                                    },
                        ]
                    },
                    {
                        'type': 'actions',
                        'elements': [
                                {
                                    'type': 'button',
                                    'text': {
                                        'type': 'plain_text',
                                        'text': 'View log'
                                    },
                                    'style': 'primary',
                                    'url': build['logUrl']
                                },
                            {
                                    'type': 'button',
                                    'text': {
                                        'type': 'plain_text',
                                        'text': 'View repo'
                                    },
                                    'url': 'https://github.com/NekoSarada1101/{}'.format(build['substitutions']['REPO_NAME'])
                                    }
                        ]
                    }
                ]
            }
        ]

    except KeyError as e:
        logger.error(e)

    logger.info('data={}'.format(data))
    response = client.chat_postMessage(channel=CHANNEL_ID, attachments=data, username='Cloud Build Notifier', icon_emoji=':cloud_build:')
    logger.info('response={}'.format(response.text))
    logger.info('===== end cloud build notifier =====')


if __name__ == '__main__':
    cloud_build_notifier('event', 'context')
