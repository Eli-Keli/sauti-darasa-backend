from pydantic import BaseModel, Field

class TranscribeRequest(BaseModel):
    """Request model for audio transcription"""
    audioChunk: str = Field(
        ..., 
        description="Base64-encoded audio data (without data URL prefix)",
        min_length=1
    )

class TranscribeResponse(BaseModel):
    """Response model for transcription results"""
    success: bool
    transcript: str
    sessionId: str
    error: str | None = None
