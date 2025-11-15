"""
Long-Term Memory - Persistent User Knowledge

Learns from historical events to build comprehensive user profiles including:
- Career preferences and patterns
- Job search behavior
- Skills and competencies  
- Learning preferences
- Interaction patterns
- Success indicators
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from collections import Counter
import logging

from app.services.foundation.events import event_store, event_analytics
from app.services.foundation.profile import unified_profile_manager

logger = logging.getLogger(__name__)


class CareerPreferences(BaseModel):
    """Learned career preferences from user behavior"""
    preferred_industries: List[str] = Field(default_factory=list)
    preferred_roles: List[str] = Field(default_factory=list)
    preferred_companies: List[str] = Field(default_factory=list)
    preferred_locations: List[str] = Field(default_factory=list)
    salary_range: Optional[Dict[str, int]] = None
    work_arrangement: Optional[str] = None  # remote, hybrid, onsite
    company_size: Optional[str] = None  # startup, mid, enterprise
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)


class SkillProfile(BaseModel):
    """Learned skills and competencies"""
    technical_skills: List[str] = Field(default_factory=list)
    soft_skills: List[str] = Field(default_factory=list)
    skill_gaps: List[str] = Field(default_factory=list)
    learning_interests: List[str] = Field(default_factory=list)
    proficiency_levels: Dict[str, str] = Field(default_factory=dict)  # skill -> level


class BehaviorPatterns(BaseModel):
    """Learned behavior patterns"""
    most_active_times: List[str] = Field(default_factory=list)  # hours of day
    preferred_features: List[str] = Field(default_factory=list)
    typical_session_duration: Optional[int] = None  # minutes
    engagement_level: str = "medium"  # low, medium, high
    job_search_intensity: str = "casual"  # casual, active, urgent
    response_to_nudges: str = "neutral"  # positive, neutral, negative


class UserMemoryProfile(BaseModel):
    """Complete long-term memory profile for a user"""
    user_id: str
    career_preferences: CareerPreferences = Field(default_factory=CareerPreferences)
    skill_profile: SkillProfile = Field(default_factory=SkillProfile)
    behavior_patterns: BehaviorPatterns = Field(default_factory=BehaviorPatterns)
    career_goals: List[str] = Field(default_factory=list)
    pain_points: List[str] = Field(default_factory=list)
    success_indicators: Dict[str, Any] = Field(default_factory=dict)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)


class LongTermMemory:
    """
    Long-term memory system that learns from user events.
    
    Analyzes historical events to build persistent knowledge about users
    that AI agents can use for personalization.
    """
    
    def __init__(self):
        self.cache: Dict[str, UserMemoryProfile] = {}
        self.cache_ttl = timedelta(hours=1)
        self.min_events_for_learning = 20
    
    async def get_user_memory(
        self,
        user_id: str,
        force_refresh: bool = False
    ) -> UserMemoryProfile:
        """
        Get complete long-term memory profile for a user.
        
        Args:
            user_id: User ID
            force_refresh: Force rebuild from events
            
        Returns:
            UserMemoryProfile with learned knowledge
        """
        try:
            # Check cache
            if not force_refresh and user_id in self.cache:
                profile = self.cache[user_id]
                if datetime.utcnow() - profile.last_updated < self.cache_ttl:
                    return profile
            
            # Build memory profile from events
            profile = await self._build_memory_profile(user_id)
            
            # Cache it
            self.cache[user_id] = profile
            
            logger.info(f"Built memory profile for {user_id}: confidence={profile.confidence_score:.2f}")
            return profile
            
        except Exception as e:
            logger.error(f"Error getting user memory for {user_id}: {e}")
            # Return empty profile on error
            return UserMemoryProfile(user_id=user_id)
    
    async def _build_memory_profile(self, user_id: str) -> UserMemoryProfile:
        """Build memory profile by analyzing user events"""
        
        # Get historical events (last 90 days)
        start_date = datetime.utcnow() - timedelta(days=90)
        events = await event_store.get_events_by_user(
            user_id=user_id,
            start_date=start_date,
            limit=1000
        )
        
        # Get unified profile for current state
        unified_profile = await unified_profile_manager.get_unified_profile(user_id)
        
        # Not enough data yet
        if len(events) < self.min_events_for_learning:
            return UserMemoryProfile(
                user_id=user_id,
                confidence_score=len(events) / self.min_events_for_learning
            )
        
        # Learn from different event types
        career_prefs = await self._learn_career_preferences(events)
        skill_prof = await self._learn_skill_profile(events, unified_profile)
        behavior = await self._learn_behavior_patterns(events, unified_profile)
        goals = await self._infer_career_goals(events, unified_profile)
        pain_points = await self._identify_pain_points(events, unified_profile)
        
        # Calculate overall confidence based on data quality
        confidence = self._calculate_confidence(events, unified_profile)
        
        return UserMemoryProfile(
            user_id=user_id,
            career_preferences=career_prefs,
            skill_profile=skill_prof,
            behavior_patterns=behavior,
            career_goals=goals,
            pain_points=pain_points,
            confidence_score=confidence,
            last_updated=datetime.utcnow()
        )
    
    async def _learn_career_preferences(self, events: List[Dict]) -> CareerPreferences:
        """Learn career preferences from job-related events"""
        
        job_events = [e for e in events if e.get("category") == "JOB"]
        
        if not job_events:
            return CareerPreferences()
        
        # Extract patterns from job views/saves/applies
        industries = []
        roles = []
        companies = []
        locations = []
        salaries = []
        work_arrangements = []
        company_sizes = []
        
        for event in job_events:
            data = event.get("event_data", {})
            
            if "industry" in data:
                industries.append(data["industry"])
            if "job_title" in data:
                roles.append(data["job_title"])
            if "company" in data:
                companies.append(data["company"])
            if "location" in data:
                locations.append(data["location"])
            if "salary" in data:
                salaries.append(data["salary"])
            if "work_arrangement" in data:
                work_arrangements.append(data["work_arrangement"])
            if "company_size" in data:
                company_sizes.append(data["company_size"])
        
        # Find most common preferences
        top_industries = [item for item, _ in Counter(industries).most_common(5)]
        top_roles = [item for item, _ in Counter(roles).most_common(5)]
        top_companies = [item for item, _ in Counter(companies).most_common(5)]
        top_locations = [item for item, _ in Counter(locations).most_common(3)]
        
        # Calculate salary range
        salary_range = None
        if salaries:
            salary_range = {
                "min": min(salaries),
                "max": max(salaries),
                "median": sorted(salaries)[len(salaries) // 2]
            }
        
        # Most preferred work arrangement
        work_arrangement = Counter(work_arrangements).most_common(1)[0][0] if work_arrangements else None
        company_size = Counter(company_sizes).most_common(1)[0][0] if company_sizes else None
        
        # Confidence based on number of interactions
        confidence = min(1.0, len(job_events) / 50)
        
        return CareerPreferences(
            preferred_industries=top_industries,
            preferred_roles=top_roles,
            preferred_companies=top_companies,
            preferred_locations=top_locations,
            salary_range=salary_range,
            work_arrangement=work_arrangement,
            company_size=company_size,
            confidence_score=confidence
        )
    
    async def _learn_skill_profile(
        self,
        events: List[Dict],
        unified_profile: Dict
    ) -> SkillProfile:
        """Learn skills from profile and behavior"""
        
        # Get skills from profile
        profile_data = unified_profile.get("profile", {})
        technical_skills = profile_data.get("technical_skills", [])
        soft_skills = profile_data.get("soft_skills", [])
        
        # Infer learning interests from course views and content interactions
        learning_events = [
            e for e in events 
            if e.get("event_type") in ["course_viewed", "article_read", "skill_test_taken"]
        ]
        
        learning_interests = []
        for event in learning_events:
            data = event.get("event_data", {})
            if "skill" in data:
                learning_interests.append(data["skill"])
            if "topic" in data:
                learning_interests.append(data["topic"])
        
        top_interests = [item for item, _ in Counter(learning_interests).most_common(10)]
        
        # Identify skill gaps (interests not in current skills)
        all_current_skills = set(technical_skills + soft_skills)
        skill_gaps = [skill for skill in top_interests if skill not in all_current_skills]
        
        return SkillProfile(
            technical_skills=technical_skills,
            soft_skills=soft_skills,
            skill_gaps=skill_gaps[:5],  # Top 5 gaps
            learning_interests=top_interests
        )
    
    async def _learn_behavior_patterns(
        self,
        events: List[Dict],
        unified_profile: Dict
    ) -> BehaviorPatterns:
        """Learn behavior patterns from event timing and engagement"""
        
        # Extract event hours
        event_hours = []
        for event in events:
            if "timestamp" in event:
                hour = datetime.fromisoformat(event["timestamp"].replace("Z", "+00:00")).hour
                event_hours.append(hour)
        
        # Most active times (hours)
        top_hours = [str(h) for h, _ in Counter(event_hours).most_common(3)]
        
        # Get engagement metrics
        behavior = unified_profile.get("behavior", {})
        engagement_score = unified_profile.get("engagement", {}).get("engagement_score", 50)
        
        # Determine engagement level
        if engagement_score >= 70:
            engagement_level = "high"
        elif engagement_score >= 40:
            engagement_level = "medium"
        else:
            engagement_level = "low"
        
        # Determine job search intensity from job interactions
        job_events = [e for e in events if e.get("category") == "JOB"]
        job_applications = behavior.get("jobs_applied", 0)
        
        if job_applications > 10 or len(job_events) > 100:
            intensity = "urgent"
        elif job_applications > 3 or len(job_events) > 30:
            intensity = "active"
        else:
            intensity = "casual"
        
        # Preferred features from usage
        feature_usage = {}
        for event in events:
            source = event.get("source", "unknown")
            feature_usage[source] = feature_usage.get(source, 0) + 1
        
        top_features = [feat for feat, _ in sorted(feature_usage.items(), key=lambda x: x[1], reverse=True)[:5]]
        
        return BehaviorPatterns(
            most_active_times=top_hours,
            preferred_features=top_features,
            engagement_level=engagement_level,
            job_search_intensity=intensity
        )
    
    async def _infer_career_goals(
        self,
        events: List[Dict],
        unified_profile: Dict
    ) -> List[str]:
        """Infer career goals from behavior and profile"""
        
        goals = []
        
        # From profile if available
        profile_data = unified_profile.get("profile", {})
        if "career_goals" in profile_data:
            goals.extend(profile_data["career_goals"])
        
        # Infer from job search behavior
        job_events = [e for e in events if e.get("category") == "JOB"]
        
        # Check for career transitions
        current_title = profile_data.get("current_title", "")
        viewed_titles = [e.get("event_data", {}).get("job_title", "") for e in job_events]
        
        if viewed_titles and current_title:
            # If viewing senior roles → goal: "advance to senior position"
            if any("senior" in t.lower() for t in viewed_titles) and "senior" not in current_title.lower():
                goals.append("Advance to senior-level position")
            
            # If viewing management → goal: "transition to management"
            if any("manager" in t.lower() or "lead" in t.lower() for t in viewed_titles):
                goals.append("Transition into management")
        
        # Check for skill development
        learning_events = [e for e in events if "course" in e.get("event_type", "").lower()]
        if len(learning_events) > 5:
            goals.append("Develop new technical skills")
        
        # Check for industry change
        industries = [e.get("event_data", {}).get("industry") for e in job_events if "industry" in e.get("event_data", {})]
        current_industry = profile_data.get("industry")
        if industries and current_industry and any(ind != current_industry for ind in industries):
            goals.append("Explore new industries")
        
        return list(set(goals))  # Deduplicate
    
    async def _identify_pain_points(
        self,
        events: List[Dict],
        unified_profile: Dict
    ) -> List[str]:
        """Identify user pain points from behavior"""
        
        pain_points = []
        
        behavior = unified_profile.get("behavior", {})
        
        # High views but low applications → confidence issue
        if behavior.get("jobs_viewed", 0) > 30 and behavior.get("jobs_applied", 0) < 3:
            pain_points.append("Difficulty applying to jobs (may lack confidence)")
        
        # Low profile completeness
        completeness = unified_profile.get("completeness", {}).get("overall_score", 100)
        if completeness < 50:
            pain_points.append("Incomplete profile limiting opportunities")
        
        # No recent activity → disengaged
        recent_events = [e for e in events if (datetime.utcnow() - datetime.fromisoformat(e["timestamp"].replace("Z", "+00:00"))).days < 7]
        if len(recent_events) < 3:
            pain_points.append("Low engagement - may need motivation")
        
        # Browsing but not saving → decision paralysis
        saves = behavior.get("jobs_saved", 0)
        views = behavior.get("jobs_viewed", 0)
        if views > 20 and saves < 3:
            pain_points.append("Difficulty deciding on suitable opportunities")
        
        return pain_points
    
    def _calculate_confidence(
        self,
        events: List[Dict],
        unified_profile: Dict
    ) -> float:
        """Calculate confidence score for memory profile"""
        
        factors = []
        
        # Event count (0-30 points)
        event_score = min(30, len(events) / 10)
        factors.append(event_score)
        
        # Profile completeness (0-30 points)
        completeness = unified_profile.get("completeness", {}).get("overall_score", 0)
        factors.append(completeness * 0.3)
        
        # Recent activity (0-20 points)
        recent_events = [
            e for e in events 
            if (datetime.utcnow() - datetime.fromisoformat(e["timestamp"].replace("Z", "+00:00"))).days < 14
        ]
        recent_score = min(20, len(recent_events) / 2)
        factors.append(recent_score)
        
        # Diversity of interactions (0-20 points)
        unique_event_types = len(set(e.get("event_type") for e in events))
        diversity_score = min(20, unique_event_types * 2)
        factors.append(diversity_score)
        
        return min(1.0, sum(factors) / 100)
    
    async def update_memory_insight(
        self,
        user_id: str,
        insight_type: str,
        insight_data: Dict[str, Any]
    ) -> bool:
        """
        Manually add an insight to user memory.
        
        Useful for agents to record important discoveries.
        """
        try:
            # Get current memory
            memory = await self.get_user_memory(user_id)
            
            # Update based on insight type
            if insight_type == "career_goal":
                if insight_data["goal"] not in memory.career_goals:
                    memory.career_goals.append(insight_data["goal"])
            
            elif insight_type == "pain_point":
                if insight_data["pain_point"] not in memory.pain_points:
                    memory.pain_points.append(insight_data["pain_point"])
            
            elif insight_type == "skill_gap":
                if insight_data["skill"] not in memory.skill_profile.skill_gaps:
                    memory.skill_profile.skill_gaps.append(insight_data["skill"])
            
            # Update cache
            memory.last_updated = datetime.utcnow()
            self.cache[user_id] = memory
            
            logger.info(f"Added {insight_type} insight for {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating memory insight: {e}")
            return False
    
    def clear_cache(self):
        """Clear memory cache"""
        self.cache.clear()
        logger.info("Cleared long-term memory cache")
