import json
import os
from utils import http_client

import logging
logger = logging.getLogger(__name__)

from abc import ABC, abstractmethod
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
            
class PersonalInstagramAccount(InstagramAccount):
    def __init__(self) -> None:
        id = str(os.getenv('MY_IG_ID'))
        auth_token = str(os.getenv('PERSONAL_AUTH_TOKEN'))
        super().__init__(id, auth_token)
        
class MavenAIInstagramAccount(InstagramAccount):
    def __init__(self) -> None:
        id = str(os.getenv('MAVEN_AI_IG_ID'))
        auth_token = str(os.getenv('AI_AUTH_TOKEN'))
        super().__init__(id, auth_token)
        
from enum import Enum

class InstagramAccounts(Enum):
    MAVEN_AI = "MavenAI"
    PERSONAL = "Personal"
    
class InstagramAccountFactory(ABC):
    @staticmethod
    def create(account_type) -> InstagramAccount:
        match account_type:
            case InstagramAccounts.MAVEN_AI:
                return MavenAIInstagramAccount()
            case InstagramAccounts.PERSONAL:
                return PersonalInstagramAccount()
            case _:
                 raise ValueError(f"Unsupported account type: {account_type}")
            
maven_ai_ig = InstagramAccountFactory.create(InstagramAccounts.MAVEN_AI)
personal_ig = InstagramAccountFactory.create(InstagramAccounts.PERSONAL)