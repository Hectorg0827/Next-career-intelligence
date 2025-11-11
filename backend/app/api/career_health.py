"""
Career Health Score API

Endpoints for calculating and retrieving Career Health Scores
"""

from fastapi import APIRouter, Depends, HTTPException
from app.services.career_health_score import chs_calculator, CareerHealthScore
from app.core.auth import get_current_user
from app.db.supabase import get_supabase_client
from loguru import logger
from datetime import datetime, timedelta
from typing import List

router = APIRouter(prefix="/api/career-health", tags=["career_health"])


@router.get("/score", response_model=CareerHealthScore)
async def get_career_health_score(current_user = Depends(get_current_user)):
    """
    Get current Career Health Score for authenticated user

    Returns:
        CareerHealthScore with breakdown and recommendations
    """
    try:
        score = await chs_calculator.calculate(current_user.id)
        logger.info(f"CHS calculated for user {current_user.id}: {score.overall_score}")
        return score

    except Exception as e:
        logger.error(f"Failed to calculate CHS: {e}")
        raise HTTPException(status_code=500, detail="Failed to calculate Career Health Score")


@router.get("/history")
async def get_score_history(
    limit: int = 30,
    current_user = Depends(get_current_user)
):
    """
    Get historical Career Health Scores

    Args:
        limit: Number of historical records to return (default: 30)

    Returns:
        List of historical scores with dates
    """
    try:
        supabase = get_supabase_client()
        if not supabase:
            raise HTTPException(503, "Database unavailable")
            
        response = supabase.table("career_health_history") \
            .select("score, grade, created_at") \
            .eq("user_id", current_user.id) \
            .order("created_at", desc=True) \
            .limit(limit) \
            .execute()

        history = response.data if response.data else []

        return {
            "user_id": current_user.id,
            "history": history,
            "total_records": len(history)
        }

    except Exception as e:
        logger.error(f"Failed to fetch CHS history: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch score history")


@router.get("/insights")
async def get_career_insights(current_user = Depends(get_current_user)):
    """
    Get detailed career insights and analytics

    Returns:
        Comprehensive insights including:
        - Current CHS
        - Historical trend
        - Peer comparison
        - Personalized recommendations
    """
    try:
        supabase = get_supabase_client()
        if not supabase:
            raise HTTPException(503, "Database unavailable")
            
        # Calculate current score
        current_score = await chs_calculator.calculate(current_user.id)

        # Get history for trend
        history_response = supabase.table("career_health_history") \
            .select("score, created_at") \
            .eq("user_id", current_user.id) \
            .order("created_at", desc=True) \
            .limit(7) \
            .execute()

        history = history_response.data if history_response.data else []

        # Calculate trend
        trend_data = []
        if history:
            # Reverse to get chronological order
            history.reverse()
            trend_data = [
                {
                    "date": record["created_at"],
                    "score": record["score"]
                }
                for record in history
            ]

        # Peer comparison (simplified - can be enhanced)
        peer_avg_score = 65  # TODO: Calculate from actual user data

        # Time to next milestone
        next_milestone = None
        if current_score.overall_score < 70:
            next_milestone = {"score": 70, "grade": "C", "description": "Solid Career Health"}
        elif current_score.overall_score < 80:
            next_milestone = {"score": 80, "grade": "B", "description": "Strong Career Health"}
        elif current_score.overall_score < 90:
            next_milestone = {"score": 90, "grade": "A", "description": "Excellent Career Health"}

        return {
            "current_score": current_score.dict(),
            "trend": {
                "direction": current_score.trend,
                "data": trend_data
            },
            "peer_comparison": {
                "your_score": current_score.overall_score,
                "peer_average": peer_avg_score,
                "percentile": _calculate_percentile(current_score.overall_score, peer_avg_score)
            },
            "next_milestone": next_milestone,
            "last_updated": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to generate career insights: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate insights")


@router.post("/refresh")
async def refresh_score(current_user = Depends(get_current_user)):
    """
    Force recalculation of Career Health Score

    Useful after user updates profile or completes an action
    """
    try:
        score = await chs_calculator.calculate(current_user.id)

        return {
            "status": "refreshed",
            "score": score.overall_score,
            "grade": score.grade,
            "message": "Career Health Score updated successfully"
        }

    except Exception as e:
        logger.error(f"Failed to refresh CHS: {e}")
        raise HTTPException(status_code=500, detail="Failed to refresh score")


def _calculate_percentile(user_score: int, peer_avg: int) -> int:
    """
    Calculate approximate percentile

    Simple formula - can be enhanced with actual distribution
    """
    if user_score >= peer_avg + 20:
        return 90
    elif user_score >= peer_avg + 10:
        return 75
    elif user_score >= peer_avg:
        return 60
    elif user_score >= peer_avg - 10:
        return 40
    else:
        return 25
