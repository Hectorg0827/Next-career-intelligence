"""
Salary Data Client
Provides real compensation data from Apify (Levels.fyi scraper) and BLS OES API.

Priority order:
1. Apify Levels.fyi actor (tech roles, very accurate)
2. BLS OES API (free, public, all occupations)
3. Fallback estimates based on role category
"""

import httpx
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from loguru import logger

from app.core.config import settings


# In-memory cache for salary lookups (in production, use Redis)
_salary_cache: Dict[str, tuple] = {}
CACHE_TTL_SECONDS = 86400  # 24 hours

BLS_OES_BASE = "https://api.bls.gov/publicAPI/v2"

# BLS OES series codes for common roles (precomputed from BLS occupation codes)
BLS_SERIES_MAP = {
    "software engineer": "OEUN000015113200",  # Software Developers
    "software developer": "OEUN000015113200",
    "data scientist": "OEUN000015219410",     # Data Scientists
    "data analyst": "OEUN000015151120",       # Data Analysts
    "product manager": "OEUN000011202100",    # Marketing and Sales Managers (proxy)
    "ux designer": "OEUN000027102100",        # Graphic Designers
    "devops engineer": "OEUN000015114100",    # Network/Computer Systems Admin
    "machine learning engineer": "OEUN000015219410",
    "backend engineer": "OEUN000015113200",
    "frontend engineer": "OEUN000015113200",
}


def _cache_key(role: str, location: str, seniority: str) -> str:
    return f"salary:{role.lower().strip()}:{location.lower().strip()}:{seniority.lower().strip()}"


def _get_cached(key: str) -> Optional[Dict[str, Any]]:
    if key in _salary_cache:
        data, ts = _salary_cache[key]
        if datetime.utcnow() - ts < timedelta(seconds=CACHE_TTL_SECONDS):
            return data
        del _salary_cache[key]
    return None


def _set_cached(key: str, data: Dict[str, Any]) -> None:
    _salary_cache[key] = (data, datetime.utcnow())


async def _fetch_apify_levels_fyi(role: str, location: str, seniority: str) -> Optional[Dict[str, Any]]:
    """
    Call Apify's Levels.fyi scraper actor to get compensation data.
    Actor: anchor/levels-fyi-scraper
    Requires: APIFY_API_TOKEN
    """
    if not settings.APIFY_API_TOKEN:
        return None

    try:
        actor_id = "anchor~levels-fyi-scraper"
        url = f"https://api.apify.com/v2/acts/{actor_id}/run-sync-get-dataset-items"

        payload = {
            "role": role,
            "location": location if location and location.lower() != "national" else "United States",
            "maxItems": 50,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url,
                json=payload,
                params={"token": settings.APIFY_API_TOKEN},
            )
            response.raise_for_status()
            items = response.json()

        if not items:
            return None

        # Parse compensation records
        salaries = []
        total_comps = []
        for item in items:
            base = item.get("baseSalary") or item.get("base_salary")
            tc = item.get("totalComp") or item.get("total_comp") or base
            if isinstance(base, (int, float)) and base > 0:
                salaries.append(base)
            if isinstance(tc, (int, float)) and tc > 0:
                total_comps.append(tc)

        if not salaries:
            return None

        salaries.sort()
        total_comps.sort()
        n = len(salaries)

        return {
            "role": role,
            "location": location or "National",
            "seniority": seniority,
            "p25": salaries[max(0, int(n * 0.25) - 1)],
            "p50": salaries[int(n * 0.50) - 1] if n > 0 else salaries[0],
            "p75": salaries[min(n - 1, int(n * 0.75))],
            "p90": salaries[min(n - 1, int(n * 0.90))],
            "total_comp_median": total_comps[int(len(total_comps) * 0.5) - 1] if total_comps else None,
            "sample_size": n,
            "data_source": "levels_fyi",
            "last_updated": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.warning(f"Apify Levels.fyi lookup failed for {role}: {e}")
        return None


async def _fetch_bls_oes(role: str) -> Optional[Dict[str, Any]]:
    """
    Fetch wage data from BLS Occupational Employment Statistics API.
    Free API, covers all US occupations.
    """
    role_lower = role.lower()
    series_id = None
    for keyword, sid in BLS_SERIES_MAP.items():
        if keyword in role_lower:
            series_id = sid
            break

    if not series_id:
        return None

    try:
        payload = {
            "seriesid": [series_id],
            "startyear": str(datetime.utcnow().year - 1),
            "endyear": str(datetime.utcnow().year),
        }
        if settings.BLS_API_KEY:
            payload["registrationkey"] = settings.BLS_API_KEY

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(f"{BLS_OES_BASE}/timeseries/data/", json=payload)
            response.raise_for_status()
            bls_data = response.json()

        series_list = bls_data.get("Results", {}).get("series", [])
        if not series_list:
            return None

        data_points = series_list[0].get("data", [])
        if not data_points:
            return None

        # Take most recent data point
        latest = data_points[0]
        annual_wage = int(float(latest.get("value", 0)) * 1000)  # BLS reports in thousands

        if annual_wage == 0:
            return None

        return {
            "role": role,
            "location": "National",
            "seniority": "mid",
            "p25": int(annual_wage * 0.80),
            "p50": annual_wage,
            "p75": int(annual_wage * 1.25),
            "p90": int(annual_wage * 1.50),
            "total_comp_median": None,
            "sample_size": None,
            "data_source": "bls_oes",
            "last_updated": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.warning(f"BLS OES lookup failed for {role}: {e}")
        return None


def _role_category_estimate(role: str) -> Dict[str, Any]:
    """
    Fallback estimate based on role category when no API data is available.
    These are reasonable US median ranges, not hardcoded single values.
    """
    role_lower = role.lower()

    if any(k in role_lower for k in ["staff engineer", "principal", "director"]):
        base = 180000
    elif any(k in role_lower for k in ["senior", "lead", "architect"]):
        base = 150000
    elif any(k in role_lower for k in ["engineer", "developer", "scientist", "analyst"]):
        base = 110000
    elif any(k in role_lower for k in ["manager", "product"]):
        base = 130000
    elif any(k in role_lower for k in ["designer"]):
        base = 95000
    elif any(k in role_lower for k in ["teacher", "education", "counsel"]):
        base = 65000
    elif any(k in role_lower for k in ["nurse", "therapist", "health"]):
        base = 80000
    else:
        base = 85000

    return {
        "role": role,
        "location": "National",
        "seniority": "mid",
        "p25": int(base * 0.80),
        "p50": base,
        "p75": int(base * 1.25),
        "p90": int(base * 1.55),
        "total_comp_median": None,
        "sample_size": None,
        "data_source": "estimate",
        "last_updated": datetime.utcnow().isoformat(),
    }


async def get_compensation(
    role: str,
    location: str = "National",
    seniority: str = "mid",
) -> Dict[str, Any]:
    """
    Get real compensation data for a role/location/seniority combination.

    Returns:
        {
            "role": str,
            "location": str,
            "seniority": str,
            "p25": int,    # 25th percentile annual base salary
            "p50": int,    # Median annual base salary
            "p75": int,    # 75th percentile
            "p90": int,    # 90th percentile
            "total_comp_median": int | None,
            "sample_size": int | None,
            "data_source": "levels_fyi" | "bls_oes" | "estimate",
            "last_updated": str,
        }
    """
    key = _cache_key(role, location, seniority)
    cached = _get_cached(key)
    if cached:
        logger.debug(f"Salary cache hit for {key}")
        return cached

    # Try Levels.fyi via Apify (most accurate for tech roles)
    data = await _fetch_apify_levels_fyi(role, location, seniority)

    # Fall back to BLS OES
    if not data:
        data = await _fetch_bls_oes(role)

    # Final fallback: category-based estimate
    if not data:
        data = _role_category_estimate(role)

    _set_cached(key, data)
    logger.info(f"Salary data fetched for '{role}' ({location}): p50=${data['p50']:,} [{data['data_source']}]")
    return data


async def get_total_comp_breakdown(company: str, role: str) -> Dict[str, Any]:
    """
    Get base/bonus/equity breakdown for a specific company+role combination.
    Uses Levels.fyi actor with company filter when available.
    """
    if not settings.APIFY_API_TOKEN:
        # Return reasonable placeholder split
        comp_data = await get_compensation(role)
        base = comp_data["p50"]
        return {
            "company": company,
            "role": role,
            "base_salary": base,
            "target_bonus_pct": 10,
            "target_bonus": int(base * 0.10),
            "equity_annual_estimate": int(base * 0.20),
            "total_comp_estimate": int(base * 1.30),
            "data_source": "estimate",
        }

    try:
        actor_id = "anchor~levels-fyi-scraper"
        url = f"https://api.apify.com/v2/acts/{actor_id}/run-sync-get-dataset-items"
        payload = {"role": role, "company": company, "maxItems": 30}

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url,
                json=payload,
                params={"token": settings.APIFY_API_TOKEN},
            )
            response.raise_for_status()
            items = response.json()

        if not items:
            raise ValueError("No Levels.fyi data for company/role")

        bases = [i.get("baseSalary", 0) for i in items if i.get("baseSalary")]
        bonuses = [i.get("bonus", 0) for i in items if i.get("bonus")]
        equities = [i.get("stockGrant", 0) for i in items if i.get("stockGrant")]

        med_base = sorted(bases)[len(bases) // 2] if bases else 0
        med_bonus = sorted(bonuses)[len(bonuses) // 2] if bonuses else 0
        med_equity_annual = (sorted(equities)[len(equities) // 2] / 4) if equities else 0

        return {
            "company": company,
            "role": role,
            "base_salary": med_base,
            "target_bonus_pct": round(med_bonus / med_base * 100, 1) if med_base else 0,
            "target_bonus": int(med_bonus),
            "equity_annual_estimate": int(med_equity_annual),
            "total_comp_estimate": int(med_base + med_bonus + med_equity_annual),
            "sample_size": len(bases),
            "data_source": "levels_fyi",
        }

    except Exception as e:
        logger.warning(f"Total comp breakdown failed for {company}/{role}: {e}")
        comp_data = await get_compensation(role)
        base = comp_data["p50"]
        return {
            "company": company,
            "role": role,
            "base_salary": base,
            "target_bonus_pct": 10,
            "target_bonus": int(base * 0.10),
            "equity_annual_estimate": int(base * 0.15),
            "total_comp_estimate": int(base * 1.25),
            "data_source": "estimate",
        }
