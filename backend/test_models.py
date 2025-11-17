"""
Test script for AI Displacement Risk Engine models
"""

import sys
sys.path.append('/Users/hectorgarcia/Desktop/Next-career-intelligence/backend')

from app.services.foundation.risk.models import (
    UserProfile, UserSkill, UserCredential, UserAction,
    JobData, RiskAnalysisRequest,
    DisplacementRiskScore, DebugComponents, RiskAnalysisResponse
)
from datetime import datetime


def test_models():
    """Test all data models can be instantiated correctly."""
    
    print("🧪 Testing AI Displacement Risk Engine Models\n")
    
    # Test UserSkill
    print("✓ Testing UserSkill...")
    skill = UserSkill(
        skill_name="Python",
        proficiency=0.85,
        years_experience=5.0,
        last_used_days_ago=10
    )
    print(f"  Created: {skill.skill_name} (proficiency: {skill.proficiency})")
    
    # Test UserCredential
    print("\n✓ Testing UserCredential...")
    credential = UserCredential(
        credential_type="degree",
        name="Bachelor of Science in Computer Science",
        issuer="MIT",
        year_obtained=2018
    )
    print(f"  Created: {credential.name}")
    
    # Test UserAction
    print("\n✓ Testing UserAction...")
    action = UserAction(
        action_type="course",
        linked_skills=["Python", "Machine Learning"],
        days_ago=30,
        has_certificate=True
    )
    print(f"  Created: {action.action_type} ({len(action.linked_skills)} skills)")
    
    # Test UserProfile
    print("\n✓ Testing UserProfile...")
    user_profile = UserProfile(
        user_id="user_123",
        years_experience=7,
        people_management=False,
        decision_level=0.3,
        domain_depth_years=5,
        skills=[skill],
        credentials=[credential],
        action_log=[action]
    )
    print(f"  Created profile for user: {user_profile.user_id}")
    print(f"    - {len(user_profile.skills)} skills")
    print(f"    - {len(user_profile.credentials)} credentials")
    print(f"    - {len(user_profile.action_log)} actions")
    
    # Test JobData
    print("\n✓ Testing JobData...")
    job_data = JobData(
        occupation_code="15-2051",  # Software Developers
        industry="Technology",
        wage_level=0.75,
        technical_readiness=0.85
    )
    print(f"  Created job: {job_data.occupation_code} in {job_data.industry}")
    
    # Test RiskAnalysisRequest
    print("\n✓ Testing RiskAnalysisRequest...")
    request = RiskAnalysisRequest(
        user_profile=user_profile,
        job_data=job_data
    )
    print(f"  Created request for user: {request.user_profile.user_id}")
    
    # Test DisplacementRiskScore
    print("\n✓ Testing DisplacementRiskScore...")
    risk_score = DisplacementRiskScore(
        level="Medium",
        score=55.5,
        time_horizon="2-5 years",
        confidence=85.0,
        percentile_vs_role=68.0,
        trajectory="improving",
        justification="Your risk is moderate but improving due to recent upskilling.",
        primary_vulnerabilities=["High task automation potential", "Industry velocity"],
        protection_opportunities=["Complete AI certification", "Build portfolio projects"]
    )
    print(f"  Created risk score: {risk_score.level} ({risk_score.score}/100)")
    print(f"    - Time horizon: {risk_score.time_horizon}")
    print(f"    - Trajectory: {risk_score.trajectory}")
    
    # Test DebugComponents
    print("\n✓ Testing DebugComponents...")
    debug = DebugComponents(
        StructuralRisk=62.5,
        PersonalShield=45.2,
        TAS=68.0,
        IVS=54.0,
        PSC=52.0,
        AS=38.0,
        SeniorityProtection=25.0,
        CredentialStrength=50.0,
        TimeHorizonIndex=0.55,
        Confidence=85.0
    )
    print(f"  Created debug components:")
    print(f"    - Structural Risk: {debug.StructuralRisk}")
    print(f"    - Personal Shield: {debug.PersonalShield}")
    
    # Test RiskAnalysisResponse
    print("\n✓ Testing RiskAnalysisResponse...")
    response = RiskAnalysisResponse(
        ai_displacement_risk=risk_score,
        debug_components=debug,
        calculated_at=datetime.utcnow()
    )
    print(f"  Created response at: {response.calculated_at}")
    print(f"    - Score: {response.ai_displacement_risk.score}")
    print(f"    - TAS: {response.debug_components.TAS}")
    
    print("\n" + "="*60)
    print("✅ ALL MODELS TESTED SUCCESSFULLY!")
    print("="*60)
    print("\n📋 Next step: Implement TAS Calculator")
    print("   - File: calculators/tas_calculator.py")
    print("   - Calculates Task Automation Score from ai_task_taxonomy")
    print("   - Timeline: 1-2 hours\n")


if __name__ == "__main__":
    test_models()
