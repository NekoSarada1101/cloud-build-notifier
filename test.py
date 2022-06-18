from datetime import datetime, timedelta

# dt = datetime(2022,2,13,14,23,24)
# dt = dt + timedelta(hours=9)
# print(dt)

dt = '2022-02-13T14:23:24.339402919Z'
dt = dt[:dt.find('.')]

dt = datetime.strptime(dt, '%Y-%m-%dT%H:%M:%S') + timedelta(hours=9)
print(str(dt))

from settings import SLACK_INCOMING_WEBHOOK_URL
from slack_sdk.webhook import WebhookClient

client = WebhookClient(SLACK_INCOMING_WEBHOOK_URL)

response = client.send(text='test')
print(response)
