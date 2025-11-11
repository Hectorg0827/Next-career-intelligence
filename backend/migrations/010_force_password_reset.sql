-- Migration 010: Force Password Reset (SHA-256 → bcrypt transition)
-- Purpose: Transition from insecure SHA-256 to bcrypt password hashing
-- Date: 2025-11-10
-- Impact: All users must reset password on next login

-- ============================================
-- ADD PASSWORD RESET FLAG
-- ============================================

-- Add column to track users who must reset password
ALTER TABLE public.users
ADD COLUMN IF NOT EXISTS must_reset_password BOOLEAN DEFAULT FALSE;

COMMENT ON COLUMN public.users.must_reset_password IS 'User must reset password (bcrypt migration)';

-- ============================================
-- MARK ALL EXISTING USERS FOR PASSWORD RESET
-- ============================================

-- Option 1: Force password reset for all existing users (RECOMMENDED)
-- All existing SHA-256 passwords will be invalidated
-- Users will receive "Invalid email or password" and must use password reset flow

UPDATE public.users
SET must_reset_password = TRUE,
    password_hash = NULL
WHERE password_hash IS NOT NULL
  AND password_hash NOT LIKE '$2b$%';  -- Don't reset if already bcrypt

-- Log the number of users affected
DO $$
DECLARE
    affected_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO affected_count
    FROM public.users
    WHERE must_reset_password = TRUE;

    RAISE NOTICE 'Password reset required for % users', affected_count;
END $$;

-- ============================================
-- UPDATE AUTH LOGIC (Application-Level)
-- ============================================

/*
Application Changes (already implemented in backend/app/api/auth.py):

1. Login Flow:
   - Check if user.password_hash is NULL or must_reset_password = TRUE
   - Return 403 with message: "Password reset required. Please check your email."
   - Automatically trigger password reset email

2. Password Reset Flow:
   - User requests reset via /api/auth/request-password-reset
   - Receives email with reset link
   - Sets new password via /api/auth/reset-password
   - New password hashed with bcrypt (12 rounds)
   - Set must_reset_password = FALSE

3. New User Registration:
   - All new passwords use bcrypt immediately
   - must_reset_password = FALSE (default)
*/

-- ============================================
-- EMAIL NOTIFICATION (Optional)
-- ============================================

-- Create table to track password reset emails sent
CREATE TABLE IF NOT EXISTS public.password_reset_notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    reason VARCHAR(100) DEFAULT 'bcrypt_migration'
);

CREATE INDEX idx_password_reset_notifications_user_id
    ON public.password_reset_notifications(user_id);

COMMENT ON TABLE public.password_reset_notifications IS 'Track password reset emails for security transitions';

-- ============================================
-- ALTERNATIVE: DUAL-HASH MIGRATION (Not Recommended)
-- ============================================

/*
If you prefer gradual migration (not recommended for production):

1. Keep SHA-256 passwords temporarily
2. Application checks hash format:
   - If starts with "$2b$" → verify with bcrypt
   - If not → verify with SHA-256 AND rehash with bcrypt
3. Gradually transition users as they login

Implementation in app/core/security_fixes.py:

def verify_password_with_migration(password: str, stored_hash: str) -> tuple[bool, bool]:
    if stored_hash.startswith('$2b$'):
        # Already bcrypt
        return (bcrypt.checkpw(...), False)
    else:
        # Legacy SHA-256 - verify and mark for rehash
        is_valid = verify_sha256(password, stored_hash)
        return (is_valid, True)  # needs_rehash = True

# In login endpoint:
is_valid, needs_rehash = verify_password_with_migration(...)
if needs_rehash:
    new_hash = bcrypt.hashpw(...)
    await db.update_password(user_id, new_hash)
*/

-- ============================================
-- MONITORING QUERIES
-- ============================================

-- Check migration progress
-- Run this daily to see how many users have reset passwords
CREATE OR REPLACE VIEW password_migration_status AS
SELECT
    COUNT(*) as total_users,
    COUNT(*) FILTER (WHERE password_hash IS NULL) as pending_reset,
    COUNT(*) FILTER (WHERE password_hash LIKE '$2b$%') as using_bcrypt,
    COUNT(*) FILTER (WHERE password_hash IS NOT NULL AND password_hash NOT LIKE '$2b$%') as legacy_sha256,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE password_hash LIKE '$2b$%') / NULLIF(COUNT(*), 0),
        2
    ) as migration_percentage
FROM public.users;

COMMENT ON VIEW password_migration_status IS 'Track bcrypt migration progress';

-- ============================================
-- ROLLBACK PROCEDURE (Emergency Only)
-- ============================================

/*
If you need to rollback this migration:

-- Restore password_hash from backup
-- (Requires database backup before migration)

-- 1. Restore from Supabase backup
--    Dashboard → Database → Backups → Restore

-- 2. Or remove the column
ALTER TABLE public.users DROP COLUMN IF EXISTS must_reset_password;
DROP TABLE IF EXISTS public.password_reset_notifications;
DROP VIEW IF EXISTS password_migration_status;
*/

-- ============================================
-- VERIFICATION
-- ============================================

-- Verify column was added
SELECT
    column_name,
    data_type,
    column_default,
    is_nullable
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'users'
  AND column_name = 'must_reset_password';

-- Check migration status
SELECT * FROM password_migration_status;

-- Migration complete
SELECT 'Migration 010 complete: Password reset migration ready' as status;
