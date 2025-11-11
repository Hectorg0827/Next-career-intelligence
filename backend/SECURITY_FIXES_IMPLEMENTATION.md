# Phase 1 Security Fixes Implementation Guide

**Priority**: CRITICAL
**Timeline**: Week 1 (before production deployment)
**Effort**: 8 hours

This guide implements the 4 critical security fixes identified in the security audit:

1. ✅ Replace SHA-256 with bcrypt password hashing
2. ✅ Remove authentication bypass in production
3. ✅ Implement JWT token authentication
4. ✅ Fix Stripe webhook signature validation

---

## Fix 1: Replace SHA-256 with Bcrypt Password Hashing

**Vulnerability**: SHA-256 is not designed for password hashing (no salt, too fast)
**Impact**: CRITICAL - Passwords vulnerable to rainbow table attacks
**Files to modify**: `backend/app/api/auth.py`, `backend/app/core/auth.py`

### Step 1: Update auth.py (Registration)

**File**: `backend/app/api/auth.py`

**Find this code** (around line 50):
```python
# Hash password
hashed_password = hashlib.sha256(user_data.password.encode()).hexdigest()
```

**Replace with**:
```python
# Hash password with bcrypt (12 rounds)
from app.core.security_fixes import hash_password_secure
hashed_password = hash_password_secure(user_data.password)
```

### Step 2: Update auth.py (Login)

**Find this code** (around line 120):
```python
# Verify password
password_hash = hashlib.sha256(credentials.password.encode()).hexdigest()
if user_data.get('password_hash') != password_hash:
    raise HTTPException(status_code=401, detail="Invalid credentials")
```

**Replace with**:
```python
# Verify password with bcrypt
from app.core.security_fixes import verify_password_secure

if not verify_password_secure(credentials.password, user_data.get('password_hash')):
    raise HTTPException(status_code=401, detail="Invalid credentials")
```

### Step 3: Migration Script for Existing Passwords

**IMPORTANT**: Existing SHA-256 passwords cannot be migrated to bcrypt (hashing is one-way).

**Options**:
1. **Force password reset** (recommended for production)
2. **Dual-hash support** (temporary migration period)

**Option 1: Force Password Reset** (Recommended)

Create migration: `backend/migrations/010_force_password_reset.sql`

```sql
-- Migration 010: Force password reset after bcrypt migration
-- All users must reset their password on next login

UPDATE public.users
SET password_hash = NULL,
    must_reset_password = TRUE
WHERE password_hash IS NOT NULL;

-- Add temporary column
ALTER TABLE public.users
ADD COLUMN IF NOT EXISTS must_reset_password BOOLEAN DEFAULT FALSE;

-- Update auth flow to check this flag
COMMENT ON COLUMN public.users.must_reset_password IS 'User must reset password (bcrypt migration)';
```

**Option 2: Dual-Hash Support** (Grace Period)

Add to `backend/app/core/security_fixes.py`:

```python
def verify_password_with_migration(password: str, stored_hash: str) -> tuple[bool, bool]:
    """
    Verify password with automatic SHA-256 → bcrypt migration

    Returns:
        (is_valid, needs_rehash): (bool, bool)
    """
    # Try bcrypt first (new format starts with $2b$)
    if stored_hash.startswith('$2b$'):
        try:
            is_valid = bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
            return (is_valid, False)  # Valid, no rehash needed
        except ValueError:
            return (False, False)

    # Fall back to SHA-256 (legacy)
    sha256_hash = hashlib.sha256(password.encode()).hexdigest()
    if sha256_hash == stored_hash:
        return (True, True)  # Valid, NEEDS rehash to bcrypt

    return (False, False)  # Invalid password


# Update login endpoint to use this:
is_valid, needs_rehash = verify_password_with_migration(
    credentials.password,
    user_data.get('password_hash')
)

if not is_valid:
    raise HTTPException(status_code=401, detail="Invalid credentials")

# If needs rehash, update to bcrypt
if needs_rehash:
    new_hash = hash_password_secure(credentials.password)
    supabase.table('users').update({
        'password_hash': new_hash
    }).eq('id', user_data['id']).execute()
```

---

## Fix 2: Remove Authentication Bypass in Production

**Vulnerability**: Auth bypass allows unauthenticated access if Firebase fails
**Impact**: CRITICAL - Complete authentication bypass
**File to modify**: `backend/app/core/auth.py`

### Implementation

**Find this code** (around line 80):
```python
if _firebase_app is None:
    # DEVELOPMENT ONLY: Allow requests without Firebase
    logger.warning("Firebase not initialized - allowing request (DEV MODE)")
    return None
```

**Replace with**:
```python
if _firebase_app is None:
    # Production: Fail fast if Firebase unavailable
    if settings.ENVIRONMENT == "production":
        logger.error("Firebase not initialized in production")
        raise HTTPException(
            status_code=503,
            detail="Authentication service unavailable"
        )

    # Development: Allow bypass with warning
    logger.warning("Firebase not initialized - allowing request (DEV MODE ONLY)")
    return None
```

### Verification

Add integration test: `backend/tests/test_auth_production.py`

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)


def test_auth_bypass_blocked_in_production(monkeypatch):
    """Test that auth bypass is blocked when ENVIRONMENT=production"""
    # Set production environment
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")

    # Simulate Firebase initialization failure
    from app.core import auth
    auth._firebase_app = None

    # Attempt to access protected endpoint
    response = client.get("/api/users/me")

    # Should return 503 (service unavailable), not 200
    assert response.status_code == 503
    assert "Authentication service unavailable" in response.json()["detail"]


def test_auth_bypass_allowed_in_development(monkeypatch):
    """Test that auth bypass works in development"""
    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.setattr(settings, "ENVIRONMENT", "development")

    from app.core import auth
    auth._firebase_app = None

    # Should allow request in development
    response = client.get("/api/users/me")
    # May return 404 (no user) but NOT 503
    assert response.status_code != 503
```

---

## Fix 3: Implement JWT Token Authentication

**Vulnerability**: Using random tokens instead of signed JWT
**Impact**: HIGH - Token forgery possible, no expiration
**Files to modify**: `backend/app/api/auth.py`, `backend/app/core/auth.py`

### Step 1: Update Login Endpoint

**File**: `backend/app/api/auth.py`

**Find this code** (around line 150):
```python
# Generate session token
import secrets
session_token = secrets.token_urlsafe(32)

# Store in database
supabase.table('user_sessions').insert({
    'user_id': user_data['id'],
    'session_token': session_token,
    'expires_at': datetime.utcnow() + timedelta(hours=24)
}).execute()

return {
    "access_token": session_token,
    "token_type": "bearer"
}
```

**Replace with**:
```python
# Generate JWT tokens (access + refresh)
from app.core.security_fixes import generate_jwt_tokens

tokens = generate_jwt_tokens(
    user_id=user_data['id'],
    email=user_data['email'],
    secret_key=settings.SECRET_KEY
)

# Store refresh token in database (for revocation)
supabase.table('user_sessions').insert({
    'user_id': user_data['id'],
    'refresh_token_jti': tokens['refresh_token_jti'],
    'expires_at': datetime.utcnow() + timedelta(days=30)
}).execute()

return {
    "access_token": tokens['access_token'],
    "refresh_token": tokens['refresh_token'],
    "token_type": "bearer",
    "expires_in": tokens['expires_in']
}
```

### Step 2: Update Token Verification

**File**: `backend/app/core/auth.py`

**Find this code**:
```python
def verify_token(token: str) -> dict:
    """Verify session token"""
    result = supabase.table('user_sessions') \
        .select('*') \
        .eq('session_token', token) \
        .single() \
        .execute()

    if not result.data:
        raise HTTPException(status_code=401, detail="Invalid token")

    return result.data
```

**Replace with**:
```python
from app.core.security_fixes import verify_jwt_token

def verify_token(token: str) -> dict:
    """Verify JWT access token"""
    try:
        payload = verify_jwt_token(token, settings.SECRET_KEY)

        # Verify token type
        if payload.get('type') != 'access':
            raise HTTPException(status_code=401, detail="Invalid token type")

        return payload

    except jwt.JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
```

### Step 3: Add Token Refresh Endpoint

**File**: `backend/app/api/auth.py`

**Add new endpoint**:
```python
@router.post("/refresh")
async def refresh_token(
    refresh_token: str = Body(..., embed=True)
):
    """
    Refresh access token using refresh token

    POST /api/auth/refresh
    Body: {"refresh_token": "eyJ..."}
    """
    from app.core.security_fixes import verify_jwt_token, generate_jwt_tokens

    try:
        # Verify refresh token
        payload = verify_jwt_token(refresh_token, settings.SECRET_KEY)

        if payload.get('type') != 'refresh':
            raise HTTPException(status_code=401, detail="Invalid token type")

        # Check if refresh token is revoked
        result = supabase.table('user_sessions') \
            .select('*') \
            .eq('refresh_token_jti', payload.get('jti')) \
            .single() \
            .execute()

        if not result.data:
            raise HTTPException(status_code=401, detail="Token revoked")

        # Generate new access token
        tokens = generate_jwt_tokens(
            user_id=payload['sub'],
            email=payload['email'],
            secret_key=settings.SECRET_KEY
        )

        return {
            "access_token": tokens['access_token'],
            "token_type": "bearer",
            "expires_in": tokens['expires_in']
        }

    except jwt.JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
```

### Step 4: Migration for Existing Sessions

Create migration: `backend/migrations/011_migrate_to_jwt.sql`

```sql
-- Migration 011: Migrate from session tokens to JWT
-- All existing sessions will be invalidated (users must re-login)

-- Add column for refresh token JTI (JWT ID)
ALTER TABLE public.user_sessions
ADD COLUMN IF NOT EXISTS refresh_token_jti VARCHAR(100);

-- Remove old session_token column
ALTER TABLE public.user_sessions
DROP COLUMN IF EXISTS session_token;

-- Create index on JTI for fast lookups
CREATE INDEX IF NOT EXISTS idx_user_sessions_refresh_jti
ON public.user_sessions(refresh_token_jti);

-- Invalidate all existing sessions (force re-login)
DELETE FROM public.user_sessions;

COMMENT ON COLUMN public.user_sessions.refresh_token_jti IS 'JWT ID (jti) from refresh token for revocation';
```

---

## Fix 4: Fix Stripe Webhook Signature Validation

**Vulnerability**: Webhook signature not validated, allowing forged events
**Impact**: HIGH - Payment events can be spoofed
**File to modify**: `backend/app/api/payments.py`

### Implementation

**Find this code** (around line 200):
```python
@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events"""
    payload = await request.body()
    event = json.loads(payload)

    # Process event
    if event['type'] == 'payment_intent.succeeded':
        # Handle successful payment
        pass
```

**Replace with**:
```python
@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request):
    """
    Handle Stripe webhook events with signature verification

    Docs: https://stripe.com/docs/webhooks/signatures
    """
    import stripe
    from app.core.config import settings

    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')

    # Verify webhook signature
    if not settings.STRIPE_WEBHOOK_SECRET:
        logger.error("STRIPE_WEBHOOK_SECRET not configured")
        raise HTTPException(status_code=503, detail="Webhook not configured")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        logger.error(f"Invalid webhook payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        logger.error(f"Invalid webhook signature: {e}")
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Check for duplicate webhook (idempotency)
    from app.services.payment_edge_cases import PaymentEdgeCaseHandler
    handler = PaymentEdgeCaseHandler()

    if await handler.handle_duplicate_webhook(event['id']):
        logger.info(f"Duplicate webhook ignored: {event['id']}")
        return {"status": "duplicate"}

    # Store webhook event
    supabase.table('stripe_events').insert({
        'event_id': event['id'],
        'event_type': event['type'],
        'processed_at': datetime.utcnow().isoformat()
    }).execute()

    # Process event
    if event['type'] == 'payment_intent.succeeded':
        await handler.handle_payment_success(event['data']['object'])
    elif event['type'] == 'payment_intent.payment_failed':
        await handler.handle_payment_failed(event['data']['object'])
    elif event['type'] == 'customer.subscription.updated':
        await handler.handle_subscription_past_due(event['data']['object'])
    # ... other event types

    return {"status": "success"}
```

### Step 2: Add Webhook Secret to Environment

**File**: `backend/app/core/config.py`

**Add**:
```python
class Settings(BaseSettings):
    # ... existing fields

    STRIPE_WEBHOOK_SECRET: str = Field(
        ...,
        env="STRIPE_WEBHOOK_SECRET",
        description="Stripe webhook signing secret (whsec_...)"
    )
```

**File**: `.env` (local) and Cloud Run environment variables

```bash
# Get webhook secret from Stripe Dashboard
# Developers → Webhooks → Add endpoint → Reveal signing secret

STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Step 3: Verification Test

**File**: `backend/tests/test_stripe_webhooks.py`

```python
import pytest
import stripe
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_webhook_signature_validation():
    """Test that webhooks reject invalid signatures"""
    payload = {
        "type": "payment_intent.succeeded",
        "data": {"object": {"id": "pi_test"}}
    }

    # Send webhook without signature
    response = client.post(
        "/api/payments/webhooks/stripe",
        json=payload
    )

    assert response.status_code == 401
    assert "Invalid signature" in response.json()["detail"]


def test_webhook_accepts_valid_signature():
    """Test that webhooks accept valid signatures"""
    # Generate valid test signature
    payload = '{"type": "payment_intent.succeeded"}'
    secret = "whsec_test_secret"

    timestamp = int(time.time())
    signed_payload = f"{timestamp}.{payload}"
    signature = hmac.new(
        secret.encode(),
        signed_payload.encode(),
        hashlib.sha256
    ).hexdigest()

    sig_header = f"t={timestamp},v1={signature}"

    response = client.post(
        "/api/payments/webhooks/stripe",
        data=payload,
        headers={"stripe-signature": sig_header}
    )

    assert response.status_code == 200
```

---

## Deployment Checklist

### Pre-Deployment

- [ ] All 4 security fixes implemented
- [ ] Integration tests passing
- [ ] Environment variables configured:
  - [ ] `STRIPE_WEBHOOK_SECRET` added
  - [ ] `SECRET_KEY` rotated (for JWT signing)
- [ ] Database migrations ready:
  - [ ] `010_force_password_reset.sql` OR dual-hash migration
  - [ ] `011_migrate_to_jwt.sql`

### Staging Deployment

```bash
# 1. Deploy code to staging
git checkout main
git pull origin main

# 2. Run migrations
psql $DATABASE_URL_STAGING -f backend/migrations/010_force_password_reset.sql
psql $DATABASE_URL_STAGING -f backend/migrations/011_migrate_to_jwt.sql

# 3. Update environment variables in Cloud Run
gcloud run services update next-backend-staging \
  --set-env-vars STRIPE_WEBHOOK_SECRET=$STRIPE_WEBHOOK_SECRET_STAGING \
  --region us-central1

# 4. Deploy backend
gcloud builds submit --config cloudbuild.yaml --substitutions=_ENV=staging

# 5. Test critical flows
python backend/tests/test_auth_production.py
python backend/tests/test_stripe_webhooks.py

# 6. Verify in staging
curl -X POST https://staging-api.next.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'

# Should return JWT tokens, not random session token
```

### Production Deployment

```bash
# 1. Run migrations
psql $DATABASE_URL_PRODUCTION -f backend/migrations/010_force_password_reset.sql
psql $DATABASE_URL_PRODUCTION -f backend/migrations/011_migrate_to_jwt.sql

# 2. Update environment variables
gcloud run services update next-backend \
  --set-env-vars STRIPE_WEBHOOK_SECRET=$STRIPE_WEBHOOK_SECRET_PROD \
  --set-env-vars SECRET_KEY=$NEW_SECRET_KEY \
  --region us-central1

# 3. Deploy to production
gcloud builds submit --config cloudbuild.yaml --substitutions=_ENV=production

# 4. Verify deployment
curl https://api.next.com/health

# 5. Monitor error rate in Sentry
# Should see spike in 401s (users forced to re-login) - this is expected
```

### Post-Deployment Monitoring (Week 1)

**Day 1-2**:
- [ ] Monitor Sentry for auth errors (expected: 401s from password resets)
- [ ] Check Stripe webhook processing (should see successful signature verifications)
- [ ] Verify bcrypt login performance (< 200ms)

**Day 3-7**:
- [ ] Monitor JWT token refresh rate
- [ ] Check for authentication bypass attempts (should see 503 errors if Firebase down)
- [ ] Verify no Stripe webhook signature failures

### Rollback Procedure

If critical issues arise:

```bash
# 1. Revert to previous Cloud Run revision
gcloud run services update-traffic next-backend \
  --to-revisions=next-backend-00042-xyz=100 \
  --region us-central1

# 2. Restore database (if needed)
# Use point-in-time recovery in Supabase dashboard

# 3. Notify users
# Send email: "We've temporarily rolled back a security update"
```

---

## Success Criteria

✅ **Security Audit Score**: 68/100 → 90/100 (+22 points)

✅ **Critical Vulnerabilities**: 3 → 0 (100% resolved)

✅ **High Vulnerabilities**: 4 → 2 (50% resolved, remaining: CORS, rate limiting)

✅ **Authentication**:
- Bcrypt password hashing (12 rounds)
- JWT tokens with 1-hour expiration
- Refresh tokens with 30-day expiration
- No auth bypass in production
- Stripe webhook signature validation

✅ **Performance**:
- Login latency: < 200ms (bcrypt verification)
- JWT verification: < 5ms
- Webhook processing: < 100ms

---

## Next Steps: Phase 2-3 Security Fixes (Week 2-3)

After Phase 1 is deployed and stable, implement remaining fixes:

**Week 2** (High Priority):
1. CORS configuration (whitelist only trusted origins)
2. Rate limiting (100 req/min per IP, 1000 req/hour per user)
3. Error handling (remove stack traces from production)

**Week 3** (Medium Priority):
1. Encrypt 2FA secrets at rest (Fernet symmetric encryption)
2. SQL injection prevention (parameterized queries audit)
3. PII redaction in logs (email, phone, SSN masking)

**Estimated total effort**: 12 additional hours (6h Week 2, 6h Week 3)

---

## Support

If you encounter issues during implementation:

1. **Authentication errors**: Check Sentry → Errors → Filter by "auth"
2. **Webhook failures**: Stripe Dashboard → Developers → Webhooks → Event logs
3. **Performance degradation**: Run `backend/benchmark_performance.py`
4. **Database issues**: Check Supabase → Logs → Postgres

**Emergency contact**: Check Slack #engineering-security channel
