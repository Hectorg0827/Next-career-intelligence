"""
Job Recommendations API Endpoints
Real-time job matching and alert preferences
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from loguru import logger

from app.db.database import get_db
from app.services.job_recommendation_engine import JobRecommendationEngine
from app.core.auth import get_current_user


router = APIRouter(prefix="/recommendations", tags=["Job Recommendations"])


# ============================================================================
# Request/Response Models
# ============================================================================

class AlertPreferencesRequest(BaseModel):
    min_match_score: Optional[float] = 50.0
    email_alerts_enabled: Optional[bool] = True
    alert_frequency: Optional[str] = "daily"  # instant, daily, weekly
    job_title_keywords: Optional[List[str]] = []
    locations: Optional[List[str]] = []
    remote_types: Optional[List[str]] = ["remote"]
    min_salary: Optional[float] = None
    experience_levels: Optional[List[str]] = []
    required_skills: Optional[List[str]] = []
    excluded_keywords: Optional[List[str]] = []


# ============================================================================
# Endpoints
# ============================================================================

@router.get("/new")
async def get_new_recommendations(
    hours_since: int = Query(24, ge=1, le=168, description="Check for jobs posted in last N hours"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get new job recommendations based on recently posted jobs
    
    Returns jobs posted in the specified time window that match your profile
    """
    try:
        engine = JobRecommendationEngine()
        
        recommendations = await engine.get_new_job_recommendations(
            db=db,
            user_id=current_user["user_id"],
            hours_since=hours_since
        )
        
        return {
            "recommendations": recommendations,
            "count": len(recommendations),
            "hours_checked": hours_since
        }
        
    except Exception as e:
        logger.error(f"Error getting new recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/process")
async def process_recommendations(
    background_tasks: BackgroundTasks,
    send_email: bool = Query(True, description="Send email notification if matches found"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Manually trigger recommendation processing
    
    Checks for new matches and optionally sends email notification
    """
    try:
        engine = JobRecommendationEngine()
        
        # Run in background
        result = await engine.process_user_recommendations(
            db=db,
            user_id=current_user["user_id"],
            send_email=send_email
        )
        
        return {
            "message": "Recommendations processed successfully",
            "new_recommendations": result["new_recommendations"],
            "email_sent": result["email_sent"],
            "top_matches": result.get("top_matches", [])
        }
        
    except Exception as e:
        logger.error(f"Error processing recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/preferences")
async def get_alert_preferences(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get current job alert preferences
    """
    try:
        engine = JobRecommendationEngine()
        
        preferences = await engine.get_user_preferences(
            db=db,
            user_id=current_user["user_id"]
        )
        
        return preferences
        
    except Exception as e:
        logger.error(f"Error getting preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/preferences")
async def update_alert_preferences(
    request: AlertPreferencesRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update job alert preferences
    
    Configure:
    - Minimum match score threshold
    - Email notification settings
    - Alert frequency (instant, daily, weekly)
    - Job title keywords to match
    - Preferred locations
    - Remote work preferences
    - Salary requirements
    - Required skills
    - Keywords to exclude
    """
    try:
        engine = JobRecommendationEngine()
        
        preferences_dict = request.dict(exclude_none=True)
        
        updated = await engine.update_user_preferences(
            db=db,
            user_id=current_user["user_id"],
            preferences=preferences_dict
        )
        
        return {
            "message": "Preferences updated successfully",
            "preferences": {
                "min_match_score": updated.min_match_score,
                "email_alerts_enabled": updated.email_alerts_enabled,
                "alert_frequency": updated.alert_frequency,
                "job_title_keywords": updated.job_title_keywords,
                "locations": updated.locations,
                "remote_types": updated.remote_types,
                "min_salary": updated.min_salary,
            }
        }
        
    except Exception as e:
        logger.error(f"Error updating preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-email")
async def send_test_email(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Send a test email notification to verify email setup
    """
    try:
        engine = JobRecommendationEngine()
        
        # Get latest recommendations
        recommendations = await engine.get_new_job_recommendations(
            db=db,
            user_id=current_user["user_id"],
            hours_since=168  # Last week
        )
        
        if not recommendations:
            return {
                "message": "No recommendations available to send test email",
                "email_sent": False
            }
        
        # Send email
        email_sent = await engine.send_job_alert_email(
            db=db,
            user_id=current_user["user_id"],
            recommendations=recommendations
        )
        
        return {
            "message": "Test email sent" if email_sent else "Failed to send test email",
            "email_sent": email_sent,
            "recommendations_count": len(recommendations)
        }
        
    except Exception as e:
        logger.error(f"Error sending test email: {e}")
        raise HTTPException(status_code=500, detail=str(e))
