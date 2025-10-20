"""
Database Models for Resume Studio
Career Profiles, Artifacts, and Suggestions with Privacy Compliance
"""

from sqlalchemy import Column, String, JSON, DateTime, Boolean, Text, ForeignKey, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.db.database import Base


def generate_uuid():
    """Generate UUID for primary keys"""
    return str(uuid.uuid4())


class CareerProfile(Base):
    """
    Single Source of Truth for user's career information
    Stores structured career data with provenance tracking
    """
    __tablename__ = "career_profiles"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, unique=True, nullable=False, index=True)
    
    # Structured career data (JSON following CareerProfile schema)
    profile_data = Column(JSON, nullable=False)
    
    # Privacy & compliance
    privacy_consent = Column(JSON, default=lambda: {
        "store_profile": False,
        "ai_processing": False,
        "data_retention": False
    })
    privacy_region = Column(String, default="US")  # GDPR, CCPA, etc.
    
    # Versioning & audit
    version = Column(String, default="1.0.0")
    data_hash = Column(String, nullable=True)  # SHA-256 hash for integrity
    sources = Column(JSON, default=list)  # ["resume_upload", "linkedin_paste", etc.]
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_verified_at = Column(DateTime, nullable=True)
    
    # Auto-deletion for GDPR compliance
    auto_delete_at = Column(DateTime, nullable=True)
    
    # Relationships
    artifacts = relationship("Artifact", back_populates="profile", cascade="all, delete-orphan")
    suggestions = relationship("ProfileSuggestion", back_populates="profile", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="profile", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<CareerProfile(user_id={self.user_id}, version={self.version})>"


class Artifact(Base):
    """
    Generated career documents (tailored resumes, cover letters)
    Linked to profile snapshots for reproducibility
    """
    __tablename__ = "artifacts"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, nullable=False, index=True)
    profile_id = Column(String, ForeignKey("career_profiles.id"), nullable=False)
    
    # Artifact details
    kind = Column(String, nullable=False)  # "tailored_resume", "cover_letter", "linkedin_summary"
    content = Column(Text, nullable=False)  # Markdown or plain text
    format = Column(String, default="markdown")  # "markdown", "json", "pdf"
    
    # Context that generated this artifact
    metadata = Column(JSON, default=dict)  # Job description, generation params, AI model used
    
    # Profile snapshot for reproducibility
    profile_snapshot_id = Column(String, nullable=True)  # Links to career_profiles.id at generation time
    profile_snapshot_hash = Column(String, nullable=True)  # Hash of profile at generation time
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)  # For temporary artifacts
    
    # Relationship
    profile = relationship("CareerProfile", back_populates="artifacts")
    
    def __repr__(self):
        return f"<Artifact(user_id={self.user_id}, kind={self.kind})>"


class ProfileSuggestion(Base):
    """
    Suggestions from Coach/Interviewer AI agents
    Require explicit user approval before application
    """
    __tablename__ = "profile_suggestions"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, nullable=False, index=True)
    profile_id = Column(String, ForeignKey("career_profiles.id"), nullable=False)
    
    # Suggestion details
    source = Column(String, nullable=False)  # "career_coach", "interviewer", "skill_analyzer"
    suggestion_type = Column(String, nullable=False)  # "skill_add", "bullet_improve", "certification_suggest"
    suggestion_patch = Column(JSON, nullable=False)  # The proposed change
    
    # AI reasoning
    reasoning = Column(Text, nullable=True)  # Why this suggestion was made
    confidence = Column(String, default="medium")  # "low", "medium", "high"
    evidence = Column(JSON, default=list)  # Supporting evidence for the suggestion
    
    # User action
    status = Column(String, default="pending")  # "pending", "accepted", "rejected", "expired"
    user_feedback = Column(Text, nullable=True)  # User's comment on rejection
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    applied_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)  # Suggestions expire after 30 days
    
    # Relationship
    profile = relationship("CareerProfile", back_populates="suggestions")
    
    def __repr__(self):
        return f"<ProfileSuggestion(source={self.source}, status={self.status})>"


class AuditLog(Base):
    """
    Comprehensive audit trail for privacy compliance
    Tracks all profile modifications and access
    """
    __tablename__ = "audit_logs"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    profile_id = Column(String, ForeignKey("career_profiles.id"), nullable=False)
    user_id = Column(String, nullable=False, index=True)
    
    # Action details
    action = Column(String, nullable=False)  # "create", "update", "delete", "access", "export", "erase"
    resource = Column(String, nullable=False)  # "career_profile", "artifact", "suggestion"
    resource_id = Column(String, nullable=True)
    
    # Change tracking
    changes = Column(JSON, nullable=True)  # What was changed (field-level tracking)
    before_hash = Column(String, nullable=True)  # Hash before change
    after_hash = Column(String, nullable=True)  # Hash after change
    
    # Context
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    session_id = Column(String, nullable=True)
    
    # Audit metadata
    audit_note = Column(Text, nullable=True)  # Human-readable description
    automated = Column(Boolean, default=False)  # Was this an automated action?
    
    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationship
    profile = relationship("CareerProfile", back_populates="audit_logs")
    
    def __repr__(self):
        return f"<AuditLog(user_id={self.user_id}, action={self.action}, timestamp={self.timestamp})>"


class ConsentRecord(Base):
    """
    Privacy consent tracking for GDPR/CCPA compliance
    Immutable record of user consent changes
    """
    __tablename__ = "consent_records"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, nullable=False, index=True)
    
    # Consent details
    consent_type = Column(String, nullable=False)  # "store_profile", "ai_processing", "data_retention"
    granted = Column(Boolean, nullable=False)
    
    # Regional compliance
    privacy_region = Column(String, nullable=False)  # "EU", "US", "CA", etc.
    legal_basis = Column(String, nullable=True)  # "explicit_consent", "legitimate_interest"
    
    # Context
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    
    # Timestamps (immutable - no updates allowed)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<ConsentRecord(user_id={self.user_id}, type={self.consent_type}, granted={self.granted})>"


class DataErasureRequest(Base):
    """
    GDPR Article 17 - Right to Erasure tracking
    Ensures complete data deletion
    """
    __tablename__ = "data_erasure_requests"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, nullable=False, index=True)
    
    # Request details
    status = Column(String, default="pending")  # "pending", "processing", "completed", "failed"
    reason = Column(String, nullable=True)  # User's reason for erasure
    
    # What will be deleted
    resources_to_delete = Column(JSON, default=list)  # ["career_profile", "artifacts", "suggestions"]
    
    # Processing
    initiated_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    verified_at = Column(DateTime, nullable=True)  # When deletion was verified
    
    # Compliance
    privacy_region = Column(String, nullable=False)
    legal_deadline = Column(DateTime, nullable=True)  # Must complete by this date (30 days for GDPR)
    
    # Audit trail
    deletion_log = Column(JSON, default=list)  # Step-by-step deletion record
    
    def __repr__(self):
        return f"<DataErasureRequest(user_id={self.user_id}, status={self.status})>"
