"""Events package - Event sourcing infrastructure"""

from .event_types import (
    BaseEvent,
    EventCategory,
    EventFactory,
    # Specific event types
    JobViewedEvent,
    JobSavedEvent,
    JobAppliedEvent,
    SearchPerformedEvent,
    ProfileUpdatedEvent,
    CoachMessageSentEvent,
    GoalCreatedEvent,
    GoalCompletedEvent
)

from .event_store import event_store, event_analytics
from .event_bus import event_bus, EventSubscriber

__all__ = [
    "BaseEvent",
    "EventCategory",
    "EventFactory",
    "JobViewedEvent",
    "JobSavedEvent",
    "JobAppliedEvent",
    "SearchPerformedEvent",
    "ProfileUpdatedEvent",
    "CoachMessageSentEvent",
    "GoalCreatedEvent",
    "GoalCompletedEvent",
    "event_store",
    "event_analytics",
    "event_bus",
    "EventSubscriber"
]
