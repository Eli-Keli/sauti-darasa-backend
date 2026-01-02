from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.models import TranscribeRequest, TranscribeResponse
from app.transcription import transcribe_audio
from app.firebase_client import publish_caption
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Sauti Darasa Transcription API",
    description="Real-time speech-to-text transcription service for classroom captioning",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Log startup information"""
    logger.info("🚀 Sauti Darasa Backend starting...")
    logger.info(f"Project: {settings.GCP_PROJECT_ID}")
    logger.info(f"Region: {settings.GCP_REGION}")
    logger.info(f"Language: {settings.SPEECH_LANGUAGE_CODE}")
    logger.info(f"Allowed Origins: {settings.allowed_origins_list}")

@app.get("/")
async def root():
    """Root endpoint - service information"""
    return {
        "service": "Sauti Darasa Transcription API",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "transcribe": "/api/transcribe?sessionId={id}",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "transcription-api",
        "project": settings.GCP_PROJECT_ID
    }

@app.post("/api/transcribe", response_model=TranscribeResponse)
async def transcribe(
    request: TranscribeRequest,
    sessionId: str = Query(..., description="Classroom session ID", min_length=1)
):
    """
    Transcribe audio chunk and publish to Firebase.
    
    **Request Body:**
    - `audioChunk`: Base64-encoded audio data (WebM/Opus format, 16kHz, mono)
    
    **Process:**
    1. Receives base64-encoded audio chunk from frontend
    2. Transcribes using Google Cloud Speech-to-Text
    3. Publishes caption to Firebase Realtime Database
    4. Students receive caption in real-time via Firebase listener
    
    **Response:**
    - `success`: Boolean indicating operation success
    - `transcript`: Transcribed text (empty string if no speech detected)
    - `sessionId`: Session ID for tracking
    - `error`: Error message if operation failed
    """
    try:
        logger.info(f"📝 Received transcription request for session: {sessionId}")
        
        # Transcribe audio
        transcript = await transcribe_audio(
            audio_base64=request.audioChunk,
            language_code=settings.SPEECH_LANGUAGE_CODE,
            sample_rate=settings.SPEECH_SAMPLE_RATE
        )
        
        if not transcript:
            logger.warning(f"⚠️  No transcript generated for session: {sessionId}")
            return TranscribeResponse(
                success=True,
                transcript="",
                sessionId=sessionId
            )
        
        # Publish to Firebase
        await publish_caption(sessionId, transcript)
        
        logger.info(f"✅ Transcription successful for {sessionId}: {transcript[:50]}...")
        
        return TranscribeResponse(
            success=True,
            transcript=transcript,
            sessionId=sessionId
        )
        
    except ValueError as e:
        logger.error(f"❌ Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Transcription failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 handler"""
    return {
        "error": "Endpoint not found",
        "message": "Visit /docs for API documentation"
    }
