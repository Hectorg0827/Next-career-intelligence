"""
Intervention Engine - Delivers Proactive Guidance

Generates and delivers contextual guidance messages
based on detected needs.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from .guidance_detector import GuidanceType, GuidanceSignal
from app.services.ai.memory import memory_manager
from app.services.foundation.events import EventFactory, event_store

logger = logging.getLogger(__name__)


class InterventionMessage(Dict):
    """A guidance intervention message"""
    pass


class InterventionEngine:
    """
    Generates and delivers proactive guidance interventions.
    
    Creates contextual, actionable guidance messages
    based on detected user needs.
    """
    
    def __init__(self):
        self.intervention_cooldown_hours = 24  # Don't spam users
        self.recent_interventions: Dict[str, List[datetime]] = {}
    
    async def generate_intervention(
        self,
        user_id: str,
        signal: GuidanceSignal
    ) -> Optional[InterventionMessage]:
        """
        Generate intervention message for a guidance signal.
        
        Args:
            user_id: User ID
            signal: Detected guidance signal
            
        Returns:
            Intervention message or None if cooldown active
        """
        
        try:
            # Check cooldown for this type
            if not self._check_cooldown(user_id, signal["type"]):
                logger.info(f"Intervention cooldown active for {user_id} - {signal['type']}")
                return None
            
            # Generate message based on type
            generators = {
                GuidanceType.PROFILE_COMPLETION: self._generate_profile_completion_message,
                GuidanceType.APPLICATION_COACHING: self._generate_application_coaching_message,
                GuidanceType.JOB_SEARCH_STRATEGY: self._generate_job_search_strategy_message,
                GuidanceType.SKILL_DEVELOPMENT: self._generate_skill_development_message,
                GuidanceType.RE_ENGAGEMENT: self._generate_reengagement_message,
                GuidanceType.DECISION_SUPPORT: self._generate_decision_support_message,
                GuidanceType.FEATURE_DISCOVERY: self._generate_feature_discovery_message,
                GuidanceType.SUCCESS_CELEBRATION: self._generate_success_celebration_message
            }
            
            generator = generators.get(signal["type"])
            if not generator:
                return None
            
            message = await generator(user_id, signal)
            
            if message:
                # Record intervention
                self._record_intervention(user_id, signal["type"])
                
                # Emit event
                await self._emit_intervention_event(user_id, message)
            
            return message
            
        except Exception as e:
            logger.error(f"Error generating intervention: {e}")
            return None
    
    async def _generate_profile_completion_message(
        self,
        user_id: str,
        signal: GuidanceSignal
    ) -> InterventionMessage:
        """Generate profile completion guidance"""
        
        completeness = signal["data"]["completeness"]
        missing = signal["data"]["missing_sections"]
        
        return InterventionMessage({
            "type": signal["type"],
            "title": "💡 Boost Your Job Match Score",
            "message": f"Your profile is {completeness:.0f}% complete. Complete these sections to get better job matches:",
            "actions": [
                {
                    "text": f"Add {section}",
                    "action": "complete_profile_section",
                    "params": {"section": section}
                }
                for section in missing[:3]
            ],
            "context": {
                "completeness": completeness,
                "potential_benefit": "up to 40% better job matches"
            },
            "priority": "high"
        })
    
    async def _generate_application_coaching_message(
        self,
        user_id: str,
        signal: GuidanceSignal
    ) -> InterventionMessage:
        """Generate application coaching guidance"""
        
        views = signal["data"]["views"]
        applications = signal["data"]["applications"]
        
        messages = [
            "🎯 Ready to Take the Next Step?",
            "💼 Let's Turn Views into Applications"
        ]
        
        return InterventionMessage({
            "type": signal["type"],
            "title": messages[0],
            "message": f"You've viewed {views} jobs but only applied to {applications}. I can help you apply with confidence!",
            "actions": [
                {
                    "text": "Get Application Tips",
                    "action": "open_application_coach",
                    "params": {}
                },
                {
                    "text": "Review Saved Jobs",
                    "action": "view_saved_jobs",
                    "params": {}
                }
            ],
            "context": {
                "conversion_rate": signal["data"]["conversion_rate"],
                "coaching_available": True
            },
            "priority": "high"
        })
    
    async def _generate_job_search_strategy_message(
        self,
        user_id: str,
        signal: GuidanceSignal
    ) -> InterventionMessage:
        """Generate job search strategy guidance"""
        
        # Get user preferences to suggest focus
        context = await memory_manager.get_complete_context(user_id)
        ltm = context.get("long_term_memory", {})
        prefs = ltm.get("career_preferences", {})
        
        top_industries = prefs.get("preferred_industries", [])[:2]
        top_roles = prefs.get("preferred_roles", [])[:2]
        
        focus_suggestion = ""
        if top_industries:
            focus_suggestion = f"Focus on {' and '.join(top_industries)}"
        if top_roles:
            focus_suggestion += f" in {' or '.join(top_roles)} roles"
        
        return InterventionMessage({
            "type": signal["type"],
            "title": "🎯 Let's Focus Your Job Search",
            "message": f"You're exploring many different paths. {focus_suggestion or 'Let me help you identify your best opportunities'}.",
            "actions": [
                {
                    "text": "Define My Target Roles",
                    "action": "start_career_strategy_session",
                    "params": {}
                },
                {
                    "text": "See Recommended Jobs",
                    "action": "view_recommended_jobs",
                    "params": {}
                }
            ],
            "context": {
                "industries_explored": signal["data"]["unique_industries"],
                "roles_explored": signal["data"]["unique_roles"]
            },
            "priority": "medium"
        })
    
    async def _generate_skill_development_message(
        self,
        user_id: str,
        signal: GuidanceSignal
    ) -> InterventionMessage:
        """Generate skill development guidance"""
        
        skill_gaps = signal["data"]["skill_gaps"]
        
        return InterventionMessage({
            "type": signal["type"],
            "title": "📚 Bridge Your Skill Gaps",
            "message": f"I've identified {len(skill_gaps)} in-demand skills you could learn to unlock more opportunities.",
            "actions": [
                {
                    "text": f"Learn {skill}",
                    "action": "view_learning_resources",
                    "params": {"skill": skill}
                }
                for skill in skill_gaps[:3]
            ],
            "context": {
                "skill_gaps": skill_gaps,
                "learning_available": True
            },
            "priority": "medium"
        })
    
    async def _generate_reengagement_message(
        self,
        user_id: str,
        signal: GuidanceSignal
    ) -> InterventionMessage:
        """Generate re-engagement message"""
        
        return InterventionMessage({
            "type": signal["type"],
            "title": "👋 We've Missed You!",
            "message": "Your career journey doesn't have to stop. Let's pick up where you left off.",
            "actions": [
                {
                    "text": "See New Job Matches",
                    "action": "view_recommended_jobs",
                    "params": {}
                },
                {
                    "text": "Update My Goals",
                    "action": "update_career_goals",
                    "params": {}
                }
            ],
            "context": {
                "days_inactive": signal["data"]["days_inactive"]
            },
            "priority": "low"
        })
    
    async def _generate_decision_support_message(
        self,
        user_id: str,
        signal: GuidanceSignal
    ) -> InterventionMessage:
        """Generate decision support message"""
        
        return InterventionMessage({
            "type": signal["type"],
            "title": "🤔 Need Help Deciding?",
            "message": "I notice you're reviewing some jobs multiple times. Let me help you compare and decide.",
            "actions": [
                {
                    "text": "Compare Jobs",
                    "action": "open_job_comparison",
                    "params": {}
                },
                {
                    "text": "Talk to Career Coach",
                    "action": "start_career_coach_chat",
                    "params": {}
                }
            ],
            "context": {
                "jobs_reconsidered": signal["data"]["repeated_view_count"]
            },
            "priority": "medium"
        })
    
    async def _generate_feature_discovery_message(
        self,
        user_id: str,
        signal: GuidanceSignal
    ) -> InterventionMessage:
        """Generate feature discovery message"""
        
        unused = signal["data"]["unused_features"]
        
        feature_benefits = {
            "career_coach": "Get personalized career advice",
            "skill_assessment": "Discover your skill strengths",
            "resume_builder": "Create a standout resume"
        }
        
        feature_to_highlight = unused[0] if unused else "career_coach"
        benefit = feature_benefits.get(feature_to_highlight, "Enhance your career journey")
        
        return InterventionMessage({
            "type": signal["type"],
            "title": f"✨ Try {feature_to_highlight.replace('_', ' ').title()}",
            "message": f"{benefit} - it's free and takes just 5 minutes!",
            "actions": [
                {
                    "text": f"Try {feature_to_highlight.replace('_', ' ').title()}",
                    "action": f"open_{feature_to_highlight}",
                    "params": {}
                }
            ],
            "context": {
                "unused_features": unused
            },
            "priority": "low"
        })
    
    async def _generate_success_celebration_message(
        self,
        user_id: str,
        signal: GuidanceSignal
    ) -> InterventionMessage:
        """Generate success celebration message"""
        
        milestone = signal["data"]["milestone"]
        
        celebrations = {
            "5_applications": {
                "title": "🎉 Amazing Progress!",
                "message": "You've applied to 5 jobs this week! That's fantastic momentum. Keep it up!"
            },
            "profile_completion": {
                "title": "⭐ Profile Complete!",
                "message": "Your profile is now 90%+ complete. You're ready for great opportunities!"
            }
        }
        
        celebration = celebrations.get(milestone, celebrations["5_applications"])
        
        return InterventionMessage({
            "type": signal["type"],
            "title": celebration["title"],
            "message": celebration["message"],
            "actions": [
                {
                    "text": "View My Progress",
                    "action": "view_journey_dashboard",
                    "params": {}
                }
            ],
            "context": {
                "milestone": milestone
            },
            "priority": "low"
        })
    
    def _check_cooldown(self, user_id: str, intervention_type: GuidanceType) -> bool:
        """Check if intervention cooldown allows sending"""
        
        key = f"{user_id}:{intervention_type}"
        
        if key not in self.recent_interventions:
            return True
        
        # Check if last intervention was > cooldown period ago
        last_intervention = self.recent_interventions[key][-1]
        hours_since = (datetime.utcnow() - last_intervention).total_seconds() / 3600
        
        return hours_since >= self.intervention_cooldown_hours
    
    def _record_intervention(self, user_id: str, intervention_type: GuidanceType):
        """Record that an intervention was sent"""
        
        key = f"{user_id}:{intervention_type}"
        
        if key not in self.recent_interventions:
            self.recent_interventions[key] = []
        
        self.recent_interventions[key].append(datetime.utcnow())
        
        # Keep only last 5
        self.recent_interventions[key] = self.recent_interventions[key][-5:]
    
    async def _emit_intervention_event(self, user_id: str, message: InterventionMessage):
        """Emit event for intervention"""
        
        try:
            event = EventFactory.create_event(
                "guidance_provided",
                user_id=user_id,
                source="proactive_coach",
                guidance_type=message["type"],
                title=message["title"],
                priority=message["priority"]
            )
            await event_store.store_event(event)
        except Exception as e:
            logger.error(f"Error emitting intervention event: {e}")
