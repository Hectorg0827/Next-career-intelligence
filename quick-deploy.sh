#!/bin/bash

# Quick Deploy to Google Cloud Run
# =================================

echo "🚀 NEXT Career Intelligence - Quick GCP Deployment"
echo "=================================================="
echo ""

# Your Gemini API Key
GEMINI_API_KEY="9c6779342f509f9f39e21adf9e3ec54d4ac5df70"

# Configuration
SERVICE_NAME="next-backend"
REGION="us-central1"

echo "Step 1: Building and deploying..."
echo ""

cd backend

# Deploy to Cloud Run (this will build and deploy in one command)
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
  --set-env-vars "GEMINI_API_KEY=${GEMINI_API_KEY},ENVIRONMENT=production,DEV_MODE=false"

echo ""
echo "✅ Deployment complete!"
echo ""

# Get the URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
  --region ${REGION} \
  --format 'value(status.url)')

echo "=========================================="
echo "🌐 Your Backend URL:"
echo "   ${SERVICE_URL}"
echo ""
echo "📋 Test it:"
echo "   curl ${SERVICE_URL}/api/v1/health"
echo ""
echo "🔧 Update frontend .env.local:"
echo "   NEXT_PUBLIC_API_URL=${SERVICE_URL}"
echo "=========================================="
