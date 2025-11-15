#!/usr/bin/env python3
"""
Phase 1 Foundation - Quick Test Script

Tests all core components to verify everything works.
"""

import asyncio
import sys
from datetime import datetime

# Add backend to path
sys.path.insert(0, '/Users/hectorgarcia/Desktop/Next-career-intelligence/backend')

async def test_event_types():
    """Test event type creation"""
    print("🧪 Testing Event Types...")
    
    try:
        from app.services.foundation.events import EventFactory
        
        # Create a job viewed event
        event = EventFactory.create_event(
            "job_viewed",
            user_id="test-user-123",
            source="test_script",
            job_id="job-456",
            job_title="Senior Software Engineer",
            view_duration_seconds=45
        )
        
        print(f"   ✅ Created JobViewedEvent: {event.event_type}")
        print(f"      - Event ID: {event.event_id}")
        print(f"      - User: {event.user_id}")
        print(f"      - Data: {event.event_data}")
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


async def test_event_bus():
    """Test Redis event bus connection"""
    print("\n🧪 Testing Event Bus (Redis)...")
    
    try:
        from app.services.foundation.events import event_bus
        
        # Connect to Redis
        await event_bus.connect()
        
        # Check if Redis is responsive
        if event_bus.redis_client:
            await event_bus.redis_client.ping()
            print(f"   ✅ Connected to Redis at {event_bus.redis_url}")
            
            # Disconnect
            await event_bus.disconnect()
            return True
        else:
            print(f"   ❌ Failed to connect to Redis")
            return False
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


async def test_imports():
    """Test all foundation imports"""
    print("\n🧪 Testing Foundation Imports...")
    
    try:
        # Test events
        from app.services.foundation.events import (
            BaseEvent, EventCategory, EventFactory,
            event_store, event_analytics, event_bus
        )
        print("   ✅ Events package imports working")
        
        # Test profile
        from app.services.foundation.profile import unified_profile_manager
        print("   ✅ Profile package imports working")
        
        # Test journey
        from app.services.foundation.journey import session_manager, journey_analytics
        print("   ✅ Journey package imports working")
        
        # Test orchestration
        from app.services.foundation.orchestration import orchestrator
        print("   ✅ Orchestration package imports working")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("=" * 60)
    print("Phase 1 Foundation - Component Tests")
    print("=" * 60)
    
    results = []
    
    # Test imports first
    results.append(await test_imports())
    
    # Test event types
    results.append(await test_event_types())
    
    # Test event bus
    results.append(await test_event_bus())
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed! Phase 1 Foundation is ready.")
        print("\nNext steps:")
        print("1. Apply database schema to Supabase:")
        print("   psql $DATABASE_URL -f backend/database/phase1_foundation_schema.sql")
        print("\n2. See PHASE1_INTEGRATION_GUIDE.md for integration steps")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check errors above.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
