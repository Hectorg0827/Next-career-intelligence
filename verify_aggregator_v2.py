import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.services.job_aggregator import JobAggregatorService

async def verify_aggregator():
    print("Initializing JobAggregatorService...")
    try:
        service = JobAggregatorService()
        print(f"✅ Service initialized successfully.")
        print(f"Found {len(service.fetchers)} fetchers:")
        for fetcher in service.fetchers:
            print(f" - {fetcher.source_name} ({fetcher.__class__.__name__})")
        
        expected_sources = {"remoteok", "weworkremotely", "arbeitnow", "jobicy"}
        found_sources = {f.source_name for f in service.fetchers}
        
        if expected_sources.issubset(found_sources):
            print("✅ All expected sources are present.")
        else:
            print(f"❌ Missing sources: {expected_sources - found_sources}")
            
        await service.close()
        
    except Exception as e:
        print(f"❌ Error initializing service: {e}")

if __name__ == "__main__":
    asyncio.run(verify_aggregator())
