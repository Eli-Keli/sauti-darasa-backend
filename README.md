# Sauti Darasa Backend

Real-time Speech-to-Text transcription service for classroom captioning.

## 🚀 Tech Stack
- **Python 3.11** + FastAPI
- **Google Cloud Speech-to-Text API**
- **Firebase Realtime Database**
- **Deployed on Google Cloud Run**

## 📦 Setup

### 1. Create Virtual Environment
```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env with your credentials
```

### 4. Obtain Service Account Key
```bash
# Download from GCP Console or use gcloud
gcloud iam service-accounts keys create ./sauti-darasa-key.json \
  --iam-account=YOUR_SERVICE_ACCOUNT@sauti-darasa.iam.gserviceaccount.com
```

## 🏃 Run Locally
```bash
uvicorn app.main:app --reload --port 8000
```

Visit: http://localhost:8000/docs for API documentation

## 🧪 Run Tests
```bash
pytest tests/ -v
```

## 🚀 Deployment
```bash
./deploy-backend.sh
```

## 📁 Project Structure
```
sauti-darasa-backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration
│   ├── models.py            # Pydantic models
│   ├── transcription.py     # Speech-to-Text logic
│   └── firebase_client.py   # Firebase integration
├── tests/
│   ├── test_api.py
│   └── test_transcription.py
├── Dockerfile
├── deploy-backend.sh
└── requirements.txt
```

## 🔗 Frontend Repository
https://github.com/Eli-Keli/SautiDarasa

## 📄 License
MIT
