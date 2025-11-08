import google.generativeai as genai

genai.api_key = None  # Will be set dynamically

def improve_transcript_with_structure(transcript, genre=None, purpose=None, audience=None, api_key=None):
    """Generate an improved version of the transcript while preserving structure."""
    try:
        if api_key:
            genai.api_key = api_key

        prompt = (
            f"Improve the following transcript for clarity, engagement, and readability.\n"
            f"Genre: {genre}\nPurpose: {purpose}\nAudience: {audience}\n"
            f"Transcript:\n{transcript}\n\n"
            "Return the improved transcript in plain text."
        )

        response = genai.chat(
            model="chat-bison-001",
            messages=[{"role": "user", "content": prompt}],
        )
        return {"optimized_transcript": response.last, "explanation": "Success"}
    except Exception as e:
        return {"optimized_transcript": transcript, "explanation": f"Error: {e}"}