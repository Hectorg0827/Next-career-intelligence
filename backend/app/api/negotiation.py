"""
Enhanced Negotiation API
Exposes the NegotiationAgent with real salary data, MESO tactics, and benchmarks.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from loguru import logger

router = APIRouter(prefix="/negotiation", tags=["Salary Negotiation Coach"])


# --- Request Models ---

class OfferDetails(BaseModel):
    role: str = Field(..., description="Job title of the offer")
    company: str = Field("", description="Company name")
    base_salary: int = Field(..., description="Base salary offered")
    bonus: int = Field(0, description="Target bonus amount")
    equity: Optional[Dict[str, Any]] = Field(None, description="Equity details")
    location: str = Field("National", description="Job location")
    vacation_days: int = Field(15, description="PTO days offered")


class MultiOfferRequest(BaseModel):
    offers: List[OfferDetails] = Field(..., min_items=1, description="All current offers")


class SimulateRequest(BaseModel):
    role: str
    current_offer: int
    target: int
    competing_offer: Optional[int] = None
    leverage_points: List[str] = []


# --- Endpoints ---

@router.post("/analyze-offer")
async def analyze_offer(offer: OfferDetails, user_id: str):
    """
    Full offer analysis with real market benchmarks, fairness score,
    lifetime value delta, and negotiation script.
    """
    try:
        from app.services.agents.negotiation_agent import NegotiationAgent
        from app.models.user_profile import UserProfile
        from app.core.database_pool import get_supabase

        # Fetch user profile
        db = get_supabase()
        profile_result = db.table("career_profiles").select("*").eq("user_id", user_id).limit(1).execute()

        if profile_result.data:
            raw = profile_result.data[0]
            user_profile = UserProfile(
                user_id=user_id,
                current_role=raw.get("current_role"),
                years_total_experience=raw.get("years_total_experience", 0),
            )
        else:
            user_profile = UserProfile(user_id=user_id)

        agent = NegotiationAgent()
        result = await agent.analyze_offer(
            user_profile=user_profile,
            offer_details=offer.dict(),
        )
        return result

    except Exception as e:
        logger.error(f"Offer analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/meso-strategy")
async def generate_meso_strategy(request: MultiOfferRequest, user_id: str):
    """
    Generate MESO (Multiple Equivalent Simultaneous Offers) negotiation strategy
    for a candidate with multiple concurrent offers.
    """
    try:
        from app.services.agents.negotiation_agent import NegotiationAgent
        from app.models.user_profile import UserProfile
        from app.core.database_pool import get_supabase

        db = get_supabase()
        profile_result = db.table("career_profiles").select("*").eq("user_id", user_id).limit(1).execute()
        if profile_result.data:
            raw = profile_result.data[0]
            user_profile = UserProfile(
                user_id=user_id,
                current_role=raw.get("current_role"),
                years_total_experience=raw.get("years_total_experience", 0),
            )
        else:
            user_profile = UserProfile(user_id=user_id)

        agent = NegotiationAgent()
        result = await agent.generate_meso_strategy(
            user_profile=user_profile,
            offers=[o.dict() for o in request.offers],
        )
        return result

    except Exception as e:
        logger.error(f"MESO strategy generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"MESO strategy failed: {str(e)}")


@router.get("/benchmarks")
async def get_compensation_benchmarks(role: str, location: str = "National", seniority: str = "mid"):
    """
    Get real compensation benchmarks for a role/location/seniority combination.
    Returns p25, p50, p75, p90 from Levels.fyi and/or BLS OES.
    """
    try:
        from app.services.integrations.salary_data_client import get_compensation
        data = await get_compensation(role=role, location=location, seniority=seniority)
        return data
    except Exception as e:
        logger.error(f"Benchmark fetch failed for {role}: {e}")
        raise HTTPException(status_code=500, detail=f"Benchmark fetch failed: {str(e)}")


@router.post("/simulate")
async def simulate_negotiation(request: SimulateRequest):
    """
    Simulate a negotiation scenario and generate likely outcomes.
    Returns probability of success and recommended approach.
    """
    try:
        from app.services.ai.model_router import model_router
        model = model_router.get_generative_model("negotiation_strategy")

        competing_context = (
            f"Candidate also has a competing offer at ${request.competing_offer:,}."
            if request.competing_offer else ""
        )

        prompt = f"""Simulate this salary negotiation and advise on the best approach.

Role: {request.role}
Current Offer: ${request.current_offer:,}
Target Salary: ${request.target:,}
Gap: ${request.target - request.current_offer:,} ({round((request.target - request.current_offer) / request.current_offer * 100, 1)}%)
{competing_context}

Leverage Points:
{chr(10).join(f'- {lp}' for lp in request.leverage_points)}

Return valid JSON:
{{
  "success_probability": "high/medium/low",
  "recommended_ask": <number>,
  "approach": "Direct ask / Competing offer leverage / Anchor high",
  "opening_line": "Word-for-word opening",
  "key_risk": "The main risk in this negotiation",
  "fallback": "If they say no, do this"
}}"""

        response = model.generate_content(prompt)
        import json
        import re
        json_match = re.search(r"\{.*\}", response.text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        raise ValueError("No JSON in response")

    except Exception as e:
        logger.error(f"Simulation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")


@router.get("/scripts")
async def get_negotiation_scripts():
    """
    Get pre-built negotiation scripts for common scenarios.
    """
    return {
        "scripts": [
            {
                "scenario": "Initial counter-offer",
                "context": "When you receive an offer and want to negotiate up",
                "script": (
                    "Thank you so much for the offer — I'm genuinely excited about this role and the team. "
                    "I've done some research on market compensation for [role] in [location], and based on "
                    "my [X] years of experience, I was hoping we could get closer to $[target]. "
                    "Is there flexibility to get there?"
                ),
                "notes": "Always express enthusiasm first. State the target number clearly.",
            },
            {
                "scenario": "Competing offer leverage",
                "context": "When you have another offer and want to use it professionally",
                "script": (
                    "I want to be transparent with you — I do have another offer from [Company] at $[amount]. "
                    "But [Target Company] is my first choice because [specific reason]. "
                    "If you can get to $[target], I'm ready to sign today."
                ),
                "notes": "Only use this if the competing offer is real. Never bluff.",
            },
            {
                "scenario": "Asking for a signing bonus when base is fixed",
                "context": "When they say the base salary is non-negotiable",
                "script": (
                    "I understand the base salary band has constraints. "
                    "Would it be possible to include a signing bonus to help bridge the gap? "
                    "I'm thinking $[amount] would make it work for me."
                ),
                "notes": "Signing bonuses often come from a different budget than base salary.",
            },
            {
                "scenario": "Equity negotiation",
                "context": "When you want more equity instead of higher base",
                "script": (
                    "I'd love to find a way to be compensated for the long-term value I plan to bring. "
                    "If increasing the base isn't possible, would you consider enhancing the equity package? "
                    "An additional [X] shares vesting over [Y] years would go a long way."
                ),
                "notes": "Frame equity as investing in your shared success.",
            },
            {
                "scenario": "Raise after 6 months",
                "context": "When they can't budge now but you want commitment to a future review",
                "script": (
                    "I understand the constraints right now. Could we agree in writing to a compensation "
                    "review at the 6-month mark, with a clear target of reaching $[target] if I hit [specific goals]? "
                    "Having that commitment would make the current offer work for me."
                ),
                "notes": "Get it in writing. Be specific about the milestone criteria.",
            },
        ]
    }
