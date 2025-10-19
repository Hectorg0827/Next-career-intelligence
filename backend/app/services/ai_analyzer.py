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
    
    async def generate_career_roadmap(
        self,
        job_title: str,
        skills: List[str],
        years_experience: int,
        career_goals: str = "Career advancement and AI resilience"
    ) -> Dict[str, Any]:
        """
        Generate multi-year career pathway roadmap (3, 5, and 10 years)
        
        FEATURE 2: Multi-Year Career Pathways
        
        Returns detailed roadmaps showing:
        - Career progression milestones
        - Skills to develop at each stage
        - Certifications and training
        - Salary expectations
        - AI resilience score at each stage
        - Alternative pathways (branching)
        """
        
        prompt = f"""
        Create a comprehensive multi-year career roadmap for this professional:
        
        Current Role: {job_title}
        Current Skills: {', '.join(skills)}
        Years of Experience: {years_experience}
        Career Goals: {career_goals}
        
        Provide a detailed JSON roadmap with THREE timelines (3-year, 5-year, 10-year):
        
        {{
            "career_roadmap": {{
                "3_year": {{
                    "primary_path": {{
                        "target_role": "<job title>",
                        "milestone_title": "<achievement description>",
                        "skills_to_develop": ["<skill 1>", "<skill 2>"],
                        "certifications": ["<cert 1>", "<cert 2>"],
                        "key_projects": ["<project type 1>", "<project type 2>"],
                        "estimated_salary_range": "<salary range>",
                        "ai_resilience_score": <0-100>,
                        "why_this_path": "<explanation of why this is recommended>",
                        "success_metrics": ["<metric 1>", "<metric 2>"]
                    }},
                    "alternative_path": {{
                        "target_role": "<alternative job title>",
                        "why_consider": "<reason to consider this path>",
                        "skills_to_develop": ["<skill 1>", "<skill 2>"],
                        "estimated_salary_range": "<salary range>"
                    }}
                }},
                "5_year": {{
                    "primary_path": {{
                        "target_role": "<senior/lead role>",
                        "milestone_title": "<achievement>",
                        "skills_to_develop": ["<advanced skill 1>", "<leadership>"],
                        "certifications": ["<advanced cert>"],
                        "key_projects": ["<complex project 1>", "<strategic initiative>"],
                        "estimated_salary_range": "<higher salary range>",
                        "ai_resilience_score": <0-100>,
                        "why_this_path": "<long-term value explanation>",
                        "success_metrics": ["<metric 1>", "<metric 2>"],
                        "market_trends": ["<trend 1>", "<trend 2>"]
                    }},
                    "alternative_path": {{
                        "target_role": "<alternative senior role>",
                        "why_consider": "<strategic pivot reasoning>",
                        "skills_to_develop": ["<skill>"],
                        "estimated_salary_range": "<salary range>"
                    }}
                }},
                "10_year": {{
                    "primary_path": {{
                        "target_role": "<executive/specialist role>",
                        "milestone_title": "<major career achievement>",
                        "skills_to_develop": ["<mastery skill>", "<thought leadership>"],
                        "certifications": ["<executive certification>"],
                        "key_projects": ["<transformational project>"],
                        "estimated_salary_range": "<executive salary range>",
                        "ai_resilience_score": <0-100>,
                        "why_this_path": "<legacy and impact explanation>",
                        "success_metrics": ["<executive metric>"],
                        "market_trends": ["<future trend>"],
                        "leadership_focus": ["<leadership area>"]
                    }},
                    "alternative_path": {{
                        "target_role": "<entrepreneurship or pivot>",
                        "why_consider": "<late-career opportunity>",
                        "skills_to_develop": ["<skill>"],
                        "estimated_salary_range": "<salary/equity range>"
                    }}
                }},
                "pathway_visualization": {{
                    "nodes": [
                        {{"stage": "Current", "role": "{job_title}", "year": 0}},
                        {{"stage": "3-Year", "role": "<3yr role>", "year": 3}},
                        {{"stage": "5-Year", "role": "<5yr role>", "year": 5}},
                        {{"stage": "10-Year", "role": "<10yr role>", "year": 10}}
                    ],
                    "edges": [
                        {{"from": "Current", "to": "3-Year", "skills_required": ["<skill>"], "confidence": <0-100>}},
                        {{"from": "3-Year", "to": "5-Year", "skills_required": ["<skill>"], "confidence": <0-100>}},
                        {{"from": "5-Year", "to": "10-Year", "skills_required": ["<skill>"], "confidence": <0-100>}}
                    ]
                }},
                "sankey_data": {{
                    "nodes": [
                        {{"id": 0, "name": "{job_title}", "category": "current"}},
                        {{"id": 1, "name": "<3yr primary role>", "category": "3-year"}},
                        {{"id": 2, "name": "<3yr alternative role>", "category": "3-year-alt"}},
                        {{"id": 3, "name": "<5yr primary role>", "category": "5-year"}},
                        {{"id": 4, "name": "<5yr alternative role>", "category": "5-year-alt"}},
                        {{"id": 5, "name": "<10yr primary role>", "category": "10-year"}},
                        {{"id": 6, "name": "<10yr alternative role>", "category": "10-year-alt"}}
                    ],
                    "links": [
                        {{"source": 0, "target": 1, "value": <85-95>, "skill": "<primary 3yr skill>"}},
                        {{"source": 0, "target": 2, "value": <40-60>, "skill": "<alternative 3yr skill>"}},
                        {{"source": 1, "target": 3, "value": <75-90>, "skill": "<primary 5yr skill>"}},
                        {{"source": 1, "target": 4, "value": <30-50>, "skill": "<pivot 5yr skill>"}},
                        {{"source": 2, "target": 4, "value": <60-80>, "skill": "<alt progression skill>"}},
                        {{"source": 3, "target": 5, "value": <70-85>, "skill": "<primary 10yr skill>"}},
                        {{"source": 3, "target": 6, "value": <20-40>, "skill": "<pivot 10yr skill>"}},
                        {{"source": 4, "target": 6, "value": <55-75>, "skill": "<alt progression 10yr>"}}
                    ]
                }},
                "immediate_next_steps": {{
                    "month_1_3": ["<action 1>", "<action 2>"],
                    "month_4_6": ["<action 1>", "<action 2>"],
                    "month_7_12": ["<action 1>", "<action 2>"],
                    "why_start_here": "<explanation of prioritization>"
                }},
                "risk_mitigation": {{
                    "automation_threats": ["<threat 1>", "<threat 2>"],
                    "protective_skills": ["<skill 1>", "<skill 2>"],
                    "pivot_options": ["<pivot 1>", "<pivot 2>"],
                    "why_these_skills": "<explanation>"
                }}
            }}
        }}
        
        Important Guidelines:
        1. Make paths REALISTIC and achievable based on current experience
        2. Include specific, actionable skills (not vague terms)
        3. Consider current AI trends and future labor market
        4. Salary ranges should reflect realistic market data
        5. AI resilience scores should increase over time (60→75→85→95)
        6. Provide DETAILED "why" explanations for every recommendation
        7. Alternative paths should be genuinely different strategic choices
        8. Focus on roles with strong human advantage + AI collaboration
        """
        
        try:
            logger.info(f"Generating multi-year career roadmap for {job_title}")
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert career strategist with deep knowledge of labor markets, 
                        AI trends, and professional development. Create detailed, realistic career roadmaps that 
                        balance ambition with achievability. Always explain WHY you recommend each path - users 
                        need to understand the reasoning to trust and act on your advice. Focus on building 
                        AI-resilient careers with strong human advantage factors."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.8,
                max_tokens=3000,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            logger.info("Career roadmap generated successfully")
            
            return result
            
        except Exception as e:
            logger.error(f"Career roadmap generation error: {e}")
            return self._get_fallback_roadmap(job_title, years_experience)
    
    def _get_fallback_roadmap(self, job_title: str, years_experience: int) -> Dict[str, Any]:
        """Fallback roadmap if API fails"""
        logger.warning("Using fallback career roadmap")
        
        return {
            "career_roadmap": {
                "3_year": {
                    "primary_path": {
                        "target_role": f"Senior {job_title}",
                        "milestone_title": "Technical expertise and team influence",
                        "skills_to_develop": ["Advanced technical skills", "Mentorship"],
                        "certifications": ["Industry certification"],
                        "key_projects": ["Lead a major project"],
                        "estimated_salary_range": "$80,000 - $120,000",
                        "ai_resilience_score": 70,
                        "why_this_path": "Natural progression building on current experience",
                        "success_metrics": ["Project delivery", "Team growth"]
                    },
                    "alternative_path": {
                        "target_role": "Technical Specialist",
                        "why_consider": "Deep expertise in niche area",
                        "skills_to_develop": ["Specialization"],
                        "estimated_salary_range": "$75,000 - $110,000"
                    }
                },
                "5_year": {
                    "primary_path": {
                        "target_role": f"Lead {job_title}",
                        "milestone_title": "Leadership and strategic impact",
                        "skills_to_develop": ["Leadership", "Strategy"],
                        "certifications": ["Leadership certification"],
                        "key_projects": ["Strategic initiative"],
                        "estimated_salary_range": "$120,000 - $180,000",
                        "ai_resilience_score": 80,
                        "why_this_path": "Leadership combines human skills with technical expertise",
                        "success_metrics": ["Team size", "Strategic impact"],
                        "market_trends": ["AI collaboration", "Remote leadership"]
                    },
                    "alternative_path": {
                        "target_role": "Management Track",
                        "why_consider": "People management focus",
                        "skills_to_develop": ["People management"],
                        "estimated_salary_range": "$110,000 - $160,000"
                    }
                },
                "10_year": {
                    "primary_path": {
                        "target_role": f"Director of {job_title.split()[0]} Operations",
                        "milestone_title": "Executive influence and transformation",
                        "skills_to_develop": ["Executive presence", "Business strategy"],
                        "certifications": ["Executive MBA"],
                        "key_projects": ["Organizational transformation"],
                        "estimated_salary_range": "$180,000 - $300,000+",
                        "ai_resilience_score": 90,
                        "why_this_path": "Executive roles require human judgment and strategy",
                        "success_metrics": ["P&L responsibility", "Strategic vision"],
                        "market_trends": ["AI-augmented decision making"],
                        "leadership_focus": ["Change management"]
                    },
                    "alternative_path": {
                        "target_role": "Consultant / Entrepreneur",
                        "why_consider": "Independence and impact",
                        "skills_to_develop": ["Business development"],
                        "estimated_salary_range": "$150,000 - $500,000+"
                    }
                },
                "pathway_visualization": {
                    "nodes": [
                        {"stage": "Current", "role": job_title, "year": 0},
                        {"stage": "3-Year", "role": f"Senior {job_title}", "year": 3},
                        {"stage": "5-Year", "role": f"Lead {job_title}", "year": 5},
                        {"stage": "10-Year", "role": "Director", "year": 10}
                    ],
                    "edges": [
                        {"from": "Current", "to": "3-Year", "skills_required": ["Technical mastery"], "confidence": 85},
                        {"from": "3-Year", "to": "5-Year", "skills_required": ["Leadership"], "confidence": 75},
                        {"from": "5-Year", "to": "10-Year", "skills_required": ["Strategy"], "confidence": 70}
                    ]
                },
                "sankey_data": {
                    "nodes": [
                        {"id": 0, "name": job_title, "category": "current"},
                        {"id": 1, "name": f"Senior {job_title}", "category": "3-year"},
                        {"id": 2, "name": f"Lead {job_title}", "category": "5-year"},
                        {"id": 3, "name": "Director", "category": "10-year"}
                    ],
                    "links": [
                        {"source": 0, "target": 1, "value": 85, "skill": "Technical Mastery"},
                        {"source": 1, "target": 2, "value": 75, "skill": "Leadership"},
                        {"source": 2, "target": 3, "value": 70, "skill": "Executive Strategy"}
                    ]
                },
                "immediate_next_steps": {
                    "month_1_3": ["Identify skill gaps", "Start learning"],
                    "month_4_6": ["Complete first certification", "Lead small project"],
                    "month_7_12": ["Mentorship", "Expand network"],
                    "why_start_here": "Build foundation before advancing"
                },
                "risk_mitigation": {
                    "automation_threats": ["Routine tasks", "Data processing"],
                    "protective_skills": ["Critical thinking", "Leadership", "Strategy"],
                    "pivot_options": ["Adjacent roles", "Management track"],
                    "why_these_skills": "These skills are hard for AI to replicate"
                }
            }
        }
    
    async def generate_industry_benchmarks(
        self,
        job_title: str,
        skills: List[str],
        years_experience: int,
        automation_risk_score: float
    ) -> Dict[str, Any]:
        """
        Generate industry benchmark comparisons
        
        FEATURE 6: Benchmarking Dashboard
        
        Returns comparisons to industry averages:
        - Automation risk percentile
        - Skill demand scores
        - Salary benchmarks
        - Career progression metrics
        """
        
        prompt = f"""
        Generate industry benchmark data for this professional:
        
        Role: {job_title}
        Skills: {', '.join(skills)}
        Experience: {years_experience} years
        Their Automation Risk: {automation_risk_score}%
        
        Provide detailed JSON benchmarks:
        
        {{
            "benchmarks": {{
                "automation_risk_comparison": {{
                    "your_score": {automation_risk_score},
                    "industry_average": <0-100>,
                    "percentile": <0-100>,
                    "comparison_text": "<you vs industry>",
                    "trend": "<improving|declining|stable>"
                }},
                "skill_demand": {{
                    "overall_score": <0-100>,
                    "top_skills": [
                        {{"skill": "<skill name>", "demand_score": <0-100>, "growth_rate": "<percentage>"}},
                        {{"skill": "<skill name>", "demand_score": <0-100>, "growth_rate": "<percentage>"}}
                    ],
                    "skill_gaps": [
                        {{"skill": "<missing skill>", "importance": "<high|medium|low>", "demand_score": <0-100>}}
                    ]
                }},
                "salary_benchmark": {{
                    "your_estimated_range": "<$min - $max>",
                    "industry_median": "<$amount>",
                    "percentile_25": "<$amount>",
                    "percentile_50": "<$amount>",
                    "percentile_75": "<$amount>",
                    "percentile_90": "<$amount>",
                    "your_position": "<below|at|above> market"
                }},
                "career_progression": {{
                    "pace": "<faster|average|slower> than peers",
                    "typical_years_to_next_level": <years>,
                    "your_readiness_score": <0-100>,
                    "key_gaps_for_promotion": ["<gap 1>", "<gap 2>"]
                }},
                "market_trends": {{
                    "role_growth": "<percentage> YoY",
                    "hiring_difficulty": "<high|medium|low>",
                    "remote_availability": "<percentage of jobs>",
                    "top_hiring_industries": ["<industry 1>", "<industry 2>"]
                }},
                "competitive_position": {{
                    "overall_ranking": "<top X%>",
                    "strengths": ["<strength 1>", "<strength 2>"],
                    "improvement_areas": ["<area 1>", "<area 2>"],
                    "unique_advantages": ["<advantage 1>", "<advantage 2>"]
                }}
            }}
        }}
        
        Base estimates on realistic 2025 market data for {job_title} roles.
        Be specific and actionable. Provide context for all numbers.
        """
        
        try:
            logger.info(f"Generating industry benchmarks for {job_title}")
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert labor market analyst with deep knowledge of salary data, 
                        skill trends, and career progression patterns across industries. Provide realistic, 
                        data-driven benchmarks that help professionals understand their market position."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            logger.info("Industry benchmarks generated successfully")
            
            return result
            
        except Exception as e:
            logger.error(f"Benchmark generation error: {e}")
            return self._get_fallback_benchmarks(job_title, years_experience, automation_risk_score)
    
    def _get_fallback_benchmarks(
        self, 
        job_title: str, 
        years_experience: int, 
        automation_risk_score: float
    ) -> Dict[str, Any]:
        """Fallback benchmarks if API fails"""
        logger.warning("Using fallback industry benchmarks")
        
        # Estimate salary based on experience
        base_salary = 60000 + (years_experience * 8000)
        
        return {
            "benchmarks": {
                "automation_risk_comparison": {
                    "your_score": automation_risk_score,
                    "industry_average": 55.0,
                    "percentile": 60 if automation_risk_score < 55 else 40,
                    "comparison_text": "Slightly below average risk" if automation_risk_score < 55 else "Slightly above average risk",
                    "trend": "stable"
                },
                "skill_demand": {
                    "overall_score": 70,
                    "top_skills": [
                        {"skill": "Communication", "demand_score": 85, "growth_rate": "+12%"},
                        {"skill": "Problem Solving", "demand_score": 80, "growth_rate": "+8%"}
                    ],
                    "skill_gaps": [
                        {"skill": "AI/ML Basics", "importance": "high", "demand_score": 90}
                    ]
                },
                "salary_benchmark": {
                    "your_estimated_range": f"${base_salary:,} - ${base_salary + 20000:,}",
                    "industry_median": f"${base_salary + 10000:,}",
                    "percentile_25": f"${base_salary - 10000:,}",
                    "percentile_50": f"${base_salary + 10000:,}",
                    "percentile_75": f"${base_salary + 30000:,}",
                    "percentile_90": f"${base_salary + 50000:,}",
                    "your_position": "at market"
                },
                "career_progression": {
                    "pace": "average",
                    "typical_years_to_next_level": 3,
                    "your_readiness_score": 65,
                    "key_gaps_for_promotion": ["Leadership skills", "Strategic thinking"]
                },
                "market_trends": {
                    "role_growth": "+5% YoY",
                    "hiring_difficulty": "medium",
                    "remote_availability": "45% of jobs",
                    "top_hiring_industries": ["Technology", "Healthcare", "Finance"]
                },
                "competitive_position": {
                    "overall_ranking": "top 40%",
                    "strengths": ["Experience level", "Adaptability"],
                    "improvement_areas": ["Emerging tech skills", "Leadership"],
                    "unique_advantages": ["Diverse background", "Strong fundamentals"]
                }
            }
        }
