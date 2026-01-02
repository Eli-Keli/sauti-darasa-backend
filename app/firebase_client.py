import firebase_admin
from firebase_admin import credentials, db
from app.config import settings
import logging
import os

logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK
def initialize_firebase():
    """Initialize Firebase Admin SDK if not already initialized"""
    if not firebase_admin._apps:
        try:
            # Use service account key file if provided (local dev)
            # Otherwise use Application Default Credentials (Cloud Run)
            if settings.GOOGLE_APPLICATION_CREDENTIALS and os.path.exists(settings.GOOGLE_APPLICATION_CREDENTIALS):
                logger.info(f"Using service account key: {settings.GOOGLE_APPLICATION_CREDENTIALS}")
                cred = credentials.Certificate(settings.GOOGLE_APPLICATION_CREDENTIALS)
            else:
                logger.info("Using Application Default Credentials (Cloud Run)")
                cred = credentials.ApplicationDefault()
            
            firebase_admin.initialize_app(cred, {
                'databaseURL': settings.FIREBASE_DATABASE_URL
            })
            logger.info("Firebase Admin SDK initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {str(e)}")
            raise

# Initialize on module import
initialize_firebase()

async def publish_caption(session_id: str, caption_text: str) -> None:
    """
    Publish caption to Firebase Realtime Database.
    
    Writes to: /captions/{sessionId}/latest
    Structure: { text: string, timestamp: ServerValue.TIMESTAMP }
    
    Args:
        session_id: Classroom session ID
        caption_text: Transcribed text to publish
    """
    try:
        if not caption_text:
            logger.debug(f"Skipping empty caption for session: {session_id}")
            return
        
        ref = db.reference(f'captions/{session_id}/latest')
        ref.set({
            'text': caption_text,
            'timestamp': {'.sv': 'timestamp'}  # Firebase server timestamp
        })
        
        logger.info(f"Caption published to session {session_id}: {caption_text[:30]}...")
        
    except Exception as e:
        logger.error(f"Failed to publish caption: {str(e)}")
        raise
