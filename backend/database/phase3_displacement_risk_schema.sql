-- ========================================
-- PHASE 3: AI DISPLACEMENT RISK ENGINE
-- Database Schema v1.0
-- Created: November 16, 2025
-- ========================================

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ========================================
-- TABLE 1: AI TASK TAXONOMY
-- Task-level automation potential from O*NET + research
-- ========================================

CREATE TABLE IF NOT EXISTS public.ai_task_taxonomy (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Task identification
    occupation_code VARCHAR(10) NOT NULL, -- O*NET SOC code (e.g., "15-2051")
    task_id VARCHAR(50) NOT NULL, -- O*NET Task ID
    task_name TEXT NOT NULL,
    task_description TEXT,
    
    -- Task importance (from O*NET)
    importance_score DECIMAL(3,2), -- 0.00 to 1.00
    frequency_score DECIMAL(3,2), -- 0.00 to 1.00
    
    -- Automation potential
    technical_capability DECIMAL(3,2), -- 0.00 to 1.00 (Can AI do this technically?)
    economic_viability DECIMAL(3,2), -- 0.00 to 1.00 (Is it cost-effective?)
    task_risk DECIMAL(3,2) GENERATED ALWAYS AS (technical_capability * economic_viability) STORED,
    
    -- Metadata
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    data_source VARCHAR(100), -- "McKinsey 2023", "OpenAI Research", etc.
    confidence_level DECIMAL(3,2), -- 0.00 to 1.00
    
    -- Constraints
    UNIQUE(occupation_code, task_id)
);

-- Indexes for fast queries
CREATE INDEX IF NOT EXISTS idx_task_taxonomy_occupation ON public.ai_task_taxonomy(occupation_code);
CREATE INDEX IF NOT EXISTS idx_task_taxonomy_risk ON public.ai_task_taxonomy(task_risk DESC);
CREATE INDEX IF NOT EXISTS idx_task_taxonomy_updated ON public.ai_task_taxonomy(last_updated DESC);

-- Table comment
COMMENT ON TABLE public.ai_task_taxonomy IS 
'Task-level automation scores from O*NET database combined with AI capability research. 
Used to calculate Task Automation Score (TAS) for each occupation.';

COMMENT ON COLUMN public.ai_task_taxonomy.technical_capability IS 
'0-1 score: Can current AI technology perform this task? Based on research papers and model capabilities.';

COMMENT ON COLUMN public.ai_task_taxonomy.economic_viability IS 
'0-1 score: Is it economically viable to automate this task? Considers development cost vs labor savings.';

COMMENT ON COLUMN public.ai_task_taxonomy.task_risk IS 
'Computed as technical_capability × economic_viability. Higher = more likely to be automated.';

-- ========================================
-- TABLE 2: AUTOMATION EVIDENCE
-- Evidence for automation capability per task/skill
-- ========================================

CREATE TABLE IF NOT EXISTS public.automation_evidence (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Link to task or skill
    entity_type VARCHAR(20) NOT NULL, -- 'task' or 'skill'
    entity_id VARCHAR(100) NOT NULL, -- task_id or skill_name
    
    -- Evidence data
    technical_capability DECIMAL(3,2), -- 0.00 to 1.00
    economic_viability DECIMAL(3,2), -- 0.00 to 1.00
    adoption_trend DECIMAL(3,2), -- -1.00 to +1.00 (declining to growing)
    
    -- For skills specifically
    substitutability DECIMAL(3,2), -- 0.00 to 1.00 (AI replaces this skill)
    complementarity DECIMAL(3,2), -- 0.00 to 1.00 (AI enhances this skill)
    
    -- Evidence metadata
    evidence_source TEXT, -- Paper, article, model capability
    published_date DATE,
    confidence_level DECIMAL(3,2),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CHECK (entity_type IN ('task', 'skill')),
    CHECK (technical_capability BETWEEN 0 AND 1),
    CHECK (economic_viability BETWEEN 0 AND 1),
    CHECK (adoption_trend BETWEEN -1 AND 1)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_automation_evidence_entity ON public.automation_evidence(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_automation_evidence_substitutability ON public.automation_evidence(substitutability DESC);
CREATE INDEX IF NOT EXISTS idx_automation_evidence_published ON public.automation_evidence(published_date DESC);

-- Table comment
COMMENT ON TABLE public.automation_evidence IS 
'Research evidence for AI automation capabilities per task or skill. 
Sources: academic papers, industry reports, model benchmarks.';

COMMENT ON COLUMN public.automation_evidence.substitutability IS 
'How much can AI replace this skill? High = AI does it instead of humans.';

COMMENT ON COLUMN public.automation_evidence.complementarity IS 
'How much does AI enhance this skill? High = humans with AI are more valuable.';

-- ========================================
-- TABLE 3: SKILL DEMAND HISTORY
-- Market demand trends for skills over time
-- ========================================

CREATE TABLE IF NOT EXISTS public.skill_demand_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Skill identification
    skill_name VARCHAR(100) NOT NULL,
    skill_category VARCHAR(50), -- 'technical', 'soft', 'domain', 'ai-enhanced'
    
    -- Market context
    industry VARCHAR(100), -- 'tech', 'finance', 'healthcare', 'all'
    occupation_code VARCHAR(10), -- O*NET code, NULL for industry-wide
    geography VARCHAR(50) DEFAULT 'US', -- 'US', 'CA', 'NYC', etc.
    
    -- Demand metrics (normalized 0-1)
    demand_score DECIMAL(3,2) NOT NULL, -- Current demand level
    trend_score DECIMAL(4,2), -- -1.00 to +1.00 (declining to growing)
    
    -- Volume metrics (raw counts for context)
    job_posting_count INT, -- # of postings mentioning this skill
    job_posting_growth_30d DECIMAL(5,2), -- % change vs 30 days ago
    job_posting_growth_365d DECIMAL(5,2), -- % change vs 365 days ago
    
    -- AI-specific tracking
    ai_job_postings INT, -- Postings mentioning AI + this skill
    legacy_job_postings INT, -- Postings with this skill but NO AI mention
    
    -- Time tracking
    snapshot_date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CHECK (demand_score BETWEEN 0 AND 1),
    CHECK (trend_score BETWEEN -1 AND 1),
    UNIQUE(skill_name, industry, occupation_code, geography, snapshot_date)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_skill_demand_skill ON public.skill_demand_history(skill_name);
CREATE INDEX IF NOT EXISTS idx_skill_demand_industry ON public.skill_demand_history(industry);
CREATE INDEX IF NOT EXISTS idx_skill_demand_occupation ON public.skill_demand_history(occupation_code);
CREATE INDEX IF NOT EXISTS idx_skill_demand_date ON public.skill_demand_history(snapshot_date DESC);
CREATE INDEX IF NOT EXISTS idx_skill_demand_trend ON public.skill_demand_history(trend_score DESC);
CREATE INDEX IF NOT EXISTS idx_skill_demand_category ON public.skill_demand_history(skill_category);

-- Table comment
COMMENT ON TABLE public.skill_demand_history IS 
'365-day historical tracking of skill demand across industries and geographies. 
Updated daily from job posting APIs (LinkedIn, Indeed, Adzuna). 
Used to calculate Industry Velocity Score (IVS) and Personal Skill Currency (PSC).';

COMMENT ON COLUMN public.skill_demand_history.ai_job_postings IS 
'Count of job postings that mention both this skill AND AI-related keywords.
High ratio of ai_job_postings/total indicates skill is becoming AI-enhanced.';

COMMENT ON COLUMN public.skill_demand_history.legacy_job_postings IS 
'Count of job postings with this skill but NO AI keywords.
Declining legacy postings indicates AI is replacing this skill.';

-- ========================================
-- TABLE 4: USER ACTION LOG
-- User learning and adaptation actions
-- ========================================

CREATE TABLE IF NOT EXISTS public.user_action_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    
    -- Action type
    action_type VARCHAR(50) NOT NULL,
    -- Values: 'course_completed_generic', 'course_completed_with_cert',
    --         'assessment_passed', 'project_completed_tagged_with_skill',
    --         'new_skill_added_to_profile', 'mentor_session_completed'
    
    -- Action details
    action_title TEXT,
    action_description TEXT,
    linked_skills TEXT[], -- Array of skill names
    
    -- Quality signals (for AS calculation)
    has_certificate BOOLEAN DEFAULT FALSE,
    has_verified_project BOOLEAN DEFAULT FALSE,
    skill_level_achieved VARCHAR(20), -- 'beginner', 'intermediate', 'advanced'
    
    -- Metadata
    platform VARCHAR(100), -- 'Coursera', 'Udemy', 'GitHub', 'Internal'
    external_url TEXT,
    
    -- Timestamps
    completed_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CHECK (action_type IN (
        'course_completed_generic',
        'course_completed_with_cert',
        'assessment_passed',
        'project_completed_tagged_with_skill',
        'new_skill_added_to_profile',
        'mentor_session_completed',
        'skill_assessment_passed',
        'workshop_attended'
    ))
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_user_action_user ON public.user_action_log(user_id);
CREATE INDEX IF NOT EXISTS idx_user_action_type ON public.user_action_log(action_type);
CREATE INDEX IF NOT EXISTS idx_user_action_completed ON public.user_action_log(completed_at DESC);
CREATE INDEX IF NOT EXISTS idx_user_action_skills ON public.user_action_log USING GIN(linked_skills);
CREATE INDEX IF NOT EXISTS idx_user_action_certified ON public.user_action_log(has_certificate) WHERE has_certificate = TRUE;

-- Table comment
COMMENT ON TABLE public.user_action_log IS 
'Tracks all user learning and skill development actions for Adaptability Score (AS) calculation.
This is the core of the data flywheel: more actions → better AS → lower risk → more trust.';

COMMENT ON COLUMN public.user_action_log.action_type IS 
'Type of learning action. Used to assign base points in AS calculation:
- course_completed_generic: 8 pts
- course_completed_with_cert: 12 pts
- assessment_passed: 15 pts
- project_completed_tagged_with_skill: 15 pts
- new_skill_added_to_profile: 5 pts
- mentor_session_completed: 10 pts';

COMMENT ON COLUMN public.user_action_log.linked_skills IS 
'Array of skill names this action develops. Used to apply quality multipliers 
if the linked skills have high PSC (Personal Skill Currency).';

-- ========================================
-- TABLE 5: RISK CALCULATION SNAPSHOTS
-- Historical risk calculations for trajectory tracking
-- ========================================

CREATE TABLE IF NOT EXISTS public.risk_calculation_snapshots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    
    -- Target job
    occupation_code VARCHAR(10),
    industry VARCHAR(100),
    
    -- Core scores
    displacement_risk DECIMAL(5,2) NOT NULL, -- 0.00 to 100.00
    structural_risk DECIMAL(5,2),
    personal_shield DECIMAL(5,2),
    
    -- Component scores (for debugging and analysis)
    tas_score DECIMAL(5,2),
    ivs_score DECIMAL(5,2),
    psc_score DECIMAL(5,2),
    adaptability_score DECIMAL(5,2),
    seniority_score DECIMAL(5,2),
    credential_score DECIMAL(5,2),
    
    -- Context
    time_horizon VARCHAR(20), -- "0-2 years", "2-5 years", "5+ years"
    time_horizon_index DECIMAL(3,2),
    confidence_score DECIMAL(5,2),
    
    -- Comparison
    percentile_vs_role DECIMAL(5,2), -- 0-100 (higher = safer than peers)
    
    -- Timestamp
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CHECK (displacement_risk BETWEEN 0 AND 100),
    CHECK (time_horizon IN ('0–2 years', '2–5 years', '5+ years'))
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_risk_snapshot_user ON public.risk_calculation_snapshots(user_id);
CREATE INDEX IF NOT EXISTS idx_risk_snapshot_date ON public.risk_calculation_snapshots(calculated_at DESC);
CREATE INDEX IF NOT EXISTS idx_risk_snapshot_occupation ON public.risk_calculation_snapshots(occupation_code);
CREATE INDEX IF NOT EXISTS idx_risk_snapshot_risk ON public.risk_calculation_snapshots(displacement_risk DESC);

-- Table comment
COMMENT ON TABLE public.risk_calculation_snapshots IS 
'Historical snapshots of risk calculations for each user. 
Used to calculate trajectory (improving/stable/worsening) by comparing current risk to T-90 days.
Also used for analytics and model refinement.';

-- ========================================
-- TABLE 6: RISK PERCENTILES BY ROLE
-- Pre-computed peer comparison percentiles
-- ========================================

CREATE TABLE IF NOT EXISTS public.risk_percentiles_by_role (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    occupation_code VARCHAR(10) NOT NULL,
    industry VARCHAR(100),
    
    -- Percentile buckets (pre-computed from risk_calculation_snapshots)
    p10 DECIMAL(5,2), -- 10th percentile risk score (lowest risk)
    p25 DECIMAL(5,2),
    p50 DECIMAL(5,2), -- Median
    p75 DECIMAL(5,2),
    p90 DECIMAL(5,2), -- 90th percentile (highest risk)
    
    -- Sample size
    sample_count INT,
    
    -- Timestamps
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(occupation_code, industry)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_risk_percentiles_occupation ON public.risk_percentiles_by_role(occupation_code);
CREATE INDEX IF NOT EXISTS idx_risk_percentiles_industry ON public.risk_percentiles_by_role(industry);
CREATE INDEX IF NOT EXISTS idx_risk_percentiles_updated ON public.risk_percentiles_by_role(last_updated DESC);

-- Table comment
COMMENT ON TABLE public.risk_percentiles_by_role IS 
'Pre-computed percentile distributions of risk scores by occupation and industry.
Updated weekly from risk_calculation_snapshots aggregation.
Enables fast "You are safer than X% of peers" comparisons without scanning entire history.';

-- ========================================
-- MATERIALIZED VIEW: SKILL DEMAND LATEST
-- Fast access to latest skill demand scores
-- ========================================

CREATE MATERIALIZED VIEW IF NOT EXISTS public.skill_demand_latest AS
SELECT DISTINCT ON (skill_name, industry, occupation_code, geography)
    skill_name,
    skill_category,
    industry,
    occupation_code,
    geography,
    demand_score,
    trend_score,
    job_posting_count,
    job_posting_growth_30d,
    job_posting_growth_365d,
    ai_job_postings,
    legacy_job_postings,
    snapshot_date
FROM public.skill_demand_history
ORDER BY skill_name, industry, occupation_code, geography, snapshot_date DESC;

-- Index on materialized view
CREATE INDEX IF NOT EXISTS idx_skill_demand_latest_skill ON public.skill_demand_latest(skill_name);
CREATE INDEX IF NOT EXISTS idx_skill_demand_latest_industry ON public.skill_demand_latest(industry);

COMMENT ON MATERIALIZED VIEW public.skill_demand_latest IS 
'Latest skill demand snapshot per skill/industry/occupation.
Refreshed daily after skill_demand_history updates.
Provides fast lookups for PSC and IVS calculations.';

-- ========================================
-- FUNCTIONS: HELPER UTILITIES
-- ========================================

-- Function to refresh skill demand materialized view
CREATE OR REPLACE FUNCTION refresh_skill_demand_latest()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY public.skill_demand_latest;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION refresh_skill_demand_latest IS 
'Refresh the skill_demand_latest materialized view. 
Should be called daily after new skill_demand_history data is inserted.';

-- Function to update risk percentiles
CREATE OR REPLACE FUNCTION update_risk_percentiles()
RETURNS void AS $$
BEGIN
    -- Clear old percentiles
    TRUNCATE TABLE public.risk_percentiles_by_role;
    
    -- Calculate new percentiles from last 90 days of snapshots
    INSERT INTO public.risk_percentiles_by_role (
        occupation_code,
        industry,
        p10, p25, p50, p75, p90,
        sample_count,
        last_updated
    )
    SELECT
        occupation_code,
        industry,
        PERCENTILE_CONT(0.10) WITHIN GROUP (ORDER BY displacement_risk) AS p10,
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY displacement_risk) AS p25,
        PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY displacement_risk) AS p50,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY displacement_risk) AS p75,
        PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY displacement_risk) AS p90,
        COUNT(*) AS sample_count,
        NOW() AS last_updated
    FROM public.risk_calculation_snapshots
    WHERE calculated_at >= NOW() - INTERVAL '90 days'
      AND occupation_code IS NOT NULL
      AND industry IS NOT NULL
    GROUP BY occupation_code, industry
    HAVING COUNT(*) >= 10; -- Only calculate if we have enough samples
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION update_risk_percentiles IS 
'Recalculate risk percentiles from the last 90 days of risk snapshots.
Should be run weekly to keep peer comparisons current.';

-- ========================================
-- GRANTS & PERMISSIONS
-- ========================================

-- Grant read/write access to application role
-- (Adjust role name as needed for your setup)
GRANT SELECT, INSERT, UPDATE, DELETE ON public.ai_task_taxonomy TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.automation_evidence TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.skill_demand_history TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.user_action_log TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.risk_calculation_snapshots TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.risk_percentiles_by_role TO authenticated;
GRANT SELECT ON public.skill_demand_latest TO authenticated;

-- ========================================
-- SAMPLE DATA (FOR TESTING)
-- ========================================

-- Sample task for Software Developers
INSERT INTO public.ai_task_taxonomy (
    occupation_code, task_id, task_name, task_description,
    importance_score, frequency_score,
    technical_capability, economic_viability,
    data_source, confidence_level
) VALUES (
    '15-2051', 'T001', 'Write code', 'Develop and maintain software applications',
    0.95, 0.90,
    0.70, 0.75,
    'OpenAI GPT-4 Capabilities 2024', 0.80
) ON CONFLICT (occupation_code, task_id) DO NOTHING;

-- Sample skill demand
INSERT INTO public.skill_demand_history (
    skill_name, skill_category, industry, geography,
    demand_score, trend_score,
    job_posting_count, job_posting_growth_30d, job_posting_growth_365d,
    ai_job_postings, legacy_job_postings,
    snapshot_date
) VALUES (
    'Python', 'technical', 'tech', 'US',
    0.92, 0.25,
    45000, 5.2, 18.5,
    12000, 33000,
    CURRENT_DATE
) ON CONFLICT (skill_name, industry, occupation_code, geography, snapshot_date) DO NOTHING;

-- Sample automation evidence
INSERT INTO public.automation_evidence (
    entity_type, entity_id,
    technical_capability, economic_viability, adoption_trend,
    substitutability, complementarity,
    evidence_source, published_date, confidence_level
) VALUES (
    'skill', 'Python',
    0.75, 0.80, 0.30,
    0.40, 0.85,
    'GitHub Copilot Usage Study 2024', '2024-01-15', 0.85
) ON CONFLICT DO NOTHING;

-- ========================================
-- VALIDATION QUERIES
-- ========================================

-- Check table creation
DO $$
DECLARE
    table_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO table_count
    FROM information_schema.tables
    WHERE table_schema = 'public'
      AND table_name IN (
          'ai_task_taxonomy',
          'automation_evidence',
          'skill_demand_history',
          'user_action_log',
          'risk_calculation_snapshots',
          'risk_percentiles_by_role'
      );
    
    IF table_count = 6 THEN
        RAISE NOTICE '✅ All 6 displacement risk tables created successfully';
    ELSE
        RAISE EXCEPTION '❌ Only % of 6 tables created', table_count;
    END IF;
END $$;

-- ========================================
-- MIGRATION COMPLETE
-- ========================================

COMMENT ON SCHEMA public IS 
'Career OS - Phase 3: AI Displacement Risk Engine
Schema Version: 1.0
Created: 2025-11-16
Status: Production Ready';
