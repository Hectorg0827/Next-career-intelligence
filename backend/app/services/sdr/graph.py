"""
SDR Pipeline Graph
Orchestrates the Autonomous Candidate SDR workflow.

Graph flow:
    discovery → filter → [quota_check] → research → synthesis → approval_gate → logistics

Note: This implementation uses a simple sequential async orchestrator rather than
LangGraph, to avoid the external dependency until the platform validates the feature
with real users. The LangGraph migration path is documented below and can be swapped
in when needed by installing langgraph>=0.2.0 and replacing the run_sdr_for_user function.

LangGraph migration path (when ready):
    from langgraph.graph import StateGraph, END
    workflow = StateGraph(SDRState)
    workflow.add_node("discovery", discovery_node)
    workflow.add_node("filter", filter_node)
    workflow.add_node("research", research_node)
    workflow.add_node("synthesis", synthesis_node)
    workflow.add_node("logistics", logistics_node)
    workflow.add_conditional_edges("filter", check_quota, {"continue": "research", "quota_exceeded": END})
    sdr_graph = workflow.compile(checkpointer=postgres_checkpointer)
"""

import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger

from app.services.sdr.sdr_state import SDRState, SDRCriteria
from app.services.sdr.nodes.discovery_node import discovery_node, filter_node
from app.services.sdr.nodes.research_node import research_node
from app.services.sdr.nodes.synthesis_node import synthesis_node
from app.services.sdr.nodes.logistics_node import logistics_node


async def _get_quota_used_this_week(user_id: str) -> int:
    """Count applications submitted this week for quota enforcement."""
    try:
        from app.db.supabase import get_supabase_client
        client = get_supabase_client()
        result = client.table("sdr_applications").select("id", count="exact").eq(
            "user_id", user_id
        ).eq("status", "submitted").gte(
            "submitted_at", "now() - interval '7 days'"
        ).execute()
        return result.count or 0
    except Exception:
        return 0


async def _record_sdr_run_start(user_id: str, run_id: str) -> None:
    """Record the start of an SDR run in sdr_runs table."""
    try:
        from app.db.supabase import get_supabase_client
        client = get_supabase_client()
        client.table("sdr_runs").insert({
            "id": run_id,
            "user_id": user_id,
            "started_at": datetime.utcnow().isoformat(),
            "status": "running",
        }).execute()
    except Exception as e:
        logger.warning(f"Could not record SDR run start: {e}")


async def _record_sdr_run_complete(run_id: str, final_state: Dict[str, Any]) -> None:
    """Update the sdr_runs record with final statistics."""
    try:
        from app.db.supabase import get_supabase_client
        client = get_supabase_client()
        client.table("sdr_runs").update({
            "completed_at": datetime.utcnow().isoformat(),
            "status": "complete" if not final_state.get("error") else "error",
            "jobs_discovered": len(final_state.get("discovered_jobs", [])),
            "jobs_filtered": len(final_state.get("filtered_jobs", [])),
            "jobs_researched": len(final_state.get("researched_jobs", [])),
            "applications_generated": len(final_state.get("synthesized_applications", [])),
            "applications_submitted": len(final_state.get("submitted_applications", [])),
            "error": final_state.get("error"),
        }).eq("id", run_id).execute()
    except Exception as e:
        logger.warning(f"Could not record SDR run completion: {e}")


async def run_sdr_for_user(
    user_id: str,
    criteria: Optional[Dict[str, Any]] = None,
    approved_app_ids: Optional[list] = None,
) -> Dict[str, Any]:
    """
    Execute the full SDR pipeline for a single user.

    Args:
        user_id: The user to run SDR for
        criteria: SDR criteria dict (fetched from DB if not provided)
        approved_app_ids: If provided, skip discovery/research/synthesis and
                          proceed directly to logistics for pre-approved apps

    Returns:
        Final pipeline state dict with stats
    """
    run_id = str(uuid.uuid4())

    # Fetch criteria from DB if not provided
    if not criteria:
        try:
            from app.db.supabase import get_supabase_client
            client = get_supabase_client()
            result = client.table("sdr_criteria").select("*").eq("user_id", user_id).eq(
                "is_enabled", True
            ).limit(1).execute()
            if not result.data:
                return {"error": "No SDR criteria configured for user", "user_id": user_id}
            criteria = result.data[0]
        except Exception as e:
            return {"error": f"Failed to fetch SDR criteria: {e}", "user_id": user_id}

    quota_used = await _get_quota_used_this_week(user_id)
    quota_limit = min(
        criteria.get("quota_weekly", 5),
        10,  # Hard platform cap
    )

    await _record_sdr_run_start(user_id, run_id)

    # Initialize state
    state: Dict[str, Any] = {
        "user_id": user_id,
        "run_id": run_id,
        "criteria": {
            "target_roles": criteria.get("target_roles", []),
            "salary_min": criteria.get("salary_min", 0),
            "salary_max": criteria.get("salary_max", 0),
            "locations": criteria.get("locations", []),
            "company_blacklist": criteria.get("company_blacklist", []),
            "company_whitelist": criteria.get("company_whitelist", []),
            "quota_weekly": quota_limit,
            "remote_required": criteria.get("remote_required", False),
            "employment_types": criteria.get("employment_types", ["full_time"]),
        },
        "discovered_jobs": [],
        "filtered_jobs": [],
        "researched_jobs": [],
        "synthesized_applications": [],
        "awaiting_approval": [],
        "approved_applications": [],
        "rejected_applications": [],
        "submitted_applications": [],
        "quota_used_this_week": quota_used,
        "quota_limit": quota_limit,
        "started_at": datetime.utcnow().isoformat(),
        "completed_at": None,
        "error": None,
        "pipeline_stage": "initialized",
    }

    # Handle logistics-only path (approved apps coming in from approval gate)
    if approved_app_ids:
        try:
            from app.db.supabase import get_supabase_client
            client = get_supabase_client()
            result = client.table("sdr_applications").select("*").in_("id", approved_app_ids).execute()
            approved_apps = result.data or []

            # Convert DB records back to application dicts
            reconstructed = [
                {
                    "id": a["id"],
                    "job_candidate": {"job_id": a.get("job_id"), "company": "", "title": ""},
                    "cover_letter": a.get("cover_letter", ""),
                    "match_rationale": a.get("match_rationale", ""),
                    "status": "approved",
                    "created_at": a.get("created_at", ""),
                }
                for a in approved_apps
            ]
            state["approved_applications"] = reconstructed
            state = await logistics_node(state)
        except Exception as e:
            state["error"] = str(e)
        await _record_sdr_run_complete(run_id, state)
        return state

    # Full pipeline execution
    try:
        logger.info(f"SDR pipeline starting for user {user_id} (run {run_id})")

        state = await discovery_node(state)
        if state.get("error"):
            raise RuntimeError(state["error"])

        state = await filter_node(state)

        if not state.get("filtered_jobs"):
            if state.get("pipeline_stage") == "quota_exceeded":
                logger.info(f"SDR: user {user_id} quota exceeded, stopping pipeline")
            else:
                logger.info(f"SDR: no matching jobs found for user {user_id}")
            await _record_sdr_run_complete(run_id, state)
            return state

        state = await research_node(state)
        state = await synthesis_node(state)

        # Pipeline suspends here — applications are in awaiting_approval state in DB
        # Logistics will run when user approves via /api/sdr/approve endpoint
        logger.info(
            f"SDR pipeline paused at approval gate for user {user_id}: "
            f"{len(state.get('awaiting_approval', []))} applications awaiting review"
        )

    except Exception as e:
        logger.error(f"SDR pipeline error for user {user_id}: {e}")
        state["error"] = str(e)
        state["pipeline_stage"] = "error"

    await _record_sdr_run_complete(run_id, state)
    return state
