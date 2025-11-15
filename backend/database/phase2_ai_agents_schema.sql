-- ============================================================================
-- Phase 2: Autonomous AI Agents - Database Schema
-- ============================================================================
-- This schema supports AI-powered intelligence layer including:
-- - Semantic memory storage
-- - Recommendation caching
-- - Guidance history
-- - Prediction models
-- ============================================================================

-- AI Memory Table
-- Stores learned patterns from events as semantic embeddings
CREATE TABLE IF NOT EXISTS ai_memory (
    memory_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    embedding VECTOR(768),  -- Gemini embedding dimension
    memory_type VARCHAR(50) NOT NULL, -- job_preferences, career_evolution, etc.
    source_events UUID[] NOT NULL,  -- References to career_events
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Index for vector similarity search
    -- Note: Requires pgvector extension
    INDEX idx_ai_memory_user ON ai_memory(user_id),
    INDEX idx_ai_memory_type ON ai_memory(memory_type),
    INDEX idx_ai_memory_created ON ai_memory(created_at DESC)
);

-- Enable vector similarity search (if pgvector available)
-- CREATE INDEX ON ai_memory USING ivfflat (embedding vector_cosine_ops);

COMMENT ON TABLE ai_memory IS 'Semantic memory formed from user behavior patterns';
COMMENT ON COLUMN ai_memory.embedding IS 'Vector embedding for semantic similarity search';
COMMENT ON COLUMN ai_memory.source_events IS 'Array of event IDs that formed this memory';


-- Job Recommendations Cache
-- Stores AI-generated recommendations with scores
CREATE TABLE IF NOT EXISTS job_recommendations (
    recommendation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    job_id UUID NOT NULL,  -- References jobs table
    recommendation_score DECIMAL(5,2) NOT NULL, -- 0-100
    match_reasons TEXT[] NOT NULL,
    growth_potential TEXT,
    confidence DECIMAL(3,2) NOT NULL, -- 0-1
    component_scores JSONB NOT NULL DEFAULT '{}', -- skill, behavioral, goal, etc.
    is_stretch BOOLEAN DEFAULT FALSE,
    shown_to_user BOOLEAN DEFAULT FALSE,
    user_clicked BOOLEAN DEFAULT FALSE,
    user_applied BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL DEFAULT NOW() + INTERVAL '7 days',
    
    -- Constraints
    CONSTRAINT valid_score CHECK (recommendation_score >= 0 AND recommendation_score <= 100),
    CONSTRAINT valid_confidence CHECK (confidence >= 0 AND confidence <= 1),
    
    -- Indexes
    INDEX idx_job_recs_user ON job_recommendations(user_id),
    INDEX idx_job_recs_score ON job_recommendations(recommendation_score DESC),
    INDEX idx_job_recs_expires ON job_recommendations(expires_at),
    
    -- Prevent duplicate recommendations
    UNIQUE(user_id, job_id, created_at)
);

COMMENT ON TABLE job_recommendations IS 'AI-generated job recommendations with scoring';
COMMENT ON COLUMN job_recommendations.recommendation_score IS 'Overall match score (0-100)';
COMMENT ON COLUMN job_recommendations.confidence IS 'Model confidence in recommendation (0-1)';


-- Proactive Guidance History
-- Tracks guidance messages shown to users
CREATE TABLE IF NOT EXISTS guidance_history (
    guidance_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    guidance_type VARCHAR(50) NOT NULL, -- profile_completion, application_coaching, etc.
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    priority INT NOT NULL, -- 1-5, 5=urgent
    shown_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    clicked BOOLEAN DEFAULT FALSE,
    clicked_at TIMESTAMPTZ,
    dismissed BOOLEAN DEFAULT FALSE,
    dismissed_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}',
    
    -- Indexes
    INDEX idx_guidance_user ON guidance_history(user_id),
    INDEX idx_guidance_type ON guidance_history(guidance_type),
    INDEX idx_guidance_shown ON guidance_history(shown_at DESC)
);

COMMENT ON TABLE guidance_history IS 'History of proactive guidance shown to users';
COMMENT ON COLUMN guidance_history.priority IS 'Urgency level 1-5, where 5 is most urgent';


-- Churn Predictions
-- Stores churn risk predictions for users
CREATE TABLE IF NOT EXISTS churn_predictions (
    prediction_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    risk_level VARCHAR(20) NOT NULL, -- low, medium, high, critical
    churn_probability DECIMAL(3,2) NOT NULL, -- 0-1
    days_until_churn INT,
    risk_factors TEXT[] NOT NULL,
    recommended_actions TEXT[] NOT NULL,
    confidence DECIMAL(3,2) NOT NULL, -- 0-1
    predicted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    intervention_taken BOOLEAN DEFAULT FALSE,
    intervention_type VARCHAR(50),
    outcome VARCHAR(20), -- retained, churned, unknown
    
    -- Constraints
    CONSTRAINT valid_probability CHECK (churn_probability >= 0 AND churn_probability <= 1),
    CONSTRAINT valid_confidence_churn CHECK (confidence >= 0 AND confidence <= 1),
    
    -- Indexes
    INDEX idx_churn_user ON churn_predictions(user_id),
    INDEX idx_churn_risk ON churn_predictions(risk_level),
    INDEX idx_churn_predicted ON churn_predictions(predicted_at DESC)
);

COMMENT ON TABLE churn_predictions IS 'AI predictions of user churn risk';
COMMENT ON COLUMN churn_predictions.intervention_taken IS 'Whether we took action based on prediction';
COMMENT ON COLUMN churn_predictions.outcome IS 'Actual outcome for model feedback';


-- Success Predictions
-- Stores predictions of job search success likelihood
CREATE TABLE IF NOT EXISTS success_predictions (
    prediction_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    success_probability DECIMAL(3,2) NOT NULL, -- 0-1
    estimated_days_to_hire INT,
    success_factors TEXT[] NOT NULL,
    blocking_issues TEXT[] NOT NULL,
    recommended_improvements TEXT[] NOT NULL,
    predicted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actual_hire_date DATE,
    prediction_accuracy DECIMAL(3,2), -- Calculated after hire
    
    -- Constraints
    CONSTRAINT valid_success_prob CHECK (success_probability >= 0 AND success_probability <= 1),
    
    -- Indexes
    INDEX idx_success_user ON success_predictions(user_id),
    INDEX idx_success_predicted ON success_predictions(predicted_at DESC)
);

COMMENT ON TABLE success_predictions IS 'AI predictions of job search success probability';
COMMENT ON COLUMN success_predictions.prediction_accuracy IS 'Actual vs predicted (for model improvement)';


-- Engagement Forecasts
-- Stores predictions of future user engagement
CREATE TABLE IF NOT EXISTS engagement_forecasts (
    forecast_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    predicted_weekly_events INT NOT NULL,
    predicted_features TEXT[] NOT NULL,
    engagement_trend VARCHAR(20) NOT NULL, -- increasing, stable, declining
    forecast_confidence DECIMAL(3,2) NOT NULL, -- 0-1
    forecast_period VARCHAR(20) NOT NULL, -- next_7_days, next_30_days
    forecasted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actual_events INT,
    forecast_accuracy DECIMAL(3,2),
    
    -- Constraints
    CONSTRAINT valid_forecast_confidence CHECK (forecast_confidence >= 0 AND forecast_confidence <= 1),
    
    -- Indexes
    INDEX idx_forecast_user ON engagement_forecasts(user_id),
    INDEX idx_forecast_date ON engagement_forecasts(forecasted_at DESC)
);

COMMENT ON TABLE engagement_forecasts IS 'AI forecasts of user engagement levels';
COMMENT ON COLUMN engagement_forecasts.actual_events IS 'Actual count after forecast period (for accuracy)';


-- Intervention Timing
-- Stores optimal timing for user nudges/guidance
CREATE TABLE IF NOT EXISTS intervention_timing (
    timing_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    best_day_of_week INT NOT NULL, -- 0=Monday, 6=Sunday
    best_hour INT NOT NULL, -- 0-23
    confidence DECIMAL(3,2) NOT NULL, -- 0-1
    based_on_events INT NOT NULL, -- Number of events analyzed
    calculated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_day CHECK (best_day_of_week >= 0 AND best_day_of_week <= 6),
    CONSTRAINT valid_hour CHECK (best_hour >= 0 AND best_hour <= 23),
    CONSTRAINT valid_timing_confidence CHECK (confidence >= 0 AND confidence <= 1),
    
    -- Indexes
    INDEX idx_timing_user ON intervention_timing(user_id),
    INDEX idx_timing_calculated ON intervention_timing(calculated_at DESC),
    
    -- Only keep most recent timing per user
    UNIQUE(user_id, calculated_at)
);

COMMENT ON TABLE intervention_timing IS 'Optimal times to send guidance/nudges per user';
COMMENT ON COLUMN intervention_timing.based_on_events IS 'Sample size used for calculation';


-- ============================================================================
-- Row Level Security (RLS) Policies
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE ai_memory ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_recommendations ENABLE ROW LEVEL SECURITY;
ALTER TABLE guidance_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE churn_predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE success_predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE engagement_forecasts ENABLE ROW LEVEL SECURITY;
ALTER TABLE intervention_timing ENABLE ROW LEVEL SECURITY;

-- Users can only see their own data
CREATE POLICY user_own_memory ON ai_memory
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY user_own_recommendations ON job_recommendations
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY user_own_guidance ON guidance_history
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY user_own_churn ON churn_predictions
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY user_own_success ON success_predictions
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY user_own_forecasts ON engagement_forecasts
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY user_own_timing ON intervention_timing
    FOR ALL USING (auth.uid() = user_id);


-- ============================================================================
-- Cleanup Job Functions
-- ============================================================================

-- Auto-delete expired recommendations
CREATE OR REPLACE FUNCTION cleanup_expired_recommendations()
RETURNS void AS $$
BEGIN
    DELETE FROM job_recommendations
    WHERE expires_at < NOW()
    AND shown_to_user = FALSE;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION cleanup_expired_recommendations IS 'Removes expired recommendations that were never shown';


-- Keep only last 3 predictions per user (for performance)
CREATE OR REPLACE FUNCTION cleanup_old_predictions()
RETURNS void AS $$
BEGIN
    -- Keep last 3 churn predictions
    DELETE FROM churn_predictions
    WHERE prediction_id NOT IN (
        SELECT prediction_id
        FROM churn_predictions
        WHERE user_id = churn_predictions.user_id
        ORDER BY predicted_at DESC
        LIMIT 3
    );
    
    -- Keep last 3 success predictions
    DELETE FROM success_predictions
    WHERE prediction_id NOT IN (
        SELECT prediction_id
        FROM success_predictions
        WHERE user_id = success_predictions.user_id
        ORDER BY predicted_at DESC
        LIMIT 3
    );
    
    -- Keep last 5 forecasts
    DELETE FROM engagement_forecasts
    WHERE forecast_id NOT IN (
        SELECT forecast_id
        FROM engagement_forecasts
        WHERE user_id = engagement_forecasts.user_id
        ORDER BY forecasted_at DESC
        LIMIT 5
    );
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION cleanup_old_predictions IS 'Keeps only recent predictions per user';


-- ============================================================================
-- Profile Assistant Tables
-- ============================================================================

-- Profile Analysis History
-- Stores profile completeness analysis over time
CREATE TABLE IF NOT EXISTS profile_analysis (
    analysis_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    completeness_score DECIMAL(3,2) NOT NULL, -- 0-1
    completeness_level VARCHAR(20) NOT NULL, -- minimal, basic, good, excellent, perfect
    missing_fields TEXT[] NOT NULL,
    incomplete_fields TEXT[] NOT NULL,
    strengths TEXT[] NOT NULL,
    weaknesses TEXT[] NOT NULL,
    analyzed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    INDEX idx_profile_analysis_user ON profile_analysis(user_id),
    INDEX idx_profile_analysis_time ON profile_analysis(analyzed_at DESC)
);

COMMENT ON TABLE profile_analysis IS 'Profile completeness analysis over time';


-- Profile Suggestions
-- AI-generated suggestions for profile improvement
CREATE TABLE IF NOT EXISTS profile_suggestions (
    suggestion_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    field VARCHAR(100) NOT NULL,
    suggestion_type VARCHAR(50) NOT NULL, -- missing, incomplete, inconsistent, optimization
    current_value TEXT,
    suggested_value TEXT NOT NULL,
    reasoning TEXT NOT NULL,
    priority INTEGER NOT NULL, -- 1=critical, 2=high, 3=medium, 4=low
    impact_score DECIMAL(3,2) NOT NULL, -- 0-1
    status VARCHAR(20) DEFAULT 'pending', -- pending, accepted, dismissed, applied
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    INDEX idx_suggestions_user ON profile_suggestions(user_id),
    INDEX idx_suggestions_priority ON profile_suggestions(priority, impact_score DESC),
    INDEX idx_suggestions_status ON profile_suggestions(status)
);

COMMENT ON TABLE profile_suggestions IS 'AI suggestions for profile improvement';


-- Inferred Profile Data
-- Data inferred by AI from available context
CREATE TABLE IF NOT EXISTS inferred_profile_data (
    inference_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    field VARCHAR(100) NOT NULL,
    inferred_value JSONB NOT NULL,
    confidence DECIMAL(3,2) NOT NULL, -- 0-1
    reasoning TEXT NOT NULL,
    source TEXT NOT NULL, -- experience, behavior, preferences, etc.
    applied_to_profile BOOLEAN DEFAULT FALSE,
    inferred_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    INDEX idx_inferred_user ON inferred_profile_data(user_id),
    INDEX idx_inferred_field ON inferred_profile_data(field),
    INDEX idx_inferred_confidence ON inferred_profile_data(confidence DESC)
);

COMMENT ON TABLE inferred_profile_data IS 'Profile data inferred by AI';


-- ============================================================================
-- Indexes for Performance
-- ============================================================================

-- Additional composite indexes for common queries
CREATE INDEX idx_recs_user_score ON job_recommendations(user_id, recommendation_score DESC)
    WHERE shown_to_user = FALSE;

CREATE INDEX idx_guidance_user_type ON guidance_history(user_id, guidance_type, shown_at DESC);

CREATE INDEX idx_churn_risk_recent ON churn_predictions(risk_level, predicted_at DESC)
    WHERE intervention_taken = FALSE;

CREATE INDEX idx_profile_suggestions_actionable ON profile_suggestions(user_id, priority, status)
    WHERE status = 'pending';


-- ============================================================================
-- Summary
-- ============================================================================
-- Tables Created: 10
-- - ai_memory: Semantic embeddings learned from events
-- - job_recommendations: Cached AI recommendations
-- - guidance_history: Proactive guidance tracking
-- - churn_predictions: Churn risk predictions
-- - success_predictions: Job search success predictions
-- - engagement_forecasts: Engagement level predictions
-- - intervention_timing: Optimal nudge timing
-- - profile_analysis: Profile completeness tracking
-- - profile_suggestions: AI profile improvement suggestions
-- - inferred_profile_data: AI-inferred profile information
--
-- Capabilities Enabled:
-- ✅ Semantic memory formation from events
-- ✅ AI-powered job recommendations
-- ✅ Proactive user guidance
-- ✅ Churn prediction & prevention
-- ✅ Success probability forecasting
-- ✅ Engagement trend analysis
-- ✅ Optimal intervention timing
-- ✅ Intelligent profile completion
-- ✅ Profile optimization suggestions
-- ✅ Automated data inference
-- ============================================================================
