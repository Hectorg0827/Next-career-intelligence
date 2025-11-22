-- ========================================
-- SKILL GRAPH SCHEMA
-- ========================================

-- 1. Global Skills Taxonomy
CREATE TABLE IF NOT EXISTS public.skills (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    category VARCHAR(100), -- 'Technical', 'Soft', 'Domain', 'Tool', 'Language'
    aliases JSONB DEFAULT '[]'::jsonb, -- Array of strings: ["react.js", "reactjs"]
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Index for fast lookups by name
CREATE INDEX IF NOT EXISTS idx_skills_name ON public.skills(name);

-- 2. User Skills (The "Skill Graph" edges)
CREATE TABLE IF NOT EXISTS public.user_skills (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    skill_id UUID NOT NULL REFERENCES public.skills(id) ON DELETE CASCADE,
    
    -- Proficiency & Confidence
    proficiency_level INT CHECK (proficiency_level BETWEEN 1 AND 5), -- 1=Beginner, 5=Expert
    confidence_score FLOAT CHECK (confidence_score BETWEEN 0 AND 1), -- AI confidence
    
    -- Metadata
    source_tags JSONB DEFAULT '[]'::jsonb, -- ["resume", "conversation", "task", "inferred_prior"]
    evidence_snippets JSONB DEFAULT '[]'::jsonb, -- Array of strings: ["Mentioned using React in project X"]
    
    -- User Validation
    confirmed_by_user BOOLEAN DEFAULT false,
    hidden BOOLEAN DEFAULT false, -- If user wants to hide a skill
    
    last_updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    
    -- Ensure unique skill per user
    CONSTRAINT unique_user_skill UNIQUE(user_id, skill_id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_user_skills_user_id ON public.user_skills(user_id);
CREATE INDEX IF NOT EXISTS idx_user_skills_skill_id ON public.user_skills(skill_id);

-- 3. Role Skill Templates (Priors)
CREATE TABLE IF NOT EXISTS public.role_skill_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    occupation_code VARCHAR(255) NOT NULL UNIQUE, -- e.g., "police_officer", "software_engineer"
    role_title VARCHAR(255) NOT NULL,
    
    -- The template
    skills JSONB NOT NULL, -- Array of objects: [{"name": "Conflict Resolution", "confidence": 0.8, "category": "Soft"}]
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Index
CREATE INDEX IF NOT EXISTS idx_role_templates_code ON public.role_skill_templates(occupation_code);

-- ========================================
-- RLS POLICIES
-- ========================================

-- Enable RLS
ALTER TABLE public.skills ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_skills ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.role_skill_templates ENABLE ROW LEVEL SECURITY;

-- Skills: Publicly readable, admin writable (or AI service writable)
DROP POLICY IF EXISTS "Everyone can view skills" ON public.skills;
CREATE POLICY "Everyone can view skills" ON public.skills
    FOR SELECT USING (true);

-- User Skills: Users manage their own
DROP POLICY IF EXISTS "Users can view own skills" ON public.user_skills;
CREATE POLICY "Users can view own skills" ON public.user_skills
    FOR SELECT USING (user_id IN (
        SELECT id FROM public.users WHERE firebase_uid = auth.uid()::text
    ));

DROP POLICY IF EXISTS "Users can insert own skills" ON public.user_skills;
CREATE POLICY "Users can insert own skills" ON public.user_skills
    FOR INSERT WITH CHECK (user_id IN (
        SELECT id FROM public.users WHERE firebase_uid = auth.uid()::text
    ));

DROP POLICY IF EXISTS "Users can update own skills" ON public.user_skills;
CREATE POLICY "Users can update own skills" ON public.user_skills
    FOR UPDATE USING (user_id IN (
        SELECT id FROM public.users WHERE firebase_uid = auth.uid()::text
    ));

DROP POLICY IF EXISTS "Users can delete own skills" ON public.user_skills;
CREATE POLICY "Users can delete own skills" ON public.user_skills
    FOR DELETE USING (user_id IN (
        SELECT id FROM public.users WHERE firebase_uid = auth.uid()::text
    ));

-- Role Templates: Publicly readable
DROP POLICY IF EXISTS "Everyone can view role templates" ON public.role_skill_templates;
CREATE POLICY "Everyone can view role templates" ON public.role_skill_templates
    FOR SELECT USING (true);

-- Grant permissions
GRANT ALL ON public.role_skill_templates TO anon, authenticated;

-- Add missing columns if they don't exist (for updates)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'user_skills' AND column_name = 'evidence_source') THEN
        ALTER TABLE public.user_skills ADD COLUMN evidence_source VARCHAR(50);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'user_skills' AND column_name = 'last_used_year') THEN
        ALTER TABLE public.user_skills ADD COLUMN last_used_year FLOAT;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'user_skills' AND column_name = 'created_at') THEN
        ALTER TABLE public.user_skills ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'user_skills' AND column_name = 'updated_at') THEN
        ALTER TABLE public.user_skills ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'skills' AND column_name = 'normalized_name') THEN
        ALTER TABLE public.skills ADD COLUMN normalized_name VARCHAR(255);
        CREATE INDEX IF NOT EXISTS idx_skills_normalized_name ON public.skills(normalized_name);
    END IF;

    -- Update proficiency_level constraint to 1-10
    ALTER TABLE public.user_skills DROP CONSTRAINT IF EXISTS user_skills_proficiency_level_check;
    ALTER TABLE public.user_skills ADD CONSTRAINT user_skills_proficiency_level_check CHECK (proficiency_level BETWEEN 1 AND 10);
END $$;

-- Create Education table if not exists
CREATE TABLE IF NOT EXISTS public.education (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    degree VARCHAR(255) NOT NULL,
    institution VARCHAR(255) NOT NULL,
    field_of_study VARCHAR(255),
    start_year FLOAT,
    end_year FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_education_user_id ON public.education(user_id);

-- Education Policies
ALTER TABLE public.education ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view own education" ON public.education;
CREATE POLICY "Users can view own education" ON public.education
    FOR SELECT USING (user_id IN (
        SELECT id FROM public.users WHERE firebase_uid = auth.uid()::text
    ));

DROP POLICY IF EXISTS "Users can insert own education" ON public.education;
CREATE POLICY "Users can insert own education" ON public.education
    FOR INSERT WITH CHECK (user_id IN (
        SELECT id FROM public.users WHERE firebase_uid = auth.uid()::text
    ));

DROP POLICY IF EXISTS "Users can update own education" ON public.education;
CREATE POLICY "Users can update own education" ON public.education
    FOR UPDATE USING (user_id IN (
        SELECT id FROM public.users WHERE firebase_uid = auth.uid()::text
    ));

DROP POLICY IF EXISTS "Users can delete own education" ON public.education;
CREATE POLICY "Users can delete own education" ON public.education
    FOR DELETE USING (user_id IN (
        SELECT id FROM public.users WHERE firebase_uid = auth.uid()::text
    ));

GRANT ALL ON public.education TO anon, authenticated;
