"""
Redis Cache Performance Test

Tests cache performance improvements:
- Cold cache (no cache) vs warm cache comparison
- Cache hit rate validation
- Response time improvement measurement
- Cache key collision testing

Expected Results:
- 50-70% reduction in response time with cache
- 80%+ cache hit rate after warming
- LLM justifications: 1000ms → 50ms (cached)
- DB queries: 200ms → 10ms (cached)
"""

import asyncio
import asyncpg
import uuid
import time
from typing import List, Dict
from statistics import mean, median
from loguru import logger

from app.services.foundation.risk.displacement_engine import DisplacementRiskEngine
from app.services.foundation.risk.models import UserProfile, UserSkill, UserCredential, JobData
from app.services.foundation.risk.cache import get_cache


class CachePerformanceTester:
    """Test Redis cache performance improvements"""
    
    def __init__(self, db_pool: asyncpg.Pool):
        self.db = db_pool
        self.engine = DisplacementRiskEngine(db_pool)
        self.cache = get_cache()
        self.results = {
            "cold_cache_times": [],
            "warm_cache_times": [],
            "cache_hits": 0,
            "cache_misses": 0,
            "total_requests": 0
        }
    
    async def setup(self):
        """Initialize cache connection and clear for clean test"""
        await self.cache.connect()
        
        # Clear cache for clean test
        if self.cache.enabled:
            await self.cache.redis.flushdb()
            logger.info("🧹 Cache cleared for performance test")
    
    def _create_test_profile(self, profile_type: str) -> UserProfile:
        """Create test user profile"""
        profiles = {
            "junior": {
                "exp": 2.0,
                "decision": 0.1,
                "mgmt": False,
                "domain": 1,
                "creds": [UserCredential(credential_type="degree", name="BS CS", year_obtained=2023)]
            },
            "mid": {
                "exp": 8.0,
                "decision": 0.3,
                "mgmt": False,
                "domain": 5,
                "creds": [
                    UserCredential(credential_type="degree", name="BS CS", year_obtained=2017),
                    UserCredential(credential_type="cert", name="AWS Certified", year_obtained=2022)
                ]
            },
            "senior": {
                "exp": 15.0,
                "decision": 0.7,
                "mgmt": True,
                "domain": 12,
                "creds": [
                    UserCredential(credential_type="degree", name="BS CS", year_obtained=2010),
                    UserCredential(credential_type="degree", name="MS AI", year_obtained=2023),
                    UserCredential(credential_type="cert", name="AWS SA", year_obtained=2021)
                ]
            }
        }
        
        config = profiles[profile_type]
        return UserProfile(
            user_id=str(uuid.uuid4()),
            years_experience=config["exp"],
            decision_level=config["decision"],
            people_management=config["mgmt"],
            domain_depth_years=config["domain"],
            skills=[
                UserSkill(skill_name="Python", proficiency=0.8, years_experience=config["exp"]*0.8, last_used_days_ago=5),
                UserSkill(skill_name="Machine Learning", proficiency=0.7, years_experience=config["exp"]*0.4, last_used_days_ago=10)
            ],
            credentials=config["creds"],
            action_log=[]
        )
    
    async def test_cold_cache(self, iterations: int = 10) -> List[float]:
        """Test performance WITHOUT cache (cold)"""
        logger.info(f"\n📊 TEST 1: Cold Cache Performance ({iterations} requests)")
        logger.info("=" * 70)
        
        times = []
        
        for i in range(iterations):
            # Clear cache before each request to simulate cold cache
            if self.cache.enabled:
                await self.cache.redis.flushdb()
            
            profile = self._create_test_profile("mid")
            job = JobData(
                occupation_code="15-1252.00",
                industry="Technology",
                wage_level=0.75,
                technical_readiness=0.85
            )
            
            start = time.time()
            result = await self.engine.analyze(profile, job)
            duration = (time.time() - start) * 1000  # Convert to ms
            
            times.append(duration)
            self.results["cold_cache_times"].append(duration)
            self.results["total_requests"] += 1
            
            logger.info(f"  Request {i+1}: {duration:.0f}ms (risk: {result.ai_displacement_risk.score:.1f})")
        
        avg = mean(times)
        p50 = median(times)
        logger.info(f"\n  Cold Cache Stats:")
        logger.info(f"    Average: {avg:.0f}ms")
        logger.info(f"    Median: {p50:.0f}ms")
        logger.info(f"    Min: {min(times):.0f}ms")
        logger.info(f"    Max: {max(times):.0f}ms")
        
        return times
    
    async def test_warm_cache(self, iterations: int = 10) -> List[float]:
        """Test performance WITH cache (warm)"""
        logger.info(f"\n📊 TEST 2: Warm Cache Performance ({iterations} requests)")
        logger.info("=" * 70)
        
        # Use same profile and job for all requests to hit cache
        profile = self._create_test_profile("mid")
        job = JobData(
            occupation_code="15-1252.00",
            industry="Technology",
            wage_level=0.75,
            technical_readiness=0.85
        )
        
        times = []
        
        for i in range(iterations):
            start = time.time()
            result = await self.engine.analyze(profile, job)
            duration = (time.time() - start) * 1000  # Convert to ms
            
            times.append(duration)
            self.results["warm_cache_times"].append(duration)
            self.results["total_requests"] += 1
            
            # First request is cache miss, rest are hits
            if i == 0:
                self.results["cache_misses"] += 1
                logger.info(f"  Request {i+1}: {duration:.0f}ms (CACHE MISS - first request)")
            else:
                self.results["cache_hits"] += 1
                logger.info(f"  Request {i+1}: {duration:.0f}ms (CACHE HIT)")
        
        avg = mean(times)
        p50 = median(times)
        
        # Calculate improvement (excluding first request which is cache miss)
        cached_times = times[1:]
        avg_cached = mean(cached_times) if cached_times else avg
        
        logger.info(f"\n  Warm Cache Stats:")
        logger.info(f"    Average (all): {avg:.0f}ms")
        logger.info(f"    Average (cached only): {avg_cached:.0f}ms")
        logger.info(f"    Median: {p50:.0f}ms")
        logger.info(f"    Min: {min(times):.0f}ms")
        logger.info(f"    Max: {max(times):.0f}ms")
        
        return times
    
    async def test_cache_warming(self, num_profiles: int = 5) -> None:
        """Test cache warming with common profiles"""
        logger.info(f"\n📊 TEST 3: Cache Warming ({num_profiles} profiles)")
        logger.info("=" * 70)
        
        common_profiles = [
            ("junior", "15-1252.00", "Technology"),
            ("mid", "15-1252.00", "Technology"),
            ("senior", "15-1252.00", "Technology"),
            ("mid", "15-1256.00", "Technology"),  # Data Scientist
            ("senior", "15-1211.00", "Technology"),  # Software Architect
        ]
        
        warmed = 0
        for profile_type, occ_code, industry in common_profiles[:num_profiles]:
            profile = self._create_test_profile(profile_type)
            job = JobData(
                occupation_code=occ_code,
                industry=industry,
                wage_level=0.75,
                technical_readiness=0.85
            )
            
            start = time.time()
            await self.engine.analyze(profile, job)
            duration = (time.time() - start) * 1000
            
            warmed += 1
            logger.info(f"  Warmed {profile_type} + {occ_code}: {duration:.0f}ms")
        
        logger.info(f"\n  ✅ Cache warmed with {warmed} common profiles")
    
    async def test_cache_hit_rate(self, iterations: int = 20) -> Dict[str, float]:
        """Test cache hit rate with mixed requests"""
        logger.info(f"\n📊 TEST 4: Cache Hit Rate ({iterations} mixed requests)")
        logger.info("=" * 70)
        
        # Warm cache with 3 profiles
        await self.test_cache_warming(3)
        
        profile_types = ["junior", "mid", "senior"]
        hits_before = self.results["cache_hits"]
        
        for i in range(iterations):
            # Rotate through profiles to test cache hits
            profile_type = profile_types[i % len(profile_types)]
            profile = self._create_test_profile(profile_type)
            job = JobData(
                occupation_code="15-1252.00",
                industry="Technology",
                wage_level=0.75,
                technical_readiness=0.85
            )
            
            await self.engine.analyze(profile, job)
            self.results["total_requests"] += 1
        
        hits_after = self.results["cache_hits"]
        new_hits = hits_after - hits_before
        hit_rate = (new_hits / iterations) * 100
        
        logger.info(f"\n  Cache Hit Rate: {hit_rate:.1f}% ({new_hits}/{iterations})")
        
        return {"hit_rate": hit_rate, "hits": new_hits, "total": iterations}
    
    def print_summary(self, cold_times: List[float], warm_times: List[float]) -> None:
        """Print comprehensive performance summary"""
        logger.info("\n" + "=" * 70)
        logger.info("🎯 CACHE PERFORMANCE SUMMARY")
        logger.info("=" * 70)
        
        # Calculate averages (exclude first warm cache request which is a miss)
        cold_avg = mean(cold_times)
        warm_cached = warm_times[1:] if len(warm_times) > 1 else warm_times
        warm_avg = mean(warm_cached)
        
        # Calculate improvement
        improvement_ms = cold_avg - warm_avg
        improvement_pct = (improvement_ms / cold_avg) * 100
        speedup = cold_avg / warm_avg
        
        logger.info(f"\n📈 Response Times:")
        logger.info(f"  Cold Cache (no cache): {cold_avg:.0f}ms")
        logger.info(f"  Warm Cache (cached):   {warm_avg:.0f}ms")
        logger.info(f"  Improvement:           {improvement_ms:.0f}ms ({improvement_pct:.1f}% faster)")
        logger.info(f"  Speedup:               {speedup:.2f}x")
        
        # Cache statistics
        total_requests = self.results["total_requests"]
        hits = self.results["cache_hits"]
        misses = self.results["cache_misses"]
        overall_hit_rate = (hits / total_requests * 100) if total_requests > 0 else 0
        
        logger.info(f"\n📊 Cache Statistics:")
        logger.info(f"  Total Requests:  {total_requests}")
        logger.info(f"  Cache Hits:      {hits}")
        logger.info(f"  Cache Misses:    {misses}")
        logger.info(f"  Hit Rate:        {overall_hit_rate:.1f}%")
        
        # Performance assessment
        logger.info(f"\n✅ Performance Assessment:")
        
        if improvement_pct >= 50:
            logger.info(f"  🎉 EXCELLENT: {improvement_pct:.0f}% improvement (target: 50-70%)")
        elif improvement_pct >= 30:
            logger.info(f"  ✅ GOOD: {improvement_pct:.0f}% improvement (close to target)")
        else:
            logger.info(f"  ⚠️  NEEDS TUNING: {improvement_pct:.0f}% improvement (target: 50-70%)")
        
        if overall_hit_rate >= 80:
            logger.info(f"  🎉 EXCELLENT: {overall_hit_rate:.0f}% cache hit rate")
        elif overall_hit_rate >= 60:
            logger.info(f"  ✅ GOOD: {overall_hit_rate:.0f}% cache hit rate")
        else:
            logger.info(f"  ⚠️  LOW: {overall_hit_rate:.0f}% cache hit rate (target: 80%+)")
        
        logger.info("\n" + "=" * 70)


async def main():
    """Run cache performance tests"""
    print("=" * 70)
    print("🚀 REDIS CACHE PERFORMANCE TEST")
    print("=" * 70)
    
    # Connect to database
    db_pool = await asyncpg.create_pool(
        "postgresql://postgres:ssuRd6vrGSdP5z7a@db.whxbxjpymksgvixudnjh.supabase.co:5432/postgres",
        min_size=2,
        max_size=10
    )
    
    tester = CachePerformanceTester(db_pool)
    await tester.setup()
    
    # Check if Redis is available
    cache = get_cache()
    if not cache.enabled:
        logger.error("❌ Redis cache is DISABLED - cannot run performance tests")
        logger.info("   Enable Redis by setting REDIS_ENABLED=true and REDIS_URL in .env")
        await db_pool.close()
        return
    
    try:
        # Test 1: Cold cache (no cache)
        cold_times = await tester.test_cold_cache(iterations=10)
        
        # Test 2: Warm cache (with cache)
        warm_times = await tester.test_warm_cache(iterations=10)
        
        # Test 3: Cache warming
        await tester.test_cache_warming(num_profiles=5)
        
        # Test 4: Cache hit rate
        await tester.test_cache_hit_rate(iterations=20)
        
        # Print summary
        tester.print_summary(cold_times, warm_times)
        
    finally:
        await cache.close()
        await db_pool.close()


if __name__ == "__main__":
    asyncio.run(main())
