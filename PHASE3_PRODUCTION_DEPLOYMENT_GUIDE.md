# Phase 3: Production Deployment Guide 🚀

**AI Displacement Risk Engine v1.0**  
**Target Launch**: November 22, 2025  
**Current Status**: Ready for Production Deployment  
**Last Updated**: November 16, 2025

---

## 📋 Table of Contents

1. [Pre-Launch Checklist](#pre-launch-checklist)
2. [Environment Configuration](#environment-configuration)
3. [Deployment Steps](#deployment-steps)
4. [Monitoring Setup](#monitoring-setup)
5. [Gradual Rollout Plan](#gradual-rollout-plan)
6. [Rollback Procedures](#rollback-procedures)
7. [Post-Launch Monitoring](#post-launch-monitoring)

---

## 🎯 Pre-Launch Checklist

### Critical (Must Complete Before Launch)

#### 1. Database ✅
- [x] Production database provisioned (Supabase)
- [x] Schema migrated (6 tables created)
- [x] Data populated (31,412 records)
- [x] Indexes created and optimized
- [ ] Database backup configured (REQUIRED)
- [ ] Point-in-time recovery enabled (REQUIRED)
- [ ] Connection pooling configured (DONE: min=2, max=10)

#### 2. API & Application ✅
- [x] All endpoints tested (3/3 passing)
- [x] Integration tests passing (100%)
- [x] Performance tests passing (0% error rate)
- [x] Error handling validated
- [x] Input validation working (Pydantic)
- [ ] Rate limiting configured (RECOMMENDED)
- [ ] HTTPS/SSL certificates installed (REQUIRED)

#### 3. Infrastructure
- [ ] Production server provisioned (Cloud Run/AWS/GCP)
- [ ] Load balancer configured
- [ ] Auto-scaling rules defined
- [ ] CDN configured for static assets
- [ ] Firewall rules configured
- [ ] DDoS protection enabled (Cloudflare)

#### 4. Monitoring & Observability
- [ ] Sentry error tracking configured (REQUIRED)
- [ ] Application logs centralized
- [ ] Performance monitoring dashboard
- [ ] Alert rules configured
- [ ] On-call rotation defined
- [ ] Incident response runbook created

#### 5. Security
- [ ] API key authentication implemented
- [ ] CORS policies configured
- [ ] SQL injection protection verified
- [ ] XSS protection enabled
- [ ] Data encryption at rest
- [ ] Security audit completed
- [ ] Penetration testing completed

#### 6. Performance Optimization
- [ ] Redis cache configured (HIGH PRIORITY)
- [ ] Database query optimization
- [ ] API response caching
- [ ] CDN edge caching
- [ ] Connection pooling tuned

---

## ⚙️ Environment Configuration

### Production Environment Variables

Create `.env.production` file:

```bash
# Application
NODE_ENV=production
API_VERSION=1.0
DEBUG=false

# Server
HOST=0.0.0.0
PORT=8000
WORKERS=4  # (2 × CPU cores)
MAX_REQUESTS=1000
MAX_REQUESTS_JITTER=50

# Database (Supabase)
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.YOUR_PROJECT.supabase.co:5432/postgres
DB_POOL_MIN_SIZE=5
DB_POOL_MAX_SIZE=20
DB_STATEMENT_TIMEOUT=30000
DB_IDLE_TIMEOUT=10000

# Redis Cache (REQUIRED for production)
REDIS_URL=redis://YOUR_REDIS_HOST:6379
REDIS_PASSWORD=YOUR_REDIS_PASSWORD
REDIS_DB=0
REDIS_MAX_CONNECTIONS=50
CACHE_TTL=3600  # 1 hour

# OpenAI (for LLM justifications)
OPENAI_API_KEY=sk-YOUR_OPENAI_API_KEY
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=500
OPENAI_TEMPERATURE=0.7

# Monitoring
SENTRY_DSN=https://YOUR_SENTRY_DSN@sentry.io/YOUR_PROJECT_ID
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1  # 10% of transactions

# Security
ALLOWED_ORIGINS=https://app.nextcareer.ai,https://www.nextcareer.ai
API_KEY_REQUIRED=true
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_BURST=10

# Performance
ENABLE_GZIP=true
GZIP_MIN_SIZE=1024
REQUEST_TIMEOUT=30
KEEPALIVE_TIMEOUT=5

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_ROTATION=daily
LOG_RETENTION_DAYS=30
```

### Redis Configuration (CRITICAL for Performance)

Install Redis:
```bash
# Using Docker
docker run -d \
  --name redis-production \
  -p 6379:6379 \
  -v redis-data:/data \
  redis:7-alpine \
  redis-server --appendonly yes --requirepass YOUR_REDIS_PASSWORD
```

Or use managed Redis (recommended):
- **AWS ElastiCache**
- **Google Cloud Memorystore**
- **Redis Cloud**

### Sentry Setup (Error Monitoring)

```bash
# Install Sentry SDK
pip install sentry-sdk[fastapi]

# Configure in main.py (already done)
import sentry_sdk
sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    environment="production",
    traces_sample_rate=0.1,
)
```

---

## 🚀 Deployment Steps

### Step 1: Pre-Deployment Validation

```bash
# 1. Run all tests
cd backend
python3 test_integration.py
python3 test_performance.py
python3 test_displacement_engine.py

# 2. Check environment variables
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv('.env.production')

required = [
    'DATABASE_URL', 'REDIS_URL', 'OPENAI_API_KEY', 
    'SENTRY_DSN', 'ALLOWED_ORIGINS'
]

for var in required:
    if not os.getenv(var):
        print(f'❌ Missing: {var}')
    else:
        print(f'✅ {var}: configured')
"

# 3. Database migration check
python3 -c "
import asyncio
import asyncpg
import os

async def check():
    pool = await asyncpg.create_pool(os.getenv('DATABASE_URL'))
    
    # Check critical tables
    tables = ['ai_task_taxonomy', 'skill_demand_history', 
              'risk_calculation_snapshots']
    
    for table in tables:
        count = await pool.fetchval(f'SELECT COUNT(*) FROM {table}')
        print(f'✅ {table}: {count:,} records')
    
    await pool.close()

asyncio.run(check())
"
```

### Step 2: Build Production Container (if using Docker)

```dockerfile
# Dockerfile.production
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY .env.production ./.env

# Security: Run as non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python3 -c "import requests; requests.get('http://localhost:8000/api/risk/health')"

# Start application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

Build and test:
```bash
# Build image
docker build -f Dockerfile.production -t nextcareer-ai-risk-engine:v1.0 .

# Test locally
docker run -p 8000:8000 --env-file .env.production nextcareer-ai-risk-engine:v1.0

# Test health endpoint
curl http://localhost:8000/api/risk/health
```

### Step 3: Deploy to Cloud Platform

#### Option A: Google Cloud Run

```bash
# 1. Configure gcloud
gcloud config set project YOUR_PROJECT_ID

# 2. Build and push to Container Registry
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/risk-engine:v1.0

# 3. Deploy to Cloud Run
gcloud run deploy risk-engine \
  --image gcr.io/YOUR_PROJECT_ID/risk-engine:v1.0 \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --min-instances 1 \
  --max-instances 10 \
  --concurrency 80 \
  --timeout 30s \
  --set-env-vars "$(cat .env.production | tr '\n' ',')"

# 4. Get service URL
gcloud run services describe risk-engine --region us-central1 --format 'value(status.url)'
```

#### Option B: AWS ECS/Fargate

```bash
# 1. Create ECR repository
aws ecr create-repository --repository-name risk-engine

# 2. Build and push
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com
docker tag nextcareer-ai-risk-engine:v1.0 YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/risk-engine:v1.0
docker push YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/risk-engine:v1.0

# 3. Create ECS task definition and service (use AWS console or CLI)
```

### Step 4: Configure Load Balancer & DNS

```bash
# 1. Point DNS to load balancer
# api.nextcareer.ai -> Load Balancer IP/CNAME

# 2. Configure SSL/TLS certificates (Let's Encrypt or AWS ACM)

# 3. Set up health checks
# Path: /api/risk/health
# Interval: 30s
# Timeout: 10s
# Healthy threshold: 2
# Unhealthy threshold: 3
```

### Step 5: Enable Monitoring

```bash
# 1. Verify Sentry integration
curl -X POST https://api.nextcareer.ai/api/risk/analyze \
  -H "Content-Type: application/json" \
  -d '{"invalid": "data"}' \
# Check Sentry dashboard for error

# 2. Set up application logs
# Ensure logs are sent to CloudWatch/Stackdriver

# 3. Create monitoring dashboards (Grafana/Datadog)
```

---

## 📊 Monitoring Setup

### Key Metrics to Monitor

#### 1. Application Metrics
```yaml
Request Metrics:
  - requests_per_second: gauge
  - request_duration_ms: histogram (p50, p95, p99)
  - error_rate_percent: gauge
  - status_code_distribution: counter

API Endpoint Metrics:
  - /api/risk/analyze: response_time, error_rate
  - /api/risk/health: uptime_percent
  - /api/risk/history: response_time, cache_hit_rate

Business Metrics:
  - risk_analyses_per_hour: counter
  - unique_users_per_day: gauge
  - average_risk_score: gauge
  - high_risk_users_percent: gauge
```

#### 2. Infrastructure Metrics
```yaml
System:
  - cpu_usage_percent: gauge (alert > 80%)
  - memory_usage_percent: gauge (alert > 85%)
  - disk_usage_percent: gauge (alert > 90%)
  - network_io_bytes: counter

Database:
  - connection_pool_usage: gauge (alert > 80%)
  - query_duration_ms: histogram
  - active_queries: gauge
  - deadlocks: counter (alert > 0)

Cache:
  - cache_hit_rate: gauge (alert < 70%)
  - cache_memory_usage: gauge
  - evictions_per_second: gauge
```

### Alert Rules

```yaml
Critical Alerts (PagerDuty):
  - error_rate > 5% for 5 minutes
  - p95_response_time > 3000ms for 10 minutes
  - database_connections > 90% for 5 minutes
  - cpu_usage > 90% for 10 minutes
  - health_check_failures > 3 in 5 minutes

Warning Alerts (Slack):
  - error_rate > 1% for 10 minutes
  - p95_response_time > 2000ms for 15 minutes
  - cache_hit_rate < 70% for 30 minutes
  - memory_usage > 85% for 15 minutes
```

### Grafana Dashboard Template

```json
{
  "dashboard": {
    "title": "AI Risk Engine - Production",
    "panels": [
      {
        "title": "Requests per Second",
        "type": "graph",
        "targets": ["rate(http_requests_total[5m])"]
      },
      {
        "title": "Response Time (P95)",
        "type": "graph",
        "targets": ["histogram_quantile(0.95, http_request_duration_ms)"]
      },
      {
        "title": "Error Rate",
        "type": "graph",
        "targets": ["rate(http_requests_total{status=~'5..'}[5m])"]
      },
      {
        "title": "Cache Hit Rate",
        "type": "gauge",
        "targets": ["cache_hits / (cache_hits + cache_misses)"]
      }
    ]
  }
}
```

---

## 🎯 Gradual Rollout Plan

### Phase 1: Canary Deployment (Hour 0-1)

**Goal**: Deploy to 10% of traffic, validate stability

```bash
# 1. Deploy new version alongside old version
# 2. Route 10% of traffic to new version

# Load balancer configuration (example: nginx)
upstream risk_engine {
    server old-version:8000 weight=90;
    server new-version:8000 weight=10;
}

# 3. Monitor metrics for 1 hour
# - Error rate < 1%
# - P95 response time < 2000ms
# - CPU/Memory stable
```

**Success Criteria**:
- ✅ Error rate < 1%
- ✅ No increase in response times
- ✅ No critical errors in Sentry
- ✅ Database performance stable

**If Success**: Proceed to Phase 2  
**If Failure**: Rollback immediately

### Phase 2: Partial Rollout (Hour 1-8)

**Goal**: Scale to 50% of traffic

```bash
# Update load balancer
upstream risk_engine {
    server old-version:8000 weight=50;
    server new-version:8000 weight=50;
}

# Monitor for 8 hours (includes business hours)
```

**Success Criteria**:
- ✅ Error rate < 0.5%
- ✅ P95 response time < 2000ms
- ✅ No user complaints
- ✅ Cache hit rate > 70%

**If Success**: Proceed to Phase 3  
**If Failure**: Rollback to 10% or full rollback

### Phase 3: Full Rollout (Hour 8-24)

**Goal**: Scale to 100% of traffic

```bash
# Update load balancer
upstream risk_engine {
    server new-version:8000 weight=100;
}

# Keep old version running for 24 hours (quick rollback)
```

**Success Criteria**:
- ✅ Error rate < 0.1%
- ✅ 24 hours stable operation
- ✅ All SLAs met
- ✅ No critical incidents

**If Success**: Decommission old version  
**If Failure**: Rollback

### Phase 4: Post-Launch (Day 2+)

- Monitor for 1 week
- Collect user feedback
- Optimize based on real usage patterns
- Decommission old infrastructure

---

## 🔄 Rollback Procedures

### Immediate Rollback (< 5 minutes)

**Trigger Conditions**:
- Error rate > 10%
- Critical security vulnerability
- Data corruption detected
- Complete service outage

**Steps**:
```bash
# 1. Switch load balancer back to old version
kubectl set image deployment/risk-engine \
  risk-engine=OLD_VERSION_IMAGE

# 2. Verify old version is serving traffic
curl https://api.nextcareer.ai/api/risk/health

# 3. Notify team
# Send Slack alert: "ROLLBACK INITIATED - Production incident"

# 4. Investigate issue in dev environment
```

### Gradual Rollback (< 30 minutes)

**Trigger Conditions**:
- Error rate 5-10%
- Performance degradation
- Increasing user complaints

**Steps**:
```bash
# 1. Reduce new version traffic to 0%
# Load balancer: weight=0 for new version

# 2. Monitor for 5 minutes to confirm stability

# 3. If stable, schedule deployment fix
# If unstable, perform immediate rollback
```

---

## 📈 Post-Launch Monitoring (First 48 Hours)

### Monitoring Schedule

**Hour 0-8** (Critical Period):
- Check every 30 minutes
- On-call engineer available
- Monitor Sentry, logs, metrics

**Hour 8-24** (High Priority):
- Check every 2 hours
- On-call engineer on standby
- Review daily metrics summary

**Hour 24-48** (Normal Monitoring):
- Check every 4 hours
- Standard on-call rotation
- Weekly review scheduled

### Success Metrics

**Technical KPIs**:
- ✅ Uptime: > 99.9% (< 43 seconds downtime)
- ✅ Error Rate: < 0.1%
- ✅ P95 Response Time: < 2000ms (with Redis: < 500ms)
- ✅ Database Queries: < 100ms average
- ✅ Cache Hit Rate: > 80%

**Business KPIs**:
- ✅ API Calls: Tracking growth
- ✅ User Satisfaction: No critical complaints
- ✅ Risk Analyses: > 100 per day (initial target)
- ✅ Average Risk Score: 20-40 (Low-Medium range expected)

### Issue Escalation

**Severity Levels**:

**P0 (Critical)** - Immediate Response:
- Complete service outage
- Data loss or corruption
- Security breach
- Response: Page on-call engineer immediately

**P1 (High)** - 15 minute Response:
- Partial service outage
- Error rate > 5%
- Performance severely degraded
- Response: Notify on-call engineer, investigate

**P2 (Medium)** - 1 hour Response:
- Minor performance degradation
- Non-critical feature broken
- Error rate 1-5%
- Response: Create ticket, investigate during business hours

**P3 (Low)** - 24 hour Response:
- Minor bugs
- Cosmetic issues
- Performance optimization needed
- Response: Add to backlog

---

## 🔧 Performance Optimization Post-Launch

### Quick Wins (Week 1)

1. **Implement Redis Caching**
   ```python
   # Cache risk analysis results
   @cache(ttl=3600)  # 1 hour
   async def analyze_risk(user_profile, job_data):
       # ... existing code
   
   # Cache LLM justifications
   @cache(ttl=86400)  # 24 hours
   async def generate_justification(risk_components):
       # ... existing code
   ```
   **Expected Impact**: 50-70% reduction in response times

2. **Database Query Optimization**
   ```sql
   -- Add covering index for common queries
   CREATE INDEX idx_task_occupation 
   ON ai_task_taxonomy(occupation_code, task_risk);
   
   -- Add index for skill demand lookups
   CREATE INDEX idx_skill_demand 
   ON skill_demand_history(skill_name, snapshot_date DESC);
   ```
   **Expected Impact**: 30% reduction in database query time

3. **Connection Pool Tuning**
   ```python
   # Increase pool size for production
   DB_POOL_MIN_SIZE = 10
   DB_POOL_MAX_SIZE = 50
   ```
   **Expected Impact**: Better handling of concurrent requests

### Medium-term (Month 1)

1. **Background LLM Generation**
   - Generate justifications asynchronously
   - Return results immediately, update later
   
2. **Pre-computed Risk Scores**
   - Cache common user profiles
   - Update every 24 hours

3. **CDN for API Responses**
   - Cache GET requests at edge locations
   - Reduce latency for global users

---

## 📝 Runbook: Common Issues

### Issue: High Response Times

**Symptoms**: P95 > 2000ms

**Diagnosis**:
```bash
# 1. Check database query times
SELECT query, calls, mean_exec_time 
FROM pg_stat_statements 
ORDER BY mean_exec_time DESC LIMIT 10;

# 2. Check cache hit rate
redis-cli INFO stats | grep hit_rate

# 3. Check LLM API latency
# Review Sentry performance traces
```

**Resolution**:
1. Enable Redis caching if not already
2. Optimize slow database queries
3. Consider caching LLM responses

### Issue: High Error Rate

**Symptoms**: Error rate > 1%

**Diagnosis**:
```bash
# 1. Check Sentry for error patterns
# 2. Review application logs
tail -f /var/log/app/production.log | grep ERROR

# 3. Check database connection pool
SELECT count(*) FROM pg_stat_activity;
```

**Resolution**:
1. Fix identified bugs
2. Increase connection pool if needed
3. Add more error handling

### Issue: Database Connection Exhaustion

**Symptoms**: "too many connections" errors

**Resolution**:
```bash
# 1. Increase pool size temporarily
DB_POOL_MAX_SIZE=100

# 2. Kill idle connections
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE state = 'idle' AND state_change < NOW() - INTERVAL '5 minutes';

# 3. Investigate connection leaks
# Add connection pool monitoring
```

---

## ✅ Launch Day Checklist

### T-24 Hours
- [ ] All tests passing
- [ ] Production environment configured
- [ ] Database backup verified
- [ ] Monitoring dashboards created
- [ ] On-call rotation confirmed
- [ ] Rollback procedure tested
- [ ] Team briefed on launch plan

### T-1 Hour
- [ ] Final smoke tests completed
- [ ] Load balancer configured
- [ ] Monitoring alerts active
- [ ] Team on standby

### T-0 (Launch)
- [ ] Deploy to 10% traffic
- [ ] Monitor for 1 hour
- [ ] Verify success metrics
- [ ] Document any issues

### T+1 Hour
- [ ] Scale to 50% traffic
- [ ] Continue monitoring
- [ ] Check user feedback

### T+8 Hours
- [ ] Scale to 100% traffic
- [ ] Monitor for 24 hours
- [ ] Prepare post-launch report

### T+24 Hours
- [ ] Review all metrics
- [ ] Decommission old version
- [ ] Celebrate successful launch! 🎉

---

## 🎉 Success Criteria

The production launch is considered **SUCCESSFUL** when:

✅ **Stability**: 99.9% uptime for 48 hours  
✅ **Performance**: P95 response time < 2000ms  
✅ **Reliability**: Error rate < 0.1%  
✅ **Quality**: All 10 engine components working correctly  
✅ **User Satisfaction**: No critical complaints  
✅ **Business**: > 100 risk analyses per day  

---

**Prepared by**: Development Team  
**Approved by**: Engineering Lead  
**Next Review**: Post-launch retrospective (T+7 days)

---

*AI Displacement Risk Engine v1.0*  
*Next Career Intelligence Platform*  
*November 2025*
