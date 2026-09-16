from abc import ABC

from instagram.message.message import Message
from instagram.message.message_type import MessageType
from instagram.message.messages.text import TextMessage
from instagram.message.messages.attachment import AttachmentMessage

class MessageFactory(ABC):
    @staticmethod
    def create(entry):
        message = Message(entry)

        match message.type:
            case MessageType.TEXT:
                return TextMessage(entry)

            case MessageType.ATTACHMENTS:
                return AttachmentMessage(entry)

            case _:
                raise ValueError(f"Unsupported message type: {message.type}")