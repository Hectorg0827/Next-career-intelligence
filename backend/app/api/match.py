"""
Match API - Job-User Compatibility Analysis
Exposes the multi-agent orchestrator via REST API
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from loguru import logger

from app.services.orchestrator import CareerOrchestrator
from app.models.orchestrator_schemas import OrchestratorOutput, JobOpportunity
from app.models.user_profile import UserProfile


router = APIRouter(prefix="/match", tags=["Career Matching"])

# Lazy initialize orchestrator on first use to avoid blocking app startup
_orchestrator = None


def get_orchestrator():
    """Lazy load orchestrator on first use"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = CareerOrchestrator()
    return _orchestrator


class MatchRequest(BaseModel):
    """Request to analyze a job match"""

    user_id: str
    job: JobOpportunity
    recent_conversation: Optional[str] = None


class RankJobsRequest(BaseModel):
    """Request to rank multiple jobs"""

    user_id: str
    jobs: List[JobOpportunity]


@router.post("/analyze", response_model=OrchestratorOutput)
async def analyze_job_match(request: MatchRequest = Body(...)):
    """
    Analyze compatibility between a user and a job opportunity

    This endpoint runs the full multi-agent analysis:
    - Retrieves user profile (source of truth)
    - Assesses AI displacement risk
    - Calculates compatibility score
    - Identifies skill gaps
    - Generates next steps
    - Updates user profile with learnings
    - Provides questions for coach

    Returns standardized OrchestratorOutput JSON.
    """

    try:
        logger.info(f"Match analysis request for user {request.user_id}")

        result = await get_orchestrator().analyze_job_match(
            user_id=request.user_id, job=request.job, recent_conversation=request.recent_conversation
        )

        return result

    except Exception as e:
        logger.error(f"Error in match analysis: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to analyze job match: {str(e)}")


@router.post("/rank")
async def rank_jobs(request: RankJobsRequest = Body(...)):
    """
    Rank multiple job opportunities for a user

    Analyzes all jobs and returns them sorted by overall recommendation score.
    Considers:
    - Compatibility
    - Stability (AI displacement risk)
    - Trajectory (long-term career growth)

    Returns sorted list with full analysis for each job.
    """

    try:
        logger.info(f"Ranking {len(request.jobs)} jobs for user {request.user_id}")

        ranked = await get_orchestrator().rank_jobs(user_id=request.user_id, jobs=request.jobs)

        return {"user_id": request.user_id, "total_jobs": len(ranked), "ranked_jobs": ranked}

    except Exception as e:
        logger.error(f"Error ranking jobs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to rank jobs: {str(e)}")


@router.get("/profile/{user_id}")
async def get_user_profile(user_id: str):
    """
    Retrieve the complete User Profile (source of truth)

    Returns the persistent, evolving record of the user's career identity.
    """

    try:
        profile = await get_orchestrator().profile_agent.get_profile(user_id)

        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")

        return profile

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving profile: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve profile: {str(e)}")


@router.post("/profile/{user_id}/create")
async def create_user_profile(user_id: str, email: Optional[str] = None):
    """
    Create a new User Profile

    Initializes an empty profile that will be populated over time.
    """

    try:
        profile = await get_orchestrator().profile_agent.create_profile(user_id, email)

        return {"message": "Profile created successfully", "profile": profile}

    except Exception as e:
        logger.error(f"Error creating profile: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create profile: {str(e)}")


@router.get("/user/{user_id}/current-job-risk")
async def assess_current_job_risk(user_id: str):
    """
    Assess AI displacement risk for user's CURRENT job

    Helps identify if user needs to transition urgently.
    """

    try:
        profile = await get_orchestrator().profile_agent.get_profile(user_id)

        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")

        risk_assessment = await get_orchestrator().risk_agent.assess_current_job_risk(profile)

        return risk_assessment

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assessing current job risk: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to assess risk: {str(e)}")


# ==================== LAYER 2 ENDPOINTS (Predictive Intelligence) ====================


@router.get("/user/{user_id}/career-forecast")
async def get_career_forecast(user_id: str):
    """
    Predict 3 most likely career paths for user

    Returns:
    - career_forecast: Array of 3 paths with probabilities, timelines, salaries
    - current_trajectory_score: Career momentum (0-100)
    - pivot_opportunities: Alternative paths worth considering

    Frontend: Powers "Career Path Visualizer" module
    """

    try:
        profile = await get_orchestrator().profile_agent.get_profile(user_id)

        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")

        # Get market context
        role_keywords = profile.current_role or "professional"
        industry = profile.industry

        market_context = await get_orchestrator().market_intel_agent.get_market_intelligence(
            role_keywords=role_keywords, industry=industry
        )

        # Generate forecast
        forecast = await get_orchestrator().trajectory_agent.forecast_career_paths(
            user_profile=profile, market_context=market_context
        )

        return forecast

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating career forecast: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to forecast career paths: {str(e)}")


@router.get("/market-intelligence")
async def get_market_intelligence(role_keywords: str, industry: Optional[str] = None, location: Optional[str] = None):
    """
    Get live labor market intelligence

    Returns:
    - demand_trend: "rising" | "stable" | "declining"
    - demand_change_90d: Percentage change in job postings
    - avg_salary: Market average for role
    - top_hiring_companies: Who's hiring
    - emerging_skills: Skills gaining traction
    - automation_risk_trend: "increasing" | "stable" | "decreasing"
    - layoff_alerts: Recent workforce reductions

    Frontend: Powers "Market Pulse Widget" scrolling ticker
    """

    try:
        intel = await get_orchestrator().market_intel_agent.get_market_intelligence(
            role_keywords=role_keywords, industry=industry, location=location
        )

        return intel

    except Exception as e:
        logger.error(f"Error fetching market intelligence: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch market data: {str(e)}")


# ==================== LAYER 3 ENDPOINTS (Proactive Protection) ====================


@router.get("/user/{user_id}/early-warnings")
async def get_early_warnings(user_id: str):
    """
    Scan for threats before they're urgent

    Returns alerts for:
    - automation_threat: Current role at high AI displacement risk
    - skill_obsolescence: Skills declining in demand
    - market_decline: Industry contracting
    - burnout_risk: User showing exhaustion signals
    - confidence_decay: User losing self-efficacy

    Each alert includes:
    - severity: "critical" | "high" | "medium" | "low"
    - urgency_days: How soon to act
    - recommended_actions: What to do

    Frontend: Powers "Early Warning Banner" and proactive email alerts
    Subscription: Pro tier ($29/mo) and Elite tier ($99/mo)
    """

    try:
        profile = await get_orchestrator().profile_agent.get_profile(user_id)

        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")

        warnings = await get_orchestrator().early_warning_agent.scan_for_threats(profile)

        return warnings

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scanning for threats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to scan for threats: {str(e)}")


class OfferAnalysisRequest(BaseModel):
    """Request to analyze a job offer"""

    user_id: str
    offer_details: Dict[str, Any]  # {salary, equity, bonus, benefits, company, role, etc.}


@router.post("/user/{user_id}/analyze-offer")
async def analyze_offer(request: OfferAnalysisRequest = Body(...)):
    """
    Analyze a job offer and generate negotiation strategy

    Returns:
    - market_analysis: How offer compares to market
    - fairness_score: 0-100 (90+ = top 25% of market)
    - lifetime_value_delta: 5-year value vs market median
    - leverage_points: User's negotiation strengths
    - recommended_counter: Suggested counter-offer
    - negotiation_script: AI-generated talking points
    - fallback_positions: Backup asks if salary won't budge

    Frontend: Powers "Offer Optimizer" card
    Subscription: Elite tier ($99/mo) exclusive feature
    """

    try:
        profile = await get_orchestrator().profile_agent.get_profile(request.user_id)

        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")

        analysis = await get_orchestrator().negotiation_agent.analyze_offer(
            user_profile=profile, offer_details=request.offer_details
        )

        return analysis

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing offer: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to analyze offer: {str(e)}")


@router.get("/user/{user_id}/peer-insights")
async def get_peer_insights(user_id: str):
    """
    Get anonymized career insights from similar users

    Returns:
    - peer_cohort_size: How many similar profiles found
    - common_transitions: Popular career moves (from role → to role)
    - salary_comparison: User's position vs cohort median
    - skill_gaps_vs_peers: Skills user is missing that peers have
    - trending_skills_in_cohort: What's gaining traction

    Frontend: Powers "Peer Lens" comparison module
    Subscription: Enterprise tier feature
    """

    try:
        profile = await get_orchestrator().profile_agent.get_profile(user_id)

        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")

        insights = await get_orchestrator().peer_benchmarking_agent.find_peer_insights(profile)

        return insights

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching peer insights: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch peer data: {str(e)}")
