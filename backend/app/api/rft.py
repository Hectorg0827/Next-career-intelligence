"""
RFT (Reinforcement Fine-Tuning) Feedback API

Collects user feedback signals for training self-improving AI agents
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List
from app.db.supabase import get_supabase_client
from app.core.auth import get_current_user
from loguru import logger
from datetime import datetime
import json

router = APIRouter(prefix="/api/rft", tags=["rft"])


class RFTFeedbackCreate(BaseModel):
    """User feedback for RFT training"""
    event_type: str  # 'resume_bullet_accepted', 'resume_bullet_rejected', 'interview_answer_rated'
    agent_name: str  # 'resume_studio', 'interviewer_ai', 'career_coach'
    prompt: str  # Input to the AI model
    model_output: str  # What the AI generated
    preferred_output: Optional[str] = None  # What user actually wanted (if rejected)
    user_rating: Optional[int] = None  # 1-5 stars
    user_accepted: Optional[bool] = None  # Did user accept the suggestion?
    user_edited: Optional[bool] = False  # Did user manually edit?
    context_data: Dict = {}  # Additional context (job description, etc.)
    related_job_id: Optional[str] = None
    related_application_id: Optional[str] = None
    related_session_id: Optional[str] = None


class ApplicationSuccessUpdate(BaseModel):
    """Update feedback with ultimate success signal"""
    application_id: str
    status: str  # 'interview' or 'offer'


@router.post("/feedback")
async def record_feedback(
    feedback: RFTFeedbackCreate,
    current_user = Depends(get_current_user)
):
    """
    Record user feedback for RFT training

    This is the core data collection endpoint. Every time a user:
    - Accepts/rejects an AI suggestion
    - Rates AI-generated content
    - Manually edits AI output

    We capture that signal for model improvement.
    """
    try:
        feedback_record = {
            "user_id": current_user.id,
            "event_type": feedback.event_type,
            "agent_name": feedback.agent_name,
            "prompt": feedback.prompt,
            "model_output": feedback.model_output,
            "preferred_output": feedback.preferred_output,
            "user_rating": feedback.user_rating,
            "user_accepted": feedback.user_accepted,
            "user_edited": feedback.user_edited,
            "context_data": feedback.context_data,
            "related_job_id": feedback.related_job_id,
            "related_application_id": feedback.related_application_id,
            "related_session_id": feedback.related_session_id,
            "created_at": datetime.utcnow().isoformat()
        }

        # Insert into database
        response = supabase.table("rft_feedback").insert(feedback_record).execute()

        feedback_id = response.data[0]["id"] if response.data else None

        logger.info(
            f"RFT Feedback recorded: {feedback.event_type} for {feedback.agent_name} "
            f"(user: {current_user.id}, accepted: {feedback.user_accepted})"
        )

        return {
            "status": "recorded",
            "feedback_id": feedback_id,
            "message": "Thank you! Your feedback helps improve our AI."
        }

    except Exception as e:
        logger.error(f"Failed to record RFT feedback: {e}")
        raise HTTPException(status_code=500, detail="Failed to record feedback")


@router.patch("/feedback/{feedback_id}/success")
async def update_feedback_success(
    feedback_id: str,
    led_to_interview: Optional[bool] = None,
    led_to_offer: Optional[bool] = None,
    current_user = Depends(get_current_user)
):
    """
    Update feedback with ultimate success signal

    When a user gets an interview or offer, we retroactively update
    all related feedback to mark it as successful.

    This is the ULTIMATE reward signal for RL.
    """
    try:
        update_data = {}
        if led_to_interview is not None:
            update_data["led_to_interview"] = led_to_interview
        if led_to_offer is not None:
            update_data["led_to_offer"] = led_to_offer

        update_data["updated_at"] = datetime.utcnow().isoformat()

        response = supabase.table("rft_feedback") \
            .update(update_data) \
            .eq("id", feedback_id) \
            .eq("user_id", current_user.id) \
            .execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Feedback not found")

        logger.info(
            f"RFT Feedback updated with success signal: {feedback_id} "
            f"(interview: {led_to_interview}, offer: {led_to_offer})"
        )

        return {
            "status": "updated",
            "message": "Success signal recorded"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update feedback success: {e}")
        raise HTTPException(status_code=500, detail="Failed to update feedback")


@router.post("/application-success")
async def mark_application_success(
    update: ApplicationSuccessUpdate,
    current_user = Depends(get_current_user)
):
    """
    Mark all feedback related to an application as successful

    When user updates application status to 'interview' or 'offer',
    find all related feedback and mark it.
    """
    try:
        # Find all feedback related to this application
        feedback_response = supabase.table("rft_feedback") \
            .select("id") \
            .eq("user_id", current_user.id) \
            .eq("related_application_id", update.application_id) \
            .execute()

        feedback_ids = [f["id"] for f in feedback_response.data] if feedback_response.data else []

        if not feedback_ids:
            return {
                "status": "no_feedback_found",
                "message": "No feedback found for this application"
            }

        # Update all related feedback
        update_data = {
            "led_to_interview": update.status in ["interview", "offer"],
            "led_to_offer": update.status == "offer",
            "updated_at": datetime.utcnow().isoformat()
        }

        for feedback_id in feedback_ids:
            supabase.table("rft_feedback") \
                .update(update_data) \
                .eq("id", feedback_id) \
                .execute()

        logger.info(
            f"Marked {len(feedback_ids)} feedback records as {update.status} "
            f"for application {update.application_id}"
        )

        return {
            "status": "updated",
            "feedback_count": len(feedback_ids),
            "message": f"Marked {len(feedback_ids)} feedback records with success signal"
        }

    except Exception as e:
        logger.error(f"Failed to mark application success: {e}")
        raise HTTPException(status_code=500, detail="Failed to mark application success")


@router.get("/feedback/my")
async def get_my_feedback(
    limit: int = 50,
    current_user = Depends(get_current_user)
):
    """Get user's feedback history"""
    try:
        response = supabase.table("rft_feedback") \
            .select("*") \
            .eq("user_id", current_user.id) \
            .order("created_at", desc=True) \
            .limit(limit) \
            .execute()

        feedback = response.data if response.data else []

        return {
            "feedback": feedback,
            "count": len(feedback)
        }

    except Exception as e:
        logger.error(f"Failed to fetch feedback: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch feedback")


@router.get("/feedback/stats")
async def get_feedback_stats(current_user = Depends(get_current_user)):
    """Get user's feedback statistics"""
    try:
        # Total feedback count
        total_response = supabase.table("rft_feedback") \
            .select("id", count="exact") \
            .eq("user_id", current_user.id) \
            .execute()

        total_count = total_response.count or 0

        # Acceptance rate
        accepted_response = supabase.table("rft_feedback") \
            .select("id", count="exact") \
            .eq("user_id", current_user.id) \
            .eq("user_accepted", True) \
            .execute()

        accepted_count = accepted_response.count or 0
        acceptance_rate = (accepted_count / total_count * 100) if total_count > 0 else 0

        # Success rate
        success_response = supabase.table("rft_feedback") \
            .select("id", count="exact") \
            .eq("user_id", current_user.id) \
            .or_("led_to_interview.eq.true,led_to_offer.eq.true") \
            .execute()

        success_count = success_response.count or 0
        success_rate = (success_count / total_count * 100) if total_count > 0 else 0

        # By agent
        by_agent_response = supabase.table("rft_feedback") \
            .select("agent_name") \
            .eq("user_id", current_user.id) \
            .execute()

        agent_counts = {}
        if by_agent_response.data:
            for record in by_agent_response.data:
                agent = record.get("agent_name", "unknown")
                agent_counts[agent] = agent_counts.get(agent, 0) + 1

        return {
            "total_feedback": total_count,
            "accepted_count": accepted_count,
            "acceptance_rate": round(acceptance_rate, 1),
            "success_count": success_count,
            "success_rate": round(success_rate, 1),
            "by_agent": agent_counts
        }

    except Exception as e:
        logger.error(f"Failed to fetch feedback stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch stats")


@router.get("/models/active")
async def get_active_models():
    """Get currently active RFT model versions"""
    try:
        response = supabase.table("rft_model_versions") \
            .select("*") \
            .eq("is_active", True) \
            .execute()

        models = response.data if response.data else []

        return {
            "active_models": models,
            "count": len(models)
        }

    except Exception as e:
        logger.error(f"Failed to fetch active models: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch models")
