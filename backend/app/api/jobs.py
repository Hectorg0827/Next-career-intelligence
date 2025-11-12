"""
Job-related endpoints (autocomplete, search, etc.)
"""

from fastapi import APIRouter, Query, HTTPException, status
from typing import List
from loguru import logger

from app.models.schemas import JobSuggestion
from app.services.onet_service import ONetService

router = APIRouter()


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
