"""
SDR Research Node
Performs company research for each filtered job candidate.
Uses NewsAPI + Gemini to generate strategic context relevant to the candidate.
"""

import asyncio
import httpx
from typing import Dict, Any, List, Optional
from loguru import logger
from datetime import datetime

from app.core.config import settings

# Simple in-memory cache for company research: {company_name: (data, timestamp)}
_company_cache: Dict[str, tuple] = {}
COMPANY_CACHE_TTL = 604800  # 7 days in seconds


def _get_cached_research(company: str) -> Optional[Dict[str, Any]]:
    if company in _company_cache:
        data, ts = _company_cache[company]
        if (datetime.utcnow().timestamp() - ts) < COMPANY_CACHE_TTL:
            return data
        del _company_cache[company]
    return None


def _set_cached_research(company: str, data: Dict[str, Any]) -> None:
    _company_cache[company] = (data, datetime.utcnow().timestamp())


async def _fetch_news_for_company(company: str) -> List[str]:
    """Fetch recent news headlines about the company from NewsAPI."""
    if not settings.NEWS_API_KEY:
        return []

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://newsapi.org/v2/everything",
                params={
                    "q": f'"{company}"',
                    "sortBy": "publishedAt",
                    "pageSize": 5,
                    "language": "en",
                    "apiKey": settings.NEWS_API_KEY,
                },
            )
            response.raise_for_status()
            articles = response.json().get("articles", [])
            return [a.get("title", "") for a in articles if a.get("title")]
    except Exception as e:
        logger.debug(f"NewsAPI fetch failed for {company}: {e}")
        return []


async def _summarize_company_research(
    company: str,
    job_title: str,
    news_headlines: List[str],
) -> Dict[str, Any]:
    """Use Gemini Flash to summarize company research into 3-5 strategic insights."""
    if not settings.GEMINI_API_KEY:
        return {
            "summary": f"{company} is a potential employer for the {job_title} role.",
            "key_insights": [],
            "red_flags": [],
            "data_sources": [],
        }

    try:
        from app.services.ai.model_router import model_router
        model = model_router.get_generative_model("company_research_summary")

        news_section = "\n".join(f"- {h}" for h in news_headlines[:5]) if news_headlines else "No recent news found."

        prompt = f"""Analyze this company for a candidate considering a job offer.

Company: {company}
Role Being Considered: {job_title}

Recent News Headlines:
{news_section}

Provide a strategic briefing for the candidate in valid JSON:
{{
  "summary": "2-3 sentence company overview relevant to this role",
  "key_insights": [
    "3-5 specific, actionable insights about why this company is/isn't a good fit for this role"
  ],
  "red_flags": [
    "Any warning signs from recent news (layoffs, pivots, leadership changes, poor reviews)"
  ],
  "growth_signals": [
    "Positive signals like funding, expansion, strong product momentum"
  ],
  "data_sources": ["news"]
}}

Be specific. If no news is available, be honest about data limitations.
Return ONLY valid JSON."""

        response = model.generate_content(prompt)

        import json
        import re
        json_match = re.search(r"\{.*\}", response.text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except Exception as e:
        logger.warning(f"Company research summarization failed for {company}: {e}")

    return {
        "summary": f"Research on {company} is limited. Candidate should verify independently.",
        "key_insights": [f"Consider researching {company}'s recent news and Glassdoor reviews before applying"],
        "red_flags": [],
        "growth_signals": [],
        "data_sources": [],
    }


async def _research_single_company(job: Dict[str, Any]) -> Dict[str, Any]:
    """Research a single company and attach insights to the job candidate."""
    company = job.get("company", "")
    title = job.get("title", "")

    # Check cache first
    cached = _get_cached_research(company)
    if cached:
        logger.debug(f"Company research cache hit for {company}")
        return {**job, "company_research": cached}

    # Fetch news
    news = await _fetch_news_for_company(company)

    # Summarize with AI
    research = await _summarize_company_research(company, title, news)

    _set_cached_research(company, research)
    return {**job, "company_research": research}


async def research_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Research node: for each filtered job, fetch company intel and summarize.
    Results are cached per company with a 7-day TTL.
    """
    filtered_jobs = state.get("filtered_jobs", [])
    user_id = state["user_id"]

    if not filtered_jobs:
        logger.info(f"SDR Research: no jobs to research for user {user_id}")
        return {**state, "researched_jobs": [], "pipeline_stage": "research_complete"}

    logger.info(f"SDR Research: researching {len(filtered_jobs)} companies for user {user_id}")

    # Research all companies concurrently (with rate limiting)
    tasks = [_research_single_company(job) for job in filtered_jobs]
    researched = await asyncio.gather(*tasks, return_exceptions=True)

    # Filter out exceptions
    valid_researched = []
    for i, result in enumerate(researched):
        if isinstance(result, Exception):
            logger.error(f"Research failed for job {filtered_jobs[i].get('job_id')}: {result}")
            valid_researched.append(filtered_jobs[i])  # Include without research
        else:
            valid_researched.append(result)

    logger.info(f"SDR Research complete: {len(valid_researched)} jobs researched")

    return {
        **state,
        "researched_jobs": valid_researched,
        "pipeline_stage": "research_complete",
    }
