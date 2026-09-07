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
from utils.message import is_echo, get_sender_id, get_message, respond
from ai.agent import generate_reply

app = FastAPI()

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
    
    if is_echo(entry):
        return default_response
    
    message = get_message(entry)
    logger.info("Received message: %s", message)

    if not message:
        return default_response
    
    sender_id = get_sender_id(entry)
    logger.info("Sender ID: %s", sender_id)

    reply = generate_reply(sender_id, message)
    logger.info("Generated reply: %s", reply)
            
    respond(sender_id, reply)

    return default_response