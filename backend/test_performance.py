"""
Phase 3 - Performance Testing
Tests API response times and load handling
"""
import asyncio
import httpx
import time
import statistics
from datetime import datetime
import uuid

# Configuration
BASE_URL = "http://localhost:8000"
TIMEOUT = 30.0

# ANSI Colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

class PerformanceTester:
    def __init__(self):
        self.results = {
            "response_times": [],
            "errors": 0
        }
        self.total_requests = 0
    
    def create_test_payload(self):
        """Create a test risk analysis request"""
        return {
            "user_profile": {
                "user_id": str(uuid.uuid4()),
                "years_experience": 5,
                "decision_level": 0.3,
                "people_management": False,
                "domain_depth_years": 4,
                "skills": [
                    {
                        "skill_name": "Python",
                        "proficiency": 0.8,
                        "years_experience": 4,
                        "last_used_days_ago": 5
                    },
                    {
                        "skill_name": "Machine Learning",
                        "proficiency": 0.7,
                        "years_experience": 3,
                        "last_used_days_ago": 10
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
    
    async def single_request(self, client: httpx.AsyncClient, request_num: int):
        """Make a single API request and measure response time"""
        start = time.time()
        try:
            payload = self.create_test_payload()
            response = await client.post(
                f"{BASE_URL}/api/risk/analyze",
                json=payload
            )
            elapsed = (time.time() - start) * 1000  # Convert to ms
            
            self.total_requests += 1
            if response.status_code == 200:
                self.results["response_times"].append(elapsed)
                return elapsed, None
            else:
                self.results["errors"] += 1
                return elapsed, f"HTTP {response.status_code}"
                
        except Exception as e:
            elapsed = (time.time() - start) * 1000
            self.results["errors"] += 1
            return elapsed, str(e)
    
    async def test_sequential_requests(self, count: int = 10):
        """Test sequential request performance"""
        print(f"\n{BLUE}TEST 1: Sequential Requests (n={count}){RESET}")
        print("=" * 80)
        
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            for i in range(count):
                elapsed, error = await self.single_request(client, i + 1)
                
                if error:
                    print(f"   Request {i+1}: {RED}{elapsed:.0f}ms - ERROR: {error}{RESET}")
                else:
                    color = GREEN if elapsed < 500 else (YELLOW if elapsed < 1000 else RED)
                    print(f"   Request {i+1}: {color}{elapsed:.0f}ms{RESET}")
        
        if self.results["response_times"]:
            avg = statistics.mean(self.results["response_times"])
            median = statistics.median(self.results["response_times"])
            p95 = sorted(self.results["response_times"])[int(len(self.results["response_times"]) * 0.95)]
            
            print(f"\n{GREEN}✅ Sequential test complete{RESET}")
            print(f"   Average: {avg:.0f}ms")
            print(f"   Median: {median:.0f}ms")
            print(f"   P95: {p95:.0f}ms")
            print(f"   Target: <500ms P95")
            
            if p95 > 500:
                print(f"   {YELLOW}⚠️  WARNING: P95 exceeds 500ms target{RESET}")
    
    async def test_concurrent_requests(self, concurrent: int = 10):
        """Test concurrent request handling"""
        print(f"\n{BLUE}TEST 2: Concurrent Requests (n={concurrent}){RESET}")
        print("=" * 80)
        
        start_batch = time.time()
        
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            tasks = [
                self.single_request(client, i + 1)
                for i in range(concurrent)
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        batch_time = (time.time() - start_batch) * 1000
        
        successful = sum(1 for r in results if not isinstance(r, Exception) and r[1] is None)
        
        print(f"   Batch completed in: {batch_time:.0f}ms")
        print(f"   Successful: {successful}/{concurrent}")
        print(f"   Errors: {concurrent - successful}")
        
        if successful > 0:
            recent_times = self.results["response_times"][-concurrent:]
            avg = statistics.mean(recent_times)
            max_time = max(recent_times)
            
            print(f"   Average response: {avg:.0f}ms")
            print(f"   Max response: {max_time:.0f}ms")
            
            if successful == concurrent:
                print(f"\n{GREEN}✅ All concurrent requests succeeded{RESET}")
            else:
                print(f"\n{YELLOW}⚠️  Some concurrent requests failed{RESET}")
    
    async def test_load_simulation(self, users: int = 5, requests_per_user: int = 3):
        """Simulate realistic load with multiple users"""
        print(f"\n{BLUE}TEST 3: Load Simulation ({users} users × {requests_per_user} requests){RESET}")
        print("=" * 80)
        
        total = users * requests_per_user
        start_load = time.time()
        
        async def user_session(user_id: int):
            """Simulate a single user making multiple requests"""
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                for req_num in range(requests_per_user):
                    await self.single_request(client, user_id * requests_per_user + req_num + 1)
                    await asyncio.sleep(0.5)  # 500ms between requests
        
        # Run all user sessions concurrently
        user_tasks = [user_session(i) for i in range(users)]
        await asyncio.gather(*user_tasks, return_exceptions=True)
        
        load_time = (time.time() - start_load)
        throughput = total / load_time
        
        print(f"   Total time: {load_time:.1f}s")
        print(f"   Throughput: {throughput:.1f} req/s")
        print(f"   Total requests: {total}")
        print(f"   Errors: {self.results['errors']}")
        
        if self.results["errors"] == 0:
            print(f"\n{GREEN}✅ Load simulation completed successfully{RESET}")
        else:
            error_rate = (self.results["errors"] / self.total_requests) * 100 if self.total_requests > 0 else 0
            print(f"\n{YELLOW}⚠️  Error rate: {error_rate:.1f}%{RESET}")
    
    async def run_all_tests(self):
        """Run complete performance test suite"""
        print("\n" + "=" * 80)
        print(f"{BLUE}PHASE 3 - PERFORMANCE TEST SUITE{RESET}")
        print("=" * 80)
        print(f"Target: {BASE_URL}")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Run tests
        await self.test_sequential_requests(10)
        await self.test_concurrent_requests(10)
        await self.test_load_simulation(5, 3)
        
        # Final summary
        print("\n" + "=" * 80)
        print(f"{BLUE}PERFORMANCE SUMMARY{RESET}")
        print("=" * 80)
        
        if self.results["response_times"]:
            avg = statistics.mean(self.results["response_times"])
            median = statistics.median(self.results["response_times"])
            p50 = sorted(self.results["response_times"])[int(len(self.results["response_times"]) * 0.5)]
            p95 = sorted(self.results["response_times"])[int(len(self.results["response_times"]) * 0.95)]
            p99 = sorted(self.results["response_times"])[int(len(self.results["response_times"]) * 0.99)]
            min_time = min(self.results["response_times"])
            max_time = max(self.results["response_times"])
            
            print(f"Total Requests: {self.total_requests}")
            print(f"Successful: {len(self.results['response_times'])}")
            print(f"Errors: {self.results['errors']}")
            print(f"\nResponse Times:")
            print(f"   Min: {min_time:.0f}ms")
            print(f"   P50 (Median): {p50:.0f}ms")
            print(f"   Average: {avg:.0f}ms")
            print(f"   P95: {p95:.0f}ms")
            print(f"   P99: {p99:.0f}ms")
            print(f"   Max: {max_time:.0f}ms")
            
            # Performance assessment
            print(f"\nPerformance Assessment:")
            if p95 < 500:
                print(f"   {GREEN}✅ EXCELLENT: P95 < 500ms target{RESET}")
            elif p95 < 1000:
                print(f"   {YELLOW}⚠️  ACCEPTABLE: P95 < 1000ms (target: 500ms){RESET}")
            else:
                print(f"   {RED}❌ NEEDS OPTIMIZATION: P95 > 1000ms{RESET}")
            
            error_rate = (self.results['errors'] / self.total_requests) * 100 if self.total_requests > 0 else 0
            if error_rate == 0:
                print(f"   {GREEN}✅ PERFECT: 0% error rate{RESET}")
            elif error_rate < 1:
                print(f"   {GREEN}✅ EXCELLENT: {error_rate:.2f}% error rate{RESET}")
            elif error_rate < 5:
                print(f"   {YELLOW}⚠️  ACCEPTABLE: {error_rate:.1f}% error rate{RESET}")
            else:
                print(f"   {RED}❌ HIGH ERROR RATE: {error_rate:.1f}%{RESET}")
        
        print("=" * 80 + "\n")

async def main():
    """Main entry point"""
    tester = PerformanceTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
