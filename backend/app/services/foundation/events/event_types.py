"""
Event Types - Comprehensive event definitions for Career OS

This module defines all event types that can occur in the system.
Events are the foundation for:
- User journey tracking
- AI learning
- Cross-service communication
- Analytics
"""

from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID


class EventCategory(str, Enum):
    """High-level event categories"""
    USER_ACTION = "user_action"
    PROFILE = "profile"
    AI_INTERACTION = "ai_interaction"
    SYSTEM = "system"
    JOB = "job"
    GOAL = "goal"
    SKILL = "skill"


class UserActionEventType(str, Enum):
    """User-initiated actions"""
    # Navigation
    PAGE_VIEWED = "page_viewed"
    FEATURE_ACCESSED = "feature_accessed"
    
    # Search & Discovery
    SEARCH_PERFORMED = "search_performed"
    FILTER_APPLIED = "filter_applied"
    FILTER_REMOVED = "filter_removed"
    
    # Job Actions
    JOB_VIEWED = "job_viewed"
    JOB_SAVED = "job_saved"
    JOB_UNSAVED = "job_unsaved"
    JOB_APPLIED = "job_applied"
    JOB_REJECTED = "job_rejected"
    JOB_SHARED = "job_shared"
    
    # Settings
    PREFERENCES_UPDATED = "preferences_updated"
    NOTIFICATION_SETTINGS_CHANGED = "notification_settings_changed"


class ProfileEventType(str, Enum):
    """Profile-related events"""
    PROFILE_CREATED = "profile_created"
    PROFILE_UPDATED = "profile_updated"
    PROFILE_COMPLETED = "profile_completed"
    
    WORK_HISTORY_ADDED = "work_history_added"
    WORK_HISTORY_UPDATED = "work_history_updated"
    WORK_HISTORY_REMOVED = "work_history_removed"
    
    EDUCATION_ADDED = "education_added"
    EDUCATION_UPDATED = "education_updated"
    
    SKILL_ADDED = "skill_added"
    SKILL_REMOVED = "skill_removed"
    SKILL_ENDORSED = "skill_endorsed"
    
    RESUME_UPLOADED = "resume_uploaded"
    RESUME_GENERATED = "resume_generated"
    
    CERTIFICATION_ADDED = "certification_added"
    ACHIEVEMENT_ADDED = "achievement_added"


class AIInteractionEventType(str, Enum):
    """AI-related interactions"""
    # Analysis
    ANALYSIS_REQUESTED = "analysis_requested"
    ANALYSIS_COMPLETED = "analysis_completed"
    RISK_ASSESSMENT_GENERATED = "risk_assessment_generated"
    
    # Roadmap
    ROADMAP_REQUESTED = "roadmap_requested"
    ROADMAP_GENERATED = "roadmap_generated"
    
    # Coach
    COACH_MESSAGE_SENT = "coach_message_sent"
    COACH_MESSAGE_RECEIVED = "coach_message_received"
    COACH_CONVERSATION_STARTED = "coach_conversation_started"
    COACH_CONVERSATION_ENDED = "coach_conversation_ended"
    
    # Interviewer
    INTERVIEW_SESSION_STARTED = "interview_session_started"
    INTERVIEW_QUESTION_ANSWERED = "interview_question_answered"
    INTERVIEW_SESSION_COMPLETED = "interview_session_completed"
    
    # Suggestions
    AI_SUGGESTION_GENERATED = "ai_suggestion_generated"
    AI_SUGGESTION_ACCEPTED = "ai_suggestion_accepted"
    AI_SUGGESTION_REJECTED = "ai_suggestion_rejected"


class SystemEventType(str, Enum):
    """System-generated events"""
    RECOMMENDATION_GENERATED = "recommendation_generated"
    NOTIFICATION_SENT = "notification_sent"
    EMAIL_SENT = "email_sent"
    
    BACKGROUND_JOB_STARTED = "background_job_started"
    BACKGROUND_JOB_COMPLETED = "background_job_completed"
    BACKGROUND_JOB_FAILED = "background_job_failed"
    
    DATA_EXPORT_REQUESTED = "data_export_requested"
    DATA_EXPORT_COMPLETED = "data_export_completed"


class GoalEventType(str, Enum):
    """Goal-related events"""
    GOAL_CREATED = "goal_created"
    GOAL_UPDATED = "goal_updated"
    GOAL_COMPLETED = "goal_completed"
    GOAL_PAUSED = "goal_paused"
    GOAL_DELETED = "goal_deleted"
    
    MILESTONE_ADDED = "milestone_added"
    MILESTONE_COMPLETED = "milestone_completed"
    
    PROGRESS_UPDATED = "progress_updated"


# ========================================
# Event Base Classes
# ========================================

class BaseEvent(BaseModel):
    """Base event model - all events inherit from this"""
    event_id: str = Field(default_factory=lambda: str(UUID))
    user_id: str
    event_type: str
    event_category: EventCategory
    
    # Context
    session_id: Optional[str] = None
    source: Optional[str] = None  # dashboard, job_search, coach, etc.
    
    # Metadata
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    
    # Timestamp
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Event-specific data
    event_data: Dict[str, Any] = Field(default_factory=dict)


# ========================================
# User Action Events
# ========================================

class JobViewedEvent(BaseEvent):
    """User viewed a job"""
    event_type: UserActionEventType = UserActionEventType.JOB_VIEWED
    event_category: EventCategory = EventCategory.USER_ACTION
    
    job_id: str
    job_title: str
    company_name: Optional[str] = None
    view_duration_seconds: Optional[int] = None


class JobSavedEvent(BaseEvent):
    """User saved a job for later"""
    event_type: UserActionEventType = UserActionEventType.JOB_SAVED
    event_category: EventCategory = EventCategory.USER_ACTION
    
    job_id: str
    job_title: str
    reason: Optional[str] = None  # Why they saved it


class JobAppliedEvent(BaseEvent):
    """User applied to a job"""
    event_type: UserActionEventType = UserActionEventType.JOB_APPLIED
    event_category: EventCategory = EventCategory.USER_ACTION
    
    job_id: str
    job_title: str
    company_name: str
    application_method: str  # internal, external, through_platform
    resume_used: Optional[str] = None  # Resume artifact ID


class JobRejectedEvent(BaseEvent):
    """User explicitly rejected a recommendation"""
    event_type: UserActionEventType = UserActionEventType.JOB_REJECTED
    event_category: EventCategory = EventCategory.USER_ACTION
    
    job_id: str
    job_title: str
    rejection_reason: str  # salary_too_low, location, no_remote, etc.
    rejection_note: Optional[str] = None


class SearchPerformedEvent(BaseEvent):
    """User performed a search"""
    event_type: UserActionEventType = UserActionEventType.SEARCH_PERFORMED
    event_category: EventCategory = EventCategory.USER_ACTION
    
    search_query: str
    filters_applied: Dict[str, Any] = Field(default_factory=dict)
    results_count: int
    clicked_position: Optional[int] = None  # Which result they clicked


# ========================================
# Profile Events
# ========================================

class ProfileUpdatedEvent(BaseEvent):
    """Profile was updated"""
    event_type: ProfileEventType = ProfileEventType.PROFILE_UPDATED
    event_category: EventCategory = EventCategory.PROFILE
    
    fields_changed: List[str]
    old_values: Dict[str, Any] = Field(default_factory=dict)
    new_values: Dict[str, Any] = Field(default_factory=dict)
    change_source: str  # manual, ai_suggestion, import


class SkillAddedEvent(BaseEvent):
    """Skill added to profile"""
    event_type: ProfileEventType = ProfileEventType.SKILL_ADDED
    event_category: EventCategory = EventCategory.PROFILE
    
    skill_name: str
    skill_category: str  # hard, soft, domain
    proficiency: Optional[int] = None
    source: str  # manual, resume_import, ai_detected


class WorkHistoryAddedEvent(BaseEvent):
    """Work history entry added"""
    event_type: ProfileEventType = ProfileEventType.WORK_HISTORY_ADDED
    event_category: EventCategory = EventCategory.PROFILE
    
    role: str
    company: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: bool = False


# ========================================
# AI Interaction Events
# ========================================

class CoachMessageSentEvent(BaseEvent):
    """User sent message to coach"""
    event_type: AIInteractionEventType = AIInteractionEventType.COACH_MESSAGE_SENT
    event_category: EventCategory = EventCategory.AI_INTERACTION
    
    conversation_id: str
    message_content: str
    message_length: int
    conversation_turn: int  # Which turn in conversation


class CoachMessageReceivedEvent(BaseEvent):
    """Coach response received"""
    event_type: AIInteractionEventType = AIInteractionEventType.COACH_MESSAGE_RECEIVED
    event_category: EventCategory = EventCategory.AI_INTERACTION
    
    conversation_id: str
    response_content: str
    suggestions_generated: List[str] = Field(default_factory=list)
    response_time_ms: int


class AnalysisRequestedEvent(BaseEvent):
    """User requested job analysis"""
    event_type: AIInteractionEventType = AIInteractionEventType.ANALYSIS_REQUESTED
    event_category: EventCategory = EventCategory.AI_INTERACTION
    
    job_title: str
    additional_context: Optional[Dict[str, Any]] = None


class AnalysisCompletedEvent(BaseEvent):
    """Analysis completed"""
    event_type: AIInteractionEventType = AIInteractionEventType.ANALYSIS_COMPLETED
    event_category: EventCategory = EventCategory.AI_INTERACTION
    
    analysis_id: str
    risk_score: float
    compatibility_score: float
    processing_time_ms: int


# ========================================
# Goal Events
# ========================================

class GoalCreatedEvent(BaseEvent):
    """User created a goal"""
    event_type: GoalEventType = GoalEventType.GOAL_CREATED
    event_category: EventCategory = EventCategory.GOAL
    
    goal_id: str
    goal_title: str
    goal_type: str  # skill_acquisition, role_transition, etc.
    target_date: Optional[str] = None
    creation_source: str  # manual, coach_suggested


class GoalCompletedEvent(BaseEvent):
    """Goal was completed"""
    event_type: GoalEventType = GoalEventType.GOAL_COMPLETED
    event_category: EventCategory = EventCategory.GOAL
    
    goal_id: str
    goal_title: str
    days_to_complete: int
    completion_method: str  # manual, auto_detected


# ========================================
# System Events
# ========================================

class RecommendationGeneratedEvent(BaseEvent):
    """System generated recommendations"""
    event_type: SystemEventType = SystemEventType.RECOMMENDATION_GENERATED
    event_category: EventCategory = EventCategory.SYSTEM
    
    recommendation_type: str  # job, skill, goal, etc.
    recommendations_count: int
    algorithm_version: str
    confidence_score: float


# ========================================
# Event Factory
# ========================================

class EventFactory:
    """Factory to create properly typed events"""
    
    @staticmethod
    def create_event(event_type: str, **kwargs) -> BaseEvent:
        """Create an event based on type"""
        event_map = {
            UserActionEventType.JOB_VIEWED: JobViewedEvent,
            UserActionEventType.JOB_SAVED: JobSavedEvent,
            UserActionEventType.JOB_APPLIED: JobAppliedEvent,
            UserActionEventType.JOB_REJECTED: JobRejectedEvent,
            UserActionEventType.SEARCH_PERFORMED: SearchPerformedEvent,
            
            ProfileEventType.PROFILE_UPDATED: ProfileUpdatedEvent,
            ProfileEventType.SKILL_ADDED: SkillAddedEvent,
            ProfileEventType.WORK_HISTORY_ADDED: WorkHistoryAddedEvent,
            
            AIInteractionEventType.COACH_MESSAGE_SENT: CoachMessageSentEvent,
            AIInteractionEventType.COACH_MESSAGE_RECEIVED: CoachMessageReceivedEvent,
            AIInteractionEventType.ANALYSIS_REQUESTED: AnalysisRequestedEvent,
            AIInteractionEventType.ANALYSIS_COMPLETED: AnalysisCompletedEvent,
            
            GoalEventType.GOAL_CREATED: GoalCreatedEvent,
            GoalEventType.GOAL_COMPLETED: GoalCompletedEvent,
            
            SystemEventType.RECOMMENDATION_GENERATED: RecommendationGeneratedEvent,
        }
        
        event_class = event_map.get(event_type, BaseEvent)
        return event_class(**kwargs)
