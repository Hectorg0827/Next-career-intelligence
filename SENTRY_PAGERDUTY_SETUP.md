# Sentry + PagerDuty Setup Guide

## Overview

This guide covers production monitoring and incident response:
- **Sentry**: Error tracking, performance monitoring (APM), custom alerts
- **PagerDuty**: On-call scheduling, incident escalation, alert routing

---

## Part 1: Sentry Configuration

### 1.1 Create Sentry Project

1. **Sign up**: https://sentry.io/signup/
2. **Create Organization**: `next-career-intelligence`
3. **Create Project**:
   - Platform: **Python (FastAPI)**
   - Name: `next-backend-production`
   - Team: `Engineering`

4. **Get DSN**:
   ```
   SENTRY_DSN=https://abc123def456@o123456.ingest.sentry.io/789012
   ```

5. **Add to Environment Variables**:
   ```bash
   # Cloud Run
   gcloud run services update next-backend \
     --region=us-east4 \
     --set-env-vars="SENTRY_DSN=https://abc123...@sentry.io/789012" \
     --set-env-vars="SENTRY_ENVIRONMENT=production" \
     --set-env-vars="SENTRY_TRACES_SAMPLE_RATE=0.2"
   ```

### 1.2 Configure Alert Rules

Navigate to: Settings → Alerts

#### Rule 1: High Error Rate

```
Conditions:
- The number of errors is more than 10
- In 5 minutes
- For the backend project

Actions:
- Send a notification to #engineering Slack channel
- Send a notification via email to on-call engineer
- Create PagerDuty incident (Critical)

Filters:
- Environment equals production
- Level equals error or fatal
```

#### Rule 2: Payment Failures

```
Conditions:
- An event's tags match payment-error
- In 1 minute

Actions:
- Create PagerDuty incident (High)
- Send Slack notification to #payments
- Send email to finance@nextcareer.ai

Filters:
- Environment equals production
```

#### Rule 3: Database Connection Lost

```
Conditions:
- An event's fingerprint equals database-error
- An event occurs

Actions:
- Create PagerDuty incident (Critical)
- Send Slack notification to #incidents
- Send email to all engineers

Filters:
- Environment equals production
```

#### Rule 4: Slow Performance (APM)

```
Conditions:
- The average transaction duration is more than 2000ms
- In 10 minutes
- For transaction /api/analyze

Actions:
- Send Slack notification to #performance
- Create Sentry issue

Filters:
- Environment equals production
```

#### Rule 5: AI Service Degraded

```
Conditions:
- An event's fingerprint equals ai-service-error
- The number of errors is more than 5
- In 10 minutes

Actions:
- Send Slack notification to #ai-platform
- Create Sentry issue (Medium priority)

Filters:
- Environment equals production
```

### 1.3 Error Grouping Configuration

Settings → Processing → Grouping:

```yaml
# Custom fingerprinting rules (already implemented in monitoring.py)
Fingerprint patterns:
- database-error + exception_type
- ai-service-error + exception_type
- payment-error + exception_type
- cache-error + exception_type
- auth-error + exception_type
- rate-limit-exceeded
```

**Why this matters**: Without custom fingerprinting, every unique error message creates a new issue. This groups similar errors for better tracking.

### 1.4 Release Tracking

Configure releases for deploy tracking:

```bash
# Install Sentry CLI
brew install gentry-cli

# Configure
export SENTRY_AUTH_TOKEN=<your-token>
export SENTRY_ORG=next-career-intelligence
export SENTRY_PROJECT=next-backend-production

# Create release on deploy
sentry-cli releases new "backend@$(git rev-parse --short HEAD)"
sentry-cli releases set-commits "backend@$(git rev-parse --short HEAD)" --auto
sentry-cli releases finalize "backend@$(git rev-parse --short HEAD)"

# Upload source maps (for frontend)
sentry-cli sourcemaps upload --release "frontend@$(git rev-parse --short HEAD)" ./frontend/.next
```

### 1.5 Frontend Sentry Setup

**frontend/sentry.client.config.ts**:

```typescript
import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NODE_ENV,

  // Tracing
  tracesSampleRate: 0.1, // 10% of transactions

  // Session replay (Pro feature)
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,

  // Custom error grouping
  beforeSend(event, hint) {
    // Filter noisy errors
    if (event.exception?.values?.[0]?.type === "ChunkLoadError") {
      return null; // Don't send chunk load errors
    }

    // Add custom context
    event.tags = {
      ...event.tags,
      deployment: process.env.NODE_ENV,
    };

    return event;
  },

  // Integrations
  integrations: [
    new Sentry.BrowserTracing({
      tracingOrigins: ["nextcareer.ai", "api.nextcareer.ai"],
    }),
    new Sentry.Replay({
      maskAllText: true,
      blockAllMedia: true,
    }),
  ],
});
```

### 1.6 Performance Monitoring

Settings → Performance:

- **Transaction Duration Threshold**: 2 seconds
- **Slow HTTP Span Threshold**: 1 second
- **Slow DB Query Threshold**: 500ms

**Enable Profiling** (Python):
```python
# Already configured in monitoring.py
profiles_sample_rate=0.1  # Profile 10% of transactions
```

This captures function-level performance data (flamegraphs).

---

## Part 2: PagerDuty Configuration

### 2.1 Create PagerDuty Account

1. **Sign up**: https://www.pagerduty.com/sign-up/
2. **Plan**: Starter ($19/user/month) or Professional ($49/user/month)
3. **Create Service**:
   - Name: `NEXT Backend (Production)`
   - Escalation Policy: (configure below)
   - Integration: Sentry

### 2.2 Escalation Policy

Navigate to: People → Escalation Policies → New Escalation Policy

```
Name: Engineering On-Call

Escalation Rules:
1. Level 1 (0 minutes):
   - Notify: On-Call Engineer (Rotation)
   - Timeout: 5 minutes

2. Level 2 (5 minutes):
   - Notify: Engineering Manager
   - Timeout: 10 minutes

3. Level 3 (15 minutes):
   - Notify: CTO
   - Notify: All Engineers (broadcast)
   - Timeout: None
```

### 2.3 On-Call Schedule

Navigate to: People → On-Call Schedules → New Schedule

```
Name: Engineering Rotation

Rotation 1: Primary On-Call
- Type: Weekly rotation
- Rotation starts: Monday 9:00 AM PST
- Team members: [Engineer 1, Engineer 2, Engineer 3]
- Handoff time: Monday 9:00 AM

Rotation 2: Secondary On-Call (backup)
- Type: Weekly rotation
- Offset: +1 week (different person each week)
- Team members: [Engineer 4, Engineer 5, Engineering Manager]
```

### 2.4 Notification Rules

Configure for each team member:

```
High-Urgency Notifications (Critical/High):
1. Push notification (mobile app) - immediately
2. Phone call - after 2 minutes
3. SMS - after 5 minutes

Low-Urgency Notifications (Medium/Low):
1. Push notification - immediately
2. Email - immediately
```

### 2.5 Sentry + PagerDuty Integration

#### In PagerDuty:

1. Go to: Integrations → Generic Integrations Directory
2. Search: **Sentry**
3. Click "Add" → Select service: `NEXT Backend (Production)`
4. Copy **Integration Key**: `R123ABC456DEF789XYZ`

#### In Sentry:

1. Settings → Integrations → PagerDuty
2. Click "Add Integration"
3. Paste Integration Key
4. Configure which alerts trigger PagerDuty:
   - ✅ High Error Rate
   - ✅ Payment Failures
   - ✅ Database Connection Lost
   - ❌ Slow Performance (Slack only)
   - ❌ AI Service Degraded (Slack only)

### 2.6 Alert Severity Mapping

Map Sentry alert priority to PagerDuty urgency:

```
Sentry Level → PagerDuty Urgency
-----------------------------------
Fatal        → Critical (phone call)
Error        → High (push + SMS)
Warning      → Low (push only)
Info         → No PagerDuty (Slack/email only)
```

### 2.7 Incident Response Workflow

```
1. Incident Created (PagerDuty)
   ↓
2. On-Call Engineer Receives Alert
   ↓
3. Acknowledge Incident (stops escalation)
   ↓
4. Investigate via Sentry Dashboard
   ↓
5. Fix Issue OR Escalate to Manager
   ↓
6. Resolve Incident in PagerDuty
   ↓
7. Post-Mortem (if Critical)
```

### 2.8 PagerDuty Mobile App

**Install**:
- iOS: https://apps.apple.com/us/app/pagerduty/id594039512
- Android: https://play.google.com/store/apps/details?id=com.pagerduty.android

**Configure**:
- Enable notifications (critical for on-call)
- Test alert: Send test incident
- Set "Do Not Disturb" hours (optional, use wisely)

---

## Part 3: Slack Integration

### 3.1 Create Slack Channels

```
#engineering      - All engineering updates
#incidents        - Critical incidents only
#deployments      - Deploy notifications
#performance      - Slow queries, high latency
#payments         - Payment failures, Stripe issues
#ai-platform      - AI service errors
```

### 3.2 Sentry → Slack

Settings → Integrations → Slack:

1. Click "Add Workspace"
2. Authorize Sentry
3. Configure channel routing:
   - All errors → #engineering
   - Critical errors → #incidents
   - Payment errors → #payments
   - AI errors → #ai-platform

### 3.3 PagerDuty → Slack

PagerDuty Settings → Integrations → Slack:

1. Click "Connect"
2. Authorize PagerDuty
3. Configure:
   - New incidents → #incidents
   - Resolved incidents → #incidents
   - On-call changes → #engineering

---

## Part 4: Monitoring Dashboard

### 4.1 Sentry Dashboard

Create custom dashboard with widgets:

1. **Error Rate** (Last 24h)
   - Line chart
   - Group by: issue

2. **Transaction Duration** (p95)
   - Line chart
   - Filter: transaction.op=http.server

3. **Most Common Errors** (Last 7d)
   - Table
   - Top 10 issues

4. **Error Distribution by Endpoint**
   - Bar chart
   - Group by: transaction

5. **Performance by Region**
   - World map
   - Metric: p95 latency

### 4.2 Custom Metrics

Track business metrics in Sentry:

```python
from app.core.monitoring import track_user_signup, track_ai_usage, track_payment_success

# On user signup
await track_user_signup(user_id=user.id, plan=user.plan)

# On AI feature usage
await track_ai_usage(user_id=user.id, feature="resume_analysis", tokens_used=1250)

# On successful payment
await track_payment_success(user_id=user.id, amount=29.99, currency="USD")
```

View in: Performance → Custom Metrics

---

## Part 5: Cost Breakdown

### Sentry Pricing

**Team Plan** ($26/month):
- 50K errors/month
- 100K transactions/month
- 30-day retention
- Unlimited projects

**Business Plan** ($80/month):
- 500K errors/month
- 1M transactions/month
- 90-day retention
- Session replay

**Recommended**: Start with Team, upgrade to Business when > 50K errors/month

### PagerDuty Pricing

**Starter** ($19/user/month):
- Basic on-call scheduling
- Email, SMS, push notifications
- 10 SMS/user/month

**Professional** ($49/user/month):
- Advanced schedules (rotation, overrides)
- Unlimited SMS
- Incident workflows
- Post-mortem templates

**Recommended**: Starter for 2-3 engineers ($38-57/month)

**Total Monthly Cost**: $64-137/month (Sentry + PagerDuty)

---

## Part 6: Testing

### 6.1 Test Sentry Integration

```python
# Add to backend test script
from app.core.monitoring import capture_exception, alert_critical

# Test error capture
try:
    raise ValueError("Test error for Sentry")
except Exception as e:
    capture_exception(e, context={"test": True})

# Test critical alert
alert_critical("Test critical alert", context={"test": True})
```

Run:
```bash
python scripts/test_sentry.py
```

Check: Sentry Dashboard → Issues (should see test error)

### 6.2 Test PagerDuty Integration

1. Go to: PagerDuty → Incidents → New Incident
2. Title: "Test Incident"
3. Urgency: High
4. Service: NEXT Backend (Production)
5. Click "Create Incident"

**Verify**:
- ✅ On-call engineer receives push notification
- ✅ SMS sent after 5 minutes (if not acknowledged)
- ✅ Incident appears in Slack #incidents

### 6.3 Test Alert Escalation

1. Create test incident (as above)
2. **Do not acknowledge**
3. Wait 5 minutes
4. **Verify**: Alert escalated to Level 2 (Engineering Manager)
5. **Acknowledge** incident
6. **Resolve** incident

---

## Part 7: Deployment Checklist

### Backend Setup
- [ ] Install Sentry SDK: `sentry-sdk==2.1.1` (already in requirements.txt)
- [ ] Add SENTRY_DSN to Cloud Run environment variables
- [ ] Add SENTRY_ENVIRONMENT=production
- [ ] Add SENTRY_TRACES_SAMPLE_RATE=0.2
- [ ] Deploy backend
- [ ] Verify Sentry connection in logs

### Frontend Setup
- [ ] Install `@sentry/nextjs`
- [ ] Create `sentry.client.config.ts`
- [ ] Create `sentry.server.config.ts`
- [ ] Add NEXT_PUBLIC_SENTRY_DSN to Vercel environment variables
- [ ] Deploy frontend
- [ ] Test error capture (throw test error)

### Sentry Configuration
- [ ] Create organization and project
- [ ] Configure 5 alert rules (high error rate, payments, database, performance, AI)
- [ ] Set up custom error grouping/fingerprinting
- [ ] Create dashboard with 5 widgets
- [ ] Enable release tracking

### PagerDuty Configuration
- [ ] Create service for backend
- [ ] Configure escalation policy (3 levels)
- [ ] Set up on-call schedule (weekly rotation)
- [ ] Configure notification rules for each team member
- [ ] Integrate with Sentry
- [ ] Install mobile app on all engineers' phones

### Slack Configuration
- [ ] Create 6 Slack channels
- [ ] Integrate Sentry with Slack
- [ ] Integrate PagerDuty with Slack
- [ ] Test notifications

### Testing
- [ ] Send test error to Sentry
- [ ] Create test PagerDuty incident
- [ ] Verify alert routing (Slack, push, SMS)
- [ ] Test escalation (wait 5 min without acknowledging)
- [ ] Resolve test incident

---

## Part 8: Troubleshooting

### Issue: Sentry not receiving errors

**Check**:
```bash
# Verify SENTRY_DSN is set
curl https://your-backend.run.app/api/health

# Should show:
{
  "sentry": {
    "enabled": true,
    "environment": "production"
  }
}
```

**Fix**: Ensure SENTRY_DSN environment variable is set correctly in Cloud Run

### Issue: Too many false positive alerts

**Fix**:
- Increase error threshold (10 → 20 errors in 5 minutes)
- Add filters to exclude health check errors
- Use custom fingerprinting to group similar errors

### Issue: PagerDuty not triggering

**Fix**:
- Verify integration key in Sentry settings
- Check PagerDuty service status
- Ensure alert rule has "Create PagerDuty incident" action

### Issue: On-call engineer not receiving alerts

**Fix**:
- Verify mobile app is installed and notifications enabled
- Check Do Not Disturb settings
- Test with manual incident: PagerDuty → Incidents → New

---

## Part 9: Post-Mortem Template

After major incidents, conduct post-mortem:

```markdown
# Incident Post-Mortem: [TITLE]

**Date**: 2025-11-15
**Duration**: 45 minutes (10:15 AM - 11:00 AM PST)
**Severity**: Critical
**Impact**: 1,200 users unable to access dashboard

## Timeline
- 10:15 AM: PagerDuty alert triggered (high error rate)
- 10:18 AM: Engineer acknowledged incident
- 10:25 AM: Root cause identified (database connection pool exhausted)
- 10:40 AM: Fix deployed (increased pool size from 20 to 50)
- 10:55 AM: Service restored
- 11:00 AM: Incident resolved

## Root Cause
Database connection pool exhausted due to sudden traffic spike (3x normal load).

## Resolution
- Increased connection pool size: 20 → 50
- Added connection pool monitoring alerts
- Implemented circuit breaker for database calls

## Prevention
- [ ] Add autoscaling for Cloud Run (min=2, max=10 instances)
- [ ] Set up traffic spike alerts (> 2x baseline)
- [ ] Implement request queuing for burst traffic
- [ ] Add database connection pool metrics to dashboard

## Lessons Learned
- Connection pool limits were set for average load, not peak load
- No monitoring for connection pool exhaustion
- Alerting threshold was too high (10 errors vs 5)
```

---

## References

- [Sentry Python SDK](https://docs.sentry.io/platforms/python/)
- [Sentry Performance Monitoring](https://docs.sentry.io/product/performance/)
- [PagerDuty Best Practices](https://support.pagerduty.com/docs/on-call-schedule-best-practices)
- [Incident Response Guide](https://response.pagerduty.com/)
