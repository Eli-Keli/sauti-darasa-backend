import base64
from google.cloud import speech_v1 as speech
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Initialize Speech-to-Text client
speech_client = speech.SpeechClient()

async def transcribe_audio(
    audio_base64: str,
    language_code: str = "en-KE",
    sample_rate: int = 16000
) -> str:
    """
    Transcribe base64-encoded audio using Google Cloud Speech-to-Text.
    
    Args:
        audio_base64: Base64-encoded audio data (without data: prefix)
        language_code: Language code (en-KE for Kenyan English)
        sample_rate: Audio sample rate in Hz
    
    Returns:
        Transcribed text or empty string if no speech detected
    """
    try:
        # Decode base64 to bytes
        audio_bytes = base64.b64decode(audio_base64)
        
        logger.info(f"Audio chunk size: {len(audio_bytes)} bytes")
        
        # Configure recognition request
        audio = speech.RecognitionAudio(content=audio_bytes)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
            sample_rate_hertz=sample_rate,
            language_code=language_code,
            enable_automatic_punctuation=True,
            model="default",  # Options: 'default', 'video', 'phone_call', 'command_and_search'
            use_enhanced=True  # Use enhanced model for better accuracy
        )
        
        # Perform synchronous recognition
        response = speech_client.recognize(config=config, audio=audio)
        
        # Extract transcript
        transcripts = []
        for result in response.results:
            if result.alternatives:
                transcripts.append(result.alternatives[0].transcript)
        
        transcript = " ".join(transcripts).strip()
        
        if transcript:
            logger.info(f"Transcribed: {transcript}")
        else:
            logger.debug("No speech detected in audio chunk")
        
        return transcript
        
    except base64.binascii.Error as e:
        logger.error(f"Base64 decode error: {str(e)}")
        raise ValueError(f"Invalid base64 audio data: {str(e)}")
    except Exception as e:
        logger.error(f"Transcription error: {str(e)}")
        raise
