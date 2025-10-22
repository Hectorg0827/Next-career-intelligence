-- Migration: Create password_resets table
-- Purpose: Store password reset tokens for account recovery
-- RLS: Service role manages resets, users cannot directly access

DROP TABLE IF EXISTS public.password_resets CASCADE;

CREATE TABLE public.password_resets (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Reference to users
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    
    -- Reset Data
    email VARCHAR(255) NOT NULL,
    reset_token VARCHAR(255) NOT NULL UNIQUE,
    
    -- Expiration
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (CURRENT_TIMESTAMP + INTERVAL '1 hour'),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Usage Tracking
    is_used BOOLEAN DEFAULT FALSE,
    used_at TIMESTAMP WITH TIME ZONE,
    attempt_count INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3
);

-- Create indexes for performance
CREATE INDEX idx_password_resets_email ON public.password_resets(email);
CREATE INDEX idx_password_resets_token ON public.password_resets(reset_token);
CREATE INDEX idx_password_resets_user_id ON public.password_resets(user_id);
CREATE INDEX idx_password_resets_expires_at ON public.password_resets(expires_at);

-- Enable Row Level Security
ALTER TABLE public.password_resets ENABLE ROW LEVEL SECURITY;

-- Policy: Service role can manage all resets
CREATE POLICY "Service role can manage password resets"
    ON public.password_resets
    FOR ALL
    USING (current_user = 'postgres');

-- Grant permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON public.password_resets TO service_role;

-- Auto-cleanup expired reset requests
CREATE OR REPLACE FUNCTION public.cleanup_expired_password_resets()
RETURNS void AS $$
BEGIN
    DELETE FROM public.password_resets
    WHERE expires_at < CURRENT_TIMESTAMP AND NOT is_used;
END;
$$ LANGUAGE plpgsql;
