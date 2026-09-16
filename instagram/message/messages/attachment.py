from instagram.message.message import Message
from instagram.message.message_type import MessageType

class AttachmentMessage(Message):
    def __init__(self, entry) -> None:
        super().__init__(entry)
        self.attachments = self._message[MessageType.ATTACHMENTS.value]