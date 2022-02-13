from operator import imod
from settings import SLACK_INCOMING_WEBHOOK_URL

def cloud_build_notifier(event, context):
    print(event)
    print(context)
