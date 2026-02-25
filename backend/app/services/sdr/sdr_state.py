"""
SDR Pipeline State
TypedDict state schema that flows through the LangGraph SDR graph.
"""

from typing import TypedDict, List, Optional, Dict, Any
from datetime import datetime


class SDRCriteria(TypedDict):
    """User-configured SDR targeting criteria."""
    target_roles: List[str]          # e.g. ["Senior Software Engineer", "Staff Engineer"]
    salary_min: int                   # Minimum acceptable base salary
    salary_max: int                   # Maximum to cap search at (avoid overqualified rejections)
    locations: List[str]              # e.g. ["Remote", "San Francisco", "New York"]
    company_blacklist: List[str]      # Companies to never apply to
    company_whitelist: List[str]      # If set, only apply to these companies
    quota_weekly: int                 # Max applications per week (user-set, hard capped at 10)
    remote_required: bool             # Only remote roles
    employment_types: List[str]       # ["full_time", "contract"]


class JobCandidate(TypedDict):
    """A job that has passed initial discovery filtering."""
    job_id: str
    title: str
    company: str
    location: str
    salary_min: Optional[int]
    salary_max: Optional[int]
    description: str
    apply_url: str
    source: str
    posted_at: str
    match_reason: str                 # Why this job was selected
    company_research: Optional[Dict[str, Any]]  # Populated by ResearchNode


class SDRApplication(TypedDict):
    """A fully synthesized application ready for user approval."""
    id: str
    job_candidate: JobCandidate
    tailored_resume_id: Optional[str]  # ID of ephemeral resume version in resume studio
    cover_letter: str
    match_rationale: str               # Why this is a strong match for the user
    status: str                        # "pending_approval" | "approved" | "rejected" | "submitted"
    created_at: str


class SDRState(TypedDict):
    """
    Full pipeline state flowing through the LangGraph SDR graph.
    Every node reads and writes to this shared state object.
    """
    # Identity
    user_id: str
    run_id: str
    criteria: SDRCriteria

    # Pipeline stages
    discovered_jobs: List[JobCandidate]         # After DiscoveryNode
    filtered_jobs: List[JobCandidate]            # After FilterNode (quota check)
    researched_jobs: List[JobCandidate]          # After ResearchNode
    synthesized_applications: List[SDRApplication]  # After SynthesisNode

    # Approval gate
    awaiting_approval: List[SDRApplication]
    approved_applications: List[SDRApplication]
    rejected_applications: List[SDRApplication]

    # Logistics
    submitted_applications: List[SDRApplication]

    # Quota tracking
    quota_used_this_week: int
    quota_limit: int

    # Status
    started_at: str
    completed_at: Optional[str]
    error: Optional[str]
    pipeline_stage: str  # Current stage for resumability
