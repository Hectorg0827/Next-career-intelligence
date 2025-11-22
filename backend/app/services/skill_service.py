"""
Skill Service
Manages the Skill Graph: extraction, persistence, and role-based priors.
"""

from typing import List, Dict, Optional, Any
from datetime import datetime
from loguru import logger
import json
import os
import uuid
import re
from sqlalchemy.orm import Session
from sqlalchemy import and_
from sqlalchemy.dialects.postgresql import insert

from app.models.database import User, Skill, UserSkill, Education
from app.models.skill_schemas import (
    ProficiencyLevel,
    EvidenceSource,
    SkillCreate,
    SkillResponse,
    UserSkillResponse,
    EducationCreate,
    EducationResponse,
)

try:
    import google.generativeai as genai
except ImportError:
    logger.warning("google.generativeai not installed")
    genai = None

from app.services.prompts import SKILL_EXTRACTOR_PROMPT


class SkillService:
    def __init__(self):
        if genai:
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
            self.model = genai.GenerativeModel(model_name, generation_config={"response_mime_type": "application/json"})
        else:
            self.model = None

    # --- Helpers ---

    @staticmethod
    def normalize_skill_name(name: str) -> str:
        """Normalize skill name for consistent storage"""
        return re.sub(r'\s+', ' ', name.strip()).lower()

    @staticmethod
    def map_proficiency_to_int(level: ProficiencyLevel) -> int:
        mapping = {
            ProficiencyLevel.BEGINNER: 2,
            ProficiencyLevel.INTERMEDIATE: 5,
            ProficiencyLevel.ADVANCED: 8,
            ProficiencyLevel.EXPERT: 10
        }
        return mapping.get(level, 5)

    @staticmethod
    def map_int_to_proficiency(level: int) -> ProficiencyLevel:
        if level >= 9: return ProficiencyLevel.EXPERT
        if level >= 7: return ProficiencyLevel.ADVANCED
        if level >= 4: return ProficiencyLevel.INTERMEDIATE
        return ProficiencyLevel.BEGINNER

    # --- Core Logic ---

    def get_or_create_skill(self, db: Session, name: str, category: Optional[str] = None) -> Skill:
        """Get existing skill or create new one"""
        normalized_name = self.normalize_skill_name(name)
        
        # Try to find by normalized name
        skill = db.query(Skill).filter(Skill.normalized_name == normalized_name).first()
        if skill:
            return skill
            
        # Try to find by exact name (fallback)
        skill = db.query(Skill).filter(Skill.name == name.strip()).first()
        if skill:
            # Update normalized name if missing
            if not skill.normalized_name:
                skill.normalized_name = normalized_name
                db.commit()
            return skill
        
        # Create new skill
        skill = Skill(
            id=uuid.uuid4(),
            name=name.strip(),
            normalized_name=normalized_name,
            category=category or "general",
            created_at=datetime.utcnow()
        )
        db.add(skill)
        db.flush()
        return skill

    def add_user_skill(
        self,
        db: Session,
        user_id: str,
        skill_name: str,
        proficiency_level: ProficiencyLevel = ProficiencyLevel.INTERMEDIATE,
        evidence_source: EvidenceSource = EvidenceSource.SELF_REPORTED,
        last_used_year: Optional[float] = None,
        category: Optional[str] = None
    ) -> UserSkill:
        """Add or update a user's skill"""
        
        skill = self.get_or_create_skill(db, skill_name, category)
        user_uuid = uuid.UUID(user_id)
        
        # Check if user already has this skill
        user_skill = db.query(UserSkill).filter(
            and_(
                UserSkill.user_id == user_uuid,
                UserSkill.skill_id == skill.id
            )
        ).first()
        
        prof_int = self.map_proficiency_to_int(proficiency_level)
        
        if user_skill:
            # Update existing
            # Only upgrade proficiency, never downgrade automatically (unless explicit?)
            # For now, we overwrite if source is explicit
            user_skill.proficiency_level = max(user_skill.proficiency_level or 0, prof_int)
            user_skill.evidence_source = evidence_source.value
            user_skill.last_used_year = last_used_year
            user_skill.updated_at = datetime.utcnow()
            
            # Update source tags
            current_tags = user_skill.source_tags or []
            if evidence_source.value not in current_tags:
                current_tags.append(evidence_source.value)
                user_skill.source_tags = current_tags
                
        else:
            # Create new
            user_skill = UserSkill(
                id=uuid.uuid4(),
                user_id=user_uuid,
                skill_id=skill.id,
                proficiency_level=prof_int,
                evidence_source=evidence_source.value,
                source_tags=[evidence_source.value],
                last_used_year=last_used_year,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(user_skill)
        
        db.flush()
        return user_skill

    def add_multiple_skills(
        self,
        db: Session,
        user_id: str,
        skills: List[SkillCreate],
        evidence_source: EvidenceSource = EvidenceSource.SELF_REPORTED
    ) -> List[UserSkill]:
        """Add multiple skills for a user"""
        user_skills = []
        for skill_data in skills:
            user_skill = self.add_user_skill(
                db=db,
                user_id=user_id,
                skill_name=skill_data.name,
                proficiency_level=skill_data.proficiency_level or ProficiencyLevel.INTERMEDIATE,
                evidence_source=evidence_source,
                last_used_year=skill_data.last_used_year
            )
            user_skills.append(user_skill)
        return user_skills

    def get_user_skills(self, db: Session, user_id: str) -> UserSkillResponse:
        """Get all skills for a user"""
        user_uuid = uuid.UUID(user_id)
        
        user_skills = db.query(UserSkill, Skill).join(
            Skill, UserSkill.skill_id == Skill.id
        ).filter(UserSkill.user_id == user_uuid).all()
        
        skills = []
        for user_skill, skill in user_skills:
            skills.append(SkillResponse(
                id=str(skill.id),
                name=skill.name,
                category=skill.category,
                proficiency_level=self.map_int_to_proficiency(user_skill.proficiency_level or 1),
                evidence_source=EvidenceSource(user_skill.evidence_source) if user_skill.evidence_source else EvidenceSource.IMPLIED,
                last_used_year=user_skill.last_used_year,
                created_at=user_skill.created_at
            ))
        
        return UserSkillResponse(
            user_id=user_id,
            skills=skills,
            total_count=len(skills)
        )

    def add_education(
        self,
        db: Session,
        user_id: str,
        education_data: EducationCreate
    ) -> Education:
        """Add education record"""
        education = Education(
            id=uuid.uuid4(),
            user_id=uuid.UUID(user_id),
            degree=education_data.degree,
            institution=education_data.institution,
            field_of_study=education_data.field_of_study,
            start_year=education_data.start_year,
            end_year=education_data.end_year,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(education)
        db.flush()
        return education

    def get_user_education(self, db: Session, user_id: str) -> List[EducationResponse]:
        """Get user education"""
        education_records = db.query(Education).filter(
            Education.user_id == uuid.UUID(user_id)
        ).order_by(Education.end_year.desc().nullsfirst()).all()
        
        return [EducationResponse(
            id=str(edu.id),
            degree=edu.degree,
            institution=edu.institution,
            field_of_study=edu.field_of_study,
            start_year=edu.start_year,
            end_year=edu.end_year,
            created_at=edu.created_at
        ) for edu in education_records]

    # --- LLM Extraction ---

    async def extract_skills_from_text(self, text: str) -> List[Dict]:
        """
        Extract skills from conversation text using LLM.
        Returns list of dicts: {"name": str, "evidence": str, "confidence": float}
        """
        if not self.model:
            return []

        try:
            prompt = f"""{SKILL_EXTRACTOR_PROMPT}
            
            INPUT TEXT:
            "{text}"
            """
            
            response = self.model.generate_content(prompt)
            data = json.loads(response.text)
            return data.get("skills", [])
            
        except Exception as e:
            logger.error(f"Skill extraction failed: {e}")
            return []

    def parse_resume_for_skills(self, resume_text: str) -> List[SkillCreate]:
        """Simple regex-based parser"""
        # Common skill keywords
        common_skills = [
            "python", "java", "javascript", "typescript", "react", "node.js", "sql", "postgresql",
            "mongodb", "aws", "azure", "docker", "kubernetes", "git", "agile", "scrum",
            "machine learning", "deep learning", "tensorflow", "pytorch", "data analysis",
            "excel", "tableau", "power bi", "project management", "leadership", "communication"
        ]
        
        resume_lower = resume_text.lower()
        found_skills = []
        
        for skill in common_skills:
            if skill in resume_lower:
                found_skills.append(SkillCreate(
                    name=skill.title(),
                    proficiency_level=ProficiencyLevel.INTERMEDIATE
                ))
        
        return found_skills

    def apply_role_priors(self, db: Session, user_id: str, occupation_code: str):
        """
        Seed user skills based on their role.
        (Legacy support - simplified)
        """
        # This would need to be updated to use the new schema if used
        pass


skill_service = SkillService()
