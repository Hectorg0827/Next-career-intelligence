# Phase 1 Foundation - Integration Guide

## Overview

Phase 1 Foundation Layer is now complete with event-driven architecture. This guide shows how to integrate existing services with the new foundation.

## What's Been Built

### 1. Event Infrastructure ✅
- **event_types.py**: 70+ typed events (JobViewedEvent, ProfileUpdatedEvent, etc.)
- **event_store.py**: Persistent storage + analytics (engagement scoring, funnel tracking)
- **event_bus.py**: Redis Streams pub/sub for microservices

### 2. Profile Management ✅
- **unified_profile.py**: Consolidates career_profiles + user_profile into single API
- Auto-calculates completeness scores
- Generates AI context for personalization

### 3. Journey Analytics ✅
- **tracker.py**: Session management with automatic timeout
- Engagement metrics (sessions, events, features used)
- Feature adoption tracking

### 4. Service Orchestration ✅
- **service_orchestrator.py**: Coordinates cross-feature workflows
- Auto-triggers downstream actions (profile update → recalc recommendations)
- Awards milestones automatically

## Database Setup

### Step 1: Apply Schema
```bash
# Connect to Supabase and run:
psql $DATABASE_URL -f backend/database/phase1_foundation_schema.sql
```

This creates:
- `career_events` - Event log
- `user_sessions` - Session tracking
- `career_profile_versions` - Audit trail
- `user_journey_metrics` - Daily aggregations
- `career_milestones` - Achievement tracking
- `profile_completeness_history` - Progress tracking

### Step 2: Verify Tables
```sql
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name LIKE '%career%' OR table_name LIKE '%session%';
```

## Redis Setup

### Local Development
```bash
# Install Redis
brew install redis  # macOS
# or
apt-get install redis  # Linux

# Start Redis
redis-server
```

### Production (Upstash/Redis Cloud)
```bash
# Get Redis URL from provider
export REDIS_URL="redis://username:password@host:port"
```

## Integration Steps

### Step 1: Install Dependencies
```bash
cd backend
pip install redis asyncio pydantic
```

### Step 2: Update Environment Variables
```bash
# Add to .env
REDIS_URL=redis://localhost:6379
DATABASE_URL=your_supabase_url
```

### Step 3: Integrate Job Search Service

**Before:**
```python
# backend/app/api/jobs.py
@router.get("/jobs/{job_id}")
async def get_job(job_id: str):
    job = fetch_job(job_id)
    return job
```

**After:**
```python
from app.services.foundation.events import event_store, EventFactory

@router.get("/jobs/{job_id}")
async def get_job(
    job_id: str,
    user_id: str,
    session_id: Optional[str] = None
):
    # Track start time
    start_time = datetime.utcnow()
    
    # Fetch job
    job = fetch_job(job_id)
    
    # Calculate view duration
    view_duration = (datetime.utcnow() - start_time).total_seconds()
    
    # Emit event
    event = EventFactory.create_event(
        "job_viewed",
        user_id=user_id,
        session_id=session_id,
        source="job_search",
        job_id=job_id,
        job_title=job["title"],
        view_duration_seconds=view_duration
    )
    await event_store.store_event(event)
    
    return job
```

### Step 4: Integrate Career Coach

**Before:**
```python
# backend/app/api/coach.py
@router.post("/coach/message")
async def send_message(message: str):
    response = generate_coach_response(message)
    return {"response": response}
```

**After:**
```python
from app.services.foundation.events import event_store, EventFactory

@router.post("/coach/message")
async def send_message(
    user_id: str,
    conversation_id: str,
    message: str,
    session_id: Optional[str] = None
):
    # Generate response
    response = generate_coach_response(message)
    
    # Emit events for both user and AI messages
    user_event = EventFactory.create_event(
        "coach_message_sent",
        user_id=user_id,
        session_id=session_id,
        source="career_coach",
        conversation_id=conversation_id,
        message_content=message,
        sender="user",
        conversation_turn=get_turn_number(conversation_id)
    )
    await event_store.store_event(user_event)
    
    ai_event = EventFactory.create_event(
        "coach_message_received",
        user_id=user_id,
        session_id=session_id,
        source="career_coach",
        conversation_id=conversation_id,
        message_content=response,
        sender="ai",
        conversation_turn=get_turn_number(conversation_id)
    )
    await event_store.store_event(ai_event)
    
    return {"response": response}
```

### Step 5: Integrate Profile Updates

**Before:**
```python
# backend/app/api/profile.py
@router.put("/profile")
async def update_profile(user_id: str, updates: dict):
    profile = update_career_profile(user_id, updates)
    return profile
```

**After:**
```python
from app.services.foundation.profile import unified_profile_manager

@router.put("/profile")
async def update_profile(
    user_id: str,
    updates: dict,
    session_id: Optional[str] = None
):
    # Use unified profile manager (automatically emits events)
    profile = await unified_profile_manager.update_career_profile(
        user_id=user_id,
        updates=updates,
        source="manual_edit"
    )
    
    # Orchestrator will automatically:
    # 1. Recalculate completeness
    # 2. Update job fit scores
    # 3. Trigger recommendation refresh
    
    return profile
```

### Step 6: Add Session Tracking to Frontend

**Add to Next.js middleware:**
```typescript
// frontend/middleware.ts
import { v4 as uuidv4 } from 'uuid';

export function middleware(request: NextRequest) {
  // Get or create session ID
  let sessionId = request.cookies.get('session_id')?.value;
  
  if (!sessionId) {
    sessionId = uuidv4();
  }
  
  const response = NextResponse.next();
  response.cookies.set('session_id', sessionId, {
    maxAge: 30 * 60, // 30 minutes
    httpOnly: true
  });
  
  return response;
}
```

**Send session ID with API requests:**
```typescript
// frontend/lib/api.ts
const sessionId = getCookie('session_id');

const response = await fetch('/api/jobs', {
  headers: {
    'X-Session-Id': sessionId
  }
});
```

### Step 7: Start Orchestrator Service

**Create startup script:**
```python
# backend/app/main.py
from app.services.foundation.orchestration import orchestrator
import asyncio

@app.on_event("startup")
async def startup_event():
    # Start orchestrator in background
    asyncio.create_task(
        orchestrator.start(
            service_name="orchestrator",
            instance_id="main"
        )
    )

@app.on_event("shutdown")
async def shutdown_event():
    await orchestrator.stop()
```

## Testing Integration

### Test Event Storage
```python
from app.services.foundation.events import event_store, EventFactory

# Create test event
event = EventFactory.create_event(
    "job_viewed",
    user_id="test-user-123",
    source="test",
    job_id="job-456",
    job_title="Software Engineer"
)

# Store it
await event_store.store_event(event)

# Retrieve it
events = await event_store.get_events_by_user("test-user-123")
print(f"Found {len(events)} events")
```

### Test Unified Profile
```python
from app.services.foundation.profile import unified_profile_manager

# Get unified profile
profile = await unified_profile_manager.get_unified_profile("user-123")

print(f"Completeness: {profile['completeness']['overall_score']}%")
print(f"Engagement: {profile['engagement']['engagement_score']}/100")
print(f"Career Stage: {profile['ai_context']['career_stage']}")
```

### Test Session Tracking
```python
from app.services.foundation.journey import session_manager

# Create session
session_id = await session_manager.create_session(
    user_id="user-123",
    device_type="desktop",
    browser="Chrome"
)

# Update activity
await session_manager.update_session_activity(
    session_id=session_id,
    page_visited="/jobs",
    feature_used="job_search"
)

# End session
await session_manager.end_session(session_id)
```

## Monitoring

### Check Event Bus Health
```python
from app.services.foundation.events import event_bus

# Get stream info
info = await event_bus.get_stream_info("USER_ACTION")
print(f"Stream length: {info['length']}")
print(f"Consumer groups: {info['consumer_groups']}")
```

### View Engagement Metrics
```python
from app.services.foundation.journey import journey_analytics

# Get 30-day metrics
metrics = await journey_analytics.get_user_engagement_metrics(
    user_id="user-123",
    days=30
)

print(f"Total sessions: {metrics['total_sessions']}")
print(f"Total events: {metrics['total_events']}")
print(f"Activity rate: {metrics['activity_rate']}%")
```

### Check Analytics
```python
from app.services.foundation.events import event_analytics

# Engagement score
score = await event_analytics.get_user_engagement_score(
    user_id="user-123",
    days=7
)
print(f"Engagement score: {score}/100")

# Conversion funnel
funnel = await event_analytics.get_conversion_funnel("user-123")
print(f"View → Save: {funnel['viewed_to_saved_rate']}%")
print(f"Save → Apply: {funnel['saved_to_applied_rate']}%")
```

## Next Steps

### Phase 1 Completion Checklist
- [ ] Apply database schema to Supabase
- [ ] Set up Redis (local or cloud)
- [ ] Install Python dependencies
- [ ] Integrate job search (emit job_viewed events)
- [ ] Integrate career coach (emit coach_message events)
- [ ] Integrate profile updates (use unified_profile_manager)
- [ ] Add session tracking to frontend
- [ ] Start orchestrator service
- [ ] Test event flow end-to-end
- [ ] Monitor metrics dashboard

### Ready for Phase 2: Autonomous Agents
Once Phase 1 is integrated and collecting events:
- Build AI agents that learn from event history
- Implement persistent memory using event store
- Create recommendation engine using behavioral data
- Add proactive suggestions based on journey patterns

## Troubleshooting

### Events not being stored
Check Supabase connection and RLS policies:
```sql
-- Verify RLS allows backend to insert
SELECT * FROM career_events WHERE user_id = 'test-user-123';
```

### Redis connection failed
Verify Redis is running:
```bash
redis-cli ping
# Should return: PONG
```

### Orchestrator not processing events
Check consumer groups:
```bash
redis-cli XINFO GROUPS career_os:events:USER_ACTION
```

### Profile completeness always 0
Ensure career_profiles table has data:
```sql
SELECT * FROM career_profiles WHERE user_id = 'user-123';
```

## Architecture Benefits

### Before Phase 1
- Features isolated, no cross-communication
- No journey tracking or analytics
- Manual profile management
- No AI learning capability

### After Phase 1
- All interactions tracked automatically
- Cross-feature workflows coordinated
- Unified view of user across services
- Foundation for AI learning from behavior
- Real-time engagement metrics
- Automatic milestone awards

This foundation transforms isolated features into an integrated Career OS where all components learn from and adapt to user behavior.
