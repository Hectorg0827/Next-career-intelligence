"""
Event Bus - Redis Streams-based Pub/Sub for Microservices

This module provides event-driven communication between services:
- Services publish events to streams
- Services subscribe to relevant event categories
- Consumer groups ensure at-least-once delivery
- Dead letter queue handles failed events
- Event replay from specific offsets

Cost-effective alternative to Kafka using Redis Streams.
"""

import asyncio
import json
from typing import Optional, Dict, Any, List, Callable, Awaitable
from datetime import datetime
import redis.asyncio as redis

from ..events.event_types import BaseEvent, EventCategory


class EventBus:
    """
    Redis Streams-based event bus
    
    Features:
    - Topic-based routing (one stream per category)
    - Consumer groups for parallel processing
    - At-least-once delivery guarantee
    - Automatic retry with backoff
    - Dead letter queue for poison messages
    """
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        stream_prefix: str = "career_os:events:"
    ):
        self.redis_url = redis_url
        self.stream_prefix = stream_prefix
        self.redis_client: Optional[redis.Redis] = None
        self.subscribers: Dict[str, List[Callable]] = {}
        self.running = False
    
    async def connect(self):
        """Initialize Redis connection"""
        if not self.redis_client:
            self.redis_client = await redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
    
    async def disconnect(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None
    
    def _get_stream_name(self, category: str) -> str:
        """Get stream name for event category"""
        return f"{self.stream_prefix}{category}"
    
    async def publish(
        self,
        event: BaseEvent,
        category: Optional[str] = None
    ) -> str:
        """
        Publish event to appropriate stream
        
        Args:
            event: Event to publish
            category: Override event category (default: use event.event_category)
            
        Returns:
            Message ID in stream
        """
        await self.connect()
        
        # Determine stream
        stream_category = category or event.event_category
        stream_name = self._get_stream_name(stream_category)
        
        # Serialize event
        event_data = {
            "event_id": event.event_id,
            "event_type": event.event_type,
            "event_category": event.event_category,
            "user_id": event.user_id,
            "session_id": event.session_id,
            "source": event.source,
            "created_at": event.created_at,
            "event_data": json.dumps(event.event_data)
        }
        
        # Add to stream
        message_id = await self.redis_client.xadd(
            stream_name,
            event_data,
            maxlen=100000  # Keep last 100k events per stream
        )
        
        return message_id
    
    async def publish_batch(
        self,
        events: List[BaseEvent],
        category: Optional[str] = None
    ) -> List[str]:
        """
        Publish multiple events efficiently
        
        Args:
            events: List of events
            category: Override category for all events
            
        Returns:
            List of message IDs
        """
        message_ids = []
        
        for event in events:
            message_id = await self.publish(event, category)
            message_ids.append(message_id)
        
        return message_ids
    
    async def subscribe(
        self,
        category: str,
        consumer_group: str,
        consumer_name: str,
        handler: Callable[[Dict[str, Any]], Awaitable[None]],
        batch_size: int = 10,
        block_ms: int = 5000
    ):
        """
        Subscribe to event category
        
        Args:
            category: Event category to subscribe to
            consumer_group: Consumer group name (for load balancing)
            consumer_name: Unique name for this consumer
            handler: Async function to process events
            batch_size: Max events to fetch per batch
            block_ms: How long to wait for new events
        """
        await self.connect()
        
        stream_name = self._get_stream_name(category)
        
        # Create consumer group if doesn't exist
        try:
            await self.redis_client.xgroup_create(
                stream_name,
                consumer_group,
                id="0",
                mkstream=True
            )
        except redis.ResponseError as e:
            # Group already exists
            if "BUSYGROUP" not in str(e):
                raise
        
        # Start consuming
        self.running = True
        
        while self.running:
            try:
                # Read from stream
                messages = await self.redis_client.xreadgroup(
                    consumer_group,
                    consumer_name,
                    {stream_name: ">"},
                    count=batch_size,
                    block=block_ms
                )
                
                if not messages:
                    continue
                
                # Process messages
                for stream, stream_messages in messages:
                    for message_id, message_data in stream_messages:
                        try:
                            # Deserialize event data
                            event_data = {
                                **message_data,
                                "event_data": json.loads(message_data["event_data"])
                            }
                            
                            # Call handler
                            await handler(event_data)
                            
                            # Acknowledge message
                            await self.redis_client.xack(
                                stream_name,
                                consumer_group,
                                message_id
                            )
                            
                        except Exception as e:
                            print(f"Error processing event {message_id}: {e}")
                            
                            # Move to dead letter queue after retries
                            await self._handle_failed_event(
                                stream_name,
                                message_id,
                                message_data,
                                str(e)
                            )
            
            except asyncio.CancelledError:
                print(f"Subscription cancelled for {category}")
                break
            except Exception as e:
                print(f"Error in subscription loop: {e}")
                await asyncio.sleep(1)  # Brief pause before retry
    
    async def _handle_failed_event(
        self,
        stream_name: str,
        message_id: str,
        message_data: Dict[str, Any],
        error: str
    ):
        """
        Handle events that failed processing
        
        After max retries, move to dead letter queue
        """
        # TODO: Implement retry logic with exponential backoff
        # For now, just move to DLQ immediately
        
        dlq_stream = f"{stream_name}:dlq"
        
        dlq_data = {
            **message_data,
            "original_stream": stream_name,
            "original_message_id": message_id,
            "error": error,
            "failed_at": datetime.utcnow().isoformat()
        }
        
        await self.redis_client.xadd(dlq_stream, dlq_data)
        
        print(f"Moved event {message_id} to DLQ: {error}")
    
    async def replay_events(
        self,
        category: str,
        start_id: str = "0",
        end_id: str = "+",
        count: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Replay events from stream history
        
        Useful for:
        - Rebuilding projections
        - Debugging
        - Analytics
        
        Args:
            category: Event category
            start_id: Start from this message ID (0 = beginning)
            end_id: End at this message ID (+ = end)
            count: Max events to fetch
            
        Returns:
            List of events
        """
        await self.connect()
        
        stream_name = self._get_stream_name(category)
        
        messages = await self.redis_client.xrange(
            stream_name,
            min=start_id,
            max=end_id,
            count=count
        )
        
        events = []
        for message_id, message_data in messages:
            event = {
                "message_id": message_id,
                **message_data,
                "event_data": json.loads(message_data["event_data"])
            }
            events.append(event)
        
        return events
    
    async def get_stream_info(self, category: str) -> Dict[str, Any]:
        """
        Get information about a stream
        
        Returns:
            Dict with length, consumer groups, etc.
        """
        await self.connect()
        
        stream_name = self._get_stream_name(category)
        
        try:
            info = await self.redis_client.xinfo_stream(stream_name)
            groups = await self.redis_client.xinfo_groups(stream_name)
            
            return {
                "stream": stream_name,
                "length": info.get("length", 0),
                "first_entry": info.get("first-entry"),
                "last_entry": info.get("last-entry"),
                "consumer_groups": [
                    {
                        "name": g["name"],
                        "consumers": g["consumers"],
                        "pending": g["pending"]
                    }
                    for g in groups
                ]
            }
        except redis.ResponseError:
            return {
                "stream": stream_name,
                "exists": False
            }
    
    async def trim_stream(
        self,
        category: str,
        max_len: int = 50000
    ):
        """
        Trim stream to max length to save memory
        
        Args:
            category: Event category
            max_len: Maximum events to keep
        """
        await self.connect()
        
        stream_name = self._get_stream_name(category)
        await self.redis_client.xtrim(stream_name, maxlen=max_len)
    
    def stop(self):
        """Stop all subscriptions"""
        self.running = False


class EventSubscriber:
    """
    Helper class for managing event subscriptions
    
    Usage:
        subscriber = EventSubscriber(event_bus)
        
        @subscriber.on("USER_ACTION")
        async def handle_user_action(event):
            print(f"User {event['user_id']} did {event['event_type']}")
        
        await subscriber.start("my_service", "worker_1")
    """
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.handlers: Dict[str, Callable] = {}
        self.tasks: List[asyncio.Task] = []
    
    def on(self, category: str):
        """
        Decorator to register event handler
        
        @subscriber.on("USER_ACTION")
        async def my_handler(event):
            ...
        """
        def decorator(handler: Callable[[Dict[str, Any]], Awaitable[None]]):
            self.handlers[category] = handler
            return handler
        return decorator
    
    async def start(
        self,
        consumer_group: str,
        consumer_name: str
    ):
        """
        Start all subscriptions
        
        Args:
            consumer_group: Consumer group name (usually service name)
            consumer_name: Unique consumer name (usually instance ID)
        """
        for category, handler in self.handlers.items():
            task = asyncio.create_task(
                self.event_bus.subscribe(
                    category=category,
                    consumer_group=consumer_group,
                    consumer_name=consumer_name,
                    handler=handler
                )
            )
            self.tasks.append(task)
        
        # Wait for all subscriptions
        await asyncio.gather(*self.tasks)
    
    async def stop(self):
        """Stop all subscriptions"""
        self.event_bus.stop()
        
        for task in self.tasks:
            task.cancel()
        
        await asyncio.gather(*self.tasks, return_exceptions=True)


# ========================================
# Global Instance
# ========================================

# Initialize with environment variable or default
import os
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

event_bus = EventBus(redis_url=REDIS_URL)
