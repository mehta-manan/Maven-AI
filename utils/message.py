import os
import json
from utils import http_client

import logging
logger = logging.getLogger(__name__)

def is_echo(entry: dict) -> bool:
    return bool(entry.get("messaging") and entry["messaging"][0].get("message", {}).get("is_echo"))

def get_message(entry: dict) -> str:
    return str(entry.get("messaging") and entry["messaging"][0].get("message", {}).get("text"))

def get_sender_id(entry: dict) -> str:
    return entry["messaging"][0]["sender"]["id"]

def respond(recipient_id: str, reply: str):
    data = {
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": reply
        }
    }
    
    headers = {
        "Authorization": f"Bearer {os.getenv('AUTH_TOKEN')}",
        "Content-Type": "application/json"
    }
    
    from urllib.error import HTTPError
    try:
        http_client.fetch(
            os.getenv('INSTAGRAM_MESSAGES_URL'),
            'POST',
            None,
            json.dumps(data).encode('utf-8'),
            headers
            )

    except HTTPError as e:
        response = e.read().decode("utf-8")
        logger.error("HTTP Error: %s", e.code)
        logger.error("Response: %s", response)
        