"""
Labor Market Client
Provides real-time job demand, skill trends, and hiring company data.

Sources:
1. Adzuna API (free tier: 250 req/day) — job volume by role/location
2. O*NET Web Services (free) — skill demand, occupation outlook
3. Static skill-demand fallback for offline/rate-limited scenarios
"""

import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from loguru import logger

from app.core.config import settings


_demand_cache: Dict[str, tuple] = {}
CACHE_TTL_SECONDS = 43200  # 12 hours


def _cache_key(role: str, location: str) -> str:
    return f"demand:{role.lower().strip()}:{location.lower().strip()}"


def _get_cached(key: str) -> Optional[Dict[str, Any]]:
    if key in _demand_cache:
        data, ts = _demand_cache[key]
        if datetime.utcnow() - ts < timedelta(seconds=CACHE_TTL_SECONDS):
            return data
        del _demand_cache[key]
    return None


def _set_cached(key: str, data: Dict[str, Any]) -> None:
    _demand_cache[key] = (data, datetime.utcnow())


async def _fetch_adzuna_demand(role: str, location: str) -> Optional[Dict[str, Any]]:
    """
    Fetch real job volume data from Adzuna API.
    Free tier: 250 requests/day.
    Docs: https://developer.adzuna.com/
    """
    if not settings.ADZUNA_APP_ID or not settings.ADZUNA_API_KEY:
        return None

    # Adzuna uses country codes; default to US
    country = "us"
    location_param = location if location and location.lower() not in ("remote", "national", "") else None

    try:
        # Fetch current 30-day window
        params: Dict[str, Any] = {
            "app_id": settings.ADZUNA_APP_ID,
            "app_key": settings.ADZUNA_API_KEY,
            "results_per_page": 1,  # We only need count metadata
            "what": role,
            "content-type": "application/json",
        }
        if location_param:
            params["where"] = location_param

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                f"https://api.adzuna.com/v1/api/jobs/{country}/search/1",
                params=params,
            )
            response.raise_for_status()
            data = response.json()

        current_count = data.get("count", 0)

        # Fetch 90-day-ago window for trend comparison
        # Adzuna doesn't support historical counts directly, so we use a second
        # keyword-salaries endpoint to get mean salary and demand signal
        salary_params = {
            "app_id": settings.ADZUNA_APP_ID,
            "app_key": settings.ADZUNA_API_KEY,
            "what": role,
        }
        salary_data: Dict[str, Any] = {}
        try:
            sal_resp = await client.get(
                f"https://api.adzuna.com/v1/api/jobs/{country}/search/1",
                params={**salary_params, "results_per_page": 20},
            )
            if sal_resp.status_code == 200:
                sal_json = sal_resp.json()
                results = sal_json.get("results", [])
                salaries = [r.get("salary_max", 0) for r in results if r.get("salary_max")]
                if salaries:
                    salary_data["adzuna_avg_max_salary"] = int(sum(salaries) / len(salaries))

                # Extract top hiring companies from results
                companies = list({r.get("company", {}).get("display_name", "") for r in results if r.get("company")})
                salary_data["top_hiring_companies"] = [c for c in companies if c][:5]
        except Exception:
            pass

        # Determine demand trend based on raw count
        if current_count > 5000:
            trend = "growing"
        elif current_count > 1000:
            trend = "stable"
        else:
            trend = "declining"

        return {
            "job_count_30d": current_count,
            "demand_trend": trend,
            "demand_change_90d": None,  # Adzuna free tier lacks historical
            "top_hiring_companies": salary_data.get("top_hiring_companies", []),
            "adzuna_avg_max_salary": salary_data.get("adzuna_avg_max_salary"),
            "data_source": "adzuna",
        }

    except Exception as e:
        logger.warning(f"Adzuna demand fetch failed for '{role}': {e}")
        return None


async def _fetch_onet_skills(role: str) -> Optional[Dict[str, Any]]:
    """
    Fetch skill demand and occupation outlook from O*NET.
    Uses existing credentials from settings.ONET_USERNAME / settings.ONET_PASSWORD.
    """
    if not settings.ONET_USERNAME or not settings.ONET_PASSWORD:
        return None

    import base64

    credentials = f"{settings.ONET_USERNAME}:{settings.ONET_PASSWORD}"
    encoded = base64.b64encode(credentials.encode()).decode()
    headers = {"Authorization": f"Basic {encoded}", "Accept": "application/json"}

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Step 1: Find the occupation code for this role
            search_resp = await client.get(
                f"{settings.ONET_BASE_URL}/online/search",
                params={"keyword": role, "end": 1},
                headers=headers,
            )
            search_resp.raise_for_status()
            search_data = search_resp.json()
            occupations = search_data.get("occupation", [])
            if not occupations:
                return None

            onet_code = occupations[0].get("code")
            if not onet_code:
                return None

            # Step 2: Fetch skills for this occupation
            skills_resp = await client.get(
                f"{settings.ONET_BASE_URL}/online/occupations/{onet_code}/details/skills",
                headers=headers,
            )

            emerging_skills: List[str] = []
            if skills_resp.status_code == 200:
                skills_data = skills_resp.json()
                skills_list = skills_data.get("element", [])
                # Take top skills by importance score
                skills_sorted = sorted(
                    skills_list,
                    key=lambda s: s.get("score", {}).get("value", 0),
                    reverse=True,
                )
                emerging_skills = [s.get("name", "") for s in skills_sorted[:8] if s.get("name")]

        return {
            "onet_code": onet_code,
            "emerging_skills": emerging_skills,
            "data_source": "onet",
        }

    except Exception as e:
        logger.warning(f"O*NET skills fetch failed for '{role}': {e}")
        return None


def _static_skill_fallback(role_keywords: List[str]) -> List[str]:
    """
    Static skill emergence patterns when APIs unavailable.
    Kept as a last resort — not the primary source.
    """
    skill_map = {
        "teacher": ["AI literacy", "Hybrid learning design", "Social-emotional learning"],
        "education": ["EdTech tools", "Data-driven instruction", "Virtual classroom management"],
        "engineer": ["AI/ML integration", "Cloud-native architecture", "Platform engineering"],
        "developer": ["AI-assisted development", "WebAssembly", "Edge computing"],
        "data": ["LLM fine-tuning", "Vector databases", "Real-time analytics"],
        "manager": ["Remote team leadership", "OKR management", "AI-assisted decision-making"],
        "analyst": ["Generative AI prompting", "Advanced SQL", "BI + AI hybrid tools"],
        "designer": ["AI-assisted design", "Design systems", "Accessibility engineering"],
        "product": ["AI product management", "Outcome-driven roadmapping", "Growth loops"],
        "security": ["LLM security", "Cloud security posture", "Supply chain security"],
    }

    emerging: List[str] = []
    for keyword in role_keywords:
        keyword_lower = keyword.lower()
        for role_type, skills in skill_map.items():
            if role_type in keyword_lower:
                emerging.extend(skills)

    return list(dict.fromkeys(emerging))[:6]  # deduplicate, preserve order, limit


async def get_skill_demand_trends(
    role_keywords: List[str],
    location: str = "National",
) -> Dict[str, Any]:
    """
    Get real skill demand and job market trends for a set of role keywords.

    Returns:
        {
            "demand_trend": "growing" | "stable" | "declining",
            "demand_change_90d": float | None,
            "job_count_30d": int | None,
            "emerging_skills": List[str],
            "top_hiring_companies": List[str],
            "data_source": str,
        }
    """
    primary_role = " ".join(role_keywords[:2]) if role_keywords else "professional"
    key = _cache_key(primary_role, location)

    cached = _get_cached(key)
    if cached:
        logger.debug(f"Demand cache hit for {key}")
        return cached

    result: Dict[str, Any] = {
        "demand_trend": "stable",
        "demand_change_90d": None,
        "job_count_30d": None,
        "emerging_skills": [],
        "top_hiring_companies": [],
        "data_source": "fallback",
    }

    # Fetch job volume from Adzuna
    adzuna_data = await _fetch_adzuna_demand(primary_role, location)
    if adzuna_data:
        result.update({
            "demand_trend": adzuna_data["demand_trend"],
            "demand_change_90d": adzuna_data["demand_change_90d"],
            "job_count_30d": adzuna_data["job_count_30d"],
            "top_hiring_companies": adzuna_data["top_hiring_companies"],
            "data_source": "adzuna",
        })

    # Fetch skill demand from O*NET
    onet_data = await _fetch_onet_skills(primary_role)
    if onet_data and onet_data.get("emerging_skills"):
        result["emerging_skills"] = onet_data["emerging_skills"]
        if result["data_source"] == "adzuna":
            result["data_source"] = "adzuna+onet"
        else:
            result["data_source"] = "onet"
    else:
        # Static fallback for skills only
        result["emerging_skills"] = _static_skill_fallback(role_keywords)

    _set_cached(key, result)
    logger.info(
        f"Demand data for '{primary_role}' ({location}): "
        f"trend={result['demand_trend']}, jobs={result['job_count_30d']} [{result['data_source']}]"
    )
    return result
