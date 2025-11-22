"""
Job Search Service with Advanced Filtering
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime, timedelta
from loguru import logger

from app.models.database import Job
from pydantic import BaseModel


class JobSearchFilters(BaseModel):
    """Job search filters"""
    query: Optional[str] = None
    location: Optional[str] = None
    remote_only: bool = False
    location_type: Optional[List[str]] = None
    seniority: Optional[List[str]] = None
    employment_type: Optional[List[str]] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    required_skills: Optional[List[str]] = None
    posted_within_days: Optional[int] = None
    sources: Optional[List[str]] = None
    limit: int = 20
    offset: int = 0
    sort_by: str = "posted_at"
    sort_order: str = "desc"


class JobSearchResult(BaseModel):
    """Job search result with metadata"""
    jobs: List[Dict[str, Any]]
    total: int
    offset: int
    limit: int
    filters_applied: Dict[str, Any]
    

class JobSearchService:
    """Service for searching and filtering jobs"""

    @staticmethod
    def search_jobs(db: Session, filters: JobSearchFilters) -> JobSearchResult:
        """Search jobs with comprehensive filtering"""
        try:
            query = db.query(Job).filter(Job.is_active == True)
            conditions = []
            
            # Text search
            if filters.query:
                search_term = f"%{filters.query.lower()}%"
                conditions.append(
                    or_(
                        func.lower(Job.title).like(search_term),
                        func.lower(Job.description).like(search_term)
                    )
                )
            
            # Location filters
            if filters.remote_only:
                conditions.append(Job.location_type == 'remote')
            elif filters.location:
                location_term = f"%{filters.location.lower()}%"
                conditions.append(
                    or_(
                        func.lower(Job.location).like(location_term),
                        func.lower(Job.location_city).like(location_term)
                    )
                )
            
            if filters.location_type:
                conditions.append(Job.location_type.in_(filters.location_type))
            
            if filters.seniority:
                conditions.append(Job.seniority.in_(filters.seniority))
            
            if filters.employment_type:
                conditions.append(Job.employment_type.in_(filters.employment_type))
            
            if filters.salary_min:
                conditions.append(or_(Job.salary_max >= filters.salary_min, Job.salary_min >= filters.salary_min))
            
            if filters.salary_max:
                conditions.append(or_(Job.salary_min <= filters.salary_max, Job.salary_max <= filters.salary_max))
            
            if filters.posted_within_days:
                cutoff_date = datetime.utcnow() - timedelta(days=filters.posted_within_days)
                conditions.append(or_(Job.posted_at >= cutoff_date, Job.created_at >= cutoff_date))
            
            if filters.sources:
                conditions.append(Job.source.in_(filters.sources))
            
            if conditions:
                query = query.filter(and_(*conditions))
            
            total = query.count()
            
            if filters.sort_by == "posted_at":
                sort_col = Job.posted_at
            elif filters.sort_by == "salary_max":
                sort_col = Job.salary_max
            else:
                sort_col = Job.created_at
            
            if filters.sort_order == "desc":
                query = query.order_by(sort_col.desc())
            else:
                query = query.order_by(sort_col.asc())
            
            jobs = query.offset(filters.offset).limit(filters.limit).all()
            
            jobs_data = [
                {
                    'id': str(job.id),
                    'title': job.title,
                    'description': job.description[:500] if job.description else None,
                    'location': job.location,
                    'location_type': job.location_type,
                    'remote_policy': job.remote_policy,
                    'employment_type': job.employment_type,
                    'seniority': job.seniority,
                    'salary_min': job.salary_min,
                    'salary_max': job.salary_max,
                    'salary_currency': job.salary_currency,
                    'required_skills': job.required_skills,
                    'source': job.source,
                    'external_url': job.external_url,
                    'apply_url': job.apply_url,
                    'posted_at': job.posted_at.isoformat() if job.posted_at else None,
                    'company': job.job_metadata.get('company') if job.job_metadata else None,
                }
                for job in jobs
            ]
            
            filters_applied = {
                'query': filters.query,
                'location': filters.location,
                'remote_only': filters.remote_only,
                'seniority': filters.seniority,
            }
            
            return JobSearchResult(
                jobs=jobs_data,
                total=total,
                offset=filters.offset,
                limit=filters.limit,
                filters_applied=filters_applied
            )
            
        except Exception as e:
            logger.error(f"Job search error: {e}")
            raise

    @staticmethod
    def get_job_by_id(db: Session, job_id: str) -> Optional[Dict[str, Any]]:
        """Get full job details by ID"""
        try:
            job = db.query(Job).filter(Job.id == job_id, Job.is_active == True).first()
            
            if not job:
                return None
            
            return {
                'id': str(job.id),
                'title': job.title,
                'description': job.description,
                'location': job.location,
                'location_type': job.location_type,
                'remote_policy': job.remote_policy,
                'employment_type': job.employment_type,
                'seniority': job.seniority,
                'salary_min': job.salary_min,
                'salary_max': job.salary_max,
                'salary_currency': job.salary_currency,
                'required_skills': job.required_skills,
                'source': job.source,
                'external_url': job.external_url,
                'apply_url': job.apply_url,
                'posted_at': job.posted_at.isoformat() if job.posted_at else None,
                'job_metadata': job.job_metadata
            }
            
        except Exception as e:
            logger.error(f"Get job by ID error: {e}")
            return None

    @staticmethod
    def get_filter_options(db: Session) -> Dict[str, Any]:
        """Get available filter options from existing jobs"""
        try:
            location_types = db.query(Job.location_type).distinct().filter(Job.location_type.isnot(None)).all()
            seniorities = db.query(Job.seniority).distinct().filter(Job.seniority.isnot(None)).all()
            employment_types = db.query(Job.employment_type).distinct().filter(Job.employment_type.isnot(None)).all()
            sources = db.query(Job.source).distinct().filter(Job.source.isnot(None)).all()
            
            salary_stats = db.query(
                func.min(Job.salary_min).label('min_salary'),
                func.max(Job.salary_max).label('max_salary')
            ).first()
            
            return {
                'location_types': [lt[0] for lt in location_types if lt[0]],
                'seniorities': [s[0] for s in seniorities if s[0]],
                'employment_types': [et[0] for et in employment_types if et[0]],
                'sources': [src[0] for src in sources if src[0]],
                'salary_range': {
                    'min': salary_stats.min_salary if salary_stats else 0,
                    'max': salary_stats.max_salary if salary_stats else 200000
                }
            }
            
        except Exception as e:
            logger.error(f"Get filter options error: {e}")
            return {}


job_search_service = JobSearchService()
