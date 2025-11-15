"""
Memory Manager - Unified Interface for AI Memory Systems

Combines long-term and working memory to provide complete context
for AI agents and autonomous systems.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from .long_term_memory import LongTermMemory, UserMemoryProfile
from .working_memory import WorkingMemory, ConversationContext

logger = logging.getLogger(__name__)


class MemoryManager:
    """
    Unified memory management for AI agents.
    
    Provides single interface to access both long-term knowledge
    and short-term working memory context.
    """
    
    def __init__(self):
        self.long_term = LongTermMemory()
        self.working = WorkingMemory()
        logger.info("Memory manager initialized")
    
    # ==================== Unified Context ====================
    
    async def get_complete_context(
        self,
        user_id: str,
        conversation_id: Optional[str] = None,
        include_long_term: bool = True,
        include_working: bool = True
    ) -> Dict[str, Any]:
        """
        Get complete memory context for AI agents.
        
        Combines long-term knowledge with current working memory
        to provide full context for decision making.
        
        Args:
            user_id: User ID
            conversation_id: Optional conversation ID for working memory
            include_long_term: Include persistent memory profile
            include_working: Include working memory context
            
        Returns:
            Complete context dictionary with all relevant memory
        """
        
        context = {
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "long_term_memory": None,
            "working_memory": None
        }
        
        # Get long-term memory
        if include_long_term:
            try:
                memory_profile = await self.long_term.get_user_memory(user_id)
                context["long_term_memory"] = {
                    "career_preferences": memory_profile.career_preferences.model_dump(),
                    "skill_profile": memory_profile.skill_profile.model_dump(),
                    "behavior_patterns": memory_profile.behavior_patterns.model_dump(),
                    "career_goals": memory_profile.career_goals,
                    "pain_points": memory_profile.pain_points,
                    "confidence_score": memory_profile.confidence_score,
                    "last_updated": memory_profile.last_updated.isoformat()
                }
            except Exception as e:
                logger.error(f"Error getting long-term memory: {e}")
                context["long_term_memory"] = {"error": str(e)}
        
        # Get working memory
        if include_working:
            try:
                working_context = self.working.build_context_summary(
                    user_id,
                    conversation_id
                )
                context["working_memory"] = working_context
            except Exception as e:
                logger.error(f"Error getting working memory: {e}")
                context["working_memory"] = {"error": str(e)}
        
        return context
    
    async def get_ai_prompt_context(
        self,
        user_id: str,
        conversation_id: Optional[str] = None,
        purpose: str = "general"
    ) -> str:
        """
        Get formatted context string for AI prompts.
        
        Converts memory into natural language for LLM consumption.
        
        Args:
            user_id: User ID
            conversation_id: Optional conversation ID
            purpose: Purpose of context (job_search, career_advice, etc.)
            
        Returns:
            Formatted context string for AI prompts
        """
        
        context = await self.get_complete_context(user_id, conversation_id)
        
        # Build natural language context
        parts = []
        
        # Long-term memory
        if context["long_term_memory"]:
            ltm = context["long_term_memory"]
            
            parts.append("## User Profile\n")
            
            # Career preferences
            prefs = ltm["career_preferences"]
            if prefs["preferred_industries"]:
                parts.append(f"Interested in: {', '.join(prefs['preferred_industries'][:3])}")
            if prefs["preferred_roles"]:
                parts.append(f"Looking for roles: {', '.join(prefs['preferred_roles'][:3])}")
            if prefs["work_arrangement"]:
                parts.append(f"Prefers: {prefs['work_arrangement']} work")
            
            # Skills
            skills = ltm["skill_profile"]
            if skills["technical_skills"]:
                parts.append(f"\nTechnical skills: {', '.join(skills['technical_skills'][:5])}")
            if skills["skill_gaps"]:
                parts.append(f"Learning: {', '.join(skills['skill_gaps'][:3])}")
            
            # Behavior
            behavior = ltm["behavior_patterns"]
            parts.append(f"\nEngagement level: {behavior['engagement_level']}")
            parts.append(f"Job search intensity: {behavior['job_search_intensity']}")
            
            # Goals
            if ltm["career_goals"]:
                parts.append(f"\nCareer goals:")
                for goal in ltm["career_goals"]:
                    parts.append(f"- {goal}")
            
            # Pain points
            if ltm["pain_points"]:
                parts.append(f"\nChallenges:")
                for pain in ltm["pain_points"]:
                    parts.append(f"- {pain}")
        
        # Working memory
        if context["working_memory"]:
            wm = context["working_memory"]
            
            parts.append("\n## Current Context\n")
            
            # Recent actions
            recent = wm.get("active_context", {})
            if recent.get("recently_viewed_jobs"):
                parts.append("Recently viewed:")
                for job in recent["recently_viewed_jobs"][:3]:
                    parts.append(f"- {job['title']} at {job.get('company', 'Unknown')}")
            
            if recent.get("recent_searches"):
                searches = [s["query"] for s in recent["recent_searches"] if s.get("query")]
                if searches:
                    parts.append(f"\nRecent searches: {', '.join(searches)}")
            
            # Conversation context
            if wm.get("conversation"):
                conv = wm["conversation"]
                if conv.get("intent"):
                    parts.append(f"\nCurrent intent: {conv['intent']}")
                if conv.get("topic"):
                    parts.append(f"Topic: {conv['topic']}")
        
        return "\n".join(parts)
    
    # ==================== Convenience Methods ====================
    
    async def record_user_action(
        self,
        user_id: str,
        action_type: str,
        action_data: Dict[str, Any]
    ):
        """Record a user action in working memory"""
        self.working.record_action(user_id, action_type, action_data)
    
    async def start_conversation(
        self,
        conversation_id: str,
        user_id: str,
        topic: Optional[str] = None
    ) -> ConversationContext:
        """Start a new conversation"""
        return self.working.start_conversation(conversation_id, user_id, topic)
    
    async def add_conversation_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict] = None
    ) -> bool:
        """Add message to conversation"""
        return self.working.add_message(conversation_id, role, content, metadata)
    
    async def get_user_memory_profile(self, user_id: str) -> UserMemoryProfile:
        """Get long-term memory profile"""
        return await self.long_term.get_user_memory(user_id)
    
    async def refresh_user_memory(self, user_id: str) -> UserMemoryProfile:
        """Force refresh of long-term memory from events"""
        return await self.long_term.get_user_memory(user_id, force_refresh=True)
    
    async def add_memory_insight(
        self,
        user_id: str,
        insight_type: str,
        insight_data: Dict[str, Any]
    ) -> bool:
        """Add insight to long-term memory"""
        return await self.long_term.update_memory_insight(
            user_id,
            insight_type,
            insight_data
        )
    
    # ==================== Maintenance ====================
    
    def cleanup_stale_data(self):
        """Clean up stale working memory contexts"""
        self.working.cleanup_stale_contexts()
        logger.info("Cleaned up stale memory contexts")
    
    def clear_working_memory(self):
        """Clear all working memory (useful for testing)"""
        self.working.conversations.clear()
        self.working.recent_actions.clear()
        logger.info("Cleared working memory")
    
    def clear_long_term_cache(self):
        """Clear long-term memory cache"""
        self.long_term.clear_cache()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory system statistics"""
        return {
            "long_term": {
                "cached_profiles": len(self.long_term.cache),
                "cache_ttl_minutes": int(self.long_term.cache_ttl.total_seconds() / 60)
            },
            "working": self.working.get_stats()
        }
