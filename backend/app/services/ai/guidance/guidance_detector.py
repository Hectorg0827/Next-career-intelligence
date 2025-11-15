"""
Guidance Detector - Identifies When Users Need Help

Analyzes behavior patterns to detect:
- Confusion or struggle
- Missed opportunities
- Suboptimal actions
- Need for direction
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import logging

from app.services.foundation.events import event_store, event_analytics
from app.services.foundation.journey import journey_analytics
from app.services.ai.memory import memory_manager

logger = logging.getLogger(__name__)


class GuidanceType(str, Enum):
    """Types of guidance interventions"""
    PROFILE_COMPLETION = "profile_completion"
    APPLICATION_COACHING = "application_coaching"
    JOB_SEARCH_STRATEGY = "job_search_strategy"
    SKILL_DEVELOPMENT = "skill_development"
    RE_ENGAGEMENT = "re_engagement"
    DECISION_SUPPORT = "decision_support"
    FEATURE_DISCOVERY = "feature_discovery"
    SUCCESS_CELEBRATION = "success_celebration"


class GuidanceSignal(Dict):
    """Detected signal that guidance may be needed"""
    pass


class GuidanceDetector:
    """
    Detects when users need proactive guidance.
    
    Monitors behavior patterns and identifies intervention opportunities.
    """
    
    def __init__(self):
        self.detection_threshold = 0.6  # Confidence threshold
    
    async def detect_guidance_needs(
        self,
        user_id: str,
        check_types: Optional[List[GuidanceType]] = None
    ) -> List[GuidanceSignal]:
        """
        Detect all guidance needs for a user.
        
        Args:
            user_id: User ID
            check_types: Specific types to check (None = all)
            
        Returns:
            List of detected guidance signals
        """
        
        try:
            # Get user context
            context = await memory_manager.get_complete_context(user_id)
            
            # Get recent events
            recent_events = await event_store.get_events_by_user(
                user_id=user_id,
                start_date=datetime.utcnow() - timedelta(days=14),
                limit=200
            )
            
            signals = []
            
            # Check each guidance type
            detectors = {
                GuidanceType.PROFILE_COMPLETION: self._detect_profile_completion_need,
                GuidanceType.APPLICATION_COACHING: self._detect_application_coaching_need,
                GuidanceType.JOB_SEARCH_STRATEGY: self._detect_job_search_strategy_need,
                GuidanceType.SKILL_DEVELOPMENT: self._detect_skill_development_need,
                GuidanceType.RE_ENGAGEMENT: self._detect_reengagement_need,
                GuidanceType.DECISION_SUPPORT: self._detect_decision_support_need,
                GuidanceType.FEATURE_DISCOVERY: self._detect_feature_discovery_need,
                GuidanceType.SUCCESS_CELEBRATION: self._detect_success_celebration_need
            }
            
            for guidance_type, detector_func in detectors.items():
                if check_types is None or guidance_type in check_types:
                    signal = await detector_func(user_id, context, recent_events)
                    if signal:
                        signals.append(signal)
            
            # Sort by urgency
            signals.sort(key=lambda x: x.get("urgency_score", 0), reverse=True)
            
            logger.info(f"Detected {len(signals)} guidance needs for {user_id}")
            return signals
            
        except Exception as e:
            logger.error(f"Error detecting guidance needs: {e}")
            return []
    
    async def _detect_profile_completion_need(
        self,
        user_id: str,
        context: Dict,
        events: List[Dict]
    ) -> Optional[GuidanceSignal]:
        """Detect if user needs help completing profile"""
        
        ltm = context.get("long_term_memory", {})
        if not ltm or "error" in ltm:
            return None
        
        # Check profile completeness from unified profile
        from app.services.foundation.profile import unified_profile_manager
        profile = await unified_profile_manager.get_unified_profile(user_id)
        
        completeness = profile.get("completeness", {}).get("overall_score", 100)
        
        # Trigger if:
        # 1. Profile < 60% complete
        # 2. User has been active (viewed jobs) but not completed profile
        
        if completeness >= 60:
            return None
        
        job_views = len([e for e in events if e.get("event_type") == "job_viewed"])
        
        if job_views > 10:  # Active but incomplete profile
            return GuidanceSignal({
                "type": GuidanceType.PROFILE_COMPLETION,
                "confidence": 0.8,
                "urgency_score": 0.7,
                "reason": "Active job search with incomplete profile limiting opportunities",
                "data": {
                    "completeness": completeness,
                    "missing_sections": profile.get("completeness", {}).get("missing_fields", []),
                    "job_views": job_views
                }
            })
        
        return None
    
    async def _detect_application_coaching_need(
        self,
        user_id: str,
        context: Dict,
        events: List[Dict]
    ) -> Optional[GuidanceSignal]:
        """Detect if user needs help applying to jobs"""
        
        # Count job interactions
        job_views = len([e for e in events if e.get("event_type") == "job_viewed"])
        job_saves = len([e for e in events if e.get("event_type") == "job_saved"])
        job_applications = len([e for e in events if e.get("event_type") == "job_applied"])
        
        # Trigger if:
        # 1. Many views (>30) but few applications (<3)
        # 2. Or many saves (>10) but no applications
        
        if job_views > 30 and job_applications < 3:
            return GuidanceSignal({
                "type": GuidanceType.APPLICATION_COACHING,
                "confidence": 0.85,
                "urgency_score": 0.8,
                "reason": "Viewing many jobs but not applying - may lack confidence or clarity",
                "data": {
                    "views": job_views,
                    "saves": job_saves,
                    "applications": job_applications,
                    "conversion_rate": job_applications / max(job_views, 1)
                }
            })
        
        if job_saves > 10 and job_applications == 0:
            return GuidanceSignal({
                "type": GuidanceType.APPLICATION_COACHING,
                "confidence": 0.9,
                "urgency_score": 0.9,
                "reason": "Saving jobs but not applying - needs application support",
                "data": {
                    "saves": job_saves,
                    "applications": job_applications
                }
            })
        
        return None
    
    async def _detect_job_search_strategy_need(
        self,
        user_id: str,
        context: Dict,
        events: List[Dict]
    ) -> Optional[GuidanceSignal]:
        """Detect if user needs strategic job search guidance"""
        
        ltm = context.get("long_term_memory", {})
        if not ltm:
            return None
        
        # Check for scattered search pattern
        job_events = [e for e in events if e.get("category") == "JOB"]
        
        if len(job_events) < 20:
            return None  # Not enough data
        
        # Analyze diversity of searches
        industries = []
        roles = []
        
        for event in job_events:
            data = event.get("event_data", {})
            if "industry" in data:
                industries.append(data["industry"])
            if "job_title" in data:
                roles.append(data["job_title"])
        
        # If too many different industries/roles → unfocused search
        unique_industries = len(set(industries))
        unique_roles = len(set(roles))
        
        if unique_industries > 8 or unique_roles > 15:
            return GuidanceSignal({
                "type": GuidanceType.JOB_SEARCH_STRATEGY,
                "confidence": 0.75,
                "urgency_score": 0.6,
                "reason": "Unfocused job search - would benefit from strategic targeting",
                "data": {
                    "unique_industries": unique_industries,
                    "unique_roles": unique_roles,
                    "total_searches": len(job_events)
                }
            })
        
        return None
    
    async def _detect_skill_development_need(
        self,
        user_id: str,
        context: Dict,
        events: List[Dict]
    ) -> Optional[GuidanceSignal]:
        """Detect if user should focus on skill development"""
        
        ltm = context.get("long_term_memory", {})
        if not ltm:
            return None
        
        pain_points = ltm.get("pain_points", [])
        skill_gaps = ltm.get("skill_profile", {}).get("skill_gaps", [])
        
        # Check if viewing jobs with skills they don't have
        if len(skill_gaps) >= 3:
            return GuidanceSignal({
                "type": GuidanceType.SKILL_DEVELOPMENT,
                "confidence": 0.7,
                "urgency_score": 0.65,
                "reason": "Multiple skill gaps identified from job searches",
                "data": {
                    "skill_gaps": skill_gaps[:5],
                    "gap_count": len(skill_gaps)
                }
            })
        
        return None
    
    async def _detect_reengagement_need(
        self,
        user_id: str,
        context: Dict,
        events: List[Dict]
    ) -> Optional[GuidanceSignal]:
        """Detect if user has disengaged and needs re-engagement"""
        
        # Check for recent inactivity
        recent_events = [
            e for e in events
            if (datetime.utcnow() - datetime.fromisoformat(e["timestamp"].replace("Z", "+00:00"))).days < 7
        ]
        
        if len(recent_events) < 3:
            # Was previously active?
            older_events = [
                e for e in events
                if 7 < (datetime.utcnow() - datetime.fromisoformat(e["timestamp"].replace("Z", "+00:00"))).days < 14
            ]
            
            if len(older_events) >= 10:
                # Was active, now inactive
                return GuidanceSignal({
                    "type": GuidanceType.RE_ENGAGEMENT,
                    "confidence": 0.85,
                    "urgency_score": 0.7,
                    "reason": "Previously active user has become inactive",
                    "data": {
                        "recent_events": len(recent_events),
                        "previous_activity": len(older_events),
                        "days_inactive": 7
                    }
                })
        
        return None
    
    async def _detect_decision_support_need(
        self,
        user_id: str,
        context: Dict,
        events: List[Dict]
    ) -> Optional[GuidanceSignal]:
        """Detect if user is struggling with decisions"""
        
        # Check for repeated views of same jobs without action
        job_view_events = [e for e in events if e.get("event_type") == "job_viewed"]
        
        job_view_counts = {}
        for event in job_view_events:
            job_id = event.get("event_data", {}).get("job_id")
            if job_id:
                job_view_counts[job_id] = job_view_counts.get(job_id, 0) + 1
        
        # If viewing same jobs repeatedly → decision paralysis
        repeated_views = [job_id for job_id, count in job_view_counts.items() if count >= 3]
        
        if len(repeated_views) >= 3:
            return GuidanceSignal({
                "type": GuidanceType.DECISION_SUPPORT,
                "confidence": 0.75,
                "urgency_score": 0.65,
                "reason": "Viewing jobs repeatedly without taking action - may need decision support",
                "data": {
                    "repeated_view_count": len(repeated_views),
                    "jobs_viewed_multiple_times": repeated_views[:5]
                }
            })
        
        return None
    
    async def _detect_feature_discovery_need(
        self,
        user_id: str,
        context: Dict,
        events: List[Dict]
    ) -> Optional[GuidanceSignal]:
        """Detect if user is missing valuable features"""
        
        # Check feature adoption
        feature_usage = await journey_analytics.get_feature_adoption(user_id)
        
        if not feature_usage:
            return None
        
        # Identify unused high-value features
        high_value_features = ["career_coach", "skill_assessment", "resume_builder"]
        unused_features = [
            feature for feature in high_value_features
            if feature not in feature_usage
        ]
        
        # If user has been active (20+ events) but not using key features
        if len(events) > 20 and len(unused_features) >= 2:
            return GuidanceSignal({
                "type": GuidanceType.FEATURE_DISCOVERY,
                "confidence": 0.7,
                "urgency_score": 0.5,
                "reason": "Active user not utilizing key features",
                "data": {
                    "unused_features": unused_features,
                    "total_features_used": len(feature_usage)
                }
            })
        
        return None
    
    async def _detect_success_celebration_need(
        self,
        user_id: str,
        context: Dict,
        events: List[Dict]
    ) -> Optional[GuidanceSignal]:
        """Detect achievements worth celebrating"""
        
        recent_7d = [
            e for e in events
            if (datetime.utcnow() - datetime.fromisoformat(e["timestamp"].replace("Z", "+00:00"))).days < 7
        ]
        
        # Check for application milestone
        applications = [e for e in recent_7d if e.get("event_type") == "job_applied"]
        
        if len(applications) >= 5:
            return GuidanceSignal({
                "type": GuidanceType.SUCCESS_CELEBRATION,
                "confidence": 1.0,
                "urgency_score": 0.4,
                "reason": "User has applied to 5+ jobs this week - celebrate progress!",
                "data": {
                    "applications_this_week": len(applications),
                    "milestone": "5_applications"
                }
            })
        
        # Check for profile completion
        from app.services.foundation.profile import unified_profile_manager
        profile = await unified_profile_manager.get_unified_profile(user_id)
        completeness = profile.get("completeness", {}).get("overall_score", 0)
        
        if completeness >= 90:
            # Check if recently crossed threshold
            profile_events = [e for e in recent_7d if e.get("event_type") == "profile_updated"]
            if profile_events:
                return GuidanceSignal({
                    "type": GuidanceType.SUCCESS_CELEBRATION,
                    "confidence": 1.0,
                    "urgency_score": 0.3,
                    "reason": "Profile now 90%+ complete - celebrate achievement!",
                    "data": {
                        "completeness": completeness,
                        "milestone": "profile_completion"
                    }
                })
        
        return None
