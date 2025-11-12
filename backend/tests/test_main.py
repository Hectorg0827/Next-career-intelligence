"""
Sample pytest configuration and basic tests
Run with: pytest
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "NEXT | Adaptive Career Intelligence API"
    assert data["status"] == "operational"


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert "services" in data


def test_job_suggestions():
    """Test job suggestions endpoint"""
    response = client.get("/api/jobs/suggest?q=software&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 5


def test_analyze_career():
    """Test career analysis endpoint"""
    payload = {
        "job_title": "Software Developer",
        "skills": ["Python", "JavaScript", "SQL"],
        "location": "United States",
        "years_experience": 5,
    }

    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 201
    data = response.json()

    # Verify response structure
    assert "analysis_id" in data
    assert "ai_displacement_risk" in data
    assert "compatibility_score" in data
    assert "transition_pathways" in data

    # Verify risk data
    risk = data["ai_displacement_risk"]
    assert "level" in risk
    assert "score" in risk
    assert 0 <= risk["score"] <= 100


def test_invalid_analysis_request():
    """Test analysis with invalid data"""
    payload = {"job_title": "X", "skills": [], "location": ""}  # Too short  # Empty

    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 422  # Validation error
