"""
AI Analysis Service - OpenAI GPT integration for career risk analysis
"""

from openai import AsyncOpenAI
from loguru import logger
from typing import Dict, List, Any
import json

from app.core.config import settings
from app.models.schemas import AIDisplacementRisk, TransitionPathway, RiskLevel


class AIAnalyzerService:
    """Service for AI-powered career analysis using OpenAI GPT"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
    
    async def analyze_displacement_risk(
        self,
        job_title: str,
        skills: List[str],
        location: str,
        occupation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze AI displacement risk for a given job
        
        Uses GPT to evaluate:
        - Automation potential
        - AI augmentation opportunities
        - Timeline for displacement
        - Risk level classification
        """
        
        prompt = self._build_risk_analysis_prompt(
            job_title, skills, location, occupation_data
        )
        
        try:
            logger.info(f"Calling OpenAI API for risk analysis: {job_title}")
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert career analyst specializing in AI displacement risk assessment. 
                        Analyze jobs based on automation potential, AI augmentation opportunities, and human advantage factors.
                        Provide data-driven, realistic assessments based on current AI capabilities and labor market trends."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Validate and structure response
            risk_data = {
                "level": result.get("risk_level", "Medium"),
                "score": result.get("risk_score", 50),
                "velocity": result.get("automation_timeline", "Unknown"),
                "augmentation_potential": result.get("augmentation_potential", "Medium"),
                "reasoning": result.get("reasoning", "")
            }
            
            logger.info(f"Risk analysis completed: {risk_data['level']} ({risk_data['score']}%)")
            
            return risk_data
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            # Return fallback data if API fails
            return self._get_fallback_risk_analysis(job_title)
    
    async def analyze_compatibility(
        self,
        current_skills: List[str],
        occupation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze career compatibility and generate transition pathways
        
        Returns:
        - Compatibility score
        - Human advantage factors
        - Transition pathway recommendations
        - Skill gaps
        """
        
        prompt = self._build_compatibility_prompt(current_skills, occupation_data)
        
        try:
            logger.info("Analyzing career compatibility and pathways...")
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are a career transition expert. Analyze skill sets and recommend 
                        realistic career pathways that leverage existing skills while building future-proof capabilities.
                        Focus on roles with high human advantage and AI collaboration potential."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.8,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return {
                "compatibility_score": result.get("compatibility_score", 70),
                "human_advantage_factors": result.get("human_advantage_factors", []),
                "transition_pathways": result.get("transition_pathways", []),
                "skill_gaps": result.get("skill_gaps", [])
            }
            
        except Exception as e:
            logger.error(f"Compatibility analysis error: {e}")
            return self._get_fallback_compatibility()
    
    def _build_risk_analysis_prompt(
        self,
        job_title: str,
        skills: List[str],
        location: str,
        occupation_data: Dict[str, Any]
    ) -> str:
        """Build prompt for risk analysis"""
        
        return f"""
        Analyze the AI displacement risk for this job:
        
        Job Title: {job_title}
        Current Skills: {', '.join(skills)}
        Location: {location}
        O*NET Data: {json.dumps(occupation_data, indent=2)}
        
        Provide a comprehensive risk assessment in JSON format with:
        {{
            "risk_level": "Low|Medium|High|Critical",
            "risk_score": <0-100>,
            "automation_timeline": "<description of when automation might occur>",
            "augmentation_potential": "Low|Medium|High",
            "reasoning": "<brief explanation of assessment>",
            "key_factors": ["<factors contributing to risk>"]
        }}
        
        Consider:
        1. Current AI capabilities (LLMs, computer vision, robotics)
        2. Tasks that require human judgment, empathy, creativity
        3. Regulatory and safety constraints
        4. Economic feasibility of automation
        5. Regional labor market conditions
        """
    
    def _build_compatibility_prompt(
        self,
        skills: List[str],
        occupation_data: Dict[str, Any]
    ) -> str:
        """Build prompt for compatibility analysis"""
        
        return f"""
        Analyze career transition opportunities for someone with these skills:
        
        Current Skills: {', '.join(skills)}
        Current Occupation Data: {json.dumps(occupation_data, indent=2)}
        
        Provide analysis in JSON format with:
        {{
            "compatibility_score": <0-100>,
            "human_advantage_factors": ["<factors that are hard to automate>"],
            "transition_pathways": [
                {{
                    "role": "<target job title>",
                    "ease": <0-100 ease of transition>,
                    "required_skills": ["<skills needed>"],
                    "estimated_training_time": "<time estimate>",
                    "salary_potential": "<salary range>",
                    "demand_trend": "<growing|stable|declining>"
                }}
            ],
            "skill_gaps": ["<skills to develop>"]
        }}
        
        Focus on:
        1. Roles with strong human advantage (creativity, empathy, strategy)
        2. AI-augmented roles (AI collaboration, data interpretation)
        3. Realistic transitions based on current skills
        4. Future-proof career paths
        5. Provide 3-5 concrete pathway options
        """
    
    def _get_fallback_risk_analysis(self, job_title: str) -> Dict[str, Any]:
        """Fallback data if API fails"""
        logger.warning("Using fallback risk analysis data")
        
        return {
            "level": "Medium",
            "score": 50,
            "velocity": "Assessment pending - API unavailable",
            "augmentation_potential": "Medium",
            "reasoning": "Unable to complete AI analysis. This is a placeholder assessment."
        }
    
    def _get_fallback_compatibility(self) -> Dict[str, Any]:
        """Fallback compatibility data"""
        logger.warning("Using fallback compatibility data")
        
        return {
            "compatibility_score": 70,
            "human_advantage_factors": [
                "Critical thinking",
                "Interpersonal communication"
            ],
            "transition_pathways": [
                {
                    "role": "AI Collaboration Specialist",
                    "ease": 75,
                    "required_skills": ["AI literacy", "Data analysis"],
                    "estimated_training_time": "6-12 months",
                    "salary_potential": "$70,000 - $95,000",
                    "demand_trend": "growing"
                }
            ],
            "skill_gaps": ["AI fundamentals", "Data interpretation"]
        }
