"""
SDR (Autonomous Candidate SDR) API
Manages the autonomous job application pipeline.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from app.core.database_pool import get_supabase
from loguru import logger

router = APIRouter(prefix="/sdr", tags=["Autonomous SDR"])


# --- Request/Response Models ---

class SDRCriteriaRequest(BaseModel):
    target_roles: List[str] = Field(..., description="Job titles to target, e.g. ['Senior Software Engineer']")
    salary_min: int = Field(0, description="Minimum acceptable base salary")
    salary_max: int = Field(0, description="Maximum salary cap (0 = no cap)")
    locations: List[str] = Field(default=["Remote"], description="Preferred locations")
    company_blacklist: List[str] = Field(default=[], description="Companies to never apply to")
    company_whitelist: List[str] = Field(default=[], description="If set, only apply to these companies")
    quota_weekly: int = Field(5, ge=1, le=10, description="Max applications per week (1-10)")
    remote_required: bool = Field(False, description="Only consider remote roles")
    is_enabled: bool = Field(True, description="Whether SDR is active")


class ApprovalRequest(BaseModel):
    feedback: Optional[str] = Field(None, description="Optional feedback for rejected applications")


class SDRRunRequest(BaseModel):
    force: bool = Field(False, description="Force run even if quota is exhausted")


# --- Endpoints ---

@router.post("/configure")
async def configure_sdr(
    request: SDRCriteriaRequest,
    user_id: str,  # In production, extract from auth token
):
    """Configure SDR targeting criteria for the user."""
    db = get_supabase()

    criteria_data = {
        "user_id": user_id,
        "target_roles": request.target_roles,
        "salary_min": request.salary_min,
        "salary_max": request.salary_max,
        "locations": request.locations,
        "company_blacklist": request.company_blacklist,
        "company_whitelist": request.company_whitelist,
        "quota_weekly": min(request.quota_weekly, 10),  # Hard cap
        "remote_required": request.remote_required,
        "is_enabled": request.is_enabled,
        "updated_at": datetime.utcnow().isoformat(),
    }

    try:
        # Upsert criteria
        existing = db.table("sdr_criteria").select("id").eq("user_id", user_id).execute()
        if existing.data:
            db.table("sdr_criteria").update(criteria_data).eq("user_id", user_id).execute()
        else:
            db.table("sdr_criteria").insert({
                **criteria_data,
                "created_at": datetime.utcnow().isoformat(),
            }).execute()

        return {"status": "ok", "message": "SDR criteria saved", "criteria": criteria_data}

    except Exception as e:
        logger.error(f"Failed to save SDR criteria for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to save SDR criteria")


@router.get("/status")
async def get_sdr_status(user_id: str):
    """Get current SDR pipeline status, quota usage, and pending approvals."""
    db = get_supabase()

    try:
        # Get criteria
        criteria_result = db.table("sdr_criteria").select("*").eq("user_id", user_id).limit(1).execute()
        criteria = criteria_result.data[0] if criteria_result.data else None

        # Get quota used this week
        quota_result = db.table("sdr_applications").select(
            "id", count="exact"
        ).eq("user_id", user_id).eq("status", "submitted").gte(
            "submitted_at", "now() - interval '7 days'"
        ).execute()
        quota_used = quota_result.count or 0

        # Get pending approvals count
        pending_result = db.table("sdr_applications").select(
            "id", count="exact"
        ).eq("user_id", user_id).eq("status", "pending_approval").execute()
        pending_count = pending_result.count or 0

        # Get most recent run
        run_result = db.table("sdr_runs").select("*").eq("user_id", user_id).order(
            "started_at", desc=True
        ).limit(1).execute()
        last_run = run_result.data[0] if run_result.data else None

        return {
            "is_enabled": criteria.get("is_enabled", False) if criteria else False,
            "criteria_configured": criteria is not None,
            "quota_used_this_week": quota_used,
            "quota_limit": criteria.get("quota_weekly", 5) if criteria else 5,
            "pending_approvals": pending_count,
            "last_run": last_run,
        }

    except Exception as e:
        logger.error(f"Failed to get SDR status for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve SDR status")


@router.get("/pending")
async def get_pending_applications(user_id: str):
    """Get applications awaiting user approval."""
    db = get_supabase()

    try:
        result = db.table("sdr_applications").select(
            "id, job_id, cover_letter, match_rationale, company_research, created_at"
        ).eq("user_id", user_id).eq("status", "pending_approval").order(
            "created_at", desc=True
        ).execute()

        applications = result.data or []

        # Enrich with job details
        enriched = []
        for app in applications:
            job_id = app.get("job_id")
            job_data = {}
            if job_id:
                try:
                    job_result = db.table("jobs").select(
                        "title, company, location, salary_min, salary_max, apply_url, description"
                    ).eq("id", job_id).limit(1).execute()
                    job_data = job_result.data[0] if job_result.data else {}
                except Exception:
                    pass

            enriched.append({
                "application_id": app["id"],
                "job": job_data,
                "cover_letter": app.get("cover_letter", ""),
                "match_rationale": app.get("match_rationale", ""),
                "company_research": app.get("company_research", {}),
                "created_at": app.get("created_at"),
            })

        return {"pending_applications": enriched, "count": len(enriched)}

    except Exception as e:
        logger.error(f"Failed to get pending SDR applications for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve pending applications")


@router.post("/approve/{application_id}")
async def approve_application(
    application_id: str,
    user_id: str,
    background_tasks: BackgroundTasks,
):
    """Approve an application — triggers logistics (application tracking + reminders)."""
    db = get_supabase()

    try:
        # Verify ownership
        result = db.table("sdr_applications").select("id, user_id, status").eq(
            "id", application_id
        ).limit(1).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Application not found")

        app_record = result.data[0]
        if app_record["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Not authorized")

        if app_record["status"] != "pending_approval":
            raise HTTPException(status_code=400, detail=f"Application is already {app_record['status']}")

        # Mark as approved
        db.table("sdr_applications").update(
            {"status": "approved", "approved_at": datetime.utcnow().isoformat()}
        ).eq("id", application_id).execute()

        # Run logistics in background
        background_tasks.add_task(_run_logistics_for_approved, user_id, [application_id])

        return {"status": "approved", "application_id": application_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to approve application {application_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to approve application")


@router.post("/reject/{application_id}")
async def reject_application(
    application_id: str,
    user_id: str,
    request: ApprovalRequest,
):
    """Reject an application with optional feedback."""
    db = get_supabase()

    try:
        result = db.table("sdr_applications").select("id, user_id, status").eq(
            "id", application_id
        ).limit(1).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Application not found")

        if result.data[0]["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Not authorized")

        db.table("sdr_applications").update({
            "status": "rejected",
            "rejection_feedback": request.feedback,
            "rejected_at": datetime.utcnow().isoformat(),
        }).eq("id", application_id).execute()

        return {"status": "rejected", "application_id": application_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to reject application {application_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to reject application")


@router.post("/run")
async def trigger_sdr_run(
    user_id: str,
    request: SDRRunRequest,
    background_tasks: BackgroundTasks,
):
    """Manually trigger an SDR pipeline run for the user."""
    background_tasks.add_task(_run_sdr_background, user_id)
    return {
        "status": "started",
        "message": "SDR pipeline run started in background. Check /api/sdr/status for updates.",
    }


@router.get("/history")
async def get_sdr_history(user_id: str, limit: int = 10):
    """Get past SDR run history with statistics."""
    db = get_supabase()

    try:
        result = db.table("sdr_runs").select("*").eq("user_id", user_id).order(
            "started_at", desc=True
        ).limit(limit).execute()

        return {"runs": result.data or [], "count": len(result.data or [])}

    except Exception as e:
        logger.error(f"Failed to get SDR history for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve SDR history")


# --- Background task helpers ---

async def _run_sdr_background(user_id: str):
    """Background task: run the full SDR pipeline."""
    try:
        from app.services.sdr.graph import run_sdr_for_user
        await run_sdr_for_user(user_id=user_id)
    except Exception as e:
        logger.error(f"Background SDR run failed for user {user_id}: {e}")


async def _run_logistics_for_approved(user_id: str, app_ids: List[str]):
    """Background task: run logistics for approved applications."""
    try:
        from app.services.sdr.graph import run_sdr_for_user
        await run_sdr_for_user(user_id=user_id, approved_app_ids=app_ids)
    except Exception as e:
        logger.error(f"Background logistics failed for user {user_id}: {e}")
