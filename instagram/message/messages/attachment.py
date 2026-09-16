from instagram.message.message import Message
from instagram.message.message_type import MessageType

class AttachmentMessage(Message):
    def __init__(self, entry) -> None:
        super().__init__(entry)
        self.attachments = self._message[MessageType.ATTACHMENTS.value]
    
    def get_agent_message(self, index=0):
        return {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "The user sent you this image. Respond naturally based on it."
                },
                {
                    "type": "image_url",
                    "image_url": self.attachments[index]["payload"]["url"]
                }
            ]
        }