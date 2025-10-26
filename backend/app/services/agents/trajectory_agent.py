"""
Trajectory Agent - Career Path Prediction & Forecasting
Predicts user's next 3 likely career paths with probabilities and timelines
"""

from typing import Dict, Any, List, Optional
from loguru import logger
import google.generativeai as genai
from datetime import datetime, timedelta

from app.core.config import settings
from app.models.user_profile import UserProfile


class CareerPath(Dict):
    """A predicted career trajectory"""
    pass


class TrajectoryAgent:
    """
    Trajectory Agent - The future predictor
    
    Responsibilities:
    - Predict next 3 likely career paths
    - Calculate probability, timeline, salary ceiling for each
    - Map skill unlocks needed for each path
    - Answer: "Where can this person go next, and how long will it take?"
    """
    
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    async def forecast_career_paths(
        self,
        user_profile: UserProfile,
        market_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Predict 3 most likely career trajectories
        
        Returns:
        {
            "career_forecast": [
                {
                    "path_name": "Senior Behavior Specialist",
                    "probability": 75,
                    "timeline_months": 12,
                    "salary_range": {"min": 85000, "max": 110000},
                    "required_skills": ["Advanced crisis intervention", "Team leadership"],
                    "skill_unlock_sequence": [...],
                    "reasoning": "Your 8 years in special ed positions you perfectly..."
                }
            ],
            "current_trajectory_score": 68,
            "pivot_opportunities": [...]
        }
        """
        
        try:
            prompt = self._build_trajectory_prompt(user_profile, market_context)
            
            response = self.model.generate_content(prompt)
            
            forecast = self._parse_trajectory_response(response.text, user_profile)
            
            logger.info(f"Generated {len(forecast['career_forecast'])} career paths for user {user_profile.user_id}")
            
            return forecast
            
        except Exception as e:
            logger.error(f"Error forecasting career paths: {e}")
            return self._create_fallback_forecast(user_profile)
    
    def _build_trajectory_prompt(
        self,
        user_profile: UserProfile,
        market_context: Optional[Dict[str, Any]]
    ) -> str:
        """Build AI prompt for trajectory forecasting"""
        
        user_skills = [s.name for s in user_profile.skills[:15]]
        user_role = user_profile.current_role or "Not specified"
        years_exp = user_profile.years_total_experience or 0
        
        goals_text = ""
        if user_profile.career_goals:
            goals_text = "\n".join([f"- {g.timeframe}: {g.description}" for g in user_profile.career_goals[:3]])
        
        market_intel = ""
        if market_context:
            market_intel = f"\n\nMarket Context:\n{market_context.get('summary', 'Not available')}"
        
        prompt = f"""You are a career trajectory analyst. Predict the 3 most likely career paths for this person.

User Profile:
- Current Role: {user_role}
- Years Experience: {years_exp}
- Skills: {', '.join(user_skills)}
- Career Goals:
{goals_text or '- Not specified'}
{market_intel}

Predict 3 realistic career paths they could take in the next 12-36 months.

For each path, provide:
1. Path name (target role/position)
2. Probability (0-100) - how likely they'll succeed in this transition
3. Timeline in months
4. Salary range (realistic market rates)
5. Required skills they need to develop
6. Skill unlock sequence (what to learn first, second, third)
7. Reasoning (why this path makes sense for them)

Also include:
- current_trajectory_score (0-100): How strong is their current career momentum?
- pivot_opportunities: Alternative directions if they want a major change

Return ONLY valid JSON:
{{
  "career_forecast": [
    {{
      "path_name": "Senior Behavior Intervention Specialist",
      "probability": 75,
      "timeline_months": 12,
      "salary_range": {{"min": 80000, "max": 110000, "currency": "USD"}},
      "required_skills": ["Advanced crisis de-escalation", "Program leadership"],
      "skill_unlock_sequence": [
        "Get certified in Applied Behavior Analysis",
        "Lead at least 2 intervention programs",
        "Document measurable student outcomes"
      ],
      "reasoning": "Your 8 years in special ed + proven behavioral work positions you perfectly. High demand, low automation risk."
    }}
  ],
  "current_trajectory_score": 68,
  "pivot_opportunities": ["EdTech Product Manager", "School District Consultant"]
}}

Be realistic, data-driven, and consider automation risk. Output ONLY valid JSON."""

        return prompt
    
    def _parse_trajectory_response(self, response_text: str, user_profile: UserProfile) -> Dict[str, Any]:
        """Parse AI response into structured forecast"""
        
        import json
        import re
        
        try:
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            
            if json_match:
                forecast_data = json.loads(json_match.group())
                
                # Validate structure
                if "career_forecast" not in forecast_data:
                    raise ValueError("Missing career_forecast")
                
                return forecast_data
            else:
                raise ValueError("No JSON found in response")
                
        except Exception as e:
            logger.error(f"Error parsing trajectory response: {e}")
            return self._create_fallback_forecast(user_profile)
    
    def _create_fallback_forecast(self, user_profile: UserProfile) -> Dict[str, Any]:
        """Create basic forecast when AI fails"""
        
        current_role = user_profile.current_role or "your field"
        
        return {
            "career_forecast": [
                {
                    "path_name": f"Senior {current_role}",
                    "probability": 65,
                    "timeline_months": 18,
                    "salary_range": {"min": 70000, "max": 95000, "currency": "USD"},
                    "required_skills": ["Leadership", "Strategic planning"],
                    "skill_unlock_sequence": ["Gain management experience", "Build strategic portfolio"],
                    "reasoning": "Natural progression based on your experience level."
                },
                {
                    "path_name": f"{current_role} - Specialized Track",
                    "probability": 55,
                    "timeline_months": 12,
                    "salary_range": {"min": 65000, "max": 85000, "currency": "USD"},
                    "required_skills": ["Deep specialization", "Certification"],
                    "skill_unlock_sequence": ["Get industry certification", "Build specialized expertise"],
                    "reasoning": "Deepen expertise in your current domain."
                }
            ],
            "current_trajectory_score": 60,
            "pivot_opportunities": ["Adjacent roles in growing industries"]
        }
    
    def calculate_trajectory_score(self, user_profile: UserProfile) -> int:
        """
        Calculate current career momentum/trajectory strength (0-100)
        
        Factors:
        - Recent skill growth
        - Market demand for current skills
        - Years of experience vs typical career arc
        - Goal clarity
        """
        
        score = 50  # Start neutral
        
        # Boost for clear goals
        if user_profile.career_goals and len(user_profile.career_goals) > 0:
            score += 15
        
        # Boost for diverse skill set
        if user_profile.skills and len(user_profile.skills) > 5:
            score += 10
        
        # Boost for recent activity
        if user_profile.total_interactions > 10:
            score += 10
        
        # Penalize for high burnout
        if user_profile.burnout_level and user_profile.burnout_level > 7:
            score -= 20
        
        # Boost for confidence
        if user_profile.confidence_level and user_profile.confidence_level > 7:
            score += 15
        
        return max(min(score, 100), 0)
