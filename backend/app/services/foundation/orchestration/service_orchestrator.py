"""
Service Orchestrator - Coordinate Cross-Feature Workflows

This module orchestrates complex workflows that span multiple services:
- Job view → Generate analysis → Update recommendations
- Profile update → Recalculate fit scores → Notify user
- Goal completion → Award milestone → Update analytics

Transforms isolated features into integrated Career OS.
"""

from typing import Optional, Dict, Any, List, Callable, Awaitable
from datetime import datetime
import asyncio

from ..events.event_bus import event_bus, EventSubscriber
from ..events.event_store import event_store
from ..events.event_types import EventFactory, EventCategory
from ..profile.unified_profile import unified_profile_manager
from ..journey.tracker import session_manager


class WorkflowOrchestrator:
    """
    Orchestrate multi-service workflows
    
    Workflows are triggered by events and coordinate actions across services.
    Example: When user views a job, trigger AI analysis, update recommendations,
    and track in journey analytics.
    """
    
    def __init__(self):
        self.subscriber = EventSubscriber(event_bus)
        self.workflows: Dict[str, Callable] = {}
        self._register_workflows()
    
    def _register_workflows(self):
        """Register all workflow handlers"""
        
        # User action workflows
        self.subscriber.on("USER_ACTION")(self._handle_user_action)
        
        # Profile workflows
        self.subscriber.on("PROFILE")(self._handle_profile_event)
        
        # AI interaction workflows
        self.subscriber.on("AI_INTERACTION")(self._handle_ai_interaction)
        
        # Job workflows
        self.subscriber.on("JOB")(self._handle_job_event)
        
        # Goal workflows
        self.subscriber.on("GOAL")(self._handle_goal_event)
    
    async def _handle_user_action(self, event: Dict[str, Any]):
        """
        Handle user action events
        
        User actions often trigger downstream processing:
        - Search performed → Update preferences
        - Filter applied → Learn user intent
        - Feature used → Update engagement metrics
        """
        event_type = event["event_type"]
        user_id = event["user_id"]
        session_id = event["session_id"]
        event_data = event["event_data"]
        
        print(f"[Orchestrator] User action: {event_type} by {user_id}")
        
        # Update session activity
        if session_id:
            await session_manager.update_session_activity(
                session_id=session_id,
                feature_used=event.get("source")
            )
        
        # Workflow: Search performed
        if event_type == "search_performed":
            await self._workflow_search_performed(user_id, event_data)
        
        # Workflow: Page viewed
        elif event_type == "page_viewed":
            await self._workflow_page_viewed(user_id, session_id, event_data)
    
    async def _handle_profile_event(self, event: Dict[str, Any]):
        """
        Handle profile events
        
        Profile changes trigger:
        - Recalculate job fit scores
        - Update recommendations
        - Notify relevant services
        """
        event_type = event["event_type"]
        user_id = event["user_id"]
        event_data = event["event_data"]
        
        print(f"[Orchestrator] Profile event: {event_type} for {user_id}")
        
        # Workflow: Profile updated
        if event_type == "profile_updated":
            await self._workflow_profile_updated(user_id, event_data)
        
        # Workflow: Profile created
        elif event_type == "profile_created":
            await self._workflow_profile_created(user_id, event_data)
    
    async def _handle_ai_interaction(self, event: Dict[str, Any]):
        """
        Handle AI interaction events
        
        AI interactions provide learning signals:
        - Coach conversations → Understand user needs
        - Analysis requests → Track feature usage
        - Feedback provided → Improve AI
        """
        event_type = event["event_type"]
        user_id = event["user_id"]
        event_data = event["event_data"]
        
        print(f"[Orchestrator] AI interaction: {event_type} by {user_id}")
        
        # Workflow: Coach message sent
        if event_type == "coach_message_sent":
            await self._workflow_coach_interaction(user_id, event_data)
    
    async def _handle_job_event(self, event: Dict[str, Any]):
        """
        Handle job-related events
        
        Job events trigger:
        - Update recommendations based on views
        - Track application funnel
        - Generate insights
        """
        event_type = event["event_type"]
        user_id = event["user_id"]
        event_data = event["event_data"]
        
        print(f"[Orchestrator] Job event: {event_type} by {user_id}")
        
        # Workflow: Job viewed
        if event_type == "job_viewed":
            await self._workflow_job_viewed(user_id, event_data)
        
        # Workflow: Job applied
        elif event_type == "job_applied":
            await self._workflow_job_applied(user_id, event_data)
    
    async def _handle_goal_event(self, event: Dict[str, Any]):
        """
        Handle goal events
        
        Goal events trigger:
        - Award milestones
        - Update progress tracking
        - Generate recommendations
        """
        event_type = event["event_type"]
        user_id = event["user_id"]
        event_data = event["event_data"]
        
        print(f"[Orchestrator] Goal event: {event_type} for {user_id}")
        
        # Workflow: Goal completed
        if event_type == "goal_completed":
            await self._workflow_goal_completed(user_id, event_data)
    
    # ========================================
    # Workflow Implementations
    # ========================================
    
    async def _workflow_search_performed(
        self,
        user_id: str,
        event_data: Dict[str, Any]
    ):
        """
        Workflow: User performed a search
        
        Actions:
        1. Update user preferences based on search query
        2. Log search for analytics
        3. Update recommendation engine
        """
        search_query = event_data.get("search_query", "")
        filters = event_data.get("filters_applied", {})
        results_count = event_data.get("results_count", 0)
        
        print(f"  → Search workflow: '{search_query}' ({results_count} results)")
        
        # TODO: Update user preferences
        # TODO: Update recommendation engine
        # TODO: Log for analytics
    
    async def _workflow_page_viewed(
        self,
        user_id: str,
        session_id: Optional[str],
        event_data: Dict[str, Any]
    ):
        """
        Workflow: User viewed a page
        
        Actions:
        1. Update session with page visit
        2. Track feature engagement
        """
        page_url = event_data.get("page_url", "")
        
        if session_id:
            await session_manager.update_session_activity(
                session_id=session_id,
                page_visited=page_url
            )
    
    async def _workflow_profile_updated(
        self,
        user_id: str,
        event_data: Dict[str, Any]
    ):
        """
        Workflow: User updated their profile
        
        Actions:
        1. Recalculate profile completeness
        2. Update job fit scores for saved jobs
        3. Generate new recommendations
        4. Emit profile_analysis_updated event
        """
        fields_changed = event_data.get("fields_changed", [])
        
        print(f"  → Profile update workflow: {fields_changed}")
        
        # Get updated profile
        profile = await unified_profile_manager.get_unified_profile(user_id)
        
        # Check if significant fields changed (skills, experience, etc.)
        significant_fields = ["skills", "work_history", "education", "professional_summary"]
        significant_change = any(field in significant_fields for field in fields_changed)
        
        if significant_change:
            # Emit event for recommendation engine to update
            recommendation_event = EventFactory.create_event(
                "profile_analysis_updated",
                user_id=user_id,
                source="orchestrator",
                profile_completeness=profile["completeness"]["overall_score"],
                fields_changed=fields_changed
            )
            await event_bus.publish(recommendation_event, category="SYSTEM")
            
            print(f"  → Triggered recommendation update")
    
    async def _workflow_profile_created(
        self,
        user_id: str,
        event_data: Dict[str, Any]
    ):
        """
        Workflow: User created their first profile
        
        Actions:
        1. Award onboarding milestone
        2. Initialize recommendations
        3. Send welcome guidance
        """
        profile_id = event_data.get("profile_id")
        
        print(f"  → Profile creation workflow")
        
        # Award milestone
        milestone_event = EventFactory.create_event(
            "milestone_achieved",
            user_id=user_id,
            source="orchestrator",
            milestone_type="profile_created",
            title="Profile Created",
            description="Created your first Career Profile"
        )
        await event_bus.publish(milestone_event, category="SYSTEM")
        
        print(f"  → Awarded 'Profile Created' milestone")
    
    async def _workflow_coach_interaction(
        self,
        user_id: str,
        event_data: Dict[str, Any]
    ):
        """
        Workflow: User interacted with Career Coach
        
        Actions:
        1. Update coach conversation context
        2. Track topics discussed
        3. Generate follow-up recommendations
        """
        conversation_id = event_data.get("conversation_id")
        message_content = event_data.get("message_content", "")
        
        print(f"  → Coach interaction workflow")
        
        # TODO: Analyze conversation topics
        # TODO: Update user context with discussed topics
        # TODO: Generate follow-up actions
    
    async def _workflow_job_viewed(
        self,
        user_id: str,
        event_data: Dict[str, Any]
    ):
        """
        Workflow: User viewed a job
        
        Actions:
        1. Track job in user profile
        2. Update recommendation engine
        3. Generate job analysis (if premium)
        """
        job_id = event_data.get("job_id")
        job_title = event_data.get("job_title", "Unknown")
        view_duration = event_data.get("view_duration_seconds", 0)
        
        print(f"  → Job view workflow: {job_title} ({view_duration}s)")
        
        # Significant view = user spent time reading
        significant_view = view_duration > 10
        
        if significant_view:
            # Emit event for recommendation engine
            interest_event = EventFactory.create_event(
                "job_interest_signal",
                user_id=user_id,
                source="orchestrator",
                job_id=job_id,
                job_title=job_title,
                interest_level="high",
                view_duration_seconds=view_duration
            )
            await event_bus.publish(interest_event, category="SYSTEM")
            
            print(f"  → Registered high interest signal")
    
    async def _workflow_job_applied(
        self,
        user_id: str,
        event_data: Dict[str, Any]
    ):
        """
        Workflow: User applied to a job
        
        Actions:
        1. Track in user profile
        2. Award milestone (if first application)
        3. Update analytics
        4. Generate follow-up guidance
        """
        job_id = event_data.get("job_id")
        job_title = event_data.get("job_title", "Unknown")
        
        print(f"  → Job application workflow: {job_title}")
        
        # Check if first application
        events = await event_store.get_events_by_user(
            user_id=user_id,
            limit=10000
        )
        
        application_events = [e for e in events if e["event_type"] == "job_applied"]
        
        if len(application_events) == 1:
            # First application! Award milestone
            milestone_event = EventFactory.create_event(
                "milestone_achieved",
                user_id=user_id,
                source="orchestrator",
                milestone_type="first_application",
                title="First Application",
                description="Submitted your first job application"
            )
            await event_bus.publish(milestone_event, category="SYSTEM")
            
            print(f"  → Awarded 'First Application' milestone")
    
    async def _workflow_goal_completed(
        self,
        user_id: str,
        event_data: Dict[str, Any]
    ):
        """
        Workflow: User completed a goal
        
        Actions:
        1. Award milestone
        2. Update progress tracking
        3. Generate next goal recommendations
        """
        goal_id = event_data.get("goal_id")
        goal_title = event_data.get("goal_title", "Unknown")
        
        print(f"  → Goal completion workflow: {goal_title}")
        
        # Award milestone
        milestone_event = EventFactory.create_event(
            "milestone_achieved",
            user_id=user_id,
            source="orchestrator",
            milestone_type="goal_completed",
            title=f"Completed: {goal_title}",
            description=f"Successfully completed goal: {goal_title}"
        )
        await event_bus.publish(milestone_event, category="SYSTEM")
        
        print(f"  → Awarded goal completion milestone")
    
    # ========================================
    # Service Control
    # ========================================
    
    async def start(self, service_name: str = "orchestrator", instance_id: str = "main"):
        """
        Start orchestrator service
        
        Args:
            service_name: Name of this service
            instance_id: Unique instance identifier
        """
        print(f"[Orchestrator] Starting service: {service_name}/{instance_id}")
        
        await event_bus.connect()
        await self.subscriber.start(service_name, instance_id)
    
    async def stop(self):
        """Stop orchestrator service"""
        print(f"[Orchestrator] Stopping service")
        await self.subscriber.stop()
        await event_bus.disconnect()


# ========================================
# Standalone Workflow Functions
# ========================================

async def trigger_job_recommendation_update(user_id: str):
    """
    Manually trigger job recommendation update
    
    Use when profile changes or new preferences detected
    """
    event = EventFactory.create_event(
        "recommendation_update_requested",
        user_id=user_id,
        source="manual_trigger"
    )
    await event_bus.publish(event, category="SYSTEM")


async def trigger_profile_analysis(user_id: str):
    """
    Manually trigger profile analysis
    
    Use when user requests analysis or profile significantly updated
    """
    event = EventFactory.create_event(
        "profile_analysis_requested",
        user_id=user_id,
        source="manual_trigger"
    )
    await event_bus.publish(event, category="SYSTEM")


# ========================================
# Global Instance
# ========================================

orchestrator = WorkflowOrchestrator()
