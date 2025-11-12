"""
User Profile - Single Source of Truth
Persistent, evolving record of the user's career identity
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class WorkHistoryEntry(BaseModel):
    """Individual work experience entry"""

    role: str
    company: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None  # None means current
    industry: Optional[str] = None
    responsibilities: List[str] = []
    achievements: List[str] = []
    skills_used: List[str] = []


class CareerGoal(BaseModel):
    """User's career objectives"""

    timeframe: str  # "short-term" (0-12mo), "mid-term" (1-3yr), "long-term" (3+yr)
    description: str
    priority: int = Field(ge=1, le=10, default=5)


class PreferenceCategory(str, Enum):
    """Categories of user preferences"""

    WORK_STYLE = "work_style"
    TEAM_TYPE = "team_type"
    LOCATION = "location"
    COMPENSATION = "compensation"
    WORK_LIFE_BALANCE = "work_life_balance"
    CAREER_VALUES = "career_values"


class UserPreference(BaseModel):
    """Specific user preference"""

    category: PreferenceCategory
    preference: str
    strength: int = Field(ge=1, le=10, default=5)  # How important
    is_dealbreaker: bool = False


class RiskFactor(BaseModel):
    """Career risk or threat"""

    type: str  # "automation", "layoff", "burnout", "market_decline", etc.
    description: str
    severity: int = Field(ge=1, le=10)
    detected_at: datetime = Field(default_factory=datetime.utcnow)


class MotivationSignal(BaseModel):
    """What drives or drains the user"""

    signal_type: str  # "enjoy", "hate", "fear_losing", "aspire_to"
    description: str
    intensity: int = Field(ge=1, le=10)
    source: str = "conversation"  # "conversation", "behavior", "assessment"


class DevelopmentNeed(BaseModel):
    """Skills or experience gaps to address"""

    skill_or_experience: str
    gap_size: str  # "minor", "medium", "critical"
    time_to_close: str  # "2 weeks", "3 months", "1+ year"
    recommended_actions: List[str] = []
    priority: int = Field(ge=1, le=10, default=5)


class Skill(BaseModel):
    """User skill with proficiency"""

    name: str
    category: str  # "hard", "soft", "transferable", "technical", "domain"
    proficiency: int = Field(ge=1, le=10, default=5)
    years_experience: Optional[float] = None
    last_used: Optional[datetime] = None
    is_verified: bool = False  # From endorsements, certifications, etc.


class UserProfile(BaseModel):
    """
    Single Source of Truth for User Identity
    This is the persistent, evolving record that all agents read from and update
    """

    # Core Identity
    user_id: str
    email: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    # Work History
    work_history: List[WorkHistoryEntry] = []
    current_role: Optional[str] = None
    current_company: Optional[str] = None
    years_total_experience: Optional[float] = None

    # Skills & Competencies
    skills: List[Skill] = []
    core_competencies: List[str] = []  # Top 5-10 proven strengths
    transferable_skills: List[str] = []

    # Preferences & Constraints
    preferences: List[UserPreference] = []
    dealbreakers: List[str] = []  # Absolute no-gos

    # Career Goals & Aspirations
    career_goals: List[CareerGoal] = []
    desired_roles: List[str] = []
    target_industries: List[str] = []

    # Risk & Stability
    risk_factors: List[RiskFactor] = []
    current_job_stability_score: Optional[int] = Field(None, ge=0, le=100)

    # Motivation & Sentiment
    motivation_signals: List[MotivationSignal] = []
    burnout_level: Optional[int] = Field(None, ge=0, le=10)  # 0=energized, 10=critical
    confidence_level: Optional[int] = Field(None, ge=0, le=10)

    # Development Needs
    development_needs: List[DevelopmentNeed] = []

    # Behavioral Data (learning from actions)
    jobs_viewed: List[str] = []  # Job IDs
    jobs_saved: List[str] = []
    jobs_applied: List[str] = []
    jobs_rejected: List[str] = []
    rejection_reasons: Dict[str, str] = {}  # job_id -> reason

    # Contextual Data
    location: Optional[str] = None
    remote_preference: Optional[str] = None  # "remote_only", "hybrid", "on_site", "flexible"
    salary_expectations: Optional[Dict[str, Any]] = None  # {"min": 80000, "target": 100000, "currency": "USD"}
    relocation_willing: bool = False

    # Assessment Data
    personality_insights: Optional[Dict[str, Any]] = None
    strengths_profile: Optional[List[str]] = None
    communication_style: Optional[str] = None

    # Metadata for Learning
    total_interactions: int = 0
    last_interaction_at: Optional[datetime] = None
    profile_completeness: int = Field(default=0, ge=0, le=100)  # % of fields filled

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "email": "jane@example.com",
                "current_role": "Special Education Teacher",
                "years_total_experience": 8,
                "skills": [
                    {"name": "Behavior Intervention", "category": "hard", "proficiency": 9},
                    {"name": "Parent Communication", "category": "soft", "proficiency": 8},
                ],
                "preferences": [
                    {
                        "category": "location",
                        "preference": "Remote or hybrid work",
                        "strength": 9,
                        "is_dealbreaker": False,
                    }
                ],
                "motivation_signals": [
                    {"signal_type": "enjoy", "description": "One-on-one mentoring with students", "intensity": 9},
                    {
                        "signal_type": "hate",
                        "description": "Standardized testing pressure and admin paperwork",
                        "intensity": 8,
                    },
                ],
                "burnout_level": 7,
                "career_goals": [
                    {
                        "timeframe": "short-term",
                        "description": "Find a role with better flexibility and less testing pressure",
                        "priority": 10,
                    }
                ],
            }
        }


class ProfileUpdate(BaseModel):
    """
    Updates to be merged into the User Profile
    Generated by agents after each interaction
    """

    new_skills_detected: List[Skill] = []
    new_preferences_detected: List[UserPreference] = []
    new_goals_detected: List[CareerGoal] = []
    risk_signals_detected: List[RiskFactor] = []
    motivation_signals_detected: List[MotivationSignal] = []
    development_needs_detected: List[DevelopmentNeed] = []

    # Behavioral updates
    job_interaction: Optional[Dict[str, Any]] = (
        None  # {"job_id": "...", "action": "viewed/saved/applied/rejected", "reason": "..."}
    )

    # Sentiment updates
    burnout_level_update: Optional[int] = None
    confidence_level_update: Optional[int] = None
