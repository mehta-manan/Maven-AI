from instagram.message.message import Message
from instagram.message.message_type import MessageType
from utils.image import get_image, image_to_data_url

class AttachmentMessage(Message):
    def __init__(self, entry) -> None:
        super().__init__(entry)
        self.attachments = self._message[MessageType.ATTACHMENTS.value]
    
    def get_agent_message(self, index=0):
        image_bytes = get_image(self.attachments[index]["payload"]["url"])
        image_data_url = image_to_data_url(image_bytes)
        
        return {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "The user sent you this image. Respond naturally based on it."
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image_data_url
                    }
                }
            ]
        }