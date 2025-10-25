"""
SQLAlchemy database models
"""

from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
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
    name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    analyses = relationship("Analysis", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")


class Analysis(Base):
    """Career analysis model"""
    __tablename__ = "analyses"
    
    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False, index=True)
    
    # Input data
    job_title = Column(String(255), nullable=False)
    skills = Column(JSONB, nullable=False)
    location = Column(String(255), nullable=False)
    years_experience = Column(Float, nullable=True)
    
    # Analysis results
    risk_score = Column(Float, nullable=False)
    risk_level = Column(String(50), nullable=False)
    compatibility_score = Column(Float, nullable=False)
    
    # Full analysis JSON
    analysis_result = Column(JSONB, nullable=False)
    
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
    user = relationship("User", back_populates="conversations")
    messages = relationship("CoachMessage", back_populates="conversation", cascade="all, delete-orphan", order_by="CoachMessage.created_at")


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

    id = Column(String(50), primary_key=True)
    title = Column(String(255), nullable=False, index=True)
    company = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    location = Column(String(255), nullable=True)
    remote_type = Column(String(50), nullable=True)  # 'remote', 'hybrid', 'on_site'
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    salary_currency = Column(String(10), default="USD")
    required_skills = Column(JSON, nullable=True)
    experience_level = Column(String(50), nullable=True)  # 'entry', 'mid', 'senior'
    job_type = Column(String(50), nullable=True)  # 'full_time', 'part_time', 'contract'
    company_logo_url = Column(String(500), nullable=True)
    job_url = Column(String(500), nullable=True)
    source = Column(String(50), nullable=False, index=True)  # 'github', 'onet', 'manual'
    external_id = Column(String(255), nullable=True)
    is_active = Column(String(10), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class JobApplication(Base):
    """Job application tracking model"""
    __tablename__ = "job_applications"

    id = Column(String(50), primary_key=True)
    user_id = Column(String(255), nullable=False, index=True)  # Firebase UID
    job_id = Column(String(50), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(50), default="applied", index=True)  # applied, rejected, interview, offered
    match_score = Column(Float, nullable=True)  # 0-100
    skill_gaps = Column(JSON, nullable=True)
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

    id = Column(String(50), primary_key=True)
    user_id = Column(String(255), nullable=False, index=True)  # Firebase UID
    job_id = Column(String(50), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
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
