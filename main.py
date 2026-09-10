from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()

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
from utils.message import is_echo, get_sender_id, get_recipient_id, get_message, get_message_time
from ai.agent import generate_reply

from instagram.instagram_account_factory import InstagramAccountFactory
from instagram.instagram_accounts import InstagramAccounts

from constants.messages import MESSAGE

app = FastAPI()

maven_ai_ig = InstagramAccountFactory.create(InstagramAccounts.MAVEN_AI)
personal_ig = InstagramAccountFactory.create(InstagramAccounts.PERSONAL)

subscribers = set()

def get_account_name(account_id):
    match account_id:
        case maven_ai_ig.id:
            return InstagramAccounts.MAVEN_AI.value
        case personal_ig.id:
            return InstagramAccounts.PERSONAL.value
        case _:
            return "Unknown"

def is_old_message(entry: dict) -> bool:
    message_time = get_message_time(entry) / 1000
    current_time = datetime.now().timestamp()
    time_difference = current_time - message_time
    return time_difference > 10

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
    entry = payload.entry[0]
    
    # webhook receiver account id
    account_id = str(entry.get("id"))
    account_name = get_account_name(account_id)
    
    message = get_message(entry)
    logger.info("Received message: %s", message)
    
    if not message:
        logger.info("No message found in entry: %s", entry)
        return default_response
    
    sender_id = get_sender_id(entry)
    recipient_id = get_recipient_id(entry)
    
    # when echoed, the webhook receiver id will be same as the sender id
    if is_echo(entry):
        logger.info("ECHOED: Ignoring echoed message on %s: %s", account_name, message)
        # explicit condition on (sender id, account name), just for extra confidence
        logger.info("Sender ID: %s -> Recipient ID: %s", get_reciever_name(sender_id, account_id), recipient_id)
        return default_response
    
    # NOTE: for different accounts, different sender id's exist.
    # so instead of checking on sender_id directly, we check on reciever_id
    # for any reciever, its id will be constant, as it is its own context
    
    # when the webhook receiver id is of MavenAI account, in my context I can be sure of receiver, which will be MavenAI
    if account_id == maven_ai_ig.id:
        logger.info("Message received for MavenAI Instagram account.")
        # explicit condition on (recipient_id, account name), just for extra confidence
        logger.info("Sender ID: %s -> Recipient ID: %s", sender_id, get_reciever_name(sender_id, recipient_id))
        # maven_ai_ig.send_message(sender_id, "HELLO!")
        if not is_old_message(entry):
            reply = generate_reply(sender_id, message)
            logger.info("Generated reply: %s", reply) 
            maven_ai_ig.send_message(sender_id, reply)
            
    # when the webhook receiver id is of Personal account, in my context I can be sure of receiver, which will be Personal
    elif account_id == personal_ig.id:
        logger.info("Message received for Personal Instagram account.")
        logger.info("Sender ID: %s -> Recipient ID: %s", sender_id, get_reciever_name(sender_id, recipient_id))
        # personal_ig.send_message(sender_id, "HI!")
    
    # logger.info(
    # "entry_id=%s sender=%s recipient=%s is_echo=%s",
    # entry.get("id"),
    # sender_id,
    # recipient_id,
    # is_echo(entry),
    # )
    
    
    
    
    
    
    # logger.info("Sender ID: %s -> Recipient ID: %s", sender_id, recipient_id)
     
    # if sender_id == maven_ai_ig.id:
    #     if recipient_id == personal_ig.id:
    #         maven_ai_ig.send_message(sender_id, "HELLO!")
    #     else:
    #         logger.info("Ignoring message from self even after not echoed: %s", message)
    #     return default_response
    
    # if sender_id == personal_ig.id:
    #     if recipient_id == maven_ai_ig.id:
    #         personal_ig.send_message(sender_id, "HELLO")
    #     else:
    #         logger.info("Ignoring message from self even after not echoed: %s", message)
    #     return default_response
    
    
    # if sender_id == maven_ai_ig.id:
    #     logger.info("Ignoring message from self even after not echoed: %s", message)
        
    # if recipient_id == maven_ai_ig.id:
    #     maven_ai_ig.send_message(sender_id, "HELLO!") 
        
        
    # elif recipient_id == personal_ig:
    #     personal_ig.send_message(sender_id, "HELLO")
        
    # if sender_id == os.getenv('MY_IG_ID'):
    #     logger.info("Ignoring message from self even after not echoed: %s", message)
    #     return default_response
    # message_time = get_message_time(entry) / 1000
    # current_time = datetime.now().timestamp()
    # time_difference = current_time - message_time
    
    # logger.info("Message time: %s, Current time: %s, Time difference: %s seconds", message_time, current_time, time_difference)
    # if not (current_time - message_time <= 10):
    #     logger.info("Ignoring old message: %s and asking again", message)
    #     return default_response
    
    # if message == "🔛":
    #     if sender_id in subscribers:
    #         respond(sender_id, MESSAGE["ALREADY_ACTIVE"])
    #     else:
    #         subscribers.add(sender_id)
    #         respond(sender_id, MESSAGE["GREET_HELLO"])
    #     return default_response
    # elif message == "📴":
    #     if sender_id in subscribers:
    #         subscribers.remove(sender_id)
    #         respond(sender_id, MESSAGE["GREET_BYE"])
    #     return default_response
    
    # if sender_id in subscribers:  
    #     reply = generate_reply(sender_id, message)
    #     logger.info("Generated reply: %s", reply) 
    #     respond(sender_id, reply)
    # else:
    #     logger.info("Ignoring message from non-subscriber: %s : %s", sender_id, message)

    return default_response