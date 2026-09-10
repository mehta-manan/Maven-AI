from instagram.message.message import Message
from instagram.message.message_type import MessageType

class TextMessage(Message):
    def __init__(self, entry) -> None:
        super().__init__(entry)
        self.text = self._message[MessageType.TEXT.value]