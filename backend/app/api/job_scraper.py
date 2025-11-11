"""
Job Scraper API

Endpoints for triggering and managing job scraping.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.scrapers.greenhouse_scraper import GreenhouseScraper
from app.scrapers.lever_scraper import LeverScraper
from app.db.supabase import get_supabase_client
from loguru import logger
from datetime import datetime
from typing import Dict, List

router = APIRouter(prefix="/api/job-scraper", tags=["job_scraper"])


async def run_full_scrape():
    """
    Run complete job scraping from all sources

    This is a background task that:
    1. Scrapes Greenhouse companies
    2. Scrapes Lever companies
    3. Deduplicates jobs
    4. Inserts/updates database
    """
    logger.info("🚀 Starting full job scrape...")

    all_jobs = []
    stats = {
        "greenhouse": {"scraped": 0, "inserted": 0, "updated": 0, "errors": 0},
        "lever": {"scraped": 0, "inserted": 0, "updated": 0, "errors": 0},
        "total": {"scraped": 0, "inserted": 0, "updated": 0, "duplicates": 0}
    }

    # Scrape Greenhouse
    try:
        greenhouse = GreenhouseScraper()
        gh_jobs = await greenhouse.scrape_all_companies(max_concurrent=3)
        await greenhouse.close()

        all_jobs.extend(gh_jobs)
        stats["greenhouse"]["scraped"] = len(gh_jobs)
        logger.info(f"✅ Greenhouse: {len(gh_jobs)} jobs scraped")
    except Exception as e:
        logger.error(f"❌ Greenhouse scraping failed: {e}")
        stats["greenhouse"]["errors"] += 1

    # Scrape Lever
    try:
        lever = LeverScraper()
        lever_jobs = await lever.scrape_all_companies(max_concurrent=3)
        await lever.close()

        all_jobs.extend(lever_jobs)
        stats["lever"]["scraped"] = len(lever_jobs)
        logger.info(f"✅ Lever: {len(lever_jobs)} jobs scraped")
    except Exception as e:
        logger.error(f"❌ Lever scraping failed: {e}")
        stats["lever"]["errors"] += 1

    stats["total"]["scraped"] = len(all_jobs)

    # Deduplicate (by external_id)
    unique_jobs = {}
    for job in all_jobs:
        external_id = job.get("external_id")
        if external_id and external_id not in unique_jobs:
            unique_jobs[external_id] = job

    deduplicated_jobs = list(unique_jobs.values())
    stats["total"]["duplicates"] = len(all_jobs) - len(deduplicated_jobs)

    logger.info(f"📊 After deduplication: {len(deduplicated_jobs)} unique jobs")

    # Insert/update jobs in database
    for job in deduplicated_jobs:
        try:
            external_id = job.get("external_id")

            # Check if job exists
            existing = supabase.table("jobs") \
                .select("id") \
                .eq("external_id", external_id) \
                .execute()

            if existing.data:
                # Update existing job
                supabase.table("jobs") \
                    .update(job) \
                    .eq("external_id", external_id) \
                    .execute()

                source_prefix = job["source"].split(":")[0]
                stats[source_prefix]["updated"] += 1
                stats["total"]["updated"] += 1
            else:
                # Insert new job
                supabase.table("jobs").insert(job).execute()

                source_prefix = job["source"].split(":")[0]
                stats[source_prefix]["inserted"] += 1
                stats["total"]["inserted"] += 1

        except Exception as e:
            logger.error(f"Failed to insert/update job: {e}")
            source_prefix = job["source"].split(":")[0]
            stats[source_prefix]["errors"] += 1

    logger.info(f"🎉 Job scraping complete! Stats: {stats}")

    # Store scraping run metadata
    try:
        supabase.table("scraping_runs").insert({
            "started_at": datetime.utcnow().isoformat(),
            "completed_at": datetime.utcnow().isoformat(),
            "stats": stats,
            "status": "completed"
        }).execute()
    except:
        pass  # Metadata table might not exist yet

    return stats


@router.post("/run")
async def trigger_job_scrape(background_tasks: BackgroundTasks):
    """
    Trigger a full job scraping run

    This endpoint starts a background task that:
    - Scrapes all Greenhouse companies (~15 companies)
    - Scrapes all Lever companies (~12 companies)
    - Deduplicates and inserts jobs into database

    Expected to scrape 500-1000 jobs total.
    Takes ~5-10 minutes to complete.
    """
    try:
        # Run scraping in background
        background_tasks.add_task(run_full_scrape)

        return {
            "status": "started",
            "message": "Job scraping started in background",
            "expected_duration": "5-10 minutes",
            "expected_jobs": "500-1000 jobs"
        }

    except Exception as e:
        logger.error(f"Failed to start job scrape: {e}")
        raise HTTPException(status_code=500, detail="Failed to start job scraping")


@router.post("/test-greenhouse")
async def test_greenhouse_scraping(company_name: str = "Stripe"):
    """
    Test Greenhouse scraping for a single company

    Args:
        company_name: Company name (e.g., "Stripe", "Airbnb", "GitLab")
    """
    try:
        # Find company config
        greenhouse = GreenhouseScraper()
        company = next((c for c in greenhouse.GREENHOUSE_COMPANIES if c["name"].lower() == company_name.lower()), None)

        if not company:
            available = [c["name"] for c in greenhouse.GREENHOUSE_COMPANIES]
            raise HTTPException(
                status_code=404,
                detail=f"Company not found. Available: {', '.join(available)}"
            )

        jobs = await greenhouse.scrape_company(company["name"], company["board_token"])
        await greenhouse.close()

        return {
            "company": company_name,
            "jobs_found": len(jobs),
            "sample_jobs": jobs[:3] if jobs else []
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to test Greenhouse scraping: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-lever")
async def test_lever_scraping(company_name: str = "Netflix"):
    """
    Test Lever scraping for a single company

    Args:
        company_name: Company name (e.g., "Netflix", "Uber", "Reddit")
    """
    try:
        lever = LeverScraper()
        company = next((c for c in lever.LEVER_COMPANIES if c["name"].lower() == company_name.lower()), None)

        if not company:
            available = [c["name"] for c in lever.LEVER_COMPANIES]
            raise HTTPException(
                status_code=404,
                detail=f"Company not found. Available: {', '.join(available)}"
            )

        jobs = await lever.scrape_company(company["name"], company["company_id"])
        await lever.close()

        return {
            "company": company_name,
            "jobs_found": len(jobs),
            "sample_jobs": jobs[:3] if jobs else []
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to test Lever scraping: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_scraper_stats():
    """
    Get job scraping statistics

    Returns:
    - Total jobs by source
    - Recent scraping runs
    - Job counts by company
    """
    try:
        # Count jobs by source
        response = supabase.table("jobs") \
            .select("source", count="exact") \
            .execute()

        # Group by source
        source_counts = {}
        if response.data:
            for job in response.data:
                source = job.get("source", "unknown")
                source_counts[source] = source_counts.get(source, 0) + 1

        # Total jobs
        total_jobs = sum(source_counts.values())

        # Jobs added today
        today_response = supabase.table("jobs") \
            .select("id", count="exact") \
            .gte("created_at", datetime.utcnow().date().isoformat()) \
            .execute()

        jobs_today = today_response.count or 0

        return {
            "total_jobs": total_jobs,
            "jobs_added_today": jobs_today,
            "by_source": source_counts,
            "configured_companies": {
                "greenhouse": len(GreenhouseScraper.GREENHOUSE_COMPANIES),
                "lever": len(LeverScraper.LEVER_COMPANIES)
            }
        }

    except Exception as e:
        logger.error(f"Failed to get scraper stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get stats")
