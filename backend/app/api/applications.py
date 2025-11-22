"""
Application Tracking API Endpoints
Manage job applications throughout the hiring process
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from loguru import logger

from app.db.database import get_db
from app.services.application_tracking_service import ApplicationTrackingService
from app.core.auth import get_current_user


router = APIRouter(prefix="/applications", tags=["Application Tracking"])


# ============================================================================
# Request/Response Models
# ============================================================================

class CreateApplicationRequest(BaseModel):
    job_id: str
    status: str = "applied"
    match_score: Optional[float] = None
    skill_gaps: Optional[dict] = None
    notes: Optional[str] = None


class UpdateApplicationRequest(BaseModel):
    status: str
    notes: Optional[str] = None
    interview_date: Optional[str] = None  # ISO format
    offer_salary: Optional[float] = None
    offer_status: Optional[str] = None


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/", status_code=201)
async def create_application(
    request: CreateApplicationRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new job application record
    
    Status options: saved, applied, screening, interview, assessment, offer, accepted, rejected, withdrawn
    """
    try:
        service = ApplicationTrackingService()
        
        application = service.create_application(
            db=db,
            user_id=current_user["user_id"],
            job_id=request.job_id,
            status=request.status,
            match_score=request.match_score,
            skill_gaps=request.skill_gaps,
            notes=request.notes
        )
        
        return {
            "message": "Application created successfully",
            "application_id": str(application.id),
            "status": application.status,
            "applied_at": application.applied_at.isoformat()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating application: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def get_applications(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all applications for the current user
    
    Optional status filter to show only specific application stages
    """
    try:
        service = ApplicationTrackingService()
        
        result = service.get_user_applications(
            db=db,
            user_id=current_user["user_id"],
            status=status,
            limit=limit,
            offset=offset
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting applications: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_application_stats(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get application statistics and dashboard data
    
    Returns:
    - Total and active application counts
    - Status breakdown
    - Upcoming interviews
    - Recent activity
    - Response rate
    """
    try:
        service = ApplicationTrackingService()
        
        stats = service.get_application_stats(
            db=db,
            user_id=current_user["user_id"]
        )
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting application stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{application_id}")
async def get_application(
    application_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get detailed information about a specific application
    
    Includes full job details and application history
    """
    try:
        service = ApplicationTrackingService()
        
        application = service.get_application_by_id(
            db=db,
            application_id=application_id,
            user_id=current_user["user_id"]
        )
        
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        
        return application
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting application: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{application_id}")
async def update_application(
    application_id: str,
    request: UpdateApplicationRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update application status and details
    
    Use this to track progress through the hiring pipeline:
    - Move to interview stage
    - Record offer details
    - Note rejection reasons
    - Add interview notes
    """
    try:
        service = ApplicationTrackingService()
        
        # Parse interview date if provided
        interview_date = None
        if request.interview_date:
            try:
                interview_date = datetime.fromisoformat(request.interview_date.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid interview_date format. Use ISO format.")
        
        # Build offer details if provided
        offer_details = None
        if request.offer_salary or request.offer_status:
            offer_details = {
                "salary": request.offer_salary,
                "status": request.offer_status
            }
        
        application = service.update_application_status(
            db=db,
            application_id=application_id,
            user_id=current_user["user_id"],
            status=request.status,
            notes=request.notes,
            interview_date=interview_date,
            offer_details=offer_details
        )
        
        return {
            "message": "Application updated successfully",
            "application_id": str(application.id),
            "status": application.status,
            "updated_at": application.updated_at.isoformat()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating application: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{application_id}")
async def delete_application(
    application_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete an application
    """
    try:
        service = ApplicationTrackingService()
        
        success = service.delete_application(
            db=db,
            application_id=application_id,
            user_id=current_user["user_id"]
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Application not found")
        
        return {"message": "Application deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting application: {e}")
        raise HTTPException(status_code=500, detail=str(e))
