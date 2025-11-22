"""
Job Search and Browse API
Provides endpoints for job search, filtering, and retrieval
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from loguru import logger

from app.db.database import get_db
from sqlalchemy.orm import Session
from app.services.job_search_service import JobSearchService, JobSearchFilters, JobSearchResult

router = APIRouter(prefix="/jobs-v2", tags=["Job Search"])


@router.get("/search", response_model=JobSearchResult)
async def search_jobs(
    query: Optional[str] = Query(None, description="Search term for job title or description"),
    location: Optional[str] = Query(None, description="Location filter (city, state, or country)"),
    remote_only: bool = Query(False, description="Filter for remote jobs only"),
    location_type: Optional[List[str]] = Query(None, description="Location types (remote, hybrid, on_site)"),
    seniority: Optional[List[str]] = Query(None, description="Seniority levels (entry, mid, senior)"),
    employment_type: Optional[List[str]] = Query(None, description="Employment types (full_time, part_time, contract)"),
    salary_min: Optional[int] = Query(None, description="Minimum salary"),
    salary_max: Optional[int] = Query(None, description="Maximum salary"),
    posted_within_days: Optional[int] = Query(None, description="Filter by posted date (e.g., 7, 30, 90 days)"),
    sources: Optional[List[str]] = Query(None, description="Job sources (remoteok, github, etc.)"),
    limit: int = Query(20, ge=1, le=100, description="Number of results to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    sort_by: str = Query("posted_at", description="Sort field (posted_at, salary_max)"),
    sort_order: Optional[str] = Query("desc", description="Sort order: asc or desc"),
    db: Session = Depends(get_db)
):
    """Search and filter jobs with comprehensive filtering options."""
    try:
        filters = JobSearchFilters(
            query=query,
            location=location,
            remote_only=remote_only,
            location_type=location_type,
            seniority=seniority,
            employment_type=employment_type,
            salary_min=salary_min,
            salary_max=salary_max,
            posted_within_days=posted_within_days,
            sources=sources,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        result = JobSearchService.search_jobs(db, filters)
        logger.info(f"Job search: found {result.total} jobs")
        return result
        
    except Exception as e:
        logger.error(f"Job search error: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/{job_id}")
async def get_job_by_id(
    job_id: str,
    db: Session = Depends(get_db)
):
    """Get full details for a specific job by ID."""
    try:
        job = JobSearchService.get_job_by_id(db, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return job
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get job error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve job: {str(e)}")


@router.get("/filters/options")
async def get_filter_options(db: Session = Depends(get_db)):
    """Get available filter options for building dynamic filter UI."""
    try:
        return JobSearchService.get_filter_options(db)
    except Exception as e:
        logger.error(f"Get filter options error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get filter options: {str(e)}")


@router.get("/stats")
async def get_job_stats(db: Session = Depends(get_db)):
    """Get job statistics for dashboard."""
    try:
        from app.models.database import Job
        from sqlalchemy import func
        from datetime import datetime, timedelta
        
        total_jobs = db.query(Job).filter(Job.is_active == True).count()
        
        jobs_by_source = dict(
            db.query(Job.source, func.count(Job.id))
            .filter(Job.is_active == True, Job.source.isnot(None))
            .group_by(Job.source)
            .all()
        )
        
        jobs_by_location = dict(
            db.query(Job.location_type, func.count(Job.id))
            .filter(Job.is_active == True, Job.location_type.isnot(None))
            .group_by(Job.location_type)
            .all()
        )
        
        jobs_by_seniority = dict(
            db.query(Job.seniority, func.count(Job.id))
            .filter(Job.is_active == True, Job.seniority.isnot(None))
            .group_by(Job.seniority)
            .all()
        )
        
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_jobs = db.query(Job).filter(
            Job.is_active == True,
            Job.created_at >= seven_days_ago
        ).count()
        
        return {
            "total_jobs": total_jobs,
            "jobs_by_source": jobs_by_source,
            "jobs_by_location_type": jobs_by_location,
            "jobs_by_seniority": jobs_by_seniority,
            "recent_jobs_7_days": recent_jobs
        }
    except Exception as e:
        logger.error(f"Get job stats error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")
