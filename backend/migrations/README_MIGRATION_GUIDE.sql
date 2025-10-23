-- ============================================
-- SUPABASE MIGRATION SCRIPT - RUN IN ORDER
-- ============================================
-- Instructions:
-- 1. Go to https://supabase.com/dashboard
-- 2. Select your project: whxbxjpymksgvixudnjh
-- 3. Click "SQL Editor" in left sidebar
-- 4. Copy each section below and run them ONE AT A TIME
-- 5. Check for errors before proceeding to next section
-- ============================================

-- IMPORTANT: Check if tables already exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('users', 'coach_messages', 'user_progress', 'companies', 'jobs');

-- If tables exist, you may need to drop them first or skip migrations
-- To drop all tables (DESTRUCTIVE - only for fresh start):
-- DROP SCHEMA public CASCADE;
-- CREATE SCHEMA public;
-- GRANT ALL ON SCHEMA public TO postgres;
-- GRANT ALL ON SCHEMA public TO public;

