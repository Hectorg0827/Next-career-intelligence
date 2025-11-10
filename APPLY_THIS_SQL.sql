-- ========================================
-- MINIMAL JOBS MARKETPLACE SCHEMA
-- Run this in Supabase SQL Editor
-- ========================================

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Jobs table (minimal version)
CREATE TABLE IF NOT EXISTS public.jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Basic info
    title VARCHAR(500) NOT NULL,
    seniority VARCHAR(50),

    -- Description
    description TEXT NOT NULL,
    requirements TEXT,
    responsibilities TEXT,
    benefits TEXT,

    -- Skills (extracted)
    skills_extracted JSONB DEFAULT '[]'::jsonb,

    -- Location
    location_type VARCHAR(50),
    location_city VARCHAR(255),
    location_state VARCHAR(100),
    location_country VARCHAR(100),

    -- Compensation
    salary_min INTEGER,
    salary_max INTEGER,
    salary_currency VARCHAR(10) DEFAULT 'USD',

    -- Work details
    employment_type VARCHAR(50),
    experience_years_min INTEGER,
    experience_years_max INTEGER,

    -- Application
    apply_url TEXT NOT NULL,

    -- Source
    source VARCHAR(100) NOT NULL,

    -- Status
    status VARCHAR(50) DEFAULT 'active',
    is_spam BOOLEAN DEFAULT false,

    -- Timestamps
    posted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for search performance
CREATE INDEX IF NOT EXISTS idx_jobs_title ON public.jobs(title);
CREATE INDEX IF NOT EXISTS idx_jobs_location_type ON public.jobs(location_type);
CREATE INDEX IF NOT EXISTS idx_jobs_seniority ON public.jobs(seniority);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON public.jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_posted_at ON public.jobs(posted_at DESC);
CREATE INDEX IF NOT EXISTS idx_jobs_salary_min ON public.jobs(salary_min);

-- Enable search on skills
CREATE INDEX IF NOT EXISTS idx_jobs_skills_gin ON public.jobs USING gin(skills_extracted);

-- Enable Row Level Security
ALTER TABLE public.jobs ENABLE ROW LEVEL SECURITY;

-- Policy: Everyone can read active jobs
CREATE POLICY "Anyone can view active jobs" ON public.jobs
    FOR SELECT USING (status = 'active' AND is_spam = false);

-- Grant permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT SELECT ON public.jobs TO anon, authenticated;
GRANT INSERT ON public.jobs TO service_role;
GRANT UPDATE ON public.jobs TO service_role;

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Jobs marketplace schema created successfully!';
    RAISE NOTICE '📝 You can now seed jobs using: POST /api/jobs/seed?count=50';
END $$;
