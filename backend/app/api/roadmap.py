"""
Career Roadmap API Endpoints
Generates multi-year career roadmaps with visual Sankey data
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from loguru import logger
from typing import Optional

from app.models.schemas import AnalysisRequest
from app.services.gemini_analyzer import gemini_analyzer
from app.db.database import get_db

router = APIRouter(prefix="/api", tags=["roadmap"])


@router.post("/roadmap")
async def generate_career_roadmap(
    request: AnalysisRequest,
    db: Session = Depends(get_db)
):
    """
    Generate multi-year career roadmap with visual Sankey data
    Now powered by Google Gemini Pro
    """
    try:
        logger.info(f"Generating Gemini roadmap for {request.job_title}")

        # Generate roadmap using Gemini
        roadmap = await gemini_analyzer.generate_career_roadmap(
            job_title=request.job_title,
            skills=request.skills,
            location=request.location,
            years_experience=request.years_experience,
            timeline=getattr(request, 'timeline', '5 years')
        )

        logger.info(f"Gemini roadmap generated successfully for {request.job_title}")
        return {"career_roadmap": roadmap}

    except Exception as e:
        logger.error(f"Roadmap generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))