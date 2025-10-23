#!/bin/bash

# Phase 3 Testing Script
# This script runs automated tests for Phase 3 implementation

set -e

echo "🧪 PHASE 3 TEST EXECUTION SUITE"
echo "================================"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_BLOCKED=0

# Logging function
log_test() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

log_pass() {
    echo -e "${GREEN}[✓ PASS]${NC} $1"
    ((TESTS_PASSED++))
}

log_fail() {
    echo -e "${RED}[✗ FAIL]${NC} $1"
    ((TESTS_FAILED++))
}

log_block() {
    echo -e "${YELLOW}[⊘ BLOCKED]${NC} $1"
    ((TESTS_BLOCKED++))
}

# ============================================
# SETUP VERIFICATION
# ============================================
echo -e "${BLUE}=== SETUP VERIFICATION ===${NC}"
echo ""

# Test 1: Backend health
log_test "Backend health check"
BACKEND_HEALTH=$(curl -s http://localhost:8000/api/v1/health 2>&1 || echo "FAIL")
if echo "$BACKEND_HEALTH" | grep -q "healthy"; then
    log_pass "Backend running and healthy"
else
    log_fail "Backend not responding or unhealthy"
fi

# Test 2: Frontend check
log_test "Frontend server check"
FRONTEND_CHECK=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>&1)
if [ "$FRONTEND_CHECK" = "200" ]; then
    log_pass "Frontend running on port 3000"
else
    log_fail "Frontend not responding (HTTP $FRONTEND_CHECK)"
fi

echo ""

# ============================================
# API INTEGRATION TESTS
# ============================================
echo -e "${BLUE}=== API INTEGRATION TESTS ===${NC}"
echo ""

# Get test user's Firebase UID (from environment or use test value)
# In a real scenario, this would be obtained from login
TEST_UID="test-user-$(date +%s)"

# Test 3: Create conversation via API
log_test "Create new conversation (API)"
CREATE_RESPONSE=$(curl -s -X POST http://localhost:8000/api/coach/conversations \
  -H "Content-Type: application/json" \
  -d "{
    \"firebase_uid\": \"$TEST_UID\",
    \"title\": \"Test Conversation\",
    \"career_context\": \"Software Engineer\"
  }" 2>&1)

if echo "$CREATE_RESPONSE" | grep -q "conversation_id\|id"; then
    CONVERSATION_ID=$(echo "$CREATE_RESPONSE" | grep -o '"id":"[^"]*"' | cut -d'"' -f4 | head -1)
    if [ -z "$CONVERSATION_ID" ]; then
        CONVERSATION_ID=$(echo "$CREATE_RESPONSE" | grep -o '"conversation_id":"[^"]*"' | cut -d'"' -f4 | head -1)
    fi
    log_pass "Conversation created (ID: ${CONVERSATION_ID:0:8}...)"
else
    log_fail "Failed to create conversation: $CREATE_RESPONSE"
    CONVERSATION_ID=""
fi

echo ""

# Test 4: List conversations via API
log_test "List conversations (API)"
LIST_RESPONSE=$(curl -s "http://localhost:8000/api/coach/conversations?firebase_uid=$TEST_UID" 2>&1)

if echo "$LIST_RESPONSE" | grep -q "\[\|conversations"; then
    log_pass "Conversations list retrieved"
else
    log_fail "Failed to list conversations"
fi

echo ""

# Test 5: Get specific conversation via API
log_test "Get conversation details (API)"
if [ -n "$CONVERSATION_ID" ]; then
    GET_RESPONSE=$(curl -s "http://localhost:8000/api/coach/conversations/$CONVERSATION_ID?firebase_uid=$TEST_UID" 2>&1)
    
    if echo "$GET_RESPONSE" | grep -q "conversation_id\|id\|title"; then
        log_pass "Conversation details retrieved"
    else
        log_fail "Failed to retrieve conversation details"
    fi
else
    log_block "Skipped - no conversation ID from previous test"
fi

echo ""

# Test 6: Archive conversation via API
log_test "Archive conversation (API)"
if [ -n "$CONVERSATION_ID" ]; then
    ARCHIVE_RESPONSE=$(curl -s -X PUT "http://localhost:8000/api/coach/conversations/$CONVERSATION_ID/archive?firebase_uid=$TEST_UID" 2>&1)
    
    if echo "$ARCHIVE_RESPONSE" | grep -q "archived\|success"; then
        log_pass "Conversation archived successfully"
    else
        log_fail "Failed to archive conversation"
    fi
else
    log_block "Skipped - no conversation ID from previous test"
fi

echo ""

# ============================================
# FRONTEND NAVIGATION TESTS
# ============================================
echo -e "${BLUE}=== FRONTEND NAVIGATION TESTS ===${NC}"
echo ""

# Test 7: Coach chat page accessible
log_test "Coach chat page (/coach/chat)"
CHAT_PAGE=$(curl -s http://localhost:3000/coach/chat 2>&1 | grep -o "coach\|chat" | head -1)
if [ "$CHAT_PAGE" != "" ]; then
    log_pass "Chat page loads successfully"
else
    log_fail "Chat page failed to load"
fi

echo ""

# Test 8: Conversations list page accessible
log_test "Conversations list page (/coach/conversations)"
CONV_PAGE=$(curl -s http://localhost:3000/coach/conversations 2>&1 | grep -o "conversation" | head -1)
if [ "$CONV_PAGE" != "" ]; then
    log_pass "Conversations list page loads successfully"
else
    log_fail "Conversations list page failed to load"
fi

echo ""

# ============================================
# DATABASE CONNECTIVITY TESTS
# ============================================
echo -e "${BLUE}=== DATABASE CONNECTIVITY TESTS ===${NC}"
echo ""

# Test 9: Database connection
log_test "Database connectivity"
DB_CHECK=$(curl -s -X GET http://localhost:8000/api/v1/health 2>&1 | grep -o "healthy\|error" | head -1)
if [ "$DB_CHECK" = "healthy" ]; then
    log_pass "Database connected and healthy"
else
    log_fail "Database connectivity issue"
fi

echo ""

# ============================================
# TEST SUMMARY
# ============================================
echo -e "${BLUE}========== TEST SUMMARY ==========${NC}"
echo ""
echo -e "Tests Passed:  ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Failed:  ${RED}$TESTS_FAILED${NC}"
echo -e "Tests Blocked: ${YELLOW}$TESTS_BLOCKED${NC}"
echo ""

TOTAL_TESTS=$((TESTS_PASSED + TESTS_FAILED + TESTS_BLOCKED))
echo "Total Tests: $TOTAL_TESTS"
echo ""

# Determine overall status
if [ $TESTS_FAILED -eq 0 ] && [ $TESTS_PASSED -gt 0 ]; then
    echo -e "${GREEN}✅ ALL TESTS PASSED${NC}"
    exit 0
elif [ $TESTS_FAILED -gt 0 ]; then
    echo -e "${RED}❌ SOME TESTS FAILED${NC}"
    exit 1
else
    echo -e "${YELLOW}⚠️  NO TESTS COULD RUN${NC}"
    exit 2
fi
