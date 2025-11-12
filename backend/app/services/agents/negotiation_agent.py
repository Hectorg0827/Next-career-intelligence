"""
Negotiation Agent - Salary & Offer Analysis
Helps users optimize job offers and negotiate better terms
"""

from typing import Dict, Any, List, Optional
from loguru import logger
import google.generativeai as genai

from app.core.config import settings
from app.models.user_profile import UserProfile
from app.services.agents.market_intel_agent import MarketIntelAgent


class NegotiationAgent:
    """
    Negotiation Agent - The compensation optimizer

    Responsibilities:
    - Analyze job offers
    - Compare to market rates
    - Calculate lifetime value delta
    - Generate negotiation scripts
    - Answer: "Is this offer fair, and how do I get more?"
    """

    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel("gemini-1.5-flash")
        self.market_intel = MarketIntelAgent()

    async def analyze_offer(self, user_profile: UserProfile, offer_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a job offer and generate negotiation strategy

        Input offer_details:
        {
            "role": "Senior Behavior Specialist",
            "company": "ABC School District",
            "base_salary": 85000,
            "bonus": 5000,
            "equity": None,
            "benefits": {...},
            "location": "Remote",
            "vacation_days": 15
        }

        Returns:
        {
            "market_analysis": {...},
            "fairness_score": 72,  # 0-100
            "lifetime_value_delta": -45000,  # vs market average
            "negotiation_script": "...",
            "leverage_points": [...],
            "recommended_counter": {...}
        }
        """

        try:
            # Get market data for this role
            market_data = await self.market_intel.get_salary_trends(
                role=offer_details.get("role", ""), location=offer_details.get("location")
            )

            # Calculate fairness score
            fairness = self._calculate_fairness_score(offer_details, market_data)

            # Calculate lifetime value
            lifetime_delta = self._calculate_lifetime_delta(offer_details, market_data)

            # Generate negotiation strategy using AI
            negotiation_strategy = await self._generate_negotiation_strategy(
                user_profile, offer_details, market_data, fairness
            )

            result = {
                "market_analysis": market_data,
                "fairness_score": fairness,
                "lifetime_value_delta": lifetime_delta,
                **negotiation_strategy,
            }

            logger.info(f"Offer analysis complete: fairness={fairness}/100, delta=${lifetime_delta}")

            return result

        except Exception as e:
            logger.error(f"Error analyzing offer: {e}")
            return self._create_fallback_analysis(offer_details)

    def _calculate_fairness_score(self, offer: Dict[str, Any], market_data: Dict[str, Any]) -> int:
        """
        Calculate how fair the offer is (0-100)
        100 = excellent offer (top of market)
        50 = market average
        0 = significantly below market
        """

        offered_salary = offer.get("base_salary", 0) + offer.get("bonus", 0)
        market_median = market_data.get("median_salary", 75000)
        market_75th = market_data.get("percentile_75", 95000)
        market_25th = market_data.get("percentile_25", 60000)

        if offered_salary >= market_75th:
            # Top 25% of market
            return 90 + int((offered_salary - market_75th) / market_75th * 10)
        elif offered_salary >= market_median:
            # Above median
            ratio = (offered_salary - market_median) / (market_75th - market_median)
            return 70 + int(ratio * 20)
        elif offered_salary >= market_25th:
            # Below median but not bottom
            ratio = (offered_salary - market_25th) / (market_median - market_25th)
            return 40 + int(ratio * 30)
        else:
            # Bottom 25%
            return max(int((offered_salary / market_25th) * 40), 0)

    def _calculate_lifetime_delta(self, offer: Dict[str, Any], market_data: Dict[str, Any]) -> int:
        """
        Calculate 5-year lifetime value difference vs market
        Assumes 3% annual raises
        """

        offered_salary = offer.get("base_salary", 0) + offer.get("bonus", 0)
        market_median = market_data.get("median_salary", 75000)

        # Simple 5-year projection with 3% raises
        offered_lifetime = sum(offered_salary * (1.03**year) for year in range(5))
        market_lifetime = sum(market_median * (1.03**year) for year in range(5))

        return int(offered_lifetime - market_lifetime)

    async def _generate_negotiation_strategy(
        self, user_profile: UserProfile, offer: Dict[str, Any], market_data: Dict[str, Any], fairness_score: int
    ) -> Dict[str, Any]:
        """Use AI to generate negotiation talking points and script"""

        try:
            prompt = self._build_negotiation_prompt(user_profile, offer, market_data, fairness_score)

            response = self.model.generate_content(prompt)

            strategy = self._parse_negotiation_response(response.text)

            return strategy

        except Exception as e:
            logger.error(f"Error generating negotiation strategy: {e}")
            return self._create_fallback_strategy(offer, market_data, fairness_score)

    def _build_negotiation_prompt(
        self, user_profile: UserProfile, offer: Dict[str, Any], market_data: Dict[str, Any], fairness_score: int
    ) -> str:
        """Build AI prompt for negotiation guidance"""

        user_years_exp = user_profile.years_total_experience or 0

        prompt = f"""You are a career negotiation coach. Help this person negotiate their job offer.

Candidate Profile:
- Years Experience: {user_years_exp}
- Current Role: {user_profile.current_role or 'Not specified'}

Job Offer:
- Role: {offer.get('role')}
- Company: {offer.get('company')}
- Base Salary: ${offer.get('base_salary', 0):,}
- Bonus: ${offer.get('bonus', 0):,}
- Total Comp: ${offer.get('base_salary', 0) + offer.get('bonus', 0):,}

Market Data:
- Market Median: ${market_data.get('median_salary', 0):,}
- 75th Percentile: ${market_data.get('percentile_75', 0):,}

Fairness Score: {fairness_score}/100

Generate a negotiation strategy with:
1. Leverage points (why they deserve more)
2. Recommended counter-offer (specific numbers)
3. Negotiation script (what to say word-for-word)
4. Fallback positions if they say no

Return ONLY valid JSON:
{{
  "leverage_points": [
    "Your {user_years_exp} years of experience exceed the typical requirement",
    "Market data shows this role typically pays $X-$Y for your experience level"
  ],
  "recommended_counter": {{
    "base_salary": 90000,
    "bonus": 7000,
    "additional_requests": ["Extra week of vacation", "Remote work flexibility"]
  }},
  "negotiation_script": "Thank you for the offer. I'm excited about this role. Based on my research and {user_years_exp} years of experience, I was hoping we could discuss the compensation...",
  "fallback_positions": ["If salary is fixed, ask for signing bonus", "Request performance review in 6 months"]
}}

Be assertive but professional. Output ONLY valid JSON."""

        return prompt

    def _parse_negotiation_response(self, response_text: str) -> Dict[str, Any]:
        """Parse AI negotiation response"""

        import json
        import re

        try:
            json_match = re.search(r"\{.*\}", response_text, re.DOTALL)

            if json_match:
                return json.loads(json_match.group())
            else:
                raise ValueError("No JSON found")

        except Exception as e:
            logger.error(f"Error parsing negotiation response: {e}")
            return {
                "leverage_points": ["Your experience and skills are valuable"],
                "recommended_counter": {},
                "negotiation_script": "I'd like to discuss the compensation package.",
                "fallback_positions": ["Consider other benefits if salary is fixed"],
            }

    def _create_fallback_analysis(self, offer: Dict[str, Any]) -> Dict[str, Any]:
        """Basic analysis when AI/market data unavailable"""

        return {
            "market_analysis": {"median_salary": 75000},
            "fairness_score": 60,
            "lifetime_value_delta": 0,
            "leverage_points": ["Your experience and expertise"],
            "recommended_counter": {"base_salary": int(offer.get("base_salary", 0) * 1.10)},
            "negotiation_script": "Thank you for the offer. I'd like to discuss the compensation.",
            "fallback_positions": ["Consider signing bonus or additional benefits"],
        }

    def _create_fallback_strategy(
        self, offer: Dict[str, Any], market_data: Dict[str, Any], fairness_score: int
    ) -> Dict[str, Any]:
        """Fallback negotiation strategy"""

        current_offer = offer.get("base_salary", 0) + offer.get("bonus", 0)
        market_median = market_data.get("median_salary", 75000)

        if fairness_score < 60:
            # Offer is below market
            target = int(market_median * 1.05)
        else:
            # Offer is fair, aim for 10% more
            target = int(current_offer * 1.10)

        return {
            "leverage_points": [
                "Market data supports a higher compensation for this role",
                "Your experience and skills justify above-average compensation",
            ],
            "recommended_counter": {
                "base_salary": target,
                "additional_requests": ["Performance review in 6 months", "Remote work flexibility"],
            },
            "negotiation_script": f"I appreciate the offer of ${current_offer:,}. Based on my research and experience, I was expecting closer to ${target:,}. Can we discuss?",
            "fallback_positions": [
                "If base salary is fixed, request signing bonus",
                "Ask for additional vacation days or professional development budget",
            ],
        }
