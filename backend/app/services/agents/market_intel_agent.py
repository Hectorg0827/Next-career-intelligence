"""
Market Intel Agent - Real-time market trends and industry intelligence
Monitors job market conditions, salary trends, and demand signals
"""

from typing import Dict, Any, List, Optional
from loguru import logger
import google.generativeai as genai
from datetime import datetime

from app.core.config import settings
from app.models.user_profile import UserProfile


class MarketIntelAgent:
    """
    Market Intel Agent - The market analyst
    
    Responsibilities:
    - Track real-time job market trends
    - Monitor salary movements by role/location
    - Identify emerging skill demands
    - Detect industry shifts and disruptions
    - Answer: "What's happening in the market right now?"
    """
    
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    async def get_market_snapshot(
        self,
        role: str,
        location: Optional[str] = None,
        industry: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get current market snapshot for a specific role/location
        
        Returns:
        - demand_level: high/medium/low
        - salary_trend: increasing/stable/decreasing
        - competition_level: Number of candidates per opening
        - hot_skills: Most in-demand skills
        - market_insights: Key observations
        """
        try:
            prompt = self._build_market_snapshot_prompt(role, location, industry)
            
            response = self.model.generate_content(prompt)
            market_data = self._parse_market_response(response.text)
            
            # Enrich with synthetic data (would use real APIs in production)
            market_data["timestamp"] = datetime.utcnow().isoformat()
            market_data["confidence_score"] = 0.85
            
            logger.info(f"Market snapshot for {role}: {market_data.get('demand_level', 'unknown')}")
            
            return market_data
            
        except Exception as e:
            logger.error(f"Market snapshot failed: {e}")
            return self._get_fallback_market_data(role)
    
    async def analyze_salary_trends(
        self,
        role: str,
        location: Optional[str] = None,
        years_experience: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Analyze salary trends and provide compensation intelligence
        
        Returns:
        - current_range: {min, max, median}
        - trend_direction: up/down/stable
        - percentile_breakdown: 25th, 50th, 75th, 90th percentiles
        - factors_affecting: List of factors driving changes
        """
        try:
            prompt = f"""
            Analyze current salary trends for:
            Role: {role}
            Location: {location or 'United States'}
            Experience: {years_experience or 'All levels'}
            
            Provide realistic salary data:
            1. Current Range (min, max, median in USD)
            2. Trend Direction (increasing/stable/decreasing with %)
            3. Percentile Breakdown (25th, 50th, 75th, 90th)
            4. Key Factors (what's driving salary changes)
            
            Format as JSON with keys: current_range, trend_direction, percentile_breakdown, factors_affecting
            """
            
            response = self.model.generate_content(prompt)
            salary_data = self._parse_salary_response(response.text, role)
            
            return salary_data
            
        except Exception as e:
            logger.error(f"Salary analysis failed: {e}")
            return self._get_fallback_salary_data(role)
    
    async def identify_emerging_skills(
        self,
        industry: str,
        lookback_months: int = 6
    ) -> List[Dict[str, Any]]:
        """
        Identify skills that are rapidly growing in demand
        
        Returns list of emerging skills with growth metrics
        """
        try:
            prompt = f"""
            Identify emerging skills in {industry} industry over the last {lookback_months} months.
            
            For each skill provide:
            1. Skill Name
            2. Growth Rate (% increase in job postings)
            3. Adoption Stage (emerging/growing/mainstream)
            4. Related Roles (which jobs need this skill)
            
            Return top 10 skills as JSON array with keys: skill_name, growth_rate, adoption_stage, related_roles
            """
            
            response = self.model.generate_content(prompt)
            skills_data = self._parse_skills_response(response.text)
            
            logger.info(f"Identified {len(skills_data)} emerging skills in {industry}")
            
            return skills_data
            
        except Exception as e:
            logger.error(f"Emerging skills identification failed: {e}")
            return self._get_fallback_skills_data(industry)
    
    async def detect_market_disruptions(
        self,
        industry: str,
        user_profile: Optional[UserProfile] = None
    ) -> List[Dict[str, Any]]:
        """
        Detect major disruptions affecting the job market
        
        Returns:
        - List of disruptions (AI adoption, layoffs, industry shifts)
        - Impact level (critical/high/medium/low)
        - Recommended actions
        """
        try:
            disruptions = []
            
            # AI/Automation disruption (always relevant)
            disruptions.append({
                "type": "ai_automation",
                "title": "AI and Automation Acceleration",
                "impact_level": "high",
                "description": "Rapid AI adoption is changing skill requirements across industries",
                "affected_roles": ["Data Entry", "Customer Service", "Content Writing"],
                "recommendations": [
                    "Develop AI literacy and collaboration skills",
                    "Focus on uniquely human capabilities",
                    "Learn to work alongside AI tools"
                ],
                "urgency": "ongoing"
            })
            
            # Industry-specific analysis
            if industry:
                prompt = f"""
                Identify major disruptions affecting {industry} industry jobs:
                
                Consider:
                - Technology changes
                - Economic shifts
                - Regulatory changes
                - Market consolidation
                
                Return 2-3 key disruptions as JSON array with:
                type, title, impact_level, description, affected_roles, recommendations, urgency
                """
                
                response = self.model.generate_content(prompt)
                ai_disruptions = self._parse_disruptions_response(response.text)
                disruptions.extend(ai_disruptions)
            
            return disruptions[:5]  # Top 5 most relevant
            
        except Exception as e:
            logger.error(f"Disruption detection failed: {e}")
            return [{
                "type": "general",
                "title": "Market Volatility",
                "impact_level": "medium",
                "description": "General market uncertainty requires adaptability",
                "affected_roles": ["All roles"],
                "recommendations": ["Stay informed", "Build diverse skill set"],
                "urgency": "ongoing"
            }]
    
    async def get_demand_forecast(
        self,
        role: str,
        timeframe_months: int = 12
    ) -> Dict[str, Any]:
        """
        Forecast demand trends for a specific role
        
        Returns projected demand over timeframe
        """
        try:
            prompt = f"""
            Forecast job demand for {role} over the next {timeframe_months} months.
            
            Provide:
            1. Demand Trajectory (increasing/stable/decreasing)
            2. Growth Rate (% change expected)
            3. Key Drivers (what's influencing demand)
            4. Risk Factors (what could change the forecast)
            
            Format as JSON with keys: trajectory, growth_rate, key_drivers, risk_factors
            """
            
            response = self.model.generate_content(prompt)
            forecast_data = self._parse_forecast_response(response.text)
            
            return forecast_data
            
        except Exception as e:
            logger.error(f"Demand forecast failed: {e}")
            return {
                "trajectory": "stable",
                "growth_rate": 0.0,
                "key_drivers": ["Market conditions"],
                "risk_factors": ["Economic uncertainty"]
            }
    
    # Helper methods for prompt building and parsing
    
    def _build_market_snapshot_prompt(
        self,
        role: str,
        location: Optional[str],
        industry: Optional[str]
    ) -> str:
        """Build prompt for market snapshot"""
        return f"""
        Provide current job market snapshot:
        
        Role: {role}
        Location: {location or 'United States'}
        Industry: {industry or 'General'}
        
        Analyze:
        1. Demand Level (high/medium/low and trend)
        2. Salary Trend (increasing/stable/decreasing with %)
        3. Competition Level (candidates per opening estimate)
        4. Hot Skills (top 5 most requested skills)
        5. Market Insights (2-3 key observations)
        
        Format as JSON with keys: demand_level, salary_trend, competition_level, hot_skills, market_insights
        """
    
    def _parse_market_response(self, response_text: str) -> Dict[str, Any]:
        """Parse market snapshot response"""
        try:
            import json
            import re
            
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return {
            "demand_level": "medium",
            "salary_trend": "stable",
            "competition_level": "moderate",
            "hot_skills": ["Communication", "Problem Solving", "Technical Skills"],
            "market_insights": ["Market conditions vary by location", "Skills are key differentiator"]
        }
    
    def _parse_salary_response(self, response_text: str, role: str) -> Dict[str, Any]:
        """Parse salary analysis response"""
        try:
            import json
            import re
            
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        # Fallback with reasonable defaults
        return self._get_fallback_salary_data(role)
    
    def _parse_skills_response(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse emerging skills response"""
        try:
            import json
            import re
            
            json_match = re.search(r'\[[\s\S]*\]', response_text)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return []
    
    def _parse_disruptions_response(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse disruptions response"""
        try:
            import json
            import re
            
            json_match = re.search(r'\[[\s\S]*\]', response_text)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return []
    
    def _parse_forecast_response(self, response_text: str) -> Dict[str, Any]:
        """Parse demand forecast response"""
        try:
            import json
            import re
            
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return {
            "trajectory": "stable",
            "growth_rate": 0.0,
            "key_drivers": ["Standard market forces"],
            "risk_factors": ["Economic conditions"]
        }
    
    def _get_fallback_market_data(self, role: str) -> Dict[str, Any]:
        """Fallback market data"""
        return {
            "demand_level": "medium",
            "salary_trend": "stable",
            "competition_level": "moderate",
            "hot_skills": ["Industry knowledge", "Technical skills", "Communication"],
            "market_insights": [
                f"{role} positions remain in demand",
                "Continuous learning is essential"
            ],
            "timestamp": datetime.utcnow().isoformat(),
            "confidence_score": 0.5
        }
    
    def _get_fallback_salary_data(self, role: str) -> Dict[str, Any]:
        """Fallback salary data"""
        # Simple role-based salary estimates
        base_salaries = {
            "software engineer": {"min": 80000, "max": 150000, "median": 115000},
            "data scientist": {"min": 90000, "max": 160000, "median": 125000},
            "product manager": {"min": 100000, "max": 170000, "median": 135000},
            "designer": {"min": 60000, "max": 120000, "median": 90000},
        }
        
        role_lower = role.lower()
        salary_range = base_salaries.get(role_lower, {"min": 50000, "max": 100000, "median": 75000})
        
        return {
            "current_range": salary_range,
            "trend_direction": "stable (0-2% growth)",
            "percentile_breakdown": {
                "25th": int(salary_range["min"] * 1.1),
                "50th": salary_range["median"],
                "75th": int(salary_range["max"] * 0.85),
                "90th": salary_range["max"]
            },
            "factors_affecting": [
                "Experience level",
                "Location and cost of living",
                "Company size and funding",
                "Market demand for skills"
            ]
        }
    
    def _get_fallback_skills_data(self, industry: str) -> List[Dict[str, Any]]:
        """Fallback emerging skills data"""
        return [
            {
                "skill_name": "AI/ML Tools",
                "growth_rate": 45.0,
                "adoption_stage": "growing",
                "related_roles": ["Data Scientist", "Engineer", "Analyst"]
            },
            {
                "skill_name": "Cloud Platforms",
                "growth_rate": 30.0,
                "adoption_stage": "mainstream",
                "related_roles": ["DevOps", "Infrastructure Engineer"]
            },
            {
                "skill_name": "Data Analytics",
                "growth_rate": 25.0,
                "adoption_stage": "mainstream",
                "related_roles": ["Analyst", "Manager", "Consultant"]
            }
        ]
