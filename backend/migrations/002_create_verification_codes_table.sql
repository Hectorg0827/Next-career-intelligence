-- Migration: Create verification_codes table
-- Purpose: Store email verification codes for user sign-up flow
-- RLS: Service role manages codes, users cannot directly access

DROP TABLE IF EXISTS public.verification_codes CASCADE;

CREATE TABLE public.verification_codes (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Reference to users
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    
    -- Verification Data
    email VARCHAR(255) NOT NULL,
    code VARCHAR(6) NOT NULL, -- 6-digit code
    
    -- Expiration
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (CURRENT_TIMESTAMP + INTERVAL '15 minutes'),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Usage Tracking
    is_used BOOLEAN DEFAULT FALSE,
    used_at TIMESTAMP WITH TIME ZONE,
    attempt_count INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 5
);

-- Create indexes for performance
CREATE INDEX idx_verification_codes_email ON public.verification_codes(email);
CREATE INDEX idx_verification_codes_code ON public.verification_codes(code);
CREATE INDEX idx_verification_codes_user_id ON public.verification_codes(user_id);
CREATE INDEX idx_verification_codes_email_code ON public.verification_codes(email, code);
CREATE INDEX idx_verification_codes_expires_at ON public.verification_codes(expires_at);

-- Enable Row Level Security
ALTER TABLE public.verification_codes ENABLE ROW LEVEL SECURITY;

-- Policy: Service role can manage all codes
CREATE POLICY "Service role can manage verification codes"
    ON public.verification_codes
    FOR ALL
    USING (current_user = 'postgres');

-- Grant permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON public.verification_codes TO service_role;

-- Auto-cleanup expired codes (via trigger or scheduled function)
CREATE OR REPLACE FUNCTION public.cleanup_expired_verification_codes()
RETURNS void AS $$
BEGIN
    DELETE FROM public.verification_codes
    WHERE expires_at < CURRENT_TIMESTAMP AND NOT is_used;
END;
$$ LANGUAGE plpgsql;
