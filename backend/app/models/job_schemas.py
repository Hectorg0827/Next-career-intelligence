"""Pydantic schemas for job marketplace"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ============================================================================
# JOB SCHEMAS
# ============================================================================

class JobBase(BaseModel):
    """Base job schema"""
    title: str
    company: str
    description: Optional[str] = None
    location: Optional[str] = None
    remote_type: Optional[str] = None  # 'remote', 'hybrid', 'on_site'
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: str = "USD"
    required_skills: Optional[List[str]] = None
    experience_level: Optional[str] = None  # 'entry', 'mid', 'senior'
    job_type: Optional[str] = None  # 'full_time', 'part_time', 'contract'
    company_logo_url: Optional[str] = None
    job_url: Optional[str] = None
    source: str  # 'github', 'onet', 'manual'
    external_id: Optional[str] = None
    is_active: bool = True


class JobCreate(JobBase):
    """Schema for creating a job"""
    pass


class JobUpdate(BaseModel):
    """Schema for updating a job"""
    title: Optional[str] = None
    company: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    remote_type: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    required_skills: Optional[List[str]] = None
    experience_level: Optional[str] = None
    job_type: Optional[str] = None
    is_active: Optional[bool] = None


class JobResponse(JobBase):
    """Schema for job response"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class JobWithMatchScore(JobResponse):
    """Job response with AI match score"""
    match_score: Optional[float] = None
    skill_gaps: Optional[List[str]] = None
    recommended_prep: Optional[str] = None


# ============================================================================
# JOB APPLICATION SCHEMAS
# ============================================================================

class JobApplicationBase(BaseModel):
    """Base job application schema"""
    job_id: int
    status: str = "applied"  # applied, rejected, interview, offered
    match_score: Optional[float] = None
    skill_gaps: Optional[List[str]] = None
    recommended_prep: Optional[str] = None


class JobApplicationCreate(BaseModel):
    """Schema for creating a job application"""
    job_id: int


class JobApplicationUpdate(BaseModel):
    """Schema for updating a job application"""
    status: Optional[str] = None
    interview_date: Optional[datetime] = None
    interview_notes: Optional[str] = None
    offer_salary: Optional[int] = None
    offer_status: Optional[str] = None
    rejection_reason: Optional[str] = None


class JobApplicationResponse(BaseModel):
    """Schema for job application response"""
    id: int
    user_id: str
    job_id: int
    status: str
    match_score: Optional[float]
    skill_gaps: Optional[List[str]]
    recommended_prep: Optional[str]
    interview_date: Optional[datetime]
    interview_notes: Optional[str]
    offer_salary: Optional[int]
    offer_status: Optional[str]
    rejection_reason: Optional[str]
    applied_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class JobApplicationWithDetails(JobApplicationResponse):
    """Job application with full job details"""
    job: Optional[JobResponse] = None


# ============================================================================
# SAVED JOB SCHEMAS
# ============================================================================

class SavedJobBase(BaseModel):
    """Base saved job schema"""
    job_id: int
    notes: Optional[str] = None


class SavedJobCreate(BaseModel):
    """Schema for saving a job"""
    job_id: int
    notes: Optional[str] = None


class SavedJobResponse(BaseModel):
    """Schema for saved job response"""
    id: int
    user_id: str
    job_id: int
    saved_at: datetime
    notes: Optional[str]

    class Config:
        from_attributes = True


class SavedJobWithDetails(SavedJobResponse):
    """Saved job with full job details"""
    job: Optional[JobResponse] = None


# ============================================================================
# JOB ALERT PREFERENCES SCHEMAS
# ============================================================================

class JobAlertPreferencesBase(BaseModel):
    """Base job alert preferences schema"""
    job_title_keywords: Optional[List[str]] = None
    locations: Optional[List[str]] = None
    remote_types: Optional[List[str]] = None
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    experience_levels: Optional[List[str]] = None
    required_skills: Optional[List[str]] = None
    excluded_keywords: Optional[List[str]] = None
    min_match_score: Optional[float] = 0.5
    email_alerts_enabled: bool = True
    alert_frequency: str = "daily"  # 'instant', 'daily', 'weekly'


class JobAlertPreferencesCreate(JobAlertPreferencesBase):
    """Schema for creating alert preferences"""
    pass


class JobAlertPreferencesUpdate(BaseModel):
    """Schema for updating alert preferences"""
    job_title_keywords: Optional[List[str]] = None
    locations: Optional[List[str]] = None
    remote_types: Optional[List[str]] = None
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    experience_levels: Optional[List[str]] = None
    required_skills: Optional[List[str]] = None
    excluded_keywords: Optional[List[str]] = None
    min_match_score: Optional[float] = None
    email_alerts_enabled: Optional[bool] = None
    alert_frequency: Optional[str] = None


class JobAlertPreferencesResponse(JobAlertPreferencesBase):
    """Schema for alert preferences response"""
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# SEARCH & FILTER SCHEMAS
# ============================================================================

class JobSearchFilters(BaseModel):
    """Job search and filter parameters"""
    query: Optional[str] = None
    location: Optional[str] = None
    remote_type: Optional[str] = None
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    experience_level: Optional[str] = None
    required_skills: Optional[List[str]] = None
    job_type: Optional[str] = None
    source: Optional[str] = None
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)
    sort_by: Optional[str] = None  # 'recent', 'salary', 'relevance'


class JobSearchResponse(BaseModel):
    """Job search results response"""
    total: int
    page: int
    limit: int
    results: List[JobWithMatchScore]


# ============================================================================
# DASHBOARD SCHEMAS
# ============================================================================

class ApplicationStats(BaseModel):
    """User application statistics"""
    total_applications: int
    applied: int
    interviewing: int
    offered: int
    rejected: int
    average_match_score: Optional[float]


class JobMarketplaceStats(BaseModel):
    """Overall job marketplace statistics"""
    total_jobs: int
    total_applications: int
    active_users: int
    average_match_score: Optional[float]
