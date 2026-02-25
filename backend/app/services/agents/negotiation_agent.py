"""
Negotiation Agent - Salary & Offer Analysis
Helps users optimize job offers and negotiate better terms.
Now uses real compensation data from Levels.fyi/BLS and supports MESO tactics.
"""

import json
import re
from typing import Dict, Any, List, Optional
from loguru import logger

from app.core.config import settings
from app.models.user_profile import UserProfile
from app.services.agents.market_intel_agent import MarketIntelAgent


class NegotiationAgent:
    """
    Negotiation Agent - The compensation optimizer

    Responsibilities:
    - Analyze job offers against real market benchmarks (Levels.fyi / BLS)
    - Calculate lifetime value delta with real p50/p75 data
    - Generate MESO (Multiple Equivalent Simultaneous Offers) strategies
    - Generate word-for-word negotiation scripts
    - Answer: "Is this offer fair, and how do I get more?"
    """

    def __init__(self):
        self.market_intel = MarketIntelAgent()
        self._model = None

    def _get_model(self, task_type: str = "negotiation_strategy"):
        if self._model is None:
            from app.services.ai.model_router import model_router
            self._model = model_router.get_generative_model(task_type)
        return self._model

    async def analyze_offer(
        self,
        user_profile: UserProfile,
        offer_details: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Analyze a job offer and generate negotiation strategy.

        Input offer_details:
        {
            "role": "Senior Software Engineer",
            "company": "ACME Corp",
            "base_salary": 130000,
            "bonus": 15000,
            "equity": {"shares": 5000, "vesting_years": 4},
            "benefits": {...},
            "location": "San Francisco, CA",
            "vacation_days": 15,
        }

        Returns:
        {
            "market_analysis": {real p25/p50/p75 from Levels.fyi/BLS},
            "fairness_score": 72,
            "fairness_label": "Below market",
            "lifetime_value_delta": -45000,
            "leverage_points": [...],
            "recommended_counter": {...},
            "negotiation_script": "...",
            "fallback_positions": [...],
            "meso_offers": [...],  # Multiple Equivalent Simultaneous Offers
        }
        """
        try:
            # Get real market data
            market_data = await self.market_intel.get_salary_trends(
                role=offer_details.get("role", ""),
                location=offer_details.get("location"),
            )

            # Also fetch total comp breakdown if company specified
            total_comp_data = None
            company = offer_details.get("company", "")
            role = offer_details.get("role", "")
            if company and role:
                try:
                    from app.services.integrations.salary_data_client import get_total_comp_breakdown
                    total_comp_data = await get_total_comp_breakdown(company=company, role=role)
                except Exception:
                    pass

            fairness = self._calculate_fairness_score(offer_details, market_data)
            lifetime_delta = self._calculate_lifetime_delta(offer_details, market_data)

            negotiation_strategy = await self._generate_negotiation_strategy(
                user_profile, offer_details, market_data, fairness
            )

            # Generate MESO offers
            meso_offers = self._generate_meso_offers(offer_details, market_data, total_comp_data)

            fairness_label = self._fairness_label(fairness)

            result = {
                "market_analysis": market_data,
                "total_comp_breakdown": total_comp_data,
                "fairness_score": fairness,
                "fairness_label": fairness_label,
                "lifetime_value_delta": lifetime_delta,
                "meso_offers": meso_offers,
                **negotiation_strategy,
            }

            logger.info(
                f"Offer analysis complete: role={role}, fairness={fairness}/100 ({fairness_label}), "
                f"delta=${lifetime_delta:,}, p50=${market_data.get('median_salary', 0):,} "
                f"[{market_data.get('data_source', 'unknown')}]"
            )
            return result

        except Exception as e:
            logger.error(f"Error analyzing offer: {e}")
            return self._create_fallback_analysis(offer_details)

    def _calculate_fairness_score(
        self,
        offer: Dict[str, Any],
        market_data: Dict[str, Any],
    ) -> int:
        """
        Calculate how fair the offer is (0-100).
        100 = excellent (top of market), 50 = median, 0 = significantly below.
        Uses real p25/p50/p75 from market_data.
        """
        offered_salary = offer.get("base_salary", 0) + offer.get("bonus", 0)
        market_median = market_data.get("median_salary", 0)
        market_75th = market_data.get("percentile_75", 0)
        market_25th = market_data.get("percentile_25", 0)

        if market_median == 0:
            return 50  # No data available

        if offered_salary >= market_75th:
            excess = min((offered_salary - market_75th) / market_75th * 10, 10)
            return min(100, 90 + int(excess))
        elif offered_salary >= market_median:
            range_size = max(market_75th - market_median, 1)
            ratio = (offered_salary - market_median) / range_size
            return 70 + int(ratio * 20)
        elif offered_salary >= market_25th:
            range_size = max(market_median - market_25th, 1)
            ratio = (offered_salary - market_25th) / range_size
            return 40 + int(ratio * 30)
        else:
            if market_25th == 0:
                return 20
            return max(int((offered_salary / market_25th) * 40), 0)

    def _fairness_label(self, score: int) -> str:
        if score >= 90:
            return "Exceptional — top of market"
        elif score >= 75:
            return "Strong — above market median"
        elif score >= 60:
            return "Fair — near market median"
        elif score >= 40:
            return "Below market"
        else:
            return "Significantly below market"

    def _calculate_lifetime_delta(
        self,
        offer: Dict[str, Any],
        market_data: Dict[str, Any],
    ) -> int:
        """
        Calculate 5-year lifetime value difference vs p50 market rate.
        Assumes 3% annual raises, compounded.
        """
        offered_salary = offer.get("base_salary", 0) + offer.get("bonus", 0)
        market_median = market_data.get("median_salary", 0)

        if market_median == 0:
            return 0

        offered_lifetime = sum(offered_salary * (1.03 ** year) for year in range(5))
        market_lifetime = sum(market_median * (1.03 ** year) for year in range(5))

        return int(offered_lifetime - market_lifetime)

    def _generate_meso_offers(
        self,
        offer: Dict[str, Any],
        market_data: Dict[str, Any],
        total_comp_data: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Generate MESO (Multiple Equivalent Simultaneous Offers) package alternatives.
        Each offer trades off components (base, equity, PTO, remote) for equivalent total value.
        This teaches candidates to avoid accepting the first offer by presenting choices.
        """
        current_base = offer.get("base_salary", 0)
        market_p75 = market_data.get("percentile_75", current_base)
        target_base = max(market_p75, int(current_base * 1.12))  # At least 12% bump

        # MESO Option A: Maximum Base
        option_a = {
            "label": "Option A — Maximum Base",
            "description": "Prioritize guaranteed cash. Best if you have lower risk tolerance or near-term expenses.",
            "base_salary": target_base,
            "bonus_target_pct": offer.get("bonus_pct", 10),
            "equity": offer.get("equity"),
            "pto_days": offer.get("vacation_days", 15),
            "remote_days_per_week": None,
            "total_comp_estimate": int(target_base * 1.10),
            "batna_note": "If they won't meet this, ask: 'What's the highest base salary approved for this level?'",
        }

        # MESO Option B: Balanced (base + equity + PTO)
        option_b_base = int(target_base * 0.92)  # Slightly lower base...
        option_b = {
            "label": "Option B — Balanced Package",
            "description": "Lower base in exchange for more equity and PTO. Best if company has strong growth prospects.",
            "base_salary": option_b_base,
            "bonus_target_pct": offer.get("bonus_pct", 12),
            "equity": "1.5x current offer" if offer.get("equity") else "Request initial equity grant",
            "pto_days": (offer.get("vacation_days") or 15) + 5,
            "remote_days_per_week": None,
            "total_comp_estimate": int(option_b_base * 1.25),  # Equity upside reflected
            "batna_note": "If they can't increase equity, ask for a 6-month performance review with raise built in.",
        }

        # MESO Option C: Remote + Flexibility premium
        option_c_base = int(target_base * 0.95)
        option_c = {
            "label": "Option C — Remote & Flexibility",
            "description": "Slightly lower base in exchange for full remote flexibility and learning budget.",
            "base_salary": option_c_base,
            "bonus_target_pct": offer.get("bonus_pct", 10),
            "equity": offer.get("equity"),
            "pto_days": offer.get("vacation_days", 15),
            "remote_days_per_week": 5,
            "learning_budget": 3000,
            "total_comp_estimate": int(option_c_base * 1.12),
            "batna_note": "If full remote is non-negotiable, request a $3-5K home office stipend as equivalent value.",
        }

        return [option_a, option_b, option_c]

    async def _generate_negotiation_strategy(
        self,
        user_profile: UserProfile,
        offer: Dict[str, Any],
        market_data: Dict[str, Any],
        fairness_score: int,
    ) -> Dict[str, Any]:
        """Use Gemini Pro to generate negotiation talking points and word-for-word scripts."""
        try:
            model = self._get_model("negotiation_strategy")
            prompt = self._build_negotiation_prompt(user_profile, offer, market_data, fairness_score)
            response = model.generate_content(prompt)
            return self._parse_negotiation_response(response.text)
        except Exception as e:
            logger.error(f"Error generating negotiation strategy: {e}")
            return self._create_fallback_strategy(offer, market_data, fairness_score)

    def _build_negotiation_prompt(
        self,
        user_profile: UserProfile,
        offer: Dict[str, Any],
        market_data: Dict[str, Any],
        fairness_score: int,
    ) -> str:
        user_years_exp = user_profile.years_total_experience or 0
        current_offer_total = offer.get("base_salary", 0) + offer.get("bonus", 0)
        market_p50 = market_data.get("median_salary", 0)
        market_p75 = market_data.get("percentile_75", 0)
        data_source = market_data.get("data_source", "market data")

        return f"""You are a senior compensation advisor. Help this professional negotiate their job offer.

Candidate Profile:
- Years Experience: {user_years_exp}
- Current Role: {user_profile.current_role or 'Not specified'}

Current Offer:
- Role: {offer.get('role')}
- Company: {offer.get('company')}
- Base Salary: ${offer.get('base_salary', 0):,}
- Bonus: ${offer.get('bonus', 0):,}
- Total Guaranteed: ${current_offer_total:,}
- Location: {offer.get('location', 'Not specified')}

Real Market Data (source: {data_source}):
- p25 (entry/below market): ${market_data.get('percentile_25', 0):,}
- p50 (market median): ${market_p50:,}
- p75 (strong offer): ${market_p75:,}
- p90 (top of market): ${market_data.get('percentile_90', market_p75):,}

Fairness Score: {fairness_score}/100

Craft a negotiation strategy. Be specific and assertive but professional.

Return ONLY valid JSON:
{{
  "leverage_points": [
    "Specific, evidence-based reasons they deserve more (cite actual market data)"
  ],
  "recommended_counter": {{
    "base_salary": <target number based on p75>,
    "bonus": <target number>,
    "additional_requests": ["Specific non-salary items to request"]
  }},
  "negotiation_script": "Word-for-word script for the salary conversation. Should feel natural, confident, and reference the p50/p75 data.",
  "fallback_positions": ["Specific fallback asks if primary counter is rejected"],
  "email_template": "Optional: draft negotiation email if preferred over phone"
}}

Rules:
- Counter offer should target p75 (not an arbitrary % bump)
- Scripts must sound human, not robotic
- Include BATNA (Best Alternative) awareness
- Output ONLY valid JSON"""

    def _parse_negotiation_response(self, response_text: str) -> Dict[str, Any]:
        try:
            json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            logger.error(f"Error parsing negotiation response: {e}")
        return {
            "leverage_points": ["Your experience and skills are valuable"],
            "recommended_counter": {},
            "negotiation_script": "I'd like to discuss the compensation package.",
            "fallback_positions": ["Consider other benefits if salary is fixed"],
        }

    async def generate_meso_strategy(
        self,
        user_profile: UserProfile,
        offers: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Generate a full MESO strategy when candidate has multiple concurrent offers.
        MESO = Multiple Equivalent Simultaneous Offers

        Takes a list of offers and generates:
        - Ranked MESO package options for the best offer
        - Scripts for leveraging competing offers
        - BATNA (Best Alternative to Negotiated Agreement) positioning
        """
        if not offers:
            return {"error": "No offers provided"}

        # Find the strongest offer by total comp
        strongest = max(offers, key=lambda o: o.get("base_salary", 0) + o.get("bonus", 0))
        other_offers = [o for o in offers if o != strongest]

        market_data = await self.market_intel.get_salary_trends(
            role=strongest.get("role", ""),
            location=strongest.get("location"),
        )

        meso_options = self._generate_meso_offers(strongest, market_data)

        # Generate competing-offers leverage script
        leverage_context = ""
        if other_offers:
            competing = other_offers[0]
            competing_total = competing.get("base_salary", 0) + competing.get("bonus", 0)
            leverage_context = (
                f"You have a competing offer from {competing.get('company', 'another company')} "
                f"at ${competing_total:,}. Use this as leverage."
            )

        try:
            model = self._get_model("negotiation_meso")
            prompt = f"""Generate a MESO negotiation strategy for a professional with {len(offers)} job offers.

Primary offer: {strongest.get('company')} — ${strongest.get('base_salary', 0):,} base + ${strongest.get('bonus', 0):,} bonus
{leverage_context}

Market p75 for {strongest.get('role', 'this role')}: ${market_data.get('percentile_75', 0):,}

Generate a BATNA-aware negotiation script that:
1. Uses competing offers as leverage without burning bridges
2. Presents MESO options (base-heavy vs equity-heavy vs flexibility-heavy)
3. Sets a clear walk-away point

Return valid JSON:
{{
  "batna_point": "The minimum acceptable offer before walking away",
  "opening_statement": "Word-for-word script to open the negotiation",
  "meso_presentation_script": "How to present the 3 package options",
  "competing_offer_script": "How to mention competing offers professionally",
  "close_script": "How to close the negotiation and set a deadline"
}}"""
            response = model.generate_content(prompt)
            meso_scripts_raw = re.search(r"\{.*\}", response.text, re.DOTALL)
            meso_scripts = json.loads(meso_scripts_raw.group()) if meso_scripts_raw else {}
        except Exception as e:
            logger.error(f"MESO strategy generation failed: {e}")
            meso_scripts = {}

        return {
            "primary_offer": strongest,
            "competing_offers": other_offers,
            "market_data": market_data,
            "meso_options": meso_options,
            "scripts": meso_scripts,
        }

    def _create_fallback_analysis(self, offer: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "market_analysis": {"median_salary": 0, "data_source": "unavailable"},
            "fairness_score": 50,
            "fairness_label": "Unable to assess — market data unavailable",
            "lifetime_value_delta": 0,
            "meso_offers": [],
            "leverage_points": ["Your experience and expertise are valuable assets"],
            "recommended_counter": {"base_salary": int(offer.get("base_salary", 0) * 1.10)},
            "negotiation_script": "Thank you for the offer. I'd like to discuss the compensation package.",
            "fallback_positions": ["Consider signing bonus or additional benefits if base is fixed"],
        }

    def _create_fallback_strategy(
        self,
        offer: Dict[str, Any],
        market_data: Dict[str, Any],
        fairness_score: int,
    ) -> Dict[str, Any]:
        current_offer = offer.get("base_salary", 0) + offer.get("bonus", 0)
        market_p75 = market_data.get("percentile_75", 0)
        target = max(market_p75, int(current_offer * 1.12))

        return {
            "leverage_points": [
                f"Market data shows this role pays ${market_p75:,} at the 75th percentile",
                "Your experience and skills justify above-median compensation",
            ],
            "recommended_counter": {
                "base_salary": target,
                "additional_requests": ["Performance review in 6 months", "Remote work flexibility"],
            },
            "negotiation_script": (
                f"I appreciate the offer of ${current_offer:,}. "
                f"Based on market data showing the 75th percentile at ${market_p75:,}, "
                f"I was expecting closer to ${target:,}. Can we find a path to get there?"
            ),
            "fallback_positions": [
                "If base salary is fixed, request a signing bonus to bridge the gap",
                "Ask for a built-in 6-month salary review with specific targets",
                "Request additional equity or PTO as equivalent value",
            ],
        }
