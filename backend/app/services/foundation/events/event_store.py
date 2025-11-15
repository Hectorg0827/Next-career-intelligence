"""
Event Store - Persistent storage for all career events

This is the foundation of the Career OS learning system.
Every user interaction is captured and can be replayed for:
- AI training and personalization
- Analytics and insights
- Debugging and audit
- Building user journey timelines
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from uuid import uuid4
import json

from .event_types import BaseEvent, EventCategory
from app.db.supabase import get_supabase_client


class EventStore:
    """
    Persistent event storage using Supabase
    
    Design principles:
    - Append-only (never delete or update events)
    - Fast writes (async, batched)
    - Efficient queries (indexed by user, type, date)
    - JSON-queryable event data
    """
    
    def __init__(self):
        self.supabase = get_supabase_client()
        self.table_name = "career_events"
    
    async def store_event(self, event: BaseEvent) -> str:
        """
        Store a single event
        
        Args:
            event: Event to store
            
        Returns:
            event_id: UUID of stored event
        """
        try:
            # Convert event to dict for storage
            event_dict = {
                "user_id": event.user_id,
                "event_type": event.event_type,
                "event_category": event.event_category,
                "event_data": event.event_data,
                "session_id": event.session_id,
                "source": event.source,
                "user_agent": event.user_agent,
                "ip_address": event.ip_address,
                "created_at": event.created_at.isoformat(),
            }
            
            # Insert into Supabase
            result = self.supabase.table(self.table_name).insert(event_dict).execute()
            
            if result.data:
                return result.data[0]["id"]
            else:
                raise Exception("Failed to store event")
                
        except Exception as e:
            print(f"Error storing event: {e}")
            raise
    
    async def store_events_batch(self, events: List[BaseEvent]) -> List[str]:
        """
        Store multiple events in a single transaction
        Better performance for bulk operations
        
        Args:
            events: List of events to store
            
        Returns:
            event_ids: List of UUIDs
        """
        try:
            events_dicts = []
            for event in events:
                event_dict = {
                    "user_id": event.user_id,
                    "event_type": event.event_type,
                    "event_category": event.event_category,
                    "event_data": event.event_data,
                    "session_id": event.session_id,
                    "source": event.source,
                    "user_agent": event.user_agent,
                    "ip_address": event.ip_address,
                    "created_at": event.created_at.isoformat(),
                }
                events_dicts.append(event_dict)
            
            result = self.supabase.table(self.table_name).insert(events_dicts).execute()
            
            if result.data:
                return [row["id"] for row in result.data]
            else:
                raise Exception("Failed to store events batch")
                
        except Exception as e:
            print(f"Error storing events batch: {e}")
            raise
    
    async def get_events_by_user(
        self,
        user_id: str,
        limit: int = 100,
        offset: int = 0,
        event_category: Optional[EventCategory] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Get events for a specific user
        
        Args:
            user_id: User UUID
            limit: Max number of events
            offset: Pagination offset
            event_category: Filter by category
            start_date: Filter events after this date
            end_date: Filter events before this date
            
        Returns:
            List of event dictionaries
        """
        try:
            query = self.supabase.table(self.table_name).select("*").eq("user_id", user_id)
            
            # Apply filters
            if event_category:
                query = query.eq("event_category", event_category)
            
            if start_date:
                query = query.gte("created_at", start_date.isoformat())
            
            if end_date:
                query = query.lte("created_at", end_date.isoformat())
            
            # Order and paginate
            query = query.order("created_at", desc=True).limit(limit).offset(offset)
            
            result = query.execute()
            return result.data if result.data else []
            
        except Exception as e:
            print(f"Error getting events by user: {e}")
            return []
    
    async def get_events_by_session(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get all events in a user session
        Useful for understanding user behavior patterns
        
        Args:
            session_id: Session UUID
            
        Returns:
            List of events in chronological order
        """
        try:
            result = (
                self.supabase.table(self.table_name)
                .select("*")
                .eq("session_id", session_id)
                .order("created_at", desc=False)
                .execute()
            )
            
            return result.data if result.data else []
            
        except Exception as e:
            print(f"Error getting events by session: {e}")
            return []
    
    async def get_event_counts(
        self,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, int]:
        """
        Get event counts by type for a user
        
        Args:
            user_id: User UUID
            start_date: Count events after this date
            end_date: Count events before this date
            
        Returns:
            Dict mapping event_type to count
        """
        try:
            query = self.supabase.table(self.table_name).select("event_type").eq("user_id", user_id)
            
            if start_date:
                query = query.gte("created_at", start_date.isoformat())
            
            if end_date:
                query = query.lte("created_at", end_date.isoformat())
            
            result = query.execute()
            
            # Count by type
            counts: Dict[str, int] = {}
            for event in result.data:
                event_type = event["event_type"]
                counts[event_type] = counts.get(event_type, 0) + 1
            
            return counts
            
        except Exception as e:
            print(f"Error getting event counts: {e}")
            return {}
    
    async def get_recent_events_by_type(
        self,
        user_id: str,
        event_type: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get most recent events of a specific type
        
        Args:
            user_id: User UUID
            event_type: Event type to filter
            limit: Number of events
            
        Returns:
            List of events
        """
        try:
            result = (
                self.supabase.table(self.table_name)
                .select("*")
                .eq("user_id", user_id)
                .eq("event_type", event_type)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            
            return result.data if result.data else []
            
        except Exception as e:
            print(f"Error getting recent events by type: {e}")
            return []
    
    async def get_user_timeline(
        self,
        user_id: str,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get complete user timeline for the last N days
        Useful for visualizing user journey
        
        Args:
            user_id: User UUID
            days: Number of days to look back
            
        Returns:
            List of events in chronological order
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        try:
            result = (
                self.supabase.table(self.table_name)
                .select("*")
                .eq("user_id", user_id)
                .gte("created_at", start_date.isoformat())
                .order("created_at", desc=False)
                .execute()
            )
            
            return result.data if result.data else []
            
        except Exception as e:
            print(f"Error getting user timeline: {e}")
            return []
    
    async def search_events(
        self,
        user_id: str,
        search_term: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Search events by content in event_data
        Uses PostgreSQL's JSONB search capabilities
        
        Args:
            user_id: User UUID
            search_term: Term to search for in event_data
            limit: Max results
            
        Returns:
            Matching events
        """
        try:
            # Use Supabase's textSearch for JSONB columns
            result = (
                self.supabase.table(self.table_name)
                .select("*")
                .eq("user_id", user_id)
                .textSearch("event_data", search_term)
                .limit(limit)
                .execute()
            )
            
            return result.data if result.data else []
            
        except Exception as e:
            print(f"Error searching events: {e}")
            return []


# ========================================
# Event Store Analytics
# ========================================

class EventStoreAnalytics:
    """
    Analytics queries on the event store
    Higher-level insights from raw events
    """
    
    def __init__(self):
        self.event_store = EventStore()
    
    async def get_user_engagement_score(
        self,
        user_id: str,
        days: int = 7
    ) -> float:
        """
        Calculate user engagement score based on recent activity
        
        Score factors:
        - Number of events
        - Variety of event types
        - Frequency over time
        - Completion of actions (viewed -> saved -> applied)
        
        Returns:
            Score from 0-100
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get event counts
        events = await self.event_store.get_events_by_user(
            user_id=user_id,
            start_date=start_date
        )
        
        if not events:
            return 0.0
        
        # Calculate sub-scores
        volume_score = min(len(events) / 50 * 40, 40)  # Max 40 points for volume
        
        # Variety score (unique event types)
        unique_types = len(set(event["event_type"] for event in events))
        variety_score = min(unique_types / 10 * 30, 30)  # Max 30 points
        
        # Frequency score (events per day)
        events_per_day = len(events) / days
        frequency_score = min(events_per_day / 5 * 30, 30)  # Max 30 points
        
        total_score = volume_score + variety_score + frequency_score
        
        return round(total_score, 2)
    
    async def get_feature_usage_stats(
        self,
        user_id: str,
        days: int = 30
    ) -> Dict[str, Dict[str, Any]]:
        """
        Get statistics on which features the user has used
        
        Returns:
            Dict with usage counts and last used date for each feature
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        events = await self.event_store.get_events_by_user(
            user_id=user_id,
            start_date=start_date,
            limit=1000
        )
        
        feature_stats: Dict[str, Dict[str, Any]] = {}
        
        for event in events:
            source = event.get("source", "unknown")
            
            if source not in feature_stats:
                feature_stats[source] = {
                    "count": 0,
                    "first_used": event["created_at"],
                    "last_used": event["created_at"],
                    "event_types": set()
                }
            
            feature_stats[source]["count"] += 1
            feature_stats[source]["last_used"] = event["created_at"]
            feature_stats[source]["event_types"].add(event["event_type"])
        
        # Convert sets to lists for JSON serialization
        for feature in feature_stats:
            feature_stats[feature]["event_types"] = list(feature_stats[feature]["event_types"])
        
        return feature_stats
    
    async def get_conversion_funnel(
        self,
        user_id: str,
        days: int = 30
    ) -> Dict[str, int]:
        """
        Track job application funnel:
        viewed -> saved -> applied
        
        Returns:
            Counts at each funnel stage
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        viewed = await self.event_store.get_recent_events_by_type(
            user_id=user_id,
            event_type="job_viewed",
            limit=1000
        )
        
        saved = await self.event_store.get_recent_events_by_type(
            user_id=user_id,
            event_type="job_saved",
            limit=1000
        )
        
        applied = await self.event_store.get_recent_events_by_type(
            user_id=user_id,
            event_type="job_applied",
            limit=1000
        )
        
        return {
            "viewed": len(viewed),
            "saved": len(saved),
            "applied": len(applied),
            "view_to_save_rate": len(saved) / len(viewed) * 100 if viewed else 0,
            "save_to_apply_rate": len(applied) / len(saved) * 100 if saved else 0,
            "view_to_apply_rate": len(applied) / len(viewed) * 100 if viewed else 0,
        }


# ========================================
# Global Instance
# ========================================

event_store = EventStore()
event_analytics = EventStoreAnalytics()
