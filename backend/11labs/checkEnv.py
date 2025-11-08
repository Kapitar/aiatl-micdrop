import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from root speech-coach folder
root_dir = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=root_dir / ".env")

print(f"Python version: {os.sys.version}")
print(f"Platform: {os.sys.platform}")

elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
google_key = os.getenv("GOOGLE_AI_STUDIO_API_KEY")

print("ELEVENLABS_API_KEY loaded:", bool(elevenlabs_key))
print("GOOGLE_AI_STUDIO_API_KEY loaded:", bool(google_key))