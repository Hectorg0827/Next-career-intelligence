#!/bin/bash
set -e

cd /Users/hectorgarcia/Desktop/Next-career-intelligence/backend

# Deploy with all environment variables using update-env-vars
gcloud run deploy next-career-backend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --update-env-vars \
    ENVIRONMENT=production \
    DEBUG=false \
    LOG_LEVEL=INFO \
    SUPABASE_URL=https://whxbxjpymksgvixudnjh.supabase.co \
    DATABASE_URL=postgresql://postgres:ssuRd6vrGSdP5z7a@db.whxbxjpymksgvixudnjh.supabase.co:5432/postgres

# Now update with the remaining variables that include special characters
gcloud run deploy next-career-backend \
  --no-gen2 \
  --region us-central1 \
  --update-env-vars \
    SUPABASE_SERVICE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndoeGJ4anB5bWtzZ3ZpeHVkbmpoIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MDg2MDM0OSwiZXhwIjoyMDc2NDM2MzQ5fQ.0HqpO0KEmyvCIKhf1WdTCFw2iH-UGXVxGRE6_Ati3ig" \
    SUPABASE_ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndoeGJ4anB5bWtzZ3ZpeHVkbmpoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA4NjAzNDksImV4cCI6MjA3NjQzNjM0OX0.8ykQi5mPIe48aA8E3J82acqqPlhEtS7VICduXOui0zc" \
    GEMINI_API_KEY="AIzaSyBT4RfbAa2jcjrXC8hAwAZTKveC48V5QXg"

echo "Deployment initiated"
