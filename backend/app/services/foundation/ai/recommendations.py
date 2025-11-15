"""
AI-Powered Job Recommendation Engine

Uses learned patterns from memory layer to generate personalized recommendations.
Goes beyond simple matching to understand:
- What jobs user actually clicks on vs. skills listed
- Success patterns from applied/saved jobs
- Career trajectory and growth potential
- Engagement signals (time spent, repeat views)
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from uuid import uuid4

from loguru import logger
import google.generativeai as genai

from app.core.config import settings
from app.db.supabase import get_supabase_client
from ..events.event_store import event_store
from .memory import ai_memory


class JobRecommendation:
    """Single job recommendation with reasoning"""
    
    def __init__(
        self,
        job_id: str,
        recommendation_score: float,  # 0-100
        match_reasons: List[str],
        growth_potential: str,
        confidence: float,  # 0-1
        metadata: Dict[str, Any]
    ):
        self.job_id = job_id
        self.recommendation_score = recommendation_score
        self.match_reasons = match_reasons
        self.growth_potential = growth_potential
        self.confidence = confidence
        self.metadata = metadata


class RecommendationEngine:
    """
    AI-powered job recommendation system
    
    Recommendation Algorithm:
    1. Get user's behavior patterns from memory
    2. Score jobs based on:
       - Skill match (30%)
       - Behavioral signals (25%) - what they actually view/save
       - Career goal alignment (20%)
       - Growth potential (15%)
       - Engagement prediction (10%)
    3. Filter out already seen/applied jobs
    4. Return top N with explanations
    """
    
    def __init__(self):
        self.supabase = get_supabase_client()
        
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel("gemini-pro")
        else:
            logger.warning("GEMINI_API_KEY not set - recommendations will be rule-based only")
            self.model = None
    
    async def get_recommendations(
        self,
        user_id: str,
        limit: int = 10,
        include_stretch: bool = True
    ) -> List[JobRecommendation]:
        """
        Generate personalized job recommendations
        
        Args:
            user_id: User identifier
            limit: Number of recommendations
            include_stretch: Include challenging roles user might grow into
        
        Returns:
            List of recommendations sorted by score
        """
        try:
            logger.info(f"Generating recommendations for user {user_id}")
            
            # Get user context from AI memory
            context = await ai_memory.get_user_context(user_id)
            
            if not context.get("ai_ready", False):
                logger.info("Insufficient memory, using cold-start recommendations")
                return await self._cold_start_recommendations(user_id, limit)
            
            # Get user's profile
            profile = await self._get_user_profile(user_id)
            
            # Get candidate jobs
            candidate_jobs = await self._get_candidate_jobs(user_id)
            
            if not candidate_jobs:
                logger.warning(f"No candidate jobs found for user {user_id}")
                return []
            
            # Score each job
            scored_jobs = []
            for job in candidate_jobs:
                score = await self._score_job(
                    user_id=user_id,
                    job=job,
                    context=context,
                    profile=profile
                )
                if score:
                    scored_jobs.append(score)
            
            # Sort by recommendation score
            scored_jobs.sort(key=lambda x: x.recommendation_score, reverse=True)
            
            # Filter stretch goals if needed
            if not include_stretch:
                scored_jobs = [j for j in scored_jobs if j.metadata.get("is_stretch", False) == False]
            
            recommendations = scored_jobs[:limit]
            
            logger.info(f"Generated {len(recommendations)} recommendations")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return []
    
    async def _score_job(
        self,
        user_id: str,
        job: Dict[str, Any],
        context: Dict[str, Any],
        profile: Dict[str, Any]
    ) -> Optional[JobRecommendation]:
        """
        Score single job against user profile and behavior
        
        Returns JobRecommendation or None if not suitable
        """
        try:
            job_id = job.get("id", "")
            job_title = job.get("title", "")
            job_skills = job.get("required_skills", [])
            job_description = job.get("description", "")
            
            # Component scores
            skill_score = self._calculate_skill_match(profile, job_skills)
            behavioral_score = await self._calculate_behavioral_match(user_id, job, context)
            goal_alignment = self._calculate_goal_alignment(context, job)
            growth_score = self._calculate_growth_potential(profile, job)
            engagement_score = self._predict_engagement(context, job)
            
            # Weighted total
            total_score = (
                skill_score * 0.30 +
                behavioral_score * 0.25 +
                goal_alignment * 0.20 +
                growth_score * 0.15 +
                engagement_score * 0.10
            )
            
            # Generate explanations
            reasons = []
            
            if skill_score >= 70:
                reasons.append(f"Strong skill match ({int(skill_score)}%)")
            elif skill_score >= 50:
                reasons.append(f"Good skill foundation ({int(skill_score)}%)")
            
            if behavioral_score >= 70:
                reasons.append("Similar to jobs you've shown interest in")
            
            if goal_alignment >= 70:
                reasons.append("Aligns with your career goals")
            
            if growth_score >= 70:
                reasons.append("Excellent growth opportunity")
            
            # Generate growth potential text
            growth_text = self._generate_growth_text(growth_score, skill_score)
            
            # Calculate confidence
            confidence = self._calculate_confidence(
                skill_score, behavioral_score, context
            )
            
            # Determine if stretch role
            is_stretch = skill_score < 60 and growth_score > 70
            
            recommendation = JobRecommendation(
                job_id=job_id,
                recommendation_score=total_score,
                match_reasons=reasons,
                growth_potential=growth_text,
                confidence=confidence,
                metadata={
                    "job_title": job_title,
                    "component_scores": {
                        "skill": skill_score,
                        "behavioral": behavioral_score,
                        "goal": goal_alignment,
                        "growth": growth_score,
                        "engagement": engagement_score
                    },
                    "is_stretch": is_stretch,
                    "recommended_at": datetime.utcnow().isoformat()
                }
            )
            
            return recommendation
            
        except Exception as e:
            logger.error(f"Error scoring job: {e}")
            return None
    
    def _calculate_skill_match(
        self,
        profile: Dict[str, Any],
        job_skills: List[str]
    ) -> float:
        """Calculate skill overlap (0-100)"""
        
        user_skills = set(s.lower() for s in profile.get("skills", []))
        required_skills = set(s.lower() for s in job_skills)
        
        if not required_skills:
            return 50.0  # Neutral if no requirements specified
        
        matched = user_skills.intersection(required_skills)
        match_ratio = len(matched) / len(required_skills)
        
        return min(100.0, match_ratio * 120)  # Boost score for strong matches
    
    async def _calculate_behavioral_match(
        self,
        user_id: str,
        job: Dict[str, Any],
        context: Dict[str, Any]
    ) -> float:
        """
        Analyze if job is similar to what user actually engages with
        
        Uses memory to find patterns in viewed/saved jobs
        """
        try:
            # Get job preferences from memory
            job_prefs = context.get("context", {}).get("job_preferences", [])
            
            if not job_prefs:
                return 50.0  # Neutral
            
            # Extract patterns from memory
            job_title = job.get("title", "").lower()
            job_company = job.get("company", "").lower()
            
            # Simple keyword matching for now
            # (In production: use embedding similarity)
            score = 50.0
            
            for pref in job_prefs:
                pref_lower = pref.lower()
                
                # Check if similar titles mentioned
                if any(word in pref_lower for word in job_title.split()):
                    score += 15
                
                # Check if company type mentioned
                if job_company and job_company in pref_lower:
                    score += 10
            
            return min(100.0, score)
            
        except Exception as e:
            logger.error(f"Error calculating behavioral match: {e}")
            return 50.0
    
    def _calculate_goal_alignment(
        self,
        context: Dict[str, Any],
        job: Dict[str, Any]
    ) -> float:
        """Check if job aligns with stated career goals"""
        
        career_goals = context.get("context", {}).get("career_goals", [])
        
        if not career_goals:
            return 50.0
        
        job_title = job.get("title", "").lower()
        job_desc = job.get("description", "").lower()
        
        score = 50.0
        
        for goal in career_goals:
            goal_lower = goal.lower()
            
            # Check for goal keywords in job
            goal_words = goal_lower.split()
            matches = sum(1 for word in goal_words if word in job_title or word in job_desc)
            
            if matches > 0:
                score += (matches / len(goal_words)) * 50
        
        return min(100.0, score)
    
    def _calculate_growth_potential(
        self,
        profile: Dict[str, Any],
        job: Dict[str, Any]
    ) -> float:
        """
        Assess learning opportunities
        
        Higher score for jobs that stretch skills without being unreachable
        """
        user_skills = set(s.lower() for s in profile.get("skills", []))
        job_skills = set(s.lower() for s in job.get("required_skills", []))
        
        if not job_skills:
            return 50.0
        
        matched = user_skills.intersection(job_skills)
        new_skills = job_skills - user_skills
        
        match_ratio = len(matched) / len(job_skills) if job_skills else 0
        new_skill_ratio = len(new_skills) / len(job_skills) if job_skills else 0
        
        # Sweet spot: 40-70% match = good growth
        if 0.4 <= match_ratio <= 0.7:
            growth_score = 80.0 + (new_skill_ratio * 20)
        elif match_ratio < 0.4:
            growth_score = 40.0  # Too much stretch
        else:
            growth_score = 60.0  # Limited growth
        
        return growth_score
    
    def _predict_engagement(
        self,
        context: Dict[str, Any],
        job: Dict[str, Any]
    ) -> float:
        """
        Predict if user will engage with this recommendation
        
        Based on historical interaction patterns
        """
        interaction_patterns = context.get("context", {}).get("interaction_patterns", [])
        
        if not interaction_patterns:
            return 50.0
        
        # Check if user is active (proxy: has interaction memories)
        if len(interaction_patterns) > 0:
            return 75.0  # Engaged user
        else:
            return 50.0  # Neutral
    
    def _generate_growth_text(self, growth_score: float, skill_score: float) -> str:
        """Generate human-readable growth potential description"""
        
        if growth_score >= 80 and skill_score >= 60:
            return "Excellent learning opportunity with strong foundation"
        elif growth_score >= 80:
            return "Significant growth potential - consider upskilling first"
        elif growth_score >= 60:
            return "Moderate growth opportunity"
        else:
            return "May not challenge your current skill set"
    
    def _calculate_confidence(
        self,
        skill_score: float,
        behavioral_score: float,
        context: Dict[str, Any]
    ) -> float:
        """
        How confident are we in this recommendation?
        
        Higher confidence with more data and clearer signals
        """
        memory_count = context.get("memory_count", 0)
        
        # Base confidence from data availability
        data_confidence = min(1.0, memory_count / 10.0)
        
        # Signal strength
        signal_strength = (skill_score + behavioral_score) / 200.0
        
        # Combined
        confidence = (data_confidence * 0.6) + (signal_strength * 0.4)
        
        return confidence
    
    async def _get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Fetch user profile from database"""
        
        try:
            response = self.supabase.table("career_profiles") \
                .select("*") \
                .eq("user_id", user_id) \
                .single() \
                .execute()
            
            if response.data:
                return response.data.get("profile_data", {})
            else:
                return {}
                
        except Exception as e:
            logger.error(f"Error fetching profile: {e}")
            return {}
    
    async def _get_candidate_jobs(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get pool of jobs to recommend from
        
        Filters out already seen/applied jobs
        """
        try:
            # Get jobs user has already interacted with
            seen_jobs = await self._get_seen_jobs(user_id)
            
            # Get active jobs
            response = self.supabase.table("jobs") \
                .select("*") \
                .eq("status", "active") \
                .limit(100) \
                .execute()
            
            jobs = response.data if response.data else []
            
            # Filter out seen jobs
            candidates = [j for j in jobs if j.get("id") not in seen_jobs]
            
            return candidates
            
        except Exception as e:
            logger.error(f"Error fetching candidate jobs: {e}")
            return []
    
    async def _get_seen_jobs(self, user_id: str) -> set:
        """Get IDs of jobs user has already viewed/applied to"""
        
        try:
            events = await event_store.get_events_by_user(
                user_id=user_id,
                category="JOB",
                limit=500
            )
            
            seen = set()
            for event in events:
                job_id = event.get("event_data", {}).get("job_id")
                if job_id:
                    seen.add(job_id)
            
            return seen
            
        except Exception as e:
            logger.error(f"Error getting seen jobs: {e}")
            return set()
    
    async def _cold_start_recommendations(
        self,
        user_id: str,
        limit: int
    ) -> List[JobRecommendation]:
        """
        Fallback recommendations for new users with no behavior history
        
        Uses only profile data
        """
        logger.info("Generating cold-start recommendations")
        
        try:
            profile = await self._get_user_profile(user_id)
            
            if not profile:
                return []
            
            # Get recent jobs
            response = self.supabase.table("jobs") \
                .select("*") \
                .eq("status", "active") \
                .order("created_at", desc=True) \
                .limit(50) \
                .execute()
            
            jobs = response.data if response.data else []
            
            # Simple skill-based matching
            recommendations = []
            for job in jobs[:limit]:
                skill_score = self._calculate_skill_match(profile, job.get("required_skills", []))
                
                if skill_score >= 40:  # Lower threshold for cold start
                    recommendations.append(JobRecommendation(
                        job_id=job.get("id", ""),
                        recommendation_score=skill_score,
                        match_reasons=["Based on your skills"],
                        growth_potential="Complete your profile for better recommendations",
                        confidence=0.5,
                        metadata={
                            "job_title": job.get("title", ""),
                            "is_cold_start": True
                        }
                    ))
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error in cold-start recommendations: {e}")
            return []


# Global instance
recommendation_engine = RecommendationEngine()
