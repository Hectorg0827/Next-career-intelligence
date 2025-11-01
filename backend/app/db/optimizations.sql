-- Phase 4 Database Optimizations
-- Performance indexes and query optimizations for better reliability

-- ============================================================================
-- USERS TABLE OPTIMIZATIONS
-- ============================================================================

-- Index for email lookups (authentication)
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Index for user status queries
CREATE INDEX IF NOT EXISTS idx_users_status ON users(subscription_tier, is_active);

-- Composite index for user profile queries
CREATE INDEX IF NOT EXISTS idx_users_profile ON users(id, email, subscription_tier);

-- ============================================================================
-- JOBS TABLE OPTIMIZATIONS
-- ============================================================================

-- Index for job status filtering
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status) WHERE status = 'active';

-- Index for job location searches
CREATE INDEX IF NOT EXISTS idx_jobs_location ON jobs(location);

-- Index for job posting date (for sorting)
CREATE INDEX IF NOT EXISTS idx_jobs_posted_at ON jobs(posted_at DESC);

-- Composite index for job searches
CREATE INDEX IF NOT EXISTS idx_jobs_search ON jobs(status, location, posted_at DESC);

-- Index for salary range queries
CREATE INDEX IF NOT EXISTS idx_jobs_salary ON jobs(salary_min, salary_max) WHERE salary_min IS NOT NULL;

-- Full-text search index for job titles and descriptions
CREATE INDEX IF NOT EXISTS idx_jobs_title_search ON jobs USING gin(to_tsvector('english', title));
CREATE INDEX IF NOT EXISTS idx_jobs_description_search ON jobs USING gin(to_tsvector('english', description));

-- ============================================================================
-- APPLICATIONS TABLE OPTIMIZATIONS
-- ============================================================================

-- Index for user's applications
CREATE INDEX IF NOT EXISTS idx_applications_user ON applications(user_id, created_at DESC);

-- Index for job applications
CREATE INDEX IF NOT EXISTS idx_applications_job ON applications(job_id);

-- Index for application status
CREATE INDEX IF NOT EXISTS idx_applications_status ON applications(status, updated_at DESC);

-- Composite index for application tracking
CREATE INDEX IF NOT EXISTS idx_applications_tracking ON applications(user_id, job_id, status);

-- ============================================================================
-- SKILLS TABLE OPTIMIZATIONS
-- ============================================================================

-- Index for skill name lookups
CREATE INDEX IF NOT EXISTS idx_skills_name ON skills(name);

-- Index for skill category
CREATE INDEX IF NOT EXISTS idx_skills_category ON skills(category);

-- ============================================================================
-- USER_SKILLS TABLE OPTIMIZATIONS
-- ============================================================================

-- Index for user skill lookups
CREATE INDEX IF NOT EXISTS idx_user_skills_user ON user_skills(user_id);

-- Index for skill users lookups
CREATE INDEX IF NOT EXISTS idx_user_skills_skill ON user_skills(skill_id);

-- Composite index for skill proficiency queries
CREATE INDEX IF NOT EXISTS idx_user_skills_proficiency ON user_skills(user_id, skill_id, proficiency_level);

-- ============================================================================
-- JOB_SKILLS TABLE OPTIMIZATIONS
-- ============================================================================

-- Index for job skill requirements
CREATE INDEX IF NOT EXISTS idx_job_skills_job ON job_skills(job_id);

-- Index for skill job openings
CREATE INDEX IF NOT EXISTS idx_job_skills_skill ON job_skills(skill_id);

-- Composite index for skill matching
CREATE INDEX IF NOT EXISTS idx_job_skills_matching ON job_skills(job_id, skill_id, required_level);

-- ============================================================================
-- CAREER_RECOMMENDATIONS TABLE OPTIMIZATIONS
-- ============================================================================

-- Index for user recommendations
CREATE INDEX IF NOT EXISTS idx_career_recs_user ON career_recommendations(user_id, created_at DESC);

-- Index for recommendation status
CREATE INDEX IF NOT EXISTS idx_career_recs_status ON career_recommendations(status);

-- ============================================================================
-- SKILL_ASSESSMENTS TABLE OPTIMIZATIONS
-- ============================================================================

-- Index for user assessments
CREATE INDEX IF NOT EXISTS idx_skill_assessments_user ON skill_assessments(user_id, completed_at DESC);

-- Index for skill assessments
CREATE INDEX IF NOT EXISTS idx_skill_assessments_skill ON skill_assessments(skill_id);

-- Composite index for assessment tracking
CREATE INDEX IF NOT EXISTS idx_skill_assessments_tracking ON skill_assessments(user_id, skill_id, status);

-- ============================================================================
-- NOTIFICATIONS TABLE OPTIMIZATIONS
-- ============================================================================

-- Index for user notifications
CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id, created_at DESC);

-- Index for unread notifications
CREATE INDEX IF NOT EXISTS idx_notifications_unread ON notifications(user_id, is_read, created_at DESC) WHERE is_read = false;

-- ============================================================================
-- MESSAGES TABLE OPTIMIZATIONS
-- ============================================================================

-- Index for user messages (sender)
CREATE INDEX IF NOT EXISTS idx_messages_sender ON messages(sender_id, created_at DESC);

-- Index for user messages (receiver)
CREATE INDEX IF NOT EXISTS idx_messages_receiver ON messages(receiver_id, created_at DESC);

-- Index for conversation threads
CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(sender_id, receiver_id, created_at);

-- ============================================================================
-- ANALYTICS TABLES OPTIMIZATIONS
-- ============================================================================

-- Index for user activity tracking
CREATE INDEX IF NOT EXISTS idx_user_activity_user ON user_activity(user_id, timestamp DESC);

-- Index for activity type analytics
CREATE INDEX IF NOT EXISTS idx_user_activity_type ON user_activity(activity_type, timestamp DESC);

-- Index for job view analytics
CREATE INDEX IF NOT EXISTS idx_job_views_job ON job_views(job_id, viewed_at DESC);

-- Index for user job views
CREATE INDEX IF NOT EXISTS idx_job_views_user ON job_views(user_id, viewed_at DESC);

-- ============================================================================
-- MATERIALIZED VIEWS FOR COMPLEX QUERIES
-- ============================================================================

-- Materialized view for job match scores (expensive calculation)
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_job_match_scores AS
SELECT 
    u.id as user_id,
    j.id as job_id,
    j.title,
    j.location,
    j.salary_min,
    j.salary_max,
    COUNT(DISTINCT us.skill_id) as matching_skills,
    AVG(us.proficiency_level) as avg_proficiency,
    j.posted_at
FROM users u
CROSS JOIN jobs j
LEFT JOIN user_skills us ON us.user_id = u.id
LEFT JOIN job_skills js ON js.job_id = j.id AND js.skill_id = us.skill_id
WHERE j.status = 'active'
GROUP BY u.id, j.id, j.title, j.location, j.salary_min, j.salary_max, j.posted_at;

-- Index on materialized view
CREATE INDEX IF NOT EXISTS idx_mv_job_matches_user ON mv_job_match_scores(user_id, matching_skills DESC);
CREATE INDEX IF NOT EXISTS idx_mv_job_matches_job ON mv_job_match_scores(job_id);

-- Refresh function for materialized view
CREATE OR REPLACE FUNCTION refresh_job_match_scores()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_job_match_scores;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- QUERY PERFORMANCE FUNCTIONS
-- ============================================================================

-- Function to get user's recommended jobs (optimized)
CREATE OR REPLACE FUNCTION get_user_recommended_jobs(
    p_user_id UUID,
    p_limit INTEGER DEFAULT 10,
    p_offset INTEGER DEFAULT 0
)
RETURNS TABLE (
    job_id UUID,
    title VARCHAR,
    location VARCHAR,
    salary_min DECIMAL,
    salary_max DECIMAL,
    match_score INTEGER,
    posted_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        j.id,
        j.title,
        j.location,
        j.salary_min,
        j.salary_max,
        COALESCE(m.matching_skills, 0)::INTEGER as match_score,
        j.posted_at
    FROM jobs j
    LEFT JOIN mv_job_match_scores m ON m.job_id = j.id AND m.user_id = p_user_id
    WHERE j.status = 'active'
    ORDER BY match_score DESC, j.posted_at DESC
    LIMIT p_limit
    OFFSET p_offset;
END;
$$ LANGUAGE plpgsql;

-- Function to get user's skill gaps for a job
CREATE OR REPLACE FUNCTION get_skill_gaps(
    p_user_id UUID,
    p_job_id UUID
)
RETURNS TABLE (
    skill_name VARCHAR,
    required_level INTEGER,
    user_level INTEGER,
    gap INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        s.name,
        js.required_level,
        COALESCE(us.proficiency_level, 0) as user_level,
        js.required_level - COALESCE(us.proficiency_level, 0) as gap
    FROM job_skills js
    JOIN skills s ON s.id = js.skill_id
    LEFT JOIN user_skills us ON us.skill_id = js.skill_id AND us.user_id = p_user_id
    WHERE js.job_id = p_job_id
    AND (us.proficiency_level IS NULL OR us.proficiency_level < js.required_level)
    ORDER BY gap DESC;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- AUTOMATED MAINTENANCE
-- ============================================================================

-- Function to clean up old notifications
CREATE OR REPLACE FUNCTION cleanup_old_notifications()
RETURNS void AS $$
BEGIN
    DELETE FROM notifications
    WHERE created_at < NOW() - INTERVAL '90 days'
    AND is_read = true;
END;
$$ LANGUAGE plpgsql;

-- Function to clean up expired job postings
CREATE OR REPLACE FUNCTION cleanup_expired_jobs()
RETURNS void AS $$
BEGIN
    UPDATE jobs
    SET status = 'expired'
    WHERE status = 'active'
    AND posted_at < NOW() - INTERVAL '60 days';
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- PERFORMANCE MONITORING VIEWS
-- ============================================================================

-- View to monitor slow queries
CREATE OR REPLACE VIEW slow_queries AS
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    max_time
FROM pg_stat_statements
WHERE mean_time > 100  -- queries taking more than 100ms
ORDER BY total_time DESC
LIMIT 50;

-- View to monitor table sizes
CREATE OR REPLACE VIEW table_sizes AS
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
    pg_total_relation_size(schemaname||'.'||tablename) AS size_bytes
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY size_bytes DESC;

-- View to monitor index usage
CREATE OR REPLACE VIEW index_usage AS
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
ORDER BY idx_scan ASC;

-- ============================================================================
-- VACUUM AND ANALYZE RECOMMENDATIONS
-- ============================================================================

-- Run these commands periodically for maintenance:
-- VACUUM ANALYZE users;
-- VACUUM ANALYZE jobs;
-- VACUUM ANALYZE applications;
-- VACUUM ANALYZE user_skills;
-- VACUUM ANALYZE job_skills;
-- 
-- Or run for all tables:
-- VACUUM ANALYZE;

-- ============================================================================
-- NOTES
-- ============================================================================

-- To apply these optimizations, run:
-- psql -d your_database -f optimizations.sql

-- To refresh materialized views periodically, set up a cron job:
-- SELECT refresh_job_match_scores();

-- To monitor query performance:
-- SELECT * FROM slow_queries;

-- To check table sizes:
-- SELECT * FROM table_sizes;

-- To check index usage:
-- SELECT * FROM index_usage WHERE idx_scan < 100;
