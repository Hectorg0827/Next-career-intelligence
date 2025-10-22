"""
Career Roadmap API Endpoints
Generates multi-year career roadmaps with visual Sankey data
POWERED BY NEXTAI - Advanced Career Intelligence
"""

from fastapi import APIRouter, HTTPException
from loguru import logger
from typing import Optional

from app.models.schemas import AnalysisRequest
from app.services.gemini_analyzer import GeminiAnalyzer

router = APIRouter()


@router.post("/roadmap")
async def generate_career_roadmap(
    request: AnalysisRequest,
    user_id: str = None  # TODO: Get from auth token
):
    """
    Generate multi-year career roadmap with visual Sankey data
    Powered by NextAI - Advanced Career Intelligence
    """
    try:
        logger.info(f"🗺️ Generating NextAI roadmap for {request.job_title}")

        # Initialize NextAI analyzer
        nextai = GeminiAnalyzer()

        # Generate roadmap using NextAI
        roadmap = await nextai.generate_career_roadmap(
            job_title=request.job_title,
            skills=request.skills,
            location=request.location,
            years_experience=request.years_experience,
            timeline=getattr(request, 'timeline', '5 years')
        )

        logger.info(f"✅ NextAI roadmap generated successfully for {request.job_title}")
        return {"career_roadmap": roadmap}

    except Exception as e:
        logger.error(f"❌ Roadmap generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))