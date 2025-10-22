-- ============================================
-- SUPABASE RLS POLICIES SETUP
-- Run these SQL commands in Supabase SQL Editor
-- ============================================

-- 1. USERS TABLE
-- Allow service role full access
CREATE POLICY "Service role can manage users"
ON users
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

-- Allow users to view their own data
CREATE POLICY "Users can view own data"
ON users
FOR SELECT
TO authenticated
USING (auth.uid()::text = firebase_uid);

-- Allow users to update their own data
CREATE POLICY "Users can update own data"
ON users
FOR UPDATE
TO authenticated
USING (auth.uid()::text = firebase_uid)
WITH CHECK (auth.uid()::text = firebase_uid);


-- 2. CAREER_PROFILES TABLE
CREATE POLICY "Service role can manage career profiles"
ON career_profiles
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

CREATE POLICY "Users can manage own profiles"
ON career_profiles
FOR ALL
TO authenticated
USING (
  EXISTS (
    SELECT 1 FROM users
    WHERE users.id = career_profiles.user_id
    AND users.firebase_uid = auth.uid()::text
  )
)
WITH CHECK (
  EXISTS (
    SELECT 1 FROM users
    WHERE users.id = career_profiles.user_id
    AND users.firebase_uid = auth.uid()::text
  )
);


-- 3. ANALYSES TABLE
CREATE POLICY "Service role can manage analyses"
ON analyses
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

CREATE POLICY "Users can view own analyses"
ON analyses
FOR SELECT
TO authenticated
USING (
  EXISTS (
    SELECT 1 FROM users
    WHERE users.id = analyses.user_id
    AND users.firebase_uid = auth.uid()::text
  )
);


-- 4. CAREER_ROADMAPS TABLE
CREATE POLICY "Service role can manage roadmaps"
ON career_roadmaps
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

CREATE POLICY "Users can view own roadmaps"
ON career_roadmaps
FOR SELECT
TO authenticated
USING (
  EXISTS (
    SELECT 1 FROM users
    WHERE users.id = career_roadmaps.user_id
    AND users.firebase_uid = auth.uid()::text
  )
);


-- 5. INTERVIEW_SESSIONS TABLE
CREATE POLICY "Service role can manage interview sessions"
ON interview_sessions
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

CREATE POLICY "Users can manage own interview sessions"
ON interview_sessions
FOR ALL
TO authenticated
USING (
  EXISTS (
    SELECT 1 FROM users
    WHERE users.id = interview_sessions.user_id
    AND users.firebase_uid = auth.uid()::text
  )
)
WITH CHECK (
  EXISTS (
    SELECT 1 FROM users
    WHERE users.id = interview_sessions.user_id
    AND users.firebase_uid = auth.uid()::text
  )
);


-- 6. INTERVIEW_ANSWERS TABLE
CREATE POLICY "Service role can manage interview answers"
ON interview_answers
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

CREATE POLICY "Users can manage own interview answers"
ON interview_answers
FOR ALL
TO authenticated
USING (
  EXISTS (
    SELECT 1 FROM interview_sessions
    JOIN users ON users.id = interview_sessions.user_id
    WHERE interview_sessions.id = interview_answers.session_id
    AND users.firebase_uid = auth.uid()::text
  )
)
WITH CHECK (
  EXISTS (
    SELECT 1 FROM interview_sessions
    JOIN users ON users.id = interview_sessions.user_id
    WHERE interview_sessions.id = interview_answers.session_id
    AND users.firebase_uid = auth.uid()::text
  )
);


-- 7. COACH_CONVERSATIONS TABLE
CREATE POLICY "Service role can manage coach conversations"
ON coach_conversations
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

CREATE POLICY "Users can manage own coach conversations"
ON coach_conversations
FOR ALL
TO authenticated
USING (
  EXISTS (
    SELECT 1 FROM users
    WHERE users.id = coach_conversations.user_id
    AND users.firebase_uid = auth.uid()::text
  )
)
WITH CHECK (
  EXISTS (
    SELECT 1 FROM users
    WHERE users.id = coach_conversations.user_id
    AND users.firebase_uid = auth.uid()::text
  )
);


-- 8. CAREER_GOALS TABLE
CREATE POLICY "Service role can manage career goals"
ON career_goals
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

CREATE POLICY "Users can manage own career goals"
ON career_goals
FOR ALL
TO authenticated
USING (
  EXISTS (
    SELECT 1 FROM users
    WHERE users.id = career_goals.user_id
    AND users.firebase_uid = auth.uid()::text
  )
)
WITH CHECK (
  EXISTS (
    SELECT 1 FROM users
    WHERE users.id = career_goals.user_id
    AND users.firebase_uid = auth.uid()::text
  )
);


-- 9. JOB_APPLICATIONS TABLE
CREATE POLICY "Service role can manage job applications"
ON job_applications
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

CREATE POLICY "Users can manage own job applications"
ON job_applications
FOR ALL
TO authenticated
USING (
  EXISTS (
    SELECT 1 FROM users
    WHERE users.id = job_applications.user_id
    AND users.firebase_uid = auth.uid()::text
  )
)
WITH CHECK (
  EXISTS (
    SELECT 1 FROM users
    WHERE users.id = job_applications.user_id
    AND users.firebase_uid = auth.uid()::text
  )
);


-- 10. SUBSCRIPTIONS TABLE
CREATE POLICY "Service role can manage subscriptions"
ON subscriptions
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

CREATE POLICY "Users can view own subscriptions"
ON subscriptions
FOR SELECT
TO authenticated
USING (
  EXISTS (
    SELECT 1 FROM users
    WHERE users.id = subscriptions.user_id
    AND users.firebase_uid = auth.uid()::text
  )
);


-- ============================================
-- ENABLE RLS ON ALL TABLES
-- ============================================
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE career_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE career_roadmaps ENABLE ROW LEVEL SECURITY;
ALTER TABLE interview_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE interview_answers ENABLE ROW LEVEL SECURITY;
ALTER TABLE coach_conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE career_goals ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_applications ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;


-- ============================================
-- VERIFICATION QUERY
-- ============================================
-- Run this to verify policies are active:
SELECT 
  schemaname,
  tablename,
  policyname,
  roles,
  cmd,
  qual
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename, policyname;
