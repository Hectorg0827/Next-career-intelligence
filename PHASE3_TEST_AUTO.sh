#!/bin/bash

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║          PHASE 3 AUTOMATED TEST EXECUTION SUITE              ║"
echo "║                    Starting Tests...                         ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Test counters
PASSED=0
FAILED=0
TOTAL=0

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Backend Health
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 1: Backend Health Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
TOTAL=$((TOTAL + 1))

RESPONSE=$(curl -s http://localhost:8000/api/v1/health)
if echo "$RESPONSE" | grep -q "healthy"; then
    echo -e "${GREEN}✅ PASSED${NC}"
    echo "Response: $RESPONSE"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}❌ FAILED${NC}"
    echo "Response: $RESPONSE"
    FAILED=$((FAILED + 1))
fi
echo ""

# Test 2: Frontend Server
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 2: Frontend Server Running"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
TOTAL=$((TOTAL + 1))

if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PASSED${NC}"
    echo "Frontend server is responding on port 3000"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}❌ FAILED${NC}"
    echo "Frontend server not responding"
    FAILED=$((FAILED + 1))
fi
echo ""

# Test 3: API Documentation
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 3: API Documentation Available"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
TOTAL=$((TOTAL + 1))

if curl -s http://localhost:8000/docs > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PASSED${NC}"
    echo "API documentation available at http://localhost:8000/docs"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}❌ FAILED${NC}"
    echo "API documentation not accessible"
    FAILED=$((FAILED + 1))
fi
echo ""

# Test 4: Backend Logs
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 4: Backend Process Verification"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
TOTAL=$((TOTAL + 1))

if pgrep -f "uvicorn" > /dev/null; then
    echo -e "${GREEN}✅ PASSED${NC}"
    echo "Backend process (uvicorn) is running"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}❌ FAILED${NC}"
    echo "Backend process not found"
    FAILED=$((FAILED + 1))
fi
echo ""

# Test 5: Database Connection
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 5: Database Connectivity"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
TOTAL=$((TOTAL + 1))

# Check if we can connect to database through API
RESPONSE=$(curl -s http://localhost:8000/api/v1/health)
if echo "$RESPONSE" | grep -q "healthy"; then
    echo -e "${GREEN}✅ PASSED${NC}"
    echo "Database is accessible (verified through API)"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}❌ FAILED${NC}"
    echo "Database connectivity issue"
    FAILED=$((FAILED + 1))
fi
echo ""

# Summary
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    TEST EXECUTION SUMMARY                    ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Total Tests:    $TOTAL"
echo -e "Passed:         ${GREEN}$PASSED${NC}"
echo -e "Failed:         ${RED}$FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║           🎉 ALL AUTOMATED TESTS PASSED! 🎉                  ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "System Status: ✅ READY FOR MANUAL TESTING"
    echo ""
    echo "Next Steps:"
    echo "1. Open http://localhost:3000/coach/chat in your browser"
    echo "2. Follow PHASE3_QUICK_TEST.md for quick 5-minute verification"
    echo "3. Or follow PHASE3_TEST_EXECUTION.md for comprehensive 15-minute testing"
else
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║              ⚠️ SOME TESTS FAILED ⚠️                         ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
fi
