"""
Market Intelligence Agent - Live Market Data & Trends
Aggregates real-time labor market intelligence from Adzuna, O*NET, BLS, and Layoffs.fyi.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from loguru import logger

from app.core.config import settings


class MarketIntelAgent:
    """
    Market Intelligence Agent - The market watcher

    Responsibilities:
    - Track labor market trends (real job volume from Adzuna)
    - Monitor skill demand changes (O*NET + Adzuna)
    - Detect layoff patterns (Layoffs.fyi)
    - Analyze salary movements (Levels.fyi via Apify + BLS OES)
    - Answer: "What's happening in the market right now?"
    """

    def __init__(self):
        self._cache: Dict[str, tuple] = {}
        self._cache_duration = timedelta(hours=6)

    def _get_cached(self, key: str) -> Optional[Dict[str, Any]]:
        if key in self._cache:
            data, ts = self._cache[key]
            if datetime.utcnow() - ts < self._cache_duration:
                return data
            del self._cache[key]
        return None

    def _set_cached(self, key: str, data: Dict[str, Any]) -> None:
        self._cache[key] = (data, datetime.utcnow())

    async def get_market_intelligence(
        self,
        role_keywords: List[str],
        industry: Optional[str] = None,
        location: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get comprehensive market intelligence for specific roles/skills.

        Returns:
        {
            "demand_trend": "growing" | "stable" | "declining",
            "demand_change_90d": float | None,
            "job_count_30d": int | None,
            "avg_salary": {"p25": int, "p50": int, "p75": int, "currency": "USD"},
            "top_hiring_companies": List[str],
            "emerging_skills": List[str],
            "automation_risk_trend": "increasing" | "stable" | "decreasing",
            "layoff_alerts": List[dict],
            "market_summary": str,
            "last_updated": str,
            "data_sources": List[str],
        }
        """
        cache_key = f"{'-'.join(role_keywords)}_{industry}_{location}"
        cached = self._get_cached(cache_key)
        if cached:
            logger.info(f"Returning cached market data for {cache_key}")
            return cached

        market_data = await self._fetch_market_data(role_keywords, industry, location)
        self._set_cached(cache_key, market_data)
        return market_data

    async def _fetch_market_data(
        self,
        role_keywords: List[str],
        industry: Optional[str],
        location: Optional[str],
    ) -> Dict[str, Any]:
        """Aggregate data from Adzuna (demand), O*NET (skills), salary client, and layoff monitor."""
        from app.services.integrations.labor_market_client import get_skill_demand_trends
        from app.services.integrations.salary_data_client import get_compensation
        from app.services.integrations.layoff_monitor import get_layoff_alerts

        data_sources = []

        # --- Demand & Skills (Adzuna + O*NET) ---
        demand_data = await get_skill_demand_trends(
            role_keywords=role_keywords,
            location=location or "National",
        )
        if demand_data.get("data_source") not in ("fallback",):
            data_sources.append(demand_data["data_source"])

        demand_trend = demand_data.get("demand_trend", "stable")
        demand_change_90d = demand_data.get("demand_change_90d")
        job_count_30d = demand_data.get("job_count_30d")
        top_hiring_companies = demand_data.get("top_hiring_companies", [])
        emerging_skills = demand_data.get("emerging_skills", [])

        # --- Salary (Levels.fyi / BLS) ---
        primary_role = " ".join(role_keywords[:2]) if role_keywords else "professional"
        salary_data = await get_compensation(
            role=primary_role,
            location=location or "National",
            seniority="mid",
        )
        if salary_data.get("data_source") not in ("estimate",):
            data_sources.append(salary_data["data_source"])

        avg_salary = {
            "p25": salary_data.get("p25", 0),
            "p50": salary_data.get("p50", 0),
            "p75": salary_data.get("p75", 0),
            "p90": salary_data.get("p90", 0),
            "currency": "USD",
            "data_source": salary_data.get("data_source", "estimate"),
        }

        # --- Layoff Alerts ---
        layoff_alerts = await get_layoff_alerts(industry=industry, days_back=60)
        if layoff_alerts:
            data_sources.append("layoffs_fyi")

        # --- Automation Risk (deterministic, role-based) ---
        automation_risk_trend = self._assess_automation_trend(role_keywords)

        # --- Market Summary ---
        trend_desc = {
            "growing": "experiencing strong growth",
            "stable": "holding steady",
            "declining": "facing reduced demand",
        }.get(demand_trend, "stable")

        market_summary = (
            f"The {primary_role} market is {trend_desc}. "
            f"Median compensation is ${avg_salary['p50']:,} (p25: ${avg_salary['p25']:,}, p75: ${avg_salary['p75']:,}). "
        )
        if job_count_30d:
            market_summary += f"{job_count_30d:,} active openings tracked in the past 30 days. "
        if emerging_skills:
            market_summary += f"High-demand skills: {', '.join(emerging_skills[:3])}."

        return {
            "demand_trend": demand_trend,
            "demand_change_90d": demand_change_90d,
            "job_count_30d": job_count_30d,
            "avg_salary": avg_salary,
            # Legacy compat field — points to real p50 now
            "avg_salary_min": avg_salary["p25"],
            "avg_salary_max": avg_salary["p75"],
            "top_hiring_companies": top_hiring_companies,
            "emerging_skills": emerging_skills,
            "automation_risk_trend": automation_risk_trend,
            "layoff_alerts": [
                {
                    "company": a.get("company"),
                    "headcount_reduction": a.get("headcount_reduction"),
                    "industry": a.get("industry"),
                    "date": a.get("announcement_date"),
                }
                for a in layoff_alerts[:5]
            ],
            "market_summary": market_summary,
            "last_updated": datetime.utcnow().isoformat(),
            "data_sources": list(set(data_sources)) if data_sources else ["estimate"],
        }

    def _assess_automation_trend(self, role_keywords: List[str]) -> str:
        """Assess if automation risk is increasing or decreasing for this role."""
        high_risk_keywords = ["data entry", "transcription", "basic admin", "receptionist", "bookkeeper"]
        low_risk_keywords = ["teacher", "coach", "therapist", "nurse", "mentor", "counselor", "social worker"]

        role_text = " ".join(role_keywords).lower()

        if any(kw in role_text for kw in high_risk_keywords):
            return "increasing"
        if any(kw in role_text for kw in low_risk_keywords):
            return "stable"
        return "stable"

    async def get_layoff_alerts(self, industry: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get recent layoff alerts for an industry.
        Now backed by real Layoffs.fyi data via layoff_monitor.
        """
        from app.services.integrations.layoff_monitor import get_layoff_alerts
        return await get_layoff_alerts(industry=industry, days_back=60)

    async def get_salary_trends(
        self,
        role: str,
        location: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get salary trend data from real sources (Levels.fyi / BLS OES).
        Previously returned hardcoded $75,000 — now uses live data.
        """
        from app.services.integrations.salary_data_client import get_compensation

        data = await get_compensation(
            role=role,
            location=location or "National",
            seniority="mid",
        )

        return {
            "role": role,
            "location": location or "National",
            "median_salary": data["p50"],
            "percentile_25": data["p25"],
            "percentile_75": data["p75"],
            "percentile_90": data.get("p90", data["p75"]),
            "total_comp_median": data.get("total_comp_median"),
            "sample_size": data.get("sample_size"),
            "data_source": data.get("data_source", "estimate"),
            # Legacy field name for backwards compat
            "yoy_change": None,  # Not available without historical data
            "last_updated": data.get("last_updated", datetime.utcnow().isoformat()),
        }
