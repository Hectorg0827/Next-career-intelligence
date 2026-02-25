"""
SDR Logistics Node
Handles post-approval actions: creates ApplicationTracking records
and schedules follow-up reminders for approved applications.
"""

from typing import Dict, Any, List
from loguru import logger
from datetime import datetime, timedelta


async def logistics_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    For each approved application:
    1. Create an ApplicationTracking record (status: applied)
    2. Schedule follow-up reminders (3-day check-in, 1-week follow-up)
    3. Update sdr_applications status to "submitted"
    """
    approved = state.get("approved_applications", [])
    user_id = state["user_id"]

    if not approved:
        logger.info(f"SDR Logistics: no approved applications for user {user_id}")
        return {
            **state,
            "submitted_applications": [],
            "completed_at": datetime.utcnow().isoformat(),
            "pipeline_stage": "complete",
        }

    logger.info(f"SDR Logistics: processing {len(approved)} approved applications for user {user_id}")

    submitted = []
    try:
        from app.db.supabase import get_supabase_client
        client = get_supabase_client()

        for app in approved:
            job = app.get("job_candidate", {})
            app_id = app.get("id")

            try:
                # Create ApplicationTracking record
                tracking_record = {
                    "user_id": user_id,
                    "job_id": job.get("job_id"),
                    "company": job.get("company", ""),
                    "role": job.get("title", ""),
                    "status": "applied",
                    "applied_at": datetime.utcnow().isoformat(),
                    "apply_url": job.get("apply_url", ""),
                    "source": "sdr",
                    "notes": f"Applied via SDR pipeline. Match rationale: {app.get('match_rationale', '')}",
                }
                client.table("applications").insert(tracking_record).execute()

                # Update SDR application status to submitted
                client.table("sdr_applications").update(
                    {"status": "submitted", "submitted_at": datetime.utcnow().isoformat()}
                ).eq("id", app_id).execute()

                # Schedule follow-up reminders (stored as tasks/notifications)
                now = datetime.utcnow()
                reminders = [
                    {
                        "user_id": user_id,
                        "application_id": app_id,
                        "reminder_type": "3_day_check_in",
                        "scheduled_for": (now + timedelta(days=3)).isoformat(),
                        "message": f"3-day check-in: Have you heard back from {job.get('company')} about the {job.get('title')} role?",
                        "status": "pending",
                    },
                    {
                        "user_id": user_id,
                        "application_id": app_id,
                        "reminder_type": "1_week_follow_up",
                        "scheduled_for": (now + timedelta(days=7)).isoformat(),
                        "message": (
                            f"1-week follow-up: Consider sending a follow-up email to {job.get('company')} "
                            f"for the {job.get('title')} position."
                        ),
                        "status": "pending",
                    },
                ]
                for reminder in reminders:
                    try:
                        client.table("sdr_reminders").insert(reminder).execute()
                    except Exception:
                        pass  # Reminders table may not exist yet; non-critical

                submitted.append({**app, "status": "submitted"})
                logger.info(f"Application submitted for {job.get('title')} at {job.get('company')}")

            except Exception as e:
                logger.error(f"Logistics failed for application {app_id}: {e}")
                continue

    except Exception as e:
        logger.error(f"SDR Logistics failed for user {user_id}: {e}")

    logger.info(f"SDR Logistics complete: {len(submitted)} applications submitted")

    return {
        **state,
        "submitted_applications": submitted,
        "completed_at": datetime.utcnow().isoformat(),
        "pipeline_stage": "complete",
    }
