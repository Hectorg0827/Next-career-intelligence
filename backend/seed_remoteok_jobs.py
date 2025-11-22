"""Script to fetch and seed jobs from RemoteOK API into the database.

Usage:
    python seed_remoteok_jobs.py [--limit 50] [--replace]
"""

import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from app.db.database import SessionLocal
from app.services.remoteok_service import RemoteOKService
from loguru import logger


async def main(limit: int = 50, replace: bool = False):
    """Main function to seed jobs."""
    logger.info("Starting RemoteOK job seeding process...")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Initialize service
        service = RemoteOKService()
        
        # Fetch and seed jobs
        count = await service.seed_jobs_to_db(
            db=db,
            limit=limit,
            replace_existing=replace
        )
        
        logger.info(f"✅ Successfully seeded {count} jobs from RemoteOK")
        
        # Show summary
        from app.models.database import Job
        total_jobs = db.query(Job).count()
        remoteok_jobs = db.query(Job).filter(Job.source == 'remoteok').count()
        
        logger.info(f"📊 Database Summary:")
        logger.info(f"   Total jobs: {total_jobs}")
        logger.info(f"   RemoteOK jobs: {remoteok_jobs}")
        
        return count
        
    except Exception as e:
        logger.error(f"❌ Error seeding jobs: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Seed jobs from RemoteOK API")
    parser.add_argument("--limit", type=int, default=50, help="Maximum number of jobs to fetch (default: 50)")
    parser.add_argument("--replace", action="store_true", help="Replace existing RemoteOK jobs")
    
    args = parser.parse_args()
    
    # Run async function
    count = asyncio.run(main(limit=args.limit, replace=args.replace))
    
    print(f"\n✅ Seeding complete! Added/updated {count} jobs.")
