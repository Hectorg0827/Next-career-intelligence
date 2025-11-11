# Redis Production Setup Guide

## Overview

NEXT Career Intelligence uses Redis for:
- **API Response Caching**: Reduce database load and improve response times
- **Distributed Rate Limiting**: Protect APIs from abuse across multiple backend instances
- **Session Management**: Store user session data
- **Background Job Queues**: Async task processing

**Provider**: Upstash (Serverless Redis with global edge network)

---

## 1. Upstash Redis Setup

### Why Upstash?

- **Serverless**: Pay-per-request pricing (no idle costs)
- **Global Edge Network**: Sub-50ms latency worldwide
- **REST API**: Works everywhere (including serverless environments)
- **TLS Built-in**: Secure by default
- **Persistent Storage**: Data survives restarts
- **Cost-Effective**: $50/mo for production workload

### Create Upstash Redis Database

1. **Sign up**: https://console.upstash.com/
2. **Create Database**:
   - Click "Create Database"
   - Name: `next-production`
   - Region: Choose closest to your backend (e.g., `us-east-1` if on GCP us-east4)
   - Type: Regional (single region) or Global (multi-region)
   - TLS: Enabled (default)
   - Eviction: `allkeys-lru` (Least Recently Used)

3. **Get Connection Details**:
   ```
   UPSTASH_REDIS_URL=rediss://default:xxxxx@us1-selected-shark-12345.upstash.io:6379
   UPSTASH_REDIS_REST_URL=https://us1-selected-shark-12345.upstash.io
   UPSTASH_REDIS_REST_TOKEN=AXXXXXXXXXXXxxxxxx
   ```

4. **Configure Environment Variables**:
   - Add to Cloud Run environment variables (for production backend)
   - Add to `.env.production` (for testing)
   - Add to GitHub Secrets (for CI/CD)

---

## 2. Environment Configuration

### Production Environment Variables

Add these to your deployment environment:

```bash
# Redis Configuration (Upstash)
REDIS_URL=rediss://default:<PASSWORD>@<HOST>.upstash.io:6379
REDIS_TLS=true
REDIS_MAX_CONNECTIONS=50
REDIS_SOCKET_TIMEOUT=5
REDIS_SOCKET_CONNECT_TIMEOUT=5

# Optional: Upstash REST API (for serverless environments)
UPSTASH_REDIS_REST_URL=https://<HOST>.upstash.io
UPSTASH_REDIS_REST_TOKEN=<REST_TOKEN>

# Cache Configuration
CACHE_ENABLED=true
CACHE_DEFAULT_TTL=3600  # 1 hour
CACHE_SHORT_TTL=300     # 5 minutes
CACHE_LONG_TTL=86400    # 24 hours

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS_PER_MINUTE=60
RATE_LIMIT_BURST_SIZE=10
```

### Local Development (Optional)

For local development, you can use Docker Redis or Upstash:

```bash
# Option 1: Local Docker Redis
REDIS_URL=redis://localhost:6379/0

# Option 2: Upstash (recommended - same as production)
REDIS_URL=rediss://default:<PASSWORD>@<HOST>.upstash.io:6379
```

---

## 3. Backend Configuration Updates

### Update `backend/app/core/config.py`

Ensure settings support production Redis configuration:

```python
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_TLS: bool = False
    REDIS_MAX_CONNECTIONS: int = 50
    REDIS_SOCKET_TIMEOUT: int = 5
    REDIS_SOCKET_CONNECT_TIMEOUT: int = 5

    # Cache Settings
    CACHE_ENABLED: bool = True
    CACHE_DEFAULT_TTL: int = 3600
    CACHE_SHORT_TTL: int = 300
    CACHE_LONG_TTL: int = 86400

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 60
    RATE_LIMIT_BURST_SIZE: int = 10

    class Config:
        env_file = ".env"
        case_sensitive = True
```

### Update `backend/app/core/cache.py`

The existing `cache.py` already supports Upstash! Just ensure the Redis URL is set correctly.

Key features already implemented:
- ✅ Connection pooling with timeout
- ✅ Graceful fallback if Redis unavailable
- ✅ Namespaced keys (`next:namespace:key`)
- ✅ JSON serialization
- ✅ TTL-based expiration
- ✅ Rate limiting with sliding window
- ✅ Cache statistics endpoint

---

## 4. Cloud Run Deployment

### Add Redis URL to Cloud Run

```bash
# Deploy with Redis configuration
gcloud run deploy next-backend \
  --source=./backend \
  --region=us-east4 \
  --set-env-vars="REDIS_URL=rediss://default:<PASSWORD>@<HOST>.upstash.io:6379" \
  --set-env-vars="REDIS_TLS=true" \
  --set-env-vars="CACHE_ENABLED=true" \
  --set-env-vars="RATE_LIMIT_ENABLED=true" \
  --allow-unauthenticated
```

### Using Secret Manager (Recommended)

Store Redis URL in Secret Manager for better security:

```bash
# Create secret
echo -n "rediss://default:<PASSWORD>@<HOST>.upstash.io:6379" | \
  gcloud secrets create redis-url --data-file=-

# Grant Cloud Run access
gcloud secrets add-iam-policy-binding redis-url \
  --member="serviceAccount:<PROJECT_ID>@appspot.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Deploy with secret reference
gcloud run deploy next-backend \
  --source=./backend \
  --region=us-east4 \
  --set-secrets="REDIS_URL=redis-url:latest" \
  --allow-unauthenticated
```

---

## 5. Cache Warming Strategy

On application startup, pre-populate frequently accessed data:

### Implementation in `backend/app/main.py`

```python
from app.core.cache import Cache, init_redis

@app.on_event("startup")
async def startup_event():
    """Startup tasks"""
    # Initialize Redis connection
    await init_redis()

    # Warm up cache with frequently accessed data
    await warm_cache()

async def warm_cache():
    """Pre-populate cache with hot data"""
    logger.info("🔥 Warming up cache...")

    try:
        # Cache popular job listings
        popular_jobs = await db.query("SELECT * FROM jobs WHERE is_featured = true LIMIT 50")
        for job in popular_jobs:
            await Cache.set("jobs", job["id"], job, ttl=Cache.TTL_LONG)

        # Cache skill taxonomy
        skills = await db.query("SELECT * FROM skills")
        await Cache.set("taxonomy", "skills", skills, ttl=Cache.TTL_LONG)

        # Cache subscription plans
        plans = await db.query("SELECT * FROM subscription_plans WHERE active = true")
        await Cache.set("billing", "plans", plans, ttl=Cache.TTL_LONG)

        logger.info(f"✅ Cache warmed: {len(popular_jobs)} jobs, {len(skills)} skills, {len(plans)} plans")

    except Exception as e:
        logger.warning(f"⚠️ Cache warming failed (non-critical): {e}")
```

---

## 6. Monitoring & Observability

### Cache Hit Rate Monitoring

Add endpoint to track cache performance:

```python
from app.core.cache import get_cache_stats

@app.get("/api/admin/cache-stats")
async def get_cache_statistics(admin_user = Depends(require_admin)):
    """Get cache performance metrics (Admin only)"""
    stats = await get_cache_stats()

    # Calculate hit rate
    hits = stats.get("keyspace_hits", 0)
    misses = stats.get("keyspace_misses", 0)
    total = hits + misses
    hit_rate = (hits / total * 100) if total > 0 else 0

    return {
        "status": stats.get("status"),
        "connected": stats.get("connected"),
        "memory_usage": stats.get("used_memory"),
        "connected_clients": stats.get("connected_clients"),
        "total_commands": stats.get("total_commands"),
        "hit_rate_percent": round(hit_rate, 2),
        "hits": hits,
        "misses": misses
    }
```

### Upstash Dashboard

Monitor Redis performance in Upstash Console:
- **Requests/sec**: Track traffic patterns
- **Latency**: p50, p99, p999 metrics
- **Hit Rate**: Cache effectiveness
- **Memory Usage**: Storage consumption
- **Eviction Rate**: How often keys are removed

Target metrics:
- **Hit Rate**: > 80%
- **p99 Latency**: < 10ms
- **Memory Usage**: < 80% of limit
- **Eviction Rate**: < 5% of requests

---

## 7. Rate Limiting Implementation

### Apply Rate Limits to Endpoints

```python
from app.core.cache import rate_limiter
from fastapi import HTTPException, Request

async def rate_limit_middleware(request: Request, user_id: str = None):
    """
    Rate limiting middleware

    Limits:
    - Authenticated users: 1000 req/hour
    - Anonymous users: 100 req/hour
    - AI endpoints: 20 req/min
    """
    if user_id:
        identifier = f"user:{user_id}"
        max_requests = 1000
        window = 3600  # 1 hour
    else:
        # Use IP address for anonymous users
        identifier = f"ip:{request.client.host}"
        max_requests = 100
        window = 3600

    allowed, info = await rate_limiter.check_rate_limit(
        identifier=identifier,
        max_requests=max_requests,
        window_seconds=window
    )

    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Reset in {info['reset_in']}s",
            headers={
                "X-RateLimit-Limit": str(info["limit"]),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(info["reset_in"])
            }
        )

    # Add rate limit headers to response
    return info

# Apply to AI endpoints
@router.post("/api/analyze")
async def analyze_resume(
    request: Request,
    current_user = Depends(get_current_user)
):
    # Check AI-specific rate limit (stricter)
    rate_info = await rate_limit_middleware(request, current_user.id)

    allowed, ai_rate_info = await rate_limiter.check_rate_limit(
        identifier=f"ai:{current_user.id}",
        max_requests=20,  # 20 AI requests per minute
        window_seconds=60
    )

    if not allowed:
        raise HTTPException(429, "AI rate limit exceeded")

    # Proceed with analysis...
```

---

## 8. Disaster Recovery

### Backup Strategy

Upstash provides automatic backups:
- **Daily snapshots**: 7-day retention
- **Point-in-time recovery**: Up to 24 hours

Manual backup (if needed):
```bash
# Use redis-cli to dump all keys
redis-cli -u $REDIS_URL --rdb /backups/redis-backup-$(date +%Y%m%d).rdb
```

### Recovery Procedure

If Redis fails:
1. **Graceful Degradation**: Application continues without cache (slower, but functional)
2. **Check Upstash Status**: https://status.upstash.com/
3. **Restore from Backup**: Contact Upstash support for recovery
4. **Cache Warming**: After recovery, run cache warming script

---

## 9. Cost Estimation

### Upstash Pricing Tiers

**Free Tier**:
- 10,000 commands/day
- 256 MB storage
- Good for: Development/Testing

**Pay As You Go**:
- $0.2 per 100K commands
- $0.25 per GB storage/month
- Good for: Early production

**Pro Plan** ($50/mo):
- 10M commands/month included
- 10 GB storage included
- $0.15 per additional 100K commands
- Good for: Production launch

### Expected Usage (10,000 users)

Assumptions:
- 5,000 daily active users
- 20 API requests/user/day (average)
- 50% cache hit rate
- Average key size: 2 KB

**Monthly Cost Estimate**:
```
Commands/month = 5,000 users × 20 req/day × 30 days × 2 (read + write)
                = 6,000,000 commands/month

Storage = 10,000 keys × 2 KB × 50% fill rate
        = 10 MB (well under limit)

Cost = $50/month (Pro plan, includes 10M commands)
```

**At Scale (100,000 users)**:
```
Commands/month = 60,000,000 commands
Extra commands = 50,000,000 commands
Extra cost = 50M / 100K × $0.15 = $75

Total = $50 (base) + $75 (overage) = $125/month
```

---

## 10. Testing

### Verify Redis Connection

```bash
# Test connection
curl https://your-backend-url.run.app/api/health

# Expected response:
{
  "status": "healthy",
  "redis": {
    "status": "connected",
    "connected": true,
    "used_memory": "1.2M",
    "hit_rate_percent": 82.5
  }
}
```

### Load Testing with Cache

```bash
# Install k6 (load testing tool)
brew install k6

# Run load test
k6 run scripts/load-tests/cache-test.js

# Targets:
# - 100 req/sec: p95 < 100ms
# - 500 req/sec: p95 < 200ms
# - 1000 req/sec: p95 < 500ms
```

### Cache Invalidation Testing

```bash
# Update user profile
curl -X PUT https://your-backend-url.run.app/api/users/profile \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name": "Updated Name"}'

# Verify cache was invalidated
curl https://your-backend-url.run.app/api/users/profile \
  -H "Authorization: Bearer $TOKEN"

# Should show updated data immediately (not cached old data)
```

---

## 11. Migration Checklist

- [ ] Create Upstash Redis database
- [ ] Copy connection URL
- [ ] Add `REDIS_URL` to Cloud Run environment variables
- [ ] Deploy backend with Redis configuration
- [ ] Verify Redis connection in logs
- [ ] Check `/api/health` endpoint shows Redis connected
- [ ] Test cache hit rate (should be > 50% after warmup)
- [ ] Test rate limiting (should return 429 after limit)
- [ ] Monitor Upstash dashboard for 24 hours
- [ ] Set up alerts for Redis downtime
- [ ] Document Redis URL in password manager (1Password/LastPass)

---

## 12. Troubleshooting

### Issue: "Redis connection timeout"

**Cause**: Cloud Run can't reach Upstash (firewall/network issue)

**Fix**:
```bash
# Verify DNS resolution
nslookup <your-redis-host>.upstash.io

# Test connection from Cloud Run
gcloud run services describe next-backend --region=us-east4 --format=json | jq '.status'

# Check Cloud Run egress settings (should allow all)
```

### Issue: "NOAUTH Authentication required"

**Cause**: Missing or incorrect password in `REDIS_URL`

**Fix**:
```bash
# Verify REDIS_URL format
# Correct: rediss://default:<PASSWORD>@host:6379
# Wrong: rediss://host:6379 (missing default:<PASSWORD>@)

# Update environment variable
gcloud run services update next-backend \
  --region=us-east4 \
  --set-env-vars="REDIS_URL=rediss://default:<PASSWORD>@<HOST>:6379"
```

### Issue: "Out of Memory" errors

**Cause**: Cache size exceeds Upstash storage limit

**Fix**:
```bash
# Check memory usage
redis-cli -u $REDIS_URL INFO memory

# Reduce TTLs to evict data faster
# Or upgrade Upstash plan
# Or implement LRU eviction policy (already default)
```

### Issue: Low cache hit rate (< 50%)

**Cause**: TTLs too short, cache not being warmed, or queries not cacheable

**Fix**:
1. Increase TTLs for stable data
2. Implement cache warming on startup
3. Review which endpoints are being cached
4. Add caching to frequently accessed endpoints

---

## 13. Next Steps

After Redis is deployed:

1. **CDN Setup** (Week 2, Days 3-4): Cloudflare Pro for static assets
2. **Monitoring** (Week 2, Days 5-6): Sentry, PagerDuty, custom dashboards
3. **Load Testing** (Week 10): Verify cache performance under load

---

## References

- [Upstash Redis Documentation](https://docs.upstash.com/redis)
- [Redis Best Practices](https://redis.io/docs/manual/patterns/)
- [FastAPI Caching Strategies](https://fastapi.tiangolo.com/advanced/middleware/)
- [Rate Limiting Patterns](https://cloud.google.com/architecture/rate-limiting-strategies-techniques)
