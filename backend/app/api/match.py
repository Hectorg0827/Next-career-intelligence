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

# Initialize orchestrator
orchestrator = CareerOrchestrator()


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
        
        result = await orchestrator.analyze_job_match(
            user_id=request.user_id,
            job=request.job,
            recent_conversation=request.recent_conversation
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error in match analysis: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze job match: {str(e)}"
        )


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
        
        ranked = await orchestrator.rank_jobs(
            user_id=request.user_id,
            jobs=request.jobs
        )
        
        return {
            "user_id": request.user_id,
            "total_jobs": len(ranked),
            "ranked_jobs": ranked
        }
        
    except Exception as e:
        logger.error(f"Error ranking jobs: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to rank jobs: {str(e)}"
        )


@router.get("/profile/{user_id}")
async def get_user_profile(user_id: str):
    """
    Retrieve the complete User Profile (source of truth)
    
    Returns the persistent, evolving record of the user's career identity.
    """
    
    try:
        profile = await orchestrator.profile_agent.get_profile(user_id)
        
        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        return profile
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving profile: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve profile: {str(e)}"
        )


@router.post("/profile/{user_id}/create")
async def create_user_profile(user_id: str, email: Optional[str] = None):
    """
    Create a new User Profile
    
    Initializes an empty profile that will be populated over time.
    """
    
    try:
        profile = await orchestrator.profile_agent.create_profile(user_id, email)
        
        return {
            "message": "Profile created successfully",
            "profile": profile
        }
        
    except Exception as e:
        logger.error(f"Error creating profile: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create profile: {str(e)}"
        )


@router.get("/user/{user_id}/current-job-risk")
async def assess_current_job_risk(user_id: str):
    """
    Assess AI displacement risk for user's CURRENT job
    
    Helps identify if user needs to transition urgently.
    """
    
    try:
        profile = await orchestrator.profile_agent.get_profile(user_id)
        
        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        risk_assessment = await orchestrator.risk_agent.assess_current_job_risk(profile)
        
        return risk_assessment
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assessing current job risk: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to assess risk: {str(e)}"
        )
