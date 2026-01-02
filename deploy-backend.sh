#!/bin/bash

set -e

echo "🚀 Deploying Sauti Darasa Backend to Google Cloud Run..."

# Configuration
PROJECT_ID="sauti-darasa"
REGION="africa-south1"
SERVICE_NAME="sauti-darasa-backend"
SERVICE_ACCOUNT="sauti-darasa-backend@sauti-darasa.iam.gserviceaccount.com"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

# Set project
echo "🔧 Setting GCP project..."
gcloud config set project $PROJECT_ID

# Configure Docker authentication
echo "🔐 Configuring Docker authentication..."
gcloud auth configure-docker --quiet

# Build Docker image
echo "🏗️  Building Docker image..."
docker build --platform linux/amd64 -t $IMAGE_NAME:latest .

# Push to Google Container Registry
echo "📤 Pushing to GCR..."
docker push $IMAGE_NAME:latest

# Deploy to Cloud Run with service account
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE_NAME:latest \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --timeout 60s \
  --max-instances 10 \
  --min-instances 0 \
  --service-account $SERVICE_ACCOUNT \
  --set-env-vars "GCP_PROJECT_ID=$PROJECT_ID,GCP_REGION=$REGION,FIREBASE_DATABASE_URL=https://sautidarasa.firebaseio.com,FIREBASE_PROJECT_ID=sautidarasa,SPEECH_LANGUAGE_CODE=en-KE,SPEECH_SAMPLE_RATE=16000,ALLOWED_ORIGINS=https://sauti-darasa-pwa-512236104756.africa-south1.run.app,http://localhost:5173"

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)')

echo ""
echo "✅ Deployment successful!"
echo "🌐 Backend URL: $SERVICE_URL"
echo ""
echo "📋 Next steps:"
echo "  1. Test health endpoint: curl $SERVICE_URL/health"
echo "  2. View API docs: open $SERVICE_URL/docs"
echo "  3. Update frontend .env.gcloud with:"
echo "     VITE_BACKEND_API_URL=$SERVICE_URL"
echo "  4. Redeploy frontend to use new backend"
