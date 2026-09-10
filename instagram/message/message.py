from datetime import datetime

from message.message_type import MessageType

import logging
logger = logging.getLogger(__name__)

class Message():
    def __init__(self, entry) -> None:
        self._message = self.extract_message(entry)
        
        # safe checking as property will not be present in the message if it is not an echo message
        self.is_echo = bool(self._message.get("is_echo"))
        
        self.sender_id = self.get_sender_id(entry)
        self.recipient_id = self.get_recipient_id(entry)
        
        self.message_time = self.get_message_time(entry)
        
        self.type = self.classify_message()
    
    @staticmethod
    def _get_messaging(entry: dict) -> dict:
        return entry["messaging"][0]
        
    @staticmethod
    def extract_message(entry: dict) -> dict:
        return Message._get_messaging(entry).get("message", {})
    
    def get_sender_id(self, entry: dict) -> str:
        return Message._get_messaging(entry)["sender"]["id"]

    def get_recipient_id(self, entry: dict) -> str:
        return Message._get_messaging(entry)["recipient"]["id"]

    def get_message_time(self, entry: dict) -> int:
        return int(Message._get_messaging(entry)["timestamp"] / 1000)
    
    def is_old_message(self) -> bool:
        current_time = datetime.now().timestamp()
        time_difference = current_time - self.message_time
        return time_difference > 120
    
    def classify_message(self):
        if self._message[MessageType.TEXT.value]:
            return MessageType.TEXT
        elif self._message[MessageType.ATTACHMENTS.value]:
            return MessageType.ATTACHMENTS
        else:
            return None, None        