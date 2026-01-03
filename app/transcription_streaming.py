"""
Streaming transcription using Google Cloud Speech-to-Text
This handles real-time audio chunks properly
"""
import base64
import queue
import threading
from google.cloud import speech_v1 as speech
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Initialize Speech-to-Text client
speech_client = speech.SpeechClient()

def transcribe_audio_streaming(audio_base64: str, language_code: str = "en-KE") -> str:
    """
    Use streaming recognition for better chunk handling.
    Note: This is a simplified version - full streaming requires websockets.
    """
    try:
        audio_bytes = base64.b64decode(audio_base64)
        logger.info(f"Streaming audio chunk size: {len(audio_bytes)} bytes")
        
        # For now, use the synchronous method with proper config
        audio = speech.RecognitionAudio(content=audio_bytes)
        
        # Use LINEAR16 encoding which is more reliable for chunks
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
            sample_rate_hertz=48000,
            language_code=language_code,
            enable_automatic_punctuation=True,
            model="default",
        )
        
        response = speech_client.recognize(config=config, audio=audio)
        
        transcripts = []
        for result in response.results:
            if result.alternatives:
                transcripts.append(result.alternatives[0].transcript)
        
        return " ".join(transcripts).strip()
        
    except Exception as e:
        logger.error(f"Streaming transcription error: {str(e)}")
        return ""
