-- Phase 4 Database Optimizations (Schema-matched)
-- Performance indexes based on actual database schema

-- ============================================================================
-- USERS TABLE OPTIMIZATIONS
-- ============================================================================

-- Index for email lookups (authentication)
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Index for user status queries
CREATE INDEX IF NOT EXISTS idx_users_status ON users(subscription_status, is_active);

-- Index for subscription management
CREATE INDEX IF NOT EXISTS idx_users_subscription ON users(stripe_customer_id) WHERE stripe_customer_id IS NOT NULL;

-- Index for Firebase integration
CREATE INDEX IF NOT EXISTS idx_users_firebase ON users(firebase_uid) WHERE firebase_uid IS NOT NULL;

-- Index for role-based queries
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role) WHERE role IS NOT NULL;

-- ============================================================================
-- JOBS TABLE OPTIMIZATIONS
-- ============================================================================

-- Index for active job filtering
CREATE INDEX IF NOT EXISTS idx_jobs_active ON jobs(is_active, posted_date DESC) WHERE is_active = true;

-- Index for job location searches
CREATE INDEX IF NOT EXISTS idx_jobs_location ON jobs(location) WHERE location IS NOT NULL;

-- Index for job posting date (for sorting)
CREATE INDEX IF NOT EXISTS idx_jobs_posted_date ON jobs(posted_date DESC);

-- Index for remote policy filtering
CREATE INDEX IF NOT EXISTS idx_jobs_remote ON jobs(remote_policy) WHERE remote_policy IS NOT NULL;

-- Index for salary range queries
CREATE INDEX IF NOT EXISTS idx_jobs_salary ON jobs(salary_min, salary_max) WHERE salary_min IS NOT NULL;

-- Index for company jobs
CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company_id, is_active);

-- Full-text search index for job titles
CREATE INDEX IF NOT EXISTS idx_jobs_title_search ON jobs USING gin(to_tsvector('english', title));

-- Full-text search index for job descriptions
CREATE INDEX IF NOT EXISTS idx_jobs_description_search ON jobs USING gin(to_tsvector('english', description));

-- ============================================================================
-- APPLICATIONS TABLE OPTIMIZATIONS
-- ============================================================================

-- Index for user's applications
CREATE INDEX IF NOT EXISTS idx_applications_user ON user_job_applications(user_id, applied_at DESC);

-- Index for job applications
CREATE INDEX IF NOT EXISTS idx_applications_job ON user_job_applications(job_id);

-- Index for application status tracking
CREATE INDEX IF NOT EXISTS idx_applications_status ON user_job_applications(status);

-- Composite index for user application tracking
CREATE INDEX IF NOT EXISTS idx_applications_user_job ON user_job_applications(user_id, job_id, status);

-- ============================================================================
-- COMPANIES TABLE OPTIMIZATIONS
-- ============================================================================

-- Index for company lookups
CREATE INDEX IF NOT EXISTS idx_companies_name ON companies(name);

-- ============================================================================
-- CAREER PROFILES TABLE OPTIMIZATIONS
-- ============================================================================

-- Index for user profile lookup
CREATE INDEX IF NOT EXISTS idx_career_profiles_user ON career_profiles(user_id);

-- ============================================================================
-- ANALYSES TABLE OPTIMIZATIONS
-- ============================================================================

-- Index for user analyses
CREATE INDEX IF NOT EXISTS idx_analyses_user ON analyses(user_id, created_at DESC);

-- ============================================================================
-- ONBOARDING TABLE OPTIMIZATIONS
-- ============================================================================

-- Index for user onboarding status
CREATE INDEX IF NOT EXISTS idx_onboarding_user ON onboarding(user_id);

-- Index for completion tracking
CREATE INDEX IF NOT EXISTS idx_onboarding_complete ON onboarding(is_complete) WHERE is_complete = true;

-- ============================================================================
-- MATERIALIZED VIEWS FOR COMPLEX QUERIES
-- ============================================================================

-- Drop existing views if they exist
DROP MATERIALIZED VIEW IF EXISTS mv_job_stats CASCADE;
DROP MATERIALIZED VIEW IF EXISTS mv_user_activity CASCADE;

-- Materialized view for job statistics
CREATE MATERIALIZED VIEW mv_job_stats AS
SELECT
    COUNT(*) as total_jobs,
    COUNT(*) FILTER (WHERE is_active = true) as active_jobs,
    COUNT(DISTINCT company_id) as total_companies,
    COUNT(DISTINCT location) as total_locations,
    AVG(salary_min) FILTER (WHERE salary_min IS NOT NULL) as avg_min_salary,
    AVG(salary_max) FILTER (WHERE salary_max IS NOT NULL) as avg_max_salary,
    DATE_TRUNC('day', NOW()) as last_updated
FROM jobs;

-- Create index on materialized view
CREATE UNIQUE INDEX idx_mv_job_stats_updated ON mv_job_stats(last_updated);

-- Materialized view for user activity
CREATE MATERIALIZED VIEW mv_user_activity AS
SELECT
    COUNT(*) as total_users,
    COUNT(*) FILTER (WHERE is_active = true) as active_users,
    COUNT(*) FILTER (WHERE is_email_verified = true) as verified_users,
    COUNT(*) FILTER (WHERE subscription_status = 'active') as subscribed_users,
    COUNT(*) FILTER (WHERE role = 'recruiter') as recruiters,
    DATE_TRUNC('day', NOW()) as last_updated
FROM users;

-- Create index on materialized view
CREATE UNIQUE INDEX idx_mv_user_activity_updated ON mv_user_activity(last_updated);

-- ============================================================================
-- DATABASE MAINTENANCE FUNCTIONS
-- ============================================================================

-- Function to refresh materialized views
CREATE OR REPLACE FUNCTION refresh_materialized_views()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_job_stats;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_user_activity;
END;
$$ LANGUAGE plpgsql;

-- Function to analyze tables (update statistics)
CREATE OR REPLACE FUNCTION analyze_all_tables()
RETURNS void AS $$
BEGIN
    ANALYZE users;
    ANALYZE jobs;
    ANALYZE user_job_applications;
    ANALYZE companies;
    ANALYZE career_profiles;
    ANALYZE analyses;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- SUMMARY
-- ============================================================================

-- Print summary
DO $$
BEGIN
    RAISE NOTICE '✅ Database optimizations applied successfully!';
    RAISE NOTICE '📊 Indexes created for: users, jobs, applications, companies, profiles, analyses';
    RAISE NOTICE '📈 Materialized views created: job_stats, user_activity';
    RAISE NOTICE '🔧 Maintenance functions created: refresh_materialized_views, analyze_all_tables';
END $$;
