#!/bin/bash

# Seed jobs marketplace with AI-generated job postings

echo "🌱 Seeding job marketplace..."

# Login to get JWT token
TOKEN=$(curl -s -X POST "https://next-career-backend-795538981829.us-central1.run.app/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "elite@nextci.net",
    "password": "NextElite2025!"
  }' | jq -r '.access_token')

if [ -z "$TOKEN" ] || [ "$TOKEN" = "null" ]; then
  echo "❌ Failed to get authentication token"
  exit 1
fi

echo "✅ Authenticated successfully"

# Seed jobs
RESPONSE=$(curl -s -X POST "https://next-career-backend-795538981829.us-central1.run.app/api/jobs/seed?count=50" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")

echo "$RESPONSE" | jq .

if echo "$RESPONSE" | jq -e '.success' > /dev/null 2>&1; then
  echo "✅ Successfully seeded job marketplace!"
else
  echo "❌ Failed to seed jobs"
  exit 1
fi
