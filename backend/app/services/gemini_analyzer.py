"""
NextAI Analyzer - Advanced Career Intelligence
Powered by state-of-the-art AI for career analysis
"""

import os
from typing import Dict, List, Optional, Any
import json
from loguru import logger
import google.generativeai as genai
from fastapi import HTTPException

# Configure AI Engine
NEXTAI_API_KEY = os.getenv("GEMINI_API_KEY")  # Internal config name
if NEXTAI_API_KEY:
    genai.configure(api_key=NEXTAI_API_KEY)


class GeminiAnalyzer:
    """
    NextAI Career Intelligence Analyzer
    Advanced AI-powered career analysis and insights
    WITH SAFETY SETTINGS
    """
    
    def __init__(self):
        # Configure safety settings for career-focused content
        safety_settings = {
            genai.types.HarmCategory.HARM_CATEGORY_HATE_SPEECH: genai.types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            genai.types.HarmCategory.HARM_CATEGORY_HARASSMENT: genai.types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            genai.types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: genai.types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            genai.types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: genai.types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }
        
        self.model = genai.GenerativeModel(
            'gemini-2.5-flash',  # Latest fast model, good for production
            safety_settings=safety_settings
        )
    
    def _clean_json_response(self, text: str) -> str:
        """
        Clean Gemini response text to ensure valid JSON
        Removes markdown code blocks and fixes control characters
        """
        import re
        
        # Remove markdown code blocks
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        
        # Remove any leading/trailing whitespace
        text = text.strip()
        
        # Replace problematic control characters in string values
        # This preserves JSON structure while cleaning string content
        text = text.replace('\\n', ' ')
        text = text.replace('\\r', ' ')
        text = text.replace('\\t', ' ')
        text = text.replace('\n', ' ')
        text = text.replace('\r', ' ')
        text = text.replace('\t', ' ')
        
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        return text
    
    async def analyze_with_prompts(
        self,
        system_prompt: str,
        developer_prompt: str,
        task_prompt: str,
        safety_settings: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Multi-tier prompt analysis for Resume Studio.
        Combines system, developer, and task prompts with safety enforcement.
        """
        try:
            # Construct hierarchical prompt
            full_prompt = f"""SYSTEM CONTEXT:
{system_prompt}

DEVELOPER INSTRUCTIONS:
{developer_prompt}

USER TASK:
{task_prompt}

Return ONLY valid JSON matching the requested schema. No markdown, no explanations."""

            # Apply additional safety settings if provided
            generation_config = {
                "temperature": 0.3,  # Lower temperature for factual, structured output
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 4096,
            }
            
            response = self.model.generate_content(
                full_prompt,
                generation_config=generation_config
            )
            
            # Parse JSON response
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text.replace("```json", "").replace("```", "").strip()
            elif response_text.startswith("```"):
                response_text = response_text.replace("```", "").strip()
            
            result = json.loads(response_text)
            
            logger.info("Gemini multi-prompt analysis completed successfully")
            return {"parsed_data": result}
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error in Gemini response: {e}")
            logger.error(f"Response text: {response.text[:500]}")
            raise ValueError(f"Invalid JSON response from AI: {str(e)}")
        except Exception as e:
            logger.error(f"Gemini multi-prompt analysis error: {e}")
            raise
        
    async def analyze_displacement_risk(
        self,
        job_title: str,
        skills: List[str],
        years_experience: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Analyze AI displacement risk using NextAI intelligence
        """
        try:
            prompt = f"""Analyze AI automation risk for {job_title} ({years_experience or 0}y exp) with skills: {', '.join(skills[:8])}.

Score 0-100 based on: routine work %, AI maturity, human judgment needs.
Risk: Critical(80-100/1-2y), High(60-79/2-5y), Medium(40-59/5-10y), Low(0-39/10+y)
Velocity: Immediate/Rapid(1-3y)/Moderate(3-7y)/Slow(7+y)

Return valid JSON only:
{{
    "ai_displacement_risk": {{
        "score": <float between 0-100>,
        "level": "<Low|Medium|High|Critical>",
        "velocity": "<Slow|Moderate|Rapid|Immediate>",
        "augmentation_potential": "<specific description of how NextAI can augment this role>",
        "reasoning": "<2-3 sentences with SPECIFIC examples for THIS job, mention actual tasks that are/aren't automatable>"
    }},
    "compatibility_score": <float 0-100 representing human-AI collaboration potential>,
    "human_advantage_factors": [
        "<specific factor 1 for {job_title}>",
        "<specific factor 2>",
        "<specific factor 3>"
    ],
    "automation_vulnerable_tasks": [
        "<task 1 that can be automated>",
        "<task 2>"
    ],
    "automation_resistant_tasks": [
        "<task 1 requiring human skills>",
        "<task 2>"
    ]
}}

BE SPECIFIC TO THE JOB. Avoid generic phrases. Use concrete examples."""

            response = self.model.generate_content(prompt)
            
            # Clean and parse the response
            cleaned_text = self._clean_json_response(response.text)
            result = json.loads(cleaned_text)
            
            # Validate that we got real data, not defaults
            if result.get("ai_displacement_risk", {}).get("score", 50) == 50.0:
                logger.warning(f"NextAI returned potentially generic score for {job_title}")
            
            logger.info(f"✅ NextAI displacement analysis complete for {job_title}: {result.get('ai_displacement_risk', {}).get('score', 'N/A')}%")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in NextAI analysis: {e}")
            logger.error(f"Response text: {response.text[:500] if 'response' in locals() else 'No response'}")
            raise HTTPException(
                status_code=500,
                detail=f"NextAI analysis failed: Unable to parse response. Please try again."
            )
        except Exception as e:
            logger.error(f"NextAI displacement analysis error: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"NextAI analysis encountered an error. Please try again."
            )

    async def generate_skill_insights(
        self,
        job_title: str,
        skills: List[str],
        years_experience: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive skill insights using Gemini
        """
        try:
            prompt = f"""Skill analysis for {job_title} ({years_experience or 0}y): {', '.join(skills[:8])}

JSON output:
{{
    "transferable_to": [{{"skill":"name","confidence":0.85,"reasoning":"why","source_skills":["s1","s2"]}}],
    "hidden_skills": ["implicit skill 1"],
    "skill_gaps_for_growth": [{{"skill":"needed","priority":"High","why_important":"reason","estimated_learning_time":"2-3mo","market_demand":"High","learn_difficulty":"Moderate"}}],
    "skill_strength_score": {{"overall_score":75,"interpretation":"brief"}}
}}"""

            response = self.model.generate_content(prompt)
            
            # Clean and parse the response
            cleaned_text = self._clean_json_response(response.text)
            result = json.loads(cleaned_text)
            
            logger.info(f"Gemini skill insights generated for {job_title}")
            return result
            
        except Exception as e:
            logger.error(f"Gemini skill insights error: {e}")
            return {
                "transferable_to": [],
                "hidden_skills": [],
                "skill_gaps_for_growth": [],
                "skill_strength_score": {
                    "overall_score": 70.0,
                    "interpretation": "Analysis unavailable"
                }
            }

    async def generate_career_roadmap(
        self,
        job_title: str,
        skills: List[str],
        location: str,
        years_experience: Optional[int],
        timeline: str = "5 years"
    ) -> Dict[str, Any]:
        """
        Generate multi-year career roadmap using Gemini
        """
        try:
            prompt = f"""
You are a senior career strategist. Create a detailed {timeline} career roadmap:

Current Role: {job_title}
Skills: {', '.join(skills)}
Location: {location}
Experience: {years_experience or 'Entry level'} years

Generate comprehensive roadmap in JSON format:
{{
    "3_year": {{
        "primary_path": {{
            "target_role": "role name",
            "milestone_title": "description",
            "skills_to_develop": ["skill 1", "skill 2"],
            "certifications": ["cert 1", "cert 2"],
            "estimated_salary_range": "$80k-$120k",
            "ai_resilience_score": 85
        }},
        "alternative_path": {{
            "target_role": "alternative role",
            "why_consider": "reasoning"
        }}
    }},
    "5_year": {{
        "primary_path": {{
            "target_role": "role name",
            "milestone_title": "description",
            "skills_to_develop": ["skill 1", "skill 2"],
            "certifications": ["cert 1", "cert 2"],
            "estimated_salary_range": "$100k-$150k",
            "ai_resilience_score": 88
        }}
    }},
    "10_year": {{
        "primary_path": {{
            "target_role": "role name",
            "milestone_title": "description",
            "skills_to_develop": ["skill 1", "skill 2"],
            "certifications": ["cert 1", "cert 2"],
            "estimated_salary_range": "$150k-$220k",
            "ai_resilience_score": 90
        }}
    }},
    "sankey_data": {{
        "nodes": [
            {{"id": "current", "name": "{job_title}", "category": "current"}},
            {{"id": "year3", "name": "3-Year Role", "category": "short_term"}},
            {{"id": "year5", "name": "5-Year Role", "category": "mid_term"}},
            {{"id": "year10", "name": "10-Year Role", "category": "long_term"}}
        ],
        "links": [
            {{"source": "current", "target": "year3", "value": 1, "skill": "key skill"}},
            {{"source": "year3", "target": "year5", "value": 1, "skill": "key skill"}},
            {{"source": "year5", "target": "year10", "value": 1, "skill": "key skill"}}
        ]
    }}
}}

Make the roadmap realistic, AI-resilient, and location-appropriate.
Return ONLY valid JSON.
"""

            response = self.model.generate_content(prompt)
            
            # Clean and parse the response
            cleaned_text = self._clean_json_response(response.text)
            result = json.loads(cleaned_text)
            
            logger.info(f"Gemini roadmap generated for {job_title}")
            return result
            
        except Exception as e:
            logger.error(f"Gemini roadmap generation error: {e}")
            # Fallback basic roadmap
            return self._generate_fallback_roadmap(job_title, timeline)

    async def generate_industry_benchmarks(
        self,
        job_title: str,
        skills: List[str],
        location: str,
        years_experience: Optional[int]
    ) -> Dict[str, Any]:
        """
        Generate industry benchmarking data using Gemini
        """
        try:
            prompt = f"""Benchmarks for {job_title} in {location} ({years_experience or 0}y): {', '.join(skills[:5])}

JSON:
{{
    "automation_risk_comparison": {{"your_score":45,"industry_average":52,"percentile":65,"comparison_text":"6.5pts below avg","trend":"improving"}},
    "skill_demand": {{"overall_score":78,"top_skills":[{{"name":"Skill1","demand":95,"growth":"+15%"}}],"skill_gaps":[{{"name":"Gap1","importance":85}}]}},
    "salary_benchmark": {{"your_estimated_range":"$90k-$130k","industry_median":110000,"percentile_25":85000,"percentile_50":110000,"percentile_75":140000,"percentile_90":175000,"your_position":"Above median"}},
    "career_progression": {{"pace":"Moderate","typical_years_to_next_level":3,"your_readiness_score":75}},
    "market_trends": {{"role_growth":"+18% annually","hiring_difficulty":"High","remote_availability":"85%","top_hiring_industries":["Tech","Finance"]}},
    "competitive_position": {{"peer_ranking":"Top 30%","strengths":["Strength1"],"areas_for_improvement":["Area1"]}}
}}

Use {location} market data."""

            response = self.model.generate_content(prompt)
            
            # Clean and parse the response
            cleaned_text = self._clean_json_response(response.text)
            result = json.loads(cleaned_text)
            
            logger.info(f"Gemini benchmarks generated for {job_title}")
            return result
            
        except Exception as e:
            logger.error(f"Gemini benchmarks error: {e}")
            return self._generate_fallback_benchmarks(job_title, location)

    def _generate_fallback_roadmap(self, job_title: str, timeline: str) -> Dict[str, Any]:
        """Fallback roadmap if Gemini fails"""
        return {
            "3_year": {
                "primary_path": {
                    "target_role": f"Senior {job_title}",
                    "milestone_title": "Advance to senior level",
                    "skills_to_develop": ["Leadership", "Advanced technical skills"],
                    "certifications": ["Industry certification"],
                    "estimated_salary_range": "$90k-$130k",
                    "ai_resilience_score": 75
                }
            },
            "5_year": {
                "primary_path": {
                    "target_role": f"Lead {job_title}",
                    "milestone_title": "Move to leadership role",
                    "skills_to_develop": ["Team management", "Strategy"],
                    "certifications": ["Management training"],
                    "estimated_salary_range": "$120k-$170k",
                    "ai_resilience_score": 80
                }
            },
            "10_year": {
                "primary_path": {
                    "target_role": f"Director of {job_title.split()[0]} Engineering",
                    "milestone_title": "Executive leadership",
                    "skills_to_develop": ["Executive presence", "Business strategy"],
                    "certifications": ["Executive MBA"],
                    "estimated_salary_range": "$180k-$250k",
                    "ai_resilience_score": 85
                }
            },
            "sankey_data": {
                "nodes": [
                    {"id": "current", "name": job_title, "category": "current"},
                    {"id": "year3", "name": f"Senior {job_title}", "category": "short_term"},
                    {"id": "year5", "name": f"Lead {job_title}", "category": "mid_term"},
                    {"id": "year10", "name": "Director", "category": "long_term"}
                ],
                "links": [
                    {"source": "current", "target": "year3", "value": 1, "skill": "Experience"},
                    {"source": "year3", "target": "year5", "value": 1, "skill": "Leadership"},
                    {"source": "year5", "target": "year10", "value": 1, "skill": "Strategy"}
                ]
            }
        }

    def _generate_fallback_benchmarks(self, job_title: str, location: str) -> Dict[str, Any]:
        """Fallback benchmarks if Gemini fails"""
        return {
            "automation_risk_comparison": {
                "your_score": 50.0,
                "industry_average": 55.0,
                "percentile": 55,
                "comparison_text": "Moderate risk compared to industry",
                "trend": "stable"
            },
            "skill_demand": {
                "overall_score": 70.0,
                "top_skills": [
                    {"name": "Core Skill", "demand": 80, "growth": "+10%"}
                ],
                "skill_gaps": []
            },
            "salary_benchmark": {
                "your_estimated_range": "$80k-$120k",
                "industry_median": 100000,
                "percentile_25": 75000,
                "percentile_50": 100000,
                "percentile_75": 125000,
                "percentile_90": 150000,
                "your_position": "At median"
            },
            "career_progression": {
                "pace": "Moderate",
                "typical_years_to_next_level": 3,
                "your_readiness_score": 70
            },
            "market_trends": {
                "role_growth": "+10% annually",
                "hiring_difficulty": "Moderate",
                "remote_availability": "60%",
                "top_hiring_industries": ["Technology", "Services"]
            },
            "competitive_position": {
                "peer_ranking": "Middle 50%",
                "strengths": ["Experience"],
                "areas_for_improvement": ["Skill development"]
            }
        }


# Global instance
gemini_analyzer = GeminiAnalyzer()
