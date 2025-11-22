-- Create coach_memory table for long-term conversation summaries
CREATE TABLE IF NOT EXISTS public.coach_memory (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    summary TEXT NOT NULL,
    last_updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    
    -- Ensure one memory record per user
    CONSTRAINT unique_user_memory UNIQUE(user_id)
);

-- Enable RLS
ALTER TABLE public.coach_memory ENABLE ROW LEVEL SECURITY;

-- Policies
-- Policies
DROP POLICY IF EXISTS "Users can view own memory" ON public.coach_memory;
CREATE POLICY "Users can view own memory" ON public.coach_memory
    FOR SELECT USING (user_id IN (
        SELECT id FROM public.users WHERE firebase_uid = auth.uid()::text
    ));

DROP POLICY IF EXISTS "Users can update own memory" ON public.coach_memory;
CREATE POLICY "Users can update own memory" ON public.coach_memory
    FOR UPDATE USING (user_id IN (
        SELECT id FROM public.users WHERE firebase_uid = auth.uid()::text
    ));

DROP POLICY IF EXISTS "Users can insert own memory" ON public.coach_memory;
CREATE POLICY "Users can insert own memory" ON public.coach_memory
    FOR INSERT WITH CHECK (user_id IN (
        SELECT id FROM public.users WHERE firebase_uid = auth.uid()::text
    ));

-- Index
CREATE INDEX IF NOT EXISTS idx_coach_memory_user_id ON public.coach_memory(user_id);
