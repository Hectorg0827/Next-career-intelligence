-- Supabase Database Schema for NEXT Career Intelligence
-- Run this in the Supabase SQL Editor to create the required tables

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    firebase_uid VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Analyses table
CREATE TABLE IF NOT EXISTS public.analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    job_title VARCHAR(255) NOT NULL,
    risk_score FLOAT NOT NULL,
    risk_level VARCHAR(50) NOT NULL,
    analysis_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Career Roadmaps table
CREATE TABLE IF NOT EXISTS public.career_roadmaps (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    analysis_id UUID NOT NULL REFERENCES public.analyses(id) ON DELETE CASCADE,
    roadmap_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email);
CREATE INDEX IF NOT EXISTS idx_users_firebase_uid ON public.users(firebase_uid);
CREATE INDEX IF NOT EXISTS idx_analyses_user_id ON public.analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_analyses_created_at ON public.analyses(created_at);
CREATE INDEX IF NOT EXISTS idx_career_roadmaps_user_id ON public.career_roadmaps(user_id);
CREATE INDEX IF NOT EXISTS idx_career_roadmaps_analysis_id ON public.career_roadmaps(analysis_id);

-- Enable Row Level Security (RLS)
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.career_roadmaps ENABLE ROW LEVEL SECURITY;

-- Create policies for users table (users can only access their own data)
CREATE POLICY "Users can view own profile" ON public.users
    FOR SELECT USING (auth.uid()::text = firebase_uid);

CREATE POLICY "Users can update own profile" ON public.users
    FOR UPDATE USING (auth.uid()::text = firebase_uid);

-- Create policies for analyses table
CREATE POLICY "Users can view own analyses" ON public.analyses
    FOR SELECT USING (user_id IN (
        SELECT id FROM public.users WHERE firebase_uid = auth.uid()::text
    ));

CREATE POLICY "Users can insert own analyses" ON public.analyses
    FOR INSERT WITH CHECK (user_id IN (
        SELECT id FROM public.users WHERE firebase_uid = auth.uid()::text
    ));

-- Create policies for career_roadmaps table
CREATE POLICY "Users can view own roadmaps" ON public.career_roadmaps
    FOR SELECT USING (user_id IN (
        SELECT id FROM public.users WHERE firebase_uid = auth.uid()::text
    ));

CREATE POLICY "Users can insert own roadmaps" ON public.career_roadmaps
    FOR INSERT WITH CHECK (user_id IN (
        SELECT id FROM public.users WHERE firebase_uid = auth.uid()::text
    ));

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON public.users TO anon, authenticated;
GRANT ALL ON public.analyses TO anon, authenticated;
GRANT ALL ON public.career_roadmaps TO anon, authenticated;

-- ========================================
-- PREMIUM FEATURES SCHEMA
-- Resume Studio, Career Coach, Interviewer AI
-- ========================================

-- Career Profiles (Single Source of Truth for Resume Studio)
CREATE TABLE IF NOT EXISTS public.career_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,

    -- Basic information
    full_name VARCHAR(255),
    headline VARCHAR(500),
    location VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    links JSONB DEFAULT '[]'::jsonb, -- LinkedIn, portfolio, GitHub, etc.

    -- Career data (authoritative SSOT)
    work_history JSONB DEFAULT '[]'::jsonb, -- Array of work experience objects
    education JSONB DEFAULT '[]'::jsonb,
    certifications JSONB DEFAULT '[]'::jsonb,
    skills JSONB DEFAULT '{"hard": [], "soft": [], "domains": []}'::jsonb,
    achievements JSONB DEFAULT '[]'::jsonb,

    -- Metadata
    ats_normalized BOOLEAN DEFAULT false,
    last_verified_at TIMESTAMP WITH TIME ZONE,
    sources JSONB DEFAULT '[]'::jsonb, -- Track where data came from

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,

    -- Ensure one profile per user
    CONSTRAINT unique_user_profile UNIQUE(user_id)
);

-- Resume artifacts (tailored resumes & cover letters)
CREATE TABLE IF NOT EXISTS public.resume_artifacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    profile_id UUID NOT NULL REFERENCES public.career_profiles(id) ON DELETE CASCADE,

    -- Artifact type and content
    artifact_type VARCHAR(50) NOT NULL, -- 'resume' or 'cover_letter'
    content TEXT NOT NULL, -- Markdown or plain text

    -- Context for tailoring
    job_description JSONB, -- JD details if tailored for specific job
    company_name VARCHAR(255),
    role_title VARCHAR(255),

    -- ATS and quality metrics
    ats_notes JSONB DEFAULT '[]'::jsonb,
    keyword_coverage JSONB DEFAULT '{}'::jsonb,
    risk_flags JSONB DEFAULT '[]'::jsonb,
    placeholders JSONB DEFAULT '[]'::jsonb,

    -- Profile snapshot for provenance
    profile_snapshot_id UUID, -- Reference to profile version at time of creation

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Profile suggestions (from Coach/Interviewer - require user approval)
CREATE TABLE IF NOT EXISTS public.profile_suggestions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    profile_id UUID NOT NULL REFERENCES public.career_profiles(id) ON DELETE CASCADE,

    -- Suggestion details
    source VARCHAR(50) NOT NULL, -- 'coach', 'interviewer', 'manual'
    suggestion_type VARCHAR(50) NOT NULL, -- 'bullet', 'skill', 'achievement', 'certification'

    -- Proposed change (JSON patch format)
    proposed_patch JSONB NOT NULL,

    -- Evidence and reasoning
    evidence TEXT,
    confidence_score FLOAT CHECK (confidence_score >= 0 AND confidence_score <= 1),
    reasoning TEXT,

    -- Status
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'accepted', 'rejected'
    applied_at TIMESTAMP WITH TIME ZONE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Career goals (managed by Coach)
CREATE TABLE IF NOT EXISTS public.career_goals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,

    -- Goal details (SMART format)
    goal_title VARCHAR(500) NOT NULL,
    goal_type VARCHAR(50), -- 'skill_acquisition', 'role_transition', 'salary_increase', 'certification'
    description TEXT,

    -- SMART criteria
    specific TEXT,
    measurable TEXT,
    achievable TEXT,
    relevant TEXT,
    time_bound VARCHAR(100), -- e.g., "3 months", "Q2 2025"

    -- Progress tracking
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'completed', 'paused', 'retired'
    progress_percentage INT DEFAULT 0 CHECK (progress_percentage >= 0 AND progress_percentage <= 100),

    -- Milestones
    milestones JSONB DEFAULT '[]'::jsonb,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Interview sessions (from Interviewer AI)
CREATE TABLE IF NOT EXISTS public.interview_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    profile_id UUID NOT NULL REFERENCES public.career_profiles(id) ON DELETE CASCADE,

    -- Session details
    role_title VARCHAR(255) NOT NULL,
    company_name VARCHAR(255),
    job_description JSONB,

    -- Interview type
    interview_type VARCHAR(50) DEFAULT 'behavioral', -- 'behavioral', 'technical', 'case_study'

    -- Questions and responses
    questions JSONB DEFAULT '[]'::jsonb, -- Array of Q&A objects

    -- Evidence extracted
    evidence_summaries JSONB DEFAULT '[]'::jsonb, -- Verifiable STAR statements

    -- Suggestions generated
    generated_suggestions JSONB DEFAULT '[]'::jsonb, -- Potential resume bullets

    -- Session status
    status VARCHAR(20) DEFAULT 'in_progress', -- 'in_progress', 'completed', 'abandoned'

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Coach conversations (context for coaching sessions)
CREATE TABLE IF NOT EXISTS public.coach_conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,

    -- Conversation context
    conversation_title VARCHAR(500),
    conversation_type VARCHAR(50), -- 'skill_discovery', 'goal_setting', 'resume_review', 'general'

    -- Messages
    messages JSONB DEFAULT '[]'::jsonb, -- Array of message objects {role, content, timestamp}

    -- Generated insights
    insights JSONB DEFAULT '[]'::jsonb,

    -- Status
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'archived'

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Subscription tiers (for premium feature gating)
CREATE TABLE IF NOT EXISTS public.subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,

    -- Subscription details
    tier VARCHAR(50) NOT NULL DEFAULT 'free', -- 'free', 'premium', 'enterprise'
    status VARCHAR(20) NOT NULL DEFAULT 'active', -- 'active', 'cancelled', 'expired'

    -- Billing
    stripe_subscription_id VARCHAR(255),
    stripe_customer_id VARCHAR(255),

    -- Dates
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE,
    cancelled_at TIMESTAMP WITH TIME ZONE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,

    CONSTRAINT unique_user_subscription UNIQUE(user_id)
);

-- ========================================
-- INDEXES FOR PREMIUM FEATURES
-- ========================================

CREATE INDEX IF NOT EXISTS idx_career_profiles_user_id ON public.career_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_resume_artifacts_user_id ON public.resume_artifacts(user_id);
CREATE INDEX IF NOT EXISTS idx_resume_artifacts_profile_id ON public.resume_artifacts(profile_id);
CREATE INDEX IF NOT EXISTS idx_resume_artifacts_type ON public.resume_artifacts(artifact_type);
CREATE INDEX IF NOT EXISTS idx_profile_suggestions_user_id ON public.profile_suggestions(user_id);
CREATE INDEX IF NOT EXISTS idx_profile_suggestions_status ON public.profile_suggestions(status);
CREATE INDEX IF NOT EXISTS idx_career_goals_user_id ON public.career_goals(user_id);
CREATE INDEX IF NOT EXISTS idx_career_goals_status ON public.career_goals(status);
CREATE INDEX IF NOT EXISTS idx_interview_sessions_user_id ON public.interview_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_coach_conversations_user_id ON public.coach_conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON public.subscriptions(user_id);

-- ========================================
-- ROW LEVEL SECURITY FOR PREMIUM FEATURES
-- ========================================

ALTER TABLE public.career_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.resume_artifacts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.profile_suggestions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.career_goals ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.interview_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.coach_conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.subscriptions ENABLE ROW LEVEL SECURITY;

-- Career profiles policies
CREATE POLICY "Users can view own profile" ON public.career_profiles
    FOR SELECT USING (user_id IN (
        SELECT id FROM public.users WHERE firebase_uid = auth.uid()::text
    ));

CREATE POLICY "Users can insert own profile" ON public.career_profiles
    FOR INSERT WITH CHECK (user_id IN (
        SELECT id FROM public.users WHERE firebase_uid = auth.uid()::text
    ));

CREATE POLICY "Users can update own profile" ON public.career_profiles
    FOR UPDATE USING (user_id IN (
        SELECT id FROM public.users WHERE firebase_uid = auth.uid()::text
    ));

-- Resume artifacts policies
CREATE POLICY "Users can view own artifacts" ON public.resume_artifacts
    FOR SELECT USING (user_id IN (
        SELECT id FROM public.users WHERE firebase_uid = auth.uid()::text
    ));

CREATE POLICY "Users can insert own artifacts" ON public.resume_artifacts
    FOR INSERT WITH CHECK (user_id IN (
        SELECT id FROM public.users WHERE firebase_uid = auth.uid()::text
    ));

-- Profile suggestions policies
CREATE POLICY "Users can view own suggestions" ON public.profile_suggestions
    FOR SELECT USING (user_id IN (
        SELECT id FROM public.users WHERE firebase_uid = auth.uid()::text
    ));

CREATE POLICY "Users can insert own suggestions" ON public.profile_suggestions
    FOR INSERT WITH CHECK (user_id IN (
        SELECT id FROM public.users WHERE firebase_uid = auth.uid()::text
    ));

CREATE POLICY "Users can update own suggestions" ON public.profile_suggestions
    FOR UPDATE USING (user_id IN (
        SELECT id FROM public.users WHERE firebase_uid = auth.uid()::text
    ));

-- Career goals policies
CREATE POLICY "Users can view own goals" ON public.career_goals
    FOR SELECT USING (user_id IN (
        SELECT id FROM public.users WHERE firebase_uid = auth.uid()::text
    ));

CREATE POLICY "Users can manage own goals" ON public.career_goals
    FOR ALL USING (user_id IN (
        SELECT id FROM public.users WHERE firebase_uid = auth.uid()::text
    ));

-- Interview sessions policies
CREATE POLICY "Users can view own interview sessions" ON public.interview_sessions
    FOR SELECT USING (user_id IN (
        SELECT id FROM public.users WHERE firebase_uid = auth.uid()::text
    ));

CREATE POLICY "Users can manage own interview sessions" ON public.interview_sessions
    FOR ALL USING (user_id IN (
        SELECT id FROM public.users WHERE firebase_uid = auth.uid()::text
    ));

-- Coach conversations policies
CREATE POLICY "Users can view own conversations" ON public.coach_conversations
    FOR SELECT USING (user_id IN (
        SELECT id FROM public.users WHERE firebase_uid = auth.uid()::text
    ));

CREATE POLICY "Users can manage own conversations" ON public.coach_conversations
    FOR ALL USING (user_id IN (
        SELECT id FROM public.users WHERE firebase_uid = auth.uid()::text
    ));

-- Subscriptions policies
CREATE POLICY "Users can view own subscription" ON public.subscriptions
    FOR SELECT USING (user_id IN (
        SELECT id FROM public.users WHERE firebase_uid = auth.uid()::text
    ));

-- Grant permissions for premium tables
GRANT ALL ON public.career_profiles TO anon, authenticated;
GRANT ALL ON public.resume_artifacts TO anon, authenticated;
GRANT ALL ON public.profile_suggestions TO anon, authenticated;
GRANT ALL ON public.career_goals TO anon, authenticated;
GRANT ALL ON public.interview_sessions TO anon, authenticated;
GRANT ALL ON public.coach_conversations TO anon, authenticated;
GRANT ALL ON public.subscriptions TO anon, authenticated;