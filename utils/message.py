import logging
logger = logging.getLogger(__name__)

# property will not be present in the message if it is not an echo message
def is_echo(entry: dict) -> bool:
    return bool(entry.get("messaging") and entry["messaging"][0].get("message", {}).get("is_echo"))

# message will not be present in the entry if it is an attachment message (image, video, etc.)
def get_message(entry: dict) -> str:
    return str(entry.get("messaging") and entry["messaging"][0].get("message", {}).get("text"))

def get_message_time(entry: dict) -> int:
    return int(entry["messaging"][0]["timestamp"])

def get_sender_id(entry: dict) -> str:
    return entry["messaging"][0]["sender"]["id"]

def get_recipient_id(entry: dict) -> str:
    return entry["messaging"][0]["recipient"]["id"]
        