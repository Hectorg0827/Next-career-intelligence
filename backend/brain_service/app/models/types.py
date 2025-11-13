"""
Type definitions for brain service
"""
from typing import List, Optional, Dict, Literal
from pydantic import BaseModel, Field
from datetime import datetime


class Skill(BaseModel):
    """User or job skill"""
    name: str
    proficiency: float = Field(default=0.5, ge=0, le=1, description="User proficiency (0-1)")
    importance: float = Field(default=1.0, ge=0, le=1, description="Job importance (0-1)")
    years_experience: Optional[int] = Field(default=None, description="Years of experience with skill")
    last_used: Optional[datetime] = Field(default=None, description="When skill was last used")


class SkillMatchResult(BaseModel):
    """Result of semantic skill matching"""
    score: float = Field(..., ge=0, le=100, description="Match score 0-100")
    matched_skills: List[Dict] = Field(default_factory=list, description="Skills that matched")
    missing_skills: List[Dict] = Field(default_factory=list, description="Required skills user is missing")
    skill_gap_severity: Literal["low", "medium", "high"] = Field(..., description="How severe are the gaps")
    explanation: str = Field(..., description="Human-readable explanation")
    match_percentage: float = Field(..., ge=0, le=100, description="% of required skills matched")


class ExperienceMatch(BaseModel):
    """Result of experience level matching"""
    score: float = Field(..., ge=0, le=100, description="Match score 0-100")
    years_score: float = Field(..., ge=0, le=100)
    seniority_score: float = Field(..., ge=0, le=100)
    trajectory_score: float = Field(..., ge=0, le=100)
    is_appropriate: bool = Field(..., description="Is this experience level appropriate?")
    concerns: List[str] = Field(default_factory=list, description="Potential concerns")
    explanation: str = Field(..., description="Human-readable explanation")


class CareerHealthComponents(BaseModel):
    """Components of career health score"""
    skill_relevance: float = Field(..., ge=0, le=100)
    experience_trajectory: float = Field(..., ge=0, le=100)
    market_positioning: float = Field(..., ge=0, le=100)
    learning_velocity: float = Field(..., ge=0, le=100)
    automation_resilience: float = Field(..., ge=0, le=100)


class CareerHealthResult(BaseModel):
    """Complete career health assessment"""
    score: float = Field(..., ge=0, le=100, description="Overall health score")
    grade: str = Field(..., description="Letter grade A-F")
    components: CareerHealthComponents
    trend_7d: Optional[float] = Field(default=None, description="Score change over 7 days")
    trend_30d: Optional[float] = Field(default=None, description="Score change over 30 days")
    insights: List[str] = Field(default_factory=list, description="Actionable insights")
    action_items: List[Dict] = Field(default_factory=list, description="Specific actions to improve")
    risk_level: Literal["low", "medium", "high"] = Field(..., description="Overall career risk")


class MatchScoreComponents(BaseModel):
    """All components contributing to match score"""
    hard_skills: float = Field(..., ge=0, le=100)
    soft_skills: float = Field(default=50.0, ge=0, le=100)
    experience: float = Field(..., ge=0, le=100)
    goal_alignment: float = Field(default=50.0, ge=0, le=100)
    automation_safety: float = Field(..., ge=0, le=100)
    trajectory: float = Field(default=50.0, ge=0, le=100)
    preferences: float = Field(default=50.0, ge=0, le=100)


class ComprehensiveMatchResult(BaseModel):
    """Complete job match result"""
    overall_score: float = Field(..., ge=0, le=100, description="Final match score")
    components: MatchScoreComponents
    skill_details: SkillMatchResult
    experience_details: ExperienceMatch
    should_apply: bool = Field(..., description="Recommendation to apply")
    confidence: Literal["low", "medium", "high"] = Field(..., description="Confidence in score")
    explanation: Optional[str] = Field(default=None, description="LLM-generated explanation")
    timestamp: datetime = Field(default_factory=datetime.now)


# Simple data classes for inputs
class UserProfile(BaseModel):
    """Simplified user profile for matching"""
    user_id: str
    current_title: str
    years_experience: int
    skills: List[Skill]
    current_salary: Optional[int] = None
    location: Optional[str] = None
    career_health_score: Optional[float] = None


class JobPosting(BaseModel):
    """Simplified job posting for matching"""
    job_id: str
    title: str
    company: str
    required_skills: List[Skill]
    experience_required: str  # e.g., "5-7 years"
    description: str
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    location: Optional[str] = None
    is_remote: bool = False
    automation_risk: float = Field(default=50.0, ge=0, le=100)
