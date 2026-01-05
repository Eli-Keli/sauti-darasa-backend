from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    # Google Cloud
    GCP_PROJECT_ID: str
    GCP_REGION: str
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    
    # Firebase
    FIREBASE_DATABASE_URL: str
    FIREBASE_PROJECT_ID: str
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    ALLOWED_ORIGINS: str
    
    # Speech-to-Text Settings
    SPEECH_LANGUAGE_CODE: str = "en-KE"
    SPEECH_SAMPLE_RATE: int = 48000  # Updated default to 48kHz (browser standard)
    
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
