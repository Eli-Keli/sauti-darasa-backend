from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech
from google.api_core.client_options import ClientOptions
import asyncio
import json
import logging
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

REGION = "us"  # US region for guaranteed chirp_3 availability
PROJECT_ID = settings.gcp_project_id

class TranscriptionStream:
    def __init__(self, websocket: WebSocket, session_id: str):
        self.websocket = websocket
        self.session_id = session_id
        self.client = SpeechClient(
            client_options=ClientOptions(
                api_endpoint=f"{REGION}-speech.googleapis.com"
            )
        )
        self.audio_queue = asyncio.Queue()
        self.is_streaming = False
    
    async def start(self):
        """Start bidirectional streaming with Google Speech-to-Text V2"""
        self.is_streaming = True
        
        logger.info(f"🎙️  Starting streaming for session: {self.session_id}")
        
        # Create streaming config with chirp_3
        recognition_config = cloud_speech.RecognitionConfig(
            auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),
            language_codes=["en-US", "sw-KE"],  # English + Swahili Kenya
            model="chirp_3",
            features=cloud_speech.RecognitionFeatures(
                enable_automatic_punctuation=True,
                enable_word_time_offsets=True,
            ),
        )
        
        streaming_config = cloud_speech.StreamingRecognitionConfig(
            config=recognition_config,
            streaming_features=cloud_speech.StreamingRecognitionFeatures(
                interim_results=True  # Get word-by-word results
            ),
        )
        
        # Initial config request
        config_request = cloud_speech.StreamingRecognizeRequest(
            recognizer=f"projects/{PROJECT_ID}/locations/{REGION}/recognizers/_",
            streaming_config=streaming_config,
        )
        
        # Generator for audio requests
        async def audio_generator():
            yield config_request
            while self.is_streaming:
                try:
                    audio_data = await asyncio.wait_for(
                        self.audio_queue.get(), 
                        timeout=1.0
                    )
                    yield cloud_speech.StreamingRecognizeRequest(audio=audio_data)
                except asyncio.TimeoutError:
                    continue
        
        try:
            # Start gRPC streaming
            responses = self.client.streaming_recognize(
                requests=audio_generator()
            )
            
            # Process responses and send back via WebSocket
            for response in responses:
                for result in response.results:
                    transcript = result.alternatives[0].transcript
                    is_final = result.is_final
                    confidence = result.alternatives[0].confidence if is_final else 0.0
                    
                    logger.info(f"{'✅' if is_final else '⏳'} {transcript} (confidence: {confidence:.2%})")
                    
                    await self.websocket.send_json({
                        "type": "transcription",
                        "transcript": transcript,
                        "isFinal": is_final,
                        "confidence": confidence,
                        "sessionId": self.session_id,
                    })
                    
                    # Publish final transcripts to Firebase Realtime DB
                    if is_final and transcript.strip():
                        try:
                            from app.firebase_client import publish_caption
                            await publish_caption(self.session_id, transcript)
                            logger.info(f"✅ Published to Firebase: {transcript[:50]}...")
                        except Exception as fb_error:
                            logger.error(f"❌ Firebase publish failed: {str(fb_error)}")
                            # Don't fail the whole stream if Firebase fails
        except Exception as e:
            logger.error(f"❌ Streaming error: {str(e)}", exc_info=True)
            try:
                await self.websocket.send_json({
                    "type": "error",
                    "message": str(e),
                })
            except:
                pass  # WebSocket might be closed
    
    async def send_audio(self, audio_bytes: bytes):
        """Queue audio data for streaming"""
        await self.audio_queue.put(audio_bytes)
    
    async def stop(self):
        """Stop streaming"""
        self.is_streaming = False
        logger.info(f"🛑 Stopped streaming for session: {self.session_id}")


@router.websocket("/ws/transcribe/{session_id}")
async def websocket_transcribe(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time speech transcription.
    
    Flow:
    1. Client connects and starts sending audio chunks
    2. Server streams audio to Google Speech-to-Text V2 via gRPC
    3. Interim and final results are sent back to client via WebSocket
    4. Client sends {"command": "stop"} to end streaming
    """
    await websocket.accept()
    
    logger.info(f"🔌 WebSocket connected: {session_id}")
    
    stream = TranscriptionStream(websocket, session_id)
    
    try:
        # Start streaming in background
        streaming_task = asyncio.create_task(stream.start())
        
        # Receive audio from frontend
        while True:
            data = await websocket.receive()
            
            if "bytes" in data:
                # Received audio chunk
                await stream.send_audio(data["bytes"])
            elif "text" in data:
                message = json.loads(data["text"])
                if message.get("command") == "stop":
                    break
        
        await stream.stop()
        await streaming_task
        
    except WebSocketDisconnect:
        logger.info(f"🔌 WebSocket disconnected: {session_id}")
        await stream.stop()
    except Exception as e:
        logger.error(f"❌ WebSocket error: {str(e)}", exc_info=True)
        await stream.stop()
    finally:
        logger.info(f"🔚 WebSocket closed: {session_id}")
