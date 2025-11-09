from google import genai
import uuid
import logging
from typing import Dict, Any

from app.config import GOOGLE_AI_STUDIO_API_KEY, GEMINI_MODEL

logger = logging.getLogger(__name__)

CHAT_SYSTEM_INSTRUCTION = """You are a helpful, precise assistant that answers questions about a user's speaking performance using ONLY the provided feedback_json. The feedback_json follows the schema with non_verbal (eye_contact, gestures, posture); delivery (clarity_enunciation, intonation, eloquence_filler_words + filler_word_counts); content (organization_flow, persuasiveness_impact, clarity_of_message); overall_feedback.

Primary goals:
- Ground every answer strictly in feedback_json. Do not invent metrics, timestamps, or observations.
- Be concise, actionable, and specific. Prefer short sentences or 3–6 bullets.
- When relevant, cite exact timestamp ranges from feedback_json (e.g., 00:45-01:05).
- If data is unavailable in feedback_json, say so briefly and suggest a next step.

Use of the JSON:
- Do not alter numeric values (effectiveness_score, filler_word_counts). Quote them exactly.
- Map user intent to the correct sub-categories: eye contact/gestures/posture → non_verbal; clarity/intonation/filler words → delivery; organization/persuasiveness/clarity of message → content.
- To explain a score, pair the effectiveness_score with 2–3 most relevant observations or timestamped_feedback details.
- If asked "how to improve," translate observations into concrete, practice-ready actions tied to timestamps.

Answer style:
- Output plain English (no JSON, no code fences).
- Structure: brief direct answer + actionable steps. Include timestamps when helpful.
- Keep to the scope. If asked about things outside feedback_json, respond briefly and refocus.

Refusal and transparency:
- If the user asks for info not present, say it isn't available in the feedback and avoid guessing.
- If asked to compare sessions but only one JSON is provided, ask for the other session's JSON.

Safety and tone:
- Be supportive and factual. No medical, psychological, or diagnostic claims.
- Avoid judgmental language; focus on behavior and improvement."""

class FeedbackChat:
    """Interactive chat for discussing speech feedback."""
    
    def __init__(self):
        self.client = genai.Client(api_key=GOOGLE_AI_STUDIO_API_KEY)
        # In-memory store for dev; use Redis/DB in production
        self.conversations: Dict[str, Dict[str, Any]] = {}
    
    def start_conversation(self, feedback_json: Dict[str, Any]) -> str:
        """
        Start a new conversation with the given feedback JSON.
        
        Args:
            feedback_json: The complete feedback from analysis
            
        Returns:
            conversation_id: Unique ID for this conversation
        """
        conversation_id = str(uuid.uuid4())
        
        # Store conversation with empty history
        self.conversations[conversation_id] = {
            "history": [],
            "feedback_json": feedback_json
        }
        
        logger.info(f"Started conversation {conversation_id}")
        return conversation_id
    
    async def send_message(self, conversation_id: str, user_message: str) -> str:
        """
        Send a message in an existing conversation.
        
        Args:
            conversation_id: The conversation ID
            user_message: The user's question
            
        Returns:
            The assistant's reply
        """
        if conversation_id not in self.conversations:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        conv = self.conversations[conversation_id]
        history = conv["history"]
        feedback_json = conv["feedback_json"]
        
        # Construct prompt with feedback context
        user_prompt = f"""feedback_json = {feedback_json}

user_message = {user_message}

Answer the user's question using only the feedback_json above."""
        
        try:
            # Build contents with system instruction and conversation history
            contents = []
            
            # Add system instruction as first user message if history is empty
            if not history:
                contents.append({
                    "role": "user",
                    "parts": [{"text": CHAT_SYSTEM_INSTRUCTION}]
                })
                contents.append({
                    "role": "model",
                    "parts": [{"text": "Understood. I will answer questions strictly based on the feedback_json provided."}]
                })
            
            # Add conversation history
            contents.extend(history)
            
            # Add current user message
            contents.append({
                "role": "user",
                "parts": [{"text": user_prompt}]
            })
            
            response = self.client.models.generate_content(
                model=GEMINI_MODEL,
                contents=contents,
                config={
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 2048,
                }
            )
            
            assistant_reply = response.text
            
            # Update conversation history
            history.append({
                "role": "user",
                "parts": [{"text": user_prompt}]
            })
            history.append({
                "role": "model",
                "parts": [{"text": assistant_reply}]
            })
            
            return assistant_reply
        except Exception as e:
            logger.error(f"Chat error: {e}")
            raise
