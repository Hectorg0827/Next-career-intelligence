"""
Skill Recommender - Intelligent Skill Development Recommendations

Analyzes skill gaps and career goals to recommend skills worth developing.
"""

from typing import Dict, List, Optional, Any
from collections import Counter
import logging

from app.services.ai.memory import memory_manager
from app.services.foundation.events import event_store

logger = logging.getLogger(__name__)


class SkillRecommendation(Dict):
    """Skill recommendation with rationale"""
    pass


class SkillRecommender:
    """
    Intelligent skill recommendation system.
    
    Recommends skills based on:
    - Career goals and target roles
    - Current skill gaps
    - Job market trends
    - Learning interests
    """
    
    def __init__(self):
        # In production, these would come from market data/APIs
        self.trending_skills = {
            "tech": ["AI/ML", "Cloud Computing", "Kubernetes", "React", "Python", "TypeScript", "DevOps"],
            "data": ["SQL", "Data Analysis", "Tableau", "Power BI", "Statistics", "Python"],
            "product": ["Product Strategy", "User Research", "Data Analysis", "Agile", "Roadmapping"],
            "design": ["Figma", "UI/UX Design", "Prototyping", "User Research", "Design Systems"]
        }
    
    async def get_skill_recommendations(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[SkillRecommendation]:
        """
        Get personalized skill development recommendations.
        
        Returns ranked list of skills to learn with rationale.
        """
        
        try:
            # Get user context
            context = await memory_manager.get_complete_context(user_id)
            ltm = context.get("long_term_memory", {})
            
            if not ltm or "error" in ltm:
                return await self._get_default_recommendations(limit)
            
            recommendations = []
            
            # 1. Skills from job searches (what jobs require)
            job_skill_recs = await self._recommend_from_job_interests(ltm)
            recommendations.extend(job_skill_recs)
            
            # 2. Skills to fill identified gaps
            gap_recs = await self._recommend_from_skill_gaps(ltm)
            recommendations.extend(gap_recs)
            
            # 3. Skills for career goals
            goal_recs = await self._recommend_from_career_goals(ltm)
            recommendations.extend(goal_recs)
            
            # 4. Adjacent skills (related to current skills)
            adjacent_recs = await self._recommend_adjacent_skills(ltm)
            recommendations.extend(adjacent_recs)
            
            # Deduplicate and rank
            skill_scores = {}
            skill_reasons = {}
            
            for rec in recommendations:
                skill = rec["skill"]
                score = rec["score"]
                reason = rec["reason"]
                
                if skill in skill_scores:
                    skill_scores[skill] += score
                    skill_reasons[skill].append(reason)
                else:
                    skill_scores[skill] = score
                    skill_reasons[skill] = [reason]
            
            # Build final recommendations
            final_recs = []
            for skill, score in sorted(skill_scores.items(), key=lambda x: x[1], reverse=True):
                final_recs.append(SkillRecommendation({
                    "skill": skill,
                    "score": min(1.0, score),
                    "reasons": skill_reasons[skill],
                    "priority": self._get_priority_level(score)
                }))
            
            logger.info(f"Generated {len(final_recs[:limit])} skill recommendations for {user_id}")
            return final_recs[:limit]
            
        except Exception as e:
            logger.error(f"Error generating skill recommendations: {e}")
            return []
    
    async def _recommend_from_job_interests(self, ltm: Dict) -> List[Dict]:
        """Recommend skills from jobs user is interested in"""
        
        recommendations = []
        prefs = ltm.get("career_preferences", {})
        skills = ltm.get("skill_profile", {})
        current_skills = set(s.lower() for s in skills.get("technical_skills", []))
        
        # Get skills from preferred industries/roles
        preferred_industries = prefs.get("preferred_industries", [])
        
        for industry in preferred_industries[:2]:  # Top 2 industries
            industry_lower = industry.lower()
            
            # Map industries to skill categories
            if any(term in industry_lower for term in ["tech", "software", "it"]):
                trending = self.trending_skills["tech"]
            elif any(term in industry_lower for term in ["data", "analytics"]):
                trending = self.trending_skills["data"]
            elif "product" in industry_lower:
                trending = self.trending_skills["product"]
            elif "design" in industry_lower:
                trending = self.trending_skills["design"]
            else:
                trending = self.trending_skills["tech"]  # Default
            
            for skill in trending:
                if skill.lower() not in current_skills:
                    recommendations.append({
                        "skill": skill,
                        "score": 0.4,
                        "reason": f"Valuable for {industry} roles"
                    })
        
        return recommendations
    
    async def _recommend_from_skill_gaps(self, ltm: Dict) -> List[Dict]:
        """Recommend skills to fill identified gaps"""
        
        recommendations = []
        skills = ltm.get("skill_profile", {})
        skill_gaps = skills.get("skill_gaps", [])
        
        for gap in skill_gaps:
            recommendations.append({
                "skill": gap,
                "score": 0.5,
                "reason": "Identified as skill gap from your job searches"
            })
        
        return recommendations
    
    async def _recommend_from_career_goals(self, ltm: Dict) -> List[Dict]:
        """Recommend skills aligned with career goals"""
        
        recommendations = []
        goals = ltm.get("career_goals", [])
        
        for goal in goals:
            goal_lower = goal.lower()
            
            if "senior" in goal_lower or "advance" in goal_lower:
                recommendations.extend([
                    {"skill": "Leadership", "score": 0.4, "reason": "Essential for advancement"},
                    {"skill": "System Design", "score": 0.3, "reason": "Important for senior roles"},
                    {"skill": "Mentoring", "score": 0.3, "reason": "Key senior responsibility"}
                ])
            
            elif "management" in goal_lower or "lead" in goal_lower:
                recommendations.extend([
                    {"skill": "Team Management", "score": 0.5, "reason": "Critical for management roles"},
                    {"skill": "Strategic Planning", "score": 0.4, "reason": "Key management skill"},
                    {"skill": "Communication", "score": 0.3, "reason": "Essential for leadership"}
                ])
            
            elif "skill" in goal_lower:
                # User wants to develop skills - recommend trending ones
                for skill in self.trending_skills["tech"][:3]:
                    recommendations.append({
                        "skill": skill,
                        "score": 0.3,
                        "reason": "Trending skill aligned with development goals"
                    })
        
        return recommendations
    
    async def _recommend_adjacent_skills(self, ltm: Dict) -> List[Dict]:
        """Recommend skills adjacent to current skills"""
        
        recommendations = []
        skills = ltm.get("skill_profile", {})
        current_skills = [s.lower() for s in skills.get("technical_skills", [])]
        
        # Define skill relationships
        adjacent_map = {
            "python": ["Django", "FastAPI", "Machine Learning", "Data Analysis"],
            "javascript": ["TypeScript", "React", "Node.js", "Next.js"],
            "react": ["Next.js", "TypeScript", "Redux", "React Native"],
            "sql": ["PostgreSQL", "Data Modeling", "Database Design", "ETL"],
            "aws": ["Kubernetes", "Docker", "Terraform", "DevOps"],
            "docker": ["Kubernetes", "AWS", "DevOps", "CI/CD"]
        }
        
        for skill in current_skills:
            if skill in adjacent_map:
                for adjacent in adjacent_map[skill]:
                    if adjacent.lower() not in current_skills:
                        recommendations.append({
                            "skill": adjacent,
                            "score": 0.35,
                            "reason": f"Complements your {skill.title()} skills"
                        })
        
        return recommendations
    
    async def _get_default_recommendations(self, limit: int) -> List[SkillRecommendation]:
        """Get default recommendations when no user context available"""
        
        # Return trending skills
        default_skills = self.trending_skills["tech"][:limit]
        
        return [
            SkillRecommendation({
                "skill": skill,
                "score": 0.5,
                "reasons": ["Currently trending in the job market"],
                "priority": "medium"
            })
            for skill in default_skills
        ]
    
    def _get_priority_level(self, score: float) -> str:
        """Convert score to priority level"""
        if score >= 0.7:
            return "high"
        elif score >= 0.4:
            return "medium"
        else:
            return "low"
    
    async def get_skill_learning_path(
        self,
        user_id: str,
        target_skill: str
    ) -> Dict[str, Any]:
        """
        Get learning path for a specific skill.
        
        Returns prerequisites and recommended sequence.
        """
        
        # Define skill prerequisites
        prerequisites_map = {
            "react": ["JavaScript", "HTML", "CSS"],
            "typescript": ["JavaScript"],
            "kubernetes": ["Docker", "Linux"],
            "machine learning": ["Python", "Statistics", "Linear Algebra"],
            "fastapi": ["Python"],
            "next.js": ["React", "JavaScript"]
        }
        
        target_lower = target_skill.lower()
        prerequisites = prerequisites_map.get(target_lower, [])
        
        # Get user's current skills
        context = await memory_manager.get_complete_context(user_id)
        ltm = context.get("long_term_memory", {})
        current_skills = [s.lower() for s in ltm.get("skill_profile", {}).get("technical_skills", [])]
        
        # Determine what they need to learn first
        missing_prereqs = [p for p in prerequisites if p.lower() not in current_skills]
        has_prereqs = [p for p in prerequisites if p.lower() in current_skills]
        
        return {
            "target_skill": target_skill,
            "prerequisites": prerequisites,
            "missing_prerequisites": missing_prereqs,
            "completed_prerequisites": has_prereqs,
            "ready_to_learn": len(missing_prereqs) == 0,
            "learning_sequence": missing_prereqs + [target_skill] if missing_prereqs else [target_skill]
        }
