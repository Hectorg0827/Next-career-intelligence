"""
Post-Hire Retention & Compensation Monitoring API
Helps placed candidates monitor if their compensation is falling behind market
and provides raise case building tools.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from loguru import logger

router = APIRouter(prefix="/retention", tags=["Post-Hire Retention"])


class PlacementRecord(BaseModel):
    role: str = Field(..., description="Current job title")
    company: str = Field(..., description="Current employer")
    base_salary: int = Field(..., description="Starting base salary")
    total_comp: Optional[int] = Field(None, description="Total compensation including equity/bonus")
    start_date: str = Field(..., description="Start date ISO format (YYYY-MM-DD)")
    location: str = Field("National", description="Work location")
    is_monitoring_enabled: bool = Field(True, description="Enable ongoing compensation monitoring")


class RaiseCaseRequest(BaseModel):
    role: str
    company: str
    current_salary: int
    target_salary: int
    tenure_months: int
    key_achievements: list[str] = []
    location: str = "National"


@router.post("/placed")
async def record_placement(placement: PlacementRecord, user_id: str):
    """
    Record a user as placed in a new role.
    Enables ongoing compensation monitoring for this user.
    """
    try:
        from app.core.database_pool import get_supabase
        db = get_supabase()

        record = {
            "user_id": user_id,
            "role": placement.role,
            "company": placement.company,
            "base_salary": placement.base_salary,
            "total_comp": placement.total_comp or placement.base_salary,
            "start_date": placement.start_date,
            "location": placement.location,
            "is_monitoring_enabled": placement.is_monitoring_enabled,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }

        # Upsert (one active placement per user at a time)
        existing = db.table("career_placements").select("id").eq("user_id", user_id).execute()
        if existing.data:
            db.table("career_placements").update(record).eq("user_id", user_id).execute()
        else:
            db.table("career_placements").insert(record).execute()

        return {
            "status": "recorded",
            "message": f"Congratulations on your new role as {placement.role} at {placement.company}!",
            "monitoring_enabled": placement.is_monitoring_enabled,
        }

    except Exception as e:
        logger.error(f"Failed to record placement for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to record placement")


@router.get("/compensation")
async def check_compensation_drift(user_id: str):
    """
    Compare current salary against current market p50/p75.
    Returns whether the user is falling behind market and by how much.
    """
    try:
        from app.core.database_pool import get_supabase
        from app.services.integrations.salary_data_client import get_compensation

        db = get_supabase()
        result = db.table("career_placements").select("*").eq("user_id", user_id).limit(1).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="No placement record found. Call /api/retention/placed first.")

        placement = result.data[0]
        current_salary = placement["base_salary"]
        role = placement["role"]
        location = placement.get("location", "National")
        start_date = placement.get("start_date", "")

        # Get current market data
        market_data = await get_compensation(role=role, location=location, seniority="mid")
        market_p50 = market_data["p50"]
        market_p75 = market_data["p75"]

        drift_vs_p50 = current_salary - market_p50
        drift_pct = round(drift_vs_p50 / market_p50 * 100, 1) if market_p50 else 0

        # Determine alert level
        if drift_pct < -15:
            alert_level = "high"
            alert_message = f"Your salary is {abs(drift_pct):.1f}% below market median. Consider negotiating a raise."
        elif drift_pct < -5:
            alert_level = "medium"
            alert_message = f"Your salary is {abs(drift_pct):.1f}% below market median. Worth monitoring."
        elif drift_pct >= 15:
            alert_level = "none"
            alert_message = "Your compensation is above market median. Well positioned."
        else:
            alert_level = "none"
            alert_message = "Your compensation is near market median."

        return {
            "role": role,
            "location": location,
            "current_salary": current_salary,
            "market_p50": market_p50,
            "market_p75": market_p75,
            "drift_vs_p50_dollars": drift_vs_p50,
            "drift_vs_p50_pct": drift_pct,
            "alert_level": alert_level,
            "alert_message": alert_message,
            "data_source": market_data.get("data_source"),
            "start_date": start_date,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Compensation drift check failed for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to check compensation drift")


@router.get("/market-pulse")
async def get_market_pulse(user_id: str):
    """
    What are people in my role being paid right now?
    Returns current market distribution for the user's current role.
    """
    try:
        from app.core.database_pool import get_supabase
        from app.services.integrations.salary_data_client import get_compensation
        from app.services.integrations.labor_market_client import get_skill_demand_trends

        db = get_supabase()
        result = db.table("career_placements").select("role, location").eq("user_id", user_id).limit(1).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="No placement record found.")

        role = result.data[0]["role"]
        location = result.data[0].get("location", "National")

        import asyncio
        comp_data, demand_data = await asyncio.gather(
            get_compensation(role=role, location=location, seniority="mid"),
            get_skill_demand_trends([role], location),
        )

        return {
            "role": role,
            "location": location,
            "salary_distribution": {
                "p25": comp_data["p25"],
                "p50": comp_data["p50"],
                "p75": comp_data["p75"],
                "p90": comp_data.get("p90"),
            },
            "demand_trend": demand_data.get("demand_trend", "stable"),
            "job_count_30d": demand_data.get("job_count_30d"),
            "emerging_skills": demand_data.get("emerging_skills", []),
            "data_source": comp_data.get("data_source"),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Market pulse failed for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get market pulse")


@router.post("/raise-case")
async def build_raise_case(request: RaiseCaseRequest, user_id: str):
    """
    Generate a data-backed raise justification document.
    Combines market data with the user's achievements.
    """
    try:
        from app.services.ai.model_router import model_router
        from app.services.integrations.salary_data_client import get_compensation

        # Get market data for context
        market_data = await get_compensation(role=request.role, location=request.location)
        market_p75 = market_data["p75"]
        market_p50 = market_data["p50"]

        model = model_router.get_generative_model("negotiation_strategy")

        achievements_text = "\n".join(f"- {a}" for a in request.key_achievements) if request.key_achievements else "- Delivered consistent results in role"

        prompt = f"""Write a professional raise justification document for this employee.

Employee Information:
- Role: {request.role} at {request.company}
- Current Salary: ${request.current_salary:,}
- Target Salary: ${request.target_salary:,} (requesting ${request.target_salary - request.current_salary:,} / {round((request.target_salary - request.current_salary) / request.current_salary * 100, 1)}% increase)
- Tenure: {request.tenure_months} months

Key Achievements:
{achievements_text}

Market Context:
- Market Median (p50): ${market_p50:,}
- Market 75th Percentile: ${market_p75:,}
- Current salary vs market: {round((request.current_salary - market_p50) / market_p50 * 100, 1)}% vs median

Write a 3-paragraph raise request email that:
1. Opens by referencing tenure and key contributions
2. Makes the market data case with specific numbers
3. Closes with a clear ask and enthusiasm for continued growth

Tone: Professional, confident, data-backed. Not entitled.
Return only the email text."""

        response = model.generate_content(prompt)
        raise_email = response.text.strip()

        return {
            "role": request.role,
            "current_salary": request.current_salary,
            "target_salary": request.target_salary,
            "market_p50": market_p50,
            "market_p75": market_p75,
            "positioning": "above median" if request.current_salary >= market_p50 else "below median",
            "raise_justification_email": raise_email,
            "data_source": market_data.get("data_source"),
        }

    except Exception as e:
        logger.error(f"Raise case generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate raise case: {str(e)}")


@router.get("/job-market-alert")
async def get_job_market_alert(user_id: str, threshold_pct: float = 15.0):
    """
    Alert if the job market has moved more than threshold_pct above current salary.
    Useful for knowing when it's time to look for a new role.
    """
    try:
        from app.core.database_pool import get_supabase
        from app.services.integrations.salary_data_client import get_compensation

        db = get_supabase()
        result = db.table("career_placements").select("*").eq("user_id", user_id).limit(1).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="No placement record found.")

        placement = result.data[0]
        current_salary = placement["base_salary"]
        role = placement["role"]
        location = placement.get("location", "National")

        market_data = await get_compensation(role=role, location=location)
        market_p50 = market_data["p50"]

        market_above_current_pct = round((market_p50 - current_salary) / current_salary * 100, 1)

        alert_triggered = market_above_current_pct >= threshold_pct

        return {
            "alert_triggered": alert_triggered,
            "market_p50": market_p50,
            "current_salary": current_salary,
            "market_above_current_pct": market_above_current_pct,
            "threshold_pct": threshold_pct,
            "message": (
                f"Market has moved {market_above_current_pct:.1f}% above your current salary. "
                "Consider exploring new opportunities or negotiating a raise."
            ) if alert_triggered else (
                f"Your salary is within {abs(market_above_current_pct):.1f}% of market median. "
                "No immediate action needed."
            ),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Market alert check failed for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to check market alert")
