"""
Learning Recommender - Personalized Course and Content Recommendations

Recommends courses, articles, and learning resources based on
skill gaps and learning interests.
"""

from typing import Dict, List, Optional, Any
import logging

from app.services.ai.memory import memory_manager

logger = logging.getLogger(__name__)


class LearningRecommendation(Dict):
    """Learning resource recommendation"""
    pass


class LearningRecommender:
    """
    Intelligent learning resource recommendation system.
    
    Recommends:
    - Online courses
    - Articles and tutorials
    - Practice projects
    - Certifications
    """
    
    def __init__(self):
        self.min_relevance_score = 0.3
    
    async def get_learning_recommendations(
        self,
        user_id: str,
        resource_pool: Optional[List[Dict]] = None,
        limit: int = 10
    ) -> List[LearningRecommendation]:
        """
        Get personalized learning recommendations.
        
        Args:
            user_id: User ID
            resource_pool: Available learning resources to recommend from
            limit: Maximum recommendations
            
        Returns:
            Ranked list of learning recommendations
        """
        
        try:
            # Get user context
            context = await memory_manager.get_complete_context(user_id)
            ltm = context.get("long_term_memory", {})
            
            if not ltm or "error" in ltm:
                return []
            
            # If no resource pool provided, generate generic recommendations
            if not resource_pool:
                return await self._generate_topic_recommendations(user_id, ltm, limit)
            
            # Score each resource
            scored_resources = []
            for resource in resource_pool:
                score, explanation = await self._score_resource(resource, ltm)
                
                if score >= self.min_relevance_score:
                    scored_resources.append(LearningRecommendation({
                        "resource": resource,
                        "relevance_score": score,
                        "explanation": explanation
                    }))
            
            # Sort by relevance
            scored_resources.sort(key=lambda x: x["relevance_score"], reverse=True)
            
            logger.info(f"Generated {len(scored_resources[:limit])} learning recommendations for {user_id}")
            return scored_resources[:limit]
            
        except Exception as e:
            logger.error(f"Error generating learning recommendations: {e}")
            return []
    
    async def _score_resource(
        self,
        resource: Dict[str, Any],
        ltm: Dict
    ) -> tuple[float, Dict[str, Any]]:
        """
        Score a learning resource for relevance.
        
        Returns: (score, explanation)
        """
        
        score = 0.0
        explanation = {"factors": [], "reasons": []}
        
        resource_topics = [t.lower() for t in resource.get("topics", [])]
        resource_skills = [s.lower() for s in resource.get("skills_taught", [])]
        resource_level = resource.get("difficulty_level", "").lower()
        
        # Get user profile
        skills = ltm.get("skill_profile", {})
        current_skills = [s.lower() for s in skills.get("technical_skills", [])]
        skill_gaps = [s.lower() for s in skills.get("skill_gaps", [])]
        learning_interests = [i.lower() for i in skills.get("learning_interests", [])]
        
        prefs = ltm.get("career_preferences", {})
        goals = [g.lower() for g in ltm.get("career_goals", [])]
        
        # 1. Skill gap coverage (weight: 0.4)
        gap_coverage = len([s for s in resource_skills if s in skill_gaps])
        if gap_coverage > 0:
            score += 0.4 * (gap_coverage / max(len(resource_skills), 1))
            explanation["factors"].append("fills_skill_gap")
            explanation["reasons"].append(f"Teaches {gap_coverage} skills you're missing")
        
        # 2. Learning interests match (weight: 0.3)
        interest_match = len([t for t in resource_topics if t in learning_interests])
        if interest_match > 0:
            score += 0.3 * (interest_match / max(len(resource_topics), 1))
            explanation["factors"].append("interest_match")
            explanation["reasons"].append("Matches your learning interests")
        
        # 3. Career goal alignment (weight: 0.2)
        goal_alignment = any(
            any(goal_word in topic for goal_word in goal.split())
            for goal in goals
            for topic in resource_topics
        )
        if goal_alignment:
            score += 0.2
            explanation["factors"].append("goal_aligned")
            explanation["reasons"].append("Supports your career goals")
        
        # 4. Appropriate difficulty (weight: 0.1)
        # Beginner: no related skills
        # Intermediate: some related skills
        # Advanced: most related skills
        
        related_skills_count = len([s for s in resource_skills if s in current_skills])
        skill_ratio = related_skills_count / max(len(resource_skills), 1)
        
        if resource_level == "beginner" and skill_ratio < 0.3:
            score += 0.1
            explanation["factors"].append("difficulty_appropriate")
        elif resource_level == "intermediate" and 0.3 <= skill_ratio < 0.7:
            score += 0.1
            explanation["factors"].append("difficulty_appropriate")
        elif resource_level == "advanced" and skill_ratio >= 0.7:
            score += 0.1
            explanation["factors"].append("difficulty_appropriate")
        elif skill_ratio < 0.5 and resource_level == "advanced":
            explanation["reasons"].append("⚠ May be too advanced")
        
        return min(1.0, score), explanation
    
    async def _generate_topic_recommendations(
        self,
        user_id: str,
        ltm: Dict,
        limit: int
    ) -> List[LearningRecommendation]:
        """Generate topic-based recommendations when no resource pool available"""
        
        recommendations = []
        
        skills = ltm.get("skill_profile", {})
        skill_gaps = skills.get("skill_gaps", [])[:5]
        learning_interests = skills.get("learning_interests", [])[:5]
        
        # Recommend topics for skill gaps
        for gap in skill_gaps:
            recommendations.append(LearningRecommendation({
                "topic": gap,
                "type": "skill_development",
                "relevance_score": 0.8,
                "explanation": {
                    "reasons": ["Fills identified skill gap", "Based on your job searches"]
                },
                "suggested_formats": ["online_course", "tutorial", "practice_project"]
            }))
        
        # Recommend topics for interests
        for interest in learning_interests:
            if interest not in skill_gaps:  # Don't duplicate
                recommendations.append(LearningRecommendation({
                    "topic": interest,
                    "type": "interest_based",
                    "relevance_score": 0.6,
                    "explanation": {
                        "reasons": ["Matches your interests"]
                    },
                    "suggested_formats": ["online_course", "article", "video"]
                }))
        
        return recommendations[:limit]
    
    async def get_learning_path_for_goal(
        self,
        user_id: str,
        goal: str
    ) -> Dict[str, Any]:
        """
        Generate a structured learning path for a career goal.
        
        Returns sequential learning steps.
        """
        
        # Get user context
        context = await memory_manager.get_complete_context(user_id)
        ltm = context.get("long_term_memory", {})
        
        skills = ltm.get("skill_profile", {})
        current_skills = [s.lower() for s in skills.get("technical_skills", [])]
        
        goal_lower = goal.lower()
        
        # Define learning paths for common goals
        paths = {
            "frontend_developer": [
                {"skill": "HTML/CSS", "duration": "2 weeks", "priority": "foundation"},
                {"skill": "JavaScript", "duration": "4 weeks", "priority": "foundation"},
                {"skill": "React", "duration": "4 weeks", "priority": "core"},
                {"skill": "TypeScript", "duration": "2 weeks", "priority": "core"},
                {"skill": "Next.js", "duration": "3 weeks", "priority": "advanced"}
            ],
            "backend_developer": [
                {"skill": "Python", "duration": "4 weeks", "priority": "foundation"},
                {"skill": "SQL", "duration": "3 weeks", "priority": "foundation"},
                {"skill": "FastAPI/Django", "duration": "4 weeks", "priority": "core"},
                {"skill": "PostgreSQL", "duration": "2 weeks", "priority": "core"},
                {"skill": "Docker", "duration": "2 weeks", "priority": "advanced"},
                {"skill": "Kubernetes", "duration": "3 weeks", "priority": "advanced"}
            ],
            "data_analyst": [
                {"skill": "SQL", "duration": "3 weeks", "priority": "foundation"},
                {"skill": "Python", "duration": "4 weeks", "priority": "foundation"},
                {"skill": "Statistics", "duration": "4 weeks", "priority": "core"},
                {"skill": "Tableau/Power BI", "duration": "3 weeks", "priority": "core"},
                {"skill": "Data Visualization", "duration": "2 weeks", "priority": "advanced"}
            ]
        }
        
        # Find matching path
        matching_path = None
        for path_key, path_steps in paths.items():
            if path_key.replace("_", " ") in goal_lower:
                matching_path = path_steps
                break
        
        if not matching_path:
            return {
                "goal": goal,
                "path_available": False,
                "message": "Custom learning path not yet available for this goal"
            }
        
        # Filter out skills user already has
        remaining_steps = [
            step for step in matching_path
            if step["skill"].lower() not in current_skills
        ]
        
        completed_steps = [
            step for step in matching_path
            if step["skill"].lower() in current_skills
        ]
        
        # Calculate estimated completion time
        total_weeks = sum(int(step["duration"].split()[0]) for step in remaining_steps)
        
        return {
            "goal": goal,
            "path_available": True,
            "total_steps": len(matching_path),
            "completed_steps": len(completed_steps),
            "remaining_steps": len(remaining_steps),
            "estimated_duration": f"{total_weeks} weeks",
            "progress_percentage": int((len(completed_steps) / len(matching_path)) * 100),
            "next_steps": remaining_steps[:3],  # Next 3 steps
            "learning_path": {
                "foundation": [s for s in remaining_steps if s["priority"] == "foundation"],
                "core": [s for s in remaining_steps if s["priority"] == "core"],
                "advanced": [s for s in remaining_steps if s["priority"] == "advanced"]
            }
        }
