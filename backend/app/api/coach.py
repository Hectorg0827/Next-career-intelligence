"""AI Career Coach API - ChatGPT-style Conversational Chatbot"""

from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional, Dict, List, Any
from datetime import datetime
from loguru import logger
from pydantic import BaseModel
import uuid
import json

from app.db.database import get_db
from app.models.database import User, Conversation, CoachMessage
# Assuming we have models for CoachMemory and CareerGoal, otherwise raw SQL
from app.services.ai_coach_service import coach_service

router = APIRouter(prefix="/coach", tags=["AI Coach"])


class StartConversationRequest(BaseModel):
    firebase_uid: str
    career_context: Optional[Dict] = None


class SendMessageRequest(BaseModel):
    firebase_uid: str
    conversation_id: str
    message: str


class ConversationResponse(BaseModel):
    conversation_id: str
    message: str
    timestamp: str
    role: str
    suggestions: Optional[List[Any]] = None
    goal_updates: Optional[List[Any]] = None
    next_actions: Optional[List[str]] = None


@router.post("/conversations/start", response_model=ConversationResponse)
async def start_conversation(request: StartConversationRequest, db: Session = Depends(get_db)):
    """Start new AI Coach conversation"""
    try:
        user = db.query(User).filter(User.firebase_uid == request.firebase_uid).first()
        if not user:
            raise HTTPException(404, "User not found")

        # Load Memory
        memory_result = db.execute(
            "SELECT summary FROM public.coach_memory WHERE user_id = :uid", 
            {"uid": str(user.id)}
        ).fetchone()
        memory_summary = memory_result[0] if memory_result else None

        # Prepare Context
        context = request.career_context or {}
        context["memory_summary"] = memory_summary
        
        # Load Goals (Simplified)
        goals_result = db.execute(
            "SELECT goal_title FROM public.career_goals WHERE user_id = :uid AND status = 'active'",
            {"uid": str(user.id)}
        ).fetchall()
        if goals_result:
            context["goals"] = [g[0] for g in goals_result]

        # Create conversation in database
        conversation = Conversation(
            user_id=str(user.id), career_context=context, title="New Conversation"
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        # Get AI response
        response = await coach_service.start_conversation(
            user_id=str(user.id), user_name=user.name or "there", career_context=context
        )

        # Save assistant message
        assistant_message = CoachMessage(
            conversation_id=str(conversation.id), role="assistant", content=response["message"]
        )
        db.add(assistant_message)
        db.commit()

        logger.info(f"Started conversation {conversation.id} for user {user.email}")

        return ConversationResponse(
            conversation_id=str(conversation.id),
            message=response["message"],
            timestamp=response["timestamp"],
            role="assistant",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start conversation: {e}")
        db.rollback()
        raise HTTPException(500, str(e))


@router.post("/conversations/message", response_model=ConversationResponse)
async def send_message(
    request: SendMessageRequest, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Send message and get AI response"""
    try:
        user = db.query(User).filter(User.firebase_uid == request.firebase_uid).first()
        if not user:
            raise HTTPException(404, "User not found")

        # Get conversation
        conversation = (
            db.query(Conversation)
            .filter(Conversation.id == request.conversation_id, Conversation.user_id == str(user.id))
            .first()
        )

        if not conversation:
            raise HTTPException(404, "Conversation not found")

        # Get conversation history
        messages = (
            db.query(CoachMessage)
            .filter(CoachMessage.conversation_id == request.conversation_id)
            .order_by(CoachMessage.created_at)
            .all()
        )

        history = [{"role": m.role, "content": m.content} for m in messages]

        # Save user message
        user_message = CoachMessage(conversation_id=request.conversation_id, role="user", content=request.message)
        db.add(user_message)
        db.commit()

        # Prepare Context (Reload fresh data)
        memory_result = db.execute(
            "SELECT summary FROM public.coach_memory WHERE user_id = :uid", 
            {"uid": str(user.id)}
        ).fetchone()
        memory_summary = memory_result[0] if memory_result else None
        
        context = conversation.career_context or {}
        context["memory_summary"] = memory_summary

        # Get AI response
        response = await coach_service.send_message(
            user_id=str(user.id),
            message=request.message,
            conversation_history=history,
            user_context=context,
            db_session=db # Pass DB for skill mining
        )

        # Save assistant message
        assistant_message = CoachMessage(
            conversation_id=request.conversation_id,
            role="assistant",
            content=response["message"],
            suggestions=response.get("suggestions"),
        )
        db.add(assistant_message)
        
        # Handle Goal Updates
        if response.get("goal_updates"):
            for update in response["goal_updates"]:
                # Simple insert for now
                if update.get("action") == "new":
                    data = update.get("goal_data", {})
                    db.execute(
                        """
                        INSERT INTO public.career_goals (
                            user_id, goal_title, specific, measurable, achievable, relevant, time_bound, status, created_at, updated_at
                        ) VALUES (
                            :uid, :title, :s, :m, :a, :r, :t, 'active', NOW(), NOW()
                        )
                        """,
                        {
                            "uid": str(user.id),
                            "title": data.get("goal_title", "New Goal"),
                            "s": data.get("specific", ""),
                            "m": data.get("measurable", ""),
                            "a": data.get("achievable", ""),
                            "r": data.get("relevant", ""),
                            "t": data.get("time_bound", "")
                        }
                    )
        
        # Update conversation timestamp
        conversation.last_message_at = datetime.utcnow()
        db.commit()

        # Background Task: Update Long-Term Memory
        # We do this every turn for now, or could be sampled
        background_tasks.add_task(
            update_memory_task, 
            str(user.id), 
            memory_summary, 
            history + [{"role": "user", "content": request.message}, {"role": "assistant", "content": response["message"]}]
        )

        return ConversationResponse(
            conversation_id=request.conversation_id,
            message=response["message"],
            timestamp=response["timestamp"],
            role="assistant",
            suggestions=response.get("suggestions"),
            goal_updates=response.get("goal_updates"),
            next_actions=response.get("next_actions")
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        db.rollback()
        raise HTTPException(500, str(e))

async def update_memory_task(user_id: str, old_summary: str, recent_turns: List[Dict]):
    """Background task to update coach memory"""
    try:
        # We need a new DB session for background task
        # For simplicity in this snippet, we'll skip the DB write here or assume coach_service handles it if we passed a session factory.
        # But wait, coach_service.update_long_term_memory just returns the string.
        # We need to write it.
        
        new_summary = await coach_service.update_long_term_memory(user_id, old_summary, recent_turns)
        
        # Quick and dirty DB update (in real app, use dependency injection for session)
        from app.db.database import SessionLocal
        db = SessionLocal()
        try:
            db.execute(
                """
                INSERT INTO public.coach_memory (user_id, summary, last_updated_at)
                VALUES (:uid, :summary, NOW())
                ON CONFLICT (user_id) DO UPDATE SET
                summary = :summary,
                last_updated_at = NOW()
                """,
                {"uid": user_id, "summary": new_summary}
            )
            db.commit()
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Background memory update failed: {e}")

# ... (Keep existing list_conversations, get_conversation, etc.)
