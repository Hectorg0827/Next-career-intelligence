-- Phase 1: Foundation Layer - Database Schema
-- This adds event tracking, journey analytics, and profile versioning

-- ========================================
-- EVENT STORE
-- ========================================

-- Store every user interaction for replay, analytics, and AI learning
CREATE TABLE IF NOT EXISTS public.career_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    
    -- Event metadata
    event_type VARCHAR(100) NOT NULL, -- job_viewed, skill_added, goal_created, etc.
    event_category VARCHAR(50) NOT NULL, -- user_action, system_event, ai_interaction
    
    -- Event data (flexible JSONB)
    event_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    
    -- Context
    session_id UUID, -- Groups related events in one session
    source VARCHAR(50), -- dashboard, job_search, coach, etc.
    
    -- Metadata
    user_agent TEXT,
    ip_address INET,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    
    -- Indexing for fast queries
    INDEX idx_career_events_user_id (user_id),
    INDEX idx_career_events_type (event_type),
    INDEX idx_career_events_category (event_category),
    INDEX idx_career_events_session (session_id),
    INDEX idx_career_events_created (created_at DESC)
);

-- Event types enum (for documentation - actual validation in app layer)
COMMENT ON COLUMN public.career_events.event_type IS 
'Event types:
USER_ACTION: job_viewed, job_saved, job_applied, job_rejected, search_performed, filter_changed
PROFILE: profile_updated, skill_added, goal_created, goal_completed, work_history_added
AI: analysis_requested, roadmap_generated, coach_message, interview_session
SYSTEM: recommendation_generated, notification_sent, email_sent';

-- ========================================
-- USER SESSIONS
-- ========================================

-- Track user sessions for grouping events and understanding behavior patterns
CREATE TABLE IF NOT EXISTS public.user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    
    -- Session data
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    ended_at TIMESTAMP WITH TIME ZONE,
    duration_seconds INT,
    
    -- Context
    device_type VARCHAR(50), -- desktop, mobile, tablet
    browser VARCHAR(100),
    os VARCHAR(100),
    referrer TEXT,
    entry_page VARCHAR(255),
    exit_page VARCHAR(255),
    
    -- Engagement metrics
    pages_visited INT DEFAULT 0,
    events_count INT DEFAULT 0,
    features_used JSONB DEFAULT '[]'::jsonb, -- List of features used in session
    
    -- Indexes
    INDEX idx_user_sessions_user_id (user_id),
    INDEX idx_user_sessions_started (started_at DESC)
);

-- ========================================
-- PROFILE VERSION HISTORY
-- ========================================

-- Track all changes to career profiles for audit and rollback
CREATE TABLE IF NOT EXISTS public.career_profile_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES public.career_profiles(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    
    -- Version data
    version_number INT NOT NULL,
    profile_snapshot JSONB NOT NULL, -- Complete profile at this version
    
    -- Change metadata
    changed_fields JSONB, -- List of fields that changed
    change_source VARCHAR(50), -- manual, ai_suggestion, resume_upload, etc.
    change_reason TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    
    -- Indexes
    INDEX idx_profile_versions_profile_id (profile_id),
    INDEX idx_profile_versions_user_id (user_id),
    INDEX idx_profile_versions_created (created_at DESC),
    
    -- Ensure sequential versioning per profile
    UNIQUE(profile_id, version_number)
);

-- ========================================
-- USER JOURNEY ANALYTICS
-- ========================================

-- Aggregated metrics for understanding user journey and patterns
CREATE TABLE IF NOT EXISTS public.user_journey_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    
    -- Time period
    metric_date DATE NOT NULL,
    week_start DATE,
    month_start DATE,
    
    -- Engagement metrics
    sessions_count INT DEFAULT 0,
    total_time_seconds INT DEFAULT 0,
    events_count INT DEFAULT 0,
    
    -- Feature usage
    features_used JSONB DEFAULT '{}'::jsonb, -- {feature_name: count}
    
    -- Job search activity
    jobs_viewed_count INT DEFAULT 0,
    jobs_saved_count INT DEFAULT 0,
    jobs_applied_count INT DEFAULT 0,
    searches_performed_count INT DEFAULT 0,
    
    -- AI interactions
    coach_messages_count INT DEFAULT 0,
    analyses_requested_count INT DEFAULT 0,
    roadmaps_generated_count INT DEFAULT 0,
    
    -- Profile activity
    profile_updates_count INT DEFAULT 0,
    skills_added_count INT DEFAULT 0,
    goals_created_count INT DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    
    -- Indexes
    INDEX idx_journey_metrics_user_id (user_id),
    INDEX idx_journey_metrics_date (metric_date DESC),
    
    -- One row per user per day
    UNIQUE(user_id, metric_date)
);

-- ========================================
-- CAREER MILESTONES
-- ========================================

-- Track significant events in user's career journey
CREATE TABLE IF NOT EXISTS public.career_milestones (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    
    -- Milestone data
    milestone_type VARCHAR(50) NOT NULL, -- goal_completed, job_applied, skill_mastered, etc.
    title VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Context
    related_entity_type VARCHAR(50), -- goal, job, skill, etc.
    related_entity_id UUID,
    
    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,
    
    -- Timestamps
    achieved_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    
    -- Indexes
    INDEX idx_milestones_user_id (user_id),
    INDEX idx_milestones_type (milestone_type),
    INDEX idx_milestones_achieved (achieved_at DESC)
);

-- ========================================
-- PROFILE COMPLETENESS TRACKING
-- ========================================

-- Track profile completeness over time to encourage engagement
CREATE TABLE IF NOT EXISTS public.profile_completeness_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    profile_id UUID NOT NULL REFERENCES public.career_profiles(id) ON DELETE CASCADE,
    
    -- Completeness metrics
    overall_score INT NOT NULL CHECK (overall_score >= 0 AND overall_score <= 100),
    
    -- Section scores
    basics_score INT DEFAULT 0,
    work_history_score INT DEFAULT 0,
    education_score INT DEFAULT 0,
    skills_score INT DEFAULT 0,
    achievements_score INT DEFAULT 0,
    
    -- Missing critical fields
    missing_fields JSONB DEFAULT '[]'::jsonb,
    
    -- Timestamps
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    
    -- Indexes
    INDEX idx_completeness_user_id (user_id),
    INDEX idx_completeness_profile_id (profile_id),
    INDEX idx_completeness_calculated (calculated_at DESC)
);

-- ========================================
-- ROW LEVEL SECURITY (RLS)
-- ========================================

-- Enable RLS on all new tables
ALTER TABLE public.career_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.career_profile_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_journey_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.career_milestones ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.profile_completeness_history ENABLE ROW LEVEL SECURITY;

-- Policies for career_events
CREATE POLICY "Users can view own events" ON public.career_events
    FOR SELECT USING (user_id IN (
        SELECT id FROM public.users WHERE firebase_uid = auth.uid()::text
    ));

CREATE POLICY "System can insert events" ON public.career_events
    FOR INSERT WITH CHECK (true); -- Allow backend to insert events

-- Policies for user_sessions
CREATE POLICY "Users can view own sessions" ON public.user_sessions
    FOR SELECT USING (user_id IN (
        SELECT id FROM public.users WHERE firebase_uid = auth.uid()::text
    ));

CREATE POLICY "System can manage sessions" ON public.user_sessions
    FOR ALL USING (true); -- Allow backend to manage sessions

-- Policies for career_profile_versions
CREATE POLICY "Users can view own profile versions" ON public.career_profile_versions
    FOR SELECT USING (user_id IN (
        SELECT id FROM public.users WHERE firebase_uid = auth.uid()::text
    ));

-- Policies for user_journey_metrics
CREATE POLICY "Users can view own metrics" ON public.user_journey_metrics
    FOR SELECT USING (user_id IN (
        SELECT id FROM public.users WHERE firebase_uid = auth.uid()::text
    ));

-- Policies for career_milestones
CREATE POLICY "Users can view own milestones" ON public.career_milestones
    FOR SELECT USING (user_id IN (
        SELECT id FROM public.users WHERE firebase_uid = auth.uid()::text
    ));

-- Policies for profile_completeness_history
CREATE POLICY "Users can view own completeness history" ON public.profile_completeness_history
    FOR SELECT USING (user_id IN (
        SELECT id FROM public.users WHERE firebase_uid = auth.uid()::text
    ));

-- ========================================
-- FUNCTIONS & TRIGGERS
-- ========================================

-- Function to update journey metrics when events are created
CREATE OR REPLACE FUNCTION update_journey_metrics()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.user_journey_metrics (
        user_id,
        metric_date,
        week_start,
        month_start,
        events_count
    ) VALUES (
        NEW.user_id,
        CURRENT_DATE,
        date_trunc('week', CURRENT_DATE),
        date_trunc('month', CURRENT_DATE),
        1
    )
    ON CONFLICT (user_id, metric_date) 
    DO UPDATE SET
        events_count = user_journey_metrics.events_count + 1,
        updated_at = NOW();
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update metrics
CREATE TRIGGER trigger_update_journey_metrics
AFTER INSERT ON public.career_events
FOR EACH ROW
EXECUTE FUNCTION update_journey_metrics();

-- Function to create profile version on update
CREATE OR REPLACE FUNCTION create_profile_version()
RETURNS TRIGGER AS $$
DECLARE
    version_num INT;
BEGIN
    -- Get next version number
    SELECT COALESCE(MAX(version_number), 0) + 1 
    INTO version_num
    FROM public.career_profile_versions 
    WHERE profile_id = NEW.id;
    
    -- Insert version snapshot
    INSERT INTO public.career_profile_versions (
        profile_id,
        user_id,
        version_number,
        profile_snapshot,
        change_source,
        created_at
    ) VALUES (
        NEW.id,
        NEW.user_id,
        version_num,
        row_to_json(NEW)::jsonb,
        COALESCE(current_setting('app.change_source', true), 'unknown'),
        NOW()
    );
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically version profiles
CREATE TRIGGER trigger_version_profile
AFTER UPDATE ON public.career_profiles
FOR EACH ROW
WHEN (OLD.* IS DISTINCT FROM NEW.*)
EXECUTE FUNCTION create_profile_version();

-- ========================================
-- INDEXES FOR PERFORMANCE
-- ========================================

-- GIN indexes for JSONB columns (fast search within JSON)
CREATE INDEX IF NOT EXISTS idx_career_events_data_gin ON public.career_events USING GIN (event_data);
CREATE INDEX IF NOT EXISTS idx_profile_versions_snapshot_gin ON public.career_profile_versions USING GIN (profile_snapshot);
CREATE INDEX IF NOT EXISTS idx_journey_metrics_features_gin ON public.user_journey_metrics USING GIN (features_used);

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_events_user_type_date 
    ON public.career_events (user_id, event_type, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_sessions_user_date 
    ON public.user_sessions (user_id, started_at DESC);

-- ========================================
-- GRANTS
-- ========================================

GRANT ALL ON public.career_events TO anon, authenticated;
GRANT ALL ON public.user_sessions TO anon, authenticated;
GRANT ALL ON public.career_profile_versions TO anon, authenticated;
GRANT ALL ON public.user_journey_metrics TO anon, authenticated;
GRANT ALL ON public.career_milestones TO anon, authenticated;
GRANT ALL ON public.profile_completeness_history TO anon, authenticated;

-- ========================================
-- COMMENTS FOR DOCUMENTATION
-- ========================================

COMMENT ON TABLE public.career_events IS 'Event store for all user interactions - foundation for learning and analytics';
COMMENT ON TABLE public.user_sessions IS 'User session tracking for engagement analytics';
COMMENT ON TABLE public.career_profile_versions IS 'Version history of career profiles for audit and rollback';
COMMENT ON TABLE public.user_journey_metrics IS 'Aggregated daily metrics for user journey analytics';
COMMENT ON TABLE public.career_milestones IS 'Significant achievements in user career journey';
COMMENT ON TABLE public.profile_completeness_history IS 'Track profile completeness over time';
