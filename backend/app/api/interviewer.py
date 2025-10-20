"""
Interviewer AI API - Premium Feature
Conducts STAR interviews and generates evidence-based suggestions
"""

from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict, Any
from datetime import datetime
from loguru import logger
import json
import uuid

from app.db.supabase import get_supabase_client
from app.services.gemini_analyzer import gemini_analyzer
from app.services.prompts import get_prompt_set
from app.models.premium_schemas import (
    StartInterviewRequest,
    SubmitAnswerRequest,
    CompleteInterviewRequest,
    InterviewSessionResponse,
    InterviewQuestion,
    EvidenceSummary,
    ProfilePatchSuggestion
)

router = APIRouter(prefix="/interviewer", tags=["Interviewer AI - Premium"])


# ========================================
# HELPER FUNCTIONS
# ========================================

async def get_career_profile(user_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve career profile from Supabase (read-only)"""
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


async def get_interview_session(session_id: str, user_id: str) -> Optional[Dict[str, Any]]:
    """Get existing interview session"""
    try:
        client = get_supabase_client()
        if not client:
            return None

        response = client.table('interview_sessions')\
            .select('*')\
            .eq('id', session_id)\
            .eq('user_id', user_id)\
            .single()\
            .execute()

        return response.data if response.data else None
    except Exception as e:
        logger.error(f"Failed to get interview session: {e}")
        return None


# ========================================
# ENDPOINTS
# ========================================

@router.post("/start", response_model=InterviewSessionResponse)
async def start_interview(request: StartInterviewRequest):
    """
    Start a new interview session
    Generates 5-7 behavioral interview questions tailored to the role and user's background
    """
    try:
        # 1. Get career profile (read-only)
        profile = await get_career_profile(request.user_id)
        if not profile:
            raise HTTPException(404, "Career profile not found. Please create a profile first in Resume Studio.")

        # 2. Get prompts
        prompt_set = get_prompt_set('interviewer', 'start')

        # 3. Build task prompt
        jd_json = request.job_description.model_dump() if request.job_description else {}

        task_prompt = prompt_set['task'].format(
            role_title=request.role_title,
            company_name=request.company_name or "the company",
            job_description_json=json.dumps(jd_json, indent=2) if jd_json else "{}",
            career_profile_json=json.dumps(profile.get('profile_data', {}), indent=2),
            interview_type=request.interview_type
        )

        # 4. Call Gemini to generate questions
        response = await gemini_analyzer.analyze_with_prompts(
            system_prompt=prompt_set['system'],
            developer_prompt=prompt_set['developer'],
            task_prompt=task_prompt
        )

        result = response.get('parsed_data', {})
        questions_data = result.get('questions', [])

        # Convert to InterviewQuestion objects
        questions = [
            InterviewQuestion(
                question=q.get('question', ''),
                user_response=None
            )
            for q in questions_data
        ]

        # 5. Create interview session in database
        session_id = str(uuid.uuid4())
        client = get_supabase_client()

        if client:
            try:
                client.table('interview_sessions')\
                    .insert({
                        'id': session_id,
                        'user_id': request.user_id,
                        'profile_id': profile['id'],
                        'role_title': request.role_title,
                        'company_name': request.company_name,
                        'job_description': jd_json,
                        'interview_type': request.interview_type,
                        'questions': [q.model_dump() for q in questions],
                        'evidence_summaries': [],
                        'generated_suggestions': [],
                        'status': 'in_progress'
                    })\
                    .execute()
            except Exception as e:
                logger.error(f"Failed to save interview session: {e}")

        # 6. Return session
        return InterviewSessionResponse(
            session_id=session_id,
            role_title=request.role_title,
            company_name=request.company_name,
            interview_type=request.interview_type,
            questions=questions,
            evidence_summaries=[],
            generated_suggestions=[],
            status='in_progress',
            created_at=datetime.utcnow()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Start interview error: {e}", exc_info=True)
        raise HTTPException(500, f"Failed to start interview: {str(e)}")


@router.post("/answer")
async def submit_answer(request: SubmitAnswerRequest):
    """
    Submit an answer to an interview question
    Extracts STAR evidence and may ask follow-up questions
    """
    try:
        # 1. Get interview session
        session = await get_interview_session(request.session_id, request.user_id)
        if not session:
            raise HTTPException(404, "Interview session not found")

        if session['status'] != 'in_progress':
            raise HTTPException(400, "Interview session is not active")

        # 2. Get the question
        questions = session.get('questions', [])
        if request.question_index >= len(questions):
            raise HTTPException(400, "Invalid question index")

        question = questions[request.question_index]

        # 3. Get prompts
        prompt_set = get_prompt_set('interviewer', 'extract')

        # 4. Build task prompt
        task_prompt = prompt_set['task'].format(
            question=question['question'],
            user_answer=request.answer
        )

        # 5. Call Gemini to extract evidence
        response = await gemini_analyzer.analyze_with_prompts(
            system_prompt=prompt_set['system'],
            developer_prompt=prompt_set['developer'],
            task_prompt=task_prompt
        )

        result = response.get('parsed_data', {})

        # 6. Update question with STAR breakdown
        questions[request.question_index].update({
            'user_response': request.answer,
            'situation': result.get('situation'),
            'task': result.get('task'),
            'action': result.get('action'),
            'result': result.get('result'),
            'timestamp': datetime.utcnow().isoformat()
        })

        # 7. Add evidence summary if extracted
        evidence_summaries = session.get('evidence_summaries', [])
        if result.get('evidence_summary'):
            evidence = result['evidence_summary']
            evidence['source_question_index'] = request.question_index
            evidence_summaries.append(evidence)

        # 8. Update session in database
        client = get_supabase_client()
        if client:
            try:
                client.table('interview_sessions')\
                    .update({
                        'questions': questions,
                        'evidence_summaries': evidence_summaries
                    })\
                    .eq('id', request.session_id)\
                    .execute()
            except Exception as e:
                logger.error(f"Failed to update interview session: {e}")

        # 9. Return result with optional follow-up
        return {
            "success": True,
            "evidence_extracted": result.get('evidence_summary') is not None,
            "follow_up_question": result.get('follow_up_question'),
            "star_breakdown": {
                "situation": result.get('situation'),
                "task": result.get('task'),
                "action": result.get('action'),
                "result": result.get('result')
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Submit answer error: {e}", exc_info=True)
        raise HTTPException(500, f"Failed to process answer: {str(e)}")


@router.post("/complete", response_model=InterviewSessionResponse)
async def complete_interview(request: CompleteInterviewRequest):
    """
    Complete interview session and generate resume bullet suggestions
    """
    try:
        # 1. Get interview session
        session = await get_interview_session(request.session_id, request.user_id)
        if not session:
            raise HTTPException(404, "Interview session not found")

        # 2. Get career profile
        profile = await get_career_profile(request.user_id)

        # 3. Get prompts
        prompt_set = get_prompt_set('interviewer', 'suggestions')

        # 4. Build task prompt
        task_prompt = prompt_set['task'].format(
            evidence_summaries_json=json.dumps(session.get('evidence_summaries', []), indent=2),
            career_profile_json=json.dumps(profile.get('profile_data', {}) if profile else {}, indent=2),
            job_description_json=json.dumps(session.get('job_description', {}), indent=2)
        )

        # 5. Call Gemini to generate suggestions
        response = await gemini_analyzer.analyze_with_prompts(
            system_prompt=prompt_set['system'],
            developer_prompt=prompt_set['developer'],
            task_prompt=task_prompt
        )

        result = response.get('parsed_data', {})
        suggestions = result.get('profile_patch_suggestions', [])

        # 6. Update session status and save suggestions
        client = get_supabase_client()
        if client:
            try:
                # Update interview session
                client.table('interview_sessions')\
                    .update({
                        'generated_suggestions': suggestions,
                        'status': 'completed',
                        'completed_at': datetime.utcnow().isoformat()
                    })\
                    .eq('id', request.session_id)\
                    .execute()

                # Save suggestions to profile_suggestions table
                if profile:
                    for suggestion in suggestions:
                        client.table('profile_suggestions')\
                            .insert({
                                'user_id': request.user_id,
                                'profile_id': profile['id'],
                                'source': 'interviewer',
                                'suggestion_type': suggestion.get('suggestion_type', 'bullet'),
                                'proposed_patch': suggestion.get('proposed_patch', {}),
                                'evidence': suggestion.get('evidence'),
                                'confidence_score': suggestion.get('confidence_score', 0.5),
                                'reasoning': suggestion.get('reasoning', ''),
                                'status': 'pending'
                            })\
                            .execute()
            except Exception as e:
                logger.error(f"Failed to save interview completion: {e}")

        # 7. Return completed session
        questions = [InterviewQuestion(**q) for q in session.get('questions', [])]
        evidence_summaries = [EvidenceSummary(**e) for e in session.get('evidence_summaries', [])]
        generated_suggestions = [ProfilePatchSuggestion(**s) for s in suggestions]

        return InterviewSessionResponse(
            session_id=request.session_id,
            role_title=session['role_title'],
            company_name=session.get('company_name'),
            interview_type=session['interview_type'],
            questions=questions,
            evidence_summaries=evidence_summaries,
            generated_suggestions=generated_suggestions,
            status='completed',
            created_at=session['created_at'],
            completed_at=datetime.utcnow()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Complete interview error: {e}", exc_info=True)
        raise HTTPException(500, f"Failed to complete interview: {str(e)}")


@router.get("/sessions/{user_id}")
async def get_user_sessions(user_id: str):
    """Get all interview sessions for a user"""
    try:
        client = get_supabase_client()
        if not client:
            raise HTTPException(503, "Database unavailable")

        response = client.table('interview_sessions')\
            .select('*')\
            .eq('user_id', user_id)\
            .order('created_at', desc=True)\
            .execute()

        sessions = response.data if response.data else []

        return {
            "sessions": sessions,
            "total_count": len(sessions),
            "in_progress_count": len([s for s in sessions if s.get('status') == 'in_progress']),
            "completed_count": len([s for s in sessions if s.get('status') == 'completed'])
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get sessions error: {e}", exc_info=True)
        raise HTTPException(500, f"Failed to get sessions: {str(e)}")


@router.get("/session/{session_id}", response_model=InterviewSessionResponse)
async def get_session(session_id: str, user_id: str):
    """Get specific interview session details"""
    try:
        session = await get_interview_session(session_id, user_id)
        if not session:
            raise HTTPException(404, "Interview session not found")

        questions = [InterviewQuestion(**q) for q in session.get('questions', [])]
        evidence_summaries = [EvidenceSummary(**e) for e in session.get('evidence_summaries', [])]
        generated_suggestions = [ProfilePatchSuggestion(**s) for s in session.get('generated_suggestions', [])]

        return InterviewSessionResponse(
            session_id=session_id,
            role_title=session['role_title'],
            company_name=session.get('company_name'),
            interview_type=session['interview_type'],
            questions=questions,
            evidence_summaries=evidence_summaries,
            generated_suggestions=generated_suggestions,
            status=session['status'],
            created_at=session['created_at'],
            completed_at=session.get('completed_at')
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get session error: {e}", exc_info=True)
        raise HTTPException(500, f"Failed to get session: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check for Interviewer AI service"""
    return {
        "status": "operational",
        "service": "Interviewer AI",
        "access_mode": "read-only (career_profile)",
        "features": ["behavioral_interview", "technical_interview", "star_extraction", "suggestions"],
        "timestamp": datetime.utcnow().isoformat()
    }
