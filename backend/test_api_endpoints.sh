#!/bin/bash

# Test API endpoints for AI Displacement Risk Engine

BASE_URL="http://localhost:8000/api/risk"

echo "================================================================================"
echo "AI DISPLACEMENT RISK API ENDPOINT TESTS"
echo "================================================================================"
echo ""

# Test 1: Health Check
echo "TEST 1: Health Check"
echo "--------------------"
curl -s "$BASE_URL/health" | python3 -m json.tool
echo ""
echo ""

# Test 2: POST /analyze
echo "TEST 2: POST /api/risk/analyze"
echo "-------------------------------"
curl -s -X POST "$BASE_URL/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "user_profile": {
      "user_id": "550e8400-e29b-41d4-a716-446655440099",
      "years_experience": 8,
      "people_management": false,
      "decision_level": 0.3,
      "domain_depth_years": 5,
      "skills": [
        {
          "skill_name": "Python",
          "proficiency": 0.8,
          "years_experience": 6.0,
          "last_used_days_ago": 2
        },
        {
          "skill_name": "Machine Learning",
          "proficiency": 0.6,
          "years_experience": 3.0,
          "last_used_days_ago": 10
        }
      ],
      "credentials": [
        {
          "credential_type": "degree",
          "name": "BS Computer Science",
          "year_obtained": 2016
        }
      ],
      "action_log": []
    },
    "job_data": {
      "occupation_code": "15-2051",
      "industry": "Technology",
      "wage_level": 0.75,
      "technical_readiness": 0.8
    }
  }' | python3 -m json.tool
echo ""
echo ""

# Test 3: GET /history/:user_id
echo "TEST 3: GET /api/risk/history/:user_id"
echo "---------------------------------------"
curl -s "$BASE_URL/history/550e8400-e29b-41d4-a716-446655440099?limit=5" | python3 -m json.tool
echo ""
echo ""

echo "================================================================================"
echo "✅ ALL TESTS COMPLETE"
echo "================================================================================"
