import os
from elevenlabs import set_api_key, transcribe

set_api_key(os.getenv("ELEVENLABS_API_KEY"))

def transcribe_audio(file_path: str) -> str:
    try:
        transcript = transcribe(file_path)
        print("Transcription successful.")
        return transcript
    except Exception as e:
        print("Transcription failed:", e)
        return ""