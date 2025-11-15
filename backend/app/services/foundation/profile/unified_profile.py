"""
Unified Profile Manager - Single Source of Truth for User Data

This module consolidates user data from multiple sources:
- user_profile (analyzer behavioral data)
- career_profiles (resume studio SSOT)
- career_profile_versions (audit history)
- user_journey_metrics (engagement data)

Provides a single, coherent API for accessing complete user context.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from uuid import uuid4

from app.db.supabase import get_supabase_client
from ..events.event_store import event_store, event_analytics
from ..events.event_types import EventFactory, EventCategory


class UnifiedProfileManager:
    """
    Manage unified user profiles
    
    Consolidates data from multiple tables into single coherent view:
    - Career data (resume, experience, skills)
    - Behavioral data (jobs viewed, saved, applied)
    - Journey metrics (engagement, feature usage)
    - Preferences and goals
    """
    
    def __init__(self):
        self.supabase = get_supabase_client()
        self.career_profiles_table = "career_profiles"
        self.user_profile_table = "user_profile"
        self.profile_versions_table = "career_profile_versions"
        self.journey_metrics_table = "user_journey_metrics"
    
    async def get_unified_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Get complete unified profile for user
        
        Args:
            user_id: User UUID
            
        Returns:
            Complete profile with all data sources merged
        """
        try:
            # Get career profile (SSOT from resume studio)
            career_profile = await self._get_career_profile(user_id)
            
            # Get behavioral profile (from analyzer)
            behavioral_profile = await self._get_behavioral_profile(user_id)
            
            # Get engagement metrics
            engagement_metrics = await self._get_engagement_metrics(user_id)
            
            # Get recent activity
            recent_activity = await self._get_recent_activity(user_id, days=7)
            
            # Get profile completeness
            completeness = await self._calculate_completeness(career_profile)
            
            # Merge everything
            unified = {
                "user_id": user_id,
                "updated_at": datetime.utcnow().isoformat(),
                
                # Career data
                "career": career_profile,
                
                # Behavioral data
                "behavior": behavioral_profile,
                
                # Engagement data
                "engagement": engagement_metrics,
                
                # Recent activity
                "recent_activity": recent_activity,
                
                # Profile health
                "completeness": completeness,
                
                # AI context (synthesized insights)
                "ai_context": await self._generate_ai_context(
                    career_profile,
                    behavioral_profile,
                    engagement_metrics
                )
            }
            
            return unified
            
        except Exception as e:
            print(f"Error getting unified profile: {e}")
            raise
    
    async def _get_career_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get career profile from resume studio"""
        try:
            result = (
                self.supabase.table(self.career_profiles_table)
                .select("*")
                .eq("user_id", user_id)
                .order("updated_at", desc=True)
                .limit(1)
                .execute()
            )
            
            if result.data:
                profile = result.data[0]
                
                # Parse JSONB fields
                return {
                    "profile_id": profile.get("id"),
                    "personal_info": profile.get("personal_info", {}),
                    "professional_summary": profile.get("professional_summary"),
                    "work_history": profile.get("work_history", []),
                    "education": profile.get("education", []),
                    "skills": profile.get("skills", []),
                    "certifications": profile.get("certifications", []),
                    "projects": profile.get("projects", []),
                    "achievements": profile.get("achievements", []),
                    "last_updated": profile.get("updated_at")
                }
            
            return None
            
        except Exception as e:
            print(f"Error getting career profile: {e}")
            return None
    
    async def _get_behavioral_profile(self, user_id: str) -> Dict[str, Any]:
        """Get behavioral data from analyzer"""
        try:
            result = (
                self.supabase.table(self.user_profile_table)
                .select("*")
                .eq("user_id", user_id)
                .single()
                .execute()
            )
            
            if result.data:
                profile = result.data
                
                return {
                    "jobs_viewed": profile.get("jobs_viewed", []),
                    "jobs_saved": profile.get("jobs_saved", []),
                    "jobs_applied": profile.get("jobs_applied", []),
                    "preferred_industries": profile.get("preferred_industries", []),
                    "preferred_locations": profile.get("preferred_locations", []),
                    "salary_expectations": profile.get("salary_expectations", {}),
                    "work_preferences": profile.get("work_preferences", {}),
                    "last_job_search": profile.get("last_job_search_date")
                }
            
            return {
                "jobs_viewed": [],
                "jobs_saved": [],
                "jobs_applied": [],
                "preferred_industries": [],
                "preferred_locations": [],
                "salary_expectations": {},
                "work_preferences": {},
                "last_job_search": None
            }
            
        except Exception as e:
            print(f"Error getting behavioral profile: {e}")
            return {}
    
    async def _get_engagement_metrics(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get engagement metrics from journey tracker"""
        try:
            # Get aggregated metrics from past 30 days
            start_date = datetime.utcnow() - timedelta(days=days)
            
            result = (
                self.supabase.table(self.journey_metrics_table)
                .select("*")
                .eq("user_id", user_id)
                .gte("metric_date", start_date.date().isoformat())
                .execute()
            )
            
            if not result.data:
                return {
                    "total_sessions": 0,
                    "total_events": 0,
                    "features_used": [],
                    "engagement_score": 0
                }
            
            metrics = result.data
            
            # Aggregate
            total_sessions = sum(m.get("sessions_count", 0) for m in metrics)
            total_events = sum(m.get("events_count", 0) for m in metrics)
            
            # Collect all features used
            all_features = set()
            for m in metrics:
                features = m.get("features_used", [])
                all_features.update(features)
            
            # Get engagement score from analytics
            engagement_score = await event_analytics.get_user_engagement_score(
                user_id=user_id,
                days=days
            )
            
            return {
                "total_sessions": total_sessions,
                "total_events": total_events,
                "avg_events_per_session": round(total_events / total_sessions, 2) if total_sessions > 0 else 0,
                "features_used": list(all_features),
                "engagement_score": engagement_score,
                "days_active": len(metrics),
                "activity_rate": len(metrics) / days * 100
            }
            
        except Exception as e:
            print(f"Error getting engagement metrics: {e}")
            return {}
    
    async def _get_recent_activity(self, user_id: str, days: int = 7) -> List[Dict[str, Any]]:
        """Get recent user activity timeline"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            events = await event_store.get_user_timeline(user_id=user_id, days=days)
            
            # Format for display
            timeline = []
            for event in events[-20:]:  # Last 20 events
                timeline.append({
                    "event_type": event["event_type"],
                    "category": event["event_category"],
                    "timestamp": event["created_at"],
                    "source": event.get("source"),
                    "summary": self._format_event_summary(event)
                })
            
            return timeline
            
        except Exception as e:
            print(f"Error getting recent activity: {e}")
            return []
    
    def _format_event_summary(self, event: Dict[str, Any]) -> str:
        """Format event into human-readable summary"""
        event_type = event["event_type"]
        data = event.get("event_data", {})
        
        summaries = {
            "job_viewed": f"Viewed job: {data.get('job_title', 'Unknown')}",
            "job_saved": f"Saved job: {data.get('job_title', 'Unknown')}",
            "job_applied": f"Applied to job: {data.get('job_title', 'Unknown')}",
            "search_performed": f"Searched for: {data.get('search_query', '')}",
            "profile_updated": f"Updated profile: {', '.join(data.get('fields_changed', []))}",
            "coach_message_sent": f"Sent message to Career Coach",
            "goal_created": f"Created goal: {data.get('goal_title', 'Unknown')}",
            "goal_completed": f"Completed goal: {data.get('goal_title', 'Unknown')}",
            "resume_generated": f"Generated resume: {data.get('resume_name', 'New Resume')}",
            "interview_session_started": f"Started interview practice session"
        }
        
        return summaries.get(event_type, f"Event: {event_type}")
    
    async def _calculate_completeness(self, career_profile: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate profile completeness score"""
        if not career_profile:
            return {
                "overall_score": 0,
                "sections": {},
                "missing_fields": ["Everything - no profile created yet"]
            }
        
        scores = {}
        missing = []
        
        # Personal info (20%)
        personal = career_profile.get("personal_info", {})
        personal_fields = ["name", "email", "phone", "location"]
        personal_filled = sum(1 for f in personal_fields if personal.get(f))
        scores["personal_info"] = (personal_filled / len(personal_fields)) * 100
        if personal_filled < len(personal_fields):
            missing.append(f"Personal info incomplete ({personal_filled}/{len(personal_fields)})")
        
        # Professional summary (15%)
        summary = career_profile.get("professional_summary")
        scores["professional_summary"] = 100 if summary and len(summary) > 50 else 0
        if not summary or len(summary) <= 50:
            missing.append("Professional summary needed")
        
        # Work history (25%)
        work_history = career_profile.get("work_history", [])
        scores["work_history"] = min(len(work_history) * 25, 100)
        if len(work_history) < 2:
            missing.append("Add more work experience")
        
        # Education (15%)
        education = career_profile.get("education", [])
        scores["education"] = min(len(education) * 50, 100)
        if len(education) == 0:
            missing.append("Add education history")
        
        # Skills (15%)
        skills = career_profile.get("skills", [])
        scores["skills"] = min(len(skills) * 10, 100)
        if len(skills) < 5:
            missing.append("Add more skills")
        
        # Projects/Achievements (10%)
        projects = career_profile.get("projects", [])
        achievements = career_profile.get("achievements", [])
        combined = len(projects) + len(achievements)
        scores["projects_achievements"] = min(combined * 25, 100)
        if combined == 0:
            missing.append("Add projects or achievements")
        
        # Calculate weighted overall score
        weights = {
            "personal_info": 0.20,
            "professional_summary": 0.15,
            "work_history": 0.25,
            "education": 0.15,
            "skills": 0.15,
            "projects_achievements": 0.10
        }
        
        overall = sum(scores[k] * weights[k] for k in scores)
        
        return {
            "overall_score": round(overall, 1),
            "sections": {k: round(v, 1) for k, v in scores.items()},
            "missing_fields": missing,
            "status": self._get_completeness_status(overall)
        }
    
    def _get_completeness_status(self, score: float) -> str:
        """Get status label for completeness score"""
        if score >= 90:
            return "Excellent"
        elif score >= 75:
            return "Good"
        elif score >= 50:
            return "Fair"
        elif score >= 25:
            return "Needs Work"
        else:
            return "Just Starting"
    
    async def _generate_ai_context(
        self,
        career_profile: Optional[Dict[str, Any]],
        behavioral_profile: Dict[str, Any],
        engagement_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate AI context summary for personalization
        
        This context is used by AI features to provide personalized recommendations
        """
        context = {
            "career_stage": self._infer_career_stage(career_profile),
            "job_search_intent": self._infer_job_search_intent(behavioral_profile),
            "engagement_level": self._classify_engagement(engagement_metrics),
            "primary_interests": self._extract_interests(career_profile, behavioral_profile),
            "skill_gaps": [],  # TODO: Implement skill gap analysis
            "recommended_features": []  # TODO: Feature recommendations based on usage
        }
        
        return context
    
    def _infer_career_stage(self, career_profile: Optional[Dict[str, Any]]) -> str:
        """Infer career stage from work history"""
        if not career_profile:
            return "entry_level"
        
        work_history = career_profile.get("work_history", [])
        
        if len(work_history) == 0:
            return "entry_level"
        elif len(work_history) <= 2:
            return "early_career"
        elif len(work_history) <= 4:
            return "mid_career"
        else:
            return "senior"
    
    def _infer_job_search_intent(self, behavioral_profile: Dict[str, Any]) -> str:
        """Infer job search intent from behavior"""
        jobs_viewed = len(behavioral_profile.get("jobs_viewed", []))
        jobs_saved = len(behavioral_profile.get("jobs_saved", []))
        jobs_applied = len(behavioral_profile.get("jobs_applied", []))
        
        if jobs_applied > 0:
            return "actively_applying"
        elif jobs_saved > 5:
            return "actively_searching"
        elif jobs_viewed > 10:
            return "casually_browsing"
        else:
            return "not_searching"
    
    def _classify_engagement(self, engagement_metrics: Dict[str, Any]) -> str:
        """Classify engagement level"""
        score = engagement_metrics.get("engagement_score", 0)
        
        if score >= 70:
            return "highly_engaged"
        elif score >= 40:
            return "moderately_engaged"
        elif score >= 20:
            return "lightly_engaged"
        else:
            return "new_user"
    
    def _extract_interests(
        self,
        career_profile: Optional[Dict[str, Any]],
        behavioral_profile: Dict[str, Any]
    ) -> List[str]:
        """Extract primary interests from profile and behavior"""
        interests = []
        
        # From career profile
        if career_profile:
            skills = career_profile.get("skills", [])
            interests.extend(skills[:5])  # Top 5 skills
        
        # From behavior
        preferred_industries = behavioral_profile.get("preferred_industries", [])
        interests.extend(preferred_industries)
        
        return list(set(interests))[:10]  # Top 10 unique interests
    
    async def update_career_profile(
        self,
        user_id: str,
        updates: Dict[str, Any],
        source: str = "manual_edit"
    ) -> Dict[str, Any]:
        """
        Update career profile and emit events
        
        Args:
            user_id: User UUID
            updates: Fields to update
            source: Source of update (manual_edit, ai_suggestion, import, etc.)
            
        Returns:
            Updated profile
        """
        try:
            # Get current profile
            current = await self._get_career_profile(user_id)
            
            if not current:
                # Create new profile
                profile_id = str(uuid4())
                profile_data = {
                    "id": profile_id,
                    "user_id": user_id,
                    **updates,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
                
                result = self.supabase.table(self.career_profiles_table).insert(profile_data).execute()
                
                # Emit profile created event
                event = EventFactory.create_event(
                    "profile_created",
                    user_id=user_id,
                    source="profile_manager",
                    profile_id=profile_id
                )
                await event_store.store_event(event)
                
                return await self._get_career_profile(user_id)
            
            # Update existing profile
            profile_id = current["profile_id"]
            
            # Track what changed
            changed_fields = list(updates.keys())
            old_values = {k: current.get(k) for k in changed_fields if k in current}
            
            # Apply updates
            update_data = {
                **updates,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            self.supabase.table(self.career_profiles_table).update(update_data).eq("id", profile_id).execute()
            
            # Emit profile updated event
            event = EventFactory.create_event(
                "profile_updated",
                user_id=user_id,
                source="profile_manager",
                profile_id=profile_id,
                fields_changed=changed_fields,
                old_values=old_values,
                new_values=updates
            )
            await event_store.store_event(event)
            
            # Note: career_profile_versions will be auto-created by trigger
            
            return await self._get_career_profile(user_id)
            
        except Exception as e:
            print(f"Error updating career profile: {e}")
            raise


# ========================================
# Global Instance
# ========================================

unified_profile_manager = UnifiedProfileManager()
