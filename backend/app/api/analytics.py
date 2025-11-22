"""
Analytics API Endpoints
Dashboard metrics and user activity insights
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from loguru import logger

from app.db.database import get_db
from app.services.analytics_service import AnalyticsService
from app.core.auth import get_current_user


router = APIRouter(prefix="/analytics", tags=["Analytics & Insights"])


# ============================================================================
# Endpoints
# ============================================================================

@router.get("/dashboard")
async def get_dashboard_metrics(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get comprehensive dashboard metrics
    
    Returns:
    - Job search activity summary
    - Application status breakdown
    - AI Coach usage statistics
    - Skills profile overview
    """
    try:
        service = AnalyticsService()
        
        summary = service.get_user_activity_summary(
            db=db,
            user_id=current_user["user_id"],
            days=days
        )
        
        return summary
        
    except Exception as e:
        logger.error(f"Error getting dashboard metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/timeline")
async def get_activity_timeline(
    days: int = Query(90, ge=7, le=365, description="Number of days to show"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get application activity timeline
    
    Returns daily application counts for chart visualization
    """
    try:
        service = AnalyticsService()
        
        timeline = service.get_application_timeline(
            db=db,
            user_id=current_user["user_id"],
            days=days
        )
        
        return {
            "timeline": timeline,
            "period_days": days
        }
        
    except Exception as e:
        logger.error(f"Error getting timeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/success-metrics")
async def get_success_metrics(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get success rates and conversion metrics
    
    Returns:
    - Response rate (applications that got responses)
    - Interview rate (applications that led to interviews)
    - Offer rate (applications that resulted in offers)
    - Average time to response
    """
    try:
        service = AnalyticsService()
        
        metrics = service.get_success_metrics(
            db=db,
            user_id=current_user["user_id"]
        )
        
        return metrics
        
    except Exception as e:
        logger.error(f"Error getting success metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/skill-gaps")
async def get_skill_gap_insights(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Analyze skill gaps across all applications
    
    Returns:
    - Most commonly missing skills
    - Average match score
    - Skills to prioritize learning
    """
    try:
        service = AnalyticsService()
        
        insights = service.get_skill_gap_insights(
            db=db,
            user_id=current_user["user_id"]
        )
        
        return insights
        
    except Exception as e:
        logger.error(f"Error getting skill gap insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top-categories")
async def get_top_job_categories(
    limit: int = Query(10, ge=1, le=50, description="Number of categories to return"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get most applied-to job categories/titles
    
    Helps identify user's job search focus areas
    """
    try:
        service = AnalyticsService()
        
        categories = service.get_top_job_categories(
            db=db,
            user_id=current_user["user_id"],
            limit=limit
        )
        
        return {
            "categories": categories,
            "total": len(categories)
        }
        
    except Exception as e:
        logger.error(f"Error getting top categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/engagement")
async def get_platform_engagement(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get platform usage and engagement statistics
    
    Returns:
    - AI Coach session count
    - Job search activity
    - Application updates
    - Overall engagement score and level
    """
    try:
        service = AnalyticsService()
        
        stats = service.get_platform_usage_stats(
            db=db,
            user_id=current_user["user_id"],
            days=days
        )
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting engagement stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendations-performance")
async def get_recommendations_performance(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Analyze how well AI recommendations perform
    
    Returns:
    - Average match score of applied recommendations
    - Success rate for high-match recommendations
    - Overall recommendation quality assessment
    """
    try:
        service = AnalyticsService()
        
        performance = service.get_recommendations_performance(
            db=db,
            user_id=current_user["user_id"]
        )
        
        return performance
        
    except Exception as e:
        logger.error(f"Error getting recommendations performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/overview")
async def get_complete_overview(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get complete analytics overview for homepage dashboard
    
    Combines all key metrics in a single call
    """
    try:
        service = AnalyticsService()
        
        # Gather all metrics
        activity_summary = service.get_user_activity_summary(db, current_user["user_id"], days=30)
        success_metrics = service.get_success_metrics(db, current_user["user_id"])
        skill_insights = service.get_skill_gap_insights(db, current_user["user_id"])
        engagement = service.get_platform_usage_stats(db, current_user["user_id"], days=30)
        rec_performance = service.get_recommendations_performance(db, current_user["user_id"])
        
        return {
            "activity": activity_summary,
            "success": success_metrics,
            "skills": skill_insights,
            "engagement": engagement,
            "recommendations": rec_performance
        }
        
    except Exception as e:
        logger.error(f"Error getting complete overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))
