"""
Test script for Skills V2 API endpoints
Tests skill ingestion, education, and gap analysis
"""

import asyncio
import json
from typing import Dict, Any
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# Load env
load_dotenv('backend/.env')

from app.models.database import User, Skill, UserSkill, Education
from app.services.skill_service import skill_service
from app.models.skill_schemas import (
    SkillCreate,
    ProficiencyLevel,
    EvidenceSource,
    EducationCreate,
    SkillGapRequest
)

def setup_db() -> Session:
    """Setup database connection"""
    database_url = os.getenv("DATABASE_URL")
    engine = create_engine(database_url)
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()

def test_skill_ingestion(db: Session, user_id: str):
    """Test adding skills"""
    print("\n=== Testing Skill Ingestion ===")
    
    # Test 1: Add manual skills
    print("\n1. Adding manual skills...")
    skills = [
        SkillCreate(name="Python", proficiency_level=ProficiencyLevel.ADVANCED),
        SkillCreate(name="JavaScript", proficiency_level=ProficiencyLevel.INTERMEDIATE),
        SkillCreate(name="SQL", proficiency_level=ProficiencyLevel.ADVANCED),
    ]
    
    try:
        skill_service.add_multiple_skills(
            db=db,
            user_id=user_id,
            skills=skills,
            evidence_source=EvidenceSource.SELF_REPORTED
        )
        db.commit()
        print("✅ Manual skills added successfully")
    except Exception as e:
        print(f"❌ Failed to add manual skills: {e}")
        db.rollback()
        return False
    
    # Test 2: Get user skills
    print("\n2. Retrieving user skills...")
    try:
        user_skills_response = skill_service.get_user_skills(db, user_id)
        print(f"✅ Retrieved {user_skills_response.total_count} skills")
        for skill in user_skills_response.skills:
            print(f"   - {skill.name} ({skill.proficiency_level.value})")
    except Exception as e:
        print(f"❌ Failed to get user skills: {e}")
        return False
    
    # Test 3: Resume parsing
    print("\n3. Testing resume parsing...")
    resume_text = """
    Software Engineer with 5 years of experience.
    
    Technical Skills:
    - Python, Java, JavaScript
    - React, Node.js
    - PostgreSQL, MongoDB
    - AWS, Docker
    - Git, Agile, Scrum
    
    Experience in machine learning and data analysis.
    """
    
    try:
        parsed_skills = skill_service.parse_resume_for_skills(resume_text)
        print(f"✅ Parsed {len(parsed_skills)} skills from resume")
        for skill in parsed_skills[:5]:
            print(f"   - {skill.name}")
    except Exception as e:
        print(f"❌ Failed to parse resume: {e}")
        return False
    
    return True

def test_education(db: Session, user_id: str):
    """Test education endpoints"""
    print("\n=== Testing Education ===")
    
    # Add education
    print("\n1. Adding education record...")
    edu_data = EducationCreate(
        degree="Bachelor of Science",
        institution="MIT",
        field_of_study="Computer Science",
        start_year=2015.0,
        end_year=2019.0
    )
    
    try:
        education = skill_service.add_education(db, user_id, edu_data)
        db.commit()
        print(f"✅ Education added: {education.degree} from {education.institution}")
    except Exception as e:
        print(f"❌ Failed to add education: {e}")
        db.rollback()
        return False
    
    # Get education
    print("\n2. Retrieving education records...")
    try:
        education_list = skill_service.get_user_education(db, user_id)
        print(f"✅ Retrieved {len(education_list)} education records")
        for edu in education_list:
            print(f"   - {edu.degree} from {edu.institution}")
    except Exception as e:
        print(f"❌ Failed to get education: {e}")
        return False
    
    return True

async def test_gap_analysis(db: Session, user_id: str):
    """Test skill gap analysis"""
    print("\n=== Testing Skill Gap Analysis ===")
    
    from app.services.skill_gap_analyzer import skill_gap_analyzer
    
    request = SkillGapRequest(
        target_role_title="Data Analyst"
    )
    
    try:
        print(f"\n1. Analyzing gap for role: {request.target_role_title}")
        analysis = await skill_gap_analyzer.analyze_skill_gap(db, user_id, request)
        
        print(f"✅ Gap analysis completed!")
        print(f"\n📊 Results:")
        print(f"   Title: {analysis.title}")
        print(f"   Fit Score: {analysis.role_fit_score}%")
        print(f"   Matched Skills: {analysis.matched_count}")
        print(f"   Gap Skills: {analysis.gap_count}")
        
        if analysis.matched_skills:
            print(f"\n   ✅ Top Matched Skills:")
            for skill in analysis.matched_skills[:3]:
                print(f"      - {skill.name} ({skill.relevance_score}% match)")
        
        if analysis.gap_skills:
            print(f"\n   ⚠️  Top Gap Skills:")
            for skill in analysis.gap_skills[:3]:
                print(f"      - {skill.name} ({skill.importance})")
        
        if analysis.suggested_learning_clusters:
            print(f"\n   📚 Learning Path:")
            for cluster in analysis.suggested_learning_clusters:
                print(f"      - {cluster.cluster_name} ({cluster.priority} priority)")
        
        print(f"\n   💡 Summary: {analysis.summary}")
        
        return True
    except Exception as e:
        print(f"❌ Failed gap analysis: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests"""
    print("=" * 60)
    print("Skills V2 Integration Test Suite")
    print("=" * 60)
    
    db = setup_db()
    
    # Find a test user
    print("\n🔍 Finding test user...")
    user = db.query(User).first()
    if not user:
        print("❌ No users found in database. Please create a test user first.")
        return
    
    user_id = str(user.id)
    print(f"✅ Using test user: {user.email} (ID: {user_id})")
    
    # Run tests
    results = {
        "skill_ingestion": test_skill_ingestion(db, user_id),
        "education": test_education(db, user_id),
        "gap_analysis": await test_gap_analysis(db, user_id)
    }
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️  Some tests failed. Check logs above.")
    
    db.close()

if __name__ == "__main__":
    asyncio.run(main())
