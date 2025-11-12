"""Database models for job marketplace"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import ARRAY
from datetime import datetime

from app.db.database import Base


class Job(Base):
    """Job listing model"""

    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    company = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    location = Column(String(255), nullable=True)
    remote_type = Column(String(50), nullable=True)  # 'remote', 'hybrid', 'on_site'
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    salary_currency = Column(String(10), default="USD")
    required_skills = Column(ARRAY(String), nullable=True)
    experience_level = Column(String(50), nullable=True)  # 'entry', 'mid', 'senior'
    job_type = Column(String(50), nullable=True)  # 'full_time', 'part_time', 'contract'
    company_logo_url = Column(String(500), nullable=True)
    job_url = Column(String(500), nullable=True)
    source = Column(String(50), nullable=False, index=True)  # 'github', 'onet', 'manual'
    external_id = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (UniqueConstraint("external_id", "source", name="uq_external_job_id"),)


class JobApplication(Base):
    """Job application tracking model"""

    __tablename__ = "job_applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)  # Firebase UID
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(50), default="applied", index=True)  # applied, rejected, interview, offered
    match_score = Column(Float, nullable=True)  # 0-100
    skill_gaps = Column(ARRAY(String), nullable=True)
    recommended_prep = Column(Text, nullable=True)
    interview_date = Column(DateTime, nullable=True)
    interview_notes = Column(Text, nullable=True)
    offer_salary = Column(Integer, nullable=True)
    offer_status = Column(String(50), nullable=True)  # 'pending', 'accepted', 'declined'
    rejection_reason = Column(Text, nullable=True)
    applied_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (UniqueConstraint("user_id", "job_id", name="uq_user_job_application"),)


class SavedJob(Base):
    """User's saved/bookmarked jobs model"""

    __tablename__ = "saved_jobs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)  # Firebase UID
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    saved_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)  # User's personal notes

    __table_args__ = (UniqueConstraint("user_id", "job_id", name="uq_user_saved_job"),)


class JobAlertPreferences(Base):
    """User's job alert preferences and search filters"""

    __tablename__ = "job_alert_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, unique=True, index=True)  # Firebase UID
    job_title_keywords = Column(ARRAY(String), nullable=True)
    locations = Column(ARRAY(String), nullable=True)
    remote_types = Column(ARRAY(String), nullable=True)  # 'remote', 'hybrid', 'on_site'
    min_salary = Column(Integer, nullable=True)
    max_salary = Column(Integer, nullable=True)
    experience_levels = Column(ARRAY(String), nullable=True)
    required_skills = Column(ARRAY(String), nullable=True)
    excluded_keywords = Column(ARRAY(String), nullable=True)
    min_match_score = Column(Float, default=0.5)  # Minimum match % to alert
    email_alerts_enabled = Column(Boolean, default=True)
    alert_frequency = Column(String(50), default="daily")  # 'instant', 'daily', 'weekly'
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
