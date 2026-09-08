import json
import os
from utils import http_client

import logging
logger = logging.getLogger(__name__)

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