import logging
from typing import Optional, Dict, Any
from pathlib import Path
from elevenlabs import ElevenLabs, VoiceSettings
import google.generativeai as genai

from app.config import (
    ELEVENLABS_API_KEY, 
    ELEVENLABS_VOICE_SETTINGS,
    GOOGLE_AI_STUDIO_API_KEY,
    GEMINI_MODEL,
    GENERATION_CONFIG
)

logger = logging.getLogger(__name__)


class ElevenLabsService:
    """Service for ElevenLabs API operations: transcription, voice cloning, and TTS."""
    
    def __init__(self):
        self.client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        genai.configure(api_key=GOOGLE_AI_STUDIO_API_KEY)
        self.gemini_model = genai.GenerativeModel(GEMINI_MODEL)
        
    async def transcribe_audio(
        self, 
        audio_path: str,
        language_code: Optional[str] = None,
        diarize: bool = False,
        tag_audio_events: bool = False
    ) -> str:
        """
        Transcribe audio file to text using ElevenLabs.
        
        Args:
            audio_path: Path to the audio file
            language_code: Language code (e.g., 'eng', 'spa'). None for auto-detect
            diarize: Whether to annotate who is speaking
            tag_audio_events: Tag audio events like laughter, applause, etc.
            
        Returns:
            Transcribed text
        """
        try:
            logger.info(f"Transcribing audio: {audio_path} with language_code: {language_code}")
            
            # Normalize language code: convert empty string or "None" to actual None
            if language_code is not None and isinstance(language_code, str):
                stripped = language_code.strip()
                if stripped == "" or stripped.lower() == "none":
                    language_code = None
                else:
                    language_code = stripped
            
            with open(audio_path, 'rb') as audio_file:
                # Build parameters dict, excluding language_code if None
                params = {
                    "file": audio_file,
                    "model_id": "scribe_v1",
                    "diarize": diarize,
                    "tag_audio_events": tag_audio_events,
                }
                
                # Only include language_code if it's not None
                if language_code is not None:
                    params["language_code"] = language_code
                
                # Use ElevenLabs speech-to-text with correct parameters
                transcription = self.client.speech_to_text.convert(**params)
                
            logger.info(f"Transcription completed: {len(transcription.text)} characters")
            return transcription.text
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise RuntimeError(f"Transcription failed: {str(e)}")
    
    async def improve_speech_content(
        self, 
        transcription: str,
        improvement_focus: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Use Gemini to improve the content of a speech transcription.
        
        Args:
            transcription: The original transcribed text
            improvement_focus: Optional specific areas to focus on (e.g., "clarity", "persuasiveness")
            
        Returns:
            Dictionary with improved text and suggestions
        """
        try:
            logger.info("Improving speech content with Gemini")
            
            # Build the improvement prompt
            prompt = f"""You are a professional speech coach. Analyze and improve the following speech transcription.

Original Speech:
{transcription}

{f"Focus areas: {improvement_focus}" if improvement_focus else ""}

Please provide:
1. An improved version of the speech with better structure, clarity, and impact
2. Specific suggestions for improvement
3. Key changes made and why

Return your response in the following JSON format:
{{
    "improved_speech": "The improved version of the speech",
    "suggestions": [
        "Suggestion 1",
        "Suggestion 2",
        "Suggestion 3"
    ],
    "key_changes": [
        {{
            "change": "Description of change",
            "reason": "Why this change improves the speech"
        }}
    ],
    "summary": "Brief summary of the improvements made"
}}
"""
            
            response = self.gemini_model.generate_content(
                prompt,
                generation_config=GENERATION_CONFIG
            )
            
            # Parse the response
            import json
            raw_text = response.text.strip()
            
            # Remove markdown code fences if present
            if raw_text.startswith("```"):
                raw_text = raw_text.split("```")[1]
                if raw_text.startswith("json"):
                    raw_text = raw_text[4:]
                raw_text = raw_text.strip()
            
            improved_content = json.loads(raw_text)
            logger.info("Speech content improvement completed")
            
            return improved_content
            
        except Exception as e:
            logger.error(f"Speech improvement failed: {e}")
            raise RuntimeError(f"Speech improvement failed: {str(e)}")
    
    async def clone_voice_and_generate(
        self,
        audio_path: str,
        text: str,
        voice_name: str = "User Cloned Voice"
    ) -> bytes:
        """
        Clone a voice from an audio file and generate speech with the cloned voice.
        
        Args:
            audio_path: Path to the audio file to clone voice from
            text: Text to generate speech for
            voice_name: Name for the cloned voice
            
        Returns:
            Audio bytes of the generated speech
        """
        try:
            logger.info(f"Cloning voice from: {audio_path}")
            
            # Clone voice using IVC (Instant Voice Cloning)
            from io import BytesIO
            with open(audio_path, 'rb') as audio_file:
                audio_bytes = BytesIO(audio_file.read())
                voice = self.client.voices.ivc.create(
                    name=voice_name,
                    files=[audio_bytes],
                )
            
            logger.info(f"Voice cloned successfully with ID: {voice.voice_id}")
            
            # Generate speech with the cloned voice
            logger.info("Generating speech with cloned voice")
            audio_generator = self.client.text_to_speech.convert(
                voice_id=voice.voice_id,
                text=text,
                model_id="eleven_multilingual_v2",
                voice_settings=VoiceSettings(
                    stability=ELEVENLABS_VOICE_SETTINGS["stability"],
                    similarity_boost=ELEVENLABS_VOICE_SETTINGS["similarity_boost"],
                    style=ELEVENLABS_VOICE_SETTINGS["style"],
                    use_speaker_boost=ELEVENLABS_VOICE_SETTINGS["use_speaker_boost"]
                )
            )
            
            # Collect audio bytes
            generated_audio_bytes = b"".join(audio_generator)
            logger.info(f"Generated audio: {len(generated_audio_bytes)} bytes")
            
            # Clean up: delete the cloned voice
            try:
                self.client.voices.ivc.delete(voice.voice_id)
                logger.info(f"Cleaned up cloned voice: {voice.voice_id}")
            except Exception as e:
                logger.warning(f"Failed to cleanup cloned voice: {e}")
            
            return generated_audio_bytes
            
        except Exception as e:
            logger.error(f"Voice cloning failed: {e}")
            raise RuntimeError(f"Voice cloning failed: {str(e)}")
    
    async def full_speech_improvement_workflow(
        self,
        audio_path: str,
        improvement_focus: Optional[str] = None,
        language_code: Optional[str] = None,
        diarize: bool = False,
        tag_audio_events: bool = False
    ) -> Dict[str, Any]:
        """
        Complete workflow: transcribe -> improve -> clone voice -> generate improved speech.
        
        Args:
            audio_path: Path to the original audio file
            improvement_focus: Optional specific areas to focus on
            language_code: Language code (e.g., 'eng', 'spa'). None for auto-detect
            diarize: Whether to annotate who is speaking
            tag_audio_events: Tag audio events like laughter, applause, etc.
            
        Returns:
            Dictionary with transcription, improvements, and audio bytes
        """
        try:
            # Step 1: Transcribe with optional parameters
            transcription = await self.transcribe_audio(
                audio_path,
                language_code=language_code,
                diarize=diarize,
                tag_audio_events=tag_audio_events
            )
            
            # Step 2: Improve content
            improvements = await self.improve_speech_content(
                transcription,
                improvement_focus
            )
            
            # Step 3: Clone voice and generate improved speech
            improved_audio = await self.clone_voice_and_generate(
                audio_path,
                improvements["improved_speech"]
            )
            
            return {
                "original_transcription": transcription,
                "improved_content": improvements,
                "improved_audio_bytes": improved_audio,
                "audio_size": len(improved_audio)
            }
            
        except Exception as e:
            logger.error(f"Full workflow failed: {e}")
            raise RuntimeError(f"Full workflow failed: {str(e)}")
