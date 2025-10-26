"""
Negotiation Agent - Salary and Offer Negotiation Intelligence
Provides data-driven negotiation strategies and guidance
"""

from typing import Dict, Any, List, Optional
from loguru import logger
import google.generativeai as genai

from app.core.config import settings
from app.models.user_profile import UserProfile
from app.models.orchestrator_schemas import JobOpportunity


class NegotiationAgent:
    """
    Negotiation Agent - The deal advisor
    
    Responsibilities:
    - Provide salary negotiation ranges and strategies
    - Analyze offer packages holistically (equity, benefits, bonus)
    - Suggest negotiation talking points based on market data
    - Calculate total compensation value
    - Answer: "How should I negotiate this offer?"
    """
    
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    async def analyze_offer(
        self,
        user_profile: UserProfile,
        job: JobOpportunity,
        offer_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Comprehensive offer analysis
        
        Args:
            offer_details: {
                "base_salary": 120000,
                "bonus": 15000,
                "equity": {"type": "rsu", "value": 50000, "vesting_years": 4},
                "benefits": ["401k match", "health insurance"],
                "pto_days": 20,
                "remote_policy": "hybrid"
            }
        
        Returns detailed analysis and negotiation recommendations
        """
        try:
            # Calculate total compensation
            total_comp = self._calculate_total_compensation(offer_details)
            
            # Get market benchmark
            market_data = await self._get_market_benchmark(job.title, job.location)
            
            # Generate negotiation strategy
            strategy = await self._generate_negotiation_strategy(
                user_profile, job, offer_details, market_data
            )
            
            return {
                "offer_summary": {
                    "base_salary": offer_details.get("base_salary", 0),
                    "total_comp_year_1": total_comp["year_1"],
                    "total_comp_4_year": total_comp["total_4_year"],
                    "components_breakdown": total_comp["breakdown"]
                },
                "market_comparison": {
                    "market_median": market_data["median"],
                    "percentile": self._calculate_percentile(
                        offer_details.get("base_salary", 0),
                        market_data
                    ),
                    "vs_market": total_comp["year_1"] - market_data["median"]
                },
                "negotiation_strategy": strategy,
                "recommendation": self._generate_recommendation(
                    total_comp, market_data, strategy
                )
            }
            
        except Exception as e:
            logger.error(f"Offer analysis failed: {e}")
            return self._get_fallback_analysis(offer_details)
    
    async def suggest_counteroffer(
        self,
        current_offer: Dict[str, Any],
        market_data: Dict[str, Any],
        user_leverage: str = "medium"  # low/medium/high
    ) -> Dict[str, Any]:
        """
        Generate counteroffer suggestion
        
        Returns recommended ask with justification
        """
        try:
            base_salary = current_offer.get("base_salary", 0)
            
            # Determine counteroffer multiplier based on leverage
            multipliers = {
                "low": 1.05,      # 5% increase
                "medium": 1.10,   # 10% increase
                "high": 1.15      # 15% increase
            }
            multiplier = multipliers.get(user_leverage, 1.10)
            
            suggested_base = int(base_salary * multiplier)
            
            # Generate talking points
            prompt = f"""
            Generate negotiation talking points for salary counteroffer:
            
            Current Offer: ${base_salary:,}
            Suggested Counter: ${suggested_base:,}
            Market Median: ${market_data.get('median', base_salary):,}
            User Leverage: {user_leverage}
            
            Provide:
            1. 3 key reasons to justify the counteroffer
            2. 2 alternative negotiation points (bonus, equity, PTO)
            3. Professional email template
            
            Format as JSON with keys: justification_points, alternative_negotiables, email_template
            """
            
            response = self.model.generate_content(prompt)
            talking_points = self._parse_counteroffer_response(response.text)
            
            return {
                "suggested_base_salary": suggested_base,
                "increase_amount": suggested_base - base_salary,
                "increase_percent": round(((suggested_base - base_salary) / base_salary) * 100, 1),
                "justification": talking_points.get("justification_points", []),
                "alternative_asks": talking_points.get("alternative_negotiables", []),
                "email_template": talking_points.get("email_template", ""),
                "confidence_level": user_leverage
            }
            
        except Exception as e:
            logger.error(f"Counteroffer generation failed: {e}")
            base = current_offer.get("base_salary", 100000)
            return {
                "suggested_base_salary": int(base * 1.10),
                "increase_amount": int(base * 0.10),
                "increase_percent": 10.0,
                "justification": ["Market rate alignment", "Skill level match"],
                "confidence_level": "medium"
            }
    
    async def evaluate_benefits_package(
        self,
        benefits: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate the value of benefits package
        
        Converts benefits to dollar value for comparison
        """
        try:
            valuations = {}
            total_value = 0
            
            # Health insurance (~$7k-15k value)
            if benefits.get("health_insurance"):
                valuations["health_insurance"] = 10000
                total_value += 10000
            
            # 401k match (% of salary)
            if benefits.get("401k_match"):
                match_pct = benefits.get("401k_match_percent", 0.04)  # 4% default
                base = benefits.get("base_salary", 100000)
                valuations["401k_match"] = int(base * match_pct)
                total_value += valuations["401k_match"]
            
            # PTO days (daily rate * days)
            pto_days = benefits.get("pto_days", 0)
            if pto_days > 0:
                daily_rate = benefits.get("base_salary", 100000) / 260  # ~260 work days
                valuations["pto"] = int(daily_rate * pto_days)
                total_value += valuations["pto"]
            
            # Remote work (commute savings)
            if benefits.get("remote_policy") in ["remote", "hybrid"]:
                # Estimate $3k-5k annual savings
                valuations["remote_work"] = 4000
                total_value += 4000
            
            # Professional development budget
            prof_dev = benefits.get("professional_development_budget", 0)
            if prof_dev > 0:
                valuations["professional_development"] = prof_dev
                total_value += prof_dev
            
            return {
                "total_benefits_value": total_value,
                "breakdown": valuations,
                "quality_rating": self._rate_benefits_quality(benefits),
                "improvement_areas": self._suggest_benefit_improvements(benefits)
            }
            
        except Exception as e:
            logger.error(f"Benefits evaluation failed: {e}")
            return {
                "total_benefits_value": 0,
                "breakdown": {},
                "quality_rating": "unknown"
            }
    
    # Helper methods
    
    def _calculate_total_compensation(self, offer: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate total compensation over multiple years"""
        base = offer.get("base_salary", 0)
        bonus = offer.get("bonus", 0)
        
        equity = offer.get("equity", {})
        equity_value = equity.get("value", 0) if isinstance(equity, dict) else 0
        vesting_years = equity.get("vesting_years", 4) if isinstance(equity, dict) else 4
        equity_annual = equity_value / vesting_years if vesting_years > 0 else 0
        
        year_1 = base + bonus + equity_annual
        total_4_year = (base + bonus) * 4 + equity_value
        
        return {
            "year_1": int(year_1),
            "total_4_year": int(total_4_year),
            "breakdown": {
                "base_salary": base,
                "annual_bonus": bonus,
                "equity_annual": int(equity_annual),
                "equity_total": equity_value
            }
        }
    
    async def _get_market_benchmark(self, role: str, location: Optional[str]) -> Dict[str, Any]:
        """Get market salary benchmark"""
        # Simplified benchmark (would use real data in production)
        base_medians = {
            "software engineer": 120000,
            "senior software engineer": 150000,
            "staff engineer": 180000,
            "engineering manager": 160000,
            "product manager": 130000,
            "senior product manager": 160000,
            "data scientist": 125000,
            "designer": 95000
        }
        
        role_lower = role.lower()
        median = base_medians.get(role_lower, 100000)
        
        # Location adjustment (simplified)
        if location and "san francisco" in location.lower():
            median = int(median * 1.3)
        elif location and "new york" in location.lower():
            median = int(median * 1.25)
        
        return {
            "median": median,
            "p25": int(median * 0.8),
            "p75": int(median * 1.2),
            "p90": int(median * 1.4)
        }
    
    async def _generate_negotiation_strategy(
        self,
        user_profile: UserProfile,
        job: JobOpportunity,
        offer: Dict[str, Any],
        market: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate negotiation strategy"""
        try:
            prompt = f"""
            Generate negotiation strategy:
            
            Offer: ${offer.get('base_salary', 0):,}
            Market Median: ${market['median']:,}
            Role: {job.title}
            User Experience: {user_profile.seniority_level or 'Unknown'}
            
            Provide:
            1. Negotiation leverage assessment (low/medium/high)
            2. Top 3 negotiation points
            3. Potential tradeoffs (if salary isn't flexible)
            4. Red flags to watch for
            
            Format as JSON with keys: leverage, key_points, tradeoffs, red_flags
            """
            
            response = self.model.generate_content(prompt)
            return self._parse_strategy_response(response.text)
            
        except:
            return {
                "leverage": "medium",
                "key_points": ["Market rate alignment", "Skill match", "Experience level"],
                "tradeoffs": ["Equity", "Bonus structure", "PTO"],
                "red_flags": []
            }
    
    def _calculate_percentile(self, salary: int, market: Dict[str, Any]) -> int:
        """Calculate salary percentile vs market"""
        if salary <= market["p25"]:
            return 25
        elif salary <= market["median"]:
            return 50
        elif salary <= market["p75"]:
            return 75
        elif salary <= market["p90"]:
            return 90
        else:
            return 95
    
    def _generate_recommendation(
        self,
        total_comp: Dict[str, Any],
        market: Dict[str, Any],
        strategy: Dict[str, Any]
    ) -> str:
        """Generate overall recommendation"""
        year_1 = total_comp["year_1"]
        median = market["median"]
        
        if year_1 >= median * 1.15:
            return "Strong offer - above market median. Consider accepting or minor negotiation."
        elif year_1 >= median:
            return "Fair offer - at market rate. Room for negotiation to reach 75th percentile."
        else:
            return "Below market offer - recommend negotiation to reach market median."
    
    def _rate_benefits_quality(self, benefits: Dict[str, Any]) -> str:
        """Rate overall benefits quality"""
        score = 0
        
        if benefits.get("health_insurance"): score += 2
        if benefits.get("401k_match"): score += 2
        if benefits.get("pto_days", 0) >= 20: score += 1
        if benefits.get("remote_policy") in ["remote", "hybrid"]: score += 1
        if benefits.get("professional_development_budget", 0) > 0: score += 1
        
        if score >= 6:
            return "excellent"
        elif score >= 4:
            return "good"
        elif score >= 2:
            return "fair"
        else:
            return "limited"
    
    def _suggest_benefit_improvements(self, benefits: Dict[str, Any]) -> List[str]:
        """Suggest areas to negotiate benefits"""
        suggestions = []
        
        if not benefits.get("health_insurance"):
            suggestions.append("Request health insurance coverage")
        if not benefits.get("401k_match"):
            suggestions.append("Ask about 401k matching")
        if benefits.get("pto_days", 0) < 20:
            suggestions.append("Negotiate for additional PTO days")
        if benefits.get("remote_policy") == "on_site":
            suggestions.append("Discuss hybrid/remote options")
        
        return suggestions
    
    def _parse_counteroffer_response(self, response_text: str) -> Dict[str, Any]:
        """Parse counteroffer response"""
        try:
            import json
            import re
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        return {
            "justification_points": [],
            "alternative_negotiables": [],
            "email_template": ""
        }
    
    def _parse_strategy_response(self, response_text: str) -> Dict[str, Any]:
        """Parse strategy response"""
        try:
            import json
            import re
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        return {
            "leverage": "medium",
            "key_points": [],
            "tradeoffs": [],
            "red_flags": []
        }
    
    def _get_fallback_analysis(self, offer: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback analysis if AI fails"""
        return {
            "offer_summary": {
                "base_salary": offer.get("base_salary", 0),
                "total_comp_year_1": offer.get("base_salary", 0),
                "total_comp_4_year": offer.get("base_salary", 0) * 4
            },
            "market_comparison": {
                "percentile": 50
            },
            "recommendation": "Unable to generate detailed analysis"
        }
