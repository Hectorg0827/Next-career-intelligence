"""
SQLAlchemy database models
"""

from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, backref
from datetime import datetime
import uuid

from app.db.database import Base


def generate_uuid():
    """Generate UUID string"""
    return str(uuid.uuid4())


class User(Base):
    """User model"""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    firebase_uid = Column(String(255), unique=True, nullable=False, index=True)
    
    # Profile fields
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    profile_picture_url = Column(Text, nullable=True)
    bio = Column(Text, nullable=True)
    
    # Auth fields
    password_hash = Column(String(255), nullable=True)
    is_email_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # OAuth IDs
    google_id = Column(String(255), nullable=True)
    microsoft_id = Column(String(255), nullable=True)
    github_id = Column(String(255), nullable=True)
    
    # Metadata
    user_metadata = Column("metadata", JSONB, nullable=True)
    
    # Subscription
    role = Column(String(50), default="user", nullable=False)  # 'user', 'elite', 'admin'
    subscription_status = Column(String(50), default="free")  # 'free', 'pro', 'elite'
    subscription_started_at = Column(DateTime, nullable=True)
    subscription_ends_at = Column(DateTime, nullable=True)
    trial_ends_at = Column(DateTime, nullable=True)
    stripe_customer_id = Column(String(255), nullable=True)
    stripe_subscription_id = Column(String(255), nullable=True)
    free_reports_used = Column(Float, default=0)
    last_free_analysis_at = Column(DateTime, nullable=True)
    
    # Timestamps
    account_created_at = Column(DateTime, nullable=True)
    last_login_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    analyses = relationship("Analysis", back_populates="user", cascade="all, delete-orphan")
    # conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")



class Analysis(Base):
    """Career analysis model"""

    __tablename__ = "analyses"

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False, index=True)

    # Input data
    job_title = Column(String(255), nullable=False)
    # skills = Column(JSONB, nullable=False)
    # location = Column(String(255), nullable=False)
    # years_experience = Column(Float, nullable=True)

    # Analysis results
    risk_score = Column(Float, nullable=False)
    risk_level = Column(String(50), nullable=False)
    # compatibility_score = Column(Float, nullable=False)

    # Full analysis JSON
    analysis_data = Column(JSONB, nullable=False)
    # analysis_result = Column(JSONB, nullable=False)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="analyses")


class Conversation(Base):
    """AI Coach conversation model"""

    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False, index=True)

    # Conversation metadata
    title = Column(String(255), nullable=True)  # Auto-generated from first message
    career_context = Column(JSONB, nullable=True)  # User's career context at start

    # Status
    is_active = Column(String(10), default="active")  # active, archived

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_message_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    # user = relationship("User", back_populates="conversations")
    messages = relationship(
        "CoachMessage", back_populates="conversation", cascade="all, delete-orphan", order_by="CoachMessage.created_at"
    )


class CoachMessage(Base):
    """AI Coach message model"""

    __tablename__ = "coach_messages"

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    conversation_id = Column(UUID(as_uuid=False), ForeignKey("conversations.id"), nullable=False, index=True)

    # Message content
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)

    # Metadata
    suggestions = Column(JSONB, nullable=True)  # Quick reply suggestions
    message_metadata = Column(JSONB, nullable=True)  # Additional context

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")


# ============================================================================
# Job Marketplace Models
# ============================================================================


class Job(Base):
    """Job listing model"""

    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    location = Column(String(255), nullable=True)
    remote_policy = Column(String(50), nullable=True)
    employment_type = Column(String(50), nullable=True)
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    salary_currency = Column(String(10), nullable=True)
    required_skills = Column(JSONB, nullable=True)
    required_years_experience = Column(Integer, nullable=True)
    education_level = Column(String(50), nullable=True)
    source = Column(String(50), nullable=True)
    external_url = Column(Text, nullable=True)
    external_id = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    posted_date = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    job_metadata = Column("metadata", JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    apply_url = Column(Text, nullable=True)
    benefits = Column(Text, nullable=True)
    requirements = Column(Text, nullable=True)
    responsibilities = Column(Text, nullable=True)
    seniority = Column(String(50), nullable=True)
    skills_extracted = Column(JSONB, nullable=True)
    location_type = Column(String(50), nullable=True)
    location_city = Column(String(255), nullable=True)
    location_state = Column(String(100), nullable=True)
    location_country = Column(String(100), nullable=True)
    posted_at = Column(DateTime, nullable=True)


class JobApplication(Base):
    """Job application tracking model"""

    __tablename__ = "job_applications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), nullable=False, index=True)  # Firebase UID (String)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(50), default="applied", index=True)  # applied, rejected, interview, offered
    match_score = Column(Float, nullable=True)  # 0-100
    skill_gaps = Column(JSONB, nullable=True)
    recommended_prep = Column(Text, nullable=True)
    interview_date = Column(DateTime, nullable=True)
    interview_notes = Column(Text, nullable=True)
    offer_salary = Column(Float, nullable=True)
    offer_status = Column(String(50), nullable=True)  # 'pending', 'accepted', 'declined'
    rejection_reason = Column(Text, nullable=True)
    applied_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SavedJob(Base):
    """User's saved/bookmarked jobs model"""

    __tablename__ = "saved_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), nullable=False, index=True)  # Firebase UID
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    saved_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)  # User's personal notes


class JobAlertPreferences(Base):
    """User's job alert preferences and search filters"""

    __tablename__ = "job_alert_preferences"

    id = Column(String(50), primary_key=True)
    user_id = Column(String(255), nullable=False, unique=True, index=True)  # Firebase UID
    job_title_keywords = Column(JSON, nullable=True)
    locations = Column(JSON, nullable=True)
    remote_types = Column(JSON, nullable=True)  # 'remote', 'hybrid', 'on_site'
    min_salary = Column(Float, nullable=True)
    max_salary = Column(Float, nullable=True)
    experience_levels = Column(JSON, nullable=True)
    required_skills = Column(JSON, nullable=True)
    excluded_keywords = Column(JSON, nullable=True)
    min_match_score = Column(Float, default=0.5)  # Minimum match % to alert
    email_alerts_enabled = Column(String(10), default="true")
    alert_frequency = Column(String(50), default="daily")  # 'instant', 'daily', 'weekly'
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ============================================================================
# Skill & Education Models (Second Wedge)
# ============================================================================


class Skill(Base):
    """Skill model (Canonical)"""

    __tablename__ = "skills"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True, index=True)
    normalized_name = Column(String(255), index=True)
    category = Column(String(100), nullable=True)
    aliases = Column(JSONB, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class UserSkill(Base):
    """User's skill with proficiency and metadata"""

    __tablename__ = "user_skills"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    skill_id = Column(UUID(as_uuid=True), ForeignKey("skills.id"), nullable=False, index=True)
    
    # Proficiency: 1-10 scale (1=Beginner, 10=Expert)
    proficiency_level = Column(Integer, default=1)
    
    # Metadata
    confidence_score = Column(Float, default=0.0)
    source_tags = Column(JSONB, default=[]) # e.g. ["resume", "manual", "linkedin"]
    evidence_snippets = Column(JSONB, default=[])
    confirmed_by_user = Column(Boolean, default=False)
    hidden = Column(Boolean, default=False)
    
    # New fields for V2
    evidence_source = Column(String(50), nullable=True) # e.g. "RESUME", "MANUAL"
    last_used_year = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_updated_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", backref=backref("user_skills", cascade="all, delete-orphan"))
    skill = relationship("Skill")


class Education(Base):
    """User education history"""

    __tablename__ = "education"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    degree = Column(String(255), nullable=False)
    institution = Column(String(255), nullable=False)
    field_of_study = Column(String(255), nullable=True)
    start_year = Column(Float, nullable=True)
    end_year = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", backref="education")
