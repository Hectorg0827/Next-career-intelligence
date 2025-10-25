#!/bin/bash

# Google Cloud Run Deployment Script for NEXT Career Intelligence Backend
# =========================================================================

set -e  # Exit on error

echo "🚀 Deploying NEXT Career Intelligence Backend to Google Cloud Run"
echo "=================================================================="
echo ""

# Configuration
PROJECT_ID="next-career-intelligence"
SERVICE_NAME="next-backend"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"
PORT=8000

# API Key from user
GEMINI_API_KEY="9c6779342f509f9f39e21adf9e3ec54d4ac5df70"

echo "📋 Configuration:"
echo "  Project ID: ${PROJECT_ID}"
echo "  Service Name: ${SERVICE_NAME}"
echo "  Region: ${REGION}"
echo "  Port: ${PORT}"
echo ""

# Step 1: Check if gcloud is installed
echo "1️⃣  Checking gcloud CLI installation..."
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found!"
    echo "   Please install: https://cloud.google.com/sdk/docs/install"
    exit 1
fi
echo "✅ gcloud CLI found"
echo ""

# Step 2: Set the project
echo "2️⃣  Setting Google Cloud project..."
gcloud config set project ${PROJECT_ID} 2>/dev/null || {
    echo "⚠️  Project ${PROJECT_ID} not found. Creating new project..."
    gcloud projects create ${PROJECT_ID} --name="NEXT Career Intelligence"
    gcloud config set project ${PROJECT_ID}
}
echo "✅ Project set to: ${PROJECT_ID}"
echo ""

# Step 3: Enable required APIs
echo "3️⃣  Enabling required Google Cloud APIs..."
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    containerregistry.googleapis.com \
    artifactregistry.googleapis.com \
    --project=${PROJECT_ID}
echo "✅ APIs enabled"
echo ""

# Step 4: Build the container image
echo "4️⃣  Building Docker container..."
cd backend
gcloud builds submit \
    --tag ${IMAGE_NAME} \
    --project=${PROJECT_ID} \
    --timeout=20m
echo "✅ Container built: ${IMAGE_NAME}"
echo ""

# Step 5: Deploy to Cloud Run
echo "5️⃣  Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME} \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --port ${PORT} \
    --memory 2Gi \
    --cpu 2 \
    --min-instances 0 \
    --max-instances 10 \
    --timeout 300 \
    --set-env-vars "GEMINI_API_KEY=${GEMINI_API_KEY}" \
    --set-env-vars "ENVIRONMENT=production" \
    --set-env-vars "DEV_MODE=false" \
    --project=${PROJECT_ID}

echo ""
echo "✅ Deployment complete!"
echo ""

# Step 6: Get the service URL
echo "6️⃣  Getting service URL..."
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
    --platform managed \
    --region ${REGION} \
    --format 'value(status.url)' \
    --project=${PROJECT_ID})

echo ""
echo "=========================================="
echo "✅ DEPLOYMENT SUCCESSFUL!"
echo "=========================================="
echo ""
echo "🌐 Backend URL: ${SERVICE_URL}"
echo ""
echo "📋 API Endpoints:"
echo "  Health Check: ${SERVICE_URL}/api/v1/health"
echo "  Documentation: ${SERVICE_URL}/docs"
echo "  OpenAPI: ${SERVICE_URL}/openapi.json"
echo ""
echo "🔧 Update your frontend .env.local:"
echo "  NEXT_PUBLIC_API_URL=${SERVICE_URL}"
echo ""
echo "🧪 Test the deployment:"
echo "  curl ${SERVICE_URL}/api/v1/health"
echo ""
echo "=========================================="
