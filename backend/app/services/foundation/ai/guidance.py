"""
Proactive Guidance System - AI Agent That Anticipates User Needs

Monitors user behavior and provides timely interventions:
- Profile completion nudges when data is missing
- Application coaching when user views but doesn't apply
- Skill gap alerts when missing critical skills
- Career path suggestions when user seems lost
- Re-engagement triggers for inactive users

Philosophy: Don't wait for users to ask - proactively guide them.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from enum import Enum

from loguru import logger

from app.db.supabase import get_supabase_client
from ..events.event_store import event_store, event_analytics
from ..journey.tracker import session_manager, journey_analytics
from ..profile.unified_profile import unified_profile_manager
from .memory import ai_memory


class GuidanceType(str, Enum):
    """Types of proactive guidance"""
    PROFILE_COMPLETION = "profile_completion"
    APPLICATION_COACHING = "application_coaching"
    SKILL_GAP_ALERT = "skill_gap_alert"
    CAREER_PATH_SUGGESTION = "career_path_suggestion"
    REENGAGEMENT = "reengagement"
    MILESTONE_CELEBRATION = "milestone_celebration"
    LEARNING_RECOMMENDATION = "learning_recommendation"


class GuidanceMessage:
    """Single guidance message to show user"""
    
    def __init__(
        self,
        guidance_type: GuidanceType,
        priority: int,  # 1-5, 5=urgent
        title: str,
        message: str,
        action_text: str,
        action_link: str,
        metadata: Dict[str, Any]
    ):
        self.guidance_type = guidance_type
        self.priority = priority
        self.title = title
        self.message = message
        self.action_text = action_text
        self.action_link = action_link
        self.metadata = metadata
        self.created_at = datetime.utcnow()


class ProactiveGuidanceSystem:
    """
    AI-powered proactive guidance engine
    
    Detection Rules:
    - Profile <30% complete → nudge to complete
    - 50+ jobs viewed, 0 applied → coaching needed
    - Skill match <60% repeatedly → highlight gaps
    - No activity 7 days → re-engagement
    - Goal created but no progress → path suggestion
    """
    
    def __init__(self):
        self.supabase = get_supabase_client()
    
    async def get_guidance_for_user(self, user_id: str) -> List[GuidanceMessage]:
        """
        Analyze user state and generate appropriate guidance
        
        Returns prioritized list of guidance messages
        """
        try:
            logger.info(f"Analyzing guidance needs for user {user_id}")
            
            guidance_messages = []
            
            # Check each guidance type
            profile_guidance = await self._check_profile_completion(user_id)
            if profile_guidance:
                guidance_messages.append(profile_guidance)
            
            app_coaching = await self._check_application_behavior(user_id)
            if app_coaching:
                guidance_messages.append(app_coaching)
            
            skill_alert = await self._check_skill_gaps(user_id)
            if skill_alert:
                guidance_messages.append(skill_alert)
            
            path_suggestion = await self._check_career_direction(user_id)
            if path_suggestion:
                guidance_messages.append(path_suggestion)
            
            reengagement = await self._check_user_activity(user_id)
            if reengagement:
                guidance_messages.append(reengagement)
            
            milestone = await self._check_milestones(user_id)
            if milestone:
                guidance_messages.append(milestone)
            
            # Sort by priority
            guidance_messages.sort(key=lambda x: x.priority, reverse=True)
            
            logger.info(f"Generated {len(guidance_messages)} guidance messages")
            return guidance_messages
            
        except Exception as e:
            logger.error(f"Error generating guidance: {e}")
            return []
    
    async def _check_profile_completion(self, user_id: str) -> Optional[GuidanceMessage]:
        """
        Detect incomplete profiles and nudge completion
        
        Triggers if completeness <30% and user has been active
        """
        try:
            # Get profile completeness
            profile = await unified_profile_manager.get_unified_profile(user_id)
            
            if not profile:
                return None
            
            completeness = profile.get("completeness", {})
            overall_score = completeness.get("overall_score", 0)
            missing_sections = completeness.get("missing_sections", [])
            
            if overall_score >= 30:
                return None  # Profile is sufficient
            
            # Check if user is active (has recent events)
            events = await event_store.get_events_by_user(user_id, limit=10)
            if not events:
                return None  # Don't nag inactive users
            
            # Build personalized message
            if overall_score < 15:
                urgency = 5
                title = "🎯 Complete Your Profile to Get Started"
                message = f"Your profile is only {int(overall_score)}% complete. Add your skills, experience, and career goals to unlock personalized job recommendations."
            else:
                urgency = 3
                title = "📝 Boost Your Profile"
                message = f"You're {int(overall_score)}% complete. Adding {', '.join(missing_sections[:2])} will improve your job matches by up to 40%."
            
            return GuidanceMessage(
                guidance_type=GuidanceType.PROFILE_COMPLETION,
                priority=urgency,
                title=title,
                message=message,
                action_text="Complete Profile",
                action_link="/profile/edit",
                metadata={
                    "current_score": overall_score,
                    "missing_sections": missing_sections
                }
            )
            
        except Exception as e:
            logger.error(f"Error checking profile completion: {e}")
            return None
    
    async def _check_application_behavior(self, user_id: str) -> Optional[GuidanceMessage]:
        """
        Detect users browsing extensively but not applying
        
        Triggers if 50+ jobs viewed but <5% conversion to applications
        """
        try:
            # Get job-related events from last 30 days
            events = await event_store.get_events_by_user(
                user_id=user_id,
                category="JOB",
                limit=200
            )
            
            viewed_count = sum(1 for e in events if e.get("event_type") == "job_viewed")
            applied_count = sum(1 for e in events if e.get("event_type") == "job_applied")
            
            if viewed_count < 20:
                return None  # Not enough data
            
            conversion_rate = (applied_count / viewed_count * 100) if viewed_count > 0 else 0
            
            if conversion_rate < 5 and viewed_count >= 50:
                # User is browsing heavily but not applying
                return GuidanceMessage(
                    guidance_type=GuidanceType.APPLICATION_COACHING,
                    priority=4,
                    title="💪 Ready to Take the Next Step?",
                    message=f"You've viewed {viewed_count} jobs but only applied to {applied_count}. Let's work together to identify the perfect roles and craft winning applications. Our AI coach can help!",
                    action_text="Get Application Coaching",
                    action_link="/coach?topic=application_help",
                    metadata={
                        "viewed_count": viewed_count,
                        "applied_count": applied_count,
                        "conversion_rate": conversion_rate
                    }
                )
            elif conversion_rate < 10 and viewed_count >= 30:
                # Moderate issue
                return GuidanceMessage(
                    guidance_type=GuidanceType.APPLICATION_COACHING,
                    priority=2,
                    title="📈 Improve Your Application Success",
                    message=f"You're viewing many jobs ({viewed_count}) but only applying to a few ({applied_count}). Let me help you find the best matches and increase your confidence.",
                    action_text="Chat with Coach",
                    action_link="/coach",
                    metadata={
                        "viewed_count": viewed_count,
                        "applied_count": applied_count
                    }
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking application behavior: {e}")
            return None
    
    async def _check_skill_gaps(self, user_id: str) -> Optional[GuidanceMessage]:
        """
        Detect repeated interest in jobs with missing skills
        
        Triggers when user views jobs requiring skills they don't have
        """
        try:
            # Get profile
            profile = await unified_profile_manager.get_unified_profile(user_id)
            if not profile:
                return None
            
            user_skills = set(s.lower() for s in profile.get("career_data", {}).get("skills", []))
            
            # Get recent job views
            events = await event_store.get_events_by_user(
                user_id=user_id,
                category="JOB",
                limit=50
            )
            
            viewed_jobs = [e for e in events if e.get("event_type") == "job_viewed"]
            
            if len(viewed_jobs) < 10:
                return None
            
            # Track missing skills across viewed jobs
            missing_skills = {}
            
            for job_event in viewed_jobs:
                job_data = job_event.get("event_data", {})
                required_skills = job_data.get("skills", [])
                
                for skill in required_skills:
                    skill_lower = skill.lower()
                    if skill_lower not in user_skills:
                        missing_skills[skill] = missing_skills.get(skill, 0) + 1
            
            # Find skills missing in >40% of viewed jobs
            threshold = len(viewed_jobs) * 0.4
            critical_gaps = {
                skill: count
                for skill, count in missing_skills.items()
                if count >= threshold
            }
            
            if critical_gaps:
                top_gaps = sorted(critical_gaps.items(), key=lambda x: x[1], reverse=True)[:3]
                gap_names = [skill for skill, _ in top_gaps]
                
                return GuidanceMessage(
                    guidance_type=GuidanceType.SKILL_GAP_ALERT,
                    priority=4,
                    title="🎓 Skill Gap Identified",
                    message=f"Many jobs you're interested in require: {', '.join(gap_names)}. Learning these skills could unlock {len(viewed_jobs)} more opportunities.",
                    action_text="See Learning Path",
                    action_link=f"/learning?skills={','.join(gap_names)}",
                    metadata={
                        "skill_gaps": gap_names,
                        "opportunities_unlocked": len(viewed_jobs)
                    }
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking skill gaps: {e}")
            return None
    
    async def _check_career_direction(self, user_id: str) -> Optional[GuidanceMessage]:
        """
        Detect users who seem lost or unfocused
        
        Triggers when behavior is scattered across many different job types
        """
        try:
            # Get job viewing behavior
            events = await event_store.get_events_by_user(
                user_id=user_id,
                category="JOB",
                limit=100
            )
            
            viewed_jobs = [e for e in events if e.get("event_type") == "job_viewed"]
            
            if len(viewed_jobs) < 20:
                return None  # Not enough data
            
            # Extract job titles
            job_titles = [e.get("event_data", {}).get("job_title", "") for e in viewed_jobs]
            
            # Simple analysis: count unique first words in titles
            # (In production: use clustering)
            first_words = [title.split()[0].lower() for title in job_titles if title]
            unique_first_words = len(set(first_words))
            
            # If >70% of jobs have different starting words, user may be unfocused
            diversity_ratio = unique_first_words / len(first_words) if first_words else 0
            
            if diversity_ratio > 0.7:
                return GuidanceMessage(
                    guidance_type=GuidanceType.CAREER_PATH_SUGGESTION,
                    priority=3,
                    title="🗺️ Let's Map Your Career Path",
                    message=f"I notice you're exploring many different roles ({unique_first_words} types). Let's chat about your goals and create a focused career plan.",
                    action_text="Define Your Path",
                    action_link="/coach?topic=career_planning",
                    metadata={
                        "job_diversity": diversity_ratio,
                        "job_types_explored": unique_first_words
                    }
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking career direction: {e}")
            return None
    
    async def _check_user_activity(self, user_id: str) -> Optional[GuidanceMessage]:
        """
        Detect inactive users and trigger re-engagement
        
        Triggers after 7 days of no activity
        """
        try:
            # Get user's last event
            events = await event_store.get_events_by_user(user_id, limit=1)
            
            if not events:
                return None  # No history to compare
            
            last_event_time = datetime.fromisoformat(events[0].get("created_at", ""))
            days_inactive = (datetime.utcnow() - last_event_time).days
            
            if days_inactive >= 7:
                # Get engagement metrics to personalize message
                metrics = await journey_analytics.get_user_engagement_metrics(user_id, days=30)
                
                jobs_viewed = metrics.get("total_events", {}).get("job_viewed", 0)
                
                if jobs_viewed > 10:
                    # Was active before
                    return GuidanceMessage(
                        guidance_type=GuidanceType.REENGAGEMENT,
                        priority=3,
                        title="👋 We Miss You!",
                        message=f"It's been {days_inactive} days since your last visit. We've added {25} new jobs that match your profile. Come check them out!",
                        action_text="See New Jobs",
                        action_link="/jobs/recommendations",
                        metadata={
                            "days_inactive": days_inactive,
                            "previous_engagement": jobs_viewed
                        }
                    )
                else:
                    # Was never very active
                    return GuidanceMessage(
                        guidance_type=GuidanceType.REENGAGEMENT,
                        priority=2,
                        title="🚀 Ready to Accelerate Your Career?",
                        message="Your personalized career dashboard is waiting. Let's find your dream job together.",
                        action_text="Get Started",
                        action_link="/dashboard",
                        metadata={
                            "days_inactive": days_inactive
                        }
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking user activity: {e}")
            return None
    
    async def _check_milestones(self, user_id: str) -> Optional[GuidanceMessage]:
        """
        Celebrate positive milestones
        
        Triggers for achievements like profile completion, first application, etc.
        """
        try:
            # Check for recent milestones
            response = self.supabase.table("career_milestones") \
                .select("*") \
                .eq("user_id", user_id) \
                .eq("celebrated", False) \
                .order("achieved_at", desc=True) \
                .limit(1) \
                .execute()
            
            milestones = response.data if response.data else []
            
            if not milestones:
                return None
            
            milestone = milestones[0]
            milestone_type = milestone.get("milestone_type", "")
            
            messages = {
                "first_application": (
                    "🎉 First Application Submitted!",
                    "You've taken the first step! Keep the momentum going - every application brings you closer to your dream job."
                ),
                "profile_completed": (
                    "✨ Profile Complete!",
                    "Your profile is now 100% complete! You're 3x more likely to get matched with great opportunities."
                ),
                "10_applications": (
                    "🚀 10 Applications Milestone!",
                    "You've applied to 10 jobs - that's commitment! Keep it up, success is around the corner."
                )
            }
            
            if milestone_type in messages:
                title, message = messages[milestone_type]
                
                # Mark as celebrated
                self.supabase.table("career_milestones") \
                    .update({"celebrated": True}) \
                    .eq("id", milestone.get("id")) \
                    .execute()
                
                return GuidanceMessage(
                    guidance_type=GuidanceType.MILESTONE_CELEBRATION,
                    priority=5,
                    title=title,
                    message=message,
                    action_text="Continue",
                    action_link="/dashboard",
                    metadata={
                        "milestone_type": milestone_type
                    }
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking milestones: {e}")
            return None
    
    async def trigger_guidance(
        self,
        user_id: str,
        guidance_message: GuidanceMessage
    ) -> bool:
        """
        Record that guidance was shown to user
        
        Returns True if successfully recorded
        """
        try:
            self.supabase.table("guidance_history").insert({
                "user_id": user_id,
                "guidance_type": guidance_message.guidance_type.value,
                "title": guidance_message.title,
                "message": guidance_message.message,
                "priority": guidance_message.priority,
                "shown_at": datetime.utcnow().isoformat(),
                "metadata": guidance_message.metadata
            }).execute()
            
            logger.info(f"Recorded guidance trigger: {guidance_message.guidance_type}")
            return True
            
        except Exception as e:
            logger.error(f"Error recording guidance: {e}")
            return False


# Global instance
proactive_guidance = ProactiveGuidanceSystem()
