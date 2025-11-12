"""Script to seed job database with GitHub jobs.

Usage:
    python seed_jobs.py        # Seed 5 pages of general jobs
    python seed_jobs.py --positions  # Seed jobs by specific positions
    python seed_jobs.py --full   # Seed 10 pages for full seeding
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from app.db.database import SessionLocal
from app.services.github_jobs_service import GitHubJobsService


async def seed_general_jobs(pages: int = 5):
    """Seed general tech jobs."""
    db = SessionLocal()
    try:
        print(f"\n🔄 Seeding {pages} pages of GitHub jobs...")
        created, skipped = await GitHubJobsService.seed_github_jobs_batch(
            db=db,
            num_pages=pages,
            source="github",
        )
        print(f"\n✅ Seeding complete!")
        print(f"   📊 Created: {created} jobs")
        print(f"   ⏭️  Skipped: {skipped} (already in database)")
    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
    finally:
        db.close()


async def seed_by_position():
    """Seed jobs by specific positions."""
    db = SessionLocal()
    positions = [
        "Python Developer",
        "JavaScript Developer",
        "Full Stack Developer",
        "DevOps Engineer",
        "Data Engineer",
        "Machine Learning Engineer",
        "Frontend Developer",
        "Backend Developer",
        "Software Engineer",
        "Systems Engineer",
    ]

    try:
        print(f"\n🔄 Seeding jobs for {len(positions)} positions...")
        created, skipped = await GitHubJobsService.seed_jobs_by_position(
            db=db,
            positions=positions,
            pages_per_position=2,
            source="github",
        )
        print(f"\n✅ Position-based seeding complete!")
        print(f"   📊 Created: {created} jobs")
        print(f"   ⏭️  Skipped: {skipped} (already in database)")
    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
    finally:
        db.close()


async def main():
    """Main entry point."""
    print("\n" + "=" * 70)
    print("🌱 Job Database Seeder - GitHub Jobs Integration")
    print("=" * 70)

    if len(sys.argv) > 1:
        if sys.argv[1] == "--positions":
            await seed_by_position()
        elif sys.argv[1] == "--full":
            await seed_general_jobs(pages=10)
        elif sys.argv[1] == "--help":
            print("\nUsage:")
            print("  python seed_jobs.py              # Seed 5 pages (default)")
            print("  python seed_jobs.py --positions  # Seed by job positions")
            print("  python seed_jobs.py --full       # Seed 10 pages")
        else:
            pages = int(sys.argv[1]) if sys.argv[1].isdigit() else 5
            await seed_general_jobs(pages=pages)
    else:
        await seed_general_jobs()

    print("\n" + "=" * 70)
    print("✨ All done! Your database is ready.")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
