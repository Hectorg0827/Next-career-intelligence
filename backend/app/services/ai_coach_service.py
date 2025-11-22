"""
AI Coach Service - Conversational Career Coaching
ChatGPT-style conversational AI for personalized career guidance
"""

from typing import List, Dict, Optional
from datetime import datetime
from loguru import logger
import json
import os
import asyncio

try:
    import google.generativeai as genai
except ImportError:
    logger.warning("google.generativeai not installed")
    genai = None

from app.services.prompts import (
    CAREER_COACH_SYSTEM, 
    TOPIC_CLASSIFIER_PROMPT, 
    MEMORY_SUMMARIZER_PROMPT
)
from app.services.skill_service import skill_service

# We need database access for memory and skills
# Since this service is often called from API, we'll assume the caller handles DB session
# But for async sidecars, we might need a fresh session. 
# For this implementation, we'll keep it simple and assume the API layer passes necessary data or we use a helper.

class AICoachService:
    """
    AI Coach - Your Personal Career Development Assistant
    Provides contextual, ongoing career coaching through natural conversation
    """

    def __init__(self):
        if genai:
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
            self.model = genai.GenerativeModel(model_name)
            # Separate model for fast tasks to avoid context pollution
            self.fast_model = genai.GenerativeModel("gemini-1.5-flash") 
        else:
            self.model = None
            self.fast_model = None
            logger.warning("AI Coach running without Gemini - responses will be limited")

    async def is_career_related(self, message: str) -> bool:
        """Check if the user message is within scope."""
        if not self.fast_model:
            return True # Fail open if no model

        try:
            prompt = f"""{TOPIC_CLASSIFIER_PROMPT}
            
            User message: "{message}"
            """
            response = self.fast_model.generate_content(prompt)
            label = response.text.strip().upper()
            return "IN_SCOPE" in label
        except Exception as e:
            logger.error(f"Topic classification failed: {e}")
            return True # Fail open

    async def start_conversation(
        self, user_id: str, user_name: Optional[str] = None, career_context: Optional[Dict] = None
    ) -> Dict:
        """
        Start a new coaching conversation with personalized greeting
        """
        try:
            # Build user context
            context_parts = []

            if user_name:
                context_parts.append(f"User's name: {user_name}")

            if career_context:
                if career_context.get("current_role"):
                    context_parts.append(f"Current role: {career_context['current_role']}")
                if career_context.get("target_role"):
                    context_parts.append(f"Target role: {career_context['target_role']}")
                if career_context.get("skills"):
                    context_parts.append(f"Current skills: {', '.join(career_context['skills'][:5])}")
                if career_context.get("goals"):
                    context_parts.append(f"Goals: {', '.join(career_context['goals'][:3])}")
                if career_context.get("memory_summary"):
                    context_parts.append(f"MEMORY_SUMMARY: {career_context['memory_summary']}")

            context = "\n".join(context_parts) if context_parts else "New user, no career context yet"

            # Generate personalized greeting
            greeting_prompt = f"""You're meeting a user for a coaching session.
            
            CONTEXT:
            {context}
            
            Introduce yourself briefly. If there is a MEMORY_SUMMARY, reference a past topic to show continuity.
            Ask 1 specific question to get started. Keep it warm and conversational."""

            if self.model:
                response = self.model.generate_content(greeting_prompt)
                message = response.text
            else:
                message = f"Hi{' ' + user_name if user_name else ''}! I'm your AI Career Coach. I'm here to help you navigate your career journey. What would you like to work on today?"

            return {
                "message": message,
                "timestamp": datetime.utcnow().isoformat(),
                "message_id": None,
                "context": career_context or {},
            }

        except Exception as e:
            logger.error(f"Failed to start conversation: {e}")
            raise

    async def send_message(
        self, user_id: str, message: str, conversation_history: List[Dict], user_context: Optional[Dict] = None, db_session = None
    ) -> Dict:
        """
        Send a message and get AI Coach response with full conversation context
        """
        try:
            # 1. Guardrail: Topic Filter
            if not await self.is_career_related(message):
                return {
                    "message": "I'm focused only on your career, skills, and job security. For general questions, please use a general AI assistant. Let's bring this back to your professional goals.",
                    "timestamp": datetime.utcnow().isoformat(),
                    "metadata": {"blocked": True}
                }

            # 2. Sidecar: Skill Extraction (Fire and forget)
            # In a real async app, we'd use background tasks. Here we just await it or run it.
            # We'll await it for simplicity in this prototype, but catch errors so it doesn't block chat.
            if db_session:
                try:
                    skills_found = await skill_service.extract_skills_from_text(message)
                    if skills_found:
                        await skill_service.upsert_user_skills(db_session, user_id, skills_found, "conversation")
                except Exception as e:
                    logger.error(f"Sidecar skill extraction failed: {e}")

            # 3. Build Context
            context_str = self._build_context_string(user_context)

            # 4. Build Prompt
            # We want structured output for goals/actions, but conversational for the reply.
            # Gemini supports response_schema, but mixed mode is tricky.
            # We'll ask for JSON to ensure we capture the data, then parse the 'reply' field for the user.
            
            full_prompt = f"""{CAREER_COACH_SYSTEM}

            CONTEXT:
            {context_str}

            CONVERSATION HISTORY:
            {self._format_conversation_history(conversation_history)}

            USER MESSAGE:
            {message}

            Return your response in JSON format as specified in the system prompt.
            """

            if self.model:
                # Force JSON mode
                response = self.model.generate_content(
                    full_prompt, 
                    generation_config={"response_mime_type": "application/json"}
                )
                try:
                    response_data = json.loads(response.text)
                    reply = response_data.get("reply", "I'm having trouble formulating a response right now.")
                    suggestions = response_data.get("profile_patch_suggestions", [])
                    goal_updates = response_data.get("goal_updates", [])
                    next_actions = response_data.get("next_actions", [])
                except json.JSONDecodeError:
                    # Fallback if model refuses JSON
                    reply = response.text
                    suggestions = []
                    goal_updates = []
                    next_actions = []
            else:
                reply = "I'm here to help! However, my AI capabilities are currently limited. Please configure the Gemini API key."
                suggestions = []
                goal_updates = []
                next_actions = []

            # 5. Update Memory (Async/Background ideally)
            # For now, we'll just return the data and let the caller handle persistence if needed
            
            return {
                "message": reply,
                "suggestions": suggestions,
                "goal_updates": goal_updates,
                "next_actions": next_actions,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": {"model": "gemini-1.5-flash", "context_used": bool(user_context)},
            }

        except Exception as e:
            logger.error(f"Failed to process message: {e}")
            raise

    async def update_long_term_memory(self, user_id: str, old_summary: str, recent_turns: List[Dict]) -> str:
        """
        Condense conversation into long-term memory.
        """
        if not self.fast_model:
            return old_summary

        try:
            turns_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent_turns])
            
            prompt = MEMORY_SUMMARIZER_PROMPT.format(
                old_summary=old_summary or "None",
                recent_turns=turns_text
            )
            
            response = self.fast_model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Memory update failed: {e}")
            return old_summary

    def _build_context_string(self, user_context: Optional[Dict]) -> str:
        """Build a formatted context string for the system prompt"""
        if not user_context:
            return "No career context available yet"

        parts = []
        
        # Profile
        if user_context.get("current_role"):
            parts.append(f"USER_PROFILE: Role={user_context['current_role']}")
        if user_context.get("skills"):
            parts.append(f"USER_PROFILE: Skills={', '.join(user_context['skills'][:10])}")
            
        # Goals
        if user_context.get("goals"):
            parts.append(f"GOALS: {', '.join(user_context['goals'])}")
            
        # Memory
        if user_context.get("memory_summary"):
            parts.append(f"MEMORY_SUMMARY: {user_context['memory_summary']}")

        return "\n".join(parts)

    def _format_conversation_history(self, history: List[Dict]) -> str:
        """Format conversation history for the prompt"""
        formatted = []
        for msg in history[-10:]:  # Only use last 10 messages for context
            role = "User" if msg["role"] == "user" else "Coach"
            formatted.append(f"{role}: {msg['content']}")

        return "\n".join(formatted)


# Singleton instance
coach_service = AICoachService()
