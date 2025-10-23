-- Migration: Create tables for Pro features (AI Coach, Interviewer, Portfolio)
-- Purpose: Track user progress, interview sessions, and portfolio projects

-- ============================================
-- AI COACH TABLES
-- ============================================

-- User Progress Tracking (Checklist items)
DROP TABLE IF EXISTS public.user_progress CASCADE;
CREATE TABLE public.user_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    
    -- Career Path Context
    target_role VARCHAR(255) NOT NULL,
    current_role VARCHAR(255),
    
    -- Progress Item
    item_type VARCHAR(50) NOT NULL CHECK (item_type IN ('skill', 'course', 'project', 'certification', 'networking', 'other')),
    item_name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Status
    status VARCHAR(50) DEFAULT 'not_started' CHECK (status IN ('not_started', 'in_progress', 'completed', 'blocked')),
    priority INTEGER DEFAULT 5 CHECK (priority BETWEEN 1 AND 10),
    
    -- Tracking
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    due_date TIMESTAMP WITH TIME ZONE,
    time_estimate_hours INTEGER,
    
    -- Metadata
    source VARCHAR(100), -- 'ai_coach', 'user', 'course_recommendation'
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- AI Coach Chat History
DROP TABLE IF EXISTS public.coach_messages CASCADE;
CREATE TABLE public.coach_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    
    -- Context
    session_id UUID, -- Group messages into conversations
    context JSONB DEFAULT '{}', -- Store relevant user progress data for AI context
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Community Cohorts
DROP TABLE IF EXISTS public.cohorts CASCADE;
CREATE TABLE public.cohorts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Cohort Definition
    source_role VARCHAR(255) NOT NULL, -- e.g., "Accountant"
    target_role VARCHAR(255) NOT NULL, -- e.g., "Data Analyst"
    
    -- Settings
    is_active BOOLEAN DEFAULT TRUE,
    max_members INTEGER DEFAULT 50,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(source_role, target_role)
);

DROP TABLE IF EXISTS public.cohort_members CASCADE;
CREATE TABLE public.cohort_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cohort_id UUID REFERENCES public.cohorts(id) ON DELETE CASCADE NOT NULL,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    
    UNIQUE(cohort_id, user_id)
);

-- ============================================
-- AI INTERVIEWER TABLES
-- ============================================

-- Interview Sessions
DROP TABLE IF EXISTS public.interview_sessions CASCADE;
CREATE TABLE public.interview_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    
    -- Job Context
    job_title VARCHAR(255) NOT NULL,
    company_name VARCHAR(255),
    job_description TEXT,
    job_url TEXT,
    
    -- Session Status
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'completed', 'abandoned')),
    current_question_number INTEGER DEFAULT 1,
    total_questions INTEGER DEFAULT 10,
    
    -- Results
    overall_score DECIMAL(3,1), -- e.g., 7.5/10
    feedback_summary TEXT,
    strengths TEXT[],
    areas_for_improvement TEXT[],
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Individual Q&A Turns
DROP TABLE IF EXISTS public.interview_turns CASCADE;
CREATE TABLE public.interview_turns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES public.interview_sessions(id) ON DELETE CASCADE NOT NULL,
    
    turn_number INTEGER NOT NULL,
    
    -- Question
    question_text TEXT NOT NULL,
    question_category VARCHAR(100), -- 'behavioral', 'technical', 'situational'
    
    -- User Answer
    answer_text TEXT,
    answer_audio_url TEXT, -- S3/Storage URL for audio recording
    answer_duration_seconds INTEGER,
    
    -- AI Feedback
    score DECIMAL(3,1), -- e.g., 7.5/10
    feedback_text TEXT,
    feedback_details JSONB DEFAULT '{}', -- {filler_words: 12, pace: "good", star_method: true}
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- PORTFOLIO PROJECTS TABLES
-- ============================================

DROP TABLE IF EXISTS public.portfolio_projects CASCADE;
CREATE TABLE public.portfolio_projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    
    -- Project Definition
    title VARCHAR(255) NOT NULL,
    brief TEXT NOT NULL, -- AI-generated project description
    difficulty VARCHAR(20) CHECK (difficulty IN ('beginner', 'intermediate', 'advanced')),
    estimated_hours INTEGER,
    
    -- Skills Targeted
    skills_targeted TEXT[] DEFAULT ARRAY[]::TEXT[],
    target_role VARCHAR(255),
    
    -- User Submission
    status VARCHAR(50) DEFAULT 'not_started' CHECK (status IN ('not_started', 'in_progress', 'submitted', 'graded')),
    submission_url TEXT, -- GitHub, portfolio URL, etc.
    submission_notes TEXT,
    submitted_at TIMESTAMP WITH TIME ZONE,
    
    -- AI Grading
    grade_score DECIMAL(3,1), -- e.g., 8.5/10
    grade_feedback TEXT,
    grade_details JSONB DEFAULT '{}', -- {code_quality: 8, documentation: 7, functionality: 9}
    graded_at TIMESTAMP WITH TIME ZONE,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================

CREATE INDEX idx_user_progress_user_id ON public.user_progress(user_id);
CREATE INDEX idx_user_progress_status ON public.user_progress(status);
CREATE INDEX idx_user_progress_target_role ON public.user_progress(target_role);

CREATE INDEX idx_coach_messages_user_id ON public.coach_messages(user_id);
CREATE INDEX idx_coach_messages_session_id ON public.coach_messages(session_id);

CREATE INDEX idx_cohorts_roles ON public.cohorts(source_role, target_role);
CREATE INDEX idx_cohort_members_user_id ON public.cohort_members(user_id);

CREATE INDEX idx_interview_sessions_user_id ON public.interview_sessions(user_id);
CREATE INDEX idx_interview_sessions_status ON public.interview_sessions(status);
CREATE INDEX idx_interview_turns_session_id ON public.interview_turns(session_id);

CREATE INDEX idx_portfolio_projects_user_id ON public.portfolio_projects(user_id);
CREATE INDEX idx_portfolio_projects_status ON public.portfolio_projects(status);

-- ============================================
-- ROW LEVEL SECURITY
-- ============================================

-- User Progress
ALTER TABLE public.user_progress ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own progress" ON public.user_progress FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own progress" ON public.user_progress FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Service role can manage all progress" ON public.user_progress FOR ALL USING (current_user = 'postgres');

-- Coach Messages
ALTER TABLE public.coach_messages ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own messages" ON public.coach_messages FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can create own messages" ON public.coach_messages FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Service role can manage all messages" ON public.coach_messages FOR ALL USING (current_user = 'postgres');

-- Interview Sessions
ALTER TABLE public.interview_sessions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own sessions" ON public.interview_sessions FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own sessions" ON public.interview_sessions FOR ALL USING (auth.uid() = user_id);

-- Interview Turns
ALTER TABLE public.interview_turns ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own turns" ON public.interview_turns FOR SELECT 
    USING (EXISTS (SELECT 1 FROM public.interview_sessions WHERE id = session_id AND user_id = auth.uid()));
CREATE POLICY "Users can create own turns" ON public.interview_turns FOR INSERT 
    WITH CHECK (EXISTS (SELECT 1 FROM public.interview_sessions WHERE id = session_id AND user_id = auth.uid()));

-- Portfolio Projects
ALTER TABLE public.portfolio_projects ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own projects" ON public.portfolio_projects FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own projects" ON public.portfolio_projects FOR ALL USING (auth.uid() = user_id);

-- Cohorts (public read, service write)
ALTER TABLE public.cohorts ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Anyone can view cohorts" ON public.cohorts FOR SELECT USING (true);
CREATE POLICY "Service role can manage cohorts" ON public.cohorts FOR ALL USING (current_user = 'postgres');

-- Cohort Members
ALTER TABLE public.cohort_members ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view cohort members" ON public.cohort_members FOR SELECT USING (true);
CREATE POLICY "Users can join cohorts" ON public.cohort_members FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Service role can manage members" ON public.cohort_members FOR ALL USING (current_user = 'postgres');

-- Grant permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON public.user_progress TO authenticated, service_role;
GRANT SELECT, INSERT ON public.coach_messages TO authenticated, service_role;
GRANT SELECT, INSERT, UPDATE ON public.interview_sessions TO authenticated, service_role;
GRANT SELECT, INSERT ON public.interview_turns TO authenticated, service_role;
GRANT SELECT, INSERT, UPDATE ON public.portfolio_projects TO authenticated, service_role;
GRANT SELECT ON public.cohorts TO authenticated, service_role;
GRANT SELECT, INSERT, UPDATE ON public.cohort_members TO authenticated, service_role;
