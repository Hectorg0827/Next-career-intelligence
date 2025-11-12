"""Job marketplace API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from app.db.database import get_db
from app.models.database import Job, JobApplication, SavedJob, JobAlertPreferences
from app.models.job_schemas import (
    JobResponse,
    JobWithMatchScore,
    JobSearchFilters,
    JobSearchResponse,
    JobApplicationCreate,
    JobApplicationUpdate,
    JobApplicationResponse,
    JobApplicationWithDetails,
    SavedJobCreate,
    SavedJobResponse,
    SavedJobWithDetails,
    JobAlertPreferencesCreate,
    JobAlertPreferencesUpdate,
    JobAlertPreferencesResponse,
    ApplicationStats,
)
from app.core.auth import get_current_user
from app.services.ai_matching_service import ai_matching_service
import asyncio

router = APIRouter(prefix="/api/v1", tags=["marketplace"])


# ============================================================================
# JOB ENDPOINTS
# ============================================================================


@router.get("/marketplace/jobs", response_model=JobSearchResponse)
async def search_jobs(
    db: Session = Depends(get_db),
    query: Optional[str] = Query(None, description="Search query"),
    location: Optional[str] = Query(None),
    remote_type: Optional[str] = Query(None),
    min_salary: Optional[int] = Query(None),
    max_salary: Optional[int] = Query(None),
    experience_level: Optional[str] = Query(None),
    skills: Optional[List[str]] = Query(None),
    job_type: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    """Search and filter jobs.

    Query parameters:
    - query: Search in title and description
    - location: Filter by location
    - remote_type: 'remote', 'hybrid', 'on_site'
    - min_salary, max_salary: Salary range
    - experience_level: 'entry', 'mid', 'senior'
    - skills: Array of required skills
    - job_type: 'full_time', 'part_time', 'contract'
    - page: Page number (1-indexed)
    - limit: Results per page
    """

    # Build query
    db_query = db.query(Job).filter(Job.is_active == "active")

    if query:
        search_term = f"%{query}%"
        db_query = db_query.filter((Job.title.ilike(search_term)) | (Job.description.ilike(search_term)))

    if location:
        db_query = db_query.filter(Job.location.ilike(f"%{location}%"))

    if remote_type:
        db_query = db_query.filter(Job.remote_type == remote_type)

    if experience_level:
        db_query = db_query.filter(Job.experience_level == experience_level)

    if job_type:
        db_query = db_query.filter(Job.job_type == job_type)

    if min_salary:
        db_query = db_query.filter(Job.salary_min >= min_salary)

    if max_salary:
        db_query = db_query.filter(Job.salary_max <= max_salary)

    # Get total count
    total = db_query.count()

    # Apply pagination
    offset = (page - 1) * limit
    jobs = db_query.offset(offset).limit(limit).all()

    return JobSearchResponse(
        total=total,
        page=page,
        limit=limit,
        results=[JobWithMatchScore.from_orm(job) for job in jobs],
    )


@router.get("/marketplace/jobs/{job_id}", response_model=JobWithMatchScore)
async def get_job_details(
    job_id: str,
    db: Session = Depends(get_db),
    user_id: Optional[str] = Query(None),
):
    """Get detailed information about a specific job.

    If user_id is provided, includes match score and recommendations.
    """
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    response = JobWithMatchScore.from_orm(job)

    # If user provided, get their application/match info
    if user_id:
        app = (
            db.query(JobApplication)
            .filter(
                JobApplication.user_id == user_id,
                JobApplication.job_id == job_id,
            )
            .first()
        )

        if app:
            response.match_score = app.match_score
            response.skill_gaps = app.skill_gaps
            response.recommended_prep = app.recommended_prep

    return response


# ============================================================================
# JOB APPLICATION ENDPOINTS
# ============================================================================


@router.post("/marketplace/job-applications", response_model=JobApplicationResponse)
async def apply_to_job(
    application: JobApplicationCreate,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Apply to a job."""

    # Verify job exists
    job = db.query(Job).filter(Job.id == application.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Check if already applied
    existing = (
        db.query(JobApplication)
        .filter(
            JobApplication.user_id == current_user,
            JobApplication.job_id == application.job_id,
        )
        .first()
    )

    if existing:
        raise HTTPException(status_code=400, detail="Already applied to this job")

    # Create application
    app_id = f"app_{uuid.uuid4().hex[:12]}"
    db_application = JobApplication(
        id=app_id,
        user_id=current_user,
        job_id=application.job_id,
        status="applied",
    )

    db.add(db_application)
    db.commit()
    db.refresh(db_application)

    return JobApplicationResponse.from_orm(db_application)


@router.get("/marketplace/user/applications", response_model=List[JobApplicationWithDetails])
async def get_user_applications(
    status: Optional[str] = Query(None),
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all applications for the current user."""

    query = db.query(JobApplication).filter(JobApplication.user_id == current_user)

    if status:
        query = query.filter(JobApplication.status == status)

    applications = query.order_by(JobApplication.applied_at.desc()).all()

    result = []
    for app in applications:
        job = db.query(Job).filter(Job.id == app.job_id).first()
        app_dict = JobApplicationResponse.from_orm(app).dict()
        app_dict["job"] = JobResponse.from_orm(job) if job else None
        result.append(JobApplicationWithDetails(**app_dict))

    return result


@router.get("/marketplace/user/applications/{application_id}", response_model=JobApplicationWithDetails)
async def get_application(
    application_id: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get specific application details."""

    app = (
        db.query(JobApplication)
        .filter(
            JobApplication.id == application_id,
            JobApplication.user_id == current_user,
        )
        .first()
    )

    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    job = db.query(Job).filter(Job.id == app.job_id).first()
    app_dict = JobApplicationResponse.from_orm(app).dict()
    app_dict["job"] = JobResponse.from_orm(job) if job else None

    return JobApplicationWithDetails(**app_dict)


@router.put("/marketplace/job-applications/{application_id}", response_model=JobApplicationResponse)
async def update_application(
    application_id: str,
    update: JobApplicationUpdate,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update job application status or details."""

    app = (
        db.query(JobApplication)
        .filter(
            JobApplication.id == application_id,
            JobApplication.user_id == current_user,
        )
        .first()
    )

    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    # Update fields
    update_data = update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(app, field, value)

    db.commit()
    db.refresh(app)

    return JobApplicationResponse.from_orm(app)


@router.delete("/marketplace/job-applications/{application_id}")
async def delete_application(
    application_id: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Withdraw from a job application."""

    app = (
        db.query(JobApplication)
        .filter(
            JobApplication.id == application_id,
            JobApplication.user_id == current_user,
        )
        .first()
    )

    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    db.delete(app)
    db.commit()

    return {"status": "deleted"}


@router.get("/marketplace/user/application-stats", response_model=ApplicationStats)
async def get_application_stats(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get application statistics for current user."""

    applications = db.query(JobApplication).filter(JobApplication.user_id == current_user).all()

    total = len(applications)
    applied = len([a for a in applications if a.status == "applied"])
    interviewing = len([a for a in applications if a.status == "interview"])
    offered = len([a for a in applications if a.status == "offered"])
    rejected = len([a for a in applications if a.status == "rejected"])

    match_scores = [a.match_score for a in applications if a.match_score]
    avg_score = sum(match_scores) / len(match_scores) if match_scores else None

    return ApplicationStats(
        total_applications=total,
        applied=applied,
        interviewing=interviewing,
        offered=offered,
        rejected=rejected,
        average_match_score=avg_score,
    )


# ============================================================================
# SAVED JOBS ENDPOINTS
# ============================================================================


@router.post("/marketplace/saved-jobs", response_model=SavedJobResponse)
async def save_job(
    saved_job: SavedJobCreate,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Save/bookmark a job."""

    # Verify job exists
    job = db.query(Job).filter(Job.id == saved_job.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Check if already saved
    existing = (
        db.query(SavedJob)
        .filter(
            SavedJob.user_id == current_user,
            SavedJob.job_id == saved_job.job_id,
        )
        .first()
    )

    if existing:
        raise HTTPException(status_code=400, detail="Job already saved")

    # Create saved job record
    saved_id = f"saved_{uuid.uuid4().hex[:12]}"
    db_saved = SavedJob(
        id=saved_id,
        user_id=current_user,
        job_id=saved_job.job_id,
        notes=saved_job.notes,
    )

    db.add(db_saved)
    db.commit()
    db.refresh(db_saved)

    return SavedJobResponse.from_orm(db_saved)


@router.get("/marketplace/user/saved-jobs", response_model=List[SavedJobWithDetails])
async def get_saved_jobs(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all saved jobs for current user."""

    saved_jobs = db.query(SavedJob).filter(SavedJob.user_id == current_user).order_by(SavedJob.saved_at.desc()).all()

    result = []
    for saved in saved_jobs:
        job = db.query(Job).filter(Job.id == saved.job_id).first()
        saved_dict = SavedJobResponse.from_orm(saved).dict()
        saved_dict["job"] = JobResponse.from_orm(job) if job else None
        result.append(SavedJobWithDetails(**saved_dict))

    return result


@router.delete("/marketplace/saved-jobs/{saved_id}")
async def remove_saved_job(
    saved_id: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove a job from saved."""

    saved = (
        db.query(SavedJob)
        .filter(
            SavedJob.id == saved_id,
            SavedJob.user_id == current_user,
        )
        .first()
    )

    if not saved:
        raise HTTPException(status_code=404, detail="Saved job not found")

    db.delete(saved)
    db.commit()

    return {"status": "removed"}


# ============================================================================
# JOB ALERT PREFERENCES ENDPOINTS
# ============================================================================


@router.post("/marketplace/job-alert-preferences", response_model=JobAlertPreferencesResponse)
async def create_alert_preferences(
    prefs: JobAlertPreferencesCreate,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create or update job alert preferences for current user."""

    # Check if exists
    existing = db.query(JobAlertPreferences).filter(JobAlertPreferences.user_id == current_user).first()

    if existing:
        # Update existing
        for field, value in prefs.dict(exclude_unset=True).items():
            setattr(existing, field, value)
        db.commit()
        db.refresh(existing)
        return JobAlertPreferencesResponse.from_orm(existing)

    # Create new
    pref_id = f"prefs_{uuid.uuid4().hex[:12]}"
    db_prefs = JobAlertPreferences(id=pref_id, user_id=current_user, **prefs.dict())

    db.add(db_prefs)
    db.commit()
    db.refresh(db_prefs)

    return JobAlertPreferencesResponse.from_orm(db_prefs)


@router.get("/marketplace/job-alert-preferences", response_model=JobAlertPreferencesResponse)
async def get_alert_preferences(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get job alert preferences for current user."""

    prefs = db.query(JobAlertPreferences).filter(JobAlertPreferences.user_id == current_user).first()

    if not prefs:
        raise HTTPException(status_code=404, detail="Preferences not found")

    return JobAlertPreferencesResponse.from_orm(prefs)


@router.put("/marketplace/job-alert-preferences", response_model=JobAlertPreferencesResponse)
async def update_alert_preferences(
    update: JobAlertPreferencesUpdate,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update job alert preferences."""

    prefs = db.query(JobAlertPreferences).filter(JobAlertPreferences.user_id == current_user).first()

    if not prefs:
        raise HTTPException(status_code=404, detail="Preferences not found")

    # Update fields
    update_data = update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(prefs, field, value)

    db.commit()
    db.refresh(prefs)

    return JobAlertPreferencesResponse.from_orm(prefs)


@router.delete("/marketplace/job-alert-preferences")
async def delete_alert_preferences(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete job alert preferences."""

    prefs = db.query(JobAlertPreferences).filter(JobAlertPreferences.user_id == current_user).first()

    if not prefs:
        raise HTTPException(status_code=404, detail="Preferences not found")

    db.delete(prefs)
    db.commit()

    return {"status": "deleted"}


# ============================================================================
# AI MATCHING ENDPOINTS
# ============================================================================


@router.post("/marketplace/calculate-matches")
async def calculate_all_matches(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=100),
):
    """Calculate AI match scores for all jobs.

    Uses the user's career profile to calculate personalized match scores
    for all available jobs using AI intelligence.
    """
    try:
        matches_calculated = await ai_matching_service.calculate_all_matches_for_user(
            user_id=current_user, db=db, limit=limit
        )

        return {
            "status": "success",
            "matches_calculated": matches_calculated,
            "message": f"Calculated matches for {matches_calculated} jobs",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating matches: {str(e)}")


@router.get("/marketplace/user/matched-jobs")
async def get_matched_jobs(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
    min_score: float = Query(60.0, ge=0, le=100),
    limit: int = Query(20, ge=1, le=100),
):
    """Get user's best matched jobs sorted by match score.

    Returns jobs with AI-calculated match scores, skill gaps, and
    preparation recommendations.
    """
    try:
        matched_jobs = await ai_matching_service.get_top_matched_jobs(
            user_id=current_user, db=db, limit=limit, min_score=min_score
        )

        return {"total": len(matched_jobs), "min_score": min_score, "results": matched_jobs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving matched jobs: {str(e)}")


@router.post("/marketplace/jobs/{job_id}/calculate-match")
async def calculate_job_match(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    """Calculate AI match score for a specific job.

    Provides detailed match analysis including:
    - Match score (0-100%)
    - Skill gaps and matches
    - Experience fit assessment
    - Interview preparation recommendations
    """
    try:
        result = await ai_matching_service.refresh_job_match(user_id=current_user, job_id=job_id, db=db)

        if not result:
            raise HTTPException(status_code=404, detail="Job or profile not found")

        return {"status": "success", "data": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating match: {str(e)}")
