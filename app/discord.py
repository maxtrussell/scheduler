import requests
from discord import Webhook, RequestsWebhookAdapter

def message(content):
    webhook = Webhook.from_url(Config.DISCORD_WEBHOOK, adapter=RequestsWebhookAdapter())
    webhook.send(content, username=Config.DISCORD_USERNAME)
