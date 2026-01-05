import base64
import os
from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Initialize Speech-to-Text V2 client
speech_client = SpeechClient()

# Get project ID from environment or settings
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", settings.gcp_project_id)

async def transcribe_audio(
    audio_base64: str,
    language_code: str = "en-US",  # Changed from en-KE - V2 API has stricter language support
    sample_rate: int = 48000
) -> str:
    """
    Transcribe base64-encoded audio using Google Cloud Speech-to-Text V2 API.
    Uses auto-detection for audio format - much more reliable!
    
    Args:
        audio_base64: Base64-encoded audio data (without data: prefix)
        language_code: Language code (en-US, en-GB supported by V2 API)
        sample_rate: Audio sample rate in Hz (default 48000)
    
    Returns:
        Transcribed text or empty string if no speech detected
    """
    try:
        # Decode base64 to bytes
        audio_bytes = base64.b64decode(audio_base64)
        
        logger.info(f"📊 Audio chunk: {len(audio_bytes)} bytes")
        
        # Log first few bytes for debugging
        if len(audio_bytes) >= 8:
            header = audio_bytes[:8].hex()
            logger.info(f"🔍 Audio header (first 8 bytes): {header}")
        
        # V2 API: Use AutoDetectDecodingConfig for automatic format detection
        config = cloud_speech.RecognitionConfig(
            auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),
            language_codes=["en-US"],  # Use en-US for better V2 API compatibility
            model="long",  # Changed to "long" - more flexible, works with short audio too
            features=cloud_speech.RecognitionFeatures(
                enable_automatic_punctuation=True,
            ),
        )
        
        # Create recognize request
        request = cloud_speech.RecognizeRequest(
            recognizer=f"projects/{PROJECT_ID}/locations/global/recognizers/_",
            config=config,
            content=audio_bytes,
        )
        
        logger.info(f"🎤 Sending to Speech-to-Text V2 API (auto-detect, en-US, long model)...")
        
        # Transcribe the audio
        response = speech_client.recognize(request=request)
        
        # Extract transcripts
        transcripts = []
        for i, result in enumerate(response.results):
            if result.alternatives:
                transcript_text = result.alternatives[0].transcript
                confidence = result.alternatives[0].confidence
                logger.info(f"  ✅ Result {i}: '{transcript_text}' (confidence: {confidence:.2%})")
                transcripts.append(transcript_text)
        
        transcript = " ".join(transcripts).strip()
        
        if transcript:
            logger.info(f"🎯 Transcription successful: {transcript}")
            return transcript
        else:
            logger.warning("⚠️  No speech detected in audio chunk")
            return ""
        
    except base64.binascii.Error as e:
        logger.error(f"❌ Base64 decode error: {str(e)}")
        raise ValueError(f"Invalid base64 audio data: {str(e)}")
    except Exception as e:
        logger.error(f"❌ Transcription error: {str(e)}", exc_info=True)
        raise
