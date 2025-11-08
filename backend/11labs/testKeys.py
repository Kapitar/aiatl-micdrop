import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from root
root_dir = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=root_dir / ".env")

# ElevenLabs
from elevenlabs import set_api_key, voices
elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
if elevenlabs_key:
    set_api_key(elevenlabs_key)
    try:
        print("ElevenLabs voices available:", [v.name for v in voices()])
    except Exception as e:
        print("ElevenLabs key error:", e)
else:
    print("ELEVENLABS_API_KEY not loaded.")

# Google AI Studio
from google.generativeai import Client
google_key = os.getenv("GOOGLE_AI_STUDIO_API_KEY")
if google_key:
    try:
        client = Client(api_key=google_key)
        resp = client.generate_text(model="text-bison-001", prompt="Hello world")
        print("Google AI Studio test success:", resp.text[:50])
    except Exception as e:
        print("Google AI Studio key error:", e)
else:
    print("GOOGLE_AI_STUDIO_API_KEY not loaded.")