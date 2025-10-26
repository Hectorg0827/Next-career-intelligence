#!/bin/bash

# =============================================================================
# NEXT Career Intelligence - Backend Deployment to Google Cloud Run
# =============================================================================
# 
# Gemini API Key: 9c6779342f509f9f39e21adf9e3ec54d4ac5df70
# Authenticated Account: hector.garcia0827@gmail.com
# =============================================================================

set -e

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  NEXT Career Intelligence - Backend Deployment            ║"
echo "║  Target: Google Cloud Run                                 ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Configuration
GEMINI_API_KEY="9c6779342f509f9f39e21adf9e3ec54d4ac5df70"
SERVICE_NAME="next-backend"
REGION="us-central1"
PROJECT_ID="next-475619"  # Your actual GCP project ID

if [ -z "$PROJECT_ID" ]; then
    echo "⚠️  Using project: ${PROJECT_ID}"
else
    echo "✓ Project ID confirmed: ${PROJECT_ID}"
fi

echo "📋 Deployment Configuration:"
echo "   ✓ Project ID: ${PROJECT_ID}"
echo "   ✓ Service Name: ${SERVICE_NAME}"
echo "   ✓ Region: ${REGION}"
echo "   ✓ Account: hector.garcia0827@gmail.com"
echo ""

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable run.googleapis.com cloudbuild.googleapis.com --project=${PROJECT_ID} 2>/dev/null || true
echo "   ✓ APIs enabled"
echo ""

# Navigate to backend directory
cd "$(dirname "$0")/backend"

echo "🏗️  Building and deploying to Cloud Run..."
echo "   (This may take 3-5 minutes)"
echo ""

# Deploy
gcloud run deploy ${SERVICE_NAME} \
  --source . \
  --region ${REGION} \
  --allow-unauthenticated \
  --port 8000 \
  --memory 2Gi \
  --cpu 2 \
  --min-instances 0 \
  --max-instances 10 \
  --timeout 300 \
  --set-env-vars "GEMINI_API_KEY=${GEMINI_API_KEY},ENVIRONMENT=production,DEV_MODE=false" \
  --project=${PROJECT_ID}

# Get the service URL
echo ""
echo "📍 Fetching service URL..."
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
  --region ${REGION} \
  --format 'value(status.url)' \
  --project=${PROJECT_ID})

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║               ✅ DEPLOYMENT SUCCESSFUL! ✅                 ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "🌐 Backend URL:"
echo "   ${SERVICE_URL}"
echo ""
echo "📋 API Endpoints:"
echo "   Health:   ${SERVICE_URL}/api/v1/health"
echo "   Docs:     ${SERVICE_URL}/docs"
echo "   Analyze:  ${SERVICE_URL}/api/v1/analyze"
echo ""
echo "🧪 Test Your Deployment:"
echo "   curl ${SERVICE_URL}/api/v1/health"
echo ""
echo "🔧 Update Frontend Configuration:"
echo "   File: frontend/.env.local"
echo "   Add:  NEXT_PUBLIC_API_URL=${SERVICE_URL}"
echo ""
echo "📊 View Logs:"
echo "   gcloud run services logs read ${SERVICE_NAME} --region ${REGION}"
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Next Steps:                                              ║"
echo "║  1. Test the health endpoint                              ║"
echo "║  2. Update frontend .env.local with backend URL           ║"
echo "║  3. Test job analysis from frontend                       ║"
echo "║  4. Monitor logs for any issues                           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
