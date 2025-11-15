"""
Foundation Layer - Phase 1 Event-Driven Architecture

This package provides the core foundation for Career OS:

Events:
- event_types: Comprehensive event type definitions
- event_store: Persistent event storage and analytics
- event_bus: Redis-based pub/sub for microservices

Profile:
- unified_profile: Consolidated user profile management

Journey:
- tracker: Session management and journey analytics

Orchestration:
- service_orchestrator: Cross-feature workflow coordination

Usage:
    from app.services.foundation.events import event_store, event_bus, EventFactory
    from app.services.foundation.profile import unified_profile_manager
    from app.services.foundation.journey import session_manager, journey_analytics
    from app.services.foundation.orchestration import orchestrator
"""

__version__ = "1.0.0"
