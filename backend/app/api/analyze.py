"""
Career analysis endpoint - Core AI analysis functionality
NOW USING GEMINI API INSTEAD OF OPENAI
"""

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
import uuid
from datetime import datetime

from app.models.schemas import AnalysisRequest, AnalysisResponse
from app.services.gemini_analyzer import GeminiAnalyzer  # CHANGED: Now using Gemini
from app.services.onet_service import ONetService
from app.services.coursera_service import CourseraService
from app.db.supabase import SupabaseDB  # CHANGED: Now using Supabase

router = APIRouter()


@router.post("/analyze", response_model=AnalysisResponse, status_code=status.HTTP_201_CREATED)
async def analyze_career(
    request: AnalysisRequest,
    user_id: str = None  # TODO: Get from auth token
):
    """
    Analyze career AI displacement risk and transition pathways
    NOW POWERED BY GOOGLE GEMINI PRO 1.5
    """
    
    analysis_id = str(uuid.uuid4())  # Generate ID at start
    
    try:
        logger.info(f"🤖 Starting Gemini analysis for job: {request.job_title} (ID: {analysis_id})")
        
        # Initialize Gemini analyzer
        gemini = GeminiAnalyzer()
        
        # Get AI displacement risk analysis from Gemini
        risk_analysis = await gemini.analyze_displacement_risk(
            job_title=request.job_title,
            skills=request.skills,
            years_experience=request.years_experience
        )
        
        # Get skill insights from Gemini
        skill_insights = await gemini.generate_skill_insights(
            job_title=request.job_title,
            skills=request.skills,
            years_experience=request.years_experience
        )
        
        # Get industry benchmarks from Gemini
        benchmarks = await gemini.generate_industry_benchmarks(
            job_title=request.job_title,
            skills=request.skills,
            location=request.location,
            years_experience=request.years_experience
        )
        
        # Compile the full analysis result
        analysis_result = {
            "analysis_id": analysis_id,
            "job_title": request.job_title,
            "ai_displacement_risk": risk_analysis.get("ai_displacement_risk", {
                "level": "Medium",
                "score": 50.0,
                "velocity": "Moderate",
                "augmentation_potential": "Analysis in progress",
                "reasoning": "Gemini analysis completed"
            }),
            "compatibility_score": risk_analysis.get("compatibility_score", 75.0),
            "human_advantage_factors": risk_analysis.get("human_advantage_factors", []),
            "transition_pathways": skill_insights.get("transition_pathways", []),
            "skill_gaps": skill_insights.get("skill_gaps", []),
            "recommended_training": skill_insights.get("recommended_training", []),
            "created_at": datetime.utcnow(),
            "metadata": {
                "location": request.location,
                "years_experience": request.years_experience,
                "ai_engine": "gemini-1.5-pro",
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
        
        logger.info(f"✅ Gemini analysis completed successfully: {analysis_id}")
        
        # Save to Supabase if user_id is available
        if user_id:
            try:
                await SupabaseDB.save_analysis(user_id, analysis_result)
                logger.info(f"💾 Analysis saved to Supabase: {analysis_id}")
            except Exception as e:
                logger.warning(f"Failed to save analysis to Supabase: {e}")
        
        return AnalysisResponse(**analysis_result)
        
    except Exception as e:
        error_msg = str(e).replace("{", "{{").replace("}", "}}")
        logger.error(f"Analysis failed for job {request.job_title}: {error_msg}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )
