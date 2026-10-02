import os
from io import BytesIO
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

client = OpenAI()

def transcribe_audio(audio_bytes: bytes) -> str:
    audio_file = BytesIO(audio_bytes)
    audio_file.name = "audio.mp4"

    transcript = client.audio.transcriptions.create(
        model=str(os.getenv("TRANSCRIPTION_MODEL")),
        file=audio_file,
    )

    return transcript.text