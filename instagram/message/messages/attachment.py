import logging
logger = logging.getLogger(__name__)

from instagram.message.message import Message
from instagram.message.message_type import MessageType
from instagram.message.messages.attachment_type import AttachmentType
from ai.stt_agent import transcribe_audio
from utils.attachment import get_image, image_to_data_url, get_audio

class AttachmentMessage(Message):
    def __init__(self, entry) -> None:
        super().__init__(entry)
        self.attachments = self._message[MessageType.ATTACHMENTS.value]
    
    def get_agent_message(self, index=0, attachment_type=None):
        if attachment_type == AttachmentType.IMAGE.value:
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
        elif attachment_type == AttachmentType.AUDIO.value:
            audio_bytes = get_audio(self.attachments[index]["payload"]["url"])
            transcript = transcribe_audio(audio_bytes)
            
            logger.info("Transcribed audio to text: %s", transcript)
            
            return {
                "role": "user",
                "content": transcript
            }   
        else:
            return None  