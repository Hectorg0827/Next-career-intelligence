"""
Test API endpoints for AI Displacement Risk Engine v1.0

Tests both /api/risk/analyze and /api/risk/history endpoints.
"""

import requests
import json
from datetime import datetime


BASE_URL = "http://localhost:8000/api/risk"


def test_health_check():
    """Test the health check endpoint"""
    print("=" * 80)
    print("TEST 1: Health Check")
    print("=" * 80)
    
    response = requests.get(f"{BASE_URL}/health")
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert data['status'] == 'healthy', "Engine should be healthy"
    assert data['engine_version'] == '1.0', "Should be version 1.0"
    
    print("✅ Health check passed\n")


def test_analyze_endpoint():
    """Test the analyze endpoint with sample data"""
    print("=" * 80)
    print("TEST 2: POST /api/risk/analyze")
    print("=" * 80)
    
    # Sample request payload
    request_data = {
        "user_profile": {
            "user_id": "550e8400-e29b-41d4-a716-446655440099",
            "years_experience": 8,
            "people_management": False,
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
                },
                {
                    "skill_name": "API Development",
                    "proficiency": 0.7,
                    "years_experience": 4.0,
                    "last_used_days_ago": 1
                }
            ],
            "credentials": [
                {
                    "credential_type": "degree",
                    "name": "BS Computer Science",
                    "year_obtained": 2016
                },
                {
                    "credential_type": "cert",
                    "name": "AWS Certified Developer",
                    "year_obtained": 2023
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
    }
    
    print(f"Request Payload:")
    print(json.dumps(request_data, indent=2))
    print()
    
    response = requests.post(
        f"{BASE_URL}/analyze",
        json=request_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        risk = data['ai_displacement_risk']
        debug = data['debug_components']
        
        print("\n" + "=" * 80)
        print("RISK ANALYSIS RESULTS")
        print("=" * 80)
        print(f"\n📊 Risk Score: {risk['score']}/100 ({risk['level']})")
        print(f"⏰ Time Horizon: {risk['time_horizon']}")
        print(f"🎯 Confidence: {risk['confidence']}/100")
        print(f"📈 Percentile: {risk['percentile_vs_role']}")
        print(f"📉 Trajectory: {risk['trajectory']}")
        
        print(f"\n💭 Justification:")
        print(risk['justification'][:200] + "...")
        
        print(f"\n⚠️  Vulnerabilities ({len(risk['primary_vulnerabilities'])}):")
        for i, vuln in enumerate(risk['primary_vulnerabilities'][:3], 1):
            print(f"  {i}. {vuln[:100]}...")
        
        print(f"\n✨ Opportunities ({len(risk['protection_opportunities'])}):")
        for i, opp in enumerate(risk['protection_opportunities'][:3], 1):
            print(f"  {i}. {opp[:100]}...")
        
        print(f"\n🔍 Debug Components:")
        print(f"  StructuralRisk: {debug['StructuralRisk']}/100")
        print(f"  PersonalShield: {debug['PersonalShield']}/100")
        print(f"  TAS: {debug['TAS']}/100")
        print(f"  IVS: {debug['IVS']}/100")
        print(f"  PSC: {debug['PSC']}/100")
        print(f"  AS: {debug['AS']}/100")
        
        print("\n✅ Analyze endpoint test passed\n")
        return True
    else:
        print(f"❌ Error: {response.text}")
        return False


def test_history_endpoint():
    """Test the history endpoint"""
    print("=" * 80)
    print("TEST 3: GET /api/risk/history/:user_id")
    print("=" * 80)
    
    user_id = "550e8400-e29b-41d4-a716-446655440099"
    
    response = requests.get(f"{BASE_URL}/history/{user_id}?limit=10")
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        print(f"Found {len(data)} historical analyses")
        
        if len(data) > 0:
            print("\nMost recent analysis:")
            latest = data[0]
            print(f"  Risk Score: {latest['ai_displacement_risk']['score']}/100")
            print(f"  Level: {latest['ai_displacement_risk']['level']}")
            print(f"  Calculated At: {latest['calculated_at']}")
        
        print("\n✅ History endpoint test passed\n")
        return True
    else:
        print(f"Response: {response.text}")
        if response.status_code == 404:
            print("⚠️  No history found (expected for new user)")
            return True
        return False


def test_invalid_request():
    """Test error handling with invalid data"""
    print("=" * 80)
    print("TEST 4: Error Handling (Invalid Request)")
    print("=" * 80)
    
    # Missing required fields
    invalid_data = {
        "user_profile": {
            "user_id": "test",
            "skills": []
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/analyze",
        json=invalid_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 422, "Should return 422 for validation error"
    print("\n✅ Error handling test passed\n")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("AI DISPLACEMENT RISK API TESTS")
    print("=" * 80)
    print("Testing endpoints at:", BASE_URL)
    print("Make sure the API server is running: python3 -m uvicorn app.main:app --reload")
    print("=" * 80 + "\n")
    
    try:
        # Run tests
        test_health_check()
        test_analyze_endpoint()
        test_history_endpoint()
        test_invalid_request()
        
        print("=" * 80)
        print("✅ ALL TESTS PASSED")
        print("=" * 80)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to API server")
        print("Make sure the server is running:")
        print("  cd backend && python3 -m uvicorn app.main:app --reload")
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
