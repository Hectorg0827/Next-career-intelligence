"""
Job Matching API Endpoints
Provides personalized job recommendations and match analysis
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from loguru import logger

from app.db.database import get_db
from app.services.job_matcher_service import JobMatcherService
from app.core.auth import get_current_user
from pydantic import BaseModel


router = APIRouter(prefix="/job-matching", tags=["Job Matching"])


# ============================================================================
# Request/Response Models
# ============================================================================

class MatchScoreResponse(BaseModel):
    overall_score: float
    skill_match: dict
    experience_match: float
    location_match: float
    salary_match: float
    recommendation: str
    reason: str
    weights: dict


class JobRecommendation(BaseModel):
    job: dict
    match: MatchScoreResponse


class JobMatchExplanation(BaseModel):
    match_score: float
    match_breakdown: dict
    explanation: str
    strengths: List[str]
    gaps: List[str]
    recommendations: List[str]


# ============================================================================
# Endpoints
# ============================================================================

@router.get("/recommendations", response_model=List[JobRecommendation])
async def get_job_recommendations(
    limit: int = Query(20, ge=1, le=100, description="Maximum number of jobs to return"),
    min_score: float = Query(50.0, ge=0, le=100, description="Minimum match score threshold"),
    location_type: Optional[str] = Query(None, description="Filter by location type (remote, hybrid, onsite)"),
    seniority: Optional[List[str]] = Query(None, description="Filter by seniority level"),
    salary_min: Optional[int] = Query(None, description="Minimum salary requirement"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get personalized job recommendations for the current user
    
    Returns jobs ranked by match score based on:
    - Skill alignment (50% weight)
    - Experience level (20% weight)
    - Location preferences (15% weight)
    - Salary expectations (15% weight)
    """
    try:
        matcher = JobMatcherService()
        
        # Build filters
        filters = {}
        if location_type:
            filters["location_type"] = location_type
        if seniority:
            filters["seniority"] = seniority
        if salary_min:
            filters["salary_min"] = salary_min
        
        recommendations = await matcher.get_recommended_jobs(
            db=db,
            user_id=current_user["user_id"],
            limit=limit,
            min_score=min_score,
            filters=filters
        )
        
        return recommendations
        
    except Exception as e:
        logger.error(f"Error getting job recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{job_id}/score", response_model=MatchScoreResponse)
async def get_job_match_score(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Calculate match score between current user and a specific job
    
    Returns detailed breakdown of:
    - Overall match percentage
    - Skill alignment details
    - Experience level match
    - Location compatibility
    - Salary alignment
    """
    try:
        from app.models.database import Job
        
        # Get job
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        matcher = JobMatcherService()
        match_data = await matcher.calculate_match_score(
            db=db,
            user_id=current_user["user_id"],
            job=job
        )
        
        return match_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating match score: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{job_id}/explain", response_model=JobMatchExplanation)
async def explain_job_match(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get AI-generated explanation of job match
    
    Provides:
    - Detailed match explanation
    - Your key strengths for this role
    - Skill/experience gaps to address
    - Actionable recommendations to improve candidacy
    """
    try:
        matcher = JobMatcherService()
        explanation = await matcher.explain_match(
            db=db,
            user_id=current_user["user_id"],
            job_id=job_id
        )
        
        return explanation
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error explaining match: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{job_id}/save")
async def save_job(
    job_id: str,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Save/bookmark a job for later review
    """
    try:
        from app.models.database import Job, SavedJob
        from datetime import datetime
        import uuid
        
        # Verify job exists
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Check if already saved
        existing = db.query(SavedJob).filter(
            SavedJob.user_id == current_user["user_id"],
            SavedJob.job_id == job_id
        ).first()
        
        if existing:
            return {"message": "Job already saved", "saved_job_id": str(existing.id)}
        
        # Create saved job
        saved_job = SavedJob(
            id=uuid.uuid4(),
            user_id=current_user["user_id"],
            job_id=job_id,
            notes=notes,
            saved_at=datetime.utcnow()
        )
        
        db.add(saved_job)
        db.commit()
        
        return {
            "message": "Job saved successfully",
            "saved_job_id": str(saved_job.id)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving job: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/saved/list")
async def get_saved_jobs(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all saved/bookmarked jobs for current user
    """
    try:
        from app.models.database import SavedJob, Job
        
        saved_jobs = db.query(SavedJob, Job).join(
            Job, SavedJob.job_id == Job.id
        ).filter(
            SavedJob.user_id == current_user["user_id"]
        ).order_by(
            SavedJob.saved_at.desc()
        ).offset(offset).limit(limit).all()
        
        result = []
        for saved_job, job in saved_jobs:
            result.append({
                "saved_at": saved_job.saved_at.isoformat(),
                "notes": saved_job.notes,
                "job": {
                    "id": str(job.id),
                    "title": job.title,
                    "company": job.company_id,
                    "location": job.location,
                    "location_type": job.location_type,
                    "salary_min": job.salary_min,
                    "salary_max": job.salary_max,
                    "posted_at": job.posted_at.isoformat() if job.posted_at else None,
                    "external_url": job.external_url,
                    "apply_url": job.apply_url,
                }
            })
        
        return {
            "saved_jobs": result,
            "total": len(result),
            "offset": offset,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"Error getting saved jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/saved/{job_id}")
async def unsave_job(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Remove a job from saved/bookmarked list
    """
    try:
        from app.models.database import SavedJob
        
        saved_job = db.query(SavedJob).filter(
            SavedJob.user_id == current_user["user_id"],
            SavedJob.job_id == job_id
        ).first()
        
        if not saved_job:
            raise HTTPException(status_code=404, detail="Saved job not found")
        
        db.delete(saved_job)
        db.commit()
        
        return {"message": "Job removed from saved list"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing saved job: {e}")
        raise HTTPException(status_code=500, detail=str(e))
