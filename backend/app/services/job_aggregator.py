"""
Job Aggregator Service
Orchestrates fetching jobs from multiple sources, normalizing them, and ensuring quality.
"""

import asyncio
import httpx
import logging
try:
    import feedparser
except ImportError:
    feedparser = None
from typing import List, Dict, Any, Optional
from datetime import datetime
from abc import ABC, abstractmethod
import re
from urllib.parse import urlparse

from app.services.job_data_quality import JobDataValidator
from app.models.database import Job

logger = logging.getLogger(__name__)

class JobFetcher(ABC):
    """Abstract base class for job fetchers"""
    
    def __init__(self, source_name: str):
        self.source_name = source_name
        self.client = httpx.AsyncClient(timeout=30.0)

    async def close(self):
        await self.client.aclose()

    @abstractmethod
    async def fetch_jobs(self) -> List[Dict[str, Any]]:
        """Fetch jobs and return raw data"""
        pass

    @abstractmethod
    def normalize_job(self, raw_job: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Convert raw job data to our schema"""
        pass

class RemoteOKFetcher(JobFetcher):
    """Fetcher for RemoteOK.io"""
    
    def __init__(self):
        super().__init__("remoteok")
        self.url = "https://remoteok.com/api"

    async def fetch_jobs(self) -> List[Dict[str, Any]]:
        try:
            response = await self.client.get(self.url)
            response.raise_for_status()
            data = response.json()
            # First element is legal text, skip it
            return data[1:] if len(data) > 0 else []
        except Exception as e:
            logger.error(f"Failed to fetch from RemoteOK: {e}")
            return []

    def normalize_job(self, raw_job: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            return {
                "title": raw_job.get("position"),
                "company": raw_job.get("company"),
                "description": raw_job.get("description"),
                "location": raw_job.get("location", "Remote"),
                "remote_policy": "remote",
                "employment_type": "full_time",  # Default assumption
                "salary_min": raw_job.get("salary_min"),
                "salary_max": raw_job.get("salary_max"),
                "salary_currency": "USD",
                "required_skills": raw_job.get("tags", []),
                "source": self.source_name,
                "external_id": str(raw_job.get("id")),
                "external_url": raw_job.get("url"),
                "apply_url": raw_job.get("apply_url") or raw_job.get("url"),
                "posted_at": datetime.fromisoformat(raw_job.get("date").replace("Z", "+00:00")) if raw_job.get("date") else datetime.utcnow(),
                "is_active": True
            }
        except Exception as e:
            logger.warning(f"Error normalizing RemoteOK job: {e}")
            return None

class WeWorkRemotelyFetcher(JobFetcher):
    """Fetcher for WeWorkRemotely RSS"""
    
    def __init__(self):
        super().__init__("weworkremotely")
        self.url = "https://weworkremotely.com/categories/remote-programming-jobs.rss"

    async def fetch_jobs(self) -> List[Dict[str, Any]]:
        if not feedparser:
            logger.warning("feedparser not installed, skipping WeWorkRemotely")
            return []

        try:
            response = await self.client.get(self.url)
            response.raise_for_status()
            feed = feedparser.parse(response.text)
            return feed.entries
        except Exception as e:
            logger.error(f"Failed to fetch from WeWorkRemotely: {e}")
            return []

    def normalize_job(self, raw_job: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            # Extract company from title "Title: Company" or similar if needed, 
            # but WWR usually has 'company' field in RSS extension or we parse title
            # WWR RSS entries usually have 'title', 'link', 'description', 'published'
            
            # Title format often: "Role: Company" or just "Role"
            title = raw_job.get("title", "")
            company = "Unknown"
            if ":" in title:
                parts = title.split(":")
                company = parts[0].strip()
                title = ":".join(parts[1:]).strip()
            
            return {
                "title": title,
                "company": company,
                "description": raw_job.get("summary", "") or raw_job.get("description", ""),
                "location": "Remote",
                "remote_policy": "remote",
                "employment_type": "full_time",
                "source": self.source_name,
                "external_id": raw_job.get("id") or raw_job.get("link"),
                "external_url": raw_job.get("link"),
                "apply_url": raw_job.get("link"),
                "posted_at": datetime(*raw_job.published_parsed[:6]) if raw_job.get("published_parsed") else datetime.utcnow(),
                "is_active": True
            }
        except Exception as e:
            logger.warning(f"Error normalizing WWR job: {e}")
            return None

class ArbeitnowFetcher(JobFetcher):
    """Fetcher for Arbeitnow API"""
    
    def __init__(self):
        super().__init__("arbeitnow")
        self.url = "https://arbeitnow.com/api/job-board-api"

    async def fetch_jobs(self) -> List[Dict[str, Any]]:
        try:
            response = await self.client.get(self.url)
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
        except Exception as e:
            logger.error(f"Failed to fetch from Arbeitnow: {e}")
            return []

    def normalize_job(self, raw_job: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            return {
                "title": raw_job.get("title"),
                "company": raw_job.get("company_name"),
                "description": raw_job.get("description"),
                "location": raw_job.get("location"),
                "remote_policy": "remote" if raw_job.get("remote") else "on_site",
                "employment_type": "full_time", # API doesn't always specify
                "required_skills": raw_job.get("tags", []),
                "source": self.source_name,
                "external_id": raw_job.get("slug"),
                "external_url": raw_job.get("url"),
                "apply_url": raw_job.get("url"),
                "posted_at": datetime.fromtimestamp(raw_job.get("created_at")) if raw_job.get("created_at") else datetime.utcnow(),
                "is_active": True
            }
        except Exception as e:
            logger.warning(f"Error normalizing Arbeitnow job: {e}")
            return None

class JobicyFetcher(JobFetcher):
    """Fetcher for Jobicy API"""
    
    def __init__(self):
        super().__init__("jobicy")
        self.url = "https://jobicy.com/api/v2/remote-jobs"

    async def fetch_jobs(self) -> List[Dict[str, Any]]:
        try:
            response = await self.client.get(self.url)
            response.raise_for_status()
            data = response.json()
            return data.get("jobs", [])
        except Exception as e:
            logger.error(f"Failed to fetch from Jobicy: {e}")
            return []

    def normalize_job(self, raw_job: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            return {
                "title": raw_job.get("jobTitle"),
                "company": raw_job.get("companyName"),
                "description": raw_job.get("jobDescription"),
                "location": "Remote", # Jobicy is remote-focused
                "remote_policy": "remote",
                "employment_type": raw_job.get("jobType", "full_time").lower().replace("-", "_"),
                "salary_min": raw_job.get("annualSalaryMin"),
                "salary_max": raw_job.get("annualSalaryMax"),
                "salary_currency": raw_job.get("salaryCurrency", "USD"),
                "required_skills": raw_job.get("jobTags", []),
                "source": self.source_name,
                "external_id": str(raw_job.get("id")),
                "external_url": raw_job.get("url"),
                "apply_url": raw_job.get("applyUrl") or raw_job.get("url"),
                "posted_at": datetime.fromisoformat(raw_job.get("pubDate").replace("Z", "+00:00")) if raw_job.get("pubDate") else datetime.utcnow(),
                "is_active": True
            }
        except Exception as e:
            logger.warning(f"Error normalizing Jobicy job: {e}")
            return None

class RemotiveFetcher(JobFetcher):
    """Fetcher for Remotive.com API"""
    
    def __init__(self):
        super().__init__("remotive")
        self.url = "https://remotive.com/api/remote-jobs"

    async def fetch_jobs(self) -> List[Dict[str, Any]]:
        try:
            # Limit to software dev category to be relevant
            response = await self.client.get(f"{self.url}?category=software-dev")
            response.raise_for_status()
            data = response.json()
            return data.get("jobs", [])
        except Exception as e:
            logger.error(f"Failed to fetch from Remotive: {e}")
            return []

    def normalize_job(self, raw_job: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            return {
                "title": raw_job.get("title"),
                "company": raw_job.get("company_name"),
                "description": raw_job.get("description"),
                "location": raw_job.get("candidate_required_location", "Remote"),
                "remote_policy": "remote",
                "employment_type": raw_job.get("job_type", "full_time").replace("-", "_"),
                "salary_min": None, # Remotive salary is a string, hard to parse reliably without NLP
                "salary_max": None,
                "salary_currency": "USD",
                "required_skills": raw_job.get("tags", []),
                "source": self.source_name,
                "external_id": str(raw_job.get("id")),
                "external_url": raw_job.get("url"),
                "apply_url": raw_job.get("url"),
                "posted_at": datetime.fromisoformat(raw_job.get("publication_date")) if raw_job.get("publication_date") else datetime.utcnow(),
                "is_active": True
            }
        except Exception as e:
            logger.warning(f"Error normalizing Remotive job: {e}")
            return None

class JobAggregatorService:
    """Service to aggregate jobs from multiple sources"""

    def __init__(self):
        self.fetchers: List[JobFetcher] = [
            RemoteOKFetcher(),
            WeWorkRemotelyFetcher(),
            ArbeitnowFetcher(),
            JobicyFetcher(),
            RemotiveFetcher()
        ]

    async def fetch_all_jobs(self) -> List[Dict[str, Any]]:
        """Fetch jobs from all configured sources"""
        all_jobs = []
        
        for fetcher in self.fetchers:
            logger.info(f"Fetching from {fetcher.source_name}...")
            raw_jobs = await fetcher.fetch_jobs()
            logger.info(f"Fetched {len(raw_jobs)} raw jobs from {fetcher.source_name}")
            
            for raw_job in raw_jobs:
                normalized_job = fetcher.normalize_job(raw_job)
                if normalized_job:
                    # Basic validation before adding
                    if normalized_job.get("title") and normalized_job.get("company"):
                        all_jobs.append(normalized_job)
            
            await fetcher.close()
            
        return all_jobs

    async def close(self):
        for fetcher in self.fetchers:
            await fetcher.close()

    async def run_scrape_and_store(self) -> Dict[str, int]:
        """Run full scrape and store in DB"""
        from app.services.job_data_quality import JobDataQualityPipeline
        from app.db.supabase import get_supabase_client
        
        pipeline = JobDataQualityPipeline()
        client = get_supabase_client()
        stats = {"scraped": 0, "inserted": 0, "updated": 0, "errors": 0, "skipped": 0}
        
        try:
            jobs = await self.fetch_all_jobs()
            stats["scraped"] = len(jobs)
            
            for job_data in jobs:
                try:
                    # Validate
                    is_valid, validated_data, errors = pipeline.validate_job_data(job_data)
                    if not is_valid:
                        stats["skipped"] += 1
                        continue
                    
                    # Enrich
                    enriched_data = pipeline.enrich_job_data(validated_data)
                    
                    # Insert/Update
                    external_id = enriched_data.get("external_id")
                    source = enriched_data.get("source")
                    
                    existing = client.table("jobs").select("id").eq("external_id", external_id).eq("source", source).execute()
                    
                    if existing.data:
                        # Update
                        if "id" in enriched_data:
                            del enriched_data["id"]
                        client.table("jobs").update(enriched_data).eq("id", existing.data[0]["id"]).execute()
                        stats["updated"] += 1
                    else:
                        # Insert
                        client.table("jobs").insert(enriched_data).execute()
                        stats["inserted"] += 1
                        
                except Exception as e:
                    logger.error(f"Error processing job {job_data.get('title')}: {e}")
                    stats["errors"] += 1
                    
            logger.info(f"✅ Aggregated scrape complete: {stats}")
            
            # Refresh match scores
            try:
                logger.info("🔄 Refreshing job match scores...")
                client.rpc("refresh_job_match_scores", {}).execute()
                logger.info("✅ Match scores refreshed")
            except Exception as e:
                logger.error(f"Failed to refresh match scores: {e}")

            return stats
            
        except Exception as e:
            logger.error(f"Aggregated scrape failed: {e}")
            raise
