"""
Working Memory - Short-term Context for Active Sessions

Maintains conversation context, recent actions, and temporary state
for active user interactions with AI agents.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from collections import deque
import logging

logger = logging.getLogger(__name__)


class Message(BaseModel):
    """A single message in a conversation"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ConversationContext(BaseModel):
    """Context for an active conversation"""
    conversation_id: str
    user_id: str
    messages: List[Message] = Field(default_factory=list)
    topic: Optional[str] = None
    intent: Optional[str] = None
    entities: Dict[str, Any] = Field(default_factory=dict)
    state: Dict[str, Any] = Field(default_factory=dict)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    
    @property
    def duration_minutes(self) -> int:
        """Get conversation duration in minutes"""
        return int((self.last_activity - self.started_at).total_seconds() / 60)
    
    @property
    def message_count(self) -> int:
        """Get total message count"""
        return len(self.messages)


class RecentAction(BaseModel):
    """A recent user action to maintain context"""
    action_type: str
    action_data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class WorkingMemory:
    """
    Working memory system for active user sessions.
    
    Maintains short-term context including:
    - Active conversations
    - Recent actions
    - Temporary state
    - Session context
    """
    
    def __init__(self, max_messages: int = 50, context_window_minutes: int = 30):
        self.conversations: Dict[str, ConversationContext] = {}
        self.recent_actions: Dict[str, deque] = {}  # user_id -> deque of actions
        self.max_messages = max_messages
        self.context_window = timedelta(minutes=context_window_minutes)
        self.max_recent_actions = 20
    
    # ==================== Conversation Management ====================
    
    def start_conversation(
        self,
        conversation_id: str,
        user_id: str,
        topic: Optional[str] = None,
        initial_state: Optional[Dict] = None
    ) -> ConversationContext:
        """Start a new conversation context"""
        
        context = ConversationContext(
            conversation_id=conversation_id,
            user_id=user_id,
            topic=topic,
            state=initial_state or {}
        )
        
        self.conversations[conversation_id] = context
        logger.info(f"Started conversation {conversation_id} for user {user_id}")
        
        return context
    
    def get_conversation(self, conversation_id: str) -> Optional[ConversationContext]:
        """Get conversation context"""
        return self.conversations.get(conversation_id)
    
    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict] = None
    ) -> bool:
        """Add a message to conversation"""
        
        if conversation_id not in self.conversations:
            logger.warning(f"Conversation {conversation_id} not found")
            return False
        
        context = self.conversations[conversation_id]
        
        message = Message(
            role=role,
            content=content,
            metadata=metadata or {}
        )
        
        context.messages.append(message)
        context.last_activity = datetime.utcnow()
        
        # Trim old messages if exceeding max
        if len(context.messages) > self.max_messages:
            context.messages = context.messages[-self.max_messages:]
        
        return True
    
    def get_recent_messages(
        self,
        conversation_id: str,
        limit: int = 10
    ) -> List[Message]:
        """Get recent messages from conversation"""
        
        context = self.conversations.get(conversation_id)
        if not context:
            return []
        
        return context.messages[-limit:]
    
    def update_conversation_state(
        self,
        conversation_id: str,
        state_updates: Dict[str, Any]
    ) -> bool:
        """Update conversation state"""
        
        if conversation_id not in self.conversations:
            return False
        
        context = self.conversations[conversation_id]
        context.state.update(state_updates)
        context.last_activity = datetime.utcnow()
        
        return True
    
    def set_conversation_intent(
        self,
        conversation_id: str,
        intent: str,
        entities: Optional[Dict] = None
    ) -> bool:
        """Set detected intent and entities for conversation"""
        
        if conversation_id not in self.conversations:
            return False
        
        context = self.conversations[conversation_id]
        context.intent = intent
        if entities:
            context.entities.update(entities)
        
        return True
    
    def end_conversation(self, conversation_id: str) -> bool:
        """End and remove conversation from working memory"""
        
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            logger.info(f"Ended conversation {conversation_id}")
            return True
        
        return False
    
    # ==================== Recent Actions ====================
    
    def record_action(
        self,
        user_id: str,
        action_type: str,
        action_data: Dict[str, Any]
    ):
        """Record a user action for context"""
        
        if user_id not in self.recent_actions:
            self.recent_actions[user_id] = deque(maxlen=self.max_recent_actions)
        
        action = RecentAction(
            action_type=action_type,
            action_data=action_data
        )
        
        self.recent_actions[user_id].append(action)
    
    def get_recent_actions(
        self,
        user_id: str,
        limit: Optional[int] = None,
        action_type: Optional[str] = None
    ) -> List[RecentAction]:
        """Get recent actions for user"""
        
        if user_id not in self.recent_actions:
            return []
        
        actions = list(self.recent_actions[user_id])
        
        # Filter by type if specified
        if action_type:
            actions = [a for a in actions if a.action_type == action_type]
        
        # Apply limit
        if limit:
            actions = actions[-limit:]
        
        return actions
    
    def get_context_window_actions(
        self,
        user_id: str,
        action_type: Optional[str] = None
    ) -> List[RecentAction]:
        """Get actions within context window (e.g., last 30 minutes)"""
        
        if user_id not in self.recent_actions:
            return []
        
        cutoff = datetime.utcnow() - self.context_window
        actions = [
            a for a in self.recent_actions[user_id]
            if a.timestamp >= cutoff
        ]
        
        if action_type:
            actions = [a for a in actions if a.action_type == action_type]
        
        return actions
    
    # ==================== Context Building ====================
    
    def build_context_summary(
        self,
        user_id: str,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Build a context summary for AI agents.
        
        Returns structured context including recent messages,
        actions, and state that agents can use for decisions.
        """
        
        summary = {
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "conversation": None,
            "recent_messages": [],
            "recent_actions": [],
            "active_context": {}
        }
        
        # Add conversation context
        if conversation_id:
            context = self.conversations.get(conversation_id)
            if context:
                summary["conversation"] = {
                    "id": conversation_id,
                    "topic": context.topic,
                    "intent": context.intent,
                    "entities": context.entities,
                    "state": context.state,
                    "duration_minutes": context.duration_minutes,
                    "message_count": context.message_count
                }
                
                # Recent messages
                recent = self.get_recent_messages(conversation_id, limit=10)
                summary["recent_messages"] = [
                    {
                        "role": m.role,
                        "content": m.content,
                        "timestamp": m.timestamp.isoformat()
                    }
                    for m in recent
                ]
        
        # Add recent actions within context window
        recent_actions = self.get_context_window_actions(user_id)
        summary["recent_actions"] = [
            {
                "type": a.action_type,
                "data": a.action_data,
                "timestamp": a.timestamp.isoformat()
            }
            for a in recent_actions
        ]
        
        # Add active context from actions
        summary["active_context"] = self._extract_active_context(recent_actions)
        
        return summary
    
    def _extract_active_context(self, actions: List[RecentAction]) -> Dict[str, Any]:
        """Extract meaningful context from recent actions"""
        
        context = {
            "recently_viewed_jobs": [],
            "recently_saved_jobs": [],
            "recent_searches": [],
            "active_features": set()
        }
        
        for action in actions:
            action_type = action.action_type
            data = action.action_data
            
            if action_type == "job_viewed":
                context["recently_viewed_jobs"].append({
                    "job_id": data.get("job_id"),
                    "title": data.get("job_title"),
                    "company": data.get("company")
                })
            
            elif action_type == "job_saved":
                context["recently_saved_jobs"].append({
                    "job_id": data.get("job_id"),
                    "title": data.get("job_title")
                })
            
            elif action_type == "search_performed":
                context["recent_searches"].append({
                    "query": data.get("query"),
                    "filters": data.get("filters")
                })
            
            # Track active features
            if "source" in data:
                context["active_features"].add(data["source"])
        
        # Convert set to list for JSON serialization
        context["active_features"] = list(context["active_features"])
        
        # Limit lists to prevent bloat
        context["recently_viewed_jobs"] = context["recently_viewed_jobs"][-5:]
        context["recently_saved_jobs"] = context["recently_saved_jobs"][-5:]
        context["recent_searches"] = context["recent_searches"][-3:]
        
        return context
    
    # ==================== Cleanup ====================
    
    def cleanup_stale_contexts(self):
        """Remove stale conversations and actions"""
        
        cutoff = datetime.utcnow() - self.context_window * 2
        
        # Remove old conversations
        stale_conversations = [
            conv_id for conv_id, context in self.conversations.items()
            if context.last_activity < cutoff
        ]
        
        for conv_id in stale_conversations:
            del self.conversations[conv_id]
        
        if stale_conversations:
            logger.info(f"Cleaned up {len(stale_conversations)} stale conversations")
        
        # Recent actions are automatically trimmed by deque maxlen
    
    def get_stats(self) -> Dict[str, int]:
        """Get working memory statistics"""
        return {
            "active_conversations": len(self.conversations),
            "users_with_recent_actions": len(self.recent_actions),
            "total_messages": sum(
                len(c.messages) for c in self.conversations.values()
            )
        }
