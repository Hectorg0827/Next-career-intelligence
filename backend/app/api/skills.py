"""Skills API - Manage User Skills and Skill Graph"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from loguru import logger

from app.db.database import get_db
from app.models.database import User
from app.services.skill_service import skill_service

router = APIRouter(prefix="/skills", tags=["Skills"])


class SkillResponse(BaseModel):
    id: str
    skill_name: str
    category: Optional[str]
    proficiency_level: Optional[int]
    confidence_score: float
    source_tags: List[str]
    evidence_snippets: List[str]
    confirmed_by_user: bool
    last_updated_at: str


class RoleTemplateResponse(BaseModel):
    occupation_code: str
    role_title: str
    skills: List[dict]


@router.get("/user/{firebase_uid}", response_model=List[SkillResponse])
async def get_user_skills(firebase_uid: str, db: Session = Depends(get_db)):
    """Get all skills for a user"""
    try:
        user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
        if not user:
            raise HTTPException(404, "User not found")

        # Query user skills with skill details
        sql = """
            SELECT 
                us.id,
                s.name as skill_name,
                s.category,
                us.proficiency_level,
                us.confidence_score,
                us.source_tags,
                us.evidence_snippets,
                us.confirmed_by_user,
                us.last_updated_at
            FROM public.user_skills us
            JOIN public.skills s ON us.skill_id = s.id
            WHERE us.user_id = :uid AND us.hidden = false
            ORDER BY us.confidence_score DESC, us.last_updated_at DESC
        """
        
        result = db.execute(sql, {"uid": str(user.id)}).fetchall()
        
        skills = []
        for row in result:
            skills.append(SkillResponse(
                id=str(row[0]),
                skill_name=row[1],
                category=row[2],
                proficiency_level=row[3],
                confidence_score=row[4],
                source_tags=row[5] or [],
                evidence_snippets=row[6] or [],
                confirmed_by_user=row[7],
                last_updated_at=row[8].isoformat()
            ))
        
        return skills
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch user skills: {e}")
        raise HTTPException(500, str(e))


@router.post("/user/{firebase_uid}/confirm/{skill_id}")
async def confirm_skill(firebase_uid: str, skill_id: str, db: Session = Depends(get_db)):
    """Confirm a skill (upgrade from inferred to verified)"""
    try:
        user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
        if not user:
            raise HTTPException(404, "User not found")

        sql = """
            UPDATE public.user_skills
            SET confirmed_by_user = true,
                confidence_score = LEAST(confidence_score + 0.2, 1.0),
                last_updated_at = NOW()
            WHERE user_id = :uid AND id = :skill_id
        """
        
        db.execute(sql, {"uid": str(user.id), "skill_id": skill_id})
        db.commit()
        
        return {"message": "Skill confirmed"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to confirm skill: {e}")
        db.rollback()
        raise HTTPException(500, str(e))


@router.delete("/user/{firebase_uid}/hide/{skill_id}")
async def hide_skill(firebase_uid: str, skill_id: str, db: Session = Depends(get_db)):
    """Hide a skill from the user's profile"""
    try:
        user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
        if not user:
            raise HTTPException(404, "User not found")

        sql = """
            UPDATE public.user_skills
            SET hidden = true,
                last_updated_at = NOW()
            WHERE user_id = :uid AND id = :skill_id
        """
        
        db.execute(sql, {"uid": str(user.id), "skill_id": skill_id})
        db.commit()
        
        return {"message": "Skill hidden"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to hide skill: {e}")
        db.rollback()
        raise HTTPException(500, str(e))


@router.get("/templates", response_model=List[RoleTemplateResponse])
async def get_role_templates(db: Session = Depends(get_db)):
    """Get all role skill templates"""
    try:
        sql = "SELECT occupation_code, role_title, skills FROM public.role_skill_templates ORDER BY role_title"
        result = db.execute(sql).fetchall()
        
        templates = []
        for row in result:
            templates.append(RoleTemplateResponse(
                occupation_code=row[0],
                role_title=row[1],
                skills=row[2]
            ))
        
        return templates
        
    except Exception as e:
        logger.error(f"Failed to fetch role templates: {e}")
        raise HTTPException(500, str(e))


@router.post("/apply-role-priors")
async def apply_role_priors(firebase_uid: str, occupation_code: str, db: Session = Depends(get_db)):
    """Apply role-based skill priors to a user"""
    try:
        user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
        if not user:
            raise HTTPException(404, "User not found")

        skill_service.apply_role_priors(db, str(user.id), occupation_code)
        
        return {"message": "Role priors applied"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to apply role priors: {e}")
        db.rollback()
        raise HTTPException(500, str(e))
