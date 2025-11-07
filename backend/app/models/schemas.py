"""
Pydantic models for request/response validation
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class RiskLevel(str, Enum):
    """AI displacement risk levels"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class AnalysisRequest(BaseModel):
    """Request model for career analysis"""
    job_title: str = Field(..., min_length=2, max_length=200, description="Current job title")
    skills: List[str] = Field(default_factory=list, description="List of current skills")
    location: str = Field(..., description="Country or region")
    years_experience: Optional[int] = Field(None, ge=0, le=50, description="Years of experience")

    @validator('skills', pre=True, always=True)
    def validate_skills(cls, v, values):
        """Ensure skill list is usable, add sensible fallback when empty"""
        provided_skills = v or []
        cleaned = [skill.strip() for skill in provided_skills if isinstance(skill, str) and skill.strip()]
        if cleaned:
            return cleaned

        # When no skills are provided, generate a fallback based on job title so AI has context
        job_title = values.get('job_title') or 'Professional'
        return [f"{job_title} core skills"]


class AIDisplacementRisk(BaseModel):
    """AI displacement risk assessment"""
    level: RiskLevel
    score: float = Field(..., ge=0, le=100, description="Risk score 0-100")
    velocity: str = Field(..., description="Timeline for automation")
    augmentation_potential: str = Field(..., description="Potential for AI augmentation")
    reasoning: Optional[str] = Field(None, description="Explanation of risk assessment")


class TransitionPathway(BaseModel):
    """Career transition pathway recommendation"""
    role: str = Field(..., description="Target role title")
    ease: float = Field(..., ge=0, le=100, description="Ease of transition score")
    required_skills: List[str] = Field(..., description="Skills needed for transition")
    estimated_training_time: Optional[str] = Field(None, description="Estimated time to acquire skills")
    salary_potential: Optional[str] = Field(None, description="Expected salary range")
    demand_trend: Optional[str] = Field(None, description="Job demand trend")


class TrainingResource(BaseModel):
    """Training course recommendation"""
    title: str
    provider: str
    url: str
    duration: Optional[str] = None
    skill_covered: str
    cost: Optional[str] = None
    rating: Optional[float] = None


class AnalysisResponse(BaseModel):
    """Response model for career analysis"""
    analysis_id: str
    job_title: str
    ai_displacement_risk: AIDisplacementRisk
    compatibility_score: float = Field(..., ge=0, le=100)
    human_advantage_factors: List[str]
    automation_vulnerable_tasks: List[str]
    automation_resistant_tasks: List[str]
    transition_pathways: List[TransitionPathway]
    skill_gaps: List[str]
    recommended_training: List[TrainingResource]
    created_at: datetime
    metadata: Optional[Dict[str, Any]] = None


class JobSuggestion(BaseModel):
    """Job title suggestion for autocomplete"""
    code: str = Field(..., description="O*NET-SOC code")
    title: str = Field(..., description="Job title")
    description: Optional[str] = Field(None, description="Brief description")


class UserCreate(BaseModel):
    """User creation model"""
    email: str
    firebase_uid: str
    name: Optional[str] = None


class UserResponse(BaseModel):
    """User response model"""
    id: str
    email: str
    name: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class AnalysisHistoryItem(BaseModel):
    """Analysis history item"""
    analysis_id: str
    job_title: str
    risk_score: float
    compatibility_score: float
    created_at: datetime
    
    class Config:
        from_attributes = True


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    timestamp: datetime
    services: Dict[str, str]
