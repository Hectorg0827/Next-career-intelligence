"""
Lever Job Scraper

Scrapes jobs from Lever-powered career sites.
Lever provides a public API for job postings.

API Documentation: https://github.com/lever/postings-api
"""

import httpx
from typing import List, Dict, Optional
from datetime import datetime
from loguru import logger
import re
import asyncio


class LeverScraper:
    """Scraper for Lever job boards"""

    BASE_URL = "https://api.lever.co/v0/postings"

    # Major tech companies using Lever
    LEVER_COMPANIES = [
        {"name": "Netflix", "company_id": "netflix"},
        {"name": "Uber", "company_id": "uber"},
        {"name": "Lyft", "company_id": "lyft"},
        {"name": "Reddit", "company_id": "reddit"},
        {"name": "Twitch", "company_id": "twitch"},
        {"name": "Shopify", "company_id": "shopify"},
        {"name": "DoorDash", "company_id": "doordash"},
        {"name": "Instacart", "company_id": "instacart"},
        {"name": "Robinhood", "company_id": "robinhood"},
        {"name": "Square", "company_id": "square"},
        {"name": "Discord", "company_id": "discord"},
        {"name": "Grammarly", "company_id": "grammarly"}
    ]

    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={
                "User-Agent": "NEXT-Career-Intelligence/1.0",
                "Accept": "application/json"
            }
        )

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

    async def scrape_company(self, company_name: str, company_id: str) -> List[Dict]:
        """
        Scrape all jobs from a company's Lever board

        Args:
            company_name: Company display name
            company_id: Lever company identifier

        Returns:
            List of processed job dictionaries
        """
        try:
            url = f"{self.BASE_URL}/{company_id}"
            params = {"mode": "json"}

            logger.info(f"Scraping {company_name} jobs from Lever...")

            response = await self.client.get(url, params=params)
            response.raise_for_status()

            jobs_data = response.json()

            processed_jobs = []
            for job in jobs_data:
                processed = self._process_job(job, company_name)
                if processed:
                    processed_jobs.append(processed)

            logger.info(f"✅ Scraped {len(processed_jobs)} jobs from {company_name}")
            return processed_jobs

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"⚠️ Lever board not found for {company_name}")
            else:
                logger.error(f"❌ HTTP error scraping {company_name}: {e}")
            return []

        except Exception as e:
            logger.error(f"❌ Failed to scrape {company_name}: {e}")
            return []

    def _process_job(self, raw_job: Dict, company_name: str) -> Optional[Dict]:
        """
        Transform Lever job format to our schema

        Args:
            raw_job: Raw job data from Lever API
            company_name: Company name

        Returns:
            Processed job dictionary or None if invalid
        """
        try:
            job_id = raw_job.get("id")
            title = raw_job.get("text", "").strip()

            if not title:
                return None

            # Location parsing
            categories = raw_job.get("categories", {})
            location_name = categories.get("location", "Remote")
            is_remote = "remote" in location_name.lower()

            # Parse location details
            location_city, location_state, location_country = self._parse_location(location_name)

            # Extract description
            description_html = raw_job.get("description", "") or ""
            additional_html = raw_job.get("additionalPlain", "") or raw_job.get("additional", "") or ""
            full_description = f"{description_html}\n\n{additional_html}"
            description = self._clean_html(full_description)

            # Lists section (requirements, responsibilities, etc.)
            lists = raw_job.get("lists", [])
            requirements, responsibilities, benefits = self._extract_from_lists(lists)

            # Determine seniority
            seniority = self._infer_seniority(title)

            # Extract skills
            skills = self._extract_skills(title, description)

            # Infer salary range
            salary_min, salary_max = self._infer_salary_range(title, seniority)

            # Determine experience years
            exp_min, exp_max = self._infer_experience_years(title, seniority, description)

            # Commitment (employment type)
            commitment = categories.get("commitment", "Full-time")
            employment_type = self._map_employment_type(commitment)

            # Apply URL
            apply_url = raw_job.get("applyUrl", "") or raw_job.get("hostedUrl", "")

            # Build job record
            job_record = {
                "external_id": f"lever_{job_id}",
                "title": title,
                "company_name": company_name,
                "seniority": seniority,
                "description": description[:5000],
                "requirements": requirements,
                "responsibilities": responsibilities,
                "benefits": benefits,
                "skills_extracted": skills,
                "location_type": "remote" if is_remote else ("hybrid" if "hybrid" in location_name.lower() else "onsite"),
                "location_city": location_city if not is_remote else None,
                "location_state": location_state if not is_remote else None,
                "location_country": location_country,
                "salary_min": salary_min,
                "salary_max": salary_max,
                "salary_currency": "USD",
                "employment_type": employment_type,
                "experience_years_min": exp_min,
                "experience_years_max": exp_max,
                "apply_url": apply_url,
                "source": f"lever:{company_name.lower().replace(' ', '_')}",
                "posted_at": self._parse_date(raw_job.get("createdAt"))
            }

            return job_record

        except Exception as e:
            logger.error(f"Failed to process job: {e}")
            return None

    def _extract_from_lists(self, lists: List[Dict]) -> tuple:
        """Extract requirements, responsibilities, and benefits from Lever lists"""
        requirements = None
        responsibilities = None
        benefits = None

        for lst in lists:
            text = lst.get("text", "").lower()
            content = lst.get("content", "")

            if not content:
                continue

            # Convert list content to text
            if isinstance(content, str):
                list_text = content
            else:
                list_text = self._clean_html(content)

            if any(keyword in text for keyword in ["requirement", "qualification", "you have"]):
                requirements = list_text[:2000]
            elif any(keyword in text for keyword in ["responsibilit", "you will", "what you'll do"]):
                responsibilities = list_text[:2000]
            elif any(keyword in text for keyword in ["benefit", "we offer", "perks"]):
                benefits = list_text[:1000]

        return (requirements, responsibilities, benefits)

    def _parse_location(self, location_str: str) -> tuple:
        """Parse location string into city, state, country"""
        if not location_str or location_str.lower() == "remote":
            return (None, None, "USA")

        parts = [p.strip() for p in location_str.split(",")]

        if len(parts) >= 3:
            return (parts[0], parts[1], parts[2])
        elif len(parts) == 2:
            # Could be "City, State" or "City, Country"
            if len(parts[1]) == 2:  # Likely state abbreviation
                return (parts[0], parts[1], "USA")
            else:
                return (parts[0], None, parts[1])
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
        skill_patterns = [
            r'\b(Python|Java|JavaScript|TypeScript|Go|Rust|C\+\+|C#|Ruby|PHP|Swift|Kotlin|Scala)\b',
            r'\b(React|Vue|Angular|Next\.js|Django|Flask|FastAPI|Spring|Express|Node\.js)\b',
            r'\b(PostgreSQL|MySQL|MongoDB|Redis|Elasticsearch|DynamoDB|Cassandra)\b',
            r'\b(AWS|Azure|GCP|Google Cloud|Kubernetes|Docker|Terraform)\b',
            r'\b(Git|CI/CD|Jenkins|GitHub Actions|Linux|Bash)\b',
            r'\b(Machine Learning|AI|TensorFlow|PyTorch|NLP|Computer Vision)\b',
        ]

        text = f"{title} {description}"
        skills = set()

        for pattern in skill_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            skills.update(match.title() for match in matches)

        return sorted(list(skills))[:20]

    def _infer_salary_range(self, title: str, seniority: str) -> tuple:
        """Infer salary range based on title and seniority"""
        salary_map = {
            "entry": (70000, 100000),
            "mid": (100000, 140000),
            "senior": (140000, 200000),
            "manager": (150000, 220000)
        }

        title_lower = title.lower()
        base_min, base_max = salary_map.get(seniority, (100000, 140000))

        if "engineer" in title_lower or "developer" in title_lower:
            base_min = int(base_min * 1.1)
            base_max = int(base_max * 1.1)

        if any(word in title_lower for word in ["machine learning", "ai", "data scientist"]):
            base_min = int(base_min * 1.2)
            base_max = int(base_max * 1.2)

        return (base_min, base_max)

    def _infer_experience_years(self, title: str, seniority: str, description: str) -> tuple:
        """Infer required experience years"""
        years_pattern = r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*experience'
        matches = re.findall(years_pattern, description.lower())

        if matches:
            min_years = int(matches[0])
            max_years = min_years + 3
            return (min_years, max_years)

        exp_map = {
            "entry": (0, 2),
            "mid": (2, 5),
            "senior": (5, 10),
            "manager": (7, 15)
        }

        return exp_map.get(seniority, (2, 5))

    def _map_employment_type(self, commitment: str) -> str:
        """Map Lever commitment to our employment type"""
        commitment_lower = commitment.lower()

        if "full" in commitment_lower:
            return "full_time"
        elif "part" in commitment_lower:
            return "part_time"
        elif "contract" in commitment_lower:
            return "contract"
        elif "intern" in commitment_lower:
            return "internship"
        else:
            return "full_time"

    def _clean_html(self, html: str) -> str:
        """Remove HTML tags and clean text"""
        text = re.sub(r'<[^>]+>', '', html)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def _parse_date(self, timestamp: Optional[int]) -> Optional[datetime]:
        """Parse Unix timestamp"""
        if not timestamp:
            return datetime.utcnow()

        try:
            return datetime.fromtimestamp(timestamp / 1000)  # Lever uses milliseconds
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
                return await self.scrape_company(company["name"], company["company_id"])

        tasks = [scrape_with_limit(company) for company in self.LEVER_COMPANIES]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, list):
                all_jobs.extend(result)

        logger.info(f"🎉 Total jobs scraped from Lever: {len(all_jobs)}")
        return all_jobs
