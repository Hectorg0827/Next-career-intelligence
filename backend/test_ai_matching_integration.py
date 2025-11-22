import uuid
import sys
import os
import asyncio
import json
from datetime import datetime

# Add backend directory to python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.models.database import User, Job, JobApplication, UserSkill, Skill
from app.services.skill_service import SkillService
from app.services.ai_matching_service import ai_matching_service
from app.models.skill_schemas import ProficiencyLevel, EvidenceSource

async def test_ai_matching_integration():
    print("="*50)
    print("TESTING AI MATCHING INTEGRATION")
    print("="*50)

    db = SessionLocal()
    skill_service = SkillService()
    
    test_user_id = str(uuid.uuid4())
    test_job_id = uuid.uuid4()
    
    try:
        # 1. Create Test User
        print(f"\n1. Creating test user: {test_user_id}")
        user = User(
            id=test_user_id,
            email=f"test_match_{test_user_id[:8]}@example.com",
            firebase_uid=f"firebase_{test_user_id}",
            first_name="Match",
            last_name="Tester",
            role="user",
            user_metadata={
                "years_of_experience": 5,
                "experience_level": "mid",
                "current_job_title": "Software Engineer"
            }
        )
        db.add(user)
        db.commit()

        # 2. Add Skills
        print("\n2. Adding skills...")
        skill_service.add_user_skill(
            db=db,
            user_id=test_user_id,
            skill_name="Python",
            proficiency_level=ProficiencyLevel.EXPERT,
            evidence_source=EvidenceSource.MANUAL
        )
        skill_service.add_user_skill(
            db=db,
            user_id=test_user_id,
            skill_name="FastAPI",
            proficiency_level=ProficiencyLevel.ADVANCED,
            evidence_source=EvidenceSource.MANUAL
        )

        # 3. Create Test Job
        print(f"\n3. Creating test job: {test_job_id}")
        job = Job(
            id=test_job_id,
            title="Senior Python Developer",
            # company="Tech Corp", # Removed as per schema
            description="We are looking for a Python expert with FastAPI experience.",
            location="Remote",
            remote_policy="remote", # Renamed from remote_type
            salary_min=120000,
            salary_max=160000,
            required_skills=["Python", "FastAPI", "PostgreSQL"],
            seniority="senior", # Renamed from experience_level
            source="manual",
            is_active=True # Boolean
        )
        db.add(job)
        db.commit()

        # 4. Run Matching
        print("\n4. Running AI Matching...")
        matches_count = await ai_matching_service.calculate_all_matches_for_user(test_user_id, db)
        print(f"   Matches calculated: {matches_count}")
        
        # 5. Verify Results
        print("\n5. Verifying results...")
        application = db.query(JobApplication).filter(
            JobApplication.user_id == test_user_id,
            JobApplication.job_id == test_job_id
        ).first()
        
        if application:
            print(f"   ✅ Match found!")
            print(f"   Score: {application.match_score}")
            print(f"   Status: {application.status}")
            print(f"   Skill Gaps: {application.skill_gaps}")
            print(f"   Prep: {application.recommended_prep}")
        else:
            print("   ❌ No match record found.")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        print("\n6. Cleaning up...")
        db.query(JobApplication).filter(JobApplication.user_id == test_user_id).delete()
        db.query(UserSkill).filter(UserSkill.user_id == test_user_id).delete()
        db.query(User).filter(User.id == test_user_id).delete()
        db.query(Job).filter(Job.id == test_job_id).delete()
        db.commit()
        db.close()
        print("   Cleanup complete.")

if __name__ == "__main__":
    asyncio.run(test_ai_matching_integration())
