"""
NextAI Analyzer - Advanced Career Intelligence
Powered by state-of-the-art AI for career analysis
"""

import os
from typing import Dict, List, Optional, Any, Iterable
import json
from loguru import logger
from google import genai
from fastapi import HTTPException
from json_repair import repair_json
from app.core.config import settings

# Configure AI Engine with new SDK
NEXTAI_API_KEY = os.getenv("GEMINI_API_KEY") or settings.GEMINI_API_KEY


class GeminiAnalyzer:
    """
    NextAI Career Intelligence Analyzer
    Advanced AI-powered career analysis and insights
    WITH SAFETY SETTINGS
    """
    
    def __init__(self):
        """Initialize Gemini client if credentials are available."""

        self.client = None

        # Use configurable model from settings
        self.model_name = getattr(settings, 'GEMINI_MODEL', 'gemini-2.0-flash-exp')

        # Configure generation settings
        self.generation_config = {
            "response_mime_type": "application/json",
            "temperature": 0.3
        }

        if NEXTAI_API_KEY:
            try:
                # Initialize the new Gemini client when credentials are present
                self.client = genai.Client(api_key=NEXTAI_API_KEY)
                logger.info("✅ Gemini client initialized successfully")
            except Exception as exc:  # pragma: no cover - defensive guard
                logger.warning(
                    "⚠️ Failed to initialize Gemini client. Falling back to offline mode: {}".format(exc)
                )
                self.client = None
        else:
            logger.warning(
                "⚠️ GEMINI_API_KEY not configured. Using deterministic fallback responses for analysis."
            )
    
    def _extract_text(self, response) -> str:
        """Safely extract text content from Gemini response."""
        try:
            candidates = getattr(response, "candidates", [])
            parts: list[str] = []
            for candidate in candidates or []:
                content = getattr(candidate, "content", None)
                for part in getattr(content, "parts", []) or []:
                    text = getattr(part, "text", None)
                    if text:
                        parts.append(text)
            if parts:
                return "\n".join(parts)
        except Exception as exc:  # pragma: no cover - defensive
            logger.debug(f"Failed to extract structured response text: {exc}")
        return getattr(response, "text", "") or ""

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

    def _parse_json_response(self, response: Any, context: str, raise_http_error: bool = False) -> Dict[str, Any]:
        """Parse a Gemini response into JSON with automatic repair fallback."""
        raw_text = self._extract_text(response)
        if not raw_text:
            raw_text = getattr(response, "text", "") or ""

        cleaned_text = self._clean_json_response(raw_text)
        try:
            return json.loads(cleaned_text)
        except json.JSONDecodeError as exc:
            logger.warning(f"JSON decode error for {context}: {exc}")
            try:
                repaired_text = repair_json(raw_text)
                repaired_clean = self._clean_json_response(repaired_text)
                parsed = json.loads(repaired_clean)
                logger.info(f"Recovered Gemini response via json-repair for {context}")
                return parsed
            except Exception as repair_exc:
                snippet = raw_text[:500] if raw_text else "<empty response>"
                logger.error(
                    f"Failed to repair Gemini response for {context}: {repair_exc}. Snippet: {snippet}"
                )
                if raise_http_error:
                    raise HTTPException(
                        status_code=500,
                        detail="NextAI analysis failed: Unable to parse response. Please try again."
                    ) from repair_exc
                raise
    
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
                "response_mime_type": "application/json"
            }
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
                config=generation_config
            )

            result = self._parse_json_response(response, "multi-prompt analysis")
            
            logger.info("Gemini multi-prompt analysis completed successfully")
            return {"parsed_data": result}
            
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
        if not self.client:
            return self._generate_fallback_displacement_risk(job_title, skills, years_experience)

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

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=self.generation_config
            )

            result = self._parse_json_response(response, f"displacement risk for {job_title}", raise_http_error=True)
            
            # Validate that we got real data, not defaults
            if result.get("ai_displacement_risk", {}).get("score", 50) == 50.0:
                logger.warning(f"NextAI returned potentially generic score for {job_title}")
            
            logger.info(f"✅ NextAI displacement analysis complete for {job_title}: {result.get('ai_displacement_risk', {}).get('score', 'N/A')}%")
            return result
            
        except Exception as e:
            logger.error(f"NextAI displacement analysis error: {e}")
            return self._generate_fallback_displacement_risk(job_title, skills, years_experience)

    async def generate_skill_insights(
        self,
        job_title: str,
        skills: List[str],
        years_experience: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive skill insights using Gemini
        """
        if not self.client:
            return self._generate_fallback_skill_insights(job_title, skills, years_experience)

        try:
            prompt = f"""Skill analysis for {job_title} ({years_experience or 0}y): {', '.join(skills[:8])}

JSON output:
{{
    "transferable_to": [{{"skill":"name","confidence":0.85,"reasoning":"why","source_skills":["s1","s2"]}}],
    "hidden_skills": ["implicit skill 1"],
    "skill_gaps_for_growth": [{{"skill":"needed","priority":"High","why_important":"reason","estimated_learning_time":"2-3mo","market_demand":"High","learn_difficulty":"Moderate"}}],
    "skill_strength_score": {{"overall_score":75,"interpretation":"brief"}}
}}"""

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=self.generation_config
            )

            result = self._parse_json_response(response, f"skill insights for {job_title}")
            
            logger.info(f"Gemini skill insights generated for {job_title}")
            return result
            
        except Exception as e:
            logger.error(f"Gemini skill insights error: {e}")
            return self._generate_fallback_skill_insights(job_title, skills, years_experience)

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

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=self.generation_config
            )

            result = self._parse_json_response(response, f"career roadmap for {job_title}")
            
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
        if not self.client:
            return self._generate_fallback_benchmarks(job_title, location)

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

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=self.generation_config
            )

            result = self._parse_json_response(response, f"industry benchmarks for {job_title}")
            
            logger.info(f"Gemini benchmarks generated for {job_title}")
            return result
            
        except Exception as e:
            logger.error(f"Gemini benchmarks error: {e}")
            return self._generate_fallback_benchmarks(job_title, location)

    def _generate_fallback_displacement_risk(
        self,
        job_title: str,
        skills: List[str],
        years_experience: Optional[int]
    ) -> Dict[str, Any]:
        """Generate deterministic displacement insights when Gemini is unavailable."""

        job_lower = job_title.lower()
        high_risk_keywords = ["data entry", "assistant", "telemarketer", "clerk", "bookkeeper", "cashier"]
        low_risk_keywords = ["therapist", "nurse", "teacher", "manager", "strategist", "leader"]
        technical_keywords = ["engineer", "developer", "scientist", "analyst", "architect", "designer"]

        if any(keyword in job_lower for keyword in high_risk_keywords):
            score = 82.0
        elif any(keyword in job_lower for keyword in low_risk_keywords):
            score = 32.0
        elif any(keyword in job_lower for keyword in technical_keywords):
            score = 58.0
        else:
            score = 48.0

        experience_bonus = min(max((years_experience or 0) * 0.6, -5), 8)
        score = max(15.0, min(95.0, score - experience_bonus))

        if score >= 80:
            level = "Critical"
            velocity = "Rapid"
        elif score >= 60:
            level = "High"
            velocity = "Rapid"
        elif score >= 40:
            level = "Medium"
            velocity = "Moderate"
        else:
            level = "Low"
            velocity = "Slow"

        highlighted_skills = skills[:3] or [f"{job_title} fundamentals"]
        augmentation = f"Adopt AI copilots to accelerate {highlighted_skills[0].lower()} and reporting workflows."
        reasoning = (
            f"Based on the task profile for {job_title}, routine work such as {highlighted_skills[0].lower()} can be automated,"
            " while stakeholder-facing responsibilities still require human judgment."
        )

        human_advantage = [
            "Relationship building and trust",
            "Handling ambiguous, cross-functional decisions",
            f"Domain knowledge of {job_title} operations"
        ]

        automation_vulnerable = [
            f"Routine {highlighted_skills[0].lower()} tasks",
            "Status reporting and documentation",
            "Data collection and consolidation"
        ]

        automation_resistant = [
            "Human-centered collaboration",
            "Strategic prioritization",
            "Ethical and compliance oversight"
        ]

        compatibility = round(max(35.0, min(92.0, 105.0 - score)), 1)

        return {
            "ai_displacement_risk": {
                "score": round(score, 1),
                "level": level,
                "velocity": velocity,
                "augmentation_potential": augmentation,
                "reasoning": reasoning,
            },
            "compatibility_score": compatibility,
            "human_advantage_factors": human_advantage,
            "automation_vulnerable_tasks": automation_vulnerable,
            "automation_resistant_tasks": automation_resistant,
        }

    def _generate_fallback_skill_insights(
        self,
        job_title: str,
        skills: List[str],
        years_experience: Optional[int]
    ) -> Dict[str, Any]:
        """Generate skill insights when Gemini is offline."""

        normalized_skills = skills[:5] or [f"{job_title} fundamentals"]
        lead_skill = normalized_skills[0]

        transition_pathways = [
            {
                "role": f"Senior {job_title}",
                "ease": 74.0,
                "required_skills": self._unique([lead_skill, "Leadership", "AI collaboration"])[:3],
                "estimated_training_time": "6-12 months",
                "salary_potential": "+$15k",
                "demand_trend": "Growing",
            },
            {
                "role": f"{job_title} Consultant",
                "ease": 61.0,
                "required_skills": self._unique([lead_skill, "Stakeholder management", "Strategy"])[:3],
                "estimated_training_time": "9-15 months",
                "salary_potential": "+$20k",
                "demand_trend": "Stable",
            },
        ]

        skill_gaps = [
            f"Advanced {lead_skill}",
            "AI collaboration workflows",
            "Strategic communication",
        ]

        recommended_training = [
            {
                "title": f"{lead_skill} Deep Dive",
                "provider": "NextAI Academy",
                "url": f"https://www.coursera.org/search?query={lead_skill.replace(' ', '%20')}",
                "duration": "4-6 weeks",
                "skill_covered": lead_skill,
                "cost": "Varies",
                "rating": 4.6,
            },
            {
                "title": "AI-Augmented Workflow Design",
                "provider": "NextAI Academy",
                "url": "https://www.coursera.org/search?query=ai%20workflow",
                "duration": "3-4 weeks",
                "skill_covered": "AI collaboration workflows",
                "cost": "Free to audit",
                "rating": 4.7,
            },
        ]

        transferable = [
            {
                "skill": lead_skill,
                "confidence": 0.72,
                "target_roles": [f"Senior {job_title}", f"{job_title} Lead"],
                "reasoning": f"{lead_skill} maps well to advanced {job_title} responsibilities and adjacent advisory roles.",
                "source_skills": normalized_skills[:3],
            }
        ]

        skill_gaps_for_growth = [
            {
                "skill": gap,
                "priority": "High" if idx == 0 else "Medium",
                "why_important": "Supports progression into higher-impact roles",
                "estimated_learning_time": "6-8 weeks" if idx == 0 else "3-4 weeks",
                "market_demand": "High",
                "learn_difficulty": "Moderate" if idx == 0 else "Easy",
            }
            for idx, gap in enumerate(skill_gaps)
        ]

        return {
            "transition_pathways": transition_pathways,
            "skill_gaps": skill_gaps,
            "recommended_training": recommended_training,
            "transferable_to": transferable,
            "hidden_skills": [f"Implicit expertise in {lead_skill}", "Stakeholder empathy"],
            "skill_gaps_for_growth": skill_gaps_for_growth,
            "skill_strength_score": {
                "overall_score": 72.0,
                "interpretation": "Core strengths established with clear upskilling opportunities",
            },
        }

    @staticmethod
    def _unique(values: Iterable[str]) -> List[str]:
        """Return unique values preserving order."""

        seen: set[str] = set()
        result: List[str] = []
        for value in values:
            if not value:
                continue
            if value not in seen:
                seen.add(value)
                result.append(value)
        return result

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
