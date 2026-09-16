import os
from dotenv import load_dotenv
load_dotenv()

from instagram.message.message_factory import MessageFactory
from instagram.message.message_type import MessageType

import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M"
)

logger = logging.getLogger(__name__)

# Your app → DEBUG
logger.setLevel(logging.DEBUG)

# Third-party libraries → WARNING
for name in ["httpcore", "httpcore2", "httpx", "openai"]:
    logging.getLogger(name).setLevel(logging.WARNING)

from fastapi import FastAPI, status, Query
from fastapi.responses import PlainTextResponse

from schemas.webhook import InstagramWebhookRequestPayload
from ai.agent import generate_reply

from instagram.instagram_account_factory import InstagramAccountFactory
from instagram.instagram_accounts import InstagramAccounts

from instagram.message.message_factory import MessageFactory
from instagram.message.message import Message
from instagram.message.messages.text import TextMessage
from instagram.message.messages.attachment import AttachmentMessage
from instagram.message.messages.attachment_type import AttachmentType

app = FastAPI()

maven_ai_ig = InstagramAccountFactory.create(InstagramAccounts.MAVEN_AI)
personal_ig = InstagramAccountFactory.create(InstagramAccounts.PERSONAL)

def get_account_name(account_id):
    match account_id:
        case maven_ai_ig.id:
            return maven_ai_ig.name
        case personal_ig.id:
            return personal_ig.name
        case _:
            return "Unknown"
     
def get_reciever_name(user_id: str, account_id: str) -> str:
    return get_account_name(account_id) if user_id == account_id else user_id

default_response = {
    "status": "ok"
}

@app.get('/')
def root():
    return "Hello from Instagram Automation server."

@app.get('/webhook/instagram', response_class=PlainTextResponse)
def verify_webhook(
    hub_mode: str = Query(alias="hub.mode"),
    hub_verify_token: str = Query(alias="hub.verify_token"),
    hub_challenge: str = Query(alias="hub.challenge")
):
    if hub_mode == "subscribe" and hub_verify_token == os.getenv('WEBHOOK_VERIFY_TOKEN'):
        return hub_challenge
    
    return PlainTextResponse(
        "Verification failed.",
        status_code=status.HTTP_403_FORBIDDEN
    )
    
@app.post("/webhook/instagram")
def instagram_webhook(
    payload: InstagramWebhookRequestPayload
):
    print(payload.entry[0])
    # return default_response
    entry = payload.entry[0]
    
    # webhook receiver account id
    account_id = str(entry.get("id"))
    account_name = get_account_name(account_id)
    
    message: Message = MessageFactory.create(entry)

    # when echoed, the webhook receiver id will be same as the sender id
    if message.is_echo:
        logger.info("ECHOED: Ignoring echoed message on %s: %s", account_name, message)
        # explicit condition on (sender id, account name), just for extra confidence
        logger.info("Sender ID: %s -> Recipient ID: %s", get_reciever_name(message.sender_id, account_id), message.recipient_id)
        return default_response
    
    # NOTE: for different accounts, different sender id's exist.
    # so instead of checking on sender_id directly, we check on reciever_id
    # for any reciever, its id will be constant, as it is its own context
    
    logger.info(f"Message received for {account_name} Instagram account.")
    # when the webhook receiver id is of MavenAI account, in my context I can be sure of receiver, which will be MavenAI
    if account_id == maven_ai_ig.id:
        # explicit condition on (recipient_id, account name), just for extra confidence
        logger.info("Sender ID: %s -> Recipient ID: %s", message.sender_id, get_reciever_name(message.recipient_id, account_id))
        # maven_ai_ig.send_message(sender_id, "HELLO!")
        if message.is_old_message():
            logger.info("Ignoring old message on %s: %s", account_name, message)
        else:
            if isinstance(message, TextMessage):
                content = message.get_agent_message()
                reply = generate_reply(message.sender_id, content)
                logger.info("Generated reply: %s", reply) 
                maven_ai_ig.send_message(message.sender_id, reply)
            elif isinstance(message, AttachmentMessage):
                for attachment in message.attachments:
                    if attachment["type"] == AttachmentType.IMAGE.value:
                        content = message.get_agent_message(message.attachments.index(attachment))
                        reply = generate_reply(message.sender_id, content)
                        logger.info("Generated reply after analyzing image: %s", reply)
                        maven_ai_ig.send_message(message.sender_id, reply)
                    else:
                        logger.warning("Unsupported attachment type received on %s: %s", account_name, attachment["type"])
            else:
                logger.warning("Unsupported message type received on %s: %s", account_name, message)

                    
                
            
    
    # NOTE: disabling personal account for now, as it is not needed in my context. If needed, can be enabled later.
            
    # when the webhook receiver id is of Personal account, in my context I can be sure of receiver, which will be Personal
    # elif account_id == personal_ig.id:
    #     logger.info("Message received for Personal Instagram account.")
    #     logger.info("Sender ID: %s -> Recipient ID: %s", message.sender_id, get_reciever_name(message.recipient_id, account_id))
    #     personal_ig.send_message(sender_id, "HI!")
    
    return default_response