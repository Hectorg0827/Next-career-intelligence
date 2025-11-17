"""
AI Displacement Risk Analysis Endpoints

Provides RESTful API access to the DisplacementRiskEngine v1.0.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import List, Optional
from loguru import logger
import asyncpg
from datetime import datetime

from app.services.foundation.risk.displacement_engine import DisplacementRiskEngine
from app.services.foundation.risk.models import (
    RiskAnalysisRequest,
    RiskAnalysisResponse,
    UserProfile,
    JobData
)


router = APIRouter(prefix="/risk", tags=["AI Displacement Risk"])


async def get_db_pool(request: Request) -> asyncpg.Pool:
    """
    Get database connection pool from app state.
    
    Usage in endpoint:
        pool = await get_db_pool(request)
    """
    return request.app.state.db_pool


@router.post(
    "/analyze",
    response_model=RiskAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze AI Displacement Risk",
    description="""
    Calculate comprehensive AI displacement risk analysis for a user.
    
    Returns:
    - Risk score (0-100) with level (Low/Medium/High/Critical)
    - Time horizon (0-2 years / 2-5 years / 5+ years)
    - Confidence score based on data coverage
    - Percentile comparison vs peers in same role
    - Trajectory (improving/stable/worsening)
    - Human-readable justification
    - Primary vulnerabilities (top risk factors)
    - Protection opportunities (actionable recommendations)
    - Debug components (all intermediate scores)
    
    Performance: Typical response time <500ms
    """
)
async def analyze_displacement_risk(
    request: RiskAnalysisRequest,
    req: Request
) -> RiskAnalysisResponse:
    """
    Run displacement risk analysis for a user.
    
    Args:
        request: Complete user profile + target job data
        req: FastAPI request object (for DB pool access)
    
    Returns:
        Complete risk analysis with scores, justifications, and recommendations
    
    Raises:
        HTTPException 400: Invalid request data
        HTTPException 500: Internal server error
    """
    try:
        # Get database pool
        pool = await get_db_pool(req)
        
        # Initialize engine
        engine = DisplacementRiskEngine(pool)
        
        # Run analysis
        logger.info(
            f"Running displacement risk analysis: "
            f"user_id={request.user_profile.user_id}, "
            f"occupation={request.job_data.occupation_code}"
        )
        
        result = await engine.analyze(
            request.user_profile,
            request.job_data
        )
        
        logger.info(
            f"Analysis complete: "
            f"risk={result.ai_displacement_risk.score}/100 "
            f"({result.ai_displacement_risk.level}), "
            f"time_horizon={result.ai_displacement_risk.time_horizon}"
        )
        
        return result
    
    except ValueError as e:
        # Invalid input data
        logger.warning(f"Invalid request data: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid request data: {str(e)}"
        )
    
    except asyncpg.PostgresError as e:
        # Database error
        logger.error(f"Database error during analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred. Please try again later."
        )
    
    except Exception as e:
        # Unexpected error
        logger.error(f"Unexpected error during analysis: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please contact support."
        )


@router.get(
    "/history/{user_id}",
    response_model=List[RiskAnalysisResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Risk Analysis History",
    description="""
    Retrieve historical risk analyses for a user.
    
    Returns list of past analyses ordered by most recent first.
    Useful for:
    - Tracking risk trajectory over time
    - Comparing different job roles
    - Monitoring impact of learning actions
    
    Query parameters:
    - limit: Maximum number of results (default: 20, max: 100)
    """
)
async def get_risk_history(
    user_id: str,
    req: Request,
    limit: int = 20
) -> List[RiskAnalysisResponse]:
    """
    Get user's historical risk analyses.
    
    Args:
        user_id: User UUID
        req: FastAPI request object (for DB pool access)
        limit: Maximum number of results to return (default 20, max 100)
    
    Returns:
        List of past risk analyses, most recent first
    
    Raises:
        HTTPException 400: Invalid parameters
        HTTPException 404: User not found
        HTTPException 500: Internal server error
    """
    try:
        # Validate limit
        if limit < 1 or limit > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Limit must be between 1 and 100"
            )
        
        # Get database pool
        pool = await get_db_pool(req)
        
        # Query historical snapshots
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT 
                    user_id,
                    occupation_code,
                    industry,
                    displacement_risk,
                    structural_risk,
                    personal_shield,
                    tas_score,
                    ivs_score,
                    psc_score,
                    adaptability_score,
                    seniority_score,
                    credential_score,
                    time_horizon,
                    time_horizon_index,
                    confidence_score,
                    percentile_vs_role,
                    calculated_at
                FROM risk_calculation_snapshots
                WHERE user_id = $1
                ORDER BY calculated_at DESC
                LIMIT $2
                """,
                user_id,
                limit
            )
        
        if not rows:
            logger.info(f"No risk history found for user: {user_id}")
            return []
        
        logger.info(f"Retrieved {len(rows)} historical analyses for user: {user_id}")
        
        # Convert to response models
        # Note: We reconstruct the response but without justifications/vulnerabilities/opportunities
        # (those aren't stored in snapshots - would need to regenerate)
        results = []
        for row in rows:
            # Create minimal response (historical data doesn't have full LLM output)
            from app.services.foundation.risk.models import (
                DisplacementRiskScore,
                DebugComponents
            )
            
            # Map risk level from score
            score = float(row['displacement_risk'])
            if score >= 75:
                level = "Critical"
            elif score >= 60:
                level = "High"
            elif score >= 40:
                level = "Medium"
            else:
                level = "Low"
            
            # Map trajectory (simplified - would need T-90 comparison for real trajectory)
            trajectory = "stable"
            
            risk_score = DisplacementRiskScore(
                level=level,
                score=round(score, 1),
                time_horizon=row['time_horizon'] or "Unknown",
                confidence=round(float(row['confidence_score'] or 0), 1),
                percentile_vs_role=round(float(row['percentile_vs_role']), 1) if row['percentile_vs_role'] else None,
                trajectory=trajectory,
                justification="Historical data - run new analysis for updated justification",
                primary_vulnerabilities=[],
                protection_opportunities=[]
            )
            
            debug = DebugComponents(
                StructuralRisk=round(float(row['structural_risk'] or 0), 1),
                PersonalShield=round(float(row['personal_shield'] or 0), 1),
                TAS=round(float(row['tas_score'] or 0), 1),
                IVS=round(float(row['ivs_score'] or 0), 1),
                PSC=round(float(row['psc_score'] or 0), 1),
                AS=round(float(row['adaptability_score'] or 0), 1),
                SeniorityProtection=round(float(row['seniority_score'] or 0), 1),
                CredentialStrength=round(float(row['credential_score'] or 0), 1),
                TimeHorizonIndex=round(float(row['time_horizon_index'] or 0), 2),
                Confidence=round(float(row['confidence_score'] or 0), 1)
            )
            
            results.append(
                RiskAnalysisResponse(
                    ai_displacement_risk=risk_score,
                    debug_components=debug,
                    calculated_at=row['calculated_at']
                )
            )
        
        return results
    
    except HTTPException:
        raise
    
    except asyncpg.PostgresError as e:
        logger.error(f"Database error retrieving history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred. Please try again later."
        )
    
    except Exception as e:
        logger.error(f"Unexpected error retrieving history: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please contact support."
        )


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Risk Engine Health Check",
    description="Check if the risk analysis engine is operational"
)
async def health_check(req: Request) -> dict:
    """
    Health check for risk analysis engine.
    
    Returns:
        Status and engine version info
    """
    try:
        pool = await get_db_pool(req)
        
        # Test database connection
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        
        return {
            "status": "healthy",
            "engine_version": "1.0",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Risk engine is unavailable"
        )
