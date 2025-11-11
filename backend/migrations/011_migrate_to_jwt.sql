-- Migration 011: Migrate from Session Tokens to JWT
-- Purpose: Replace insecure random session tokens with signed JWT tokens
-- Date: 2025-11-10
-- Impact: All existing sessions invalidated (users must re-login)

-- ============================================
-- USER SESSIONS TABLE UPDATES
-- ============================================

-- Check if user_sessions table exists, create if not
CREATE TABLE IF NOT EXISTS public.user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    last_used_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent TEXT
);

-- Add refresh token JTI (JWT ID) column for token revocation
ALTER TABLE public.user_sessions
ADD COLUMN IF NOT EXISTS refresh_token_jti VARCHAR(100) UNIQUE;

COMMENT ON COLUMN public.user_sessions.refresh_token_jti IS 'JWT ID (jti) from refresh token for revocation checking';

-- Remove old session_token column if it exists (replaced by JWT)
ALTER TABLE public.user_sessions
DROP COLUMN IF EXISTS session_token;

-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================

-- Index on refresh token JTI for fast revocation checks
CREATE INDEX IF NOT EXISTS idx_user_sessions_refresh_jti
    ON public.user_sessions(refresh_token_jti)
    WHERE refresh_token_jti IS NOT NULL;

-- Index on user_id for user session queries
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id
    ON public.user_sessions(user_id);

-- Index on expires_at for cleanup queries
CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at
    ON public.user_sessions(expires_at);

-- Composite index for active session lookups
CREATE INDEX IF NOT EXISTS idx_user_sessions_active
    ON public.user_sessions(user_id, expires_at DESC)
    WHERE expires_at > CURRENT_TIMESTAMP;

COMMENT ON INDEX idx_user_sessions_refresh_jti IS 'Fast lookup for JWT refresh token validation';
COMMENT ON INDEX idx_user_sessions_active IS 'Active sessions for user (not expired)';

-- ============================================
-- INVALIDATE ALL EXISTING SESSIONS
-- ============================================

-- Delete all existing sessions (force re-login for all users)
DELETE FROM public.user_sessions;

RAISE NOTICE 'All existing sessions invalidated. Users must re-login with JWT tokens.';

-- ============================================
-- JWT TOKEN SCHEMA
-- ============================================

/*
JWT Token Structure (implemented in backend/app/core/security_fixes.py):

Access Token (1-hour expiration):
{
  "sub": "user_id",           # Subject (user ID)
  "email": "user@example.com",
  "type": "access",           # Token type
  "exp": 1699999999,          # Expiration (1 hour from now)
  "iat": 1699996399,          # Issued at
  "jti": "random_unique_id"   # JWT ID
}

Refresh Token (30-day expiration):
{
  "sub": "user_id",
  "email": "user@example.com",
  "type": "refresh",
  "exp": 1702591999,          # Expiration (30 days from now)
  "iat": 1699996399,
  "jti": "refresh_token_jti"  # Stored in database for revocation
}

Signing: HS256 with SECRET_KEY from environment
*/

-- ============================================
-- SESSION CLEANUP FUNCTION
-- ============================================

-- Function to delete expired sessions (run daily)
CREATE OR REPLACE FUNCTION cleanup_expired_sessions()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM public.user_sessions
    WHERE expires_at < CURRENT_TIMESTAMP;

    GET DIAGNOSTICS deleted_count = ROW_COUNT;

    RAISE NOTICE 'Cleaned up % expired sessions', deleted_count;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION cleanup_expired_sessions IS 'Delete expired JWT refresh tokens (schedule daily)';

-- ============================================
-- SESSION MONITORING FUNCTIONS
-- ============================================

-- View: Active sessions per user
CREATE OR REPLACE VIEW active_user_sessions AS
SELECT
    u.id as user_id,
    u.email,
    COUNT(s.id) as active_sessions,
    MAX(s.last_used_at) as last_activity,
    MIN(s.created_at) as oldest_session,
    MAX(s.created_at) as newest_session
FROM public.users u
LEFT JOIN public.user_sessions s ON s.user_id = u.id
    AND s.expires_at > CURRENT_TIMESTAMP
GROUP BY u.id, u.email;

COMMENT ON VIEW active_user_sessions IS 'Monitor active user sessions (for security auditing)';

-- Function: Revoke all sessions for a user (force logout)
CREATE OR REPLACE FUNCTION revoke_user_sessions(target_user_id UUID)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM public.user_sessions
    WHERE user_id = target_user_id;

    GET DIAGNOSTICS deleted_count = ROW_COUNT;

    RAISE NOTICE 'Revoked % sessions for user %', deleted_count, target_user_id;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION revoke_user_sessions IS 'Force logout user by revoking all refresh tokens';

-- ============================================
-- STRIPE WEBHOOK EVENTS TABLE
-- ============================================

-- Create table to track processed Stripe webhook events (idempotency)
CREATE TABLE IF NOT EXISTS public.stripe_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id VARCHAR(255) UNIQUE NOT NULL,  -- Stripe event ID (e.g., "evt_...")
    event_type VARCHAR(100) NOT NULL,        -- Event type (e.g., "payment_intent.succeeded")
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    payload JSONB                             -- Full webhook payload (optional)
);

CREATE INDEX IF NOT EXISTS idx_stripe_events_event_id
    ON public.stripe_events(event_id);

CREATE INDEX IF NOT EXISTS idx_stripe_events_processed_at
    ON public.stripe_events(processed_at DESC);

COMMENT ON TABLE public.stripe_events IS 'Track processed Stripe webhooks for idempotency';

-- ============================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================

-- Enable RLS on user_sessions
ALTER TABLE public.user_sessions ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only view their own sessions
CREATE POLICY "Users can view own sessions" ON public.user_sessions
    FOR SELECT
    USING (auth.uid() = user_id);

-- Policy: Users can delete their own sessions (logout)
CREATE POLICY "Users can delete own sessions" ON public.user_sessions
    FOR DELETE
    USING (auth.uid() = user_id);

-- Policy: Service role can manage all sessions
CREATE POLICY "Service role can manage all sessions" ON public.user_sessions
    FOR ALL
    USING (current_user = 'postgres');

-- Grant permissions
GRANT SELECT, DELETE ON public.user_sessions TO authenticated;
GRANT ALL ON public.user_sessions TO service_role;

-- ============================================
-- SCHEDULED CLEANUP (pg_cron - if available)
-- ============================================

/*
If pg_cron extension is available, schedule daily cleanup:

CREATE EXTENSION IF NOT EXISTS pg_cron;

-- Schedule cleanup daily at 2 AM UTC
SELECT cron.schedule(
    'cleanup-expired-sessions',
    '0 2 * * *',
    'SELECT cleanup_expired_sessions();'
);
*/

-- ============================================
-- MIGRATION STATISTICS
-- ============================================

-- View: JWT migration status
CREATE OR REPLACE VIEW jwt_migration_status AS
SELECT
    (SELECT COUNT(*) FROM public.users) as total_users,
    (SELECT COUNT(*) FROM public.user_sessions) as active_sessions,
    (SELECT COUNT(*) FROM public.user_sessions WHERE expires_at < CURRENT_TIMESTAMP) as expired_sessions,
    (SELECT COUNT(DISTINCT user_id) FROM public.user_sessions WHERE expires_at > CURRENT_TIMESTAMP) as users_with_active_sessions,
    ROUND(
        100.0 * (SELECT COUNT(DISTINCT user_id) FROM public.user_sessions WHERE expires_at > CURRENT_TIMESTAMP) /
        NULLIF((SELECT COUNT(*) FROM public.users), 0),
        2
    ) as session_adoption_percentage
;

COMMENT ON VIEW jwt_migration_status IS 'Track JWT token adoption post-migration';

-- ============================================
-- SECURITY AUDIT LOG (Optional)
-- ============================================

-- Track security events (login, logout, token refresh, forced logout)
CREATE TABLE IF NOT EXISTS public.security_audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) ON DELETE SET NULL,
    event_type VARCHAR(50) NOT NULL,  -- 'login', 'logout', 'token_refresh', 'password_reset', 'forced_logout'
    ip_address VARCHAR(45),
    user_agent TEXT,
    success BOOLEAN DEFAULT TRUE,
    failure_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_security_audit_log_user_id
    ON public.security_audit_log(user_id);

CREATE INDEX idx_security_audit_log_created_at
    ON public.security_audit_log(created_at DESC);

CREATE INDEX idx_security_audit_log_event_type
    ON public.security_audit_log(event_type);

COMMENT ON TABLE public.security_audit_log IS 'Security event audit trail';

-- ============================================
-- MONITORING QUERIES
-- ============================================

-- Check session statistics
-- Run after deployment to verify users are logging in with JWT

-- 1. Active sessions count
SELECT COUNT(*) as active_jwt_sessions
FROM public.user_sessions
WHERE expires_at > CURRENT_TIMESTAMP;

-- 2. Sessions created in last 24 hours
SELECT COUNT(*) as new_sessions_24h
FROM public.user_sessions
WHERE created_at > CURRENT_TIMESTAMP - INTERVAL '24 hours';

-- 3. Users with active sessions
SELECT COUNT(DISTINCT user_id) as users_logged_in
FROM public.user_sessions
WHERE expires_at > CURRENT_TIMESTAMP;

-- 4. Top users by session count (potential security issue if > 10)
SELECT
    u.email,
    COUNT(s.id) as session_count,
    MAX(s.created_at) as last_login
FROM public.users u
JOIN public.user_sessions s ON s.user_id = u.id
WHERE s.expires_at > CURRENT_TIMESTAMP
GROUP BY u.id, u.email
ORDER BY session_count DESC
LIMIT 10;

-- ============================================
-- ROLLBACK PROCEDURE (Emergency Only)
-- ============================================

/*
If you need to rollback to session tokens:

1. Restore database from backup (before migration)
   Supabase Dashboard → Database → Backups → Restore

2. Or manually recreate session_token column:
   ALTER TABLE public.user_sessions ADD COLUMN session_token VARCHAR(255);
   CREATE INDEX idx_user_sessions_token ON public.user_sessions(session_token);

3. Revert application code to use session tokens
   (Not recommended - security vulnerability)
*/

-- ============================================
-- VERIFICATION
-- ============================================

-- Verify user_sessions table structure
SELECT
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'user_sessions'
ORDER BY ordinal_position;

-- Check indexes
SELECT
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
  AND tablename = 'user_sessions';

-- Verify all sessions cleared
SELECT
    COUNT(*) as remaining_sessions,
    CASE WHEN COUNT(*) = 0 THEN 'SUCCESS' ELSE 'FAILED' END as migration_status
FROM public.user_sessions;

-- View migration status
SELECT * FROM jwt_migration_status;

-- Migration complete
SELECT 'Migration 011 complete: JWT token system ready' as status;
