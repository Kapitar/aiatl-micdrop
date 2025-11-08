import os
from google.generativeai import Client

client = Client(api_key=os.getenv("GOOGLE_AI_STUDIO_API_KEY"))

def improve_transcript(transcript: str) -> dict:
    if not transcript.strip():
        return {"optimized_transcript": "", "explanation": "Empty transcript."}
    try:
        response = client.generate_text(
            model="text-bison-001",
            prompt=f"Improve this transcript for clarity and readability:\n{transcript}"
        )
        return {"optimized_transcript": response.text, "explanation": "Success"}
    except Exception as e:
        return {"optimized_transcript": transcript, "explanation": str(e)}