"""
Test script to check if the Speech-to-Text API can handle the audio format
"""
import base64
import os
from google.cloud import speech_v1 as speech

# Sample base64 audio (you'll need to get this from your logs or frontend)
# For now, let's just test the API configuration

def test_speech_api():
    """Test Speech-to-Text API configuration"""
    try:
        client = speech.SpeechClient()
        print("✅ Speech-to-Text client initialized successfully")
        
        # Test different configurations
        configs_to_test = [
            {
                "name": "WEBM_OPUS with 16kHz",
                "encoding": speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
                "sample_rate": 16000
            },
            {
                "name": "WEBM_OPUS with 48kHz",
                "encoding": speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
                "sample_rate": 48000
            },
            {
                "name": "WEBM_OPUS without sample rate",
                "encoding": speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
                "sample_rate": None
            }
        ]
        
        for config_test in configs_to_test:
            print(f"\n📋 Testing: {config_test['name']}")
            print(f"   Encoding: {config_test['encoding']}")
            print(f"   Sample Rate: {config_test['sample_rate']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_speech_api()
