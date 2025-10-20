-- ========================================
-- JOBS MARKETPLACE SCHEMA
-- Real jobs with AI matching & auto-apply
-- ========================================

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- Fuzzy text search
CREATE EXTENSION IF NOT EXISTS "vector";    -- pgvector for embeddings

-- ========================================
-- EMPLOYERS & JOBS
-- ========================================

-- Employers/Companies
CREATE TABLE IF NOT EXISTS public.employers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Company info
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE,
    domain VARCHAR(255),
    logo_url TEXT,
    website TEXT,

    -- Details
    description TEXT,
    industry VARCHAR(100),
    size_range VARCHAR(50), -- "1-10", "11-50", "51-200", "201-500", "501-1000", "1000+"
    headquarters VARCHAR(255),
    founded_year INTEGER,

    -- Contact
    careers_page TEXT,
    contact_email VARCHAR(255),

    -- Portal access
    has_portal_access BOOLEAN DEFAULT false,
    portal_tier VARCHAR(50), -- "free", "basic", "premium", "enterprise"

    -- Metadata
    verified BOOLEAN DEFAULT false,
    spam_score FLOAT DEFAULT 0,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Jobs (unified schema from all sources)
CREATE TABLE IF NOT EXISTS public.jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employer_id UUID REFERENCES public.employers(id) ON DELETE CASCADE,

    -- Basic info
    title VARCHAR(500) NOT NULL,
    normalized_title VARCHAR(255), -- "data_analyst_senior"
    seniority VARCHAR(50), -- "entry", "mid", "senior", "lead", "director", "vp", "executive"

    -- Description
    description TEXT NOT NULL,
    description_md TEXT, -- Markdown version
    requirements TEXT,
    responsibilities TEXT,
    benefits TEXT,

    -- Skills (extracted)
    skills_extracted JSONB DEFAULT '[]'::jsonb, -- ["Python", "SQL", "AWS"]
    skills_weight JSONB DEFAULT '{}'::jsonb, -- {"Python": 0.9, "SQL": 0.8}

    -- Location
    location_type VARCHAR(50), -- "remote", "hybrid", "onsite"
    location_city VARCHAR(255),
    location_state VARCHAR(100),
    location_country VARCHAR(100),
    headquarters VARCHAR(255),
    visa_sponsorship BOOLEAN DEFAULT false,

    -- Compensation
    salary_min INTEGER,
    salary_max INTEGER,
    salary_currency VARCHAR(10) DEFAULT 'USD',
    pay_type VARCHAR(50), -- "salary", "hourly", "contract"
    equity_offered BOOLEAN DEFAULT false,

    -- Work details
    employment_type VARCHAR(50), -- "full_time", "part_time", "contract", "internship"
    experience_years_min INTEGER,
    experience_years_max INTEGER,

    -- Application
    apply_url TEXT NOT NULL,
    external_id VARCHAR(255), -- ID from source (e.g., Greenhouse req ID)

    -- Source
    source VARCHAR(100) NOT NULL, -- "greenhouse", "lever", "ashby", "usajobs", "manual"
    source_data JSONB DEFAULT '{}'::jsonb, -- Raw data from source

    -- Embeddings for semantic search
    title_embedding vector(1536), -- OpenAI ada-002 or similar
    description_embedding vector(1536),
    combined_embedding vector(1536), -- Title + desc + skills

    -- Status
    status VARCHAR(50) DEFAULT 'active', -- "active", "expired", "filled", "paused"
    is_spam BOOLEAN DEFAULT false,
    spam_score FLOAT DEFAULT 0,

    -- Timestamps
    posted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_verified_at TIMESTAMP WITH TIME ZONE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ========================================
-- JOB MATCHING & RECOMMENDATIONS
-- ========================================

-- User job preferences
CREATE TABLE IF NOT EXISTS public.user_job_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,

    -- Search criteria
    desired_titles JSONB DEFAULT '[]'::jsonb,
    desired_industries JSONB DEFAULT '[]'::jsonb,
    desired_locations JSONB DEFAULT '[]'::jsonb,
    remote_only BOOLEAN DEFAULT false,

    -- Compensation
    salary_min INTEGER,
    salary_currency VARCHAR(10) DEFAULT 'USD',

    -- Constraints
    visa_required BOOLEAN DEFAULT false,
    willing_to_relocate BOOLEAN DEFAULT false,

    -- Preferences
    company_size_preference JSONB DEFAULT '[]'::jsonb, -- ["startup", "mid", "enterprise"]
    work_arrangement VARCHAR(50), -- "remote", "hybrid", "onsite", "flexible"

    -- Automation
    auto_apply_enabled BOOLEAN DEFAULT false,
    auto_apply_criteria JSONB DEFAULT '{}'::jsonb,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT unique_user_preferences UNIQUE(user_id)
);

-- Job recommendations (cached)
CREATE TABLE IF NOT EXISTS public.job_recommendations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    job_id UUID NOT NULL REFERENCES public.jobs(id) ON DELETE CASCADE,

    -- Matching scores
    overall_score FLOAT NOT NULL, -- 0-100
    skill_fit_score FLOAT, -- Component scores
    trajectory_fit_score FLOAT,
    value_match_score FLOAT,
    logistics_fit_score FLOAT,
    growth_potential_score FLOAT,

    -- Explanation
    match_highlights JSONB DEFAULT '[]'::jsonb,
    skill_gaps JSONB DEFAULT '[]'::jsonb,
    why_matched TEXT,

    -- AI insights
    displacement_risk_improvement FLOAT, -- How much this job reduces risk
    salary_uplift_potential FLOAT,
    growth_trajectory TEXT,

    -- Status
    status VARCHAR(50) DEFAULT 'pending', -- "pending", "viewed", "applied", "rejected", "expired"
    viewed_at TIMESTAMP WITH TIME ZONE,

    -- Ranking
    rank_position INTEGER,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT unique_user_job_rec UNIQUE(user_id, job_id)
);

-- ========================================
-- APPLICATIONS & TRACKING
-- ========================================

-- Job applications
CREATE TABLE IF NOT EXISTS public.job_applications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    job_id UUID NOT NULL REFERENCES public.jobs(id) ON DELETE CASCADE,
    employer_id UUID NOT NULL REFERENCES public.employers(id) ON DELETE CASCADE,

    -- Application materials
    resume_artifact_id UUID REFERENCES public.resume_artifacts(id),
    cover_letter_artifact_id UUID REFERENCES public.resume_artifacts(id),

    -- Tailored content (stored for reference)
    tailored_resume_text TEXT,
    cover_letter_text TEXT,

    -- Application method
    applied_via VARCHAR(50), -- "auto", "manual", "referral"
    apply_url TEXT,

    -- Status tracking
    status VARCHAR(50) DEFAULT 'submitted', -- "submitted", "screening", "interview", "offer", "rejected", "withdrawn"
    stage VARCHAR(100), -- Detailed stage from ATS

    -- Timeline
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_status_update TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Interview tracking
    interview_scheduled_at TIMESTAMP WITH TIME ZONE,
    interview_completed_at TIMESTAMP WITH TIME ZONE,

    -- Outcome
    offer_received BOOLEAN DEFAULT false,
    offer_amount INTEGER,
    offer_currency VARCHAR(10),
    accepted BOOLEAN,
    rejection_reason TEXT,

    -- Feedback
    user_feedback TEXT,
    user_rating INTEGER CHECK (user_rating >= 1 AND user_rating <= 5),

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Application status history
CREATE TABLE IF NOT EXISTS public.application_status_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    application_id UUID NOT NULL REFERENCES public.job_applications(id) ON DELETE CASCADE,

    from_status VARCHAR(50),
    to_status VARCHAR(50) NOT NULL,
    notes TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ========================================
-- JOB SCRAPING & INGESTION
-- ========================================

-- Job sources (configuration)
CREATE TABLE IF NOT EXISTS public.job_sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    name VARCHAR(255) NOT NULL UNIQUE,
    source_type VARCHAR(50) NOT NULL, -- "ats_api", "rss", "scraper", "manual", "partner"

    -- Configuration
    config JSONB DEFAULT '{}'::jsonb, -- API keys, endpoints, selectors

    -- Status
    is_active BOOLEAN DEFAULT true,
    last_run_at TIMESTAMP WITH TIME ZONE,
    last_success_at TIMESTAMP WITH TIME ZONE,
    last_error TEXT,

    -- Stats
    total_jobs_ingested INTEGER DEFAULT 0,
    jobs_ingested_today INTEGER DEFAULT 0,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Scraping jobs log
CREATE TABLE IF NOT EXISTS public.scraping_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id UUID REFERENCES public.job_sources(id) ON DELETE CASCADE,

    status VARCHAR(50), -- "running", "success", "failed"
    jobs_found INTEGER DEFAULT 0,
    jobs_new INTEGER DEFAULT 0,
    jobs_updated INTEGER DEFAULT 0,
    jobs_expired INTEGER DEFAULT 0,

    error_message TEXT,
    duration_seconds INTEGER,

    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- ========================================
-- EMPLOYER PORTAL
-- ========================================

-- Employer requisitions (from portal)
CREATE TABLE IF NOT EXISTS public.employer_requisitions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employer_id UUID NOT NULL REFERENCES public.employers(id) ON DELETE CASCADE,
    job_id UUID REFERENCES public.jobs(id), -- Created job

    -- Requisition details
    req_number VARCHAR(100),
    title VARCHAR(500) NOT NULL,
    department VARCHAR(255),
    hiring_manager VARCHAR(255),

    -- Requirements
    description TEXT NOT NULL,
    requirements JSONB DEFAULT '[]'::jsonb,

    -- Matching criteria
    min_experience_years INTEGER,
    required_skills JSONB DEFAULT '[]'::jsonb,
    nice_to_have_skills JSONB DEFAULT '[]'::jsonb,

    -- Budget
    budget_min INTEGER,
    budget_max INTEGER,

    -- Status
    status VARCHAR(50) DEFAULT 'draft', -- "draft", "active", "paused", "filled", "cancelled"
    positions_open INTEGER DEFAULT 1,
    positions_filled INTEGER DEFAULT 0,

    -- Portal settings
    anonymized_candidates BOOLEAN DEFAULT true,
    auto_match BOOLEAN DEFAULT true,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Candidate introductions (employer unlocks)
CREATE TABLE IF NOT EXISTS public.candidate_introductions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employer_id UUID NOT NULL REFERENCES public.employers(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    job_id UUID REFERENCES public.jobs(id) ON DELETE CASCADE,
    requisition_id UUID REFERENCES public.employer_requisitions(id),

    -- Introduction details
    match_score FLOAT,
    anonymized_profile JSONB, -- Skills, achievements, no PII

    -- Status
    status VARCHAR(50) DEFAULT 'pending', -- "pending", "unlocked", "interview_scheduled", "hired", "rejected"

    -- Payment
    unlock_fee INTEGER,
    paid_at TIMESTAMP WITH TIME ZONE,

    -- Interaction
    unlocked_at TIMESTAMP WITH TIME ZONE,
    employer_notes TEXT,

    -- Consent
    user_consented BOOLEAN DEFAULT false,
    consented_at TIMESTAMP WITH TIME ZONE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT unique_employer_user_job UNIQUE(employer_id, user_id, job_id)
);

-- ========================================
-- INDEXES
-- ========================================

-- Jobs indexes
CREATE INDEX IF NOT EXISTS idx_jobs_employer ON public.jobs(employer_id);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON public.jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_posted ON public.jobs(posted_at DESC);
CREATE INDEX IF NOT EXISTS idx_jobs_title ON public.jobs USING gin(to_tsvector('english', title));
CREATE INDEX IF NOT EXISTS idx_jobs_description ON public.jobs USING gin(to_tsvector('english', description));
CREATE INDEX IF NOT EXISTS idx_jobs_skills ON public.jobs USING gin(skills_extracted);
CREATE INDEX IF NOT EXISTS idx_jobs_location ON public.jobs(location_country, location_state, location_city);
CREATE INDEX IF NOT EXISTS idx_jobs_salary ON public.jobs(salary_min, salary_max);
CREATE INDEX IF NOT EXISTS idx_jobs_source ON public.jobs(source);

-- Vector similarity search (if using pgvector)
CREATE INDEX IF NOT EXISTS idx_jobs_combined_embedding ON public.jobs
    USING ivfflat (combined_embedding vector_cosine_ops) WITH (lists = 100);

-- Recommendations indexes
CREATE INDEX IF NOT EXISTS idx_recommendations_user ON public.job_recommendations(user_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_job ON public.job_recommendations(job_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_score ON public.job_recommendations(overall_score DESC);
CREATE INDEX IF NOT EXISTS idx_recommendations_status ON public.job_recommendations(status);

-- Applications indexes
CREATE INDEX IF NOT EXISTS idx_applications_user ON public.job_applications(user_id);
CREATE INDEX IF NOT EXISTS idx_applications_job ON public.job_applications(job_id);
CREATE INDEX IF NOT EXISTS idx_applications_employer ON public.job_applications(employer_id);
CREATE INDEX IF NOT EXISTS idx_applications_status ON public.job_applications(status);
CREATE INDEX IF NOT EXISTS idx_applications_submitted ON public.job_applications(submitted_at DESC);

-- Employer portal indexes
CREATE INDEX IF NOT EXISTS idx_requisitions_employer ON public.employer_requisitions(employer_id);
CREATE INDEX IF NOT EXISTS idx_requisitions_status ON public.employer_requisitions(status);
CREATE INDEX IF NOT EXISTS idx_introductions_employer ON public.candidate_introductions(employer_id);
CREATE INDEX IF NOT EXISTS idx_introductions_user ON public.candidate_introductions(user_id);
CREATE INDEX IF NOT EXISTS idx_introductions_status ON public.candidate_introductions(status);

-- ========================================
-- ROW LEVEL SECURITY
-- ========================================

ALTER TABLE public.employers ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_job_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.job_recommendations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.job_applications ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.employer_requisitions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.candidate_introductions ENABLE ROW LEVEL SECURITY;

-- Users can view active jobs
CREATE POLICY "Public jobs visible to all authenticated users" ON public.jobs
    FOR SELECT TO authenticated USING (status = 'active' AND is_spam = false);

-- Users can view their own preferences
CREATE POLICY "Users can manage own preferences" ON public.user_job_preferences
    FOR ALL TO authenticated USING (user_id IN (
        SELECT id FROM public.users WHERE firebase_uid = auth.uid()::text
    ));

-- Users can view their own recommendations
CREATE POLICY "Users can view own recommendations" ON public.job_recommendations
    FOR ALL TO authenticated USING (user_id IN (
        SELECT id FROM public.users WHERE firebase_uid = auth.uid()::text
    ));

-- Users can manage own applications
CREATE POLICY "Users can manage own applications" ON public.job_applications
    FOR ALL TO authenticated USING (user_id IN (
        SELECT id FROM public.users WHERE firebase_uid = auth.uid()::text
    ));

-- Employers can view own requisitions
CREATE POLICY "Employers can manage own requisitions" ON public.employer_requisitions
    FOR ALL TO authenticated USING (employer_id IN (
        SELECT employer_id FROM employer_users WHERE user_id IN (
            SELECT id FROM public.users WHERE firebase_uid = auth.uid()::text
        )
    ));

-- Grant permissions
GRANT ALL ON public.employers TO authenticated;
GRANT SELECT ON public.jobs TO authenticated;
GRANT ALL ON public.user_job_preferences TO authenticated;
GRANT ALL ON public.job_recommendations TO authenticated;
GRANT ALL ON public.job_applications TO authenticated;
GRANT ALL ON public.employer_requisitions TO authenticated;
GRANT ALL ON public.candidate_introductions TO authenticated;

-- ========================================
-- FUNCTIONS & TRIGGERS
-- ========================================

-- Update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_jobs_updated_at BEFORE UPDATE ON public.jobs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_applications_updated_at BEFORE UPDATE ON public.job_applications
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_employers_updated_at BEFORE UPDATE ON public.employers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Expire old jobs automatically
CREATE OR REPLACE FUNCTION expire_old_jobs()
RETURNS void AS $$
BEGIN
    UPDATE public.jobs
    SET status = 'expired'
    WHERE status = 'active'
    AND (
        expires_at < NOW()
        OR (last_verified_at IS NOT NULL AND last_verified_at < NOW() - INTERVAL '30 days')
        OR (last_verified_at IS NULL AND posted_at < NOW() - INTERVAL '60 days')
    );
END;
$$ LANGUAGE plpgsql;

-- Calculate match score (placeholder - will be overridden by Python)
CREATE OR REPLACE FUNCTION calculate_match_score(
    user_skills JSONB,
    job_skills JSONB
) RETURNS FLOAT AS $$
DECLARE
    overlap_count INTEGER;
    total_job_skills INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO overlap_count
    FROM jsonb_array_elements_text(user_skills) user_skill
    WHERE user_skill = ANY(SELECT jsonb_array_elements_text(job_skills));

    SELECT jsonb_array_length(job_skills) INTO total_job_skills;

    IF total_job_skills = 0 THEN
        RETURN 0;
    END IF;

    RETURN (overlap_count::FLOAT / total_job_skills::FLOAT) * 100;
END;
$$ LANGUAGE plpgsql;
