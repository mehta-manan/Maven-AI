import json
import os
from abc import ABC

import logging
logger = logging.getLogger(__name__)

from utils import http_client

class InstagramAccount(ABC):
    def __init__(self, id, auth_token) -> None:
        self.id = id
        self._auth_token = auth_token
        self._instagram_message_url = os.getenv('INSTAGRAM_MESSAGES_URL')
        
    def send_message(self, recipient_id: str, message: str):
        data = {
                "recipient": {
                    "id": recipient_id
                },
                "message": {
                    "text": message
                }
            }
            
        headers = {
            "Authorization": f"Bearer {self._auth_token}",
            "Content-Type": "application/json"
        }
        
        from urllib.error import HTTPError
        try:
            http_client.fetch(
                self._instagram_message_url,
                'POST',
                None,
                json.dumps(data).encode('utf-8'),
                headers
                )
    
        except HTTPError as e:
            response = e.read().decode("utf-8")
            logger.error("HTTP Error: %s", e.code)
            logger.error("Response: %s", response)