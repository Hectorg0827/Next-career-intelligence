"""
AI Career Coach API - Conversational Chatbot (ChatGPT-style)
Premium Feature - Full conversational AI coaching
"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from datetime import datetime
from loguru import logger
from pydantic import BaseModel
import uuid

from app.db.database import get_db
from app.models.database import User
from app.services.ai_coach_service import coach_service

router = APIRouter(prefix="/coach", tags=["AI Coach - Premium"])


# ========================================
# PYDANTIC SCHEMAS
# ========================================

class StartConversationRequest(BaseModel):
    user_id: str
    career_context: Optional[Dict] = None

class SendMessageRequest(BaseModel):
    user_id: str
    message: str
    conversation_id: Optional[str] = None

class GenerateActionPlanRequest(BaseModel):
    user_id: str
    goal: str
    timeline: Optional[str] = "3 months"
    current_state: Dict

class ConversationResponse(BaseModel):
    conversation_id: str
    message: str
    timestamp: str
    role: str  # "assistant" or "user"

class ActionPlanResponse(BaseModel):
    plan_id: str
    goal: str
    timeline: str
    plan: Dict
    created_at: str


# ========================================
# HELPER FUNCTIONS
# ========================================

async def get_career_profile(user_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve career profile from Supabase"""
    try:
        client = get_supabase_client()
        if not client:
            return None

        response = client.table('career_profiles')\
            .select('*')\
            .eq('user_id', user_id)\
            .single()\
            .execute()

        return response.data if response.data else None
    except Exception as e:
        logger.error(f"Failed to get career profile: {e}")
        return None


async def get_conversation(conversation_id: str, user_id: str) -> Optional[Dict[str, Any]]:
    """Get existing conversation"""
    try:
        client = get_supabase_client()
        if not client:
            return None

        response = client.table('coach_conversations')\
            .select('*')\
            .eq('id', conversation_id)\
            .eq('user_id', user_id)\
            .single()\
            .execute()

        return response.data if response.data else None
    except Exception as e:
        logger.error(f"Failed to get conversation: {e}")
        return None


async def get_user_goals(user_id: str) -> List[Dict[str, Any]]:
    """Get user's career goals"""
    try:
        client = get_supabase_client()
        if not client:
            return []

        response = client.table('career_goals')\
            .select('*')\
            .eq('user_id', user_id)\
            .order('created_at', desc=True)\
            .execute()

        return response.data if response.data else []
    except Exception as e:
        logger.error(f"Failed to get goals: {e}")
        return []


# ========================================
# ENDPOINTS
# ========================================

@router.post("/chat", response_model=CoachResponse)
async def chat_with_coach(request: CoachRequest):
    """
    Chat with Career Coach AI
    Coach has READ-ONLY access to profile and generates suggestions
    """
    try:
        # 1. Get career profile (read-only)
        profile = await get_career_profile(request.user_id)
        if not profile:
            raise HTTPException(404, "Career profile not found. Please create a profile first in Resume Studio.")

        # 2. Get or create conversation
        conversation = None
        if request.conversation_id:
            conversation = await get_conversation(request.conversation_id, request.user_id)

        if not conversation:
            # Create new conversation
            conversation_id = str(uuid.uuid4())
            conversation = {
                'id': conversation_id,
                'user_id': request.user_id,
                'conversation_type': request.conversation_type,
                'messages': [],
                'insights': [],
                'status': 'active'
            }
        else:
            conversation_id = conversation['id']

        # 3. Get user's goals
        goals = await get_user_goals(request.user_id)

        # 4. Build conversation history
        messages = conversation.get('messages', [])
        conversation_history = "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in messages[-10:]  # Last 10 messages for context
        ])

        # 5. Get prompts
        prompt_set = get_prompt_set('career_coach', 'respond')

        # 6. Build task prompt with data
        task_prompt = prompt_set['task'].format(
            career_profile_json=json.dumps(profile.get('profile_data', {}), indent=2),
            conversation_history=conversation_history if conversation_history else "First conversation",
            user_message=request.message,
            goals_json=json.dumps(goals, indent=2)
        )

        # 7. Call Gemini
        response = await gemini_analyzer.analyze_with_prompts(
            system_prompt=prompt_set['system'],
            developer_prompt=prompt_set['developer'],
            task_prompt=task_prompt
        )

        result = response.get('parsed_data', {})

        # 8. Save message to conversation
        messages.append({
            'role': 'user',
            'content': request.message,
            'timestamp': datetime.utcnow().isoformat()
        })
        messages.append({
            'role': 'assistant',
            'content': result.get('reply', 'I apologize, but I encountered an issue. Please try again.'),
            'timestamp': datetime.utcnow().isoformat()
        })

        # 9. Update conversation in database
        client = get_supabase_client()
        if client:
            try:
                if request.conversation_id:
                    # Update existing
                    client.table('coach_conversations')\
                        .update({
                            'messages': messages,
                            'updated_at': datetime.utcnow().isoformat()
                        })\
                        .eq('id', conversation_id)\
                        .execute()
                else:
                    # Insert new
                    client.table('coach_conversations')\
                        .insert({
                            'id': conversation_id,
                            'user_id': request.user_id,
                            'conversation_title': f"{request.conversation_type} - {datetime.utcnow().strftime('%Y-%m-%d')}",
                            'conversation_type': request.conversation_type,
                            'messages': messages,
                            'insights': [],
                            'status': 'active'
                        })\
                        .execute()
            except Exception as e:
                logger.error(f"Failed to save conversation: {e}")

        # 10. Save suggestions to database (if any)
        suggestions = result.get('profile_patch_suggestions', [])
        if suggestions and client:
            try:
                for suggestion in suggestions:
                    client.table('profile_suggestions')\
                        .insert({
                            'user_id': request.user_id,
                            'profile_id': profile['id'],
                            'source': 'coach',
                            'suggestion_type': suggestion.get('suggestion_type', 'skill'),
                            'proposed_patch': suggestion.get('proposed_patch', {}),
                            'evidence': suggestion.get('evidence'),
                            'confidence_score': suggestion.get('confidence_score', 0.5),
                            'reasoning': suggestion.get('reasoning', ''),
                            'status': 'pending'
                        })\
                        .execute()
            except Exception as e:
                logger.error(f"Failed to save suggestions: {e}")

        # 11. Return response
        return CoachResponse(
            conversation_id=conversation_id,
            reply=result.get('reply', 'How can I help you with your career development?'),
            profile_patch_suggestions=[ProfilePatchSuggestion(**s) for s in suggestions],
            goal_updates=result.get('goal_updates', []),
            next_actions=result.get('next_actions', [])
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Coach chat error: {e}", exc_info=True)
        raise HTTPException(500, f"Coach service error: {str(e)}")


@router.post("/goals", response_model=GoalResponse)
async def create_goal(request: CreateGoalRequest):
    """Create a new career goal"""
    try:
        client = get_supabase_client()
        if not client:
            raise HTTPException(503, "Database unavailable")

        goal_id = str(uuid.uuid4())

        response = client.table('career_goals')\
            .insert({
                'id': goal_id,
                'user_id': request.user_id,
                'goal_title': request.goal.goal_title,
                'goal_type': request.goal.goal_type,
                'description': request.goal.description,
                'specific': request.goal.specific,
                'measurable': request.goal.measurable,
                'achievable': request.goal.achievable,
                'relevant': request.goal.relevant,
                'time_bound': request.goal.time_bound,
                'status': request.goal.status,
                'progress_percentage': request.goal.progress_percentage,
                'milestones': [m.model_dump() for m in request.goal.milestones]
            })\
            .execute()

        if response.data:
            return GoalResponse(
                id=goal_id,
                user_id=request.user_id,
                goal_data=request.goal,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

        raise HTTPException(500, "Failed to create goal")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Goal creation error: {e}", exc_info=True)
        raise HTTPException(500, f"Failed to create goal: {str(e)}")


@router.get("/goals/{user_id}", response_model=GoalsListResponse)
async def get_goals(user_id: str):
    """Get all career goals for a user"""
    try:
        goals = await get_user_goals(user_id)

        active_count = len([g for g in goals if g.get('status') == 'active'])
        completed_count = len([g for g in goals if g.get('status') == 'completed'])

        return GoalsListResponse(
            goals=[
                GoalResponse(
                    id=g['id'],
                    user_id=g['user_id'],
                    goal_data=g,  # Simplified, should map properly
                    created_at=g.get('created_at', datetime.utcnow()),
                    updated_at=g.get('updated_at', datetime.utcnow()),
                    completed_at=g.get('completed_at')
                )
                for g in goals
            ],
            active_count=active_count,
            completed_count=completed_count
        )

    except Exception as e:
        logger.error(f"Get goals error: {e}", exc_info=True)
        raise HTTPException(500, f"Failed to get goals: {str(e)}")


@router.patch("/goals/{goal_id}", response_model=GoalResponse)
async def update_goal(goal_id: str, request: UpdateGoalRequest):
    """Update a career goal"""
    try:
        client = get_supabase_client()
        if not client:
            raise HTTPException(503, "Database unavailable")

        # Verify ownership
        existing = client.table('career_goals')\
            .select('*')\
            .eq('id', goal_id)\
            .eq('user_id', request.user_id)\
            .single()\
            .execute()

        if not existing.data:
            raise HTTPException(404, "Goal not found")

        # Update
        update_data = request.updates.copy()
        update_data['updated_at'] = datetime.utcnow().isoformat()

        if update_data.get('status') == 'completed' and not existing.data.get('completed_at'):
            update_data['completed_at'] = datetime.utcnow().isoformat()

        response = client.table('career_goals')\
            .update(update_data)\
            .eq('id', goal_id)\
            .execute()

        if response.data:
            return GoalResponse(
                id=goal_id,
                user_id=request.user_id,
                goal_data=response.data[0],
                created_at=existing.data['created_at'],
                updated_at=datetime.utcnow(),
                completed_at=response.data[0].get('completed_at')
            )

        raise HTTPException(500, "Failed to update goal")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Goal update error: {e}", exc_info=True)
        raise HTTPException(500, f"Failed to update goal: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check for Career Coach service"""
    return {
        "status": "operational",
        "service": "Career Coach",
        "access_mode": "read-only (career_profile)",
        "features": ["coaching", "goals", "suggestions"],
        "timestamp": datetime.utcnow().isoformat()
    }
