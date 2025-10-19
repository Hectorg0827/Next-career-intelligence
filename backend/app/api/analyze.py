"""
Career analysis endpoint - Core AI analysis functionality
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from loguru import logger
import uuid
from datetime import datetime

from app.models.schemas import AnalysisRequest, AnalysisResponse
from app.models.database import Analysis, User
from app.db.database import get_db
from app.services.ai_analyzer import AIAnalyzerService
from app.services.onet_service import ONetService
from app.services.coursera_service import CourseraService
from app.services.skill_inference import SkillInferenceEngine

router = APIRouter()


@router.post("/analyze", response_model=AnalysisResponse, status_code=status.HTTP_201_CREATED)
async def analyze_career(
    request: AnalysisRequest,
    db: Session = Depends(get_db),
    user_id: str = None  # TODO: Get from auth token
):
    """
    Analyze career AI displacement risk and transition pathways
    
    This endpoint:
    1. Validates input data
    2. Calls O*NET API for occupation data
    3. Uses OpenAI GPT for risk analysis
    4. Fetches training recommendations from Coursera
    5. Saves analysis to database
    6. Returns comprehensive analysis results
    """
    
    try:
        logger.info(f"Starting analysis for job: {request.job_title}")
        
        # Initialize services
        ai_analyzer = AIAnalyzerService()
        onet_service = ONetService()
        coursera_service = CourseraService()
        
        # Step 1: Get occupation data from O*NET
        logger.info("Fetching O*NET occupation data...")
        occupation_data = await onet_service.get_occupation_data(request.job_title)
        
        # Step 2: Perform AI risk analysis
        logger.info("Analyzing AI displacement risk...")
        risk_analysis = await ai_analyzer.analyze_displacement_risk(
            job_title=request.job_title,
            skills=request.skills,
            location=request.location,
            occupation_data=occupation_data
        )
        
        # Step 3: Calculate compatibility and transition pathways
        logger.info("Calculating career compatibility...")
        compatibility_analysis = await ai_analyzer.analyze_compatibility(
            current_skills=request.skills,
            occupation_data=occupation_data
        )
        
        # Step 3.5: Infer adjacent skills and hidden talents (NEW FEATURE!)
        logger.info("Analyzing skill inference and hidden talents...")
        skill_engine = SkillInferenceEngine()
        skill_insights = await skill_engine.infer_adjacent_skills(
            current_skills=request.skills,
            job_title=request.job_title,
            years_experience=request.years_experience
        )
        
        # Step 4: Get training recommendations
        logger.info("Fetching training recommendations...")
        skill_gaps = compatibility_analysis.get("skill_gaps", [])
        training_recommendations = await coursera_service.get_recommendations(skill_gaps)
        
        # Step 5: Generate industry benchmarks (NEW FEATURE 6!)
        logger.info("Generating industry benchmarks...")
        industry_benchmarks = await ai_analyzer.generate_industry_benchmarks(
            job_title=request.job_title,
            skills=request.skills,
            years_experience=request.years_experience,
            automation_risk_score=risk_analysis["score"]
        )
        
        # Step 6: Compile full analysis
        analysis_id = str(uuid.uuid4())
        
        analysis_result = {
            "analysis_id": analysis_id,
            "job_title": request.job_title,
            "ai_displacement_risk": risk_analysis,
            "compatibility_score": compatibility_analysis.get("compatibility_score", 0),
            "human_advantage_factors": compatibility_analysis.get("human_advantage_factors", []),
            "transition_pathways": compatibility_analysis.get("transition_pathways", []),
            "skill_gaps": skill_gaps,
            "recommended_training": training_recommendations,
            "skill_insights": skill_insights,  # Feature 1: Enhanced skill intelligence!
            "industry_benchmarks": industry_benchmarks,  # Feature 6: Market comparisons!
            "created_at": datetime.utcnow(),
            "metadata": {
                "onet_code": occupation_data.get("code"),
                "location": request.location,
                "years_experience": request.years_experience
            }
        }
        
        # Step 7: Save to database (if user is authenticated)
        if user_id:
            try:
                analysis_record = Analysis(
                    id=analysis_id,
                    user_id=user_id,
                    job_title=request.job_title,
                    skills=request.skills,
                    location=request.location,
                    years_experience=request.years_experience,
                    risk_score=risk_analysis["score"],
                    risk_level=risk_analysis["level"],
                    compatibility_score=compatibility_analysis.get("compatibility_score", 0),
                    analysis_result=analysis_result
                )
                db.add(analysis_record)
                db.commit()
                logger.info(f"Analysis saved to database: {analysis_id}")
            except Exception as e:
                logger.error(f"Failed to save analysis to database: {e}")
                db.rollback()
        
        logger.info(f"Analysis completed successfully: {analysis_id}")
        
        return AnalysisResponse(**analysis_result)
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@router.post("/roadmap", status_code=status.HTTP_200_OK)
async def generate_roadmap(
    request: AnalysisRequest,
    career_goals: str = "Career advancement and AI resilience"
):
    """
    Generate multi-year career roadmap (3, 5, and 10 years)
    
    FEATURE 2: Multi-Year Career Pathways
    
    This endpoint provides:
    - 3-year pathway (near-term goals)
    - 5-year pathway (mid-term strategy)
    - 10-year pathway (long-term vision)
    - Alternative paths at each stage
    - Immediate next steps (month-by-month)
    - Risk mitigation strategies
    - Visual pathway nodes and edges for Sankey diagrams
    
    Each pathway includes:
    - Target role and milestone
    - Skills to develop
    - Certifications recommended
    - Key projects
    - Salary expectations
    - AI resilience score
    - WHY this path (explainable AI)
    """
    
    try:
        logger.info(f"Generating career roadmap for: {request.job_title}")
        
        # Initialize AI analyzer
        ai_analyzer = AIAnalyzerService()
        
        # Generate comprehensive roadmap
        roadmap = await ai_analyzer.generate_career_roadmap(
            job_title=request.job_title,
            skills=request.skills,
            years_experience=request.years_experience,
            career_goals=career_goals
        )
        
        logger.info("Career roadmap generated successfully")
        
        return {
            "job_title": request.job_title,
            "current_experience": request.years_experience,
            "career_goals": career_goals,
            **roadmap
        }
        
    except Exception as e:
        logger.error(f"Roadmap generation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Roadmap generation failed: {str(e)}"
        )
