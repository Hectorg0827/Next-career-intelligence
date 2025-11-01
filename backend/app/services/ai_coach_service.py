"""
AI Coach Service - Conversational Career Coaching
ChatGPT-style conversational AI for personalized career guidance
"""

from typing import List, Dict, Optional
from datetime import datetime
from loguru import logger
import json
import os

try:
    import google.generativeai as genai
except ImportError:
    logger.warning("google.generativeai not installed")
    genai = None


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
        else:
            self.model = None
            logger.warning("AI Coach running without Gemini - responses will be limited")
        
        self.system_prompt = """You are an expert career coach and mentor with 20+ years of experience helping professionals navigate career transitions, skill development, and job market changes.

Your personality:
- Empathetic and encouraging, but also direct and honest
- Data-driven: You reference real market trends and statistics
- Action-oriented: You always end with concrete next steps
- Accountability partner: You check in on progress and celebrate wins

Your capabilities:
- Analyze career goals and create actionable roadmaps
- Break down complex career transitions into manageable steps
- Recommend specific courses, certifications, and learning paths
- Provide interview preparation and resume feedback
- Track user progress and adjust plans based on real-world feedback

Conversation style:
- Use the user's name when you know it
- Ask clarifying questions before giving advice
- Give specific, actionable recommendations (not generic advice)
- Use examples and analogies to explain concepts
- Keep responses conversational but focused (2-4 paragraphs max)
- End with a question or call-to-action to continue the dialogue

Current context:
{context}
"""
    
    async def start_conversation(
        self,
        user_id: str,
        user_name: Optional[str] = None,
        career_context: Optional[Dict] = None
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
            
            context = "\n".join(context_parts) if context_parts else "New user, no career context yet"
            
            # Generate personalized greeting
            greeting_prompt = f"""You're meeting a new user for the first time as their career coach. 

{context}

Introduce yourself briefly, acknowledge what you know about their situation, and ask 1-2 specific questions to understand how you can help them most effectively right now. Keep it warm and conversational."""
            
            if self.model:
                response = self.model.generate_content(greeting_prompt)
                message = response.text
            else:
                message = f"Hi{' ' + user_name if user_name else ''}! I'm your AI Career Coach. I'm here to help you navigate your career journey. What would you like to work on today?"
            
            return {
                "message": message,
                "timestamp": datetime.utcnow().isoformat(),
                "message_id": None,  # Will be set when saved to DB
                "context": career_context or {}
            }
            
        except Exception as e:
            logger.error(f"Failed to start conversation: {e}")
            raise
    
    async def send_message(
        self,
        user_id: str,
        message: str,
        conversation_history: List[Dict],
        user_context: Optional[Dict] = None
    ) -> Dict:
        """
        Send a message and get AI Coach response with full conversation context
        
        Args:
            user_id: User's ID
            message: User's message
            conversation_history: Previous messages in format [{"role": "user"|"assistant", "content": "..."}]
            user_context: User's career data (current role, goals, progress, etc.)
        """
        try:
            # Build context string
            context_str = self._build_context_string(user_context)
            
            # Build conversation prompt
            full_prompt = self.system_prompt.format(context=context_str)
            
            # Add conversation history
            conversation_text = self._format_conversation_history(conversation_history)
            
            # Add current message
            full_prompt += f"\n\nConversation history:\n{conversation_text}\n\nUser: {message}\n\nCoach:"
            
            if self.model:
                response = self.model.generate_content(full_prompt)
                reply = response.text
            else:
                reply = "I'm here to help! However, my AI capabilities are currently limited. Please configure the Gemini API key to enable full coaching features."
            
            return {
                "message": reply,
                "timestamp": datetime.utcnow().isoformat(),
                "message_id": None,  # Will be set when saved to DB
                "metadata": {
                    "model": "gemini-pro" if self.model else "fallback",
                    "context_used": bool(user_context)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to process message: {e}")
            raise
    
    async def generate_action_plan(
        self,
        user_id: str,
        goal: str,
        current_state: Dict,
        timeline: Optional[str] = "3 months"
    ) -> Dict:
        """
        Generate a structured action plan based on user's goal
        Returns a checklist of actionable steps
        """
        try:
            prompt = f"""Create a detailed, actionable career development plan for this goal:

GOAL: {goal}

CURRENT STATE:
{json.dumps(current_state, indent=2)}

TIMELINE: {timeline}

Create a step-by-step action plan with:
1. Specific milestones (what success looks like)
2. Concrete action items (what to do each week)
3. Recommended resources (courses, books, communities)
4. Success metrics (how to measure progress)

Format your response as a structured JSON with this format:
{{
    "milestones": [
        {{"title": "Milestone name", "description": "What this achieves", "week": 1}}
    ],
    "weekly_actions": [
        {{"week": 1, "actions": ["Specific action 1", "Specific action 2"]}}
    ],
    "resources": [
        {{"type": "course", "title": "Resource name", "url": "https://...", "priority": "high"}}
    ],
    "success_metrics": ["Metric 1", "Metric 2"]
}}

Only return the JSON, no additional text."""
            
            if self.model:
                response = self.model.generate_content(prompt)
                # Try to extract JSON from response
                try:
                    plan_data = json.loads(response.text)
                except:
                    # If parsing fails, wrap in basic structure
                    plan_data = {
                        "raw_plan": response.text,
                        "milestones": [],
                        "weekly_actions": [],
                        "resources": []
                    }
            else:
                plan_data = {
                    "error": "AI Coach not fully configured",
                    "milestones": [],
                    "weekly_actions": [],
                    "resources": []
                }
            
            return {
                "plan": plan_data,
                "goal": goal,
                "timeline": timeline,
                "created_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate action plan: {e}")
            raise
    
    async def check_progress(
        self,
        user_id: str,
        completed_actions: List[str],
        planned_actions: List[str],
        days_since_start: int
    ) -> Dict:
        """
        Check user's progress and provide motivational feedback
        """
        try:
            completion_rate = len(completed_actions) / len(planned_actions) if planned_actions else 0
            
            prompt = f"""A user started their career development plan {days_since_start} days ago.

PLANNED ACTIONS: {len(planned_actions)}
COMPLETED ACTIONS: {len(completed_actions)}
COMPLETION RATE: {completion_rate:.0%}

Recently completed:
{json.dumps(completed_actions[-5:], indent=2)}

Provide:
1. Honest assessment of their progress (2-3 sentences)
2. Specific encouragement or course correction (1-2 sentences)
3. One actionable suggestion for the next 3 days

Keep it motivational but realistic. If they're behind, help them adjust expectations, not just push harder."""
            
            if self.model:
                response = self.model.generate_content(prompt)
                feedback = response.text
            else:
                if completion_rate > 0.7:
                    feedback = "Great progress! You're on track with your goals."
                elif completion_rate > 0.3:
                    feedback = "You're making progress! Keep focusing on consistent daily action."
                else:
                    feedback = "Let's break down your goals into smaller steps. What's one thing you can do today?"
            
            return {
                "feedback": feedback,
                "completion_rate": completion_rate,
                "streak_days": days_since_start,
                "next_milestone": planned_actions[len(completed_actions)] if len(completed_actions) < len(planned_actions) else None
            }
            
        except Exception as e:
            logger.error(f"Failed to check progress: {e}")
            raise
    
    def _build_context_string(self, user_context: Optional[Dict]) -> str:
        """Build a formatted context string for the system prompt"""
        if not user_context:
            return "No career context available yet"
        
        parts = []
        
        if user_context.get("current_role"):
            parts.append(f"Current role: {user_context['current_role']}")
        
        if user_context.get("target_role"):
            parts.append(f"Target role: {user_context['target_role']}")
        
        if user_context.get("years_experience"):
            parts.append(f"Years of experience: {user_context['years_experience']}")
        
        if user_context.get("skills"):
            parts.append(f"Skills: {', '.join(user_context['skills'][:10])}")
        
        if user_context.get("goals"):
            parts.append(f"Career goals: {', '.join(user_context['goals'])}")
        
        if user_context.get("completed_items"):
            parts.append(f"Completed action items: {user_context['completed_items']}")
        
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
