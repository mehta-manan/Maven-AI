from instagram.message.message_type import MessageType
from instagram.message.messages.attachment_type import AttachmentType

def get_content(user_input, type):
    return _load_template(user_input, type)

def _load_template(user_input, type):
    match type:
        case MessageType.TEXT:
            return _get_agent_text_message(user_input)
        case AttachmentType.IMAGE:
            return _get_agent_image_message(user_input)
        case _:
            raise ValueError(f"Unsupported message type: {type}")
        
def _get_agent_text_message(text_message):
    return {
        "role": "user",
        "content": text_message
    }
    
def _get_agent_image_message(image_message):
    return {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "The user sent you this image. Respond naturally based on it."
            },
            {
                "type": "image_url",
                "image_url": image_message
            }
        ]
    }