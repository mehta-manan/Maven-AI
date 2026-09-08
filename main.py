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
from utils.message import is_echo, get_sender_id, get_message, get_message_time
from ai.agent import generate_reply
from apis.instagram import respond
from constants.messages import MESSAGE

app = FastAPI()

subscribers = set()

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
    
    message = get_message(entry)
    logger.info("Received message: %s", message)
    
    if not message:
        return default_response
    
    if is_echo(entry):
        logger.info("Ignoring echoed message: %s", message)
        return default_response
    
    message_time = get_message_time(entry) / 1000
    current_time = datetime.now().timestamp()
    time_difference = current_time - message_time
    
    logger.info("Message time: %s, Current time: %s, Time difference: %s seconds", message_time, current_time, time_difference)
    
    if not (current_time - message_time <= 10):
        logger.info("Ignoring old message: %s", message)
        return default_response
    
    sender_id = get_sender_id(entry)
    logger.info("Sender ID: %s", sender_id)
    
    if sender_id == os.getenv('MY_IG_ID'):
        logger.info("Ignoring message from self even after not echoed: %s", message)
        return default_response

    if message == "🔛":
        if sender_id in subscribers:
            respond(sender_id, MESSAGE["ALREADY_ACTIVE"])
        else:
            subscribers.add(sender_id)
            respond(sender_id, MESSAGE["GREET_HELLO"])
        return default_response
    elif message == "📴":
        if sender_id in subscribers:
            subscribers.remove(sender_id)
            respond(sender_id, MESSAGE["GREET_BYE"])
        return default_response
    
    if sender_id in subscribers:  
        reply = generate_reply(sender_id, message)
        logger.info("Generated reply: %s", reply) 
        respond(sender_id, reply)
    else:
        logger.info("Ignoring message from non-subscriber: %s : %s", sender_id, message)

    return default_response