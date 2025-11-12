"""
Pydantic schemas for Resume Studio premium features
Request/Response validation for API endpoints
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


# ========================================
# CAREER PROFILE SCHEMAS (SSOT)
# ========================================


class WorkHistoryItem(BaseModel):
    """Individual work experience entry"""

    id: Optional[str] = None
    company: str = Field(..., min_length=1, max_length=255)
    title: str = Field(..., min_length=1, max_length=255)
    location: Optional[str] = None
    employment_type: str = Field(default="Full-time", description="Full-time|Contract|Part-time|Internship")
    start_date: str = Field(..., description="Format: MMM YYYY (e.g., Jan 2020)")
    end_date: str = Field(..., description="Format: MMM YYYY or 'Present'")
    bullets: List[str] = Field(default=[], description="Action-oriented bullet points")
    tech_stack: List[str] = Field(default=[], description="Technologies used")
    domains: List[str] = Field(default=[], description="Industry domains")


class EducationItem(BaseModel):
    """Education entry"""

    institution: str
    degree: str
    field_of_study: Optional[str] = None
    graduation_date: Optional[str] = None
    gpa: Optional[str] = None
    honors: List[str] = Field(default=[])


class CertificationItem(BaseModel):
    """Certification entry"""

    name: str
    issuer: str
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None
    credential_id: Optional[str] = None
    url: Optional[str] = None


class SkillsSet(BaseModel):
    """Structured skills taxonomy"""

    hard: List[str] = Field(default=[], description="Technical/hard skills")
    soft: List[str] = Field(default=[], description="Soft/interpersonal skills")
    domains: List[str] = Field(default=[], description="Domain expertise")


class AchievementItem(BaseModel):
    """Notable achievement"""

    title: str
    description: str
    date: Optional[str] = None
    impact: Optional[str] = None


class CareerProfileBasics(BaseModel):
    """Basic contact information"""

    full_name: Optional[str] = None
    headline: Optional[str] = Field(None, max_length=500)
    location: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    links: List[str] = Field(default=[], description="LinkedIn, portfolio, GitHub, etc.")


class CareerProfileMetadata(BaseModel):
    """Profile metadata"""

    ats_normalized: bool = False
    last_verified_iso: Optional[str] = None
    sources: List[str] = Field(default=[], description="resume_upload, linkedin_paste, coach_suggestion, etc.")


class CareerProfileData(BaseModel):
    """Complete career profile - Single Source of Truth"""

    basics: CareerProfileBasics = Field(default_factory=CareerProfileBasics)
    work_history: List[WorkHistoryItem] = Field(default=[])
    education: List[EducationItem] = Field(default=[])
    certifications: List[CertificationItem] = Field(default=[])
    skills: SkillsSet = Field(default_factory=SkillsSet)
    achievements: List[AchievementItem] = Field(default=[])
    metadata: CareerProfileMetadata = Field(default_factory=CareerProfileMetadata)


class CareerProfileResponse(BaseModel):
    """Career profile API response"""

    id: str
    user_id: str
    profile_data: CareerProfileData
    created_at: datetime
    updated_at: datetime


# ========================================
# RESUME STUDIO INPUT/OUTPUT SCHEMAS
# ========================================


class IngestRequest(BaseModel):
    """Request to ingest and parse resume/profile"""

    text: Optional[str] = Field(None, description="Plain text resume or LinkedIn content")
    file_id: Optional[str] = Field(None, description="Reference to uploaded file")
    linkedin_url: Optional[str] = Field(None, description="LinkedIn profile URL")
    user_id: str


class ValidationSummary(BaseModel):
    """Summary of profile validation"""

    summary: str = Field(..., description="Human-readable summary of parsing")
    profile_patch_json: Dict[str, Any] = Field(..., description="Partial profile data (only confident fields)")
    open_questions: List[str] = Field(default=[], description="Clarifications needed from user")
    conflicts: List[str] = Field(default=[], description="Data conflicts found")


class ConfirmIngestRequest(BaseModel):
    """Request to confirm and save parsed profile"""

    user_id: str
    profile_patch: Dict[str, Any]
    resolved_questions: Optional[Dict[str, Any]] = None


class JobDescriptionInput(BaseModel):
    """Job description for tailoring"""

    title: str
    seniority: Optional[str] = Field(None, description="IC|Manager|Senior|Entry")
    company: str
    location: Optional[str] = None
    must_haves: List[str] = Field(default=[])
    nice_to_haves: List[str] = Field(default=[])
    keywords: List[str] = Field(default=[])
    industry: Optional[str] = None
    region: str = Field(default="US", description="US|UK|EU for ATS localization")
    description: Optional[str] = Field(None, description="Full JD text if available")


class KeywordCoverage(BaseModel):
    """Keyword matching analysis"""

    matched: List[str] = Field(default=[])
    missing: List[str] = Field(default=[])
    coverage_percentage: Optional[float] = None


class TailoredResumeOutput(BaseModel):
    """Output from resume tailoring"""

    summary: str = Field(..., description="2-4 line summary aligned to JD")
    core_skills: Dict[str, List[str]] = Field(default={}, description="Categorized skills")
    experience: List[Dict[str, Any]] = Field(default=[], description="Reordered and rewritten roles")
    education: List[EducationItem] = Field(default=[])
    certifications: List[CertificationItem] = Field(default=[])
    ats_notes: List[str] = Field(default=[], description="ATS compliance notes")
    risk_flags: List[str] = Field(default=[], description="Potential issues or gaps")
    keyword_coverage: KeywordCoverage = Field(default_factory=KeywordCoverage)
    placeholders: List[str] = Field(default=[], description="Items needing user confirmation")


class CoverLetterStructure(BaseModel):
    """Cover letter structure"""

    salutation: str = Field(default="Hiring Manager")
    opening: str
    body: List[str] = Field(..., description="2-3 paragraphs")
    closing: str
    signature_block: str
    placeholders: List[str] = Field(default=[])


class TailoredCoverLetterOutput(BaseModel):
    """Output from cover letter generation"""

    cover_letter: CoverLetterStructure
    word_count: Optional[int] = None
    tone: str = Field(default="professional")


class TailorResumeRequest(BaseModel):
    """Request to tailor resume"""

    user_id: str
    job_description: JobDescriptionInput


class TailorCoverLetterRequest(BaseModel):
    """Request to tailor cover letter"""

    user_id: str
    job_description: JobDescriptionInput


# ========================================
# PROFILE SUGGESTIONS SCHEMAS
# ========================================


class ProfilePatchSuggestion(BaseModel):
    """Suggestion for profile improvement"""

    id: Optional[str] = None
    source: str = Field(..., description="coach|interviewer|manual")
    suggestion_type: str = Field(..., description="bullet|skill|achievement|certification")
    proposed_patch: Dict[str, Any] = Field(..., description="JSON patch to apply")
    evidence: Optional[str] = None
    confidence_score: float = Field(..., ge=0, le=1)
    reasoning: str
    status: str = Field(default="pending", description="pending|accepted|rejected")


class ApplySuggestionRequest(BaseModel):
    """Request to apply a user-confirmed suggestion"""

    user_id: str
    suggestion_id: str
    user_confirmed: bool = Field(..., description="Must be true to apply")

    @validator("user_confirmed")
    def must_be_confirmed(cls, v):
        if not v:
            raise ValueError("user_confirmed must be true to apply suggestion")
        return v


class ApplySuggestionResponse(BaseModel):
    """Response after applying suggestion"""

    success: bool
    audit_note: str
    updated_profile: Optional[CareerProfileData] = None


class SuggestionsListResponse(BaseModel):
    """List of pending suggestions"""

    suggestions: List[ProfilePatchSuggestion]
    total_count: int


# ========================================
# ARTIFACT SCHEMAS
# ========================================


class ArtifactResponse(BaseModel):
    """Resume or cover letter artifact"""

    id: str
    user_id: str
    artifact_type: str
    content: str
    company_name: Optional[str] = None
    role_title: Optional[str] = None
    ats_notes: List[str] = Field(default=[])
    keyword_coverage: Optional[KeywordCoverage] = None
    risk_flags: List[str] = Field(default=[])
    created_at: datetime


class ArtifactsListResponse(BaseModel):
    """List of user artifacts"""

    artifacts: List[ArtifactResponse]
    total_count: int


# ========================================
# CAREER COACH SCHEMAS
# ========================================


class CoachMessage(BaseModel):
    """Single message in coaching conversation"""

    role: str = Field(..., description="user|assistant")
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class CoachRequest(BaseModel):
    """Request to Career Coach"""

    user_id: str
    message: str
    conversation_id: Optional[str] = None
    conversation_type: str = Field(default="general", description="skill_discovery|goal_setting|resume_review|general")


class CoachResponse(BaseModel):
    """Response from Career Coach"""

    conversation_id: str
    reply: str
    profile_patch_suggestions: List[ProfilePatchSuggestion] = Field(default=[])
    goal_updates: List[Dict[str, Any]] = Field(default=[], description="Optional SMART goal refinements")
    next_actions: List[str] = Field(default=[], description="1-3 doable actions (≤15 minutes)")


class CoachConversationResponse(BaseModel):
    """Coach conversation details"""

    id: str
    conversation_title: Optional[str] = None
    conversation_type: str
    messages: List[CoachMessage]
    insights: List[Dict[str, Any]] = Field(default=[])
    status: str
    created_at: datetime
    updated_at: datetime


# ========================================
# CAREER GOALS SCHEMAS
# ========================================


class GoalMilestone(BaseModel):
    """Milestone within a goal"""

    title: str
    completed: bool = False
    completed_at: Optional[datetime] = None


class CareerGoalData(BaseModel):
    """SMART career goal"""

    goal_title: str = Field(..., max_length=500)
    goal_type: str = Field(..., description="skill_acquisition|role_transition|salary_increase|certification")
    description: Optional[str] = None

    # SMART criteria
    specific: Optional[str] = None
    measurable: Optional[str] = None
    achievable: Optional[str] = None
    relevant: Optional[str] = None
    time_bound: Optional[str] = None

    # Progress
    status: str = Field(default="active", description="active|completed|paused|retired")
    progress_percentage: int = Field(default=0, ge=0, le=100)
    milestones: List[GoalMilestone] = Field(default=[])


class CreateGoalRequest(BaseModel):
    """Request to create a new goal"""

    user_id: str
    goal: CareerGoalData


class UpdateGoalRequest(BaseModel):
    """Request to update a goal"""

    goal_id: str
    user_id: str
    updates: Dict[str, Any]


class GoalResponse(BaseModel):
    """Career goal response"""

    id: str
    user_id: str
    goal_data: CareerGoalData
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None


class GoalsListResponse(BaseModel):
    """List of career goals"""

    goals: List[GoalResponse]
    active_count: int
    completed_count: int


# ========================================
# INTERVIEWER AI SCHEMAS
# ========================================


class InterviewQuestion(BaseModel):
    """Single interview question and response"""

    question: str
    user_response: Optional[str] = None
    situation: Optional[str] = None
    task: Optional[str] = None
    action: Optional[str] = None
    result: Optional[str] = None
    timestamp: Optional[datetime] = None


class EvidenceSummary(BaseModel):
    """Evidence extracted from interview"""

    summary: str = Field(..., description="Concise, verifiable statement")
    metric: Optional[str] = None
    confidence: float = Field(..., ge=0, le=1)
    source_question_index: Optional[int] = None


class StartInterviewRequest(BaseModel):
    """Request to start interview session"""

    user_id: str
    role_title: str
    company_name: Optional[str] = None
    job_description: Optional[JobDescriptionInput] = None
    interview_type: str = Field(default="behavioral", description="behavioral|technical|case_study")


class SubmitAnswerRequest(BaseModel):
    """Submit answer to interview question"""

    session_id: str
    user_id: str
    question_index: int
    answer: str


class CompleteInterviewRequest(BaseModel):
    """Request to complete interview and generate suggestions"""

    session_id: str
    user_id: str


class InterviewSessionResponse(BaseModel):
    """Interview session details"""

    session_id: str
    role_title: str
    company_name: Optional[str] = None
    interview_type: str
    questions: List[InterviewQuestion]
    evidence_summaries: List[EvidenceSummary] = Field(default=[])
    generated_suggestions: List[ProfilePatchSuggestion] = Field(default=[])
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None


# ========================================
# SUBSCRIPTION SCHEMAS
# ========================================


class SubscriptionTier(str, Enum):
    """Subscription tier levels"""

    FREE = "free"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class SubscriptionResponse(BaseModel):
    """User subscription details"""

    user_id: str
    tier: SubscriptionTier
    status: str
    started_at: datetime
    expires_at: Optional[datetime] = None


class FeatureAccessResponse(BaseModel):
    """Feature access check response"""

    user_id: str
    tier: SubscriptionTier
    has_access: bool
    feature_name: str
    reason: Optional[str] = None
