import requests
from discord import Webhook, RequestsWebhookAdapter

from config import Config

def message(content):
    if Config.PROD_MODE:
        webhook = Webhook.from_url(Config.DISCORD_WEBHOOK, adapter=RequestsWebhookAdapter())
        webhook.send(content, username=Config.DISCORD_USERNAME)
    else:
        print(f"[Discord]: {content}")
