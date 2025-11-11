#!/bin/bash
# NEXT Career Intelligence - Production Deployment Script
# Automated deployment to Google Cloud Run + Vercel
#
# Prerequisites:
# - gcloud CLI installed and authenticated
# - vercel CLI installed and authenticated
# - PostgreSQL client (psql) installed
# - All environment variables configured
#
# Usage: ./scripts/deploy-to-production.sh

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GCP_PROJECT_ID="${GCP_PROJECT_ID:-your-gcp-project-id}"
GCP_REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="${SERVICE_NAME:-next-backend}"

echo -e "${BLUE}=================================${NC}"
echo -e "${BLUE}NEXT Production Deployment${NC}"
echo -e "${BLUE}=================================${NC}"
echo ""

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: gcloud CLI not found. Install from https://cloud.google.com/sdk/docs/install${NC}"
    exit 1
fi

if ! command -v vercel &> /dev/null; then
    echo -e "${RED}Error: vercel CLI not found. Run: npm install -g vercel${NC}"
    exit 1
fi

if ! command -v psql &> /dev/null; then
    echo -e "${RED}Error: psql not found. Install PostgreSQL client${NC}"
    exit 1
fi

echo -e "${GREEN}✓ All prerequisites met${NC}"
echo ""

# Confirm production deployment
echo -e "${YELLOW}⚠️  You are about to deploy to PRODUCTION${NC}"
read -p "Continue? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo -e "${RED}Deployment cancelled${NC}"
    exit 0
fi
echo ""

# Step 1: Run tests
echo -e "${BLUE}Step 1/7: Running tests...${NC}"
cd "$PROJECT_ROOT/backend"
if [ -f "pytest.ini" ] || [ -d "tests" ]; then
    python -m pytest tests/ -v || {
        echo -e "${RED}Tests failed. Fix errors before deploying${NC}"
        exit 1
    }
    echo -e "${GREEN}✓ Tests passed${NC}"
else
    echo -e "${YELLOW}⚠️  No tests found, skipping${NC}"
fi
echo ""

# Step 2: Database migrations
echo -e "${BLUE}Step 2/7: Deploying database migrations...${NC}"
read -p "Enter production DATABASE_URL: " DATABASE_URL_PROD

if [ -z "$DATABASE_URL_PROD" ]; then
    echo -e "${RED}Error: DATABASE_URL is required${NC}"
    exit 1
fi

export DATABASE_URL="$DATABASE_URL_PROD"

# Test connection
echo "Testing database connection..."
psql "$DATABASE_URL" -c "SELECT version();" > /dev/null 2>&1 || {
    echo -e "${RED}Failed to connect to database${NC}"
    exit 1
}
echo -e "${GREEN}✓ Database connection successful${NC}"

# Run migrations
echo "Running migrations..."
for migration in "$PROJECT_ROOT"/backend/migrations/*.sql; do
    if [ -f "$migration" ]; then
        echo "  Applying $(basename "$migration")..."
        psql "$DATABASE_URL" -f "$migration" || {
            echo -e "${RED}Migration failed: $(basename "$migration")${NC}"
            exit 1
        }
    fi
done
echo -e "${GREEN}✓ Migrations completed${NC}"
echo ""

# Step 3: Build backend
echo -e "${BLUE}Step 3/7: Building backend...${NC}"
cd "$PROJECT_ROOT/backend"

# Create requirements.txt if it doesn't exist
if [ ! -f "requirements.txt" ]; then
    echo -e "${YELLOW}⚠️  requirements.txt not found${NC}"
fi

echo -e "${GREEN}✓ Backend build prepared${NC}"
echo ""

# Step 4: Deploy backend to Cloud Run
echo -e "${BLUE}Step 4/7: Deploying backend to Cloud Run...${NC}"

# Check if Cloud Build config exists
if [ ! -f "$PROJECT_ROOT/cloudbuild.yaml" ]; then
    echo -e "${RED}Error: cloudbuild.yaml not found${NC}"
    exit 1
fi

echo "Deploying to Cloud Run..."
gcloud builds submit \
  --config="$PROJECT_ROOT/cloudbuild.yaml" \
  --substitutions=_ENV=production,_SERVICE_NAME="$SERVICE_NAME" \
  --region="$GCP_REGION" \
  --project="$GCP_PROJECT_ID" \
  "$PROJECT_ROOT/backend" || {
    echo -e "${RED}Backend deployment failed${NC}"
    exit 1
}

echo -e "${GREEN}✓ Backend deployed successfully${NC}"
echo ""

# Step 5: Get backend URL
echo -e "${BLUE}Step 5/7: Getting backend URL...${NC}"
BACKEND_URL=$(gcloud run services describe "$SERVICE_NAME" \
  --region="$GCP_REGION" \
  --project="$GCP_PROJECT_ID" \
  --format="value(status.url)")

if [ -z "$BACKEND_URL" ]; then
    echo -e "${RED}Failed to get backend URL${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Backend URL: $BACKEND_URL${NC}"
echo ""

# Step 6: Health check
echo -e "${BLUE}Step 6/7: Health check...${NC}"
sleep 5  # Wait for service to be ready

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/health" || echo "000")

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✓ Backend is healthy${NC}"
else
    echo -e "${YELLOW}⚠️  Health check returned: $HTTP_CODE${NC}"
    read -p "Continue anyway? (yes/no): " continue_deploy
    if [ "$continue_deploy" != "yes" ]; then
        echo -e "${RED}Deployment aborted${NC}"
        exit 1
    fi
fi
echo ""

# Step 7: Deploy frontend to Vercel
echo -e "${BLUE}Step 7/7: Deploying frontend to Vercel...${NC}"
cd "$PROJECT_ROOT/frontend"

# Set environment variable for Vercel
echo "NEXT_PUBLIC_API_URL=$BACKEND_URL" > .env.production

echo "Deploying to Vercel..."
vercel --prod --yes || {
    echo -e "${RED}Frontend deployment failed${NC}"
    exit 1
}

echo -e "${GREEN}✓ Frontend deployed successfully${NC}"
echo ""

# Deployment summary
echo -e "${BLUE}=================================${NC}"
echo -e "${GREEN}✓ Deployment Complete!${NC}"
echo -e "${BLUE}=================================${NC}"
echo ""
echo -e "Backend URL:  $BACKEND_URL"
echo -e "Frontend URL: Check Vercel output above"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Verify deployment at the URLs above"
echo "2. Test critical user flows (signup, login, job search)"
echo "3. Monitor logs for errors"
echo "4. Set up monitoring alerts (see DEPLOY_TO_PRODUCTION_QUICKSTART.md)"
echo ""
echo -e "${GREEN}Deployment completed successfully! 🚀${NC}"
