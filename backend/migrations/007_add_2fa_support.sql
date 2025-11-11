-- Add Two-Factor Authentication Support
-- Migration: 007
-- Created: 2025-11-10

-- Add 2FA columns to users table
ALTER TABLE users
ADD COLUMN IF NOT EXISTS two_factor_enabled BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS two_factor_secret TEXT,
ADD COLUMN IF NOT EXISTS two_factor_backup_codes TEXT[], -- Array of hashed backup codes
ADD COLUMN IF NOT EXISTS two_factor_enabled_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS two_factor_method VARCHAR(20) DEFAULT 'totp'; -- 'totp' or 'sms' (future)

-- Add login attempts tracking
CREATE TABLE IF NOT EXISTS login_attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    ip_address INET NOT NULL,
    user_agent TEXT,
    success BOOLEAN NOT NULL,
    failure_reason VARCHAR(100), -- 'invalid_password', 'invalid_2fa', 'account_locked'
    attempted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Indexes
    INDEX idx_login_attempts_user_id (user_id),
    INDEX idx_login_attempts_email (email),
    INDEX idx_login_attempts_attempted_at (attempted_at)
);

-- Add account lockout tracking
ALTER TABLE users
ADD COLUMN IF NOT EXISTS account_locked BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS locked_until TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS failed_login_attempts INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS last_failed_login TIMESTAMP WITH TIME ZONE;

-- Create function to check if account is locked
CREATE OR REPLACE FUNCTION is_account_locked(user_id_param UUID)
RETURNS BOOLEAN AS $$
DECLARE
    is_locked BOOLEAN;
    lock_expires TIMESTAMP WITH TIME ZONE;
BEGIN
    SELECT account_locked, locked_until
    INTO is_locked, lock_expires
    FROM users
    WHERE id = user_id_param;

    -- Account locked and lock hasn't expired
    IF is_locked AND (lock_expires IS NULL OR lock_expires > CURRENT_TIMESTAMP) THEN
        RETURN TRUE;
    END IF;

    -- Lock expired, unlock account
    IF is_locked AND lock_expires IS NOT NULL AND lock_expires <= CURRENT_TIMESTAMP THEN
        UPDATE users
        SET account_locked = FALSE,
            locked_until = NULL,
            failed_login_attempts = 0
        WHERE id = user_id_param;
    END IF;

    RETURN FALSE;
END;
$$ LANGUAGE plpgsql;

-- Create function to record failed login
CREATE OR REPLACE FUNCTION record_failed_login(
    user_id_param UUID,
    max_attempts INTEGER DEFAULT 5,
    lockout_duration_minutes INTEGER DEFAULT 30
)
RETURNS VOID AS $$
DECLARE
    current_attempts INTEGER;
BEGIN
    -- Increment failed attempts
    UPDATE users
    SET failed_login_attempts = failed_login_attempts + 1,
        last_failed_login = CURRENT_TIMESTAMP
    WHERE id = user_id_param
    RETURNING failed_login_attempts INTO current_attempts;

    -- Lock account if max attempts reached
    IF current_attempts >= max_attempts THEN
        UPDATE users
        SET account_locked = TRUE,
            locked_until = CURRENT_TIMESTAMP + (lockout_duration_minutes || ' minutes')::INTERVAL
        WHERE id = user_id_param;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Create function to reset failed login attempts (on successful login)
CREATE OR REPLACE FUNCTION reset_failed_logins(user_id_param UUID)
RETURNS VOID AS $$
BEGIN
    UPDATE users
    SET failed_login_attempts = 0,
        last_failed_login = NULL,
        account_locked = FALSE,
        locked_until = NULL
    WHERE id = user_id_param;
END;
$$ LANGUAGE plpgsql;

-- Add comments
COMMENT ON COLUMN users.two_factor_enabled IS 'Whether 2FA is enabled for this user';
COMMENT ON COLUMN users.two_factor_secret IS 'Base32-encoded TOTP secret (encrypted at rest)';
COMMENT ON COLUMN users.two_factor_backup_codes IS 'Array of SHA-256 hashed backup codes';
COMMENT ON COLUMN users.account_locked IS 'Whether account is locked due to failed login attempts';
COMMENT ON COLUMN users.locked_until IS 'Timestamp when account lock expires (30 minutes default)';
COMMENT ON TABLE login_attempts IS 'Track all login attempts for security monitoring';

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_account_locked ON users(account_locked) WHERE account_locked = TRUE;
CREATE INDEX IF NOT EXISTS idx_users_2fa_enabled ON users(two_factor_enabled) WHERE two_factor_enabled = TRUE;
