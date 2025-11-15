"""
AI Memory Layer - Long-term and Working Memory for Autonomous Agents

This module provides memory systems that learn from user events and behavior
to enable personalized AI agents with context awareness.

Components:
- LongTermMemory: Persistent user knowledge (preferences, patterns, traits)
- WorkingMemory: Short-term context for active conversations/sessions
- MemoryManager: Unified interface for memory operations
"""

from .long_term_memory import LongTermMemory, UserMemoryProfile
from .working_memory import WorkingMemory, ConversationContext
from .memory_manager import MemoryManager

# Singleton instances
memory_manager = MemoryManager()

__all__ = [
    "LongTermMemory",
    "UserMemoryProfile", 
    "WorkingMemory",
    "ConversationContext",
    "MemoryManager",
    "memory_manager"
]
