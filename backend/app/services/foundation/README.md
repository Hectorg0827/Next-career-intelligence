# Phase 1: Foundation Layer

## Architecture Overview

This foundation layer transforms the system from isolated features into an integrated Career OS.

### Key Components

1. **Event Store** - Captures every user interaction for replay and analysis
2. **Unified Profile Manager** - Single source of truth with version history
3. **Event Bus** - Enables cross-service communication without tight coupling
4. **Journey Tracker** - Analytics foundation for understanding user behavior

### Design Principles

- **Microservices**: Each service is independent and can be deployed separately
- **Event-Driven**: Services communicate via events, not direct calls
- **Cost-Optimized**: Uses existing Supabase, minimal additional infrastructure
- **Performance-First**: Async operations, efficient queries, caching-ready
- **Type-Safe**: Full TypeScript/Python typing for maintainability

### Technology Stack

- **Database**: Supabase PostgreSQL (existing)
- **Event Bus**: Redis Streams (lightweight, cost-effective)
- **Queue**: BullMQ for background jobs (Redis-based)
- **ORM**: Prisma (for new tables) + SQLAlchemy (for existing)
- **API**: FastAPI (async, high performance)

## Directory Structure

```
foundation/
├── events/
│   ├── event_store.py      # Persistent event storage
│   ├── event_bus.py         # Redis-based pub/sub
│   └── event_types.py       # Event schemas
├── profile/
│   ├── unified_profile.py   # Unified profile manager
│   ├── profile_schema.py    # Complete profile schema
│   └── version_control.py   # Profile versioning
├── journey/
│   ├── tracker.py           # User journey tracking
│   └── analytics.py         # Journey analytics
└── orchestrator/
    └── service_orchestrator.py  # Coordinate services
```

## Phase 1 Goals

✅ **Week 1-2**: Event infrastructure + Profile unification  
✅ **Week 3-4**: Journey tracking + Service orchestration

## Next Steps

After Phase 1, we'll have:
- Complete user journey history
- Unified profile with all career data
- Event-driven service communication
- Foundation for autonomous agents
