-- Migration: Add subscription management fields to users table
-- Purpose: Enable freemium model with subscription tracking

-- Add subscription fields to users table
ALTER TABLE public.users 
ADD COLUMN IF NOT EXISTS subscription_status VARCHAR(20) DEFAULT 'free' CHECK (subscription_status IN ('free', 'pro', 'enterprise')),
ADD COLUMN IF NOT EXISTS subscription_started_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS subscription_ends_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS last_free_analysis_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS stripe_customer_id VARCHAR(255) UNIQUE,
ADD COLUMN IF NOT EXISTS stripe_subscription_id VARCHAR(255),
ADD COLUMN IF NOT EXISTS free_reports_used INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS trial_ends_at TIMESTAMP WITH TIME ZONE;

-- Create index for subscription queries
CREATE INDEX IF NOT EXISTS idx_users_subscription_status ON public.users(subscription_status);
CREATE INDEX IF NOT EXISTS idx_users_stripe_customer_id ON public.users(stripe_customer_id);
CREATE INDEX IF NOT EXISTS idx_users_subscription_ends_at ON public.users(subscription_ends_at);

-- Add comment
COMMENT ON COLUMN public.users.subscription_status IS 'User subscription tier: free (1 report), pro (unlimited), enterprise (B2B)';
COMMENT ON COLUMN public.users.free_reports_used IS 'Number of free reports used (max 1 for free tier)';
COMMENT ON COLUMN public.users.last_free_analysis_at IS 'Timestamp of last free analysis to track usage';
