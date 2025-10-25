"""
Career analysis endpoint - Core AI analysis functionality
POWERED BY NEXTAI - Advanced Career Intelligence
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from loguru import logger
import uuid
from datetime import datetime

from app.models.schemas import AnalysisRequest, AnalysisResponse
from app.models.database import User
from app.services.gemini_analyzer import GeminiAnalyzer
from app.services.onet_service import ONetService
from app.services.coursera_service import CourseraService
from app.db.supabase import SupabaseDB
from app.db.database import get_db

router = APIRouter()


@router.post("/analyze", response_model=AnalysisResponse, status_code=status.HTTP_201_CREATED)
async def analyze_career(
    request: AnalysisRequest,
    firebase_uid: str = None,  # Optional for demo/testing
    db: Session = Depends(get_db)
):
    """
    Analyze career AI displacement risk and transition pathways
    POWERED BY NEXTAI - Advanced Career Intelligence System
    
    SUBSCRIPTION GATING:
    - Free users: 1 analysis total
    - Pro users: Unlimited analyses
    """
    
    analysis_id = str(uuid.uuid4())  # Generate ID at start
    
    try:
        # Fetch user and check subscription (skip if no firebase_uid for demo)
        user = None
        if firebase_uid:
            user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
        
        # Check subscription limits (only if user is logged in)
        subscription_status = 'free'
        free_reports_used = 0
        
        if user:
            subscription_status = user.subscription_status or 'free'
            free_reports_used = user.free_reports_used or 0
            
            if subscription_status == 'free' and free_reports_used >= 1:
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail="Free analysis limit reached. Upgrade to Pro for unlimited analyses."
                )
        
        user_email = user.email if user else "demo"
        logger.info(f"🤖 Starting NextAI analysis for job: {request.job_title} (ID: {analysis_id})")
        logger.info(f"User: {user_email} | Tier: {subscription_status} | Reports used: {free_reports_used}")
        
        # Initialize NextAI analyzer
        nextai = GeminiAnalyzer()
        
        # 🚀 PERFORMANCE OPTIMIZATION: Run all AI calls in parallel
        # This reduces latency from ~130s to ~40-50s (60% faster!)
        # Instead of sequential: 20s + 30s + 40s = 90s
        # Parallel execution: max(20s, 30s, 40s) = 40s
        import asyncio
        
        risk_analysis, skill_insights, benchmarks = await asyncio.gather(
            nextai.analyze_displacement_risk(
                job_title=request.job_title,
                skills=request.skills,
                years_experience=request.years_experience
            ),
            nextai.generate_skill_insights(
                job_title=request.job_title,
                skills=request.skills,
                years_experience=request.years_experience
            ),
            nextai.generate_industry_benchmarks(
                job_title=request.job_title,
                skills=request.skills,
                location=request.location,
                years_experience=request.years_experience
            )
        )
        
        # Compile the full analysis result
        analysis_result = {
            "analysis_id": analysis_id,
            "job_title": request.job_title,
            "ai_displacement_risk": risk_analysis.get("ai_displacement_risk"),
            "compatibility_score": risk_analysis.get("compatibility_score"),
            "human_advantage_factors": risk_analysis.get("human_advantage_factors", []),
            "automation_vulnerable_tasks": risk_analysis.get("automation_vulnerable_tasks", []),
            "automation_resistant_tasks": risk_analysis.get("automation_resistant_tasks", []),
            "transition_pathways": skill_insights.get("transition_pathways", []),
            "skill_gaps": skill_insights.get("skill_gaps", []),
            "recommended_training": skill_insights.get("recommended_training", []),
            "created_at": datetime.utcnow(),
            "metadata": {
                "location": request.location,
                "years_experience": request.years_experience,
                "ai_engine": "NextAI",
                "benchmarks": benchmarks
            }
        }
        
        # Validate JSON serialization before returning
        try:
            import json
            json.dumps(analysis_result, default=str)  # Test if it can be serialized
        except (TypeError, ValueError) as json_error:
            logger.error(f"JSON serialization error: {json_error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to serialize analysis results. Invalid data format."
            )
        
        logger.info(f"✅ NextAI analysis completed successfully: {analysis_id}")
        
        # Update user's free report counter if on free tier (only if user exists)
        if user and subscription_status == 'free':
            user.free_reports_used = free_reports_used + 1
            user.last_free_analysis_at = datetime.utcnow()
            db.commit()
            logger.info(f"Updated free report counter: {user.free_reports_used}/1")
        
        # Save to Supabase if user exists
        if user:
            try:
                await SupabaseDB.save_analysis(str(user.id), analysis_result)
                logger.info(f"💾 Analysis saved to Supabase: {analysis_id}")
            except Exception as e:
                logger.warning(f"Failed to save analysis to Supabase: {e}")
        
        return AnalysisResponse(**analysis_result)
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e).replace("{", "{{").replace("}", "}}")
        logger.error(f"Analysis failed for job {request.job_title}: {error_msg}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )
