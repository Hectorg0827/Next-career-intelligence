-- Migration: Create onboarding table
-- Purpose: Track user onboarding progress through career intelligence platform
-- RLS: Users can only view/edit their own onboarding data

DROP TABLE IF EXISTS public.onboarding CASCADE;

CREATE TABLE public.onboarding (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Reference to users
    user_id UUID UNIQUE REFERENCES public.users(id) ON DELETE CASCADE,
    
    -- Onboarding Progress
    is_complete BOOLEAN DEFAULT FALSE,
    current_step INTEGER DEFAULT 1, -- 1-4
    steps_completed INTEGER[] DEFAULT ARRAY[]::INTEGER[],
    
    -- Career Information (Step 1)
    current_role VARCHAR(255),
    years_experience INTEGER,
    industry VARCHAR(255),
    employment_type VARCHAR(50), -- full-time, part-time, freelance, etc.
    
    -- Skills & Interests (Step 2)
    skills TEXT[] DEFAULT ARRAY[]::TEXT[],
    interests TEXT[] DEFAULT ARRAY[]::TEXT[],
    
    -- Career Goals (Step 3)
    career_goals TEXT[] DEFAULT ARRAY[]::TEXT[],
    target_roles TEXT[] DEFAULT ARRAY[]::TEXT[],
    job_search_status VARCHAR(50), -- active, passive, not-looking
    
    -- Preferences (Step 4)
    preferences JSONB DEFAULT '{
        "salary_min": 0,
        "salary_max": 0,
        "work_location": "any",
        "remote_preference": "any",
        "industry_preferences": [],
        "company_size": "any",
        "notifications_enabled": true
    }',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Metadata
    metadata JSONB DEFAULT '{}'
);

-- Create indexes for performance
CREATE INDEX idx_onboarding_user_id ON public.onboarding(user_id);
CREATE INDEX idx_onboarding_is_complete ON public.onboarding(is_complete);
CREATE INDEX idx_onboarding_created_at ON public.onboarding(created_at);
CREATE INDEX idx_onboarding_skills ON public.onboarding USING GIN (skills);
CREATE INDEX idx_onboarding_interests ON public.onboarding USING GIN (interests);

-- Enable Row Level Security
ALTER TABLE public.onboarding ENABLE ROW LEVEL SECURITY;

-- Policy: Users can view only their own onboarding data
CREATE POLICY "Users can view their own onboarding"
    ON public.onboarding
    FOR SELECT
    USING (auth.uid() = user_id OR current_user = 'postgres');

-- Policy: Users can update only their own onboarding data
CREATE POLICY "Users can update their own onboarding"
    ON public.onboarding
    FOR UPDATE
    USING (auth.uid() = user_id OR current_user = 'postgres');

-- Policy: Service role can manage all onboarding
CREATE POLICY "Service role can manage all onboarding"
    ON public.onboarding
    FOR ALL
    USING (current_user = 'postgres');

-- Grant permissions
GRANT SELECT, INSERT, UPDATE ON public.onboarding TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.onboarding TO service_role;

-- Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION public.update_onboarding_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    IF NEW.is_complete AND OLD.is_complete IS FALSE THEN
        NEW.completed_at = CURRENT_TIMESTAMP;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER onboarding_updated_at_trigger
BEFORE UPDATE ON public.onboarding
FOR EACH ROW
EXECUTE FUNCTION public.update_onboarding_timestamp();
