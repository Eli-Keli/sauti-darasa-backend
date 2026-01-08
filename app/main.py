from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.config import settings
from app.websocket import router as websocket_router
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown"""
    # Startup
    logger.info("🚀 Sauti Darasa Backend starting...")
    logger.info(f"Project: {settings.GCP_PROJECT_ID}")
    logger.info(f"Region: {settings.GCP_REGION}")
    logger.info(f"Allowed Origins: {settings.allowed_origins_list}")
    logger.info("📡 WebSocket endpoint: /ws/transcribe/{session_id}")
    yield
    # Shutdown
    logger.info("🛑 Sauti Darasa Backend shutting down...")

# Create FastAPI application
app = FastAPI(
    title="Sauti Darasa Transcription API",
    description="Real-time speech-to-text transcription service for classroom captioning",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include WebSocket router for streaming transcription
app.include_router(websocket_router, tags=["WebSocket"])

@app.get("/")
async def root():
    """Root endpoint - service information"""
    return {
        "service": "Sauti Darasa Transcription API",
        "status": "running",
        "version": "2.0.0",
        "endpoints": {
            "health": "/health",
            "websocket": "/ws/transcribe/{session_id}",
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

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 handler"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Endpoint not found",
            "message": "Visit /docs for API documentation"
        }
    )
