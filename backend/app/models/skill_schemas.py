"""
Pydantic schemas for skill-related operations
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class ProficiencyLevel(str, Enum):
    """Skill proficiency levels"""
    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"
    EXPERT = "EXPERT"


class EvidenceSource(str, Enum):
    """Evidence source for skill"""
    SELF_REPORTED = "SELF_REPORTED"
    MANUAL = "MANUAL"
    RESUME = "RESUME"
    CONVERSATION = "CONVERSATION"
    IMPLIED = "IMPLIED"


# ============================================================================
# Request Models
# ============================================================================


class SkillCreate(BaseModel):
    """Request model for creating/adding a skill manually"""
    name: str = Field(..., min_length=1, max_length=255)
    proficiency_level: Optional[ProficiencyLevel] = ProficiencyLevel.INTERMEDIATE
    last_used_year: Optional[float] = None


class ManualSkillsRequest(BaseModel):
    """Request to add multiple skills manually"""
    skills: List[SkillCreate]


class ResumeUploadRequest(BaseModel):
    """Request model for resume upload"""
    resume_text: str = Field(..., min_length=10)


class ConversationSkillRequest(BaseModel):
    """Request model for extracting skills from conversation"""
    conversation_transcript: str = Field(..., min_length=10)


class EducationCreate(BaseModel):
    """Request model for adding education"""
    degree: str = Field(..., min_length=1, max_length=255)
    institution: str = Field(..., min_length=1, max_length=255)
    field_of_study: Optional[str] = None
    start_year: Optional[float] = None
    end_year: Optional[float] = None


class SkillGapRequest(BaseModel):
    """Request model for skill gap analysis"""
    target_role_title: str = Field(..., min_length=2, max_length=200)
    target_role_id: Optional[str] = None


# ============================================================================
# Response Models
# ============================================================================


class SkillResponse(BaseModel):
    """Response model for a skill"""
    id: str
    name: str
    category: Optional[str] = None
    proficiency_level: ProficiencyLevel
    evidence_source: EvidenceSource
    last_used_year: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserSkillResponse(BaseModel):
    """Response model for user's skills"""
    user_id: str
    skills: List[SkillResponse]
    total_count: int


class EducationResponse(BaseModel):
    """Response model for education"""
    id: str
    degree: str
    institution: str
    field_of_study: Optional[str] = None
    start_year: Optional[float] = None
    end_year: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Skill Gap Analysis Models
# ============================================================================


class MatchedSkill(BaseModel):
    """A skill the user has that matches the target role"""
    name: str
    proficiency_level: ProficiencyLevel
    relevance_score: float = Field(..., ge=0, le=100)


class GapSkill(BaseModel):
    """A skill the user is missing for the target role"""
    name: str
    importance: str = Field(..., description="Low, Medium, High, Critical")
    estimated_time_to_learn: Optional[str] = None
    recommended_resources: List[str] = Field(default_factory=list)


class LearningCluster(BaseModel):
    """A group of related skills to learn together"""
    cluster_name: str
    skills: List[str]
    estimated_time: Optional[str] = None
    priority: str = Field(..., description="Low, Medium, High")


class SkillGapAnalysis(BaseModel):
    """Complete skill gap analysis response"""
    
    # Summary
    title: str = Field(..., description="e.g., 'Your Skill Match for Data Analyst'")
    summary: str = Field(..., description="Concise paragraph summary")
    
    # Scores
    role_fit_score: float = Field(..., ge=0, le=100, description="Overall fit score")
    
    # Matched skills (what user has)
    matched_skills: List[MatchedSkill] = Field(default_factory=list)
    matched_count: int
    
    # Gap skills (what user is missing)
    gap_skills: List[GapSkill] = Field(default_factory=list)
    gap_count: int
    
    # Weak skills (user has but low proficiency)
    weak_skills: List[MatchedSkill] = Field(default_factory=list)
    
    # Learning recommendations
    suggested_learning_clusters: List[LearningCluster] = Field(default_factory=list)
    
    # Metadata
    target_role: str
    analysis_date: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Your Skill Match for Data Analyst",
                "summary": "You have 8 of 12 core skills for a Data Analyst role. Your Python and SQL skills are strong matches. Focus on learning statistical analysis and data visualization tools to increase your readiness.",
                "role_fit_score": 67.0,
                "matched_skills": [
                    {"name": "Python", "proficiency_level": "ADVANCED", "relevance_score": 95.0},
                    {"name": "SQL", "proficiency_level": "INTERMEDIATE", "relevance_score": 85.0}
                ],
                "matched_count": 8,
                "gap_skills": [
                    {
                        "name": "Statistics",
                        "importance": "Critical",
                        "estimated_time_to_learn": "3-6 months",
                        "recommended_resources": ["Statistics for Data Science - Coursera"]
                    }
                ],
                "gap_count": 4,
                "weak_skills": [],
                "suggested_learning_clusters": [
                    {
                        "cluster_name": "Data Visualization",
                        "skills": ["Tableau", "Power BI", "Matplotlib"],
                        "estimated_time": "2-3 months",
                        "priority": "High"
                    }
                ],
                "target_role": "Data Analyst",
                "analysis_date": "2025-11-18T13:00:00Z"
            }
        }
