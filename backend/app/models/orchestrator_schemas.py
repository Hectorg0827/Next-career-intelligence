"""
Orchestrator Output Schema
The standardized JSON structure returned by the multi-agent system
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class DisplacementRiskLevel(str, Enum):
    """AI displacement risk levels"""

    VERY_LOW = "Very Low"
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class AIDisplacementRiskOutput(BaseModel):
    """AI displacement risk assessment"""

    level: DisplacementRiskLevel
    justification: str = Field(
        ..., description="Brief, clear reason for this risk level, focusing on core tasks and required human skills"
    )


class GapSeverity(str, Enum):
    """Skill gap severity levels"""

    MINOR = "minor gap"
    MEDIUM = "medium gap"
    CRITICAL = "critical gap"


class SkillGap(BaseModel):
    """A specific skill or experience gap"""

    skill_or_experience: str
    severity: GapSeverity
    time_to_close: str  # "2 weeks", "3 months", "requires certification", etc.
    positioning_advice: Optional[str] = None  # How to sell yourself anyway


class NextStep(BaseModel):
    """Concrete, actionable next step for the user"""

    action: str
    timeline: str = "immediate"  # "immediate", "this week", "this month"
    rationale: Optional[str] = None


class InfoRequest(BaseModel):
    """Question the coach should ask the user"""

    question: str
    reason: str  # Why we need this info
    field_to_populate: str  # Which profile field this will help fill


class OrchestratorOutput(BaseModel):
    """
    Standard output schema for all career analysis
    This is what the multi-agent orchestrator returns
    """

    # Risk Assessment
    ai_displacement_risk: AIDisplacementRiskOutput

    # Compatibility & Fit
    compatibility_score: int = Field(
        ..., ge=0, le=100, description="Overall match score considering skills, preferences, and alignment"
    )

    match_highlights: List[str] = Field(default=[], description="Key reasons why this is a good match")

    # Gaps & Growth
    skill_gaps_for_job: List[SkillGap] = Field(
        default=[], description="Missing skills or experience, with severity and advice"
    )

    next_steps_for_user: List[str] = Field(
        default=[], description="Concrete, short-term actions the user can take immediately"
    )

    # Profile Updates (Learning Loop)
    profile_update: Dict[str, Any] = Field(
        default={
            "new_skills_detected": [],
            "new_preferences_detected": [],
            "new_goals_detected": [],
            "risk_signals_detected": [],
            "motivation_signals_detected": [],
            "development_needs_detected": [],
        },
        description="New information to merge back into the User Profile",
    )

    # Coach Interaction
    info_request_for_coach: List[str] = Field(
        default=[], description="Questions the coach should ask to fill missing profile data"
    )

    # Internal Scores (for ranking/sorting)
    internal_scores: Optional[Dict[str, int]] = Field(
        default=None, description="Internal scores for backend use (stability, trajectory, etc.)"
    )

    # Warnings & Flags
    warnings: List[str] = Field(default=[], description="Red flags or cautions about this opportunity")

    class Config:
        json_schema_extra = {
            "example": {
                "ai_displacement_risk": {
                    "level": "Low",
                    "justification": "This role depends on live parent coaching, de-escalation, and case-specific behavioral planning for neurodiverse children. These are high-trust, situational judgment tasks that are not easily automated in the next 2-3 years.",
                },
                "compatibility_score": 91,
                "match_highlights": [
                    "Your 8 years working directly with students who have behavioral and learning challenges is directly aligned.",
                    "This role values one-on-one coaching and family guidance, which matches what you enjoy most.",
                    "Less classroom admin/testing pressure compared to your current environment.",
                ],
                "skill_gaps_for_job": [
                    {
                        "skill_or_experience": "District reporting software",
                        "severity": "minor gap",
                        "time_to_close": "1-2 weeks",
                        "positioning_advice": "Say: 'I'm comfortable with structured reporting workflows and can learn new systems quickly.'",
                    }
                ],
                "next_steps_for_user": [
                    "Position yourself as a behavior coach for both students AND parents, not just an in-class teacher.",
                    "Collect 1-2 concrete success stories where you reduced classroom incidents or helped a student self-regulate.",
                    "Get familiar with basic digital case-note systems.",
                ],
                "profile_update": {
                    "new_skills_detected": ["Behavioral intervention planning", "Parent coaching"],
                    "new_preferences_detected": ["Prefers remote or hybrid over full-time classroom"],
                    "new_goals_detected": ["Better pay and flexibility without leaving student support"],
                    "risk_signals_detected": ["Emotional burnout from admin/testing requirements"],
                },
                "info_request_for_coach": [
                    "What salary range feels fair for you right now?",
                    "Are you comfortable doing video calls with parents a few hours a day?",
                    "Do you want to manage other adults, or stay individual-contributor?",
                ],
            }
        }


class JobOpportunity(BaseModel):
    """Standardized job data for evaluation"""

    job_id: Optional[str] = None
    title: str
    company: str
    location: Optional[str] = None
    is_remote: bool = False
    remote_type: Optional[str] = None  # "fully_remote", "hybrid", "on_site"

    required_skills: List[str] = []
    nice_to_have_skills: List[str] = []
    responsibilities: List[str] = []

    seniority_level: Optional[str] = None  # "entry", "mid", "senior", "lead", "executive"

    compensation: Optional[Dict[str, Any]] = None  # {"min": 80000, "max": 120000, "currency": "USD"}

    # Market context
    demand_level: Optional[str] = None  # "high", "stable", "shrinking"
    automation_risk_industry: Optional[str] = None  # "low", "medium", "high"

    # Raw data
    description: Optional[str] = None
    posted_date: Optional[str] = None
    source: Optional[str] = None
