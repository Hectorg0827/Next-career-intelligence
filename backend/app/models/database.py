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
    metadata = Column(JSONB, nullable=True)  # Additional context
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
