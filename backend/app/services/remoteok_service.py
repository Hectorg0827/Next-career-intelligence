"""RemoteOK API integration service.

Fetches remote job listings from RemoteOK.com API and seeds them into the database.
RemoteOK API: https://remoteok.com/api
"""

import httpx
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import re

from app.models.database import Job

logger = logging.getLogger(__name__)

REMOTEOK_API = "https://remoteok.com/api"


class RemoteOKService:
    """Service for fetching and managing RemoteOK jobs."""

    def __init__(self):
        self.headers = {
            "User-Agent": "Next-Career-Intelligence/1.0 (Career Platform)",
            "Accept": "application/json"
        }

    @staticmethod
    def extract_skills(tags: List[str]) -> List[str]:
        """Extract and normalize skills from job tags."""
        if not tags:
            return []
        
        skill_keywords = {
            'python', 'javascript', 'typescript', 'java', 'react', 'vue', 
            'angular', 'node', 'nodejs', 'golang', 'go', 'rust', 'ruby',
            'php', 'swift', 'kotlin', 'c++', 'csharp', 'sql', 'nosql',
            'mongodb', 'postgresql', 'mysql', 'redis', 'docker', 'kubernetes',
            'aws', 'azure', 'gcp', 'devops', 'frontend', 'backend', 'fullstack',
            'mobile', 'ios', 'android', 'machine learning', 'ai', 'data science',
            'django', 'flask', 'fastapi', 'express', 'spring', 'laravel'
        }
        
        skills = []
        for tag in tags:
            tag_lower = tag.lower().strip()
            if tag_lower in skill_keywords or len(tag_lower) <= 20:
                skills.append(tag)
        
        return skills[:15]

    @staticmethod
    def extract_salary(salary_text: Optional[str]) -> tuple[Optional[int], Optional[int]]:
        """Extract min and max salary from salary text."""
        if not salary_text:
            return None, None
        
        pattern = r'\$?(\d+)[,k]?\s*[-–]\s*\$?(\d+)[,k]?'
        match = re.search(pattern, salary_text, re.IGNORECASE)
        
        if match:
            min_sal = int(match.group(1))
            max_sal = int(match.group(2))
            
            if 'k' in salary_text.lower():
                min_sal *= 1000
                max_sal *= 1000
            
            return min_sal, max_sal
        
        pattern = r'\$?(\d+)[,k]?'
        match = re.search(pattern, salary_text, re.IGNORECASE)
        
        if match:
            salary = int(match.group(1))
            if 'k' in salary_text.lower():
                salary *= 1000
            
            return int(salary * 0.8), int(salary * 1.2)
        
        return None, None

    @staticmethod
    def extract_experience_level(description: str, tags: List[str]) -> Optional[str]:
        """Extract experience level from job description and tags."""
        text = (description + " " + " ".join(tags)).lower()
        
        if any(word in text for word in ['senior', 'lead', 'principal', 'architect', 'staff']):
            return 'senior'
        elif any(word in text for word in ['junior', 'entry', 'graduate', 'intern']):
            return 'entry'
        elif any(word in text for word in ['mid', 'intermediate', '3-5 years', '2-4 years']):
            return 'mid'
        
        return 'mid'

    async def fetch_jobs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch jobs from RemoteOK API."""
        try:
            logger.info(f"Fetching up to {limit} jobs from RemoteOK...")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    REMOTEOK_API,
                    headers=self.headers,
                    follow_redirects=True
                )
                
                response.raise_for_status()
                data = response.json()
                
                jobs = []
                for item in data[1:limit+1]:
                    if not isinstance(item, dict):
                        continue
                    
                    job = self._parse_job(item)
                    if job:
                        jobs.append(job)
                
                logger.info(f"Successfully fetched {len(jobs)} jobs from RemoteOK")
                return jobs
                
        except Exception as e:
            logger.error(f"Error fetching jobs from RemoteOK: {e}")
            return []

    def _parse_job(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse a single job item from RemoteOK API response."""
        try:
            job_id = item.get('id')
            title = item.get('position')
            company = item.get('company')
            description = item.get('description', '')
            
            if not all([job_id, title, company]):
                return None
            
            tags = item.get('tags', [])
            salary_text = item.get('salary', '')
            salary_min, salary_max = self.extract_salary(salary_text)
            
            job = {
                'external_id': str(job_id),
                'source': 'remoteok',
                'title': title,
                'description': description[:5000],
                'location': item.get('location', 'Remote'),
                'location_type': 'remote',
                'remote_policy': 'remote',
                'employment_type': 'full_time',
                'salary_min': salary_min,
                'salary_max': salary_max,
                'salary_currency': 'USD',
                'required_skills': self.extract_skills(tags),
                'seniority': self.extract_experience_level(description, tags),
                'external_url': item.get('url', f"https://remoteok.com/remote-jobs/{job_id}"),
                'apply_url': item.get('apply_url', item.get('url')),
                'posted_at': self._parse_date(item.get('date')),
                'is_active': True,
                'job_metadata': {
                    'tags': tags,
                    'company': company,
                    'company_logo': item.get('company_logo'),
                    'epoch': item.get('epoch')
                }
            }
            
            return job
            
        except Exception as e:
            logger.error(f"Error parsing job: {e}")
            return None

    @staticmethod
    def _parse_date(date_value: Any) -> Optional[datetime]:
        """Parse date from RemoteOK format."""
        if not date_value:
            return None
        
        try:
            if isinstance(date_value, (int, float)):
                return datetime.fromtimestamp(date_value)
            
            if isinstance(date_value, str):
                return datetime.fromisoformat(date_value.replace('Z', '+00:00'))
            
        except Exception as e:
            logger.warning(f"Could not parse date: {date_value}, error: {e}")
        
        return datetime.utcnow()

    async def seed_jobs_to_db(self, db: Session, limit: int = 50, replace_existing: bool = False) -> int:
        """Fetch jobs from RemoteOK and seed them into the database."""
        try:
            jobs = await self.fetch_jobs(limit=limit)
            
            if not jobs:
                logger.warning("No jobs fetched from RemoteOK")
                return 0
            
            if replace_existing:
                deleted = db.query(Job).filter(Job.source == 'remoteok').delete()
                db.commit()
                logger.info(f"Deleted {deleted} existing RemoteOK jobs")
            
            seeded_count = 0
            for job_data in jobs:
                try:
                    existing = db.query(Job).filter(
                        Job.external_id == job_data['external_id'],
                        Job.source == 'remoteok'
                    ).first()
                    
                    if existing:
                        for key, value in job_data.items():
                            setattr(existing, key, value)
                        existing.updated_at = datetime.utcnow()
                        logger.debug(f"Updated job: {job_data['title']}")
                    else:
                        job = Job(**job_data)
                        db.add(job)
                        logger.debug(f"Added job: {job_data['title']}")
                    
                    seeded_count += 1
                    
                except IntegrityError:
                    db.rollback()
                    logger.warning(f"Duplicate job skipped: {job_data.get('title')}")
                    continue
                except Exception as e:
                    db.rollback()
                    logger.error(f"Error seeding job: {e}")
                    continue
            
            db.commit()
            logger.info(f"Successfully seeded {seeded_count} jobs from RemoteOK")
            
            return seeded_count
            
        except Exception as e:
            logger.error(f"Error in seed_jobs_to_db: {e}")
            db.rollback()
            return 0
