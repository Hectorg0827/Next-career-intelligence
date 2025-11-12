"""
Greenhouse Job Scraper

Scrapes jobs from Greenhouse-powered career sites.
Greenhouse provides a public API for job boards.

API Documentation: https://developers.greenhouse.io/job-board.html
"""

import httpx
from typing import List, Dict, Optional
from datetime import datetime
from loguru import logger
import re
import asyncio


class GreenhouseScraper:
    """Scraper for Greenhouse job boards"""

    BASE_URL = "https://boards-api.greenhouse.io/v1/boards"

    # Major tech companies using Greenhouse
    GREENHOUSE_COMPANIES = [
        {"name": "Airbnb", "board_token": "airbnb"},
        {"name": "Stripe", "board_token": "stripe"},
        {"name": "GitLab", "board_token": "gitlab"},
        {"name": "Coinbase", "board_token": "coinbase"},
        {"name": "Notion", "board_token": "notion"},
        {"name": "Figma", "board_token": "figma"},
        {"name": "Databricks", "board_token": "databricks"},
        {"name": "Plaid", "board_token": "plaid"},
        {"name": "Ramp", "board_token": "ramp"},
        {"name": "Scale AI", "board_token": "scaleai"},
        {"name": "Rippling", "board_token": "rippling"},
        {"name": "Airtable", "board_token": "airtable"},
        {"name": "Checkr", "board_token": "checkr"},
        {"name": "Brex", "board_token": "brex"},
        {"name": "OpenAI", "board_token": "openai"},
    ]

    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={"User-Agent": "NEXT-Career-Intelligence/1.0", "Accept": "application/json"},
        )

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

    async def scrape_company(self, company_name: str, board_token: str) -> List[Dict]:
        """
        Scrape all jobs from a company's Greenhouse board

        Args:
            company_name: Company display name
            board_token: Greenhouse board token

        Returns:
            List of processed job dictionaries
        """
        try:
            url = f"{self.BASE_URL}/{board_token}/jobs"
            params = {"content": "true"}  # Include full job description

            logger.info(f"Scraping {company_name} jobs from Greenhouse...")

            response = await self.client.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            jobs_data = data.get("jobs", [])

            processed_jobs = []
            for job in jobs_data:
                processed = self._process_job(job, company_name)
                if processed:
                    processed_jobs.append(processed)

            logger.info(f"✅ Scraped {len(processed_jobs)} jobs from {company_name}")
            return processed_jobs

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"⚠️ Greenhouse board not found for {company_name}")
            else:
                logger.error(f"❌ HTTP error scraping {company_name}: {e}")
            return []

        except Exception as e:
            logger.error(f"❌ Failed to scrape {company_name}: {e}")
            return []

    def _process_job(self, raw_job: Dict, company_name: str) -> Optional[Dict]:
        """
        Transform Greenhouse job format to our schema

        Args:
            raw_job: Raw job data from Greenhouse API
            company_name: Company name

        Returns:
            Processed job dictionary or None if invalid
        """
        try:
            job_id = raw_job.get("id")
            title = raw_job.get("title", "").strip()

            if not title:
                return None

            # Location parsing
            location = raw_job.get("location", {})
            location_name = location.get("name", "") if isinstance(location, dict) else str(location)
            is_remote = "remote" in location_name.lower()

            # Parse location details
            location_city, location_state, location_country = self._parse_location(location_name)

            # Extract description and metadata
            content = raw_job.get("content", "")
            description = self._clean_html(content) if content else ""

            # Determine seniority from title
            seniority = self._infer_seniority(title)

            # Extract requirements and responsibilities
            requirements, responsibilities, benefits = self._extract_sections(description)

            # Extract skills
            skills = self._extract_skills(title, description)

            # Infer salary range (if not provided)
            salary_min, salary_max = self._infer_salary_range(title, seniority)

            # Determine experience years
            exp_min, exp_max = self._infer_experience_years(title, seniority, description)

            # Build job record
            job_record = {
                "external_id": f"greenhouse_{job_id}",
                "title": title,
                "company_name": company_name,
                "seniority": seniority,
                "description": description[:5000],  # Limit to 5000 chars
                "requirements": requirements,
                "responsibilities": responsibilities,
                "benefits": benefits,
                "skills_extracted": skills,
                "location_type": (
                    "remote" if is_remote else ("hybrid" if "hybrid" in location_name.lower() else "onsite")
                ),
                "location_city": location_city if not is_remote else None,
                "location_state": location_state if not is_remote else None,
                "location_country": location_country,
                "salary_min": salary_min,
                "salary_max": salary_max,
                "salary_currency": "USD",
                "employment_type": "full_time",
                "experience_years_min": exp_min,
                "experience_years_max": exp_max,
                "apply_url": raw_job.get("absolute_url", ""),
                "source": f"greenhouse:{company_name.lower().replace(' ', '_')}",
                "posted_at": self._parse_date(raw_job.get("updated_at")),
            }

            return job_record

        except Exception as e:
            logger.error(f"Failed to process job: {e}")
            return None

    def _parse_location(self, location_str: str) -> tuple:
        """Parse location string into city, state, country"""
        if not location_str or location_str.lower() == "remote":
            return (None, None, "USA")

        parts = [p.strip() for p in location_str.split(",")]

        if len(parts) >= 3:
            return (parts[0], parts[1], parts[2])
        elif len(parts) == 2:
            return (parts[0], parts[1], "USA")
        elif len(parts) == 1:
            return (parts[0], None, "USA")

        return (None, None, "USA")

    def _infer_seniority(self, title: str) -> str:
        """Infer seniority level from job title"""
        title_lower = title.lower()

        if any(word in title_lower for word in ["senior", "sr.", "lead", "principal", "staff", "architect"]):
            return "senior"
        elif any(word in title_lower for word in ["junior", "jr.", "entry", "associate", "intern"]):
            return "entry"
        elif any(word in title_lower for word in ["manager", "director", "head", "vp", "chief"]):
            return "manager"
        else:
            return "mid"

    def _extract_skills(self, title: str, description: str) -> List[str]:
        """Extract technical skills from title and description"""
        # Common tech skills to look for
        skill_patterns = [
            # Programming languages
            r"\b(Python|Java|JavaScript|TypeScript|Go|Rust|C\+\+|C#|Ruby|PHP|Swift|Kotlin|Scala)\b",
            # Frameworks
            r"\b(React|Vue|Angular|Next\.js|Django|Flask|FastAPI|Spring|Express|Node\.js)\b",
            # Databases
            r"\b(PostgreSQL|MySQL|MongoDB|Redis|Elasticsearch|DynamoDB|Cassandra)\b",
            # Cloud
            r"\b(AWS|Azure|GCP|Google Cloud|Kubernetes|Docker|Terraform)\b",
            # Tools
            r"\b(Git|CI/CD|Jenkins|GitHub Actions|Linux|Bash)\b",
            # ML/AI
            r"\b(Machine Learning|AI|TensorFlow|PyTorch|NLP|Computer Vision)\b",
        ]

        text = f"{title} {description}"
        skills = set()

        for pattern in skill_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            skills.update(match.title() for match in matches)

        return sorted(list(skills))[:20]  # Limit to 20 skills

    def _infer_salary_range(self, title: str, seniority: str) -> tuple:
        """Infer salary range based on title and seniority"""
        # Rough salary estimates (in USD)
        salary_map = {
            "entry": (70000, 100000),
            "mid": (100000, 140000),
            "senior": (140000, 200000),
            "manager": (150000, 220000),
        }

        # Adjust for specific roles
        title_lower = title.lower()
        base_min, base_max = salary_map.get(seniority, (100000, 140000))

        # Engineers typically earn more
        if "engineer" in title_lower or "developer" in title_lower:
            base_min = int(base_min * 1.1)
            base_max = int(base_max * 1.1)

        # ML/AI roles earn even more
        if any(word in title_lower for word in ["machine learning", "ai", "data scientist"]):
            base_min = int(base_min * 1.2)
            base_max = int(base_max * 1.2)

        return (base_min, base_max)

    def _infer_experience_years(self, title: str, seniority: str, description: str) -> tuple:
        """Infer required experience years"""
        # Look for explicit year requirements in description
        years_pattern = r"(\d+)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*experience"
        matches = re.findall(years_pattern, description.lower())

        if matches:
            min_years = int(matches[0])
            max_years = min_years + 3
            return (min_years, max_years)

        # Default based on seniority
        exp_map = {"entry": (0, 2), "mid": (2, 5), "senior": (5, 10), "manager": (7, 15)}

        return exp_map.get(seniority, (2, 5))

    def _extract_sections(self, description: str) -> tuple:
        """Extract requirements, responsibilities, and benefits sections"""
        # Simple heuristic-based extraction
        requirements = None
        responsibilities = None
        benefits = None

        # Split by common section headers
        sections = re.split(
            r"\n\s*(?:#+\s*)?(?:Requirements?|Qualifications?|What [Ww]e\'re [Ll]ooking [Ff]or):\s*\n",
            description,
            flags=re.IGNORECASE,
        )
        if len(sections) > 1:
            requirements = sections[1].split("\n\n")[0][:2000]

        sections = re.split(
            r"\n\s*(?:#+\s*)?(?:Responsibilities?|What [Yy]ou\'ll [Dd]o|The [Rr]ole):\s*\n",
            description,
            flags=re.IGNORECASE,
        )
        if len(sections) > 1:
            responsibilities = sections[1].split("\n\n")[0][:2000]

        sections = re.split(
            r"\n\s*(?:#+\s*)?(?:Benefits?|What [Ww]e [Oo]ffer|Perks):\s*\n", description, flags=re.IGNORECASE
        )
        if len(sections) > 1:
            benefits = sections[1].split("\n\n")[0][:1000]

        return (requirements, responsibilities, benefits)

    def _clean_html(self, html: str) -> str:
        """Remove HTML tags and clean text"""
        # Simple HTML tag removal
        text = re.sub(r"<[^>]+>", "", html)
        # Clean up whitespace
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse ISO date string"""
        if not date_str:
            return datetime.utcnow()

        try:
            # Remove timezone suffix if present
            date_str = date_str.replace("Z", "+00:00")
            return datetime.fromisoformat(date_str)
        except:
            return datetime.utcnow()

    async def scrape_all_companies(self, max_concurrent: int = 3) -> List[Dict]:
        """
        Scrape jobs from all configured companies

        Args:
            max_concurrent: Maximum concurrent requests

        Returns:
            List of all scraped jobs
        """
        all_jobs = []
        semaphore = asyncio.Semaphore(max_concurrent)

        async def scrape_with_limit(company: Dict):
            async with semaphore:
                return await self.scrape_company(company["name"], company["board_token"])

        # Scrape all companies concurrently (with limit)
        tasks = [scrape_with_limit(company) for company in self.GREENHOUSE_COMPANIES]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, list):
                all_jobs.extend(result)

        logger.info(f"🎉 Total jobs scraped from Greenhouse: {len(all_jobs)}")
        return all_jobs
