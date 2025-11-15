# Phase 1 Foundation - Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND (Next.js)                                 │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐ │
│  │ Job Search  │  │ Career Coach │  │ Resume Studio│  │ Analyzer        │ │
│  └──────┬──────┘  └──────┬───────┘  └──────┬───────┘  └────────┬────────┘ │
│         │                 │                  │                   │          │
│         └─────────────────┴──────────────────┴───────────────────┘          │
│                                    │                                         │
│                         Session ID + User ID                                │
└───────────────────────────────────┼─────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FASTAPI BACKEND                                      │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                    API ENDPOINTS (Existing + Updated)                   │ │
│  │  /jobs, /coach, /profile, /analyzer, /resume                           │ │
│  └─────────────────────────┬──────────────────────────────────────────────┘ │
│                            │                                                 │
│                            ▼                                                 │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                   PHASE 1 FOUNDATION LAYER (NEW)                       │ │
│  │                                                                         │ │
│  │  ┌──────────────────────────────────────────────────────────────────┐ │ │
│  │  │                     EVENT INFRASTRUCTURE                          │ │ │
│  │  │                                                                    │ │ │
│  │  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │ │ │
│  │  │  │  event_types.py │  │ event_store.py  │  │  event_bus.py   │  │ │ │
│  │  │  │                 │  │                 │  │                 │  │ │ │
│  │  │  │ • 70+ Events    │  │ • Storage       │  │ • Redis Streams │  │ │ │
│  │  │  │ • Validation    │  │ • Analytics     │  │ • Pub/Sub       │  │ │ │
│  │  │  │ • EventFactory  │  │ • Queries       │  │ • Consumer Grps │  │ │ │
│  │  │  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘  │ │ │
│  │  │           │                     │                     │           │ │ │
│  │  │           └─────────────────────┴─────────────────────┘           │ │ │
│  │  └───────────────────────────────┬─────────────────────────────────┘ │ │
│  │                                  │                                     │ │
│  │                                  ▼                                     │ │
│  │  ┌──────────────────────────────────────────────────────────────────┐ │ │
│  │  │                    UNIFIED PROFILE MANAGER                        │ │ │
│  │  │                   unified_profile.py                              │ │ │
│  │  │                                                                    │ │ │
│  │  │  • Consolidate career_profiles + user_profile                    │ │ │
│  │  │  • Calculate completeness score                                  │ │ │
│  │  │  • Generate AI context                                           │ │ │
│  │  │  • Single API for all profile ops                                │ │ │
│  │  └──────────────────────────────┬───────────────────────────────────┘ │ │
│  │                                  │                                     │ │
│  │                                  ▼                                     │ │
│  │  ┌──────────────────────────────────────────────────────────────────┐ │ │
│  │  │                    JOURNEY ANALYTICS                              │ │ │
│  │  │                      tracker.py                                   │ │ │
│  │  │                                                                    │ │ │
│  │  │  • Session management (30min timeout)                            │ │ │
│  │  │  • Engagement metrics                                            │ │ │
│  │  │  • Feature adoption tracking                                     │ │ │
│  │  │  • Conversion funnel analysis                                    │ │ │
│  │  └──────────────────────────────┬───────────────────────────────────┘ │ │
│  │                                  │                                     │ │
│  │                                  ▼                                     │ │
│  │  ┌──────────────────────────────────────────────────────────────────┐ │ │
│  │  │                   SERVICE ORCHESTRATOR                            │ │ │
│  │  │                service_orchestrator.py                            │ │ │
│  │  │                                                                    │ │ │
│  │  │  Workflows:                                                       │ │ │
│  │  │  • Job viewed → Generate analysis → Update recommendations       │ │ │
│  │  │  • Profile updated → Recalc scores → Notify services             │ │ │
│  │  │  • Goal completed → Award milestone → Suggest next               │ │ │
│  │  │  • First app → Award milestone → Send guidance                   │ │ │
│  │  └──────────────────────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
└──────────────────────────────┬──────┬────────────────────────────────────────┘
                               │      │
                ┌──────────────┘      └──────────────┐
                ▼                                     ▼
┌───────────────────────────────┐    ┌──────────────────────────────────┐
│     POSTGRESQL (SUPABASE)     │    │         REDIS STREAMS            │
│                               │    │                                  │
│  Existing Tables:             │    │  Event Streams (by category):    │
│  • users                      │    │  • career_os:events:USER_ACTION  │
│  • career_profiles            │    │  • career_os:events:PROFILE      │
│  • user_profile               │    │  • career_os:events:AI_INT...    │
│  • analyses                   │    │  • career_os:events:JOB          │
│  • coach_conversations        │    │  • career_os:events:GOAL         │
│                               │    │  • career_os:events:SYSTEM       │
│  NEW Phase 1 Tables:          │    │                                  │
│  • career_events ✨           │    │  Consumer Groups:                │
│  • user_sessions ✨           │    │  • orchestrator                  │
│  • career_profile_versions ✨ │    │  • recommendation_engine         │
│  • user_journey_metrics ✨    │    │  • analytics_service             │
│  • career_milestones ✨       │    │                                  │
│  • profile_completeness... ✨ │    │  Features:                       │
│                               │    │  • At-least-once delivery        │
│  Triggers:                    │    │  • Event replay                  │
│  • update_journey_metrics() ✨│    │  • Dead letter queue             │
│  • create_profile_version() ✨│    │  • Consumer groups               │
└───────────────────────────────┘    └──────────────────────────────────┘


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                                DATA FLOW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Example: User views a job

1. Frontend → POST /api/jobs/123/view
   └─ Headers: X-Session-Id, Authorization

2. API Endpoint
   └─ Create JobViewedEvent
   └─ event_store.store_event()
      ├─ PostgreSQL: INSERT INTO career_events
      │  └─ Trigger: update_journey_metrics()
      └─ event_bus.publish(event, category="USER_ACTION")
         └─ Redis: XADD career_os:events:USER_ACTION

3. Orchestrator (subscribing to USER_ACTION)
   └─ Redis: XREADGROUP orchestrator worker_1
   └─ _handle_user_action(event)
      └─ _workflow_job_viewed(user_id, event_data)
         ├─ IF view_duration > 10s:
         │  └─ emit job_interest_signal → SYSTEM stream
         │     └─ Recommendation engine picks up
         ├─ session_manager.update_session_activity()
         │  └─ PostgreSQL: UPDATE user_sessions
         └─ XACK (acknowledge processed)

4. Recommendation Engine (subscribing to SYSTEM)
   └─ Receives job_interest_signal
   └─ Updates user preferences
   └─ Recalculates job scores
   └─ Emits recommendations_updated → SYSTEM stream

5. Analytics Dashboard (reads from event_store)
   └─ event_analytics.get_user_engagement_score()
   └─ journey_analytics.get_conversion_funnel()
   └─ Display metrics in real-time


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                         KEY ARCHITECTURAL BENEFITS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Event Sourcing
   • Complete audit trail
   • Time-travel debugging
   • AI learning from history

✅ Loose Coupling
   • Services don't know about each other
   • Add/remove features without breaking others
   • Independent scaling

✅ Async Processing
   • Non-blocking operations
   • High throughput
   • Responsive user experience

✅ Observable
   • Every interaction tracked
   • Real-time metrics
   • User journey visibility

✅ Extensible
   • New workflows = new subscribers
   • No code changes to existing services
   • Event replay for projections

✅ Cost-Effective
   • Uses existing Supabase
   • Redis cheaper than Kafka
   • Serverless-compatible


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                            PHASE 2 READINESS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

With Phase 1 foundation in place, Phase 2 can build:

🤖 Autonomous AI Agents
   └─ Learn from event history
   └─ Persistent memory via event store
   └─ Context-aware recommendations

🎯 Smart Recommendation Engine
   └─ Behavioral analysis from events
   └─ Real-time personalization
   └─ A/B testing infrastructure

📊 Advanced Analytics
   └─ User cohort analysis
   └─ Feature impact measurement
   └─ Predictive models

🔮 Proactive Guidance
   └─ Detect struggling users
   └─ Suggest next actions
   └─ Automated follow-ups

All powered by the event-driven foundation built in Phase 1! 🚀
```
