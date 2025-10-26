"""
Trajectory Agent - Career Path Prediction & Forecasting
Analyzes career progression patterns and predicts future trajectories
"""

from typing import Dict, Any, List, Optional
from loguru import logger
import google.generativeai as genai
from datetime import datetime, timedelta

from app.core.config import settings
from app.models.user_profile import UserProfile
from app.models.orchestrator_schemas import JobOpportunity


class TrajectoryAgent:
    """
    Trajectory Agent - The career path forecaster
    
    Responsibilities:
    - Predict likely career paths over 3-5 year horizon
    - Analyze historical progression patterns
    - Identify optimal timing for career moves
    - Map potential promotion trajectories
    - Answer: "Where is this career path heading?"
    """
    
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    async def forecast_career_path(
        self,
        user_profile: UserProfile,
        current_role: Optional[str] = None,
        time_horizon_years: int = 3
    ) -> Dict[str, Any]:
        """
        Forecast likely career trajectory over specified time horizon
        
        Returns:
        - predicted_roles: List of likely future roles with timeframes
        - skill_evolution: Skills to acquire for progression
        - key_milestones: Critical decision points
        - probability_scores: Likelihood of each path
        """
        try:
            prompt = self._build_forecast_prompt(user_profile, current_role, time_horizon_years)
            
            response = self.model.generate_content(prompt)
            trajectory_data = self._parse_trajectory_response(response.text)
            
            logger.info(f"Forecasted {len(trajectory_data.get('predicted_roles', []))} career trajectories")
            
            return trajectory_data
            
        except Exception as e:
            logger.error(f"Trajectory forecasting failed: {e}")
            return self._get_fallback_trajectory()
    
    async def analyze_progression_timing(
        self,
        user_profile: UserProfile,
        target_role: str
    ) -> Dict[str, Any]:
        """
        Analyze optimal timing for career progression
        
        Returns readiness score and recommended timeline
        """
        try:
            prompt = f"""
            Analyze career progression timing for user with profile:
            Current Role: {user_profile.job_title or 'Not specified'}
            Skills: {', '.join(user_profile.skills[:10]) if user_profile.skills else 'None listed'}
            Experience Level: {user_profile.seniority_level or 'Unknown'}
            
            Target Role: {target_role}
            
            Provide:
            1. Readiness Score (0-100): How ready is the user NOW?
            2. Recommended Timeline: When should they make the move?
            3. Critical Gaps: What's blocking immediate transition?
            4. Quick Wins: What can accelerate readiness?
            
            Format as JSON with keys: readiness_score, timeline_months, critical_gaps, quick_wins
            """
            
            response = self.model.generate_content(prompt)
            timing_data = self._parse_timing_response(response.text)
            
            return timing_data
            
        except Exception as e:
            logger.error(f"Progression timing analysis failed: {e}")
            return {
                "readiness_score": 50,
                "timeline_months": 12,
                "critical_gaps": ["Unable to analyze - using defaults"],
                "quick_wins": ["Review profile completeness"]
            }
    
    async def identify_career_inflection_points(
        self,
        user_profile: UserProfile
    ) -> List[Dict[str, Any]]:
        """
        Identify critical decision points in career trajectory
        
        Returns key moments where career direction can change significantly
        """
        try:
            inflection_points = []
            
            # Analyze based on experience level
            if user_profile.seniority_level in ["junior", "mid"]:
                inflection_points.append({
                    "type": "skill_specialization",
                    "timeframe": "6-12 months",
                    "description": "Choose between specialist vs generalist path",
                    "impact": "high"
                })
            
            if user_profile.seniority_level in ["mid", "senior"]:
                inflection_points.append({
                    "type": "leadership_transition",
                    "timeframe": "12-18 months",
                    "description": "Decide between individual contributor vs management track",
                    "impact": "critical"
                })
            
            # Add data-driven insights
            prompt = f"""
            Based on this career profile, identify critical inflection points:
            Role: {user_profile.job_title}
            Level: {user_profile.seniority_level}
            Industry: {user_profile.industry or 'General'}
            
            List 2-3 key decision points in the next 3 years where career direction significantly changes.
            Format: JSON array with type, timeframe, description, impact
            """
            
            response = self.model.generate_content(prompt)
            ai_inflections = self._parse_inflection_response(response.text)
            inflection_points.extend(ai_inflections)
            
            return inflection_points
            
        except Exception as e:
            logger.error(f"Inflection point identification failed: {e}")
            return [{
                "type": "general_assessment",
                "timeframe": "ongoing",
                "description": "Regular career health check recommended",
                "impact": "medium"
            }]
    
    def _build_forecast_prompt(
        self,
        user_profile: UserProfile,
        current_role: Optional[str],
        years: int
    ) -> str:
        """Build prompt for career trajectory forecasting"""
        return f"""
        Forecast career trajectory for the next {years} years:
        
        Current Profile:
        - Role: {current_role or user_profile.job_title or 'Not specified'}
        - Skills: {', '.join(user_profile.skills[:15]) if user_profile.skills else 'None listed'}
        - Experience: {user_profile.seniority_level or 'Unknown'}
        - Industry: {user_profile.industry or 'General'}
        
        Provide realistic career progression forecast:
        1. Predicted Roles (with year markers and probability 0-100)
        2. Skill Evolution (skills to acquire year by year)
        3. Key Milestones (certifications, projects, transitions)
        4. Alternative Paths (at least 2 different trajectories)
        
        Format as JSON with keys: predicted_roles, skill_evolution, key_milestones, alternative_paths
        Each predicted_role should have: title, year, probability, salary_range, requirements
        """
    
    def _parse_trajectory_response(self, response_text: str) -> Dict[str, Any]:
        """Parse AI response into structured trajectory data"""
        try:
            # Simple JSON extraction
            import json
            import re
            
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                data = json.loads(json_match.group())
                return data
        except:
            pass
        
        # Fallback parsing
        return {
            "predicted_roles": [
                {
                    "title": "Senior Position",
                    "year": 1,
                    "probability": 70,
                    "salary_range": "Competitive",
                    "requirements": ["Continue skill development"]
                }
            ],
            "skill_evolution": {
                "year_1": ["Advanced technical skills"],
                "year_2": ["Leadership capabilities"],
                "year_3": ["Strategic thinking"]
            },
            "key_milestones": [
                "Complete major project",
                "Gain leadership experience",
                "Expand professional network"
            ],
            "alternative_paths": [
                "Technical specialist track",
                "Management track"
            ]
        }
    
    def _parse_timing_response(self, response_text: str) -> Dict[str, Any]:
        """Parse timing analysis response"""
        try:
            import json
            import re
            
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return {
            "readiness_score": 60,
            "timeline_months": 9,
            "critical_gaps": ["Experience gap", "Skill development needed"],
            "quick_wins": ["Build portfolio", "Get certification"]
        }
    
    def _parse_inflection_response(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse inflection points from AI response"""
        try:
            import json
            import re
            
            json_match = re.search(r'\[[\s\S]*\]', response_text)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return []
    
    def _get_fallback_trajectory(self) -> Dict[str, Any]:
        """Fallback trajectory when AI fails"""
        return {
            "predicted_roles": [],
            "skill_evolution": {},
            "key_milestones": ["Review career goals regularly"],
            "alternative_paths": ["Continue in current field", "Explore adjacent roles"]
        }
