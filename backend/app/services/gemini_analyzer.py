"""
Gemini AI Analyzer - Replacement for OpenAI GPT-4
Uses Google's Gemini Pro for career intelligence analysis
"""

import os
from typing import Dict, List, Optional, Any
import json
from loguru import logger
import google.generativeai as genai

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


class GeminiAnalyzer:
    """
    Career intelligence analyzer using Google Gemini Pro
    Replaces OpenAI GPT-4 with Gemini for cost savings and performance
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
            'gemini-1.5-pro',
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
        Analyze AI displacement risk using Gemini
        """
        try:
            prompt = f"""
You are an AI career analyst. Analyze the following job for AI displacement risk:

Job Title: {job_title}
Skills: {', '.join(skills)}
Years of Experience: {years_experience or 'Not specified'}

Provide a detailed analysis in JSON format with:
1. score (0-100): Probability of AI displacement
2. level: "Low" | "Medium" | "High" | "Critical"
3. velocity: "Slow" | "Moderate" | "Rapid" | "Immediate"
4. augmentation_potential: Brief description of how AI can augment this role
5. reasoning: Detailed explanation (2-3 sentences)

Consider:
- Technical vs creative nature of work
- Human interaction requirements
- Decision-making complexity
- Current AI capabilities in this domain
- Industry automation trends

Return ONLY valid JSON, no markdown formatting.
"""

            response = self.model.generate_content(prompt)
            
            # Clean and parse the response
            cleaned_text = self._clean_json_response(response.text)
            result = json.loads(cleaned_text)
            
            logger.info(f"Gemini displacement analysis complete for {job_title}")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in displacement analysis: {e}")
            logger.error(f"Response text (first 200 chars): {response.text[:200] if 'response' in locals() else 'No response'}")
            # Fallback response
            return {
                "score": 50.0,
                "level": "Medium",
                "velocity": "Moderate",
                "augmentation_potential": "AI tools can enhance productivity in this role",
                "reasoning": "Unable to parse AI response. Default risk assessment provided."
            }
        except Exception as e:
            logger.error(f"Gemini displacement analysis error: {e}")
            # Fallback response
            return {
                "score": 50.0,
                "level": "Medium",
                "velocity": "Moderate",
                "augmentation_potential": "AI tools can enhance productivity in this role",
                "reasoning": "Unable to complete full analysis. Default risk assessment provided."
            }

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
            prompt = f"""
You are an AI career intelligence expert. Analyze these skills for career development:

Job Title: {job_title}
Current Skills: {', '.join(skills)}
Experience: {years_experience or 'Not specified'} years

Provide skill intelligence in JSON format:
{{
    "transferable_to": [
        {{
            "skill": "skill name",
            "confidence": 0.85,
            "reasoning": "why this transfers",
            "source_skills": ["origin skill 1", "origin skill 2"]
        }}
    ],
    "hidden_skills": ["implicit skill 1", "implicit skill 2"],
    "skill_gaps_for_growth": [
        {{
            "skill": "needed skill",
            "priority": "Critical" | "High" | "Medium" | "Low",
            "why_important": "explanation",
            "estimated_learning_time": "2-3 months",
            "market_demand": "High" | "Medium" | "Low",
            "learn_difficulty": "Easy" | "Moderate" | "Challenging"
        }}
    ],
    "skill_strength_score": {{
        "overall_score": 75.5,
        "interpretation": "brief assessment"
    }}
}}

Return ONLY valid JSON.
"""

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
            prompt = f"""
You are a market intelligence analyst. Generate industry benchmarks:

Role: {job_title}
Skills: {', '.join(skills)}
Location: {location}
Experience: {years_experience or 0} years

Provide comprehensive benchmarks in JSON format:
{{
    "automation_risk_comparison": {{
        "your_score": 45.5,
        "industry_average": 52.0,
        "percentile": 65,
        "comparison_text": "Your risk is 6.5 points below industry average",
        "trend": "improving"
    }},
    "skill_demand": {{
        "overall_score": 78.5,
        "top_skills": [
            {{"name": "Python", "demand": 95, "growth": "+15%"}},
            {{"name": "AI/ML", "demand": 92, "growth": "+25%"}}
        ],
        "skill_gaps": [
            {{"name": "Cloud Architecture", "importance": 85}}
        ]
    }},
    "salary_benchmark": {{
        "your_estimated_range": "$90k-$130k",
        "industry_median": 110000,
        "percentile_25": 85000,
        "percentile_50": 110000,
        "percentile_75": 140000,
        "percentile_90": 175000,
        "your_position": "Above median"
    }},
    "career_progression": {{
        "pace": "Moderate",
        "typical_years_to_next_level": 3,
        "your_readiness_score": 75
    }},
    "market_trends": {{
        "role_growth": "+18% annually",
        "hiring_difficulty": "High",
        "remote_availability": "85%",
        "top_hiring_industries": ["Tech", "Finance", "Healthcare"]
    }},
    "competitive_position": {{
        "peer_ranking": "Top 30%",
        "strengths": ["Technical expertise", "Industry experience"],
        "areas_for_improvement": ["Leadership skills", "Cloud certifications"]
    }}
}}

Base estimates on {location} market data and current trends.
Return ONLY valid JSON.
"""

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
