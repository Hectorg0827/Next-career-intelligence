"""
Job-related endpoints (autocomplete, search, etc.)
"""

from fastapi import APIRouter, Query, HTTPException, status, Depends
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from loguru import logger
import uuid

from app.models.schemas import JobSuggestion
from app.services.onet_service import ONetService
from app.db.database import get_db
from app.models.database import Job, User
from app.services.ai_matching_service import ai_matching_service

router = APIRouter()


@router.get("/jobs/matches")
async def get_job_matches(
    user_id: str,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get AI-matched jobs for a user
    """
    try:
        # Get user (check both id and firebase_uid)
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            user = db.query(User).filter(User.firebase_uid == user_id).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Calculate matches
        matches = await ai_matching_service.calculate_all_matches_for_user(str(user.id), db)
        
        # Sort by score
        matches.sort(key=lambda x: x.get("match_score", 0), reverse=True)
        
        return matches[:limit]
    except Exception as e:
        logger.error(f"Error getting matches: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs")
def list_jobs(
    skip: int = 0,
    limit: int = 20,
    title: Optional[str] = None,
    location: Optional[str] = None,
    remote: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    List jobs with filtering
    """
    query = db.query(Job).filter(Job.is_active == True)
    
    if title:
        query = query.filter(Job.title.ilike(f"%{title}%"))
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    if remote:
        query = query.filter(Job.remote_policy == "remote")
        
    jobs = query.offset(skip).limit(limit).all()
    return jobs


@router.get("/jobs/suggest", response_model=List[JobSuggestion])
async def suggest_jobs(
    q: str = Query(..., min_length=2, description="Search query for job title"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of suggestions"),
):
    """
    Autocomplete job titles from O*NET database

    Args:
        q: Search query (minimum 2 characters)
        limit: Maximum number of results to return

    Returns:
        List of job title suggestions with O*NET codes
    """

    try:
        logger.info(f"Job autocomplete request: '{q}'")

        onet_service = ONetService()
        suggestions = await onet_service.search_occupations(q, limit=limit)

        return suggestions

    except Exception as e:
        logger.error(f"Job search failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch job suggestions")


@router.get("/jobs/{onet_code}")
async def get_job_details(onet_code: str):
    """
    Get detailed information about a specific occupation

    Args:
        onet_code: O*NET-SOC code (e.g., "15-1252.00")

    Returns:
        Detailed occupation data from O*NET
    """

    try:
        onet_service = ONetService()
        job_details = await onet_service.get_occupation_by_code(onet_code)

        if not job_details:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Occupation not found: {onet_code}")

        return job_details

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job details: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch job details")
