"""
Enhanced Intelligence API
New endpoints for advanced career intelligence features
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from loguru import logger

from app.core.auth import get_current_user
from app.services.orchestrator import CareerOrchestrator
from app.services.agents.trajectory_agent import TrajectoryAgent
from app.services.agents.market_intel_agent import MarketIntelAgent
from app.services.agents.early_warning_agent import EarlyWarningAgent
from app.services.agents.negotiation_agent import NegotiationAgent
from app.services.agents.peer_benchmarking_agent import PeerBenchmarkingAgent


router = APIRouter(prefix="/api/intelligence", tags=["Enhanced Intelligence"])

# Initialize agents
orchestrator = CareerOrchestrator()


# Request/Response Models
class CareerForecastRequest(BaseModel):
    current_role: Optional[str] = None
    time_horizon_years: int = 3


class MarketSnapshotRequest(BaseModel):
    role: str
    location: Optional[str] = None
    industry: Optional[str] = None


class OfferAnalysisRequest(BaseModel):
    job_title: str
    job_location: Optional[str] = None
    offer_details: Dict[str, Any]


@router.get("/career-forecast")
async def get_career_forecast(
    time_horizon: int = 3,
    current_user: Dict = Depends(get_current_user)
):
    """
    Get AI-powered career trajectory forecast
    
    Premium/Elite feature - predicts career paths over 3-5 year horizon
    """
    try:
        user_id = current_user.get("uid")
        
        # Get user profile
        user_profile = await orchestrator.profile_agent.get_profile(user_id)
        
        if not user_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        # Generate forecast
        forecast = await orchestrator.trajectory_agent.forecast_career_path(
            user_profile=user_profile,
            time_horizon_years=time_horizon
        )
        
        logger.info(f"Generated career forecast for user {user_id}")
        
        return {
            "success": True,
            "forecast": forecast,
            "generated_for": user_profile.job_title or "Current role"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Career forecast failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate career forecast"
        )


@router.get("/market-snapshot/{role}")
async def get_market_snapshot(
    role: str,
    location: Optional[str] = None,
    current_user: Dict = Depends(get_current_user)
):
    """
    Get real-time market intelligence snapshot for a role
    
    Returns demand levels, salary trends, hot skills
    """
    try:
        # Get market snapshot
        snapshot = await orchestrator.market_intel_agent.get_market_snapshot(
            role=role,
            location=location
        )
        
        logger.info(f"Market snapshot for {role}: {snapshot.get('demand_level')}")
        
        return {
            "success": True,
            "snapshot": snapshot,
            "role": role
        }
        
    except Exception as e:
        logger.error(f"Market snapshot failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch market snapshot"
        )


@router.get("/salary-trends/{role}")
async def get_salary_trends(
    role: str,
    location: Optional[str] = None,
    years_experience: Optional[int] = None,
    current_user: Dict = Depends(get_current_user)
):
    """
    Get salary trend analysis for a specific role
    
    Returns current ranges, trends, and percentile breakdown
    """
    try:
        salary_data = await orchestrator.market_intel_agent.analyze_salary_trends(
            role=role,
            location=location,
            years_experience=years_experience
        )
        
        return {
            "success": True,
            "salary_data": salary_data,
            "role": role
        }
        
    except Exception as e:
        logger.error(f"Salary trends analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze salary trends"
        )


@router.get("/risk-scan")
async def get_risk_scan(
    current_user: Dict = Depends(get_current_user)
):
    """
    Comprehensive career risk scan
    
    Elite feature - scans for threats to career stability
    """
    try:
        user_id = current_user.get("uid")
        
        # Get user profile
        user_profile = await orchestrator.profile_agent.get_profile(user_id)
        
        if not user_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        # Generate risk report
        risk_report = await orchestrator.early_warning_agent.generate_risk_report(
            user_profile=user_profile
        )
        
        logger.info(f"Risk scan for user {user_id}: {risk_report.get('overall_risk_score')} score")
        
        return {
            "success": True,
            "risk_report": risk_report
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Risk scan failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete risk scan"
        )


@router.post("/analyze-offer")
async def analyze_job_offer(
    request: OfferAnalysisRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    Analyze a job offer with negotiation intelligence
    
    Pro/Elite feature - provides comprehensive offer analysis
    """
    try:
        user_id = current_user.get("uid")
        
        # Get user profile
        user_profile = await orchestrator.profile_agent.get_profile(user_id)
        
        if not user_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        # Create simplified job object
        from app.models.orchestrator_schemas import JobOpportunity
        job = JobOpportunity(
            title=request.job_title,
            location=request.job_location,
            company="",
            description=""
        )
        
        # Analyze offer
        analysis = await orchestrator.negotiation_agent.analyze_offer(
            user_profile=user_profile,
            job=job,
            offer_details=request.offer_details
        )
        
        logger.info(f"Offer analysis complete for user {user_id}")
        
        return {
            "success": True,
            "analysis": analysis
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Offer analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze offer"
        )


@router.get("/peer-benchmark")
async def get_peer_benchmark(
    current_user: Dict = Depends(get_current_user)
):
    """
    Get comprehensive peer benchmarking report
    
    Pro/Elite feature - compares user against career peers
    """
    try:
        user_id = current_user.get("uid")
        
        # Get user profile
        user_profile = await orchestrator.profile_agent.get_profile(user_id)
        
        if not user_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        # Generate benchmark report
        benchmark = await orchestrator.peer_benchmarking_agent.generate_benchmark_report(
            user_profile=user_profile
        )
        
        logger.info(f"Peer benchmark for user {user_id}: {benchmark.get('overall_percentile')}th percentile")
        
        return {
            "success": True,
            "benchmark": benchmark
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Peer benchmarking failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate peer benchmark"
        )


@router.get("/emerging-skills/{industry}")
async def get_emerging_skills(
    industry: str,
    lookback_months: int = 6,
    current_user: Dict = Depends(get_current_user)
):
    """
    Get emerging skills trending in an industry
    
    Identifies skills with rapid demand growth
    """
    try:
        skills = await orchestrator.market_intel_agent.identify_emerging_skills(
            industry=industry,
            lookback_months=lookback_months
        )
        
        return {
            "success": True,
            "industry": industry,
            "emerging_skills": skills
        }
        
    except Exception as e:
        logger.error(f"Emerging skills identification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to identify emerging skills"
        )


@router.get("/market-disruptions/{industry}")
async def get_market_disruptions(
    industry: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Detect major market disruptions affecting industry
    
    Returns threats and recommended actions
    """
    try:
        user_id = current_user.get("uid")
        
        # Get user profile for context
        user_profile = await orchestrator.profile_agent.get_profile(user_id)
        
        disruptions = await orchestrator.market_intel_agent.detect_market_disruptions(
            industry=industry,
            user_profile=user_profile
        )
        
        return {
            "success": True,
            "industry": industry,
            "disruptions": disruptions
        }
        
    except Exception as e:
        logger.error(f"Market disruptions detection failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to detect market disruptions"
        )


@router.get("/progression-timing/{target_role}")
async def get_progression_timing(
    target_role: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Analyze optimal timing for career progression
    
    Elite feature - tells when user should make career move
    """
    try:
        user_id = current_user.get("uid")
        
        # Get user profile
        user_profile = await orchestrator.profile_agent.get_profile(user_id)
        
        if not user_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        # Analyze timing
        timing = await orchestrator.trajectory_agent.analyze_progression_timing(
            user_profile=user_profile,
            target_role=target_role
        )
        
        return {
            "success": True,
            "target_role": target_role,
            "timing_analysis": timing
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Progression timing analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze progression timing"
        )
