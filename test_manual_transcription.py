#!/usr/bin/env python3
"""
Manual test script for Google Cloud Speech-to-Text API
Tests with a local audio file to verify the API works
"""
import os
from google.cloud import speech_v1 as speech

def transcribe_file(audio_file_path: str, encoding=None, sample_rate=16000):
    """Transcribe a local audio file"""
    
    # Initialize client
    client = speech.SpeechClient()
    
    # Read audio file
    with open(audio_file_path, 'rb') as audio_file:
        content = audio_file.read()
    
    audio = speech.RecognitionAudio(content=content)
    
    # Try different configurations
    configs = []
    
    if encoding:
        # Use specified encoding
        configs.append({
            "name": f"{encoding} with {sample_rate}Hz",
            "config": speech.RecognitionConfig(
                encoding=encoding,
                sample_rate_hertz=sample_rate,
                language_code="en-KE",
                enable_automatic_punctuation=True,
            )
        })
    else:
        # Auto-detect configurations
        configs = [
            {
                "name": "LINEAR16 16kHz",
                "config": speech.RecognitionConfig(
                    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                    sample_rate_hertz=16000,
                    language_code="en-KE",
                    enable_automatic_punctuation=True,
                )
            },
            {
                "name": "LINEAR16 48kHz",
                "config": speech.RecognitionConfig(
                    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                    sample_rate_hertz=48000,
                    language_code="en-KE",
                    enable_automatic_punctuation=True,
                )
            },
        ]
    
    for config_info in configs:
        try:
            print(f"\n🔄 Trying: {config_info['name']}")
            response = client.recognize(config=config_info['config'], audio=audio)
            
            print(f"✅ API returned {len(response.results)} results")
            
            if response.results:
                for i, result in enumerate(response.results):
                    if result.alternatives:
                        transcript = result.alternatives[0].transcript
                        confidence = result.alternatives[0].confidence
                        print(f"📝 Result {i}: '{transcript}'")
                        print(f"   Confidence: {confidence:.2%}")
                return True
            else:
                print("⚠️  No speech detected")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    return False

if __name__ == "__main__":
    print("=" * 60)
    print("Google Cloud Speech-to-Text API Manual Test")
    print("=" * 60)
    
    # Set credentials
    if os.path.exists("./sauti-darasa-key.json"):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./sauti-darasa-key.json"
        print("✅ Using service account key: sauti-darasa-key.json\n")
    else:
        print("⚠️  No service account key found, using default credentials\n")
    
    # Check for test audio file
    test_files = ["test_audio.wav", "test.wav", "sample.wav"]
    audio_file = None
    
    for f in test_files:
        if os.path.exists(f):
            audio_file = f
            break
    
    if audio_file:
        print(f"📁 Found audio file: {audio_file}")
        file_size = os.path.getsize(audio_file)
        print(f"📊 File size: {file_size} bytes\n")
        
        transcribe_file(audio_file)
    else:
        print("❌ No test audio file found!")
        print("\nTo create a test audio file:")
        print("1. Record yourself saying: 'Hello, this is a test'")
        print("2. Save as WAV file (16kHz, mono)")
        print("3. Place it in this directory as 'test_audio.wav'")
        print("\nOr use this command to record on macOS:")
        print("   rec -r 16000 -c 1 test_audio.wav trim 0 5")
        print("\nOr record using QuickTime Player and convert:")
        print("   ffmpeg -i recording.m4a -ar 16000 -ac 1 test_audio.wav")
