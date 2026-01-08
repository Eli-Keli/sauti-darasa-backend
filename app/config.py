from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # Google Cloud
    GCP_PROJECT_ID: str
    GCP_REGION: str = "africa-south1"  # Cloud Run region (near Kenya)
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    
    # Firebase
    FIREBASE_DATABASE_URL: str
    FIREBASE_PROJECT_ID: str
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    ALLOWED_ORIGINS: str
    
    # Speech-to-Text WebSocket Streaming Settings
    # Note: We use US region for Speech API (guaranteed chirp_3 + sw-KE support)
    SPEECH_API_REGION: str = "us"  # US region for Speech API
    SPEECH_MODEL: str = "chirp_3"  # Best multilingual accuracy
    SPEECH_LANGUAGES: List[str] = ["en-US", "sw-KE"]  # English + Swahili Kenya
    SPEECH_SAMPLE_RATE: int = 48000  # Browser standard (48kHz)
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Convert comma-separated ALLOWED_ORIGINS to list"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(',')]
    
    @property
    def gcp_project_id(self) -> str:
        """Lowercase accessor for GCP_PROJECT_ID"""
        return self.GCP_PROJECT_ID
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# CRITICAL: Set GOOGLE_APPLICATION_CREDENTIALS in OS environment
# Google Cloud libraries use os.environ, not Pydantic settings
if settings.GOOGLE_APPLICATION_CREDENTIALS:
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = settings.GOOGLE_APPLICATION_CREDENTIALS
    print(f"✅ Credentials set: {settings.GOOGLE_APPLICATION_CREDENTIALS}")
else:
    print("⚠️  Warning: GOOGLE_APPLICATION_CREDENTIALS not set in .env file")
