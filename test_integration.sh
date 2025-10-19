#!/bin/bash

# 🎉 Features 5 & 6 Integration Test Script
# This script tests the complete integration of Visual Career Maps and Industry Benchmarking

echo "================================================"
echo "🚀 NEXT Career Intelligence - Integration Test"
echo "================================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0

# Function to test endpoint
test_endpoint() {
    local name="$1"
    local url="$2"
    local data="$3"
    local check_field="$4"
    
    echo -n "Testing $name... "
    
    response=$(curl -s -X POST "$url" \
        -H "Content-Type: application/json" \
        -d "$data" 2>&1)
    
    if echo "$response" | grep -q "$check_field"; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}"
        echo "  Expected field: $check_field"
        echo "  Response preview: ${response:0:200}"
        ((TESTS_FAILED++))
        return 1
    fi
}

echo "📡 Testing Backend APIs..."
echo ""

# Test 1: Health Check
echo -n "1. Health Check... "
health=$(curl -s http://localhost:8000/api/health)
if echo "$health" | grep -q "operational\|degraded"; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((TESTS_FAILED++))
fi

# Test 2: Analyze API with industry_benchmarks
test_endpoint \
    "2. Analyze API (Feature 6 - Benchmarks)" \
    "http://localhost:8000/api/analyze" \
    '{
        "job_title": "Software Engineer",
        "skills": ["Python", "JavaScript"],
        "location": "San Francisco, CA",
        "years_experience": 5
    }' \
    "industry_benchmarks"

# Test 3: Roadmap API with sankey_data
test_endpoint \
    "3. Roadmap API (Feature 5 - Sankey)" \
    "http://localhost:8000/api/roadmap" \
    '{
        "job_title": "Software Engineer",
        "skills": ["Python", "JavaScript"],
        "location": "San Francisco, CA",
        "years_experience": 5,
        "timeline": "5 years"
    }' \
    "sankey_data"

echo ""
echo "🌐 Testing Frontend..."
echo ""

# Test 4: Home Page
echo -n "4. Home Page (http://localhost:3000)... "
if curl -s http://localhost:3000 | grep -q "Adaptive Career Intelligence"; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((TESTS_FAILED++))
fi

# Test 5: Dashboard Page
echo -n "5. Dashboard Page (/dashboard)... "
if curl -s http://localhost:3000/dashboard | grep -q "Career Analysis"; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((TESTS_FAILED++))
fi

echo ""
echo "================================================"
echo "📊 Test Results"
echo "================================================"
echo ""
echo -e "Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Failed: ${RED}$TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed! Integration successful!${NC}"
    echo ""
    echo "✅ Next Steps:"
    echo "  1. Open http://localhost:3000/dashboard"
    echo "  2. Fill in the form with your job details"
    echo "  3. Click 'Analyze Career' to see Features 1-3, 6"
    echo "  4. Click 'Generate Visual Roadmap' to see Feature 5"
    echo "  5. Explore all interactive components!"
    echo ""
    exit 0
else
    echo -e "${YELLOW}⚠️  Some tests failed. Check output above.${NC}"
    echo ""
    echo "Common Issues:"
    echo "  - Backend not running: cd backend && python3 -m uvicorn app.main:app --reload"
    echo "  - Frontend not running: cd frontend && npm run dev"
    echo "  - Wrong port: Check that backend=8000, frontend=3000"
    echo ""
    exit 1
fi
