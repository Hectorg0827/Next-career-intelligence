"""
AI Displacement Risk Engine v1.0

Main orchestration engine that calculates comprehensive displacement risk scores
using a 6-layer algorithm:
  Layer 1: StructuralRisk (external job risk)
  Layer 2: PersonalShield (internal protection)
  Layer 3: DisplacementRisk (core formula)
  Layer 4: TimeHorizon + Confidence
  Layer 5: Percentile + Trajectory
  Layer 6: LLM Justifications

Author: AI Career Risk Engine Team
Date: November 16, 2025
"""

import asyncpg
from typing import Tuple, List, Optional
from datetime import datetime, timedelta
import math

from .models import (
    UserProfile,
    JobData,
    RiskAnalysisResponse,
    DisplacementRiskScore,
    DebugComponents
)
from .calculators import (
    TaskAutomationCalculator,
    IndustryVelocityCalculator,
    SkillCurrencyCalculator,
    AdaptabilityCalculator
)
from .cache import get_cache


class DisplacementRiskEngine:
    """
    Main engine that orchestrates all displacement risk calculations.
    
    Uses 6-layer calculation pipeline:
    1. StructuralRisk = 0.6×TAS + 0.4×IVS
    2. PersonalShield = 0.45×PSC + 0.30×AS + 0.15×Seniority + 0.10×Credentials
    3. DisplacementRisk = StructuralRisk × (1 - PersonalShield/100)
    4. TimeHorizon + Confidence scores
    5. Percentile + Trajectory comparisons
    6. LLM-generated justifications and recommendations
    """
    
    def __init__(self, db_pool: asyncpg.Pool):
        """
        Initialize engine with database connection pool and all calculators.
        
        Args:
            db_pool: asyncpg connection pool for database queries
        """
        self.db = db_pool
        
        # Initialize all component calculators
        self.tas_calc = TaskAutomationCalculator(db_pool)
        self.ivs_calc = IndustryVelocityCalculator(db_pool)
        self.psc_calc = SkillCurrencyCalculator(db_pool)
        self.as_calc = AdaptabilityCalculator(db_pool)
        
        # Initialize cache service
        self.cache = get_cache()
    
    async def analyze(
        self,
        user_profile: UserProfile,
        job_data: JobData
    ) -> RiskAnalysisResponse:
        """
        Run complete displacement risk analysis for a user.
        
        Args:
            user_profile: Complete user profile with skills, credentials, learning actions
            job_data: Target job with occupation code and industry
        
        Returns:
            RiskAnalysisResponse with final score, debug components, and LLM justifications
        """
        # Check cache first for complete risk analysis
        cached_result = await self.cache.get_risk_analysis(
            user_id=user_profile.user_id,
            occupation_code=job_data.occupation_code,
            industry=job_data.industry
        )
        
        if cached_result:
            # Cache hit - return cached result
            return RiskAnalysisResponse(**cached_result)
        
        # Cache miss - perform full calculation
        
        # Layer 1: Calculate structural risk (external job risk)
        structural_risk, tas, ivs, task_coverage, posting_density = \
            await self._calculate_structural_risk(job_data)
        
        # Layer 2: Calculate personal shield (internal protection)
        personal_shield, psc, as_score, seniority_protection, credential_strength, skill_coverage = \
            await self._calculate_personal_shield(user_profile)
        
        # Layer 3: Calculate core displacement risk
        displacement_risk = self._calculate_displacement_risk(structural_risk, personal_shield)
        
        # Layer 4: Calculate time horizon and confidence
        time_horizon, time_horizon_index = self._calculate_time_horizon(
            job_data.technical_readiness,
            ivs,
            job_data.wage_level
        )
        confidence = self._calculate_confidence(task_coverage, posting_density, skill_coverage)
        
        # Layer 5: Calculate percentile and trajectory
        percentile = await self._calculate_percentile(job_data.occupation_code, displacement_risk)
        trajectory = await self._calculate_trajectory(user_profile.user_id, displacement_risk)
        
        # Layer 6: Generate LLM justifications and recommendations
        risk_level = self._map_risk_level(displacement_risk)
        justification = self._generate_justification(
            displacement_risk,
            risk_level,
            structural_risk,
            personal_shield,
            tas,
            ivs,
            psc,
            as_score,
            trajectory
        )
        vulnerabilities = self._generate_vulnerabilities(
            tas,
            ivs,
            psc,
            as_score,
            seniority_protection,
            len(user_profile.credentials)
        )
        opportunities = self._generate_opportunities(
            psc,
            as_score,
            seniority_protection,
            len(user_profile.credentials)
        )
        
        # Save snapshot for future trajectory analysis (optional - may fail if user doesn't exist)
        try:
            await self._save_snapshot(
                user_profile.user_id,
                job_data.occupation_code,
                displacement_risk,
                structural_risk,
                personal_shield,
                tas,
                ivs,
                psc,
                as_score,
                seniority_protection,
                credential_strength
            )
        except Exception:
            pass  # Snapshot save is optional, don't fail the analysis
        
        # Build final response
        risk_score = DisplacementRiskScore(
            level=risk_level,
            score=round(displacement_risk, 1),
            time_horizon=time_horizon,
            confidence=round(confidence, 1),
            percentile_vs_role=round(percentile, 1) if percentile is not None else None,
            trajectory=trajectory,
            justification=justification,
            primary_vulnerabilities=vulnerabilities,
            protection_opportunities=opportunities
        )
        
        debug_components = DebugComponents(
            StructuralRisk=round(structural_risk, 1),
            PersonalShield=round(personal_shield, 1),
            TAS=round(tas, 1),
            IVS=round(ivs, 1),
            PSC=round(psc, 1),
            AS=round(as_score, 1),
            SeniorityProtection=round(seniority_protection, 1),
            CredentialStrength=round(credential_strength, 1),
            TimeHorizonIndex=round(time_horizon_index, 2),
            Confidence=round(confidence, 1)
        )
        
        return RiskAnalysisResponse(
            ai_displacement_risk=risk_score,
            debug_components=debug_components,
            calculated_at=datetime.utcnow()
        )
    
    # ========================================
    # Layer 1: Structural Risk Calculation
    # ========================================
    
    async def _calculate_structural_risk(
        self,
        job_data: JobData
    ) -> Tuple[float, float, float, float, float]:
        """
        Calculate external structural risk from job characteristics.
        
        Formula: StructuralRisk = 0.6×TAS + 0.4×IVS
        
        Args:
            job_data: Job with occupation code and industry
        
        Returns:
            (structural_risk, tas, ivs, task_coverage, posting_density)
        """
        # Get TAS (Task Automation Score)
        tas, task_coverage = await self.tas_calc.calculate(job_data.occupation_code)
        
        # Get IVS (Industry Velocity Score)
        ivs, posting_density = await self.ivs_calc.calculate(job_data.industry)
        
        # Calculate weighted structural risk
        structural_risk = (0.6 * tas) + (0.4 * ivs)
        
        return structural_risk, tas, ivs, task_coverage, posting_density
    
    # ========================================
    # Layer 2: Personal Shield Calculation
    # ========================================
    
    async def _calculate_personal_shield(
        self,
        user_profile: UserProfile
    ) -> Tuple[float, float, float, float, float, float]:
        """
        Calculate internal personal shield from user characteristics.
        
        Formula: PersonalShield = 0.45×PSC + 0.30×AS + 0.15×Seniority + 0.10×Credentials
        
        Args:
            user_profile: Complete user profile
        
        Returns:
            (personal_shield, psc, as_score, seniority_protection, credential_strength, skill_coverage)
        """
        # Convert UserSkill objects to dict format for PSC calculator
        skills_as_dicts = [
            {
                "skill_name": skill.skill_name,
                "proficiency": skill.proficiency,
                "years_experience": skill.years_experience,
                "last_used_days_ago": skill.last_used_days_ago
            }
            for skill in user_profile.skills
        ]
        
        # Get PSC (Personal Skill Currency)
        psc, skill_coverage = await self.psc_calc.calculate(skills_as_dicts)
        
        # Get AS (Adaptability Score)
        as_score, _action_count = await self.as_calc.calculate(user_profile.user_id)
        
        # Calculate Seniority Protection
        seniority_protection = self._calculate_seniority_protection(user_profile)
        
        # Calculate Credential Strength
        credential_strength = self._calculate_credential_strength(user_profile.credentials)
        
        # Calculate weighted personal shield
        personal_shield = (
            0.45 * psc +
            0.30 * as_score +
            0.15 * seniority_protection +
            0.10 * credential_strength
        )
        
        return personal_shield, psc, as_score, seniority_protection, credential_strength, skill_coverage
    
    def _calculate_seniority_protection(self, user_profile: UserProfile) -> float:
        """
        Calculate seniority-based protection score.
        
        Formula: 0.4×(Years/20) + 0.2×PeopleMgmt + 0.2×DecisionLevel + 0.2×DomainDepth
        
        Args:
            user_profile: User profile with experience details
        
        Returns:
            Seniority protection score 0-100
        """
        # Years component (capped at 20 years)
        years_normalized = min(user_profile.years_experience / 20.0, 1.0)
        
        # People management component (boolean → 0 or 1)
        people_mgmt = 1.0 if user_profile.people_management else 0.0
        
        # Decision level (already 0-1 from user input)
        decision_level = user_profile.decision_level if user_profile.decision_level is not None else 0.0
        
        # Domain depth (domain years as fraction of total years)
        domain_depth = 0.0
        if user_profile.years_experience > 0 and user_profile.domain_depth_years is not None:
            domain_depth = min(user_profile.domain_depth_years / user_profile.years_experience, 1.0)
        
        # Weighted combination
        seniority_score = (
            0.4 * years_normalized +
            0.2 * people_mgmt +
            0.2 * decision_level +
            0.2 * domain_depth
        ) * 100  # Scale to 0-100
        
        return seniority_score
    
    def _calculate_credential_strength(self, credentials: List) -> float:
        """
        Calculate credential-based protection score.
        
        v1.0 Simplified: degree=50 pts, cert=30 pts, max=100
        
        Args:
            credentials: List of UserCredential objects
        
        Returns:
            Credential strength score 0-100
        """
        score = 0.0
        
        for cred in credentials:
            if cred.credential_type == 'degree':
                score += 50.0
            elif cred.credential_type == 'cert':
                score += 30.0
        
        # Cap at 100
        return min(score, 100.0)
    
    # ========================================
    # Layer 3: Core Displacement Risk Formula
    # ========================================
    
    def _calculate_displacement_risk(
        self,
        structural_risk: float,
        personal_shield: float
    ) -> float:
        """
        Calculate core displacement risk score.
        
        Formula: DisplacementRisk = StructuralRisk × (1 - PersonalShield/100)
        
        This means:
        - High structural risk + low personal shield = high displacement risk
        - High structural risk + high personal shield = mitigated displacement risk
        
        Args:
            structural_risk: External job risk (0-100)
            personal_shield: Internal protection (0-100)
        
        Returns:
            Final displacement risk score 0-100
        """
        # Personal shield is a percentage reduction
        shield_multiplier = 1.0 - (personal_shield / 100.0)
        
        # Apply shield to structural risk
        displacement_risk = structural_risk * shield_multiplier
        
        # Ensure 0-100 bounds
        return max(0.0, min(100.0, displacement_risk))
    
    # ========================================
    # Layer 4: Time Horizon & Confidence
    # ========================================
    
    def _calculate_time_horizon(
        self,
        technical_readiness: float,
        ivs: float,
        wage_level: float
    ) -> Tuple[str, float]:
        """
        Calculate time horizon for displacement.
        
        Formula: THI = 0.35×Tech + 0.35×IVS + 0.15×(1-Wage) + 0.15×(default_adoption=0.5)
        
        Mapping:
        - THI ≥ 0.70 → "0-2 years" (imminent)
        - 0.40 ≤ THI < 0.70 → "2-5 years" (medium-term)
        - THI < 0.40 → "5+ years" (long-term)
        
        Args:
            technical_readiness: AI technical capability (0-1)
            ivs: Industry Velocity Score (0-100)
            wage_level: Wage percentile (0-1, higher = more expensive = slower adoption)
        
        Returns:
            (time_horizon_string, time_horizon_index)
        """
        # Normalize IVS to 0-1
        ivs_normalized = ivs / 100.0
        
        # Economic incentive (inverse of wage - higher wages slow adoption)
        economic_incentive = 1.0 - wage_level
        
        # Adoption rate (v1.0: default to moderate 0.5)
        adoption_rate = 0.5
        
        # Calculate Time Horizon Index
        thi = (
            0.35 * technical_readiness +
            0.35 * ivs_normalized +
            0.15 * economic_incentive +
            0.15 * adoption_rate
        )
        
        # Map to time bucket
        if thi >= 0.70:
            time_horizon = "0-2 years"
        elif thi >= 0.40:
            time_horizon = "2-5 years"
        else:
            time_horizon = "5+ years"
        
        return time_horizon, thi
    
    def _calculate_confidence(
        self,
        task_coverage: float,
        posting_density: float,
        skill_coverage: float
    ) -> float:
        """
        Calculate confidence score based on data coverage.
        
        Formula: Confidence = 0.4×TaskCov + 0.3×PostDens + 0.3×SkillCov
        
        Args:
            task_coverage: Task data coverage % (0-100)
            posting_density: Job posting data density % (0-100)
            skill_coverage: Skill data coverage % (0-100)
        
        Returns:
            Confidence score 0-100
        """
        confidence = (
            0.4 * task_coverage +
            0.3 * posting_density +
            0.3 * skill_coverage
        )
        
        return max(0.0, min(100.0, confidence))
    
    # ========================================
    # Layer 5: Percentile & Trajectory
    # ========================================
    
    async def _calculate_percentile(
        self,
        occupation_code: str,
        user_risk: float
    ) -> Optional[float]:
        """
        Calculate percentile vs peers in same role.
        
        Higher percentile = safer than more peers (better position).
        
        Args:
            occupation_code: O*NET SOC code
            user_risk: User's displacement risk score
        
        Returns:
            Percentile 0-100, or None if no peer data available
        """
        async with self.db.acquire() as conn:
            # Query pre-computed percentiles for this occupation
            row = await conn.fetchrow(
                """
                SELECT p10, p25, p50, p75, p90
                FROM risk_percentiles_by_role
                WHERE occupation_code = $1
                """,
                occupation_code
            )
            
            if not row:
                return None  # No peer data available
            
            # Compare user's risk to percentile buckets
            # Lower risk = higher percentile (safer position)
            if user_risk <= row['p10']:
                return 90.0  # Safer than 90% of peers
            elif user_risk <= row['p25']:
                return 75.0
            elif user_risk <= row['p50']:
                return 50.0
            elif user_risk <= row['p75']:
                return 25.0
            elif user_risk <= row['p90']:
                return 10.0
            else:
                return 5.0  # Higher risk than 95% of peers
    
    async def _calculate_trajectory(
        self,
        user_id: str,
        current_risk: float
    ) -> str:
        """
        Calculate risk trajectory by comparing to T-90 days.
        
        Args:
            user_id: User identifier
            current_risk: Current displacement risk score
        
        Returns:
            "improving", "stable", or "worsening"
        """
        async with self.db.acquire() as conn:
            # Query most recent snapshot from 90 days ago
            ninety_days_ago = datetime.utcnow() - timedelta(days=90)
            
            row = await conn.fetchrow(
                """
                SELECT displacement_risk
                FROM risk_calculation_snapshots
                WHERE user_id = $1
                  AND calculated_at <= $2
                ORDER BY calculated_at DESC
                LIMIT 1
                """,
                user_id,
                ninety_days_ago
            )
            
            if not row:
                return "stable"  # No historical data, assume stable
            
            previous_risk = row['displacement_risk']
            delta = current_risk - previous_risk
            
            # Classify trajectory
            if delta < -5.0:
                return "improving"  # Risk decreased by >5 points
            elif delta > 5.0:
                return "worsening"  # Risk increased by >5 points
            else:
                return "stable"  # Within ±5 points
    
    # ========================================
    # Layer 6: LLM Justification Generation
    # ========================================
    
    def _map_risk_level(self, risk_score: float) -> str:
        """
        Map numeric risk score to categorical level.
        
        Args:
            risk_score: Displacement risk 0-100
        
        Returns:
            "Low", "Medium", "High", or "Critical"
        """
        if risk_score >= 75:
            return "Critical"
        elif risk_score >= 60:
            return "High"
        elif risk_score >= 40:
            return "Medium"
        else:
            return "Low"
    
    def _generate_justification(
        self,
        risk: float,
        level: str,
        structural_risk: float,
        personal_shield: float,
        tas: float,
        ivs: float,
        psc: float,
        as_score: float,
        trajectory: str
    ) -> str:
        """
        Generate human-readable explanation of risk score.
        
        Args:
            risk: Final displacement risk score
            level: Risk level string
            structural_risk: External job risk
            personal_shield: Internal protection
            tas: Task automation score
            ivs: Industry velocity score
            psc: Personal skill currency
            as_score: Adaptability score
            trajectory: Risk trajectory
        
        Returns:
            Multi-paragraph justification
        """
        # Opening statement
        justification = (
            f"Your AI displacement risk score of {risk:.1f} ({level}) reflects "
            f"the combination of external job market forces and your personal protections.\n\n"
        )
        
        # Structural risk explanation
        if structural_risk >= 60:
            justification += (
                f"**High Structural Risk ({structural_risk:.1f}/100)**: "
                f"Your role faces significant automation pressure. "
            )
            if tas >= 60:
                justification += (
                    f"Tasks in this occupation have high automation potential (TAS: {tas:.1f}/100), "
                    f"with AI systems demonstrating strong technical capability. "
                )
            if ivs >= 60:
                justification += (
                    f"The industry is experiencing rapid AI adoption (IVS: {ivs:.1f}/100), "
                    f"with accelerating displacement of traditional roles. "
                )
            justification += "\n\n"
        elif structural_risk >= 40:
            justification += (
                f"**Moderate Structural Risk ({structural_risk:.1f}/100)**: "
                f"Your role has mixed automation exposure. Some tasks face AI pressure, "
                f"while others remain difficult to automate.\n\n"
            )
        else:
            justification += (
                f"**Low Structural Risk ({structural_risk:.1f}/100)**: "
                f"Your role currently has limited automation pressure. "
                f"Tasks requiring human judgment, creativity, or interpersonal skills "
                f"remain difficult for AI systems to replicate.\n\n"
            )
        
        # Personal shield explanation
        if personal_shield >= 60:
            justification += (
                f"**Strong Personal Shield ({personal_shield:.1f}/100)**: "
                f"You have built significant protections. "
            )
            if psc >= 70:
                justification += (
                    f"Your skills are highly valued in the market (PSC: {psc:.1f}/100), "
                    f"with strong demand and complementarity to AI. "
                )
            if as_score >= 60:
                justification += (
                    f"Your learning velocity is strong (AS: {as_score:.1f}/100), "
                    f"demonstrating ability to adapt to new technologies. "
                )
        elif personal_shield >= 40:
            justification += (
                f"**Moderate Personal Shield ({personal_shield:.1f}/100)**: "
                f"You have some protections, but there's room to strengthen your position.\n\n"
            )
        else:
            justification += (
                f"**Weak Personal Shield ({personal_shield:.1f}/100)**: "
                f"Your current skill profile and learning activity provide limited protection "
                f"against automation pressure. Immediate action recommended.\n\n"
            )
        
        # Trajectory
        if trajectory == "improving":
            justification += "✅ **Positive Trend**: Your risk has decreased over the past 90 days."
        elif trajectory == "worsening":
            justification += "⚠️ **Negative Trend**: Your risk has increased over the past 90 days."
        else:
            justification += "➡️ **Stable Trend**: Your risk has remained relatively constant."
        
        return justification
    
    def _generate_vulnerabilities(
        self,
        tas: float,
        ivs: float,
        psc: float,
        as_score: float,
        seniority_protection: float,
        credential_count: int
    ) -> List[str]:
        """
        Generate list of primary risk factors.
        
        Args:
            tas: Task automation score
            ivs: Industry velocity score
            psc: Personal skill currency
            as_score: Adaptability score
            seniority_protection: Seniority protection score
            credential_count: Number of credentials
        
        Returns:
            List of 3-5 vulnerability strings
        """
        vulnerabilities = []
        
        # Task automation vulnerability
        if tas >= 70:
            vulnerabilities.append(
                f"Critical task automation exposure ({tas:.0f}/100) - "
                f"core job functions highly susceptible to AI automation"
            )
        elif tas >= 60:
            vulnerabilities.append(
                f"High task automation potential ({tas:.0f}/100) - "
                f"many tasks can be performed by current AI systems"
            )
        
        # Industry velocity vulnerability
        if ivs >= 70:
            vulnerabilities.append(
                f"Rapid industry AI adoption ({ivs:.0f}/100) - "
                f"employers aggressively deploying automation solutions"
            )
        elif ivs >= 60:
            vulnerabilities.append(
                f"Fast-moving industry dynamics ({ivs:.0f}/100) - "
                f"AI adoption accelerating in your sector"
            )
        
        # Skill currency vulnerability
        if psc < 40:
            vulnerabilities.append(
                f"Low skill market value ({psc:.0f}/100) - "
                f"current skills declining in demand or highly substitutable by AI"
            )
        elif psc < 50:
            vulnerabilities.append(
                f"Below-average skill currency ({psc:.0f}/100) - "
                f"skills need refreshing to maintain market competitiveness"
            )
        
        # Adaptability vulnerability
        if as_score < 30:
            vulnerabilities.append(
                f"Minimal learning activity ({as_score:.0f}/100) - "
                f"limited evidence of adaptation to new technologies"
            )
        elif as_score < 40:
            vulnerabilities.append(
                f"Low adaptability score ({as_score:.0f}/100) - "
                f"insufficient upskilling to keep pace with AI disruption"
            )
        
        # Seniority/credential vulnerability
        if seniority_protection < 30 and credential_count < 2:
            vulnerabilities.append(
                "Limited career anchors - neither seniority nor credentials provide strong protection"
            )
        
        # Return top 5 most critical
        return vulnerabilities[:5]
    
    def _generate_opportunities(
        self,
        psc: float,
        as_score: float,
        seniority_protection: float,
        credential_count: int
    ) -> List[str]:
        """
        Generate actionable protection opportunities.
        
        Args:
            psc: Personal skill currency
            as_score: Adaptability score
            seniority_protection: Seniority protection score
            credential_count: Number of credentials
        
        Returns:
            List of up to 5 opportunity strings
        """
        opportunities = []
        
        # Skill improvement opportunities
        if psc < 70:
            opportunities.append(
                "Learn AI-complementary skills: Focus on areas where AI augments rather than "
                "replaces human work (e.g., prompt engineering, AI system oversight, "
                "ethical AI governance)"
            )
        
        # Learning velocity opportunities
        if as_score < 60:
            opportunities.append(
                "Boost learning velocity: Complete certified courses in emerging technologies. "
                "Target: 1 course/month with verified certificate to demonstrate adaptability."
            )
            opportunities.append(
                "Build verified projects: Create portfolio demonstrating AI-era skills. "
                "Public GitHub projects with AI integration show practical capability."
            )
        
        # Seniority opportunities
        if seniority_protection < 50:
            opportunities.append(
                "Pursue management/leadership roles: People management and strategic "
                "decision-making provide stronger protection against automation"
            )
        
        # Credential opportunities
        if credential_count < 2:
            opportunities.append(
                "Earn industry-recognized certifications: Credentials signal expertise and "
                "commitment to professional development (e.g., AWS, Google Cloud, "
                "Microsoft AI certifications)"
            )
        
        # Return top 5
        return opportunities[:5]
    
    # ========================================
    # Snapshot Persistence
    # ========================================
    
    async def _save_snapshot(
        self,
        user_id: str,
        occupation_code: str,
        displacement_risk: float,
        structural_risk: float,
        personal_shield: float,
        tas: float,
        ivs: float,
        psc: float,
        as_score: float,
        seniority_protection: float,
        credential_strength: float
    ):
        """
        Save calculation snapshot for future trajectory analysis.
        
        Args:
            user_id: User identifier
            occupation_code: O*NET SOC code
            displacement_risk: Final risk score
            structural_risk: Layer 1 score
            personal_shield: Layer 2 score
            tas: Task automation score
            ivs: Industry velocity score
            psc: Personal skill currency
            as_score: Adaptability score
            seniority_protection: Seniority protection score
            credential_strength: Credential strength score
        """
        async with self.db.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO risk_calculation_snapshots (
                    user_id,
                    occupation_code,
                    displacement_risk,
                    structural_risk,
                    personal_shield,
                    tas_score,
                    ivs_score,
                    psc_score,
                    adaptability_score,
                    seniority_score,
                    credential_score,
                    calculated_at
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, NOW())
                """,
                user_id,
                occupation_code,
                displacement_risk,
                structural_risk,
                personal_shield,
                tas,
                ivs,
                psc,
                as_score,
                seniority_protection,
                credential_strength
            )
