"""
AI Displacement Risk Engine - Data Models
Models for request/response structures following the v1.0 specification.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# ========================================
# INPUT MODELS
# ========================================

class UserSkill(BaseModel):
    """User's current skill with proficiency."""
    skill_name: str
    proficiency: float = Field(..., ge=0.0, le=1.0)  # 0.0 to 1.0
    years_experience: float = Field(..., ge=0.0)
    last_used_days_ago: int = Field(0, ge=0)


class UserCredential(BaseModel):
    """User's degree or certification."""
    credential_type: str  # "degree", "certification"
    name: str
    issuer: Optional[str] = None
    year_obtained: Optional[int] = None


class UserAction(BaseModel):
    """User learning/adaptation action."""
    action_type: str  # "course", "project", "certification", "publication"
    linked_skills: List[str] = []
    days_ago: int = Field(..., ge=0)
    has_certificate: bool = False
    has_verified_project: bool = False


class UserProfile(BaseModel):
    """Complete user profile for risk analysis."""
    user_id: str
    years_experience: int = Field(..., ge=0)
    people_management: bool = False
    decision_level: float = Field(0.0, ge=0.0, le=1.0)  # 0.0 to 1.0
    domain_depth_years: int = Field(0, ge=0)
    skills: List[UserSkill] = []
    credentials: List[UserCredential] = []
    action_log: List[UserAction] = []


class JobData(BaseModel):
    """Job/role data for risk analysis."""
    occupation_code: str  # O*NET SOC code (e.g., "15-2051")
    industry: str
    wage_level: float = Field(..., ge=0.0, le=1.0)  # 0.0 to 1.0 (normalized)
    technical_readiness: float = Field(..., ge=0.0, le=1.0)  # Industry's AI readiness


class RiskAnalysisRequest(BaseModel):
    """Complete request for risk analysis."""
    user_profile: UserProfile
    job_data: JobData


# ========================================
# OUTPUT MODELS
# ========================================

class DisplacementRiskScore(BaseModel):
    """Core displacement risk score with context."""
    level: str  # "Low", "Medium", "High", "Critical"
    score: float = Field(..., ge=0.0, le=100.0)
    time_horizon: str  # "0-2 years", "2-5 years", "5+ years"
    confidence: float = Field(..., ge=0.0, le=100.0)
    percentile_vs_role: Optional[float] = Field(None, ge=0.0, le=100.0)  # May be None if no peer data
    trajectory: str  # "improving", "stable", "worsening"
    justification: str
    primary_vulnerabilities: List[str] = []
    protection_opportunities: List[str] = []


class DebugComponents(BaseModel):
    """Debug breakdown of all component scores."""
    StructuralRisk: float
    PersonalShield: float
    TAS: float
    IVS: float
    PSC: float
    AS: float
    SeniorityProtection: float
    CredentialStrength: float
    TimeHorizonIndex: float
    Confidence: float


class RiskAnalysisResponse(BaseModel):
    """Complete risk analysis response."""
    ai_displacement_risk: DisplacementRiskScore
    debug_components: DebugComponents
    calculated_at: datetime = Field(default_factory=datetime.utcnow)


# ========================================
# DATABASE MODELS (for ORM)
# ========================================

class TaskTaxonomyRecord(BaseModel):
    """Record from ai_task_taxonomy table."""
    occupation_code: str
    task_id: str
    task_name: str
    task_description: Optional[str] = None
    importance_score: float
    frequency_score: float
    technical_capability: float
    economic_viability: float
    task_risk: float
    confidence_level: Optional[float] = None


class SkillDemandRecord(BaseModel):
    """Record from skill_demand_history table."""
    skill_name: str
    industry: str
    demand_score: float
    trend_score: float
    ai_job_postings: int
    legacy_job_postings: int
    snapshot_date: datetime


class AutomationEvidenceRecord(BaseModel):
    """Record from automation_evidence table."""
    entity_type: str  # "task" or "skill"
    entity_id: str
    substitutability: float
    complementarity: float
    evidence_source: Optional[str] = None
