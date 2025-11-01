#!/bin/bash

# Phase 4 Verification Script
# Verify all Phase 4 components are working correctly

set -e

echo "🔍 Phase 4 Verification"
echo "======================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASS=0
FAIL=0

check() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $1${NC}"
        ((PASS++))
    else
        echo -e "${RED}✗ $1${NC}"
        ((FAIL++))
    fi
}

# Check Redis
echo "Checking Redis..."
if redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Redis is running${NC}"
    ((PASS++))
else
    echo -e "${YELLOW}⚠ Redis is not running (optional but recommended)${NC}"
    echo "  Start with: brew services start redis (macOS)"
fi

# Check Python dependencies
echo ""
echo "Checking Python dependencies..."
cd backend
source venv/bin/activate

python -c "import redis" 2>/dev/null
check "Redis Python package"

python -c "import hiredis" 2>/dev/null
check "Hiredis package"

python -c "import apscheduler" 2>/dev/null
check "APScheduler package"

python -c "import sentry_sdk" 2>/dev/null
check "Sentry SDK"

python -c "import slowapi" 2>/dev/null
check "SlowAPI (rate limiting)"

# Check Phase 4 files
echo ""
echo "Checking Phase 4 implementation files..."

cd ..

[ -f "backend/app/core/cache.py" ]
check "Cache module"

[ -f "backend/app/core/database_pool.py" ]
check "Database pool module"

[ -f "backend/app/core/rate_limiter.py" ]
check "Rate limiter module"

[ -f "backend/app/core/compression.py" ]
check "Compression middleware"

[ -f "backend/app/core/monitoring.py" ]
check "Monitoring module"

[ -f "backend/app/core/scheduler.py" ]
check "Scheduler module"

[ -f "backend/app/services/ai_service.py" ]
check "AI service wrapper"

[ -f "backend/app/services/query_optimizer.py" ]
check "Query optimizer"

[ -f "backend/app/db/optimizations.sql" ]
check "Database optimizations SQL"

[ -f "frontend/src/lib/performance.ts" ]
check "Frontend performance monitoring"

[ -f "frontend/src/lib/lazy-load.tsx" ]
check "Frontend lazy loading"

# Check environment variables
echo ""
echo "Checking environment configuration..."

[ -f "backend/.env" ]
check ".env file exists"

if grep -q "REDIS_ENABLED" backend/.env; then
    echo -e "${GREEN}✓ Redis configuration present${NC}"
    ((PASS++))
else
    echo -e "${RED}✗ Redis configuration missing${NC}"
    ((FAIL++))
fi

if grep -q "CACHE_ENABLED" backend/.env; then
    echo -e "${GREEN}✓ Cache configuration present${NC}"
    ((PASS++))
else
    echo -e "${RED}✗ Cache configuration missing${NC}"
    ((FAIL++))
fi

if grep -q "RATE_LIMIT_ENABLED" backend/.env; then
    echo -e "${GREEN}✓ Rate limit configuration present${NC}"
    ((PASS++))
else
    echo -e "${RED}✗ Rate limit configuration missing${NC}"
    ((FAIL++))
fi

# Summary
echo ""
echo "======================================"
echo "Verification Summary"
echo "======================================"
echo -e "Passed: ${GREEN}${PASS}${NC}"
echo -e "Failed: ${RED}${FAIL}${NC}"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}🎉 All checks passed! Phase 4 is ready to use.${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Start Redis: redis-server (if not running)"
    echo "2. Apply database optimizations: psql -d your_db -f backend/app/db/optimizations.sql"
    echo "3. Start backend: cd backend && uvicorn app.main:app --reload"
    echo "4. Check health: curl http://localhost:8000/api/health/detailed"
    exit 0
else
    echo -e "${RED}⚠️  Some checks failed. Please review and fix the issues.${NC}"
    exit 1
fi
