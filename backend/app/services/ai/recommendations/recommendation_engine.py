"""
Recommendation Engine - Unified Interface for All Recommendations

Provides single entry point for job, skill, and learning recommendations.
"""

from typing import Dict, List, Optional, Any
import logging

from .job_recommender import JobRecommender
from .skill_recommender import SkillRecommender
from .learning_recommender import LearningRecommender

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """
    Unified recommendation engine combining all recommendation types.
    
    Provides intelligent, personalized recommendations across:
    - Jobs
    - Skills
    - Learning resources
    """
    
    def __init__(self):
        self.job_recommender = JobRecommender()
        self.skill_recommender = SkillRecommender()
        self.learning_recommender = LearningRecommender()
        logger.info("Recommendation engine initialized")
    
    # ==================== Job Recommendations ====================
    
    async def recommend_jobs(
        self,
        user_id: str,
        available_jobs: List[Dict[str, Any]],
        limit: int = 10,
        explain: bool = True
    ) -> List[Dict]:
        """Get personalized job recommendations"""
        return await self.job_recommender.get_personalized_recommendations(
            user_id,
            available_jobs,
            limit,
            explain
        )
    
    async def recommend_similar_jobs(
        self,
        user_id: str,
        reference_job: Dict[str, Any],
        available_jobs: List[Dict[str, Any]],
        limit: int = 5
    ) -> List[Dict]:
        """Get jobs similar to a reference job"""
        return await self.job_recommender.get_similar_jobs(
            user_id,
            reference_job,
            available_jobs,
            limit
        )
    
    async def explain_job_recommendation(
        self,
        user_id: str,
        job: Dict[str, Any]
    ) -> str:
        """Get natural language explanation for job recommendation"""
        return await self.job_recommender.explain_recommendation(user_id, job)
    
    # ==================== Skill Recommendations ====================
    
    async def recommend_skills(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict]:
        """Get personalized skill development recommendations"""
        return await self.skill_recommender.get_skill_recommendations(user_id, limit)
    
    async def get_skill_learning_path(
        self,
        user_id: str,
        target_skill: str
    ) -> Dict[str, Any]:
        """Get learning path for a specific skill"""
        return await self.skill_recommender.get_skill_learning_path(user_id, target_skill)
    
    # ==================== Learning Recommendations ====================
    
    async def recommend_learning_resources(
        self,
        user_id: str,
        resource_pool: Optional[List[Dict]] = None,
        limit: int = 10
    ) -> List[Dict]:
        """Get personalized learning resource recommendations"""
        return await self.learning_recommender.get_learning_recommendations(
            user_id,
            resource_pool,
            limit
        )
    
    async def get_learning_path_for_goal(
        self,
        user_id: str,
        goal: str
    ) -> Dict[str, Any]:
        """Get structured learning path for a career goal"""
        return await self.learning_recommender.get_learning_path_for_goal(user_id, goal)
    
    # ==================== Combined Recommendations ====================
    
    async def get_complete_recommendations(
        self,
        user_id: str,
        available_jobs: Optional[List[Dict]] = None,
        available_resources: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Get complete recommendation package for user.
        
        Returns jobs, skills, and learning recommendations in one call.
        """
        
        try:
            recommendations = {
                "user_id": user_id,
                "jobs": [],
                "skills": [],
                "learning": []
            }
            
            # Get job recommendations if jobs provided
            if available_jobs:
                recommendations["jobs"] = await self.recommend_jobs(
                    user_id,
                    available_jobs,
                    limit=5
                )
            
            # Get skill recommendations
            recommendations["skills"] = await self.recommend_skills(user_id, limit=5)
            
            # Get learning recommendations
            recommendations["learning"] = await self.recommend_learning_resources(
                user_id,
                available_resources,
                limit=5
            )
            
            logger.info(f"Generated complete recommendations for {user_id}")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating complete recommendations: {e}")
            return {
                "user_id": user_id,
                "error": str(e)
            }
    
    async def get_dashboard_recommendations(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Get recommendations optimized for dashboard display.
        
        Returns curated, high-priority recommendations.
        """
        
        return {
            "top_skills_to_learn": await self.recommend_skills(user_id, limit=3),
            "next_learning_steps": await self.recommend_learning_resources(user_id, limit=3)
        }
