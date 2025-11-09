from google import genai
import logging
import time
from pathlib import Path
from typing import Dict, Any

from app.config import GOOGLE_AI_STUDIO_API_KEY, GEMINI_MODEL, PROMPTS_DIR
from app.models import FeedbackResponse

logger = logging.getLogger(__name__)

class SpeechAnalyzer:
    """Analyzes speech videos using Gemini and the general_prompt.txt schema."""
    
    def __init__(self):
        self.client = genai.Client(api_key=GOOGLE_AI_STUDIO_API_KEY)
        self.system_prompt = self._load_prompt()
    
    def _load_prompt(self) -> str:
        """Load the general analysis prompt."""
        prompt_path = PROMPTS_DIR / "general_prompt.txt"
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
        return prompt_path.read_text(encoding="utf-8")
    
    def _wait_for_file_active(self, file, timeout: int = 120) -> None:
        """
        Wait for uploaded file to become ACTIVE.
        
        Args:
            file: The uploaded file object
            timeout: Maximum seconds to wait (default 120)
            
        Raises:
            TimeoutError: If file doesn't become active within timeout
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            file_status = self.client.files.get(name=file.name)
            if file_status.state == "ACTIVE":
                logger.info(f"File {file.name} is now ACTIVE")
                return
            elif file_status.state == "FAILED":
                raise RuntimeError(f"File {file.name} processing FAILED")
            
            logger.info(f"File {file.name} state: {file_status.state}, waiting...")
            time.sleep(2)
        
        raise TimeoutError(f"File {file.name} did not become ACTIVE within {timeout} seconds")
    
    async def analyze_video(self, video_path: str, audio_path: str = None) -> Dict[str, Any]:
        """
        Analyze a video file and return structured feedback using Gemini's structured outputs.
        
        Args:
            video_path: Path to the video file
            audio_path: Optional path to separate audio file
            
        Returns:
            Dictionary matching the FeedbackResponse Pydantic model schema
        """
        video_file = None
        audio_file = None
        
        try:
            logger.info(f"Starting analysis for video: {video_path}")
            
            # Determine mime type for video
            import mimetypes
            video_mime_type = mimetypes.guess_type(video_path)[0] or 'video/mp4'
            
            # Upload video file - open and read the file
            with open(video_path, 'rb') as f:
                video_file = self.client.files.upload(file=f, config={'mime_type': video_mime_type})
            logger.info(f"Uploaded video: {video_file.name}, state: {video_file.state}")
            
            # Wait for file to be processed
            self._wait_for_file_active(video_file)
            
            # Prepare content parts - include the prompt and video
            content_parts = [self.system_prompt]
            
            # If separate audio provided, upload and include it
            if audio_path:
                audio_mime_type = mimetypes.guess_type(audio_path)[0] or 'audio/mpeg'
                with open(audio_path, 'rb') as f:
                    audio_file = self.client.files.upload(file=f, config={'mime_type': audio_mime_type})
                logger.info(f"Uploaded audio: {audio_file.name}, state: {audio_file.state}")
                self._wait_for_file_active(audio_file)
            
            # Generate analysis with structured output
            logger.info("Generating analysis with Gemini using structured outputs...")
            response = self.client.models.generate_content(
                model=GEMINI_MODEL,
                contents=[
                    {
                        "role": "user",
                        "parts": [
                            {"text": self.system_prompt},
                            {"file_data": {"file_uri": video_file.uri}},
                            *([{"file_data": {"file_uri": audio_file.uri}}] if audio_file else [])
                        ]
                    }
                ],
                config={
                    "response_mime_type": "application/json",
                    "response_json_schema": FeedbackResponse.model_json_schema(),
                    "temperature": 0.4,
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 8192,
                }
            )
            
            # Validate and parse the response using Pydantic
            feedback = FeedbackResponse.model_validate_json(response.text)
            logger.info("Successfully validated feedback with Pydantic model")
            
            # Return as dictionary
            return feedback.model_dump()
            
        except TimeoutError as e:
            logger.error(f"File processing timeout: {e}")
            raise RuntimeError(f"Video processing timed out. Please try with a smaller video or try again later.")
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            raise
        finally:
            # Clean up uploaded files from Gemini's storage
            try:
                if video_file:
                    self.client.files.delete(name=video_file.name)
                    logger.info(f"Deleted video file: {video_file.name}")
                if audio_file:
                    self.client.files.delete(name=audio_file.name)
                    logger.info(f"Deleted audio file: {audio_file.name}")
            except Exception as cleanup_error:
                logger.warning(f"Failed to cleanup files: {cleanup_error}")
