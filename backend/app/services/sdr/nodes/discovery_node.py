"""
SDR Discovery Node
Finds jobs matching the user's SDR criteria from the existing jobs database.
"""

from typing import Dict, Any, List
from loguru import logger
from datetime import datetime


async def discovery_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Discover jobs matching the user's criteria from the jobs database.
    Uses the existing Supabase jobs table populated by JobAggregatorService.
    """
    user_id = state["user_id"]
    criteria = state["criteria"]

    logger.info(f"SDR Discovery: searching for jobs for user {user_id}")

    try:
        from app.db.supabase import get_supabase_client
        client = get_supabase_client()

        target_roles = criteria.get("target_roles", [])
        salary_min = criteria.get("salary_min", 0)
        locations = criteria.get("locations", [])
        company_blacklist = set(c.lower() for c in criteria.get("company_blacklist", []))
        company_whitelist = set(c.lower() for c in criteria.get("company_whitelist", []))
        remote_required = criteria.get("remote_required", False)

        # Fetch recent active jobs (last 14 days)
        query = client.table("jobs").select(
            "id, title, company, location, salary_min, salary_max, description, apply_url, source, posted_at"
        ).eq("is_active", True).gte(
            "posted_at", "now() - interval '14 days'"
        ).limit(500)

        if remote_required:
            query = query.eq("remote_policy", "remote")

        result = query.execute()
        all_jobs = result.data or []

        # Filter by criteria
        discovered: List[Dict[str, Any]] = []
        for job in all_jobs:
            job_title_lower = (job.get("title") or "").lower()
            job_company_lower = (job.get("company") or "").lower()
            job_salary_min = job.get("salary_min") or 0

            # Role matching: any target role keyword must appear in job title
            role_match = any(
                role_keyword.lower() in job_title_lower
                for role_keyword in target_roles
                if role_keyword
            ) if target_roles else True

            if not role_match:
                continue

            # Blacklist check
            if job_company_lower in company_blacklist:
                continue

            # Whitelist check (if set, only apply to whitelisted companies)
            if company_whitelist and job_company_lower not in company_whitelist:
                continue

            # Salary floor check (skip if max salary is explicitly below our minimum)
            if job_salary_min and salary_min and job_salary_min < salary_min * 0.7:
                continue

            match_reason = _explain_match(job, criteria, target_roles)
            discovered.append({
                "job_id": str(job.get("id")),
                "title": job.get("title", ""),
                "company": job.get("company", ""),
                "location": job.get("location", ""),
                "salary_min": job.get("salary_min"),
                "salary_max": job.get("salary_max"),
                "description": (job.get("description") or "")[:2000],  # Truncate for state
                "apply_url": job.get("apply_url") or job.get("external_url", ""),
                "source": job.get("source", ""),
                "posted_at": str(job.get("posted_at", "")),
                "match_reason": match_reason,
                "company_research": None,
            })

        logger.info(f"SDR Discovery complete: {len(all_jobs)} jobs fetched, {len(discovered)} matched criteria")

        return {
            **state,
            "discovered_jobs": discovered,
            "pipeline_stage": "discovery_complete",
        }

    except Exception as e:
        logger.error(f"SDR Discovery failed for user {user_id}: {e}")
        return {
            **state,
            "discovered_jobs": [],
            "error": f"Discovery failed: {str(e)}",
            "pipeline_stage": "discovery_error",
        }


def _explain_match(job: Dict[str, Any], criteria: Dict[str, Any], target_roles: List[str]) -> str:
    """Generate a brief human-readable match explanation."""
    reasons = []
    title = job.get("title", "")

    for role in target_roles:
        if role.lower() in title.lower():
            reasons.append(f"matches target role '{role}'")
            break

    if job.get("remote_policy") == "remote":
        reasons.append("fully remote")

    if job.get("salary_min") and job.get("salary_max"):
        reasons.append(f"salary ${job['salary_min']:,}–${job['salary_max']:,}")

    return "; ".join(reasons) if reasons else "matches search criteria"


async def filter_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Filter discovered jobs against quota and deduplication.
    This node enforces the weekly application cap.
    """
    user_id = state["user_id"]
    discovered = state.get("discovered_jobs", [])
    quota_used = state.get("quota_used_this_week", 0)
    quota_limit = state.get("quota_limit", 5)

    remaining_quota = quota_limit - quota_used
    if remaining_quota <= 0:
        logger.info(f"SDR Filter: user {user_id} has exhausted weekly quota ({quota_used}/{quota_limit})")
        return {
            **state,
            "filtered_jobs": [],
            "pipeline_stage": "quota_exceeded",
        }

    # Remove jobs already in sdr_applications for this user (de-duplicate)
    try:
        from app.db.supabase import get_supabase_client
        client = get_supabase_client()
        existing = client.table("sdr_applications").select("job_id").eq("user_id", user_id).execute()
        seen_job_ids = {str(row["job_id"]) for row in (existing.data or [])}
    except Exception as e:
        logger.warning(f"Could not fetch existing SDR applications for dedup: {e}")
        seen_job_ids = set()

    new_jobs = [j for j in discovered if j["job_id"] not in seen_job_ids]

    # Cap at remaining quota
    filtered = new_jobs[:remaining_quota]

    logger.info(
        f"SDR Filter: {len(discovered)} discovered → {len(new_jobs)} new → {len(filtered)} within quota "
        f"({quota_used}/{quota_limit} used)"
    )

    return {
        **state,
        "filtered_jobs": filtered,
        "pipeline_stage": "filter_complete",
    }
