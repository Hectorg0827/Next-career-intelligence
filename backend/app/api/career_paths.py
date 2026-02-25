"""
Career Paths API
Provides predictive career pathing data from O*NET, BLS OES, and platform data.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from loguru import logger

router = APIRouter(prefix="/career-paths", tags=["Career Paths"])


async def _get_onet_career_transitions(role: str) -> List[Dict[str, Any]]:
    """Fetch career transition data from O*NET."""
    from app.services.onet_service import ONetService
    onet = ONetService()

    try:
        # Search for occupation
        occupations = await onet.search_occupations(role, limit=1)
        if not occupations:
            return []

        onet_code = occupations[0].get("code")
        if not onet_code:
            return []

        # Fetch related occupations (career transitions)
        import httpx
        import base64
        from app.core.config import settings

        credentials = f"{settings.ONET_USERNAME}:{settings.ONET_PASSWORD}"
        encoded = base64.b64encode(credentials.encode()).decode()
        headers = {"Authorization": f"Basic {encoded}", "Accept": "application/json"}

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                f"{settings.ONET_BASE_URL}/online/occupations/{onet_code}/related",
                headers=headers,
            )
            if response.status_code != 200:
                return []
            data = response.json()

        transitions = []
        for related in data.get("occupation", [])[:8]:
            transitions.append({
                "to_role": related.get("title", ""),
                "to_onet_code": related.get("code", ""),
                "relationship": related.get("score", {}).get("value", 0),
                "median_time_years": None,  # Not available from O*NET directly
                "salary_delta_pct": None,
            })

        return transitions

    except Exception as e:
        logger.warning(f"O*NET career transitions failed for '{role}': {e}")
        return []


async def _get_bls_occupation_outlook(role: str) -> Dict[str, Any]:
    """Get 10-year job growth projections from BLS."""
    # BLS Employment Projections table — hardcoded growth rates for major categories
    # In production, integrate the BLS EP API: https://www.bls.gov/emp/data/occupational-data.htm
    role_lower = role.lower()

    growth_map = {
        "software": {"10yr_growth_pct": 25, "demand_level": "very high"},
        "data scientist": {"10yr_growth_pct": 36, "demand_level": "very high"},
        "machine learning": {"10yr_growth_pct": 40, "demand_level": "very high"},
        "product manager": {"10yr_growth_pct": 10, "demand_level": "high"},
        "ux designer": {"10yr_growth_pct": 16, "demand_level": "high"},
        "nurse": {"10yr_growth_pct": 6, "demand_level": "high"},
        "teacher": {"10yr_growth_pct": 4, "demand_level": "moderate"},
        "financial analyst": {"10yr_growth_pct": 9, "demand_level": "high"},
        "accountant": {"10yr_growth_pct": 6, "demand_level": "moderate"},
    }

    for keyword, outlook in growth_map.items():
        if keyword in role_lower:
            return {**outlook, "source": "bls_projections"}

    return {"10yr_growth_pct": 5, "demand_level": "moderate", "source": "bls_projections_estimate"}


async def _get_skill_bridge(current_role: str, target_role: str) -> List[str]:
    """Identify skills needed to transition between roles."""
    from app.services.integrations.labor_market_client import get_skill_demand_trends

    try:
        target_demand = await get_skill_demand_trends([target_role])
        return target_demand.get("emerging_skills", [])[:5]
    except Exception:
        return []


@router.get("/{current_role}")
async def get_career_paths(
    current_role: str,
    include_salary: bool = True,
    include_skills: bool = True,
):
    """
    Get career transition paths from a current role.

    Returns common next roles, median transition time, salary delta,
    market outlook, and key skills needed for advancement.
    """
    logger.info(f"Career paths requested for: {current_role}")

    # Parallel fetches
    import asyncio
    transitions_task = asyncio.create_task(_get_onet_career_transitions(current_role))
    outlook_task = asyncio.create_task(_get_bls_occupation_outlook(current_role))

    transitions, outlook = await asyncio.gather(transitions_task, outlook_task)

    # Enrich transitions with salary data if requested
    if include_salary and transitions:
        from app.services.integrations.salary_data_client import get_compensation
        for t in transitions[:4]:  # Limit to avoid too many API calls
            try:
                sal = await get_compensation(t["to_role"])
                t["target_salary_p50"] = sal.get("p50")
                t["target_salary_p75"] = sal.get("p75")
            except Exception:
                pass

    # Get skills for advancement
    advancement_skills = []
    if include_skills:
        try:
            from app.services.integrations.labor_market_client import get_skill_demand_trends
            demand = await get_skill_demand_trends([current_role])
            advancement_skills = demand.get("emerging_skills", [])
        except Exception:
            pass

    return {
        "current_role": current_role,
        "common_transitions": transitions,
        "market_outlook": outlook,
        "key_skills_for_advancement": advancement_skills,
        "data_sources": ["onet", "bls_projections"],
    }


@router.get("/{current_role}/compare/{target_role}")
async def compare_role_transition(current_role: str, target_role: str):
    """
    Compare two specific roles: what skills are needed to move from current to target,
    salary delta, and difficulty estimate.
    """
    import asyncio

    current_sal_task = asyncio.create_task(
        __import__("app.services.integrations.salary_data_client", fromlist=["get_compensation"]).get_compensation(current_role)
    )
    target_sal_task = asyncio.create_task(
        __import__("app.services.integrations.salary_data_client", fromlist=["get_compensation"]).get_compensation(target_role)
    )
    bridge_skills_task = asyncio.create_task(_get_skill_bridge(current_role, target_role))

    try:
        from app.services.integrations.salary_data_client import get_compensation
        current_sal, target_sal, bridge_skills = await asyncio.gather(
            get_compensation(current_role),
            get_compensation(target_role),
            _get_skill_bridge(current_role, target_role),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {e}")

    current_p50 = current_sal.get("p50", 0)
    target_p50 = target_sal.get("p50", 0)
    salary_delta_pct = round((target_p50 - current_p50) / current_p50 * 100, 1) if current_p50 else 0

    return {
        "from_role": current_role,
        "to_role": target_role,
        "salary_delta_pct": salary_delta_pct,
        "current_salary": {"p50": current_p50, "p75": current_sal.get("p75")},
        "target_salary": {"p50": target_p50, "p75": target_sal.get("p75")},
        "bridge_skills_needed": bridge_skills,
        "estimated_transition_time": "12-24 months",  # Generic estimate; improve with platform data
    }
