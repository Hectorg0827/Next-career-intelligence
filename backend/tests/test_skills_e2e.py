import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
import os

# Set env vars for testing if needed
os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = "postgresql://postgres:ssuRd6vrGSdP5z7a@db.whxbxjpymksgvixudnjh.supabase.co:5432/postgres"

from app.main import app
from app.db.database import SessionLocal, engine
from app.models.database import Base, User
from app.core.auth import get_current_user
from app.core.config import settings

print(f"Using DATABASE_URL: {settings.DATABASE_URL}")

client = TestClient(app)

@pytest.fixture(scope="module")
def db():
    session = SessionLocal()
    yield session
    session.close()

@pytest.fixture(scope="module")
def test_user(db):
    # Create test user
    # We use a random firebase_uid to avoid collisions
    firebase_uid = f"test_user_{uuid.uuid4()}"
    email = f"test_{uuid.uuid4()}@example.com"
    
    # User ID must be a string if the model uses as_uuid=False
    user_id = str(uuid.uuid4())
    
    user = User(
        id=user_id,
        firebase_uid=firebase_uid,
        email=email,
        first_name="Test",
        last_name="User",
        account_created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    yield user
    
    # Cleanup
    # We need to merge the user back into the session if it's detached
    user = db.merge(user)
    db.delete(user)
    db.commit()

def test_skills_flow(test_user):
    # Override auth dependency to return our test user
    app.dependency_overrides[get_current_user] = lambda: test_user
    
    print(f"Testing with user: {test_user.id}")
    
    # 1. Add Manual Skills
    print("Testing manual skills addition...")
    response = client.post(
        "/api/profile/skills/manual",
        json={
            "skills": [
                {"name": "Python", "proficiency_level": "EXPERT"},
                {"name": "FastAPI", "proficiency_level": "ADVANCED"}
            ]
        }
    )
    assert response.status_code == 200, f"Manual skills failed: {response.text}"
    data = response.json()
    assert len(data["skills"]) >= 2
    names = [s["name"] for s in data["skills"]]
    assert "Python" in names
    assert "FastAPI" in names
    
    # 2. Upload Resume (Mock)
    print("Testing resume upload...")
    resume_text = """
    Experienced Software Engineer with skills in Docker, Kubernetes, and AWS.
    Proficient in PostgreSQL and React.
    """
    response = client.post(
        "/api/profile/skills/from-resume",
        json={"resume_text": resume_text}
    )
    assert response.status_code == 200, f"Resume upload failed: {response.text}"
    data = response.json()
    names = [s["name"].lower() for s in data["skills"]]
    assert "docker" in names
    assert "kubernetes" in names
    assert "aws" in names
    
    # 3. Conversation Extraction (Mock)
    # Note: This might fail if LLM is not configured or mocked.
    # We'll check if it returns 200 even if extraction fails (it should return current skills)
    print("Testing conversation extraction...")
    response = client.post(
        "/api/profile/skills/from-conversation",
        json={"conversation_transcript": "I have been using TypeScript for 2 years."}
    )
    assert response.status_code == 200, f"Conversation extraction failed: {response.text}"
    # If LLM is not available, it might not add skills, but shouldn't crash.
    
    # 4. Add Education
    print("Testing education addition...")
    response = client.post(
        "/api/profile/education",
        json={
            "degree": "Bachelor of Science",
            "institution": "University of Tech",
            "field_of_study": "Computer Science",
            "start_year": 2015,
            "end_year": 2019
        }
    )
    assert response.status_code == 200, f"Education addition failed: {response.text}"
    data = response.json()
    assert data["degree"] == "Bachelor of Science"
    
    # 5. Get Education
    print("Testing get education...")
    response = client.get("/api/profile/education")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["institution"] == "University of Tech"
    
    # 6. Skill Gap Analysis
    print("Testing skill gap analysis...")
    response = client.post(
        "/api/profile/skill-gap",
        json={
            "target_role_title": "Software Engineer"
        }
    )
    assert response.status_code == 200, f"Skill gap analysis failed: {response.text}"
    data = response.json()
    assert "role_fit_score" in data
    assert "matched_skills" in data
    assert "gap_skills" in data
    
    print("✅ All tests passed!")
