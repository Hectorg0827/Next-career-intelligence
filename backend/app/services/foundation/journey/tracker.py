"""
User Journey Tracker - Track and analyze user sessions and behavior patterns

This module provides session management and journey analytics to understand:
- How users interact with the platform
- Which features drive engagement
- Where users get stuck or drop off
- Patterns that lead to success
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from uuid import uuid4
import asyncio

from app.db.supabase import get_supabase_client
from ..events.event_store import event_store
from ..events.event_types import EventCategory


class SessionManager:
    """
    Manage user sessions
    
    A session represents a continuous period of user activity.
    Sessions are used to group related events and understand behavior patterns.
    """
    
    def __init__(self):
        self.supabase = get_supabase_client()
        self.sessions_table = "user_sessions"
        self.session_timeout_minutes = 30  # Session expires after 30min inactivity
    
    async def create_session(
        self,
        user_id: str,
        device_type: Optional[str] = None,
        browser: Optional[str] = None,
        os: Optional[str] = None,
        referrer: Optional[str] = None,
        entry_page: Optional[str] = None
    ) -> str:
        """
        Create a new user session
        
        Args:
            user_id: User UUID
            device_type: desktop, mobile, tablet
            browser: Chrome, Safari, Firefox, etc.
            os: Windows, macOS, iOS, Android, etc.
            referrer: Where they came from
            entry_page: First page they visited
            
        Returns:
            session_id: UUID
        """
        try:
            session_id = str(uuid4())
            
            session_data = {
                "id": session_id,
                "user_id": user_id,
                "started_at": datetime.utcnow().isoformat(),
                "device_type": device_type,
                "browser": browser,
                "os": os,
                "referrer": referrer,
                "entry_page": entry_page,
                "pages_visited": 1,
                "events_count": 0,
                "features_used": []
            }
            
            result = self.supabase.table(self.sessions_table).insert(session_data).execute()
            
            if result.data:
                return session_id
            else:
                raise Exception("Failed to create session")
                
        except Exception as e:
            print(f"Error creating session: {e}")
            raise
    
    async def get_active_session(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user's current active session (if exists)
        A session is active if last activity was within timeout window
        
        Args:
            user_id: User UUID
            
        Returns:
            Session dict or None
        """
        try:
            # Get most recent session
            result = (
                self.supabase.table(self.sessions_table)
                .select("*")
                .eq("user_id", user_id)
                .is_("ended_at", "null")
                .order("started_at", desc=True)
                .limit(1)
                .execute()
            )
            
            if not result.data:
                return None
            
            session = result.data[0]
            
            # Check if session is still active (within timeout)
            started_at = datetime.fromisoformat(session["started_at"].replace("Z", "+00:00"))
            time_since_start = datetime.utcnow() - started_at
            
            if time_since_start.total_seconds() / 60 > self.session_timeout_minutes:
                # Session expired, end it
                await self.end_session(session["id"])
                return None
            
            return session
            
        except Exception as e:
            print(f"Error getting active session: {e}")
            return None
    
    async def get_or_create_session(
        self,
        user_id: str,
        **session_kwargs
    ) -> str:
        """
        Get active session or create new one
        
        Args:
            user_id: User UUID
            **session_kwargs: Additional session parameters
            
        Returns:
            session_id: UUID
        """
        active_session = await self.get_active_session(user_id)
        
        if active_session:
            return active_session["id"]
        else:
            return await self.create_session(user_id, **session_kwargs)
    
    async def update_session_activity(
        self,
        session_id: str,
        page_visited: Optional[str] = None,
        feature_used: Optional[str] = None
    ) -> None:
        """
        Update session with new activity
        
        Args:
            session_id: Session UUID
            page_visited: Page URL/path
            feature_used: Feature identifier
        """
        try:
            # Get current session
            result = (
                self.supabase.table(self.sessions_table)
                .select("*")
                .eq("id", session_id)
                .single()
                .execute()
            )
            
            if not result.data:
                return
            
            session = result.data
            updates = {}
            
            # Increment pages visited
            if page_visited:
                updates["pages_visited"] = session.get("pages_visited", 0) + 1
                updates["exit_page"] = page_visited
            
            # Add to features used
            if feature_used:
                features = session.get("features_used", [])
                if feature_used not in features:
                    features.append(feature_used)
                    updates["features_used"] = features
            
            # Update if we have changes
            if updates:
                self.supabase.table(self.sessions_table).update(updates).eq("id", session_id).execute()
                
        except Exception as e:
            print(f"Error updating session activity: {e}")
    
    async def end_session(self, session_id: str) -> None:
        """
        End a session and calculate metrics
        
        Args:
            session_id: Session UUID
        """
        try:
            # Get session
            result = (
                self.supabase.table(self.sessions_table)
                .select("*")
                .eq("id", session_id)
                .single()
                .execute()
            )
            
            if not result.data:
                return
            
            session = result.data
            
            # Calculate duration
            started_at = datetime.fromisoformat(session["started_at"].replace("Z", "+00:00"))
            ended_at = datetime.utcnow()
            duration_seconds = int((ended_at - started_at).total_seconds())
            
            # Get event count for this session
            events = await event_store.get_events_by_session(session_id)
            events_count = len(events)
            
            # Update session
            updates = {
                "ended_at": ended_at.isoformat(),
                "duration_seconds": duration_seconds,
                "events_count": events_count
            }
            
            self.supabase.table(self.sessions_table).update(updates).eq("id", session_id).execute()
            
        except Exception as e:
            print(f"Error ending session: {e}")
    
    async def get_user_sessions(
        self,
        user_id: str,
        limit: int = 10,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get user's session history
        
        Args:
            user_id: User UUID
            limit: Max sessions
            offset: Pagination offset
            
        Returns:
            List of sessions
        """
        try:
            result = (
                self.supabase.table(self.sessions_table)
                .select("*")
                .eq("user_id", user_id)
                .order("started_at", desc=True)
                .limit(limit)
                .offset(offset)
                .execute()
            )
            
            return result.data if result.data else []
            
        except Exception as e:
            print(f"Error getting user sessions: {e}")
            return []


class JourneyAnalytics:
    """
    Analyze user journey and behavior patterns
    """
    
    def __init__(self):
        self.supabase = get_supabase_client()
        self.session_manager = SessionManager()
    
    async def get_user_engagement_metrics(
        self,
        user_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get comprehensive engagement metrics for a user
        
        Returns:
            Dict with various engagement metrics
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get sessions
        all_sessions = await self.session_manager.get_user_sessions(
            user_id=user_id,
            limit=1000
        )
        
        # Filter to date range
        sessions = [
            s for s in all_sessions
            if datetime.fromisoformat(s["started_at"].replace("Z", "+00:00")) >= start_date
        ]
        
        # Get events
        events = await event_store.get_events_by_user(
            user_id=user_id,
            start_date=start_date,
            limit=10000
        )
        
        # Calculate metrics
        total_sessions = len(sessions)
        total_time_seconds = sum(s.get("duration_seconds", 0) for s in sessions)
        avg_session_duration = total_time_seconds / total_sessions if total_sessions > 0 else 0
        
        # Event breakdown by category
        event_categories = {}
        for event in events:
            category = event.get("event_category", "unknown")
            event_categories[category] = event_categories.get(category, 0) + 1
        
        # Feature usage
        all_features = []
        for session in sessions:
            all_features.extend(session.get("features_used", []))
        
        feature_counts = {}
        for feature in all_features:
            feature_counts[feature] = feature_counts.get(feature, 0) + 1
        
        # Most used features (top 5)
        top_features = sorted(
            feature_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return {
            "period_days": days,
            "total_sessions": total_sessions,
            "total_events": len(events),
            "total_time_seconds": total_time_seconds,
            "avg_session_duration_seconds": round(avg_session_duration, 2),
            "avg_events_per_session": round(len(events) / total_sessions, 2) if total_sessions > 0 else 0,
            "event_categories": event_categories,
            "top_features": dict(top_features),
            "days_active": len(set(
                datetime.fromisoformat(s["started_at"].replace("Z", "+00:00")).date()
                for s in sessions
            )),
            "activity_rate": len(set(
                datetime.fromisoformat(s["started_at"].replace("Z", "+00:00")).date()
                for s in sessions
            )) / days * 100
        }
    
    async def get_feature_adoption(
        self,
        user_id: str
    ) -> Dict[str, Dict[str, Any]]:
        """
        Track which features user has adopted and when
        
        Returns:
            Dict of features with first_used, last_used, usage_count
        """
        events = await event_store.get_events_by_user(
            user_id=user_id,
            limit=10000
        )
        
        feature_adoption = {}
        
        for event in events:
            source = event.get("source")
            if not source:
                continue
            
            created_at = event["created_at"]
            
            if source not in feature_adoption:
                feature_adoption[source] = {
                    "first_used": created_at,
                    "last_used": created_at,
                    "usage_count": 0,
                    "event_types": set()
                }
            
            feature_adoption[source]["last_used"] = created_at
            feature_adoption[source]["usage_count"] += 1
            feature_adoption[source]["event_types"].add(event["event_type"])
        
        # Convert sets to lists
        for feature in feature_adoption:
            feature_adoption[feature]["event_types"] = list(
                feature_adoption[feature]["event_types"]
            )
        
        return feature_adoption
    
    async def get_user_journey_timeline(
        self,
        user_id: str,
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Get day-by-day timeline of user activity
        
        Returns:
            List of daily activity summaries
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        events = await event_store.get_events_by_user(
            user_id=user_id,
            start_date=start_date,
            limit=10000
        )
        
        # Group by date
        daily_activity = {}
        
        for event in events:
            event_date = datetime.fromisoformat(
                event["created_at"].replace("Z", "+00:00")
            ).date()
            
            date_key = event_date.isoformat()
            
            if date_key not in daily_activity:
                daily_activity[date_key] = {
                    "date": date_key,
                    "events_count": 0,
                    "event_categories": {},
                    "features_used": set(),
                    "highlights": []
                }
            
            daily_activity[date_key]["events_count"] += 1
            
            category = event.get("event_category", "unknown")
            daily_activity[date_key]["event_categories"][category] = \
                daily_activity[date_key]["event_categories"].get(category, 0) + 1
            
            if event.get("source"):
                daily_activity[date_key]["features_used"].add(event["source"])
            
            # Add highlights (important events)
            if event["event_type"] in ["goal_created", "goal_completed", "job_applied"]:
                daily_activity[date_key]["highlights"].append({
                    "type": event["event_type"],
                    "time": event["created_at"]
                })
        
        # Convert to list and sort
        timeline = []
        for date_key in sorted(daily_activity.keys()):
            day = daily_activity[date_key]
            day["features_used"] = list(day["features_used"])
            timeline.append(day)
        
        return timeline


# ========================================
# Global Instances
# ========================================

session_manager = SessionManager()
journey_analytics = JourneyAnalytics()
