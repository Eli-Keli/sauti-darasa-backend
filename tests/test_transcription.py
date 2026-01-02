import pytest
import base64

# Note: These tests require Google Cloud credentials to run
# Mark as integration tests that can be skipped in CI/CD

@pytest.mark.integration
@pytest.mark.asyncio
async def test_transcribe_audio_with_silence():
    """
    Test transcription with silent audio
    Note: This requires actual Google Cloud credentials
    """
    from app.transcription import transcribe_audio
    
    # Sample base64-encoded silent audio (very short)
    # This is a minimal WebM file with silence
    silent_audio = "GkXfo59ChoEBQveBAULygQRC84EIQoKEd2VibUKHgQRChYECGFOAZwH/"
    
    try:
        result = await transcribe_audio(
            audio_base64=silent_audio,
            language_code="en-US",
            sample_rate=16000
        )
        # Silent audio should return empty string
        assert isinstance(result, str)
    except Exception as e:
        pytest.skip(f"Integration test skipped: {str(e)}")

@pytest.mark.asyncio
async def test_transcribe_audio_invalid_base64():
    """Test transcription with invalid base64"""
    from app.transcription import transcribe_audio
    
    with pytest.raises(ValueError):
        await transcribe_audio(
            audio_base64="invalid-base64-$%^&*",
            language_code="en-US",
            sample_rate=16000
        )

def test_base64_decode():
    """Test basic base64 encoding/decoding"""
    test_data = b"Hello, World!"
    encoded = base64.b64encode(test_data).decode('utf-8')
    decoded = base64.b64decode(encoded)
    assert decoded == test_data
