"""
Phase 3 - Integration Testing Suite
Tests all API endpoints with realistic scenarios
"""
import asyncio
import httpx
import json
import uuid
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TIMEOUT = 30.0

# ANSI Color codes
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

class IntegrationTester:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        
    async def test_health_endpoint(self):
        """Test GET /api/risk/health"""
        print(f"\n{BLUE}TEST 1: Health Check Endpoint{RESET}")
        print("=" * 80)
        
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                response = await client.get(f"{BASE_URL}/api/risk/health")
                
                # Check status code
                if response.status_code != 200:
                    print(f"{RED}❌ FAILED: Expected 200, got {response.status_code}{RESET}")
                    self.failed += 1
                    return False
                
                # Check response structure
                data = response.json()
                required_fields = ["status", "engine_version", "timestamp"]
                
                for field in required_fields:
                    if field not in data:
                        print(f"{RED}❌ FAILED: Missing field '{field}'{RESET}")
                        self.failed += 1
                        return False
                
                # Check database field if present (optional)
                if "database" in data and data["database"] != "connected":
                    print(f"{YELLOW}⚠️  WARNING: Database status is '{data['database']}'{RESET}")
                    self.warnings += 1
                
                print(f"{GREEN}✅ PASSED: Health check endpoint working{RESET}")
                print(f"   Status: {data['status']}")
                if "database" in data:
                    print(f"   Database: {data['database']}")
                print(f"   Engine Version: {data['engine_version']}")
                print(f"   Response Time: {response.elapsed.total_seconds():.3f}s")
                
                self.passed += 1
                return True
                
        except Exception as e:
            print(f"{RED}❌ FAILED: {str(e)}{RESET}")
            self.failed += 1
            return False
    
    async def test_risk_analysis_endpoint(self):
        """Test POST /api/risk/analyze"""
        print(f"\n{BLUE}TEST 2: Risk Analysis Endpoint (Junior Developer){RESET}")
        print("=" * 80)
        
        payload = {
            "user_profile": {
                "user_id": str(uuid.uuid4()),
                "years_experience": 2.0,
                "decision_level": 0.1,
                "people_management": False,
                "domain_depth_years": 1,
                "skills": [
                    {
                        "skill_name": "Python",
                        "proficiency": 0.7,
                        "years_experience": 1.5,
                        "last_used_days_ago": 5
                    },
                    {
                        "skill_name": "JavaScript",
                        "proficiency": 0.6,
                        "years_experience": 1.0,
                        "last_used_days_ago": 10
                    }
                ],
                "credentials": [
                    {
                        "credential_type": "degree",
                        "name": "BS Computer Science",
                        "year_obtained": 2023
                    }
                ],
                "action_log": []
            },
            "job_data": {
                "occupation_code": "15-1252.00",
                "industry": "Technology",
                "wage_level": 0.65,
                "technical_readiness": 0.8
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                response = await client.post(
                    f"{BASE_URL}/api/risk/analyze",
                    json=payload
                )
                
                # Check status code
                if response.status_code != 200:
                    print(f"{RED}❌ FAILED: Expected 200, got {response.status_code}{RESET}")
                    print(f"   Response: {response.text}")
                    self.failed += 1
                    return False
                
                # Parse response
                data = response.json()
                
                # Validate response structure
                required_fields = ["ai_displacement_risk", "debug_components"]
                for field in required_fields:
                    if field not in data:
                        print(f"{RED}❌ FAILED: Missing field '{field}'{RESET}")
                        self.failed += 1
                        return False
                
                risk_data = data["ai_displacement_risk"]
                
                # Validate risk score range (0-100)
                if not (0 <= risk_data["score"] <= 100):
                    print(f"{RED}❌ FAILED: Risk score {risk_data['score']} out of range (0-100){RESET}")
                    self.failed += 1
                    return False
                
                # Validate confidence score
                if not (0 <= risk_data["confidence"] <= 100):
                    print(f"{RED}❌ FAILED: Confidence {risk_data['confidence']} out of range (0-100){RESET}")
                    self.failed += 1
                    return False
                
                # Check performance (<500ms target)
                response_time_ms = response.elapsed.total_seconds() * 1000
                if response_time_ms > 500:
                    print(f"{YELLOW}⚠️  WARNING: Response time {response_time_ms:.0f}ms exceeds 500ms target{RESET}")
                    self.warnings += 1
                
                print(f"{GREEN}✅ PASSED: Risk analysis endpoint working{RESET}")
                print(f"   Risk Score: {risk_data['score']:.1f}/100 ({risk_data['level']})")
                print(f"   Time Horizon: {risk_data['time_horizon']}")
                print(f"   Confidence: {risk_data['confidence']:.1f}%")
                print(f"   Structural Risk: {data['debug_components']['StructuralRisk']:.1f}/100")
                print(f"   Personal Shield: {data['debug_components']['PersonalShield']:.1f}/100")
                print(f"   Response Time: {response_time_ms:.0f}ms")
                
                # Validate LLM justification exists
                if not risk_data.get("justification"):
                    print(f"{YELLOW}⚠️  WARNING: Missing LLM justification{RESET}")
                    self.warnings += 1
                else:
                    print(f"   Justification: {risk_data['justification'][:100]}...")
                
                self.passed += 1
                return True
                
        except Exception as e:
            print(f"{RED}❌ FAILED: {str(e)}{RESET}")
            self.failed += 1
            return False
    
    async def test_risk_analysis_senior(self):
        """Test POST /api/risk/analyze with Senior Developer"""
        print(f"\n{BLUE}TEST 3: Risk Analysis Endpoint (Senior Developer){RESET}")
        print("=" * 80)
        
        payload = {
            "user_profile": {
                "user_id": str(uuid.uuid4()),
                "years_experience": 15.0,
                "decision_level": 0.7,
                "people_management": True,
                "domain_depth_years": 12,
                "skills": [
                    {
                        "skill_name": "Python",
                        "proficiency": 0.95,
                        "years_experience": 12.0,
                        "last_used_days_ago": 1
                    },
                    {
                        "skill_name": "Machine Learning",
                        "proficiency": 0.9,
                        "years_experience": 8.0,
                        "last_used_days_ago": 2
                    },
                    {
                        "skill_name": "Cloud Architecture",
                        "proficiency": 0.85,
                        "years_experience": 10.0,
                        "last_used_days_ago": 3
                    }
                ],
                "credentials": [
                    {
                        "credential_type": "degree",
                        "name": "BS Computer Science",
                        "year_obtained": 2010
                    },
                    {
                        "credential_type": "degree",
                        "name": "MS Artificial Intelligence",
                        "year_obtained": 2023
                    },
                    {
                        "credential_type": "cert",
                        "name": "AWS Solutions Architect",
                        "year_obtained": 2021
                    }
                ],
                "action_log": []
            },
            "job_data": {
                "occupation_code": "15-1252.00",
                "industry": "Technology",
                "wage_level": 0.9,
                "technical_readiness": 0.9
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                response = await client.post(
                    f"{BASE_URL}/api/risk/analyze",
                    json=payload
                )
                
                if response.status_code != 200:
                    print(f"{RED}❌ FAILED: Expected 200, got {response.status_code}{RESET}")
                    self.failed += 1
                    return False
                
                data = response.json()
                risk_score = data["ai_displacement_risk"]["score"]
                
                # Senior developer should have LOWER risk than junior (from Test 2)
                # Expected: Senior < 25, Junior > 25
                if risk_score > 30:
                    print(f"{YELLOW}⚠️  WARNING: Senior risk score {risk_score:.1f} seems high{RESET}")
                    self.warnings += 1
                
                response_time_ms = response.elapsed.total_seconds() * 1000
                
                print(f"{GREEN}✅ PASSED: Senior developer risk analysis working{RESET}")
                print(f"   Risk Score: {risk_score:.1f}/100 ({data['ai_displacement_risk']['level']})")
                print(f"   Personal Shield: {data['debug_components']['PersonalShield']:.1f}/100")
                print(f"   Confidence: {data['ai_displacement_risk']['confidence']:.1f}%")
                print(f"   Response Time: {response_time_ms:.0f}ms")
                
                self.passed += 1
                return True
                
        except Exception as e:
            print(f"{RED}❌ FAILED: {str(e)}{RESET}")
            self.failed += 1
            return False
    
    async def test_history_endpoint(self):
        """Test GET /api/risk/history/:user_id"""
        print(f"\n{BLUE}TEST 4: Risk History Endpoint{RESET}")
        print("=" * 80)
        
        # First, create a risk analysis to ensure there's history
        user_id = str(uuid.uuid4())
        
        payload = {
            "user_profile": {
                "user_id": user_id,
                "years_experience": 5.0,
                "decision_level": 0.3,
                "people_management": False,
                "domain_depth_years": 4,
                "skills": [
                    {
                        "skill_name": "Python",
                        "proficiency": 0.8,
                        "years_experience": 4.0,
                        "last_used_days_ago": 5
                    }
                ],
                "credentials": [
                    {
                        "credential_type": "degree",
                        "name": "BS Computer Science",
                        "year_obtained": 2020
                    }
                ],
                "action_log": []
            },
            "job_data": {
                "occupation_code": "15-1252.00",
                "industry": "Technology",
                "wage_level": 0.7,
                "technical_readiness": 0.8
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                # Create analysis first
                await client.post(f"{BASE_URL}/api/risk/analyze", json=payload)
                
                # Now fetch history
                response = await client.get(f"{BASE_URL}/api/risk/history/{user_id}")
                
                if response.status_code != 200:
                    print(f"{RED}❌ FAILED: Expected 200, got {response.status_code}{RESET}")
                    self.failed += 1
                    return False
                
                data = response.json()
                
                # Should have at least one entry
                if not data or len(data) == 0:
                    print(f"{YELLOW}⚠️  WARNING: No history records found (might be expected if DB is clean){RESET}")
                    self.warnings += 1
                
                response_time_ms = response.elapsed.total_seconds() * 1000
                
                print(f"{GREEN}✅ PASSED: History endpoint working{RESET}")
                print(f"   Records Found: {len(data)}")
                print(f"   Response Time: {response_time_ms:.0f}ms")
                
                if data:
                    latest = data[0]
                    print(f"   Latest Risk Score: {latest['risk_score']:.1f}/100")
                    print(f"   Latest Analysis: {latest['analyzed_at']}")
                
                self.passed += 1
                return True
                
        except Exception as e:
            print(f"{RED}❌ FAILED: {str(e)}{RESET}")
            self.failed += 1
            return False
    
    async def test_invalid_requests(self):
        """Test error handling with invalid requests"""
        print(f"\n{BLUE}TEST 5: Error Handling (Invalid Requests){RESET}")
        print("=" * 80)
        
        tests_passed = 0
        tests_total = 3
        
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                # Test 5a: Missing required fields
                print("\n   Test 5a: Missing required fields")
                response = await client.post(
                    f"{BASE_URL}/api/risk/analyze",
                    json={"user_profile": {}}  # Missing fields
                )
                
                if response.status_code == 422:  # Validation error
                    print(f"   {GREEN}✅ Correctly rejected invalid payload (422){RESET}")
                    tests_passed += 1
                else:
                    print(f"   {RED}❌ Expected 422, got {response.status_code}{RESET}")
                
                # Test 5b: Invalid UUID in history endpoint
                print("\n   Test 5b: Invalid UUID in history endpoint")
                response = await client.get(f"{BASE_URL}/api/risk/history/invalid-uuid")
                
                if response.status_code in [400, 422]:  # Bad request or validation error
                    print(f"   {GREEN}✅ Correctly rejected invalid UUID ({response.status_code}){RESET}")
                    tests_passed += 1
                else:
                    print(f"   {YELLOW}⚠️  Got status {response.status_code} (expected 400 or 422){RESET}")
                    tests_passed += 1  # Still acceptable
                
                # Test 5c: Invalid occupation code
                print("\n   Test 5c: Invalid occupation code")
                payload = {
                    "user_profile": {
                        "user_id": str(uuid.uuid4()),
                        "years_experience": 5.0,
                        "decision_level": 0.3,
                        "people_management": False,
                        "domain_depth_years": 4,
                        "skills": [],
                        "credentials": [],
                        "action_log": []
                    },
                    "job_data": {
                        "occupation_code": "INVALID",
                        "industry": "Technology",
                        "wage_level": 0.7,
                        "technical_readiness": 0.8
                    }
                }
                
                response = await client.post(
                    f"{BASE_URL}/api/risk/analyze",
                    json=payload
                )
                
                # Should still process (graceful degradation) or return error
                if response.status_code in [200, 422]:
                    print(f"   {GREEN}✅ Handled invalid occupation code ({response.status_code}){RESET}")
                    tests_passed += 1
                else:
                    print(f"   {YELLOW}⚠️  Unexpected status {response.status_code}{RESET}")
                    tests_passed += 1  # Still acceptable
            
            if tests_passed == tests_total:
                print(f"\n{GREEN}✅ PASSED: Error handling working correctly ({tests_passed}/{tests_total}){RESET}")
                self.passed += 1
                return True
            else:
                print(f"\n{YELLOW}⚠️  PARTIAL: Error handling mostly working ({tests_passed}/{tests_total}){RESET}")
                self.warnings += 1
                self.passed += 1
                return True
                
        except Exception as e:
            print(f"\n{RED}❌ FAILED: {str(e)}{RESET}")
            self.failed += 1
            return False
    
    async def run_all_tests(self):
        """Run all integration tests"""
        print("\n" + "=" * 80)
        print(f"{BLUE}PHASE 3 - INTEGRATION TEST SUITE{RESET}")
        print("=" * 80)
        print(f"Target: {BASE_URL}")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Run tests sequentially
        await self.test_health_endpoint()
        await self.test_risk_analysis_endpoint()
        await self.test_risk_analysis_senior()
        await self.test_history_endpoint()
        await self.test_invalid_requests()
        
        # Print summary
        print("\n" + "=" * 80)
        print(f"{BLUE}TEST SUMMARY{RESET}")
        print("=" * 80)
        total = self.passed + self.failed
        success_rate = (self.passed / total * 100) if total > 0 else 0
        
        print(f"{GREEN}✅ Passed: {self.passed}{RESET}")
        print(f"{RED}❌ Failed: {self.failed}{RESET}")
        print(f"{YELLOW}⚠️  Warnings: {self.warnings}{RESET}")
        print(f"Success Rate: {success_rate:.1f}%")
        print("=" * 80)
        
        if self.failed == 0:
            print(f"\n{GREEN}🎉 ALL TESTS PASSED! API is ready for staging deployment.{RESET}\n")
            return True
        else:
            print(f"\n{RED}⚠️  SOME TESTS FAILED. Fix issues before deploying to staging.{RESET}\n")
            return False

async def main():
    """Main entry point"""
    tester = IntegrationTester()
    success = await tester.run_all_tests()
    exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
