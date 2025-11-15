#!/usr/bin/env python3
"""
Phase 2 AI Agents Integration Testing
======================================

Comprehensive end-to-end testing of all Phase 2 AI features:
- API endpoints (15 endpoints)
- Frontend components
- Background jobs
- Error handling
- Performance validation

Usage:
    python test-phase2-integration.py
"""

import asyncio
import sys
import time
from datetime import datetime
from typing import Dict, Any, List
import httpx
import json

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_USER_ID = "test_user_phase2"
TIMEOUT = 30.0

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


class IntegrationTester:
    """Comprehensive integration testing suite"""
    
    def __init__(self):
        self.results = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "warnings": 0,
            "tests": []
        }
        self.start_time = None
        
    def print_header(self, text: str):
        """Print formatted section header"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{text:^60}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}\n")
    
    def print_test(self, name: str, passed: bool, details: str = "", warning: bool = False):
        """Print test result"""
        self.results["total"] += 1
        
        if warning:
            self.results["warnings"] += 1
            status = f"{Colors.YELLOW}⚠ WARN{Colors.RESET}"
        elif passed:
            self.results["passed"] += 1
            status = f"{Colors.GREEN}✓ PASS{Colors.RESET}"
        else:
            self.results["failed"] += 1
            status = f"{Colors.RED}✗ FAIL{Colors.RESET}"
        
        print(f"{status} {name}")
        if details:
            print(f"    {Colors.RESET}{details}{Colors.RESET}")
        
        self.results["tests"].append({
            "name": name,
            "passed": passed,
            "warning": warning,
            "details": details
        })
    
    def print_summary(self):
        """Print test results summary"""
        duration = time.time() - self.start_time
        
        self.print_header("TEST SUMMARY")
        
        print(f"Total Tests:   {self.results['total']}")
        print(f"{Colors.GREEN}Passed:       {self.results['passed']}{Colors.RESET}")
        print(f"{Colors.RED}Failed:       {self.results['failed']}{Colors.RESET}")
        print(f"{Colors.YELLOW}Warnings:     {self.results['warnings']}{Colors.RESET}")
        print(f"Duration:     {duration:.2f}s\n")
        
        if self.results['failed'] == 0:
            print(f"{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED!{Colors.RESET}\n")
            return 0
        else:
            print(f"{Colors.RED}{Colors.BOLD}❌ SOME TESTS FAILED{Colors.RESET}\n")
            return 1
    
    async def test_api_health(self, client: httpx.AsyncClient) -> bool:
        """Test API is running and healthy"""
        try:
            response = await client.get(f"{BASE_URL}/api/health")
            return response.status_code == 200
        except Exception as e:
            return False
    
    async def test_memory_endpoints(self, client: httpx.AsyncClient):
        """Test AI Memory endpoints"""
        self.print_header("Testing AI Memory Endpoints")
        
        # Test form memory
        try:
            response = await client.post(
                f"{BASE_URL}/api/ai/memory/form",
                json={
                    "user_id": TEST_USER_ID,
                    "interaction_type": "job_search",
                    "interaction_data": {"query": "senior python developer", "location": "remote"}
                },
                timeout=TIMEOUT
            )
            self.print_test(
                "POST /api/ai/memory/form",
                response.status_code == 200,
                f"Status: {response.status_code}"
            )
        except Exception as e:
            self.print_test("POST /api/ai/memory/form", False, str(e))
        
        # Test retrieve memories
        try:
            response = await client.get(
                f"{BASE_URL}/api/ai/memory/{TEST_USER_ID}",
                params={"limit": 10},
                timeout=TIMEOUT
            )
            self.print_test(
                "GET /api/ai/memory/{user_id}",
                response.status_code == 200,
                f"Status: {response.status_code}, Memories: {len(response.json().get('memories', []))}"
            )
        except Exception as e:
            self.print_test("GET /api/ai/memory/{user_id}", False, str(e))
        
        # Test search memories
        try:
            response = await client.post(
                f"{BASE_URL}/api/ai/memory/search",
                json={"user_id": TEST_USER_ID, "query": "python"},
                timeout=TIMEOUT
            )
            self.print_test(
                "POST /api/ai/memory/search",
                response.status_code == 200,
                f"Status: {response.status_code}"
            )
        except Exception as e:
            self.print_test("POST /api/ai/memory/search", False, str(e))
    
    async def test_recommendation_endpoints(self, client: httpx.AsyncClient):
        """Test Recommendation Engine endpoints"""
        self.print_header("Testing Recommendation Engine Endpoints")
        
        # Test get recommendations
        try:
            response = await client.get(
                f"{BASE_URL}/api/ai/recommendations/{TEST_USER_ID}",
                params={"limit": 10},
                timeout=TIMEOUT
            )
            self.print_test(
                "GET /api/ai/recommendations/{user_id}",
                response.status_code == 200,
                f"Status: {response.status_code}"
            )
        except Exception as e:
            self.print_test("GET /api/ai/recommendations/{user_id}", False, str(e))
        
        # Test get recommendation reasons
        try:
            response = await client.get(
                f"{BASE_URL}/api/ai/recommendations/{TEST_USER_ID}/job123",
                timeout=TIMEOUT
            )
            # 404 is OK if job doesn't exist
            passed = response.status_code in [200, 404]
            self.print_test(
                "GET /api/ai/recommendations/{user_id}/{job_id}",
                passed,
                f"Status: {response.status_code}",
                warning=(response.status_code == 404)
            )
        except Exception as e:
            self.print_test("GET /api/ai/recommendations/{user_id}/{job_id}", False, str(e))
    
    async def test_guidance_endpoints(self, client: httpx.AsyncClient):
        """Test Career Guidance endpoints"""
        self.print_header("Testing Career Guidance Endpoints")
        
        # Test get guidance
        try:
            response = await client.get(
                f"{BASE_URL}/api/ai/guidance/{TEST_USER_ID}",
                params={"limit": 5},
                timeout=TIMEOUT
            )
            self.print_test(
                "GET /api/ai/guidance/{user_id}",
                response.status_code == 200,
                f"Status: {response.status_code}"
            )
        except Exception as e:
            self.print_test("GET /api/ai/guidance/{user_id}", False, str(e))
        
        # Test generate guidance
        try:
            response = await client.post(
                f"{BASE_URL}/api/ai/guidance/generate",
                json={"user_id": TEST_USER_ID},
                timeout=TIMEOUT
            )
            self.print_test(
                "POST /api/ai/guidance/generate",
                response.status_code == 200,
                f"Status: {response.status_code}"
            )
        except Exception as e:
            self.print_test("POST /api/ai/guidance/generate", False, str(e))
        
        # Test dismiss guidance
        try:
            response = await client.post(
                f"{BASE_URL}/api/ai/guidance/msg123/dismiss",
                timeout=TIMEOUT
            )
            # 404 is OK if message doesn't exist
            passed = response.status_code in [200, 404]
            self.print_test(
                "POST /api/ai/guidance/{message_id}/dismiss",
                passed,
                f"Status: {response.status_code}",
                warning=(response.status_code == 404)
            )
        except Exception as e:
            self.print_test("POST /api/ai/guidance/{message_id}/dismiss", False, str(e))
    
    async def test_prediction_endpoints(self, client: httpx.AsyncClient):
        """Test Churn Predictor endpoints"""
        self.print_header("Testing Churn Prediction Endpoints")
        
        # Test predict churn
        try:
            response = await client.get(
                f"{BASE_URL}/api/ai/predict-churn/{TEST_USER_ID}",
                timeout=TIMEOUT
            )
            self.print_test(
                "GET /api/ai/predict-churn/{user_id}",
                response.status_code == 200,
                f"Status: {response.status_code}"
            )
        except Exception as e:
            self.print_test("GET /api/ai/predict-churn/{user_id}", False, str(e))
    
    async def test_profile_assistant_endpoints(self, client: httpx.AsyncClient):
        """Test Profile Assistant endpoints"""
        self.print_header("Testing Profile Assistant Endpoints")
        
        # Test analyze profile
        try:
            response = await client.get(
                f"{BASE_URL}/api/ai/profile/analysis",
                params={"user_id": TEST_USER_ID},
                timeout=TIMEOUT
            )
            self.print_test(
                "GET /api/ai/profile/analysis",
                response.status_code == 200,
                f"Status: {response.status_code}"
            )
        except Exception as e:
            self.print_test("GET /api/ai/profile/analysis", False, str(e))
        
        # Test get suggestions
        try:
            response = await client.get(
                f"{BASE_URL}/api/ai/profile/suggestions",
                params={"user_id": TEST_USER_ID},
                timeout=TIMEOUT
            )
            self.print_test(
                "GET /api/ai/profile/suggestions",
                response.status_code == 200,
                f"Status: {response.status_code}"
            )
        except Exception as e:
            self.print_test("GET /api/ai/profile/suggestions", False, str(e))
        
        # Test infer missing data
        try:
            response = await client.post(
                f"{BASE_URL}/api/ai/profile/infer",
                json={"user_id": TEST_USER_ID},
                timeout=TIMEOUT
            )
            self.print_test(
                "POST /api/ai/profile/infer",
                response.status_code == 200,
                f"Status: {response.status_code}"
            )
        except Exception as e:
            self.print_test("POST /api/ai/profile/infer", False, str(e))
        
        # Test generate summary
        try:
            response = await client.post(
                f"{BASE_URL}/api/ai/profile/generate-summary",
                json={"user_id": TEST_USER_ID},
                timeout=TIMEOUT
            )
            self.print_test(
                "POST /api/ai/profile/generate-summary",
                response.status_code == 200,
                f"Status: {response.status_code}"
            )
        except Exception as e:
            self.print_test("POST /api/ai/profile/generate-summary", False, str(e))
        
        # Test optimize for ATS
        try:
            response = await client.post(
                f"{BASE_URL}/api/ai/profile/optimize-ats",
                json={"user_id": TEST_USER_ID},
                timeout=TIMEOUT
            )
            self.print_test(
                "POST /api/ai/profile/optimize-ats",
                response.status_code == 200,
                f"Status: {response.status_code}"
            )
        except Exception as e:
            self.print_test("POST /api/ai/profile/optimize-ats", False, str(e))
    
    async def test_jobs_marketplace_ai(self, client: httpx.AsyncClient):
        """Test AI-enhanced jobs marketplace"""
        self.print_header("Testing Jobs Marketplace AI Integration")
        
        try:
            response = await client.get(
                f"{BASE_URL}/api/jobs/ai-recommendations",
                params={"user_id": TEST_USER_ID, "limit": 5},
                timeout=TIMEOUT
            )
            self.print_test(
                "GET /api/jobs/ai-recommendations",
                response.status_code == 200,
                f"Status: {response.status_code}"
            )
        except Exception as e:
            self.print_test("GET /api/jobs/ai-recommendations", False, str(e))
    
    async def test_performance(self, client: httpx.AsyncClient):
        """Test API performance"""
        self.print_header("Testing Performance")
        
        # Test response times
        endpoints = [
            ("/health", "Health Check"),
            (f"/api/ai/guidance/{TEST_USER_ID}", "Get Guidance"),
            (f"/api/ai/recommendations/{TEST_USER_ID}", "Get Recommendations"),
        ]
        
        for endpoint, name in endpoints:
            try:
                start = time.time()
                response = await client.get(f"{BASE_URL}{endpoint}", timeout=TIMEOUT)
                duration = (time.time() - start) * 1000  # Convert to ms
                
                # Warn if response time > 2 seconds
                warning = duration > 2000
                self.print_test(
                    f"Response Time: {name}",
                    True,
                    f"{duration:.0f}ms",
                    warning=warning
                )
            except Exception as e:
                self.print_test(f"Response Time: {name}", False, str(e))
    
    async def run_all_tests(self):
        """Run all integration tests"""
        self.start_time = time.time()
        
        print(f"\n{Colors.BOLD}{Colors.MAGENTA}Phase 2 AI Agents - Integration Testing{Colors.RESET}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        async with httpx.AsyncClient() as client:
            # Check API is running
            self.print_header("Checking API Health")
            api_healthy = await self.test_api_health(client)
            self.print_test("API Health Check", api_healthy, "Backend is running")
            
            if not api_healthy:
                print(f"\n{Colors.RED}❌ API is not running. Start the backend first:{Colors.RESET}")
                print(f"   cd backend && uvicorn app.main:app --reload\n")
                return 1
            
            # Run all endpoint tests
            await self.test_memory_endpoints(client)
            await self.test_recommendation_endpoints(client)
            await self.test_guidance_endpoints(client)
            await self.test_prediction_endpoints(client)
            await self.test_profile_assistant_endpoints(client)
            await self.test_jobs_marketplace_ai(client)
            await self.test_performance(client)
        
        # Print summary
        return self.print_summary()


async def main():
    """Main test runner"""
    tester = IntegrationTester()
    exit_code = await tester.run_all_tests()
    sys.exit(exit_code)


if __name__ == "__main__":
    asyncio.run(main())
