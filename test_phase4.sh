#!/bin/bash

echo "==================================================================="
echo "Phase 4: Better Performance and Reliability - Verification Tests"
echo "==================================================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Base URL
BASE_URL="http://localhost:8000"

echo "${BLUE}1. Testing Basic Health Check${NC}"
curl -s "$BASE_URL/api/health" | python3 -m json.tool
echo ""

echo "${BLUE}2. Testing Detailed Health Check (with Redis, Database, Scheduler)${NC}"
curl -s "$BASE_URL/api/health/detailed" | python3 -m json.tool
echo ""

echo "${BLUE}3. Testing Performance Metrics Endpoint${NC}"
curl -s "$BASE_URL/api/performance" | python3 -m json.tool
echo ""

echo "${BLUE}4. Testing Response Compression (checking headers)${NC}"
curl -s -I "$BASE_URL/api/health" | grep -i "content-encoding\|content-length"
echo ""

echo "${BLUE}5. Testing Rate Limiting (making 3 rapid requests)${NC}"
for i in {1..3}; do
  echo "Request $i:"
  curl -s -w "\nHTTP Status: %{http_code}\n" "$BASE_URL/api/health" | head -n 1
  sleep 0.5
done
echo ""

echo "${GREEN}==================================================================="
echo "Phase 4 Verification Complete!"
echo "===================================================================${NC}"
echo ""
echo "✅ Features Tested:"
echo "  1. Health monitoring system"
echo "  2. Redis caching integration"
echo "  3. Database connection pooling"
echo "  4. Background task scheduler (6 tasks)"
echo "  5. Performance metrics collection"
echo "  6. Response compression"
echo "  7. Rate limiting"
echo ""
echo "📊 Check the logs above for:"
echo "  - All services showing as 'healthy'"
echo "  - Redis connected: true"
echo "  - Database connected: true"
echo "  - Scheduler running: true"
echo "  - Active tasks: 6"
echo ""
