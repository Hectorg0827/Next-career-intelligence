"""
Market Intelligence Agent - Live Market Data & Trends
Aggregates real-time labor market intelligence
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from loguru import logger
import httpx

from app.core.config import settings


class MarketIntelAgent:
    """
    Market Intelligence Agent - The market watcher

    Responsibilities:
    - Track labor market trends
    - Monitor skill demand changes
    - Detect layoff patterns
    - Analyze salary movements
    - Answer: "What's happening in the market right now?"
    """

    def __init__(self):
        self.cache = {}  # Simple in-memory cache
        self.cache_duration = timedelta(hours=6)

    async def get_market_intelligence(
        self, role_keywords: List[str], industry: Optional[str] = None, location: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive market intelligence for specific roles/skills

        Returns:
        {
            "demand_trend": "growing" | "stable" | "declining",
            "demand_change_90d": 12.5,  # percentage
            "avg_salary": {"min": 70000, "max": 95000},
            "top_hiring_companies": [...],
            "emerging_skills": [...],
            "automation_risk_trend": "increasing" | "stable" | "decreasing",
            "layoff_alerts": [...],
            "market_summary": "..."
        }
        """

        cache_key = f"{'-'.join(role_keywords)}_{industry}_{location}"

        # Check cache
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if datetime.utcnow() - cached_time < self.cache_duration:
                logger.info(f"Returning cached market data for {cache_key}")
                return cached_data

        # Fetch fresh data
        market_data = await self._fetch_market_data(role_keywords, industry, location)

        # Cache it
        self.cache[cache_key] = (market_data, datetime.utcnow())

        return market_data

    async def _fetch_market_data(
        self, role_keywords: List[str], industry: Optional[str], location: Optional[str]
    ) -> Dict[str, Any]:
        """Aggregate data from multiple sources"""

        # In production, integrate real APIs:
        # - GitHub Jobs API
        # - Indeed API
        # - Layoffs.fyi scraper
        # - Levels.fyi API
        # For now, return structured mock data with realistic patterns

        market_data = {
            "demand_trend": "stable",
            "demand_change_90d": 0.0,
            "avg_salary": {"min": 60000, "max": 90000, "currency": "USD"},
            "top_hiring_companies": [],
            "emerging_skills": [],
            "automation_risk_trend": "stable",
            "layoff_alerts": [],
            "market_summary": f"Market data for {', '.join(role_keywords)} is being aggregated from multiple sources.",
            "last_updated": datetime.utcnow().isoformat(),
        }

        # Try to fetch real GitHub jobs data (free API)
        try:
            github_data = await self._fetch_github_jobs(role_keywords, location)
            if github_data:
                market_data["top_hiring_companies"] = github_data.get("companies", [])[:5]
                market_data["demand_trend"] = "growing" if len(github_data.get("jobs", [])) > 20 else "stable"
        except Exception as e:
            logger.warning(f"Could not fetch GitHub jobs: {e}")

        # Simulate skill demand tracking
        market_data["emerging_skills"] = self._get_emerging_skills(role_keywords)

        # Simulate automation risk trend
        market_data["automation_risk_trend"] = self._assess_automation_trend(role_keywords)

        return market_data

    async def _fetch_github_jobs(self, keywords: List[str], location: Optional[str]) -> Optional[Dict[str, Any]]:
        """Fetch real job data from GitHub Jobs API (example)"""

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Note: GitHub Jobs API was deprecated, but this shows the pattern
                # Replace with active APIs like Adzuna, Reed, etc.
                search_term = " ".join(keywords[:2])

                # For now, return None to skip
                return None

        except Exception as e:
            logger.error(f"Error fetching GitHub jobs: {e}")
            return None

    def _get_emerging_skills(self, role_keywords: List[str]) -> List[str]:
        """
        Identify emerging skills for this role category
        In production, this would query skills demand APIs
        """

        # Skill emergence patterns by role type
        skill_map = {
            "teacher": ["AI literacy", "Hybrid learning design", "Social-emotional learning"],
            "education": ["EdTech tools", "Data-driven instruction", "Virtual classroom management"],
            "engineer": ["AI/ML", "Cloud architecture", "Kubernetes"],
            "developer": ["AI integration", "Rust", "WebAssembly"],
            "manager": ["Remote team leadership", "OKR management", "AI-assisted decision-making"],
            "analyst": ["Generative AI", "Advanced SQL", "Business intelligence tools"],
            "designer": ["AI-assisted design", "Figma advanced", "Design systems"],
        }

        emerging = []
        for keyword in role_keywords:
            keyword_lower = keyword.lower()
            for role_type, skills in skill_map.items():
                if role_type in keyword_lower:
                    emerging.extend(skills)

        return list(set(emerging))[:5]  # Dedupe and limit

    def _assess_automation_trend(self, role_keywords: List[str]) -> str:
        """
        Assess if automation risk is increasing or decreasing for this role
        """

        # High automation risk roles
        high_risk_keywords = ["data entry", "transcription", "basic admin", "receptionist"]

        # Low automation risk roles
        low_risk_keywords = ["teacher", "coach", "therapist", "nurse", "mentor", "counselor"]

        role_text = " ".join(role_keywords).lower()

        if any(keyword in role_text for keyword in high_risk_keywords):
            return "increasing"

        if any(keyword in role_text for keyword in low_risk_keywords):
            return "stable"

        return "stable"

    async def get_layoff_alerts(self, industry: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get recent layoff alerts for industry
        In production: integrate layoffs.fyi API or WARN database
        """

        # Mock structure for now
        return []

    async def get_salary_trends(self, role: str, location: Optional[str] = None) -> Dict[str, Any]:
        """
        Get salary trend data
        In production: integrate Levels.fyi, Glassdoor, Payscale APIs
        """

        return {
            "role": role,
            "location": location or "National",
            "median_salary": 75000,
            "percentile_25": 60000,
            "percentile_75": 95000,
            "yoy_change": 3.2,  # percentage
            "last_updated": datetime.utcnow().isoformat(),
        }
