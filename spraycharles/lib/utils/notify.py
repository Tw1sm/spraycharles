from enum import Enum
import pymsteams
from discord_webhook import DiscordWebhook
import requests


class HookSvc(str, Enum):
    SLACK   = "Slack"
    TEAMS   = "Teams"
    DISCORD = "Discord"


def slack(webhook, host):
    payload = {
        "text": f"Credentials guessed for host: {host}"
    }
    response = requests.post(webhook, json=payload)
    response.raise_for_status()  # Raises an error for bad responses


def teams(webhook, host):
    notify = pymsteams.connectorcard(webhook)
    notify.text(f"Credentials guessed for host: {host}")
    notify.send()


def discord(webhook, host):
    notify = DiscordWebhook(
        url=webhook, content=f"Credentials guessed for host: {host}"
    )
    response = webhook.execute()
