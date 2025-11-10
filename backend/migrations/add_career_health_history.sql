-- ========================================
-- Career Health Score History Table
-- ========================================
-- Tracks historical CHS scores for trend analysis

CREATE TABLE IF NOT EXISTS public.career_health_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- User reference
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,

    -- Score snapshot
    score INTEGER NOT NULL CHECK (score >= 0 AND score <= 100),
    grade VARCHAR(1) NOT NULL CHECK (grade IN ('A', 'B', 'C', 'D', 'F')),

    -- Component breakdown
    breakdown JSONB DEFAULT '{}'::jsonb,

    -- Timestamp
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_career_health_history_user_id ON public.career_health_history(user_id);
CREATE INDEX idx_career_health_history_created_at ON public.career_health_history(created_at DESC);
CREATE INDEX idx_career_health_history_user_date ON public.career_health_history(user_id, created_at DESC);

-- RLS
ALTER TABLE public.career_health_history ENABLE ROW LEVEL SECURITY;

-- Policy: Users can view their own history
CREATE POLICY "Users can view own CHS history" ON public.career_health_history
    FOR SELECT USING (auth.uid() = user_id);

-- Permissions
GRANT SELECT ON public.career_health_history TO authenticated;
GRANT ALL ON public.career_health_history TO service_role;

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Career Health History table created!';
END $$;
