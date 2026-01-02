import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    """Test root endpoint returns service info"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert data["service"] == "Sauti Darasa Transcription API"
    assert "status" in data
    assert data["status"] == "running"

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data

def test_transcribe_endpoint_missing_session_id():
    """Test transcribe endpoint without session ID"""
    response = client.post(
        "/api/transcribe",
        json={"audioChunk": "base64-data"}
    )
    assert response.status_code == 422  # Validation error

def test_transcribe_endpoint_empty_audio():
    """Test transcribe endpoint with empty audio chunk"""
    response = client.post(
        "/api/transcribe?sessionId=test-session-123",
        json={"audioChunk": ""}
    )
    assert response.status_code == 422  # Validation error - min_length=1

def test_transcribe_endpoint_invalid_json():
    """Test transcribe endpoint with invalid JSON"""
    response = client.post(
        "/api/transcribe?sessionId=test-123",
        data="invalid json",
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 422

def test_docs_endpoint():
    """Test API documentation is available"""
    response = client.get("/docs")
    assert response.status_code == 200
