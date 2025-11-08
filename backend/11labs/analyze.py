import os
from google.generativeai import Client

client = Client(api_key=os.getenv("GOOGLE_AI_STUDIO_API_KEY"))

def analyze_transcript(transcript: str) -> dict:
    if not transcript.strip():
        return {"matches": None, "explanation": "Empty transcript."}
    try:
        response = client.generate_text(
            model="text-bison-001",
            prompt=f"Analyze the following transcript and provide insights:\n{transcript}"
        )
        return {"matches": None, "analysis": response.text}
    except Exception as e:
        return {"matches": None, "explanation": str(e)}