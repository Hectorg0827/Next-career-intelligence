import uuid
import sys
import os
from datetime import datetime

# Add backend directory to python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.models.database import User, UserSkill, Skill
from app.services.skill_service import SkillService
from app.services.skill_gap_analyzer import SkillGapAnalyzerService
from app.models.skill_schemas import ProficiencyLevel, EvidenceSource, SkillGapRequest

def test_skill_ingestion_and_gap_analysis():
    print("="*50)
    print("TESTING SKILL INGESTION & GAP ANALYSIS")
    print("="*50)

    db = SessionLocal()
    skill_service = SkillService()
    gap_analyzer = SkillGapAnalyzerService()
    
    test_user_id = str(uuid.uuid4())
    test_email = f"test_skill_{test_user_id[:8]}@example.com"
    
    try:
        # 1. Create Test User
        print(f"\n1. Creating test user: {test_email}")
        user = User(
            id=test_user_id,
            email=test_email,
            firebase_uid=f"firebase_{test_user_id}",
            first_name="Test",
            last_name="User",
            role="user"
        )
        db.add(user)
        db.commit()
        print("   User created successfully.")

        # 2. Add Skills via SkillService
        print("\n2. Adding skills via SkillService...")
        
        # Add Python (Expert)
        print("   Adding 'Python' (Expert)...")
        skill_service.add_user_skill(
            db=db,
            user_id=test_user_id,
            skill_name="Python",
            proficiency_level=ProficiencyLevel.EXPERT,
            evidence_source=EvidenceSource.MANUAL,
            last_used_year=2025.0
        )
        
        # Add SQL (Intermediate)
        print("   Adding 'SQL' (Intermediate)...")
        skill_service.add_user_skill(
            db=db,
            user_id=test_user_id,
            skill_name="SQL",
            proficiency_level=ProficiencyLevel.INTERMEDIATE,
            evidence_source=EvidenceSource.RESUME,
            last_used_year=2024.0
        )
        
        # Verify skills in DB
        user_skills = skill_service.get_user_skills(db, test_user_id)
        print(f"   User has {len(user_skills.skills)} skills.")
        for s in user_skills.skills:
            print(f"   - {s.name}: {s.proficiency_level} ({s.evidence_source})")
            
        assert len(user_skills.skills) >= 2
        
        # 3. Test Skill Gap Analysis
        print("\n3. Testing Skill Gap Analysis...")
        target_role = "Data Analyst"
        print(f"   Target Role: {target_role}")
        
        # We need to mock the async call or run it in an event loop if it's async
        # analyze_skill_gap is async
        import asyncio
        
        async def run_analysis():
            request = SkillGapRequest(target_role_title=target_role)
            analysis = await gap_analyzer.analyze_skill_gap(db, test_user_id, request)
            return analysis
            
        analysis = asyncio.run(run_analysis())
        
        print(f"   Role Fit Score: {analysis.role_fit_score:.1f}%")
        print(f"   Matched Skills: {len(analysis.matched_skills)}")
        print(f"   Weak Skills: {len(analysis.weak_skills)}")
        print(f"   Gap Skills: {len(analysis.gap_skills)}")
        
        print("   Matched:")
        for m in analysis.matched_skills:
            print(f"     - {m.name} ({m.proficiency_level}) - Relevance: {m.relevance_score}")

        print("   Weak:")
        for w in analysis.weak_skills:
            print(f"     - {w.name} ({w.proficiency_level}) - Relevance: {w.relevance_score}")
            
        print("   Gaps:")
        for g in analysis.gap_skills:
            print(f"     - {g.name} (Importance: {g.importance})")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        print("\n4. Cleaning up...")
        db.query(UserSkill).filter(UserSkill.user_id == test_user_id).delete()
        db.query(User).filter(User.id == test_user_id).delete()
        db.commit()
        db.close()
        print("   Cleanup complete.")

if __name__ == "__main__":
    test_skill_ingestion_and_gap_analysis()
