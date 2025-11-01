#!/bin/bash
# Deploy Backend to GCP Cloud Run - Quick Deploy Script

set -e  # Exit on error

echo "🚀 Deploying NEXT Career Intelligence Backend to GCP Cloud Run..."
echo ""

# Configuration
PROJECT_ID="your-gcp-project-id"
SERVICE_NAME="next-career-backend"
REGION="us-central1"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found. Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

echo "📋 Using configuration:"
echo "   Service: $SERVICE_NAME"
echo "   Region: $REGION"
echo ""

# Get current project
CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null)
if [ -z "$CURRENT_PROJECT" ]; then
    echo "⚠️  No GCP project set. Please set it with: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo "   Project: $CURRENT_PROJECT"
echo ""

# Read environment variables from .env
echo "📝 Loading environment variables from .env..."
if [ ! -f .env ]; then
    echo "❌ .env file not found! Please create it with required variables."
    exit 1
fi

# Build environment variables string for Cloud Run
ENV_VARS=""
while IFS= read -r line || [ -n "$line" ]; do
    # Skip empty lines and comments
    if [[ ! -z "$line" && ! "$line" =~ ^# ]]; then
        # Remove any trailing whitespace/newlines
        line=$(echo "$line" | tr -d '\r' | tr -d '\n')
        if [ -z "$ENV_VARS" ]; then
            ENV_VARS="$line"
        else
            ENV_VARS="$ENV_VARS,$line"
        fi
    fi
done < .env

echo "✅ Environment variables loaded"
echo ""

# Deploy to Cloud Run
echo "🏗️  Building and deploying to Cloud Run..."
echo ""

gcloud run deploy "$SERVICE_NAME" \
    --source . \
    --platform managed \
    --region "$REGION" \
    --allow-unauthenticated \
    --set-env-vars="$ENV_VARS" \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --max-instances 10 \
    --min-instances 0

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Deployment successful!"
    echo ""
    
    # Get the service URL
    SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --region "$REGION" --format 'value(status.url)')
    
    echo "🌐 Your backend is now live at:"
    echo "   $SERVICE_URL"
    echo ""
    echo "📋 Next steps:"
    echo "   1. Test health endpoint: curl $SERVICE_URL/api/health"
    echo "   2. Update frontend NEXT_PUBLIC_API_URL to: $SERVICE_URL"
    echo "   3. Update ALLOWED_ORIGINS in Cloud Run to include your frontend domain"
    echo ""
else
    echo ""
    echo "❌ Deployment failed. Please check the errors above."
    exit 1
fi
