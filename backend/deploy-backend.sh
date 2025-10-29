#!/bin/bash

# Quick Deploy Script for Backend to Google Cloud Run
# Usage: ./deploy-backend.sh

set -e

echo "🚀 Starting Backend Deployment to Google Cloud Run..."

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found. Please install it first:"
    echo "   brew install --cask google-cloud-sdk"
    exit 1
fi

# Check if logged in
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ Not logged in to gcloud. Please run: gcloud auth login"
    exit 1
fi

# Configuration
PROJECT_ID="next-fc055"
SERVICE_NAME="next-backend"
REGION="us-central1"
MEMORY="1Gi"
CPU="1"
MAX_INSTANCES="10"
MIN_INSTANCES="0"
PORT="8080"

echo "📦 Project: $PROJECT_ID"
echo "📦 Service: $SERVICE_NAME"
echo "🌍 Region: $REGION"

# Set project
gcloud config set project $PROJECT_ID

# Check if .env.production exists
if [ ! -f .env.production ]; then
    echo "⚠️  .env.production not found. Creating from template..."
    cp .env.production.template .env.production
    echo "📝 Please edit .env.production with your actual values"
    echo "   Then run this script again"
    exit 1
fi

# Build and deploy
echo "🔨 Building and deploying to Cloud Run..."

gcloud run deploy $SERVICE_NAME \
  --source . \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory $MEMORY \
  --cpu $CPU \
  --max-instances $MAX_INSTANCES \
  --min-instances $MIN_INSTANCES \
  --port $PORT \
  --env-vars-file .env.production \
  --quiet

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format='value(status.url)')

echo ""
echo "✅ Deployment successful!"
echo "🌐 Backend URL: $SERVICE_URL"
echo ""
echo "📋 Next steps:"
echo "   1. Test the health endpoint: curl $SERVICE_URL/api/health"
echo "   2. Update frontend NEXT_PUBLIC_API_URL to: $SERVICE_URL"
echo "   3. Configure CORS in backend/app/core/middleware.py"
echo ""
