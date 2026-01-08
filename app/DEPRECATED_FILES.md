# Deprecated Backend Files

The following files are **NO LONGER USED** in the WebSocket + gRPC streaming architecture:

## 1. transcription.py
**Status**: ❌ DEPRECATED  
**Reason**: Used the old HTTP-based synchronous `Speech.Recognize` API  
**Replaced by**: `websocket.py` with `StreamingRecognize` API  
**Action**: Can be safely deleted or archived for reference

## 2. transcription_streaming.py
**Status**: ❌ DEPRECATED  
**Reason**: Attempted to use Speech V1 API with improper streaming setup  
**Replaced by**: `websocket.py` with proper Speech V2 gRPC streaming  
**Action**: Can be safely deleted

## 3. models.py
**Status**: ⚠️ PARTIALLY DEPRECATED  
**Reason**: Contains `TranscribeRequest` and `TranscribeResponse` models for HTTP endpoint  
**Note**: HTTP endpoint is now commented out in `main.py`  
**Action**: Can keep for reference or delete if HTTP endpoint is permanently removed

---

## Current Active Files

✅ **websocket.py** - WebSocket endpoint with gRPC bidirectional streaming  
✅ **main.py** - FastAPI app with WebSocket router  
✅ **config.py** - Configuration settings for WebSocket streaming  
✅ **firebase_client.py** - Firebase Realtime Database integration  

---

**Recommendation**: Delete or move `transcription.py`, `transcription_streaming.py`, and `models.py` to an `archive/` folder.
