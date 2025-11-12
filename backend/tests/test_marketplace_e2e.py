"""
Automated E2E tests for job marketplace API
Tests all endpoints and complete workflows
"""

import pytest
import asyncio
from httpx import AsyncClient
from datetime import datetime
from app.main import app
from app.db.database import SessionLocal
from app.models.database import Job, JobApplication, SavedJob


# Test user credentials (Firebase token needed)
TEST_USER_ID = "test-user-001"
TEST_USER_TOKEN = "test-token"  # Replace with real Firebase token
TEST_JOB_ID = "test-job-001"


@pytest.fixture
async def client():
    """Create test client"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def db_session():
    """Create test database session"""
    db = SessionLocal()
    yield db
    db.close()


class TestJobSearchAndBrowse:
    """Test job search and browse functionality"""

    @pytest.mark.asyncio
    async def test_list_jobs(self, client):
        """Test GET /api/v1/marketplace/jobs"""
        response = await client.get("/api/v1/marketplace/jobs", params={"page": 1, "limit": 20})

        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "page" in data
        assert "limit" in data
        assert "results" in data
        assert isinstance(data["results"], list)

    @pytest.mark.asyncio
    async def test_search_jobs(self, client):
        """Test job search with query"""
        response = await client.get("/api/v1/marketplace/jobs", params={"query": "Python", "page": 1, "limit": 20})

        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) >= 0
        # Verify results contain search term
        for job in data["results"]:
            assert "Python" in job.get("title", "") or "Python" in job.get("description", "")

    @pytest.mark.asyncio
    async def test_filter_by_location(self, client):
        """Test location filter"""
        response = await client.get("/api/v1/marketplace/jobs", params={"location": "Remote", "page": 1, "limit": 20})

        assert response.status_code == 200
        data = response.json()
        for job in data["results"]:
            assert job.get("location") == "Remote"

    @pytest.mark.asyncio
    async def test_filter_by_salary(self, client):
        """Test salary range filter"""
        response = await client.get(
            "/api/v1/marketplace/jobs", params={"min_salary": 100000, "max_salary": 200000, "page": 1, "limit": 20}
        )

        assert response.status_code == 200
        data = response.json()
        for job in data["results"]:
            salary_min = job.get("salary_min", 0)
            salary_max = job.get("salary_max", float("inf"))
            assert salary_min >= 100000 and salary_max <= 200000

    @pytest.mark.asyncio
    async def test_get_job_details(self, client, db_session):
        """Test GET /api/v1/marketplace/jobs/{job_id}"""
        # First get a job ID from list
        list_response = await client.get("/api/v1/marketplace/jobs", params={"limit": 1})
        jobs = list_response.json()["results"]

        if jobs:
            job_id = jobs[0]["id"]
            response = await client.get(f"/api/v1/marketplace/jobs/{job_id}")

            assert response.status_code == 200
            data = response.json()
            assert data["id"] == job_id
            assert "title" in data
            assert "company" in data
            assert "description" in data


class TestJobApplications:
    """Test job application functionality"""

    @pytest.mark.asyncio
    async def test_apply_to_job(self, client):
        """Test POST /api/v1/marketplace/job-applications"""
        # Get a job first
        list_response = await client.get("/api/v1/marketplace/jobs", params={"limit": 1})
        jobs = list_response.json()["results"]

        if jobs:
            job_id = jobs[0]["id"]

            response = await client.post(
                "/api/v1/marketplace/job-applications",
                json={"job_id": job_id},
                headers={"Authorization": f"Bearer {TEST_USER_TOKEN}"},
            )

            # Should succeed or return 409 if already applied
            assert response.status_code in [200, 201, 409]

    @pytest.mark.asyncio
    async def test_list_applications(self, client):
        """Test GET /api/v1/marketplace/user/applications"""
        response = await client.get(
            "/api/v1/marketplace/user/applications", headers={"Authorization": f"Bearer {TEST_USER_TOKEN}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["applications"], list)
        assert "stats" in data or "total" in data

    @pytest.mark.asyncio
    async def test_get_application_details(self, client):
        """Test GET /api/v1/marketplace/user/applications/{id}"""
        # Get applications first
        list_response = await client.get(
            "/api/v1/marketplace/user/applications", headers={"Authorization": f"Bearer {TEST_USER_TOKEN}"}
        )

        applications = list_response.json().get("applications", [])
        if applications:
            app_id = applications[0]["id"]

            response = await client.get(
                f"/api/v1/marketplace/user/applications/{app_id}",
                headers={"Authorization": f"Bearer {TEST_USER_TOKEN}"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["id"] == app_id

    @pytest.mark.asyncio
    async def test_update_application_status(self, client):
        """Test PUT /api/v1/marketplace/job-applications/{id}"""
        # Get applications first
        list_response = await client.get(
            "/api/v1/marketplace/user/applications", headers={"Authorization": f"Bearer {TEST_USER_TOKEN}"}
        )

        applications = list_response.json().get("applications", [])
        if applications:
            app_id = applications[0]["id"]

            response = await client.put(
                f"/api/v1/marketplace/job-applications/{app_id}",
                json={"status": "interview_scheduled", "interview_date": "2025-11-15T10:00:00"},
                headers={"Authorization": f"Bearer {TEST_USER_TOKEN}"},
            )

            assert response.status_code in [200, 400]

    @pytest.mark.asyncio
    async def test_withdraw_application(self, client):
        """Test DELETE /api/v1/marketplace/job-applications/{id}"""
        # Get applications first
        list_response = await client.get(
            "/api/v1/marketplace/user/applications", headers={"Authorization": f"Bearer {TEST_USER_TOKEN}"}
        )

        applications = list_response.json().get("applications", [])
        if applications:
            app_id = applications[0]["id"]

            response = await client.delete(
                f"/api/v1/marketplace/job-applications/{app_id}", headers={"Authorization": f"Bearer {TEST_USER_TOKEN}"}
            )

            assert response.status_code in [200, 204, 404]

    @pytest.mark.asyncio
    async def test_get_application_stats(self, client):
        """Test GET /api/v1/marketplace/user/application-stats"""
        response = await client.get(
            "/api/v1/marketplace/user/application-stats", headers={"Authorization": f"Bearer {TEST_USER_TOKEN}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "total_applications" in data
        assert "applied" in data
        assert "average_match_score" in data


class TestSavedJobs:
    """Test saved jobs functionality"""

    @pytest.mark.asyncio
    async def test_save_job(self, client):
        """Test POST /api/v1/marketplace/saved-jobs"""
        # Get a job first
        list_response = await client.get("/api/v1/marketplace/jobs", params={"limit": 1})
        jobs = list_response.json()["results"]

        if jobs:
            job_id = jobs[0]["id"]

            response = await client.post(
                "/api/v1/marketplace/saved-jobs",
                json={"job_id": job_id, "notes": "Interested in this role"},
                headers={"Authorization": f"Bearer {TEST_USER_TOKEN}"},
            )

            assert response.status_code in [200, 201, 409]

    @pytest.mark.asyncio
    async def test_list_saved_jobs(self, client):
        """Test GET /api/v1/marketplace/user/saved-jobs"""
        response = await client.get(
            "/api/v1/marketplace/user/saved-jobs", headers={"Authorization": f"Bearer {TEST_USER_TOKEN}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "saved_jobs" in data or isinstance(data, list)

    @pytest.mark.asyncio
    async def test_remove_saved_job(self, client):
        """Test DELETE /api/v1/marketplace/saved-jobs/{id}"""
        # Get saved jobs first
        list_response = await client.get(
            "/api/v1/marketplace/user/saved-jobs", headers={"Authorization": f"Bearer {TEST_USER_TOKEN}"}
        )

        saved_jobs = (
            list_response.json()
            if isinstance(list_response.json(), list)
            else list_response.json().get("saved_jobs", [])
        )
        if saved_jobs:
            saved_id = saved_jobs[0]["id"]

            response = await client.delete(
                f"/api/v1/marketplace/saved-jobs/{saved_id}", headers={"Authorization": f"Bearer {TEST_USER_TOKEN}"}
            )

            assert response.status_code in [200, 204, 404]


class TestAlerts:
    """Test job alert preferences"""

    @pytest.mark.asyncio
    async def test_create_alert_preferences(self, client):
        """Test POST /api/v1/marketplace/job-alert-preferences"""
        response = await client.post(
            "/api/v1/marketplace/job-alert-preferences",
            json={
                "job_title_keywords": ["Python", "Senior"],
                "locations": ["Remote", "San Francisco"],
                "min_salary": 120000,
                "email_alerts_enabled": True,
            },
            headers={"Authorization": f"Bearer {TEST_USER_TOKEN}"},
        )

        assert response.status_code in [200, 201]

    @pytest.mark.asyncio
    async def test_get_alert_preferences(self, client):
        """Test GET /api/v1/marketplace/job-alert-preferences"""
        response = await client.get(
            "/api/v1/marketplace/job-alert-preferences", headers={"Authorization": f"Bearer {TEST_USER_TOKEN}"}
        )

        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_update_alert_preferences(self, client):
        """Test PUT /api/v1/marketplace/job-alert-preferences"""
        response = await client.put(
            "/api/v1/marketplace/job-alert-preferences",
            json={"min_salary": 150000, "alert_frequency": "daily"},
            headers={"Authorization": f"Bearer {TEST_USER_TOKEN}"},
        )

        assert response.status_code in [200, 404]


class TestCompleteWorkflows:
    """Test complete user workflows"""

    @pytest.mark.asyncio
    async def test_search_to_apply_workflow(self, client):
        """Complete workflow: Search → View → Apply"""
        # Step 1: Search for jobs
        search_response = await client.get("/api/v1/marketplace/jobs", params={"query": "Python", "limit": 5})
        assert search_response.status_code == 200
        jobs = search_response.json()["results"]

        if jobs:
            # Step 2: View job details
            job_id = jobs[0]["id"]
            details_response = await client.get(f"/api/v1/marketplace/jobs/{job_id}")
            assert details_response.status_code == 200

            # Step 3: Apply to job
            apply_response = await client.post(
                "/api/v1/marketplace/job-applications",
                json={"job_id": job_id},
                headers={"Authorization": f"Bearer {TEST_USER_TOKEN}"},
            )
            assert apply_response.status_code in [200, 201, 409]

    @pytest.mark.asyncio
    async def test_save_to_apply_workflow(self, client):
        """Complete workflow: Save → Apply"""
        # Step 1: Get jobs
        list_response = await client.get("/api/v1/marketplace/jobs", params={"limit": 1})
        jobs = list_response.json()["results"]

        if jobs:
            job_id = jobs[0]["id"]

            # Step 2: Save job
            save_response = await client.post(
                "/api/v1/marketplace/saved-jobs",
                json={"job_id": job_id},
                headers={"Authorization": f"Bearer {TEST_USER_TOKEN}"},
            )
            assert save_response.status_code in [200, 201, 409]

            # Step 3: Apply to job
            apply_response = await client.post(
                "/api/v1/marketplace/job-applications",
                json={"job_id": job_id},
                headers={"Authorization": f"Bearer {TEST_USER_TOKEN}"},
            )
            assert apply_response.status_code in [200, 201, 409]


if __name__ == "__main__":
    # Run with: pytest backend/tests/test_marketplace_e2e.py -v
    pytest.main([__file__, "-v", "-s"])
