"""
AI Agents API Endpoints

Exposes all Phase 2 autonomous AI agents:
- Memory Layer
- Recommendation Engine
- Proactive Guidance
- Predictive Analytics
- Smart Profile Assistant
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from app.core.auth import get_current_user
from app.services.foundation.ai import (
    ai_memory,
    recommendation_engine,
    proactive_guidance,
    predictive_analytics,
    profile_assistant,
    ProfileCompletenessLevel
)

router = APIRouter(prefix="/ai", tags=["AI Agents"])


# ============================================================================
# Request/Response Models
# ============================================================================

class MemoryResponse(BaseModel):
    memory_id: str
    content: str
    memory_type: str
    created_at: datetime
    confidence: float


class RecommendationResponse(BaseModel):
    job_id: str
    score: float
    match_reasons: List[str]
    growth_potential: Optional[str]
    is_stretch: bool


class GuidanceResponse(BaseModel):
    guidance_type: str
    priority: int
    content: str
    action_items: List[str]


class ChurnPredictionResponse(BaseModel):
    risk_level: str
    churn_probability: float
    days_until_churn: Optional[int]
    risk_factors: List[str]
    recommended_actions: List[str]


class SuccessPredictionResponse(BaseModel):
    success_probability: float
    estimated_days_to_hire: Optional[int]
    positive_signals: List[str]
    improvement_areas: List[str]


class ProfileAnalysisResponse(BaseModel):
    completeness_level: str
    completeness_score: float
    missing_fields: List[str]
    incomplete_fields: List[str]
    suggestions_count: int
    inferred_skills: List[str]
    strengths: List[str]
    weaknesses: List[str]


class ProfileSuggestionResponse(BaseModel):
    field: str
    suggestion_type: str
    suggested_value: str
    reasoning: str
    priority: int
    impact_score: float


# ============================================================================
# AI Memory Endpoints
# ============================================================================

@router.post("/memory/form")
async def form_memory(
    event_category: str = Query(..., description="Event category (JOB, PROFILE, APPLICATION, etc.)"),
    days: int = Query(7, description="Number of days to look back"),
    current_user: dict = Depends(get_current_user)
):
    """
    Form semantic memory from recent events
    
    This endpoint analyzes user events and creates semantic memories
    that capture behavioral patterns and preferences.
    """
    try:
        memory = await ai_memory.form_memory_from_events(
            user_id=current_user["id"],
            event_category=event_category,
            days=days
        )
        
        if not memory:
            return {
                "success": False,
                "message": "Insufficient events to form memory",
                "memory": None
            }
        
        return {
            "success": True,
            "message": "Memory formed successfully",
            "memory": {
                "memory_id": memory.memory_id,
                "content": memory.content,
                "memory_type": memory.memory_type,
                "created_at": memory.created_at,
                "confidence": memory.confidence
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error forming memory: {str(e)}")


@router.get("/memory/context")
async def get_user_context(
    current_user: dict = Depends(get_current_user)
):
    """
    Get complete AI context for user
    
    Returns all memories, recent goals, engagement patterns, and AI readiness.
    """
    try:
        context = await ai_memory.get_user_context(current_user["id"])
        
        return {
            "success": True,
            "context": context
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting context: {str(e)}")


# ============================================================================
# Recommendation Engine Endpoints
# ============================================================================

@router.get("/recommendations")
async def get_recommendations(
    limit: int = Query(10, ge=1, le=50, description="Number of recommendations"),
    include_stretch: bool = Query(True, description="Include stretch recommendations"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get AI-powered job recommendations
    
    Uses multi-factor scoring (skills, behavior, goals, growth, engagement)
    to recommend jobs personalized for the user.
    """
    try:
        recommendations = await recommendation_engine.get_recommendations(
            user_id=current_user["id"],
            limit=limit,
            include_stretch=include_stretch
        )
        
        return {
            "success": True,
            "count": len(recommendations),
            "recommendations": [
                {
                    "job_id": rec.job_id,
                    "score": rec.recommendation_score,
                    "match_reasons": rec.match_reasons,
                    "growth_potential": rec.growth_potential,
                    "is_stretch": rec.is_stretch,
                    "confidence": rec.confidence
                }
                for rec in recommendations
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting recommendations: {str(e)}")


# ============================================================================
# Proactive Guidance Endpoints
# ============================================================================

@router.get("/guidance")
async def get_guidance(
    current_user: dict = Depends(get_current_user)
):
    """
    Get proactive guidance messages
    
    AI analyzes user behavior and provides timely guidance on:
    - Profile completion
    - Application behavior
    - Skill gaps
    - Salary negotiation
    - Career direction
    - Re-engagement
    - Milestone celebration
    """
    try:
        guidance_messages = await proactive_guidance.get_guidance_for_user(
            current_user["id"]
        )
        
        return {
            "success": True,
            "count": len(guidance_messages),
            "messages": [
                {
                    "guidance_type": msg.guidance_type.value,
                    "priority": msg.priority,
                    "content": msg.content,
                    "action_items": msg.action_items,
                    "impact_description": msg.impact_description
                }
                for msg in guidance_messages
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting guidance: {str(e)}")


# ============================================================================
# Predictive Analytics Endpoints
# ============================================================================

@router.get("/predictions/churn")
async def predict_churn(
    current_user: dict = Depends(get_current_user)
):
    """
    Predict user churn risk
    
    Analyzes engagement patterns to predict if user will abandon platform.
    Returns risk level (low/medium/high/critical) with recommended actions.
    """
    try:
        prediction = await predictive_analytics.predict_churn(current_user["id"])
        
        return {
            "success": True,
            "prediction": {
                "risk_level": prediction.risk_level.value,
                "churn_probability": prediction.churn_probability,
                "days_until_churn": prediction.days_until_churn,
                "risk_factors": prediction.risk_factors,
                "recommended_actions": prediction.recommended_actions,
                "confidence": prediction.confidence
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error predicting churn: {str(e)}")


@router.get("/predictions/success")
async def predict_success(
    current_user: dict = Depends(get_current_user)
):
    """
    Predict job search success
    
    Estimates likelihood of getting hired and expected timeline.
    """
    try:
        prediction = await predictive_analytics.predict_success(current_user["id"])
        
        return {
            "success": True,
            "prediction": {
                "success_probability": prediction.success_probability,
                "estimated_days_to_hire": prediction.estimated_days_to_hire,
                "positive_signals": prediction.positive_signals,
                "improvement_areas": prediction.improvement_areas,
                "confidence": prediction.confidence
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error predicting success: {str(e)}")


@router.get("/predictions/engagement")
async def forecast_engagement(
    days: int = Query(7, ge=1, le=30, description="Days to forecast"),
    current_user: dict = Depends(get_current_user)
):
    """
    Forecast future engagement levels
    
    Predicts how active user will be in coming days.
    """
    try:
        forecast = await predictive_analytics.forecast_engagement(
            user_id=current_user["id"],
            days_ahead=days
        )
        
        return {
            "success": True,
            "forecast": {
                "predicted_events_per_week": forecast.predicted_events_per_week,
                "trend": forecast.trend.value,
                "confidence": forecast.confidence,
                "historical_avg": forecast.historical_avg
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error forecasting engagement: {str(e)}")


@router.get("/predictions/intervention-time")
async def get_intervention_time(
    current_user: dict = Depends(get_current_user)
):
    """
    Get optimal time to send nudges/notifications
    
    AI learns when user is most likely to engage.
    """
    try:
        timing = await predictive_analytics.optimal_intervention_time(
            current_user["id"]
        )
        
        return {
            "success": True,
            "timing": {
                "best_day": timing.best_day.value,
                "best_hour": timing.best_hour,
                "confidence": timing.confidence,
                "reasoning": timing.reasoning
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting intervention time: {str(e)}")


# ============================================================================
# Smart Profile Assistant Endpoints
# ============================================================================

@router.get("/profile/analysis")
async def analyze_profile(
    current_user: dict = Depends(get_current_user)
):
    """
    Analyze profile completeness
    
    Returns completeness score, missing fields, and improvement suggestions.
    """
    try:
        analysis = await profile_assistant.analyze_profile(current_user["id"])
        
        return {
            "success": True,
            "analysis": {
                "completeness_level": analysis.completeness_level.value,
                "completeness_score": analysis.completeness_score,
                "missing_fields": analysis.missing_fields,
                "incomplete_fields": analysis.incomplete_fields,
                "suggestions_count": len(analysis.suggestions),
                "inferred_skills": analysis.inferred_skills,
                "strengths": analysis.strengths,
                "weaknesses": analysis.weaknesses
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing profile: {str(e)}")


@router.get("/profile/suggestions")
async def get_profile_suggestions(
    current_user: dict = Depends(get_current_user)
):
    """
    Get prioritized profile improvement suggestions
    
    Returns top 5 suggestions ranked by priority and impact.
    """
    try:
        suggestions = await profile_assistant.suggest_next_steps(current_user["id"])
        
        return {
            "success": True,
            "count": len(suggestions),
            "suggestions": [
                {
                    "field": sug.field,
                    "suggestion_type": sug.suggestion_type,
                    "current_value": sug.current_value,
                    "suggested_value": sug.suggested_value,
                    "reasoning": sug.reasoning,
                    "priority": sug.priority,
                    "impact_score": sug.impact_score
                }
                for sug in suggestions
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting suggestions: {str(e)}")


@router.post("/profile/infer")
async def infer_missing_data(
    current_user: dict = Depends(get_current_user)
):
    """
    Infer missing profile data from context
    
    AI infers location, seniority, salary, skills, and preferences
    from available information.
    """
    try:
        inferred = await profile_assistant.infer_missing_data(current_user["id"])
        
        return {
            "success": True,
            "inferred_count": len(inferred),
            "inferred_data": inferred
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inferring data: {str(e)}")


@router.post("/profile/generate-summary")
async def generate_summary(
    current_user: dict = Depends(get_current_user)
):
    """
    Generate professional profile summary
    
    AI writes a compelling 2-3 sentence summary from profile data.
    """
    try:
        summary = await profile_assistant.generate_summary(current_user["id"])
        
        if not summary:
            return {
                "success": False,
                "message": "Unable to generate summary. Gemini API key may be missing or profile data insufficient.",
                "summary": None
            }
        
        return {
            "success": True,
            "summary": summary
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")


@router.post("/profile/optimize-ats")
async def optimize_for_ats(
    job_description: str = Query(..., description="Target job description"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get ATS optimization suggestions
    
    Compares profile against job description and suggests improvements
    for Applicant Tracking Systems.
    """
    try:
        suggestions = await profile_assistant.optimize_for_ats(
            user_id=current_user["id"],
            job_description=job_description
        )
        
        return {
            "success": True,
            "count": len(suggestions),
            "suggestions": suggestions
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error optimizing for ATS: {str(e)}")


# ============================================================================
# Combined Intelligence Endpoint
# ============================================================================

@router.get("/intelligence")
async def get_user_intelligence(
    current_user: dict = Depends(get_current_user)
):
    """
    Get complete AI intelligence for user
    
    Returns insights from all AI agents in one call:
    - Memory context
    - Recommendations
    - Guidance messages
    - Predictions (churn, success, engagement)
    - Profile analysis
    
    Use this for dashboard overview.
    """
    try:
        # Get insights from all agents
        context = await ai_memory.get_user_context(current_user["id"])
        recommendations = await recommendation_engine.get_recommendations(
            current_user["id"], 
            limit=5
        )
        guidance = await proactive_guidance.get_guidance_for_user(current_user["id"])
        churn = await predictive_analytics.predict_churn(current_user["id"])
        success = await predictive_analytics.predict_success(current_user["id"])
        profile = await profile_assistant.analyze_profile(current_user["id"])
        
        return {
            "success": True,
            "intelligence": {
                "memory": {
                    "memory_count": context["memory_count"],
                    "ai_ready": context["ai_ready"]
                },
                "recommendations": {
                    "count": len(recommendations),
                    "top_matches": [
                        {
                            "job_id": rec.job_id,
                            "score": rec.recommendation_score
                        }
                        for rec in recommendations[:3]
                    ]
                },
                "guidance": {
                    "count": len(guidance),
                    "high_priority": [
                        msg.content 
                        for msg in guidance 
                        if msg.priority == 1
                    ][:3]
                },
                "predictions": {
                    "churn_risk": churn.risk_level.value,
                    "churn_probability": churn.churn_probability,
                    "success_probability": success.success_probability
                },
                "profile": {
                    "completeness": profile.completeness_score,
                    "level": profile.completeness_level.value,
                    "suggestions_count": len(profile.suggestions)
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting intelligence: {str(e)}")
