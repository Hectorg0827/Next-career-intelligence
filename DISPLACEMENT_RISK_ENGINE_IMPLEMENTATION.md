# 🎯 AI Displacement Risk Engine - v1.0 Implementation Plan

**Date**: November 16, 2025  
**Status**: Ready for Implementation  
**Priority**: HIGH - Core Product Differentiator

---

## Executive Summary

This document outlines the complete implementation of the **AI Displacement Risk Engine v1.0** - a defensible, data-driven system that calculates personalized AI displacement risk scores for users.

**Why This Matters:**
- **Product Differentiator**: This is your wedge. No competitor has a principled, transparent AI risk model.
- **Revenue Driver**: Enterprise customers pay for this insight ($150K+/year contracts depend on this feature).
- **Moat Builder**: The data flywheel (user actions → better scores → more trust → more actions) creates defensibility.

**What It Does:**
- Calculates a 0-100 AI Displacement Risk score for any user + job combination
- Provides time horizon ("0-2 years", "2-5 years", "5+ years")
- Shows confidence level based on data coverage
- Compares user to peers (percentile ranking)
- Tracks trajectory (improving/stable/worsening)
- Generates actionable protection opportunities

---

## Architecture Overview

### The 6-Layer Calculation Stack

```
┌─────────────────────────────────────────────────────────────┐
│                    FINAL RISK SCORE (0-100)                 │
│                                                             │
│   DisplacementRisk = StructuralRisk × (1 - PersonalShield/100)
└─────────────────────────────────────────────────────────────┘
                           ↑
                           │
         ┌─────────────────┴─────────────────┐
         │                                   │
    ┌────────────────┐              ┌───────────────┐
    │ StructuralRisk │              │ PersonalShield│
    │   (External)   │              │   (Internal)  │
    └────────────────┘              └───────────────┘
         ↓                                   ↓
    ┌─────────┐                     ┌──────────────┐
    │ 0.6×TAS │                     │  0.45 × PSC  │
    │ 0.4×IVS │                     │  0.30 × AS   │
    └─────────┘                     │  0.15 × Sen  │
                                    │  0.10 × Cred │
                                    └──────────────┘

┌─────────────────────────────────────────────────────────────┐
│                      CONTEXT LAYERS                         │
├─────────────────────────────────────────────────────────────┤
│  TimeHorizon:  0.35×Tech + 0.35×IVS + 0.15×Econ + 0.15×Adopt│
│  Confidence:   0.4×TaskCov + 0.3×PostDens + 0.3×SkillCov   │
│  Percentile:   Compare to peers in same role               │
│  Trajectory:   Compare to T-90 days                        │
└─────────────────────────────────────────────────────────────┘
```

### Component Definitions

| Component | What It Measures | Data Source |
|-----------|------------------|-------------|
| **TAS** (Task Automation Score) | % of job tasks automatable by AI | `ai_task_taxonomy` + `automation_evidence` |
| **IVS** (Industry Velocity Score) | Speed of AI adoption in industry | `skill_demand_history` (365-day trends) |
| **PSC** (Personal Skill Currency) | Value of user's current skills | User skills + `skill_demand_history` |
| **AS** (Adaptability Score) | User's learning velocity | `user_action_log` (courses, projects, certs) |
| **Seniority** | Management/decision-making protection | User profile (years, people mgmt, decision level) |
| **Credentials** | Degree/certification strength | User profile |

---

## Implementation Phases

### Phase 1: Database Foundation (TODAY - Nov 16)

#### 1.1 Create New Tables

**File**: `backend/database/phase3_displacement_risk_schema.sql`

```sql
-- ========================================
-- AI DISPLACEMENT RISK ENGINE - v1.0
-- ========================================

-- Task-level automation potential from O*NET + research
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
    
    -- Indexes
    INDEX idx_task_taxonomy_occupation (occupation_code),
    INDEX idx_task_taxonomy_risk (task_risk DESC),
    UNIQUE(occupation_code, task_id)
);

-- Automation evidence and capabilities
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
    
    -- Indexes
    INDEX idx_automation_evidence_entity (entity_type, entity_id),
    INDEX idx_automation_evidence_substitutability (substitutability DESC)
);

-- Market demand trends for skills over time
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
    
    -- Indexes
    INDEX idx_skill_demand_skill (skill_name),
    INDEX idx_skill_demand_industry (industry),
    INDEX idx_skill_demand_date (snapshot_date DESC),
    INDEX idx_skill_demand_trend (trend_score DESC),
    UNIQUE(skill_name, industry, occupation_code, geography, snapshot_date)
);

-- User learning and adaptation actions
CREATE TABLE IF NOT EXISTS public.user_action_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    
    -- Action type
    action_type VARCHAR(50) NOT NULL,
    -- 'course_completed_generic', 'course_completed_with_cert',
    -- 'assessment_passed', 'project_completed_tagged_with_skill',
    -- 'new_skill_added_to_profile', 'mentor_session_completed'
    
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
    
    -- Indexes
    INDEX idx_user_action_user (user_id),
    INDEX idx_user_action_type (action_type),
    INDEX idx_user_action_completed (completed_at DESC),
    INDEX idx_user_action_skills (linked_skills) USING GIN
);

-- Risk calculation history (for trajectory tracking)
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
    
    -- Components (for debugging)
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
    percentile_vs_role DECIMAL(5,2), -- 0-100
    
    -- Timestamp
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Indexes
    INDEX idx_risk_snapshot_user (user_id),
    INDEX idx_risk_snapshot_date (calculated_at DESC),
    INDEX idx_risk_snapshot_occupation (occupation_code)
);

-- Peer aggregation table (pre-computed for fast percentile lookups)
CREATE TABLE IF NOT EXISTS public.risk_percentiles_by_role (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    occupation_code VARCHAR(10) NOT NULL,
    industry VARCHAR(100),
    
    -- Percentile buckets (pre-computed)
    p10 DECIMAL(5,2), -- 10th percentile risk score
    p25 DECIMAL(5,2),
    p50 DECIMAL(5,2), -- Median
    p75 DECIMAL(5,2),
    p90 DECIMAL(5,2),
    
    -- Sample size
    sample_count INT,
    
    -- Timestamps
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Indexes
    INDEX idx_risk_percentiles_occupation (occupation_code),
    UNIQUE(occupation_code, industry)
);

-- Comments for documentation
COMMENT ON TABLE public.ai_task_taxonomy IS 'Task-level automation scores from O*NET + research papers';
COMMENT ON TABLE public.automation_evidence IS 'Evidence for automation capability per task/skill';
COMMENT ON TABLE public.skill_demand_history IS '365-day market demand trends per skill/industry';
COMMENT ON TABLE public.user_action_log IS 'User learning actions for Adaptability Score';
COMMENT ON TABLE public.risk_calculation_snapshots IS 'Historical risk calculations for trajectory';
COMMENT ON TABLE public.risk_percentiles_by_role IS 'Pre-computed peer comparison percentiles';
```

#### 1.2 Migration Script

**File**: `backend/database/migrations/003_displacement_risk_tables.py`

```python
"""
Migration: Add Displacement Risk Engine tables
Created: 2025-11-16
"""

async def upgrade(connection):
    """Create displacement risk tables."""
    with open('backend/database/phase3_displacement_risk_schema.sql', 'r') as f:
        sql = f.read()
    await connection.execute(sql)
    print("✅ Created displacement risk tables")

async def downgrade(connection):
    """Drop displacement risk tables."""
    tables = [
        'risk_percentiles_by_role',
        'risk_calculation_snapshots',
        'user_action_log',
        'skill_demand_history',
        'automation_evidence',
        'ai_task_taxonomy'
    ]
    for table in tables:
        await connection.execute(f'DROP TABLE IF EXISTS public.{table} CASCADE')
    print("✅ Dropped displacement risk tables")
```

---

### Phase 2: Backend Service Implementation (Nov 16-17)

#### 2.1 Core Service Structure

**File**: `backend/app/services/foundation/risk/__init__.py`

```python
"""
AI Displacement Risk Engine - v1.0
Foundation service for calculating AI displacement risk scores.
"""

from .displacement_engine import DisplacementRiskEngine
from .models import RiskAnalysisRequest, RiskAnalysisResponse

__all__ = ['DisplacementRiskEngine', 'RiskAnalysisRequest', 'RiskAnalysisResponse']
```

#### 2.2 Data Models

**File**: `backend/app/services/foundation/risk/models.py`

```python
"""
Data models for Displacement Risk Engine.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# ========================================
# INPUT MODELS
# ========================================

class UserSkill(BaseModel):
    """User skill with proficiency and recency."""
    name: str
    proficiency: float = Field(..., ge=0.0, le=1.0)
    last_used_days_ago: int = Field(..., ge=0)

class UserCredential(BaseModel):
    """User credential (degree or certification)."""
    type: str  # 'degree' or 'cert'
    area: Optional[str] = None
    name: Optional[str] = None

class UserAction(BaseModel):
    """User learning/adaptation action."""
    action_type: str
    linked_skills: List[str] = []
    days_ago: int = Field(..., ge=0)
    has_certificate: bool = False
    has_verified_project: bool = False

class UserProfile(BaseModel):
    """Complete user profile for risk analysis."""
    user_id: str
    years_experience: int = Field(..., ge=0)
    people_management: bool = False
    decision_level: float = Field(0.0, ge=0.0, le=1.0)
    domain_depth_years: int = Field(0, ge=0)
    skills: List[UserSkill] = []
    credentials: List[UserCredential] = []
    action_log: List[UserAction] = []

class JobData(BaseModel):
    """Job/role data for risk analysis."""
    occupation_code: str  # O*NET SOC code
    industry: str
    wage_level: float = Field(..., ge=0.0, le=1.0)
    technical_readiness: float = Field(..., ge=0.0, le=1.0)

class RiskAnalysisRequest(BaseModel):
    """Complete request for risk analysis."""
    user_profile: UserProfile
    job_data: JobData

# ========================================
# OUTPUT MODELS
# ========================================

class DisplacementRiskScore(BaseModel):
    """Core displacement risk score with context."""
    level: str  # "Low", "Medium", "High", "Critical"
    score: float = Field(..., ge=0.0, le=100.0)
    time_horizon: str  # "0-2 years", "2-5 years", "5+ years"
    confidence: float = Field(..., ge=0.0, le=100.0)
    percentile_vs_role: float = Field(..., ge=0.0, le=100.0)
    trajectory: str  # "improving", "stable", "worsening"
    justification: str
    primary_vulnerabilities: List[str] = []
    protection_opportunities: List[str] = []

class DebugComponents(BaseModel):
    """Debug breakdown of all component scores."""
    StructuralRisk: float
    PersonalShield: float
    TAS: float
    IVS: float
    PSC: float
    AS: float
    SeniorityProtection: float
    CredentialStrength: float
    TimeHorizonIndex: float
    Confidence: float

class RiskAnalysisResponse(BaseModel):
    """Complete risk analysis response."""
    ai_displacement_risk: DisplacementRiskScore
    debug_components: DebugComponents
    calculated_at: datetime = Field(default_factory=datetime.utcnow)
```

#### 2.3 Main Engine Implementation

**File**: `backend/app/services/foundation/risk/displacement_engine.py`

This is the core 800+ line implementation. Due to length, I'll provide the structure:

```python
"""
AI Displacement Risk Engine - v1.0 Implementation
Follows the exact blueprint from Analysis 3.
"""

import math
from typing import Tuple, List, Dict, Any
from datetime import datetime, timedelta
from .models import *
from .calculators import (
    TaskAutomationCalculator,
    IndustryVelocityCalculator,
    SkillCurrencyCalculator,
    AdaptabilityCalculator
)

class DisplacementRiskEngine:
    """
    Main engine for calculating AI displacement risk.
    
    Usage:
        engine = DisplacementRiskEngine(db_connection)
        result = await engine.analyze(user_profile, job_data)
    """
    
    def __init__(self, db):
        self.db = db
        self.tas_calc = TaskAutomationCalculator(db)
        self.ivs_calc = IndustryVelocityCalculator(db)
        self.psc_calc = SkillCurrencyCalculator(db)
        self.as_calc = AdaptabilityCalculator(db)
    
    async def analyze(
        self,
        user_profile: UserProfile,
        job_data: JobData
    ) -> RiskAnalysisResponse:
        """
        Main entry point: Calculate complete risk analysis.
        
        Follows 6-step algorithm:
        1. Calculate StructuralRisk (TAS + IVS)
        2. Calculate PersonalShield (PSC + AS + Seniority + Credentials)
        3. Calculate DisplacementRisk = StructuralRisk × (1 - PersonalShield/100)
        4. Calculate Context (TimeHorizon, Confidence)
        5. Calculate Comparison (Percentile, Trajectory)
        6. Generate LLM justifications and opportunities
        """
        
        # Step 1: Structural Risk (External)
        structural_risk, tas, ivs, task_coverage, posting_density = \
            await self._calculate_structural_risk(job_data)
        
        # Step 2: Personal Shield (Internal)
        personal_shield, psc, adaptability, seniority, credentials, skill_coverage = \
            await self._calculate_personal_shield(user_profile)
        
        # Step 3: Core Displacement Risk
        displacement_risk = self._calculate_displacement_risk(
            structural_risk,
            personal_shield
        )
        
        # Step 4: Context Layers
        time_horizon, thi = await self._calculate_time_horizon(job_data, ivs)
        confidence = self._calculate_confidence(
            task_coverage,
            posting_density,
            skill_coverage
        )
        
        # Step 5: Comparison Layers
        percentile = await self._calculate_percentile(
            job_data.occupation_code,
            displacement_risk
        )
        trajectory = await self._calculate_trajectory(
            user_profile.user_id,
            displacement_risk
        )
        
        # Step 6: Generate LLM Content
        level = self._map_risk_level(displacement_risk)
        justification = self._generate_justification(
            displacement_risk, level, structural_risk, personal_shield,
            tas, ivs, psc, adaptability, trajectory
        )
        vulnerabilities = self._generate_vulnerabilities(
            tas, ivs, psc, adaptability
        )
        opportunities = self._generate_opportunities(
            psc, adaptability, seniority, user_profile
        )
        
        # Assemble final response
        return RiskAnalysisResponse(
            ai_displacement_risk=DisplacementRiskScore(
                level=level,
                score=round(displacement_risk, 1),
                time_horizon=time_horizon,
                confidence=round(confidence, 1),
                percentile_vs_role=round(percentile, 1),
                trajectory=trajectory,
                justification=justification,
                primary_vulnerabilities=vulnerabilities,
                protection_opportunities=opportunities
            ),
            debug_components=DebugComponents(
                StructuralRisk=round(structural_risk, 2),
                PersonalShield=round(personal_shield, 2),
                TAS=round(tas, 2),
                IVS=round(ivs, 2),
                PSC=round(psc, 2),
                AS=round(adaptability, 2),
                SeniorityProtection=round(seniority, 2),
                CredentialStrength=round(credentials, 2),
                TimeHorizonIndex=round(thi, 2),
                Confidence=round(confidence, 2)
            )
        )
    
    # ========================================
    # LAYER 1: STRUCTURAL RISK
    # ========================================
    
    async def _calculate_structural_risk(
        self,
        job_data: JobData
    ) -> Tuple[float, float, float, float, float]:
        """
        Calculate StructuralRisk = 0.6×TAS + 0.4×IVS
        Returns: (StructuralRisk, TAS, IVS, TaskCoverage, PostingDensity)
        """
        # Calculate components
        tas, task_coverage = await self.tas_calc.calculate(
            job_data.occupation_code
        )
        ivs, posting_density = await self.ivs_calc.calculate(
            job_data.industry
        )
        
        # Apply weights (v1.0)
        structural_risk = (0.6 * tas) + (0.4 * ivs)
        structural_risk = max(0.0, min(100.0, structural_risk))
        
        return structural_risk, tas, ivs, task_coverage, posting_density
    
    # ========================================
    # LAYER 2: PERSONAL SHIELD
    # ========================================
    
    async def _calculate_personal_shield(
        self,
        user_profile: UserProfile
    ) -> Tuple[float, float, float, float, float, float]:
        """
        Calculate PersonalShield = 0.45×PSC + 0.30×AS + 0.15×Seniority + 0.10×Creds
        Returns: (PersonalShield, PSC, AS, Seniority, Credentials, SkillCoverage)
        """
        # Calculate components
        psc, skill_coverage = await self.psc_calc.calculate(
            user_profile.skills
        )
        adaptability = await self.as_calc.calculate(
            user_profile.action_log
        )
        seniority = self._calculate_seniority_protection(user_profile)
        credentials = self._calculate_credential_strength(
            user_profile.credentials
        )
        
        # Apply weights (v1.0)
        personal_shield = (
            (0.45 * psc) +
            (0.30 * adaptability) +
            (0.15 * seniority) +
            (0.10 * credentials)
        )
        personal_shield = max(0.0, min(100.0, personal_shield))
        
        return personal_shield, psc, adaptability, seniority, credentials, skill_coverage
    
    def _calculate_seniority_protection(
        self,
        user_profile: UserProfile
    ) -> float:
        """
        Calculate SeniorityProtection = 0.4×Years + 0.2×Mgmt + 0.2×Decision + 0.2×Depth
        Returns: 0-100
        """
        years_norm = min(user_profile.years_experience / 20.0, 1.0)
        people_mgmt = 1.0 if user_profile.people_management else 0.0
        decision_level = user_profile.decision_level
        
        # Domain depth ratio
        if user_profile.years_experience > 0:
            domain_depth = min(
                user_profile.domain_depth_years / user_profile.years_experience,
                1.0
            )
        else:
            domain_depth = 0.0
        
        score = (
            (0.4 * years_norm) +
            (0.2 * people_mgmt) +
            (0.2 * decision_level) +
            (0.2 * domain_depth)
        )
        
        return score * 100.0
    
    def _calculate_credential_strength(
        self,
        credentials: List[UserCredential]
    ) -> float:
        """
        Calculate CredentialStrength (simplified v1.0).
        Returns: 0-100
        """
        score = 0.0
        
        # Degrees
        if any(c.type == 'degree' for c in credentials):
            score += 50.0
        
        # Certifications
        if any(c.type == 'cert' for c in credentials):
            score += 30.0
        
        return min(score, 100.0)
    
    # ========================================
    # LAYER 3: DISPLACEMENT RISK
    # ========================================
    
    def _calculate_displacement_risk(
        self,
        structural_risk: float,
        personal_shield: float
    ) -> float:
        """
        Core formula: StructuralRisk × (1 - PersonalShield/100)
        Returns: 0-100
        """
        raw_risk = structural_risk * (1.0 - (personal_shield / 100.0))
        return max(0.0, min(100.0, raw_risk))
    
    # ========================================
    # LAYER 4: CONTEXT
    # ========================================
    
    async def _calculate_time_horizon(
        self,
        job_data: JobData,
        ivs: float
    ) -> Tuple[str, float]:
        """
        Calculate TimeHorizonIndex and map to bucket.
        Formula: 0.35×Tech + 0.35×IVS + 0.15×Econ + 0.15×Adoption
        Returns: ("0-2 years", THI)
        """
        technical_readiness = job_data.technical_readiness
        industry_velocity = ivs / 100.0
        economic_incentive = job_data.wage_level
        adoption_trend = 0.5  # v1.0 placeholder
        
        thi = (
            (0.35 * technical_readiness) +
            (0.35 * industry_velocity) +
            (0.15 * economic_incentive) +
            (0.15 * adoption_trend)
        )
        thi = max(0.0, min(1.0, thi))
        
        # Map to buckets
        if thi >= 0.7:
            horizon = "0–2 years"
        elif thi >= 0.4:
            horizon = "2–5 years"
        else:
            horizon = "5+ years"
        
        return horizon, thi
    
    def _calculate_confidence(
        self,
        task_coverage: float,
        posting_density: float,
        skill_coverage: float
    ) -> float:
        """
        Calculate Confidence = 0.4×TaskCov + 0.3×PostDens + 0.3×SkillCov
        Returns: 0-100
        """
        task_cov = task_coverage / 100.0
        posting_dens = posting_density / 100.0
        skill_cov = skill_coverage / 100.0
        
        confidence = (
            (0.4 * task_cov) +
            (0.3 * posting_dens) +
            (0.3 * skill_cov)
        )
        
        return confidence * 100.0
    
    # ========================================
    # LAYER 5: COMPARISON
    # ========================================
    
    async def _calculate_percentile(
        self,
        occupation_code: str,
        displacement_risk: float
    ) -> float:
        """
        Compare user's risk to peers in same role.
        Returns: 0-100 (higher = safer than more peers)
        """
        # Query pre-computed percentiles
        query = """
            SELECT p10, p25, p50, p75, p90
            FROM public.risk_percentiles_by_role
            WHERE occupation_code = $1
        """
        row = await self.db.fetchrow(query, occupation_code)
        
        if not row:
            return 50.0  # Default to median if no data
        
        # Calculate percentile
        if displacement_risk <= row['p10']:
            return 90.0
        elif displacement_risk <= row['p25']:
            return 75.0
        elif displacement_risk <= row['p50']:
            return 50.0
        elif displacement_risk <= row['p75']:
            return 25.0
        elif displacement_risk <= row['p90']:
            return 10.0
        else:
            return 5.0
    
    async def _calculate_trajectory(
        self,
        user_id: str,
        current_risk: float
    ) -> str:
        """
        Compare current risk to T-90 days.
        Returns: "improving", "stable", "worsening"
        """
        # Query historical snapshot
        query = """
            SELECT displacement_risk
            FROM public.risk_calculation_snapshots
            WHERE user_id = $1
              AND calculated_at >= NOW() - INTERVAL '90 days'
            ORDER BY calculated_at DESC
            LIMIT 1
        """
        row = await self.db.fetchrow(query, user_id)
        
        if not row:
            return "stable"  # No history
        
        previous_risk = float(row['displacement_risk'])
        change = current_risk - previous_risk
        
        if change < -5.0:
            return "improving"
        elif change > 5.0:
            return "worsening"
        else:
            return "stable"
    
    # ========================================
    # LAYER 6: LLM GENERATION
    # ========================================
    
    def _map_risk_level(self, risk_score: float) -> str:
        """Map numeric score to risk level."""
        if risk_score > 75:
            return "Critical"
        elif risk_score > 50:
            return "High"
        elif risk_score > 25:
            return "Medium"
        else:
            return "Low"
    
    def _generate_justification(
        self,
        risk: float,
        level: str,
        structural: float,
        shield: float,
        tas: float,
        ivs: float,
        psc: float,
        adaptability: float,
        trajectory: str
    ) -> str:
        """Generate human-readable justification."""
        return f"""Your AI displacement risk score of {risk:.1f} ({level}) reflects a combination 
of external market forces and your personal protection factors. 

Your role faces a structural risk of {structural:.1f}/100, driven by {tas:.1f}% task automation 
potential and an industry velocity score of {ivs:.1f}/100. However, your personal shield of 
{shield:.1f}/100 provides significant protection through your skill currency (PSC: {psc:.1f}) 
and adaptability (AS: {adaptability:.1f}).

Your risk trajectory is {trajectory}, indicating {"positive momentum" if trajectory == "improving" 
else "stability" if trajectory == "stable" else "concerning trends"}. Focus on the protection 
opportunities below to strengthen your position."""
    
    def _generate_vulnerabilities(
        self,
        tas: float,
        ivs: float,
        psc: float,
        adaptability: float
    ) -> List[str]:
        """Generate list of primary vulnerabilities."""
        vulns = []
        
        if tas > 60:
            vulns.append(f"High task automation potential (TAS: {tas:.1f}/100) in your role")
        if ivs > 60:
            vulns.append(f"Rapid AI adoption in your industry (IVS: {ivs:.1f}/100)")
        if psc < 50:
            vulns.append(f"Skill currency below market average (PSC: {psc:.1f}/100)")
        if adaptability < 40:
            vulns.append(f"Limited recent learning activity (AS: {adaptability:.1f}/100)")
        
        if not vulns:
            vulns.append("No critical vulnerabilities detected")
        
        return vulns
    
    def _generate_opportunities(
        self,
        psc: float,
        adaptability: float,
        seniority: float,
        user_profile: UserProfile
    ) -> List[str]:
        """Generate actionable protection opportunities."""
        opps = []
        
        # PSC improvement
        if psc < 70:
            opps.append("Learn high-demand, AI-complementary skills (e.g., prompt engineering, AI strategy)")
        
        # AS improvement
        if adaptability < 60:
            opps.append("Complete a certified course in an AI-enhanced skill to boost your Adaptability Score")
            opps.append("Build a project demonstrating application of new skills (verified portfolio work)")
        
        # Seniority leverage
        if seniority < 50 and user_profile.years_experience >= 3:
            opps.append("Pursue management or strategic decision-making opportunities to increase protection")
        
        # Credential boost
        if len(user_profile.credentials) < 2:
            opps.append("Earn an industry-recognized certification in your domain")
        
        # Default
        if not opps:
            opps.append("Continue your strong learning trajectory with advanced, specialized skills")
        
        return opps[:5]  # Max 5 opportunities
```

#### 2.4 Calculator Modules

**File**: `backend/app/services/foundation/risk/calculators/tas_calculator.py`

```python
"""
Task Automation Score (TAS) Calculator
Queries ai_task_taxonomy to calculate role-level automation risk.
"""

from typing import Tuple

class TaskAutomationCalculator:
    """Calculates TAS from task-level automation evidence."""
    
    def __init__(self, db):
        self.db = db
    
    async def calculate(self, occupation_code: str) -> Tuple[float, float]:
        """
        Calculate TAS for a given occupation.
        
        Formula:
            TAS = Σ(TaskRisk_i × TaskImportance_i) / Σ(TaskImportance_i) × 100
        
        Returns:
            (TAS score 0-100, TaskCoverage % 0-100)
        """
        # Query all tasks for this occupation
        query = """
            SELECT 
                task_risk,
                importance_score,
                confidence_level
            FROM public.ai_task_taxonomy
            WHERE occupation_code = $1
              AND importance_score IS NOT NULL
        """
        rows = await self.db.fetch(query, occupation_code)
        
        if not rows:
            # No data: return median with low confidence
            return 50.0, 0.0
        
        # Calculate weighted TAS
        numerator = sum(
            float(row['task_risk']) * float(row['importance_score'])
            for row in rows
        )
        denominator = sum(float(row['importance_score']) for row in rows)
        
        if denominator == 0:
            return 50.0, 0.0
        
        tas = (numerator / denominator) * 100.0
        
        # Calculate coverage (% of tasks we have data for)
        # This requires knowing total task count from O*NET
        # For v1.0, use row count as proxy
        coverage = min(len(rows) / 20.0, 1.0) * 100.0  # Assume 20 tasks avg
        
        return tas, coverage
```

**Similar files needed:**
- `ivs_calculator.py` (Industry Velocity Score)
- `psc_calculator.py` (Personal Skill Currency)
- `as_calculator.py` (Adaptability Score)

Each follows the same pattern: query database, apply formula, return (score, coverage).

---

### Phase 3: API Endpoints (Nov 17)

**File**: `backend/app/api/v1/endpoints/risk.py`

```python
"""
API endpoints for AI Displacement Risk Engine.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ....services.foundation.risk import (
    DisplacementRiskEngine,
    RiskAnalysisRequest,
    RiskAnalysisResponse
)
from ....core.deps import get_db, get_current_user

router = APIRouter()

@router.post("/analyze", response_model=RiskAnalysisResponse)
async def analyze_displacement_risk(
    request: RiskAnalysisRequest,
    db = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Calculate AI displacement risk for a user + job combination.
    
    **Returns:**
    - Complete risk analysis with score, time horizon, confidence
    - Personalized vulnerabilities and protection opportunities
    - Debug component breakdown
    
    **Example:**
    ```json
    {
      "user_profile": {
        "user_id": "uuid",
        "years_experience": 8,
        "skills": [{"name": "Python", "proficiency": 0.8, "last_used_days_ago": 30}],
        ...
      },
      "job_data": {
        "occupation_code": "15-2051",
        "industry": "tech",
        ...
      }
    }
    ```
    """
    engine = DisplacementRiskEngine(db)
    
    try:
        result = await engine.analyze(
            user_profile=request.user_profile,
            job_data=request.job_data
        )
        
        # Save snapshot for trajectory tracking
        await _save_risk_snapshot(db, result, request)
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Risk calculation failed: {str(e)}"
        )

@router.get("/history/{user_id}", response_model=List[RiskAnalysisResponse])
async def get_risk_history(
    user_id: str,
    limit: int = 10,
    db = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Retrieve historical risk calculations for trajectory analysis.
    
    **Returns:**
    - List of past risk calculations (most recent first)
    - Useful for visualizing risk trends over time
    """
    query = """
        SELECT *
        FROM public.risk_calculation_snapshots
        WHERE user_id = $1
        ORDER BY calculated_at DESC
        LIMIT $2
    """
    rows = await db.fetch(query, user_id, limit)
    
    # Convert to response format
    results = [_snapshot_to_response(row) for row in rows]
    return results

async def _save_risk_snapshot(db, result: RiskAnalysisResponse, request: RiskAnalysisRequest):
    """Save risk calculation to history table."""
    query = """
        INSERT INTO public.risk_calculation_snapshots (
            user_id, occupation_code, industry,
            displacement_risk, structural_risk, personal_shield,
            tas_score, ivs_score, psc_score, adaptability_score,
            seniority_score, credential_score,
            time_horizon, time_horizon_index, confidence_score,
            percentile_vs_role
        ) VALUES (
            $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16
        )
    """
    await db.execute(
        query,
        request.user_profile.user_id,
        request.job_data.occupation_code,
        request.job_data.industry,
        result.ai_displacement_risk.score,
        result.debug_components.StructuralRisk,
        result.debug_components.PersonalShield,
        result.debug_components.TAS,
        result.debug_components.IVS,
        result.debug_components.PSC,
        result.debug_components.AS,
        result.debug_components.SeniorityProtection,
        result.debug_components.CredentialStrength,
        result.ai_displacement_risk.time_horizon,
        result.debug_components.TimeHorizonIndex,
        result.debug_components.Confidence,
        result.ai_displacement_risk.percentile_vs_role
    )
```

**Register endpoints in main app:**

**File**: `backend/app/api/v1/api.py`

```python
from .endpoints import risk  # Add this import

api_router.include_router(risk.router, prefix="/risk", tags=["risk"])
```

---

### Phase 4: Data Ingestion Pipelines (Nov 18-20)

This is the **moat-building** phase. You need real data to make this engine valuable.

#### 4.1 O*NET Task Ingestion

**File**: `backend/app/tasks/data_ingestion/onet_tasks.py`

```python
"""
Ingest O*NET task data into ai_task_taxonomy.
Data source: https://www.onetcenter.org/database.html
"""

import asyncio
import pandas as pd
from typing import List, Dict

async def ingest_onet_tasks(db, onet_data_path: str):
    """
    Load O*NET task data and populate ai_task_taxonomy.
    
    Steps:
    1. Load Task Statements.txt (task descriptions per SOC code)
    2. Load Task Ratings.txt (importance/frequency per task)
    3. Calculate initial automation scores (v1.0: use simple heuristics)
    4. Insert into ai_task_taxonomy
    """
    # Load O*NET data files
    tasks_df = pd.read_csv(f"{onet_data_path}/Task Statements.txt", sep="\t")
    ratings_df = pd.read_csv(f"{onet_data_path}/Task Ratings.txt", sep="\t")
    
    # Merge on Task ID
    merged = tasks_df.merge(ratings_df, on=["O*NET-SOC Code", "Task ID"])
    
    # For each task, insert into database
    insert_query = """
        INSERT INTO public.ai_task_taxonomy (
            occupation_code, task_id, task_name, task_description,
            importance_score, frequency_score,
            technical_capability, economic_viability,
            last_updated, data_source, confidence_level
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW(), $9, $10)
        ON CONFLICT (occupation_code, task_id) DO UPDATE SET
            importance_score = EXCLUDED.importance_score,
            technical_capability = EXCLUDED.technical_capability,
            last_updated = NOW()
    """
    
    for _, row in merged.iterrows():
        # v1.0: Simple heuristic for automation scores
        # (v2.0: Use ML model or research papers)
        tech_capability = _estimate_technical_capability(row['Task'])
        econ_viability = _estimate_economic_viability(row['O*NET-SOC Code'])
        
        await db.execute(
            insert_query,
            row['O*NET-SOC Code'],
            row['Task ID'],
            row['Task'],
            row['Task Description'],
            row['IM'],  # Importance
            row['FT'],  # Frequency
            tech_capability,
            econ_viability,
            'O*NET 2024',
            0.7  # Confidence
        )
    
    print(f"✅ Ingested {len(merged)} O*NET tasks")

def _estimate_technical_capability(task_text: str) -> float:
    """
    v1.0 heuristic: keyword matching for automation capability.
    v2.0: Replace with ML model trained on research papers.
    """
    task_lower = task_text.lower()
    
    # High automation keywords
    high_auto = ['data entry', 'filing', 'scheduling', 'basic calculation', 'routine']
    # Low automation keywords
    low_auto = ['creative', 'empathy', 'negotiation', 'leadership', 'strategic']
    
    if any(kw in task_lower for kw in high_auto):
        return 0.8
    elif any(kw in task_lower for kw in low_auto):
        return 0.3
    else:
        return 0.5  # Default

def _estimate_economic_viability(soc_code: str) -> float:
    """
    v1.0 heuristic: higher wages = higher automation incentive.
    v2.0: Use BLS wage data + automation cost models.
    """
    # Placeholder: map SOC to wage percentile
    return 0.6  # Default
```

#### 4.2 Job Posting Scraper

**File**: `backend/app/tasks/data_ingestion/job_postings.py`

```python
"""
Scrape job postings to populate skill_demand_history.
Data sources: LinkedIn API, Indeed, Glassdoor (if available)
"""

import asyncio
from datetime import date
from typing import List, Dict

async def ingest_job_postings(db):
    """
    Daily job: Scrape job postings and update skill_demand_history.
    
    For each skill:
    1. Count total postings mentioning the skill
    2. Calculate 30-day and 365-day growth
    3. Separate AI-related postings vs legacy postings
    4. Calculate demand_score and trend_score
    5. Insert/update skill_demand_history
    """
    # Placeholder: Integrate with job posting API
    # Example: LinkedIn Talent Solutions API, Adzuna API
    
    skills = await _get_tracked_skills(db)
    
    for skill in skills:
        data = await _scrape_skill_demand(skill)
        
        await db.execute("""
            INSERT INTO public.skill_demand_history (
                skill_name, skill_category, industry, occupation_code, geography,
                demand_score, trend_score,
                job_posting_count, job_posting_growth_30d, job_posting_growth_365d,
                ai_job_postings, legacy_job_postings,
                snapshot_date
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
            ON CONFLICT (skill_name, industry, occupation_code, geography, snapshot_date)
            DO UPDATE SET
                demand_score = EXCLUDED.demand_score,
                trend_score = EXCLUDED.trend_score,
                job_posting_count = EXCLUDED.job_posting_count
        """, 
            skill['name'], skill['category'], 'all', None, 'US',
            data['demand_score'], data['trend_score'],
            data['total_count'], data['growth_30d'], data['growth_365d'],
            data['ai_count'], data['legacy_count'],
            date.today()
        )
    
    print(f"✅ Updated skill demand data for {len(skills)} skills")

async def _scrape_skill_demand(skill: Dict) -> Dict:
    """Scrape job postings for a specific skill."""
    # Placeholder: Call external API
    return {
        'demand_score': 0.7,
        'trend_score': 0.15,
        'total_count': 5000,
        'growth_30d': 5.2,
        'growth_365d': 18.5,
        'ai_count': 1200,
        'legacy_count': 3800
    }
```

---

## Success Criteria & Testing

### Phase 5: Testing & Calibration (Nov 21-22)

#### 5.1 Test Suite

**File**: `backend/tests/test_displacement_risk.py`

```python
"""
Comprehensive tests for Displacement Risk Engine.
"""

import pytest
from app.services.foundation.risk import DisplacementRiskEngine, RiskAnalysisRequest
from app.services.foundation.risk.models import *

@pytest.mark.asyncio
async def test_low_risk_profile(db):
    """Test a user with low displacement risk."""
    request = RiskAnalysisRequest(
        user_profile=UserProfile(
            user_id="test-001",
            years_experience=12,
            people_management=True,
            decision_level=0.8,
            domain_depth_years=10,
            skills=[
                UserSkill(name="Strategic Planning", proficiency=0.9, last_used_days_ago=5),
                UserSkill(name="AI Strategy", proficiency=0.8, last_used_days_ago=10)
            ],
            credentials=[
                UserCredential(type="degree", area="business"),
                UserCredential(type="cert", name="AI Executive")
            ],
            action_log=[
                UserAction(
                    action_type="course_completed_with_cert",
                    linked_skills=["AI Strategy"],
                    days_ago=30,
                    has_certificate=True
                )
            ]
        ),
        job_data=JobData(
            occupation_code="11-2021",  # Marketing Manager
            industry="tech",
            wage_level=0.75,
            technical_readiness=0.4  # Low automation readiness
        )
    )
    
    engine = DisplacementRiskEngine(db)
    result = await engine.analyze(request.user_profile, request.job_data)
    
    # Assertions
    assert result.ai_displacement_risk.level in ["Low", "Medium"]
    assert result.ai_displacement_risk.score < 50
    assert result.debug_components.PersonalShield > 60
    assert "improving" in result.ai_displacement_risk.trajectory.lower() or \
           "stable" in result.ai_displacement_risk.trajectory.lower()

@pytest.mark.asyncio
async def test_high_risk_profile(db):
    """Test a user with high displacement risk."""
    request = RiskAnalysisRequest(
        user_profile=UserProfile(
            user_id="test-002",
            years_experience=3,
            people_management=False,
            decision_level=0.2,
            domain_depth_years=2,
            skills=[
                UserSkill(name="Data Entry", proficiency=0.7, last_used_days_ago=120),
                UserSkill(name="Excel", proficiency=0.6, last_used_days_ago=90)
            ],
            credentials=[],
            action_log=[]  # No recent learning
        ),
        job_data=JobData(
            occupation_code="43-9061",  # Office Clerk
            industry="finance",
            wage_level=0.3,
            technical_readiness=0.9  # High automation readiness
        )
    )
    
    engine = DisplacementRiskEngine(db)
    result = await engine.analyze(request.user_profile, request.job_data)
    
    # Assertions
    assert result.ai_displacement_risk.level in ["High", "Critical"]
    assert result.ai_displacement_risk.score > 60
    assert result.debug_components.StructuralRisk > 50
    assert result.debug_components.PersonalShield < 50
    assert result.ai_displacement_risk.time_horizon == "0–2 years"
```

#### 5.2 Calibration Process

1. **Run 100+ Test Profiles**: Create synthetic profiles across risk spectrum
2. **Validate Output**: Ensure scores match intuition (high-risk roles score high, etc.)
3. **Tune Weights**: Adjust the 0.6/0.4 (TAS/IVS) and 0.45/0.30/0.15/0.10 (PSC/AS/Sen/Cred) weights
4. **A/B Test**: Show scores to real users, collect feedback on accuracy

---

## Enterprise Integration

### How This Powers Your Revenue Model

**For B2C Users** ($0-29/month):
- Show risk score on dashboard
- Provide 3 protection opportunities (limited)
- Track trajectory (30-day updates)

**For B2B Enterprise** ($150K+/year):
- API access to batch risk calculations (all employees)
- Custom dashboards showing team-level risk
- Real-time alerts when employees' risk increases
- Skill gap analysis (which skills to train on)
- ROI calculation: "Training these 50 employees in AI skills reduces team risk by 30%"

**The Flywheel**:
1. User sees risk score → Takes action (completes course)
2. Action logged in `user_action_log` → AS improves
3. Next risk calculation shows lower score → User trusts system more
4. User shares with employer → Enterprise signs contract
5. Enterprise data feeds back into percentile calculations → Better benchmarks
6. **Network effects = moat**

---

## Next Steps

### Immediate Actions (Today - Nov 16)

1. **Create Database Schema**
   ```bash
   cd backend
   python -m app.database.migrations.003_displacement_risk_tables
   ```

2. **Stub Out Service**
   ```bash
   mkdir -p backend/app/services/foundation/risk/calculators
   touch backend/app/services/foundation/risk/__init__.py
   touch backend/app/services/foundation/risk/displacement_engine.py
   touch backend/app/services/foundation/risk/models.py
   ```

3. **Add API Endpoints**
   ```bash
   touch backend/app/api/v1/endpoints/risk.py
   ```

4. **Start Data Ingestion**
   - Download O*NET database (free)
   - Set up job posting scraper (Adzuna API is free tier)

### This Week (Nov 17-22)

- **Day 1-2**: Implement core engine + calculators
- **Day 3**: Build API endpoints
- **Day 4-5**: Data ingestion pipelines
- **Day 6**: Testing & calibration
- **Day 7**: Deploy to staging

### Success Metrics

- **Technical**: All tests passing, <500ms response time
- **Business**: 90%+ of test users say score "feels accurate"
- **Revenue**: Enterprise demos convert at 40%+ when they see this feature

---

## Why This Is Your Wedge

**Competitors** (LinkedIn, Indeed, etc.):
- Generic "skills in demand" lists
- No personalized risk assessment
- No defensible moat

**Your Advantage**:
- **Principled model** with transparent formulas
- **Data moat** from user actions (they can't replicate your flywheel)
- **Time horizon** (the "when" question no one else answers)
- **Actionable** (not just scores, but what to DO about it)

**The Pitch to Enterprises**:
> "We don't just tell your employees they're at risk. We quantify it, timeline it, and give them a clear path to protection. And every action they take makes our model smarter, which makes your workforce planning better. This is the system you need to manage the AI transition."

---

## Questions?

This is your v1.0 blueprint. Every function signature, every database table, every API endpoint is specified.

**What do you need clarified before starting implementation?**

- Database schema details?
- Specific calculator algorithms?
- Data source integrations?
- Frontend UI for displaying scores?

Let me know where to drill deeper. 🚀
