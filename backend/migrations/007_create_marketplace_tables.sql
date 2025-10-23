-- Migration: Create marketplace tables (Jobs, Companies, Hiring Feedback)
-- Purpose: Enable two-sided marketplace with job matching and recruiter portal

-- ============================================
-- B2C JOB HUB TABLES
-- ============================================

-- Companies (from scraping or API)
DROP TABLE IF EXISTS public.companies CASCADE;
CREATE TABLE public.companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    website_url TEXT,
    careers_page_url TEXT,
    logo_url TEXT,
    industry VARCHAR(100),
    size_range VARCHAR(50), -- e.g., "1-10", "11-50", "500-1000", "10000+"
    description TEXT,
    
    -- B2B Recruiter Access
    is_recruiter_partner BOOLEAN DEFAULT FALSE,
    recruiter_admin_id UUID REFERENCES public.users(id), -- Company admin for B2B portal
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Jobs (scraped or from API)
DROP TABLE IF EXISTS public.jobs CASCADE;
CREATE TABLE public.jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES public.companies(id) ON DELETE CASCADE,
    
    -- Job Details
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    location VARCHAR(255),
    remote_policy VARCHAR(50), -- 'remote', 'hybrid', 'onsite'
    employment_type VARCHAR(50), -- 'full_time', 'part_time', 'contract', 'internship'
    
    -- Compensation
    salary_min INTEGER,
    salary_max INTEGER,
    salary_currency VARCHAR(10) DEFAULT 'USD',
    
    -- Requirements (AI-extracted)
    required_skills JSONB DEFAULT '[]', -- ["Python", "SQL", "Machine Learning"]
    required_years_experience INTEGER,
    education_level VARCHAR(50),
    
    -- Source
    source VARCHAR(50), -- 'scraper', 'ziprecruiter', 'manual'
    external_url TEXT, -- Original job posting URL
    external_id VARCHAR(255), -- ID from external API
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    posted_date TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(external_id, source) -- Prevent duplicate jobs from same source
);

-- User Job Applications (track what users apply to)
DROP TABLE IF EXISTS public.user_job_applications CASCADE;
CREATE TABLE public.user_job_applications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    job_id UUID REFERENCES public.jobs(id) ON DELETE CASCADE NOT NULL,
    
    -- Application Status
    status VARCHAR(50) DEFAULT 'interested' CHECK (status IN (
        'interested', 
        'applied', 
        'interviewing', 
        'offered', 
        'accepted', 
        'rejected', 
        'withdrawn'
    )),
    
    -- Readiness Score (calculated)
    readiness_score DECIMAL(5,2), -- e.g., 75.50 (percent)
    skills_matched INTEGER,
    skills_total INTEGER,
    
    -- Tracking
    applied_at TIMESTAMP WITH TIME ZONE,
    updated_status_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Notes
    notes TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id, job_id) -- One application per user per job
);

-- ============================================
-- HIRING FEEDBACK (THE FLYWHEEL)
-- ============================================

-- User reports they got hired - captures what ACTUALLY mattered
DROP TABLE IF EXISTS public.hiring_feedback CASCADE;
CREATE TABLE public.hiring_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    job_id UUID REFERENCES public.jobs(id) ON DELETE SET NULL,
    
    -- Job Context (in case job is deleted)
    job_title VARCHAR(255) NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    
    -- THE GOLD: What skills were most important?
    important_skills TEXT[] NOT NULL, -- User's top 3-5 skills that got them the job
    interview_topics TEXT[], -- What was asked in interviews
    
    -- User Journey Data
    preparation_time_weeks INTEGER,
    courses_completed TEXT[],
    certifications_earned TEXT[],
    
    -- Compensation (for benchmarking)
    offered_salary INTEGER,
    salary_currency VARCHAR(10) DEFAULT 'USD',
    
    -- Additional Context
    feedback_text TEXT, -- Free-form feedback
    would_recommend BOOLEAN,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- B2B RECRUITER PORTAL TABLES
-- ============================================

-- Recruiter Search History (for analytics)
DROP TABLE IF EXISTS public.recruiter_searches CASCADE;
CREATE TABLE public.recruiter_searches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recruiter_user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    company_id UUID REFERENCES public.companies(id) ON DELETE CASCADE,
    
    -- Search Criteria
    search_query TEXT,
    filters JSONB DEFAULT '{}', -- {skills: ["Python"], location: "NYC", years_exp: 3}
    
    -- Results
    results_count INTEGER,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Recruiter Views Candidate Profile
DROP TABLE IF EXISTS public.recruiter_candidate_views CASCADE;
CREATE TABLE public.recruiter_candidate_views (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recruiter_user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    candidate_user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    company_id UUID REFERENCES public.companies(id) ON DELETE CASCADE,
    
    -- Engagement
    viewed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_shortlisted BOOLEAN DEFAULT FALSE,
    notes TEXT,
    
    UNIQUE(recruiter_user_id, candidate_user_id, viewed_at)
);

-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================

CREATE INDEX idx_companies_name ON public.companies(name);
CREATE INDEX idx_companies_recruiter_partner ON public.companies(is_recruiter_partner);

CREATE INDEX idx_jobs_company_id ON public.jobs(company_id);
CREATE INDEX idx_jobs_title ON public.jobs(title);
CREATE INDEX idx_jobs_location ON public.jobs(location);
CREATE INDEX idx_jobs_is_active ON public.jobs(is_active);
CREATE INDEX idx_jobs_required_skills ON public.jobs USING GIN (required_skills);
CREATE INDEX idx_jobs_posted_date ON public.jobs(posted_date DESC);
CREATE INDEX idx_jobs_external_source ON public.jobs(external_id, source);

CREATE INDEX idx_user_job_applications_user_id ON public.user_job_applications(user_id);
CREATE INDEX idx_user_job_applications_job_id ON public.user_job_applications(job_id);
CREATE INDEX idx_user_job_applications_status ON public.user_job_applications(status);
CREATE INDEX idx_user_job_applications_readiness_score ON public.user_job_applications(readiness_score DESC);

CREATE INDEX idx_hiring_feedback_user_id ON public.hiring_feedback(user_id);
CREATE INDEX idx_hiring_feedback_job_title ON public.hiring_feedback(job_title);
CREATE INDEX idx_hiring_feedback_important_skills ON public.hiring_feedback USING GIN (important_skills);

CREATE INDEX idx_recruiter_searches_recruiter_id ON public.recruiter_searches(recruiter_user_id);
CREATE INDEX idx_recruiter_candidate_views_recruiter_id ON public.recruiter_candidate_views(recruiter_user_id);
CREATE INDEX idx_recruiter_candidate_views_candidate_id ON public.recruiter_candidate_views(candidate_user_id);

-- ============================================
-- ROW LEVEL SECURITY
-- ============================================

-- Companies (public read for job seekers, write for service/recruiters)
ALTER TABLE public.companies ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Anyone can view companies" ON public.companies FOR SELECT USING (true);
CREATE POLICY "Recruiter admins can update their company" ON public.companies FOR UPDATE 
    USING (auth.uid() = recruiter_admin_id);
CREATE POLICY "Service role can manage companies" ON public.companies FOR ALL USING (current_user = 'postgres');

-- Jobs (public read for active jobs)
ALTER TABLE public.jobs ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Anyone can view active jobs" ON public.jobs FOR SELECT USING (is_active = true);
CREATE POLICY "Service role can manage jobs" ON public.jobs FOR ALL USING (current_user = 'postgres');

-- User Applications (users can only see their own)
ALTER TABLE public.user_job_applications ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own applications" ON public.user_job_applications FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own applications" ON public.user_job_applications FOR ALL USING (auth.uid() = user_id);

-- Hiring Feedback (users can only see their own)
ALTER TABLE public.hiring_feedback ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can create own feedback" ON public.hiring_feedback FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Service role can view all feedback" ON public.hiring_feedback FOR SELECT USING (current_user = 'postgres');

-- Recruiter Data (only visible to recruiters and service role)
ALTER TABLE public.recruiter_searches ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Recruiters can view own searches" ON public.recruiter_searches FOR SELECT 
    USING (auth.uid() = recruiter_user_id);
CREATE POLICY "Recruiters can create searches" ON public.recruiter_searches FOR INSERT 
    WITH CHECK (auth.uid() = recruiter_user_id);

ALTER TABLE public.recruiter_candidate_views ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Recruiters can view own candidate views" ON public.recruiter_candidate_views FOR SELECT 
    USING (auth.uid() = recruiter_user_id);
CREATE POLICY "Recruiters can create views" ON public.recruiter_candidate_views FOR INSERT 
    WITH CHECK (auth.uid() = recruiter_user_id);

-- Grant permissions
GRANT SELECT ON public.companies TO authenticated, service_role;
GRANT UPDATE ON public.companies TO authenticated, service_role;
GRANT SELECT ON public.jobs TO authenticated, service_role;
GRANT ALL ON public.user_job_applications TO authenticated, service_role;
GRANT INSERT ON public.hiring_feedback TO authenticated;
GRANT SELECT ON public.hiring_feedback TO service_role;
GRANT ALL ON public.recruiter_searches TO authenticated, service_role;
GRANT ALL ON public.recruiter_candidate_views TO authenticated, service_role;
