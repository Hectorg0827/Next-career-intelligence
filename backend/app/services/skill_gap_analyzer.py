"""
Skill Gap Analyzer Service
Compares user's skill profile with target role requirements
"""

from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from loguru import logger
from datetime import datetime
import os
import json

from app.models.skill_schemas import (
    SkillGapRequest,
    SkillGapAnalysis,
    MatchedSkill,
    GapSkill,
    LearningCluster,
    ProficiencyLevel
)
from app.services.skill_service import SkillService

try:
    import google.generativeai as genai
except ImportError:
    logger.warning("google.generativeai not installed")
    genai = None


# Sample role skill catalog (TODO: Move to database or external config)
ROLE_SKILL_CATALOG: Dict[str, Dict[str, any]] = {
    "data analyst": {
        "core_skills": [
            {"name": "SQL", "importance": "Critical"},
            {"name": "Python", "importance": "Critical"},
            {"name": "Excel", "importance": "High"},
            {"name": "Statistics", "importance": "Critical"},
            {"name": "Data Visualization", "importance": "High"},
        ],
        "nice_to_have": [
            {"name": "R", "importance": "Medium"},
            {"name": "Tableau", "importance": "High"},
            {"name": "Power BI", "importance": "Medium"},
        ]
    },
    "software engineer": {
        "core_skills": [
            {"name": "Programming", "importance": "Critical"},
            {"name": "Algorithms", "importance": "Critical"},
            {"name": "System Design", "importance": "High"},
            {"name": "Git", "importance": "High"},
            {"name": "Testing", "importance": "High"},
        ],
        "nice_to_have": [
            {"name": "Docker", "importance": "Medium"},
            {"name": "Kubernetes", "importance": "Medium"},
            {"name": "AWS", "importance": "Medium"},
        ]
    },
    "product manager": {
        "core_skills": [
            {"name": "Product Strategy", "importance": "Critical"},
            {"name": "Roadmapping", "importance": "Critical"},
            {"name": "User Research", "importance": "High"},
            {"name": "Data Analysis", "importance": "High"},
            {"name": "Communication", "importance": "Critical"},
        ],
        "nice_to_have": [
            {"name": "SQL", "importance": "Medium"},
            {"name": "Agile", "importance": "High"},
            {"name": "Wireframing", "importance": "Medium"},
        ]
    },
}


class SkillGapAnalyzerService:
    """Service for analyzing skill gaps between user profile and target roles"""

    def __init__(self):
        if genai:
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
            self.model = genai.GenerativeModel(
                model_name,
                generation_config={"response_mime_type": "application/json"}
            )
        else:
            self.model = None

    def get_role_requirements(self, role_title: str) -> Optional[Dict]:
        """Get skill requirements for a target role"""
        role_key = role_title.lower().strip()
        return ROLE_SKILL_CATALOG.get(role_key)

    def calculate_role_fit_score(
        self,
        user_skills: List[Dict],
        required_skills: List[Dict]
    ) -> float:
        """Calculate overall fit score based on matched skills"""
        
        if not required_skills:
            return 0.0
        
        user_skill_names = {s["name"].lower() for s in user_skills}
        
        total_weight = 0
        matched_weight = 0
        
        for req_skill in required_skills:
            req_name = req_skill["name"].lower()
            importance = req_skill.get("importance", "Medium")
            
            # Weight by importance
            weight = {
                "Critical": 3,
                "High": 2,
                "Medium": 1,
                "Low": 0.5
            }.get(importance, 1)
            
            total_weight += weight
            
            if req_name in user_skill_names:
                matched_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        return min(100.0, (matched_weight / total_weight) * 100)

    async def analyze_skill_gap(
        self,
        db: Session,
        user_id: str,
        request: SkillGapRequest
    ) -> SkillGapAnalysis:
        """Perform complete skill gap analysis"""
        
        logger.info(f"Analyzing skill gap for user {user_id}, target role: {request.target_role_title}")
        
        # 1. Get user's skills
        skill_service = SkillService()
        user_skill_response = skill_service.get_user_skills(db, user_id)
        user_skills = [
            {
                "name": s.name,
                "proficiency_level": s.proficiency_level.value
            }
            for s in user_skill_response.skills
        ]
        
        # 2. Get target role requirements
        role_requirements = self.get_role_requirements(request.target_role_title)
        
        if not role_requirements:
            # Fallback: use LLM to generate requirements
            role_requirements = await self._generate_role_requirements_with_llm(request.target_role_title)
        
        required_skills = role_requirements.get("core_skills", []) + role_requirements.get("nice_to_have", [])
        
        # 3. Match skills
        matched_skills = []
        gap_skills = []
        weak_skills = []
        
        user_skill_map = {s["name"].lower(): s for s in user_skills}
        
        for req_skill in required_skills:
            req_name_lower = req_skill["name"].lower()
            
            if req_name_lower in user_skill_map:
                user_skill = user_skill_map[req_name_lower]
                proficiency = ProficiencyLevel(user_skill["proficiency_level"])
                
                matched = MatchedSkill(
                    name=req_skill["name"],
                    proficiency_level=proficiency,
                    relevance_score=self._calculate_relevance_score(
                        proficiency,
                        req_skill.get("importance", "Medium")
                    )
                )
                
                if proficiency in [ProficiencyLevel.BEGINNER, ProficiencyLevel.INTERMEDIATE]:
                    weak_skills.append(matched)
                else:
                    matched_skills.append(matched)
            else:
                gap_skills.append(GapSkill(
                    name=req_skill["name"],
                    importance=req_skill.get("importance", "Medium"),
                    estimated_time_to_learn=self._estimate_learning_time(req_skill.get("importance", "Medium")),
                    recommended_resources=[f"{req_skill['name']} Course - Coursera"]
                ))
        
        # 4. Calculate fit score
        role_fit_score = self.calculate_role_fit_score(user_skills, required_skills)
        
        # 5. Generate learning clusters
        learning_clusters = self._create_learning_clusters(gap_skills)
        
        # 6. Generate summary
        summary = await self._generate_summary_with_llm(
            request.target_role_title,
            len(matched_skills),
            len(gap_skills),
            role_fit_score
        )
        
        return SkillGapAnalysis(
            title=f"Your Skill Match for {request.target_role_title.title()}",
            summary=summary,
            role_fit_score=round(role_fit_score, 1),
            matched_skills=matched_skills,
            matched_count=len(matched_skills),
            gap_skills=gap_skills,
            gap_count=len(gap_skills),
            weak_skills=weak_skills,
            suggested_learning_clusters=learning_clusters,
            target_role=request.target_role_title,
            analysis_date=datetime.utcnow()
        )

    def _calculate_relevance_score(self, proficiency: ProficiencyLevel, importance: str) -> float:
        """Calculate how relevant a skill is based on proficiency and importance"""
        
        proficiency_scores = {
            ProficiencyLevel.BEGINNER: 40,
            ProficiencyLevel.INTERMEDIATE: 65,
            ProficiencyLevel.ADVANCED: 85,
            ProficiencyLevel.EXPERT: 95
        }
        
        importance_multipliers = {
            "Critical": 1.0,
            "High": 0.9,
            "Medium": 0.8,
            "Low": 0.7
        }
        
        base_score = proficiency_scores.get(proficiency, 50)
        multiplier = importance_multipliers.get(importance, 0.8)
        
        return min(100.0, base_score * multiplier)

    def _estimate_learning_time(self, importance: str) -> str:
        """Estimate time to learn a skill based on importance"""
        
        estimates = {
            "Critical": "3-6 months",
            "High": "2-4 months",
            "Medium": "1-2 months",
            "Low": "2-4 weeks"
        }
        
        return estimates.get(importance, "1-3 months")

    def _create_learning_clusters(self, gap_skills: List[GapSkill]) -> List[LearningCluster]:
        """Group gap skills into learning clusters"""
        
        # Simple clustering by importance for now
        # TODO: Use semantic similarity or skill taxonomy
        
        clusters = []
        
        high_priority = [s for s in gap_skills if s.importance in ["Critical", "High"]]
        medium_priority = [s for s in gap_skills if s.importance == "Medium"]
        
        if high_priority:
            clusters.append(LearningCluster(
                cluster_name="Core Competencies",
                skills=[s.name for s in high_priority[:3]],
                estimated_time="3-6 months",
                priority="High"
            ))
        
        if medium_priority:
            clusters.append(LearningCluster(
                cluster_name="Supporting Skills",
                skills=[s.name for s in medium_priority[:3]],
                estimated_time="2-3 months",
                priority="Medium"
            ))
        
        return clusters

    async def _generate_role_requirements_with_llm(self, role_title: str) -> Dict:
        """Use LLM to generate role requirements if not in catalog"""
        
        if not self.model:
            return {"core_skills": [], "nice_to_have": []}
        
        prompt = f"""
        Generate skill requirements for the role: "{role_title}"
        
        Return a JSON object with this structure:
        {{
            "core_skills": [
                {{"name": "Skill Name", "importance": "Critical|High|Medium|Low"}}
            ],
            "nice_to_have": [
                {{"name": "Skill Name", "importance": "Medium|Low"}}
            ]
        }}
        
        Include 5-7 core skills and 3-5 nice-to-have skills.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return json.loads(response.text)
        except Exception as e:
            logger.error(f"LLM role requirements generation failed: {e}")
            return {"core_skills": [], "nice_to_have": []}

    async def _generate_summary_with_llm(
        self,
        role_title: str,
        matched_count: int,
        gap_count: int,
        fit_score: float
    ) -> str:
        """Generate natural language summary"""
        
        if not self.model:
            return f"You match {matched_count} skills for {role_title}. Work on {gap_count} gap skills to improve your fit ({fit_score:.0f}%)."
        
        prompt = f"""
        Write a concise 2-3 sentence summary for a skill gap analysis:
        - Target role: {role_title}
        - Skills matched: {matched_count}
        - Skills missing: {gap_count}
        - Fit score: {fit_score:.0f}%
        
        Be encouraging but realistic. Mention specific next steps.
        Return only the summary text, no JSON.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"LLM summary generation failed: {e}")
            return f"You match {matched_count} skills for {role_title}. Focus on developing {gap_count} key skills to increase your readiness."


skill_gap_analyzer = SkillGapAnalyzerService()
