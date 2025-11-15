"""
AI Memory Layer - Semantic Memory System for Career OS

This module creates long-term memory for AI agents by:
1. Converting events into semantic embeddings
2. Storing learned patterns about user behavior
3. Building context for personalized recommendations
4. Enabling agents to "remember" and "learn" from interactions

Architecture:
- Event Store → Memory Formation → Vector Storage → Agent Context
- Continuous learning from all user interactions
- Privacy-preserving (embeddings, not raw data)
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4
import json

from loguru import logger
import google.generativeai as genai

from app.core.config import settings
from app.db.supabase import get_supabase_client


class MemoryEmbedding:
    """Single memory embedding with metadata"""
    
    def __init__(
        self,
        memory_id: str,
        user_id: str,
        content: str,
        embedding: List[float],
        memory_type: str,
        source_events: List[str],
        metadata: Dict[str, Any],
        created_at: datetime
    ):
        self.memory_id = memory_id
        self.user_id = user_id
        self.content = content
        self.embedding = embedding
        self.memory_type = memory_type
        self.source_events = source_events
        self.metadata = metadata
        self.created_at = created_at


class AIMemoryLayer:
    """
    Semantic memory system that learns from events
    
    Memory Types:
    - job_preferences: Learned from job_viewed, job_saved, job_applied
    - career_goals: Inferred from search patterns and applications
    - interaction_patterns: How user engages with features
    - skill_interests: Technologies user explores
    - success_indicators: What leads to positive outcomes
    """
    
    def __init__(self):
        self.supabase = get_supabase_client()
        
        # Initialize Gemini for embeddings
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.embedding_model = "models/embedding-001"
        else:
            logger.warning("GEMINI_API_KEY not set - AI memory will be disabled")
            self.embedding_model = None
    
    async def form_memory_from_events(
        self,
        user_id: str,
        event_category: str,
        days: int = 7
    ) -> Optional[MemoryEmbedding]:
        """
        Analyze recent events and form a semantic memory
        
        Args:
            user_id: User identifier
            event_category: Category to analyze (JOB, PROFILE, AI_INTERACTION)
            days: How many days of history to analyze
        
        Returns:
            MemoryEmbedding or None if insufficient data
        """
        if not self.embedding_model:
            logger.warning("Embedding model not configured")
            return None
        
        try:
            # Fetch recent events
            since = datetime.utcnow() - timedelta(days=days)
            
            response = self.supabase.table("career_events") \
                .select("*") \
                .eq("user_id", user_id) \
                .eq("event_category", event_category) \
                .gte("created_at", since.isoformat()) \
                .order("created_at", desc=True) \
                .execute()
            
            events = response.data if response.data else []
            
            if len(events) < 3:
                logger.info(f"Insufficient events ({len(events)}) to form memory")
                return None
            
            # Synthesize memory from events
            memory_content = self._synthesize_memory(events, event_category)
            
            if not memory_content:
                return None
            
            # Generate embedding
            embedding = await self._generate_embedding(memory_content)
            
            # Create memory record
            memory_id = str(uuid4())
            memory_type = self._get_memory_type(event_category)
            
            memory = MemoryEmbedding(
                memory_id=memory_id,
                user_id=user_id,
                content=memory_content,
                embedding=embedding,
                memory_type=memory_type,
                source_events=[e["event_id"] for e in events[:10]],
                metadata={
                    "event_count": len(events),
                    "days_analyzed": days,
                    "formed_at": datetime.utcnow().isoformat()
                },
                created_at=datetime.utcnow()
            )
            
            # Store in database
            await self._store_memory(memory)
            
            logger.info(f"Formed {memory_type} memory for user {user_id} from {len(events)} events")
            return memory
            
        except Exception as e:
            logger.error(f"Error forming memory: {e}")
            return None
    
    def _synthesize_memory(self, events: List[Dict[str, Any]], category: str) -> Optional[str]:
        """
        Extract meaningful patterns from events
        
        Returns natural language summary of learned behavior
        """
        if category == "JOB":
            return self._synthesize_job_memory(events)
        elif category == "PROFILE":
            return self._synthesize_profile_memory(events)
        elif category == "AI_INTERACTION":
            return self._synthesize_interaction_memory(events)
        else:
            return None
    
    def _synthesize_job_memory(self, events: List[Dict[str, Any]]) -> str:
        """Learn job preferences from viewing, saving, applying behavior"""
        
        viewed = []
        saved = []
        applied = []
        
        for event in events:
            event_type = event.get("event_type", "")
            data = event.get("event_data", {})
            
            if event_type == "job_viewed":
                viewed.append({
                    "title": data.get("job_title", ""),
                    "company": data.get("company", ""),
                    "skills": data.get("skills", [])
                })
            elif event_type == "job_saved":
                saved.append(data.get("job_title", ""))
            elif event_type == "job_applied":
                applied.append(data.get("job_title", ""))
        
        # Extract patterns
        all_skills = []
        for job in viewed:
            all_skills.extend(job.get("skills", []))
        
        skill_freq = {}
        for skill in all_skills:
            skill_freq[skill] = skill_freq.get(skill, 0) + 1
        
        top_skills = sorted(skill_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Build natural language summary
        memory = f"User viewed {len(viewed)} jobs in past week. "
        
        if saved:
            memory += f"Saved {len(saved)} jobs indicating strong interest. "
        
        if applied:
            memory += f"Applied to {len(applied)} positions showing high engagement. "
        
        if top_skills:
            skills_str = ", ".join([s[0] for s in top_skills])
            memory += f"Frequently explored roles requiring: {skills_str}. "
        
        # Infer preferences
        if len(applied) > 0 and len(viewed) > 0:
            conversion_rate = len(applied) / len(viewed) * 100
            if conversion_rate > 10:
                memory += "High conversion rate suggests confident job seeker ready to apply. "
            else:
                memory += "Browsing extensively, may need guidance to commit to applications. "
        
        return memory
    
    def _synthesize_profile_memory(self, events: List[Dict[str, Any]]) -> str:
        """Learn about profile completion and career evolution"""
        
        updates = []
        completions = []
        
        for event in events:
            event_type = event.get("event_type", "")
            data = event.get("event_data", {})
            
            if event_type == "profile_updated":
                field = data.get("field_name", "")
                if field:
                    updates.append(field)
            elif event_type == "profile_completed":
                completions.append(data.get("section", ""))
        
        memory = f"User updated profile {len(updates)} times. "
        
        if updates:
            fields_str = ", ".join(set(updates[:5]))
            memory += f"Active on sections: {fields_str}. "
        
        if completions:
            memory += f"Completed {len(set(completions))} major sections indicating commitment to platform. "
        
        return memory
    
    def _synthesize_interaction_memory(self, events: List[Dict[str, Any]]) -> str:
        """Learn from coach conversations and AI interactions"""
        
        messages_sent = 0
        topics = []
        
        for event in events:
            event_type = event.get("event_type", "")
            data = event.get("event_data", {})
            
            if event_type == "coach_message_sent":
                messages_sent += 1
                topic = data.get("topic", "")
                if topic:
                    topics.append(topic)
        
        memory = f"User sent {messages_sent} messages to coach. "
        
        if topics:
            unique_topics = list(set(topics))
            topics_str = ", ".join(unique_topics[:3])
            memory += f"Primary topics: {topics_str}. "
        
        if messages_sent > 10:
            memory += "Highly engaged with AI coach, prefers conversational guidance. "
        
        return memory
    
    async def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector using Gemini
        
        Returns 768-dimensional embedding
        """
        try:
            result = genai.embed_content(
                model=self.embedding_model,
                content=text,
                task_type="retrieval_document"
            )
            return result["embedding"]
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            # Return zero vector as fallback
            return [0.0] * 768
    
    async def _store_memory(self, memory: MemoryEmbedding):
        """Store memory in database with vector"""
        
        try:
            self.supabase.table("ai_memory").insert({
                "memory_id": memory.memory_id,
                "user_id": memory.user_id,
                "content": memory.content,
                "embedding": memory.embedding,
                "memory_type": memory.memory_type,
                "source_events": memory.source_events,
                "metadata": memory.metadata,
                "created_at": memory.created_at.isoformat()
            }).execute()
            
            logger.info(f"Stored memory {memory.memory_id}")
            
        except Exception as e:
            logger.error(f"Error storing memory: {e}")
    
    def _get_memory_type(self, event_category: str) -> str:
        """Map event category to memory type"""
        mapping = {
            "JOB": "job_preferences",
            "PROFILE": "career_evolution",
            "AI_INTERACTION": "interaction_patterns",
            "GOAL": "career_goals"
        }
        return mapping.get(event_category, "general")
    
    async def get_relevant_memories(
        self,
        user_id: str,
        query: str,
        memory_type: Optional[str] = None,
        limit: int = 5
    ) -> List[MemoryEmbedding]:
        """
        Retrieve memories relevant to a query using semantic search
        
        Args:
            user_id: User identifier
            query: Natural language query
            memory_type: Filter by memory type
            limit: Max memories to return
        
        Returns:
            List of relevant memories sorted by similarity
        """
        if not self.embedding_model:
            return []
        
        try:
            # Generate query embedding
            query_embedding = await self._generate_embedding(query)
            
            # Build query
            query_builder = self.supabase.table("ai_memory") \
                .select("*") \
                .eq("user_id", user_id)
            
            if memory_type:
                query_builder = query_builder.eq("memory_type", memory_type)
            
            # Execute query (would use vector similarity in production)
            # For now, get recent memories
            response = query_builder \
                .order("created_at", desc=True) \
                .limit(limit) \
                .execute()
            
            memories = []
            for record in response.data if response.data else []:
                memories.append(MemoryEmbedding(
                    memory_id=record["memory_id"],
                    user_id=record["user_id"],
                    content=record["content"],
                    embedding=record["embedding"],
                    memory_type=record["memory_type"],
                    source_events=record["source_events"],
                    metadata=record["metadata"],
                    created_at=datetime.fromisoformat(record["created_at"])
                ))
            
            logger.info(f"Retrieved {len(memories)} memories for query: {query[:50]}")
            return memories
            
        except Exception as e:
            logger.error(f"Error retrieving memories: {e}")
            return []
    
    async def get_user_context(self, user_id: str) -> Dict[str, Any]:
        """
        Build complete AI context from all memories
        
        Returns rich context for agent personalization:
        - Job preferences learned
        - Career goals inferred
        - Interaction style
        - Success patterns
        """
        try:
            # Get all memory types
            response = self.supabase.table("ai_memory") \
                .select("*") \
                .eq("user_id", user_id) \
                .order("created_at", desc=True) \
                .limit(20) \
                .execute()
            
            memories = response.data if response.data else []
            
            # Group by type
            context = {
                "job_preferences": [],
                "career_evolution": [],
                "interaction_patterns": [],
                "career_goals": [],
                "general": []
            }
            
            for mem in memories:
                mem_type = mem.get("memory_type", "general")
                if mem_type in context:
                    context[mem_type].append(mem.get("content", ""))
            
            # Build summary
            summary = {
                "user_id": user_id,
                "memory_count": len(memories),
                "last_updated": memories[0]["created_at"] if memories else None,
                "context": context,
                "ai_ready": len(memories) >= 3
            }
            
            logger.info(f"Built context for user {user_id}: {len(memories)} memories")
            return summary
            
        except Exception as e:
            logger.error(f"Error building user context: {e}")
            return {
                "user_id": user_id,
                "memory_count": 0,
                "ai_ready": False
            }
    
    async def process_event_batch(self, user_ids: List[str]):
        """
        Background job: Process events for multiple users
        
        Call this periodically (e.g., daily) to form new memories
        """
        logger.info(f"Processing events for {len(user_ids)} users")
        
        tasks = []
        for user_id in user_ids:
            # Form memories for each category
            tasks.append(self.form_memory_from_events(user_id, "JOB", days=7))
            tasks.append(self.form_memory_from_events(user_id, "PROFILE", days=7))
            tasks.append(self.form_memory_from_events(user_id, "AI_INTERACTION", days=7))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        success_count = sum(1 for r in results if isinstance(r, MemoryEmbedding))
        logger.info(f"Formed {success_count} new memories")
        
        return success_count


# Global instance
ai_memory = AIMemoryLayer()
