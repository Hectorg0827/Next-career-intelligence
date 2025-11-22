"""
Profile API endpoints
Handles skill ingestion, education, and skill gap analysis
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from loguru import logger
from typing import List

from app.models.skill_schemas import (
    ManualSkillsRequest,
    ResumeUploadRequest,
    ConversationSkillRequest,
    EducationCreate,
    UserSkillResponse,
    EducationResponse,
    SkillGapRequest,
    SkillGapAnalysis,
    EvidenceSource,
    ProficiencyLevel,
    SkillCreate
)
from app.models.database import User
from app.db.database import get_db
from app.services.skill_service import skill_service
from app.services.skill_gap_analyzer import skill_gap_analyzer
from app.core.auth import get_current_user

router = APIRouter(prefix="/profile", tags=["profile"])


@router.post("/skills/manual", response_model=UserSkillResponse)
async def add_skills_manually(
    request: ManualSkillsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add skills manually from user input
    """
    try:
        logger.info(f"Adding {len(request.skills)} manual skills for user {current_user.id}")
        
        # Add skills using SkillService
        skill_service.add_multiple_skills(
            db=db,
            user_id=str(current_user.id),
            skills=request.skills,
            evidence_source=EvidenceSource.SELF_REPORTED
        )
        
        db.commit()
        
        # Return updated skill profile
        return skill_service.get_user_skills(db, str(current_user.id))
        
    except Exception as e:
        logger.error(f"Failed to add manual skills: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add skills: {str(e)}"
        )


@router.post("/skills/from-resume", response_model=UserSkillResponse)
async def extract_skills_from_resume(
    request: ResumeUploadRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Extract skills from resume text
    """
    try:
        logger.info(f"Extracting skills from resume for user {current_user.id}")
        
        # Parse resume for skills
        extracted_skills = skill_service.parse_resume_for_skills(request.resume_text)
        
        if not extracted_skills:
            logger.warning("No skills extracted from resume")
            return skill_service.get_user_skills(db, str(current_user.id))
        
        # Add extracted skills
        skill_service.add_multiple_skills(
            db=db,
            user_id=str(current_user.id),
            skills=extracted_skills,
            evidence_source=EvidenceSource.RESUME
        )
        
        db.commit()
        
        logger.info(f"Extracted {len(extracted_skills)} skills from resume")
        
        # Return updated skill profile
        return skill_service.get_user_skills(db, str(current_user.id))
        
    except Exception as e:
        logger.error(f"Failed to extract skills from resume: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to extract skills: {str(e)}"
        )


@router.post("/skills/from-conversation", response_model=UserSkillResponse)
async def extract_skills_from_conversation(
    request: ConversationSkillRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Extract skills from conversational text using LLM
    """
    try:
        logger.info(f"Extracting skills from conversation for user {current_user.id}")
        
        # Use skill service for LLM extraction
        skills_data = await skill_service.extract_skills_from_text(
            request.conversation_transcript
        )
        
        if not skills_data:
            logger.warning("No skills extracted from conversation")
            return skill_service.get_user_skills(db, str(current_user.id))
        
        # Convert to SkillCreate format and add
        skill_creates = []
        for skill_data in skills_data:
            # Map confidence to proficiency
            confidence = skill_data.get("confidence", 0.5)
            if confidence >= 0.8:
                proficiency = ProficiencyLevel.ADVANCED
            elif confidence >= 0.6:
                proficiency = ProficiencyLevel.INTERMEDIATE
            else:
                proficiency = ProficiencyLevel.BEGINNER
            
            skill_creates.append(SkillCreate(
                name=skill_data["name"],
                proficiency_level=proficiency
            ))
        
        skill_service.add_multiple_skills(
            db=db,
            user_id=str(current_user.id),
            skills=skill_creates,
            evidence_source=EvidenceSource.CONVERSATION
        )
        
        db.commit()
        
        logger.info(f"Extracted {len(skills_data)} skills from conversation")
        
        # Return updated skill profile
        return skill_service.get_user_skills(db, str(current_user.id))
        
    except Exception as e:
        logger.error(f"Failed to extract skills from conversation: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to extract skills: {str(e)}"
        )


@router.get("/skills", response_model=UserSkillResponse)
async def get_user_skills(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all skills for the authenticated user
    """
    try:
        return skill_service.get_user_skills(db, str(current_user.id))
    except Exception as e:
        logger.error(f"Failed to get user skills: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve skills: {str(e)}"
        )


@router.post("/education", response_model=EducationResponse)
async def add_education(
    request: EducationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add education record for user
    """
    try:
        education = skill_service.add_education(
            db=db,
            user_id=str(current_user.id),
            education_data=request
        )
        
        db.commit()
        
        return EducationResponse(
            id=str(education.id),
            degree=education.degree,
            institution=education.institution,
            field_of_study=education.field_of_study,
            start_year=education.start_year,
            end_year=education.end_year,
            created_at=education.created_at
        )
        
    except Exception as e:
        logger.error(f"Failed to add education: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add education: {str(e)}"
        )


@router.get("/education", response_model=List[EducationResponse])
async def get_user_education(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all education records for the authenticated user
    """
    try:
        return skill_service.get_user_education(db, str(current_user.id))
    except Exception as e:
        logger.error(f"Failed to get user education: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve education: {str(e)}"
        )


@router.post("/skill-gap", response_model=SkillGapAnalysis)
async def analyze_skill_gap(
    request: SkillGapRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze skill gap between user's profile and target role
    """
    try:
        logger.info(f"Analyzing skill gap for user {current_user.id}, target: {request.target_role_title}")
        
        analysis = await skill_gap_analyzer.analyze_skill_gap(
            db=db,
            user_id=str(current_user.id),
            request=request
        )
        
        return analysis
        
    except Exception as e:
        logger.error(f"Failed to analyze skill gap: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze skill gap: {str(e)}"
        )
