-- ========================================
-- RFT (Reinforcement Fine-Tuning) System
-- Database Schema Migration
-- ========================================
-- Run this in Supabase SQL Editor after APPLY_THIS_SQL.sql

-- ========================================
-- 1. RFT Feedback Events Table
-- ========================================
-- Captures all user feedback signals for training

CREATE TABLE IF NOT EXISTS public.rft_feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- User context
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,

    -- Event metadata
    event_type VARCHAR(50) NOT NULL,  -- 'resume_bullet_accepted', 'resume_bullet_rejected', 'interview_answer_rated', etc.
    agent_name VARCHAR(50) NOT NULL,  -- 'resume_studio', 'interviewer_ai', 'career_coach', etc.

    -- Input/Output pairs for training
    prompt TEXT NOT NULL,  -- The input to the AI model
    model_output TEXT NOT NULL,  -- What the AI generated
    preferred_output TEXT,  -- What user wanted (NULL if accepted model output)

    -- Feedback signals
    user_rating INTEGER CHECK (user_rating >= 1 AND user_rating <= 5),
    user_accepted BOOLEAN,
    user_edited BOOLEAN DEFAULT false,

    -- Context (for conditional training)
    context_data JSONB DEFAULT '{}'::jsonb,  -- Job description, user profile snapshot, etc.

    -- Ultimate success signals (retroactively updated)
    led_to_interview BOOLEAN DEFAULT false,
    led_to_offer BOOLEAN DEFAULT false,
    led_to_goal_completion BOOLEAN DEFAULT false,

    -- Related entities (for linking feedback to outcomes)
    related_job_id UUID REFERENCES public.jobs(id) ON DELETE SET NULL,
    related_application_id UUID REFERENCES public.job_applications(id) ON DELETE SET NULL,
    related_session_id UUID,  -- For interview sessions

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_rft_feedback_user_id ON public.rft_feedback(user_id);
CREATE INDEX idx_rft_feedback_event_type ON public.rft_feedback(event_type);
CREATE INDEX idx_rft_feedback_agent_name ON public.rft_feedback(agent_name);
CREATE INDEX idx_rft_feedback_created_at ON public.rft_feedback(created_at DESC);
CREATE INDEX idx_rft_feedback_user_accepted ON public.rft_feedback(user_accepted) WHERE user_accepted = true;
CREATE INDEX idx_rft_feedback_success_signals ON public.rft_feedback(led_to_interview, led_to_offer);

-- Enable GIN index on context_data JSONB
CREATE INDEX idx_rft_feedback_context_gin ON public.rft_feedback USING gin(context_data);

-- ========================================
-- 2. RFT Model Versions Table
-- ========================================
-- Tracks different versions of fine-tuned models

CREATE TABLE IF NOT EXISTS public.rft_model_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Model identification
    agent_name VARCHAR(50) NOT NULL,  -- Which agent this model is for
    model_name VARCHAR(100) NOT NULL,  -- e.g., 'gemini-2.0-pro-RFT-v1'
    model_type VARCHAR(50) NOT NULL,  -- 'gemini', 'openai', 'custom'

    -- Training metadata
    trained_on_feedback_count INTEGER NOT NULL,
    training_start_date TIMESTAMP WITH TIME ZONE NOT NULL,
    training_end_date TIMESTAMP WITH TIME ZONE NOT NULL,
    training_duration_minutes INTEGER,

    -- Performance metrics
    validation_accuracy FLOAT,
    validation_loss FLOAT,
    user_acceptance_rate FLOAT,  -- % of outputs users accepted
    improvement_over_baseline FLOAT,  -- % better than non-fine-tuned model

    -- Training configuration
    hyperparameters JSONB DEFAULT '{}'::jsonb,  -- Learning rate, batch size, etc.

    -- Deployment status
    is_active BOOLEAN DEFAULT false,  -- Only one active model per agent
    deployed_at TIMESTAMP WITH TIME ZONE,
    deprecated_at TIMESTAMP WITH TIME ZONE,

    -- Version info
    version_number INTEGER NOT NULL,
    parent_version_id UUID REFERENCES public.rft_model_versions(id) ON DELETE SET NULL,

    -- Notes
    training_notes TEXT,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_rft_model_versions_agent_name ON public.rft_model_versions(agent_name);
CREATE INDEX idx_rft_model_versions_is_active ON public.rft_model_versions(is_active) WHERE is_active = true;
CREATE INDEX idx_rft_model_versions_version_number ON public.rft_model_versions(agent_name, version_number);

-- Unique constraint: Only one active model per agent
CREATE UNIQUE INDEX idx_rft_model_versions_active_per_agent
    ON public.rft_model_versions(agent_name, is_active)
    WHERE is_active = true;

-- ========================================
-- 3. RFT Training Jobs Table
-- ========================================
-- Tracks scheduled and running training jobs

CREATE TABLE IF NOT EXISTS public.rft_training_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Job info
    agent_name VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',  -- 'pending', 'running', 'completed', 'failed'

    -- Training parameters
    feedback_count INTEGER NOT NULL,  -- How many feedback examples to train on
    feedback_start_date TIMESTAMP WITH TIME ZONE,
    feedback_end_date TIMESTAMP WITH TIME ZONE,

    -- Results
    resulting_model_id UUID REFERENCES public.rft_model_versions(id) ON DELETE SET NULL,
    error_message TEXT,

    -- Scheduling
    scheduled_at TIMESTAMP WITH TIME ZONE,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_rft_training_jobs_status ON public.rft_training_jobs(status);
CREATE INDEX idx_rft_training_jobs_agent_name ON public.rft_training_jobs(agent_name);
CREATE INDEX idx_rft_training_jobs_scheduled_at ON public.rft_training_jobs(scheduled_at);

-- ========================================
-- 4. Row Level Security (RLS)
-- ========================================

ALTER TABLE public.rft_feedback ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.rft_model_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.rft_training_jobs ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only read their own feedback
CREATE POLICY "Users can view own feedback" ON public.rft_feedback
    FOR SELECT USING (auth.uid() = user_id);

-- Policy: Users can insert their own feedback
CREATE POLICY "Users can create own feedback" ON public.rft_feedback
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Policy: Service role can update feedback (for retroactive success signals)
-- This is handled via service_role key, no RLS policy needed

-- Policy: Anyone can view active model versions
CREATE POLICY "Anyone can view active models" ON public.rft_model_versions
    FOR SELECT USING (is_active = true);

-- Policy: Only service role can manage models and training jobs
-- (No policies needed - service_role bypasses RLS)

-- ========================================
-- 5. Permissions
-- ========================================

GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT SELECT ON public.rft_feedback TO authenticated;
GRANT INSERT ON public.rft_feedback TO authenticated;
GRANT SELECT ON public.rft_model_versions TO anon, authenticated;

GRANT ALL ON public.rft_feedback TO service_role;
GRANT ALL ON public.rft_model_versions TO service_role;
GRANT ALL ON public.rft_training_jobs TO service_role;

-- ========================================
-- 6. Trigger: Auto-update updated_at
-- ========================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_rft_feedback_updated_at BEFORE UPDATE ON public.rft_feedback
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_rft_model_versions_updated_at BEFORE UPDATE ON public.rft_model_versions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ========================================
-- 7. Initial Data: Baseline Model
-- ========================================

INSERT INTO public.rft_model_versions (
    agent_name,
    model_name,
    model_type,
    trained_on_feedback_count,
    training_start_date,
    training_end_date,
    version_number,
    is_active,
    deployed_at,
    training_notes
) VALUES
(
    'resume_studio',
    'gemini-2.0-flash-exp',
    'gemini',
    0,  -- Baseline model, not fine-tuned
    NOW(),
    NOW(),
    0,  -- Version 0 = baseline
    true,
    NOW(),
    'Baseline model before any fine-tuning'
),
(
    'interviewer_ai',
    'gemini-2.0-flash-exp',
    'gemini',
    0,
    NOW(),
    NOW(),
    0,
    true,
    NOW(),
    'Baseline model before any fine-tuning'
),
(
    'career_coach',
    'gemini-2.0-flash-exp',
    'gemini',
    0,
    NOW(),
    NOW(),
    0,
    true,
    NOW(),
    'Baseline model before any fine-tuning'
);

-- ========================================
-- Success Message
-- ========================================

DO $$
BEGIN
    RAISE NOTICE '✅ RFT System tables created successfully!';
    RAISE NOTICE '📊 Tables: rft_feedback, rft_model_versions, rft_training_jobs';
    RAISE NOTICE '🔒 RLS policies enabled';
    RAISE NOTICE '🎯 Ready to start collecting feedback data';
    RAISE NOTICE '';
    RAISE NOTICE 'Next steps:';
    RAISE NOTICE '1. Implement frontend event tracking (RFTTracker)';
    RAISE NOTICE '2. Create backend /api/rft/feedback endpoint';
    RAISE NOTICE '3. Build grader functions for quality scoring';
    RAISE NOTICE '4. Schedule weekly training jobs';
END $$;
