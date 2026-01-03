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
    Uses multiple encoding attempts for better compatibility.
    
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
        
        # Log first few bytes to debug format
        if len(audio_bytes) > 4:
            header = audio_bytes[:4].hex()
            logger.info(f"Audio header (first 4 bytes): {header}")
        
        # Try multiple encoding configurations
        configs_to_try = [
            {
                "name": "OGG_OPUS (primary)",
                "encoding": speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
                "sample_rate": None,  # Auto-detect
            },
            {
                "name": "WEBM_OPUS (48kHz)",
                "encoding": speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
                "sample_rate": 48000,
            },
            {
                "name": "WEBM_OPUS (auto-detect)",
                "encoding": speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
                "sample_rate": None,
            },
        ]
        
        audio = speech.RecognitionAudio(content=audio_bytes)
        last_error = None
        
        for config_info in configs_to_try:
            try:
                logger.info(f"Trying {config_info['name']}...")
                
                config_params = {
                    "encoding": config_info["encoding"],
                    "language_code": language_code,
                    "enable_automatic_punctuation": True,
                    "model": "default",
                }
                
                if config_info["sample_rate"] is not None:
                    config_params["sample_rate_hertz"] = config_info["sample_rate"]
                
                config = speech.RecognitionConfig(**config_params)
                
                # Perform synchronous recognition
                response = speech_client.recognize(config=config, audio=audio)
                
                # Log response details
                logger.info(f"Speech API returned {len(response.results)} results with {config_info['name']}")
                
                # Extract transcript
                transcripts = []
                for i, result in enumerate(response.results):
                    if result.alternatives:
                        transcript_text = result.alternatives[0].transcript
                        confidence = result.alternatives[0].confidence if hasattr(result.alternatives[0], 'confidence') else 'N/A'
                        logger.info(f"  Result {i}: '{transcript_text}' (confidence: {confidence})")
                        transcripts.append(transcript_text)
                
                transcript = " ".join(transcripts).strip()
                
                if transcript:
                    logger.info(f"✅ Transcription successful with {config_info['name']}: {transcript}")
                    return transcript
                else:
                    # No speech detected with this config, try next
                    logger.warning(f"No speech detected with {config_info['name']}, trying next config...")
                    continue
                    
            except Exception as e:
                last_error = e
                logger.warning(f"Config {config_info['name']} failed: {str(e)}")
                continue
        
        # All configs failed
        if last_error:
            logger.warning(f"All encoding configs failed. Last error: {str(last_error)}")
        else:
            logger.warning("⚠️ No speech detected in audio chunk - API returned empty results for all configs")
        
        return ""
        
    except base64.binascii.Error as e:
        logger.error(f"Base64 decode error: {str(e)}")
        raise ValueError(f"Invalid base64 audio data: {str(e)}")
    except Exception as e:
        logger.error(f"Transcription error: {str(e)}")
        raise
