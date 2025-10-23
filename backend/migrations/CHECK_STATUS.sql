-- ============================================
-- QUICK MIGRATION STATUS CHECK
-- ============================================
-- Run this in Supabase SQL Editor to check which tables exist
-- ============================================

-- 1. List all tables in public schema
SELECT 
    table_name,
    CASE 
        WHEN table_name = 'users' THEN '001 - Core users table'
        WHEN table_name = 'verification_codes' THEN '002 - Email verification'
        WHEN table_name = 'password_resets' THEN '003 - Password reset'
        WHEN table_name = 'onboarding_data' THEN '004 - User onboarding'
        WHEN table_name = 'user_progress' THEN '006 - Pro features (progress tracking)'
        WHEN table_name = 'coach_messages' THEN '006 - Pro features (AI Coach)'
        WHEN table_name = 'cohorts' THEN '006 - Pro features (community)'
        WHEN table_name = 'cohort_members' THEN '006 - Pro features (community)'
        WHEN table_name = 'interview_sessions' THEN '006 - Pro features (AI Interviewer)'
        WHEN table_name = 'interview_turns' THEN '006 - Pro features (AI Interviewer)'
        WHEN table_name = 'portfolio_projects' THEN '006 - Pro features (portfolio)'
        WHEN table_name = 'companies' THEN '007 - Marketplace (companies)'
        WHEN table_name = 'jobs' THEN '007 - Marketplace (jobs)'
        WHEN table_name = 'user_job_applications' THEN '007 - Marketplace (applications)'
        WHEN table_name = 'hiring_feedback' THEN '007 - Marketplace (feedback)'
        ELSE 'Unknown table'
    END as migration_source
FROM information_schema.tables 
WHERE table_schema = 'public'
ORDER BY table_name;

-- 2. Check if subscription fields exist in users table
SELECT 
    column_name,
    data_type,
    column_default
FROM information_schema.columns 
WHERE table_name = 'users' 
AND column_name IN (
    'subscription_status',
    'stripe_customer_id',
    'free_reports_used',
    'last_free_analysis_at'
)
ORDER BY column_name;

-- 3. Count rows in each critical table
SELECT 'users' as table_name, COUNT(*) as row_count FROM users
UNION ALL
SELECT 'coach_messages', COUNT(*) FROM coach_messages
UNION ALL
SELECT 'user_progress', COUNT(*) FROM user_progress
UNION ALL
SELECT 'companies', COUNT(*) FROM companies
UNION ALL
SELECT 'jobs', COUNT(*) FROM jobs
ORDER BY table_name;

-- 4. Check RLS policies (Row Level Security)
SELECT 
    tablename,
    policyname,
    permissive,
    cmd as operation
FROM pg_policies 
WHERE schemaname = 'public'
ORDER BY tablename, policyname;

-- 5. Check indexes created
SELECT 
    schemaname,
    tablename,
    indexname
FROM pg_indexes 
WHERE schemaname = 'public'
ORDER BY tablename, indexname;

-- ============================================
-- EXPECTED RESULTS
-- ============================================
-- If all migrations ran successfully, you should see:
--
-- Tables (15):
-- ✅ users
-- ✅ verification_codes
-- ✅ password_resets
-- ✅ onboarding_data
-- ✅ user_progress
-- ✅ coach_messages (CRITICAL for AI Coach)
-- ✅ cohorts, cohort_members
-- ✅ interview_sessions, interview_turns
-- ✅ portfolio_projects
-- ✅ companies, jobs
-- ✅ user_job_applications
-- ✅ hiring_feedback
--
-- Subscription fields in users:
-- ✅ subscription_status
-- ✅ stripe_customer_id
-- ✅ free_reports_used
-- ✅ last_free_analysis_at
--
-- If missing tables, run the corresponding migration file.
-- ============================================
