"""
Job Recommender - AI-powered Job Recommendations

Uses behavioral patterns, memory profile, and semantic matching
to recommend personalized job opportunities.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

from app.services.foundation.events import event_store
from app.services.ai.memory import memory_manager

logger = logging.getLogger(__name__)


class JobRecommendation(Dict):
    """Job recommendation with explanation"""
    pass


class JobRecommender:
    """
    Intelligent job recommendation system.
    
    Learns from:
    - Job views, saves, applications
    - Career preferences and goals
    - Skill profile and gaps
    - Behavioral patterns
    """
    
    def __init__(self):
        self.min_confidence_threshold = 0.3
    
    async def get_personalized_recommendations(
        self,
        user_id: str,
        available_jobs: List[Dict[str, Any]],
        limit: int = 10,
        explain: bool = True
    ) -> List[JobRecommendation]:
        """
        Get personalized job recommendations.
        
        Args:
            user_id: User ID
            available_jobs: Pool of jobs to recommend from
            limit: Maximum recommendations to return
            explain: Include explanation for each recommendation
            
        Returns:
            Ranked list of job recommendations with scores
        """
        
        try:
            # Get complete user context
            context = await memory_manager.get_complete_context(user_id)
            
            # Score each job
            scored_jobs = []
            for job in available_jobs:
                score, explanation = await self._score_job(job, context)
                
                if score >= self.min_confidence_threshold:
                    recommendation = JobRecommendation({
                        "job": job,
                        "score": score,
                        "explanation": explanation if explain else None
                    })
                    scored_jobs.append(recommendation)
            
            # Sort by score descending
            scored_jobs.sort(key=lambda x: x["score"], reverse=True)
            
            logger.info(f"Generated {len(scored_jobs[:limit])} job recommendations for {user_id}")
            return scored_jobs[:limit]
            
        except Exception as e:
            logger.error(f"Error generating job recommendations: {e}")
            return []
    
    async def _score_job(
        self,
        job: Dict[str, Any],
        context: Dict[str, Any]
    ) -> tuple[float, Dict[str, Any]]:
        """
        Score a job for a user based on their context.
        
        Returns: (score, explanation)
        """
        
        score = 0.0
        explanation = {
            "factors": [],
            "match_reasons": [],
            "concerns": []
        }
        
        ltm = context.get("long_term_memory", {})
        if not ltm or "error" in ltm:
            # No memory available, use basic scoring
            return 0.5, {"factors": ["No user profile available"]}
        
        # Extract job attributes
        job_title = job.get("title", "").lower()
        job_industry = job.get("industry", "").lower()
        job_company = job.get("company", "")
        job_location = job.get("location", "")
        job_skills = [s.lower() for s in job.get("required_skills", [])]
        job_salary = job.get("salary")
        job_work_arrangement = job.get("work_arrangement", "").lower()
        job_company_size = job.get("company_size", "").lower()
        
        # Get user preferences
        prefs = ltm.get("career_preferences", {})
        skills = ltm.get("skill_profile", {})
        behavior = ltm.get("behavior_patterns", {})
        goals = ltm.get("career_goals", [])
        
        # 1. Industry match (weight: 0.25)
        preferred_industries = [i.lower() for i in prefs.get("preferred_industries", [])]
        if job_industry in preferred_industries:
            score += 0.25
            explanation["factors"].append("industry_match")
            explanation["match_reasons"].append(f"Matches your interest in {job_industry}")
        
        # 2. Role match (weight: 0.20)
        preferred_roles = [r.lower() for r in prefs.get("preferred_roles", [])]
        role_match = any(role in job_title for role in preferred_roles)
        if role_match:
            score += 0.20
            explanation["factors"].append("role_match")
            explanation["match_reasons"].append("Matches your target roles")
        
        # 3. Skills match (weight: 0.20)
        user_skills = [s.lower() for s in skills.get("technical_skills", [])]
        matching_skills = [s for s in job_skills if s in user_skills]
        skill_match_ratio = len(matching_skills) / len(job_skills) if job_skills else 0
        
        if skill_match_ratio >= 0.7:
            score += 0.20
            explanation["factors"].append("strong_skill_match")
            explanation["match_reasons"].append(f"Strong match: {len(matching_skills)}/{len(job_skills)} skills")
        elif skill_match_ratio >= 0.5:
            score += 0.15
            explanation["factors"].append("good_skill_match")
            explanation["match_reasons"].append(f"Good match: {len(matching_skills)}/{len(job_skills)} skills")
        elif skill_match_ratio >= 0.3:
            score += 0.10
            explanation["factors"].append("partial_skill_match")
        else:
            explanation["concerns"].append("Limited skill overlap - may need learning")
        
        # 4. Career goals alignment (weight: 0.15)
        goals_lower = [g.lower() for g in goals]
        
        if any("senior" in g for g in goals_lower) and "senior" in job_title:
            score += 0.10
            explanation["factors"].append("seniority_goal_match")
            explanation["match_reasons"].append("Aligns with advancement goals")
        
        if any("management" in g or "lead" in g for g in goals_lower) and ("manager" in job_title or "lead" in job_title):
            score += 0.10
            explanation["factors"].append("leadership_goal_match")
            explanation["match_reasons"].append("Aligns with leadership goals")
        
        if any("skills" in g for g in goals_lower):
            # Check if job offers learning opportunities
            missing_skills = [s for s in job_skills if s not in user_skills]
            if missing_skills and len(missing_skills) <= 3:
                score += 0.05
                explanation["factors"].append("learning_opportunity")
                explanation["match_reasons"].append("Offers skill development opportunities")
        
        # 5. Work preferences (weight: 0.10)
        if job_work_arrangement and prefs.get("work_arrangement"):
            if job_work_arrangement == prefs["work_arrangement"].lower():
                score += 0.05
                explanation["factors"].append("work_arrangement_match")
                explanation["match_reasons"].append(f"Matches {job_work_arrangement} preference")
        
        if job_company_size and prefs.get("company_size"):
            if job_company_size == prefs["company_size"].lower():
                score += 0.05
                explanation["factors"].append("company_size_match")
        
        # 6. Location match (weight: 0.05)
        preferred_locations = [l.lower() for l in prefs.get("preferred_locations", [])]
        if job_location and any(loc in job_location.lower() for loc in preferred_locations):
            score += 0.05
            explanation["factors"].append("location_match")
            explanation["match_reasons"].append("Preferred location")
        
        # 7. Salary match (weight: 0.05)
        salary_range = prefs.get("salary_range")
        if job_salary and salary_range:
            if salary_range["min"] <= job_salary <= salary_range["max"]:
                score += 0.05
                explanation["factors"].append("salary_match")
            elif job_salary < salary_range["min"]:
                explanation["concerns"].append("Below salary expectations")
        
        # Bonus: Company match
        preferred_companies = [c.lower() for c in prefs.get("preferred_companies", [])]
        if job_company and any(comp in job_company.lower() for comp in preferred_companies):
            score += 0.05
            explanation["factors"].append("company_match")
            explanation["match_reasons"].append("Target company")
        
        # Adjust based on behavior patterns
        job_search_intensity = behavior.get("job_search_intensity", "casual")
        if job_search_intensity == "urgent":
            # Boost recommendations slightly for urgent seekers
            score *= 1.1
            score = min(1.0, score)  # Cap at 1.0
        
        # Normalize score to 0-1
        score = max(0.0, min(1.0, score))
        
        return score, explanation
    
    async def explain_recommendation(
        self,
        user_id: str,
        job: Dict[str, Any]
    ) -> str:
        """
        Generate natural language explanation for why a job is recommended.
        """
        
        context = await memory_manager.get_complete_context(user_id)
        score, explanation = await self._score_job(job, context)
        
        if not explanation["match_reasons"]:
            return "This job matches your profile."
        
        # Build explanation text
        text = f"Match score: {score:.0%}\n\n"
        text += "Why this job is recommended:\n"
        for reason in explanation["match_reasons"]:
            text += f"✓ {reason}\n"
        
        if explanation["concerns"]:
            text += "\nConsiderations:\n"
            for concern in explanation["concerns"]:
                text += f"⚠ {concern}\n"
        
        return text
    
    async def get_similar_jobs(
        self,
        user_id: str,
        reference_job: Dict[str, Any],
        available_jobs: List[Dict[str, Any]],
        limit: int = 5
    ) -> List[JobRecommendation]:
        """
        Get jobs similar to a reference job (e.g., user viewed/saved).
        
        Uses job attributes for similarity matching.
        """
        
        similar_jobs = []
        
        ref_industry = reference_job.get("industry", "").lower()
        ref_title = reference_job.get("title", "").lower()
        ref_skills = set(s.lower() for s in reference_job.get("required_skills", []))
        
        for job in available_jobs:
            if job.get("id") == reference_job.get("id"):
                continue  # Skip the reference job itself
            
            similarity_score = 0.0
            
            # Industry match
            if job.get("industry", "").lower() == ref_industry:
                similarity_score += 0.4
            
            # Title similarity (simple keyword overlap)
            job_title_words = set(job.get("title", "").lower().split())
            ref_title_words = set(ref_title.split())
            title_overlap = len(job_title_words & ref_title_words) / max(len(ref_title_words), 1)
            similarity_score += title_overlap * 0.3
            
            # Skills similarity
            job_skills = set(s.lower() for s in job.get("required_skills", []))
            skill_overlap = len(job_skills & ref_skills) / max(len(ref_skills), 1) if ref_skills else 0
            similarity_score += skill_overlap * 0.3
            
            if similarity_score >= 0.4:  # Threshold for similarity
                similar_jobs.append(JobRecommendation({
                    "job": job,
                    "score": similarity_score,
                    "explanation": {
                        "similarity_reason": f"Similar to {reference_job.get('title')} at {reference_job.get('company')}"
                    }
                }))
        
        # Sort by similarity
        similar_jobs.sort(key=lambda x: x["score"], reverse=True)
        
        return similar_jobs[:limit]
