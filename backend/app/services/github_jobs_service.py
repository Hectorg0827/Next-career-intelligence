"""GitHub Jobs API integration service.

Fetches job listings from GitHub Jobs API and seeds them into the database.
GitHub Jobs API: https://jobs.github.com/api/
"""

import httpx
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.jobs import Job

logger = logging.getLogger(__name__)

# GitHub Jobs API base URL
GITHUB_JOBS_API = "https://jobs.github.com/api/jobs.json"

# Mapping of experience level keywords to our standardized levels
EXPERIENCE_KEYWORDS = {
    "junior": "entry",
    "entry": "entry",
    "entry-level": "entry",
    "mid": "mid",
    "mid-level": "mid",
    "intermediate": "mid",
    "senior": "senior",
    "lead": "senior",
    "principal": "senior",
    "architect": "senior",
}

# Mapping of job type keywords
JOB_TYPE_KEYWORDS = {
    "full time": "full_time",
    "full-time": "full_time",
    "fulltime": "full_time",
    "part time": "part_time",
    "part-time": "part_time",
    "parttime": "part_time",
    "contract": "contract",
    "freelance": "contract",
}

# Mapping of remote type keywords
REMOTE_KEYWORDS = {
    "remote": "remote",
    "fully remote": "remote",
    "100% remote": "remote",
    "hybrid": "hybrid",
    "on site": "on_site",
    "on-site": "on_site",
    "onsite": "on_site",
    "office": "on_site",
    "in-office": "on_site",
}


class GitHubJobsService:
    """Service for fetching and managing GitHub Jobs."""

    @staticmethod
    def extract_experience_level(description: str) -> Optional[str]:
        """Extract experience level from job description."""
        if not description:
            return None

        description_lower = description.lower()
        for keyword, level in EXPERIENCE_KEYWORDS.items():
            if keyword in description_lower:
                return level
        return None

    @staticmethod
    def extract_job_type(description: str) -> Optional[str]:
        """Extract job type from job description."""
        if not description:
            return None

        description_lower = description.lower()
        for keyword, job_type in JOB_TYPE_KEYWORDS.items():
            if keyword in description_lower:
                return job_type
        return None

    @staticmethod
    def extract_remote_type(description: str) -> Optional[str]:
        """Extract remote type from job description."""
        if not description:
            return None

        description_lower = description.lower()
        for keyword, remote_type in REMOTE_KEYWORDS.items():
            if keyword in description_lower:
                return remote_type
        return "on_site"  # Default to on-site if not specified

    @staticmethod
    def extract_skills(description: str) -> List[str]:
        """Extract common technical skills from job description."""
        if not description:
            return []

        # Common tech skills to look for
        skills = [
            "python",
            "javascript",
            "typescript",
            "java",
            "c#",
            "go",
            "rust",
            "react",
            "vue",
            "angular",
            "svelte",
            "nextjs",
            "next.js",
            "nuxt",
            "django",
            "flask",
            "fastapi",
            "spring",
            "express",
            "nestjs",
            "aws",
            "azure",
            "gcp",
            "google cloud",
            "kubernetes",
            "docker",
            "sql",
            "postgresql",
            "mysql",
            "mongodb",
            "redis",
            "elasticsearch",
            "git",
            "github",
            "gitlab",
            "ci/cd",
            "devops",
            "terraform",
            "ansible",
            "machine learning",
            "ai",
            "deep learning",
            "nlp",
            "computer vision",
            "nodejs",
            "node.js",
            "php",
            "ruby",
            "scala",
            "kotlin",
            "swift",
            "ios",
            "android",
            "react native",
            "flutter",
            "html",
            "css",
            "sass",
            "tailwind",
            "bootstrap",
            "graphql",
            "rest",
            "api",
            "microservices",
            "monolith",
            "agile",
            "scrum",
            "kanban",
            "jira",
        ]

        description_lower = description.lower()
        found_skills = []

        for skill in skills:
            if skill in description_lower:
                found_skills.append(skill)

        # Remove duplicates and return
        return list(set(found_skills))

    @staticmethod
    async def fetch_jobs(
        position: Optional[str] = None,
        location: Optional[str] = None,
        page: int = 0,
        full_time: bool = False,
    ) -> List[Dict[str, Any]]:
        """Fetch jobs from GitHub Jobs API.

        Args:
            position: Job title to search for
            location: Location to search in
            page: Page number (0-indexed)
            full_time: If True, only full-time jobs

        Returns:
            List of job dictionaries from the API
        """
        params = {
            "page": page,
        }

        if position:
            params["description"] = position
        if location:
            params["location"] = location
        if full_time:
            params["full_time"] = "true"

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(GITHUB_JOBS_API, params=params)
                response.raise_for_status()
                return response.json()
        except httpx.RequestError as e:
            logger.error(f"Error fetching jobs from GitHub API: {e}")
            return []

    @staticmethod
    def seed_jobs(
        db: Session,
        jobs_data: List[Dict[str, Any]],
        source: str = "github",
    ) -> tuple[int, int]:
        """Seed jobs into the database.

        Args:
            db: Database session
            jobs_data: List of job dictionaries from API
            source: Source identifier (default: "github")

        Returns:
            Tuple of (created_count, skipped_count)
        """
        created_count = 0
        skipped_count = 0

        for job_data in jobs_data:
            try:
                # Check if job already exists by external ID
                existing_job = (
                    db.query(Job)
                    .filter(
                        Job.external_id == job_data.get("id"),
                        Job.source == source,
                    )
                    .first()
                )

                if existing_job:
                    skipped_count += 1
                    continue

                # Extract data from API response
                description = job_data.get("description", "")
                title = job_data.get("title", "")

                # Create new job record
                job = Job(
                    title=title,
                    company=job_data.get("company", ""),
                    description=description,
                    location=job_data.get("location", ""),
                    remote_type=GitHubJobsService.extract_remote_type(description),
                    job_type=GitHubJobsService.extract_job_type(description),
                    experience_level=GitHubJobsService.extract_experience_level(description),
                    required_skills=GitHubJobsService.extract_skills(description),
                    company_logo_url=job_data.get("company_logo", None),
                    job_url=job_data.get("url", ""),
                    source=source,
                    external_id=job_data.get("id"),
                    is_active=True,
                )

                db.add(job)
                created_count += 1

            except (KeyError, ValueError) as e:
                logger.error(f"Error processing job data: {e}")
                skipped_count += 1
                continue

        try:
            db.commit()
            logger.info(f"Seeded {created_count} jobs, skipped {skipped_count}")
        except Exception as e:
            db.rollback()
            logger.error(f"Error committing jobs to database: {e}")
            created_count = 0

        return created_count, skipped_count

    @staticmethod
    async def seed_github_jobs_batch(
        db: Session,
        num_pages: int = 5,
        source: str = "github",
    ) -> tuple[int, int]:
        """Seed multiple pages of GitHub jobs.

        Args:
            db: Database session
            num_pages: Number of pages to fetch (each page has ~50 jobs)
            source: Source identifier

        Returns:
            Tuple of (total_created, total_skipped)
        """
        total_created = 0
        total_skipped = 0

        logger.info(f"Starting to seed GitHub jobs ({num_pages} pages)...")

        for page in range(num_pages):
            logger.info(f"Fetching page {page}...")
            jobs = await GitHubJobsService.fetch_jobs(page=page, full_time=True)

            if not jobs:
                logger.info(f"No jobs found on page {page}, stopping")
                break

            created, skipped = GitHubJobsService.seed_jobs(db, jobs, source)
            total_created += created
            total_skipped += skipped

            logger.info(f"Page {page}: Created {created}, Skipped {skipped}")

        logger.info(f"Seeding complete: {total_created} created, {total_skipped} skipped")
        return total_created, total_skipped

    @staticmethod
    async def seed_jobs_by_position(
        db: Session,
        positions: List[str],
        pages_per_position: int = 3,
        source: str = "github",
    ) -> tuple[int, int]:
        """Seed jobs by specific positions/titles.

        Args:
            db: Database session
            positions: List of job titles to search for
            pages_per_position: Pages to fetch per position
            source: Source identifier

        Returns:
            Tuple of (total_created, total_skipped)
        """
        total_created = 0
        total_skipped = 0

        logger.info(f"Seeding jobs for {len(positions)} positions...")

        for position in positions:
            logger.info(f"Fetching jobs for position: {position}")

            for page in range(pages_per_position):
                jobs = await GitHubJobsService.fetch_jobs(
                    position=position,
                    page=page,
                    full_time=True,
                )

                if not jobs:
                    break

                created, skipped = GitHubJobsService.seed_jobs(db, jobs, source)
                total_created += created
                total_skipped += skipped

        logger.info(f"Position seeding complete: {total_created} created, {total_skipped} skipped")
        return total_created, total_skipped
