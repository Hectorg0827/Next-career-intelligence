"""AI Career Coach API - ChatGPT-style Conversational Chatbot"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional, Dict
from datetime import datetime
from loguru import logger
from pydantic import BaseModel
import uuid
import json

from app.db.database import get_db
from app.models.database import User, Conversation, CoachMessage
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


@router.post("/conversations/start", response_model=ConversationResponse)
async def start_conversation(request: StartConversationRequest, db: Session = Depends(get_db)):
    """Start new AI Coach conversation"""
    try:
        user = db.query(User).filter(User.firebase_uid == request.firebase_uid).first()
        if not user:
            raise HTTPException(404, "User not found")
        
        # Check subscription (optional: comment out for testing)
        # if user.subscription_status not in ['pro', 'enterprise']:
        #     raise HTTPException(402, "AI Coach requires Pro subscription")
        
        # Create conversation in database
        conversation = Conversation(
            user_id=str(user.id),
            career_context=request.career_context,
            title="New Conversation"
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        
        # Get AI response
        response = await coach_service.start_conversation(
            user_id=str(user.id),
            user_name=user.name or "there",
            career_context=request.career_context
        )
        
        # Save assistant message
        assistant_message = CoachMessage(
            conversation_id=str(conversation.id),
            role="assistant",
            content=response["message"]
        )
        db.add(assistant_message)
        
        # Update conversation timestamp
        conversation.last_message_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Started conversation {conversation.id} for user {user.email}")
        
        return ConversationResponse(
            conversation_id=str(conversation.id),
            message=response["message"],
            timestamp=response["timestamp"],
            role="assistant"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start conversation: {e}")
        db.rollback()
        raise HTTPException(500, str(e))


@router.post("/conversations/message", response_model=ConversationResponse)
async def send_message(request: SendMessageRequest, db: Session = Depends(get_db)):
    """Send message and get AI response"""
    try:
        user = db.query(User).filter(User.firebase_uid == request.firebase_uid).first()
        if not user:
            raise HTTPException(404, "User not found")
        
        # Check subscription (optional: comment out for testing)
        # if user.subscription_status not in ['pro', 'enterprise']:
        #     raise HTTPException(402, "AI Coach requires Pro subscription")
        
        # Get conversation
        conversation = db.query(Conversation).filter(
            Conversation.id == request.conversation_id,
            Conversation.user_id == str(user.id)
        ).first()
        
        if not conversation:
            raise HTTPException(404, "Conversation not found")
        
        # Get conversation history from database
        messages = db.query(CoachMessage).filter(
            CoachMessage.conversation_id == request.conversation_id
        ).order_by(CoachMessage.created_at).all()
        
        history = [{"role": m.role, "content": m.content} for m in messages]
        
        # Save user message
        user_message = CoachMessage(
            conversation_id=request.conversation_id,
            role="user",
            content=request.message
        )
        db.add(user_message)
        db.commit()
        
        # Get AI response
        response = await coach_service.send_message(
            user_id=str(user.id),
            message=request.message,
            conversation_history=history,
            user_context=conversation.career_context or {}
        )
        
        # Save assistant message
        assistant_message = CoachMessage(
            conversation_id=request.conversation_id,
            role="assistant",
            content=response["message"],
            suggestions=response.get("suggestions")
        )
        db.add(assistant_message)
        
        # Update conversation
        conversation.last_message_at = datetime.utcnow()
        
        # Auto-generate title from first user message if needed
        if conversation.title == "New Conversation" and len(history) == 1:
            conversation.title = request.message[:50] + ("..." if len(request.message) > 50 else "")
        
        db.commit()
        
        logger.info(f"Message sent in conversation {conversation.id}")
        
        return ConversationResponse(
            conversation_id=request.conversation_id,
            message=response["message"],
            timestamp=response["timestamp"],
            role="assistant"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        db.rollback()
        raise HTTPException(500, str(e))


@router.get("/conversations")
async def list_conversations(firebase_uid: str, db: Session = Depends(get_db)):
    """List all conversations for a user"""
    try:
        user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
        if not user:
            raise HTTPException(404, "User not found")
        
        conversations = db.query(Conversation).filter(
            Conversation.user_id == str(user.id)
        ).order_by(Conversation.last_message_at.desc()).all()
        
        return {
            "conversations": [
                {
                    "id": str(conv.id),
                    "title": conv.title,
                    "created_at": conv.created_at.isoformat(),
                    "last_message_at": conv.last_message_at.isoformat(),
                    "is_active": conv.is_active,
                    "message_count": len(conv.messages)
                }
                for conv in conversations
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list conversations: {e}")
        raise HTTPException(500, str(e))


@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str, firebase_uid: str, db: Session = Depends(get_db)):
    """Get full conversation with all messages"""
    try:
        user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
        if not user:
            raise HTTPException(404, "User not found")
        
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == str(user.id)
        ).first()
        
        if not conversation:
            raise HTTPException(404, "Conversation not found")
        
        messages = db.query(CoachMessage).filter(
            CoachMessage.conversation_id == conversation_id
        ).order_by(CoachMessage.created_at).all()
        
        return {
            "conversation": {
                "id": str(conversation.id),
                "title": conversation.title,
                "created_at": conversation.created_at.isoformat(),
                "last_message_at": conversation.last_message_at.isoformat(),
                "is_active": conversation.is_active,
                "career_context": conversation.career_context
            },
            "messages": [
                {
                    "id": str(msg.id),
                    "role": msg.role,
                    "content": msg.content,
                    "suggestions": msg.suggestions,
                    "created_at": msg.created_at.isoformat()
                }
                for msg in messages
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get conversation: {e}")
        raise HTTPException(500, str(e))


@router.put("/conversations/{conversation_id}/archive")
async def archive_conversation(conversation_id: str, firebase_uid: str, db: Session = Depends(get_db)):
    """Archive a conversation"""
    try:
        user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
        if not user:
            raise HTTPException(404, "User not found")
        
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == str(user.id)
        ).first()
        
        if not conversation:
            raise HTTPException(404, "Conversation not found")
        
        conversation.is_active = "archived"
        conversation.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Archived conversation {conversation_id}")
        
        return {
            "id": str(conversation.id),
            "is_active": conversation.is_active,
            "message": "Conversation archived successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to archive conversation: {e}")
        db.rollback()
        raise HTTPException(500, str(e))


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str, firebase_uid: str, db: Session = Depends(get_db)):
    """Delete a conversation"""
    try:
        user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
        if not user:
            raise HTTPException(404, "User not found")
        
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == str(user.id)
        ).first()
        
        if not conversation:
            raise HTTPException(404, "Conversation not found")
        
        db.delete(conversation)
        db.commit()
        
        logger.info(f"Deleted conversation {conversation_id}")
        
        return {"message": "Conversation deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete conversation: {e}")
        db.rollback()
        raise HTTPException(500, str(e))


@router.get("/conversations/{conversation_id}/history")
async def get_conversation_history(conversation_id: str, firebase_uid: str, db: Session = Depends(get_db)):
    """Get conversation history"""
    try:
        user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
        if not user:
            raise HTTPException(404, "User not found")
        
        if user.subscription_status not in ['pro', 'enterprise']:
            raise HTTPException(402, "AI Coach requires Pro subscription")
        
        client = get_supabase_client()
        if not client:
            return {"conversation_id": conversation_id, "messages": []}
        
        response = client.table('coach_messages').select('*').eq('conversation_id', conversation_id).order('created_at', desc=False).execute()
        
        return {
            "conversation_id": conversation_id,
            "messages": response.data or [],
            "message_count": len(response.data or [])
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get history: {e}")
        raise HTTPException(500, str(e))
