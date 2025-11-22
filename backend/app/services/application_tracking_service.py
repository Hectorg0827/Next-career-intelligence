"""
Application Tracking Service
Manages job applications, status updates, and interview tracking
"""

from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from loguru import logger
from datetime import datetime, timedelta
import uuid

from app.models.database import JobApplication, Job, User


class ApplicationTrackingService:
    """Service for tracking job applications throughout the hiring process"""

    APPLICATION_STATUSES = [
        "saved",        # Bookmarked for later
        "applied",      # Application submitted
        "screening",    # Under review
        "interview",    # Interview scheduled/completed
        "assessment",   # Take-home test or assessment
        "offer",        # Offer received
        "accepted",     # Offer accepted
        "rejected",     # Application rejected
        "withdrawn"     # User withdrew application
    ]

    def create_application(
        self,
        db: Session,
        user_id: str,
        job_id: str,
        status: str = "applied",
        match_score: Optional[float] = None,
        skill_gaps: Optional[Dict] = None,
        notes: Optional[str] = None
    ) -> JobApplication:
        """Create a new job application record"""
        
        # Verify job exists
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        # Check for duplicate
        existing = db.query(JobApplication).filter(
            and_(
                JobApplication.user_id == user_id,
                JobApplication.job_id == job_id
            )
        ).first()
        
        if existing:
            logger.warning(f"Application already exists for user {user_id} and job {job_id}")
            return existing
        
        # Create application
        application = JobApplication(
            id=uuid.uuid4(),
            user_id=user_id,
            job_id=job_id,
            status=status,
            match_score=match_score,
            skill_gaps=skill_gaps,
            interview_notes=notes,
            applied_at=datetime.utcnow(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(application)
        db.commit()
        db.refresh(application)
        
        logger.info(f"Created application {application.id} for user {user_id}")
        return application

    def update_application_status(
        self,
        db: Session,
        application_id: str,
        user_id: str,
        status: str,
        notes: Optional[str] = None,
        interview_date: Optional[datetime] = None,
        offer_details: Optional[Dict] = None
    ) -> JobApplication:
        """Update application status and related information"""
        
        if status not in self.APPLICATION_STATUSES:
            raise ValueError(f"Invalid status: {status}")
        
        application = db.query(JobApplication).filter(
            and_(
                JobApplication.id == application_id,
                JobApplication.user_id == user_id
            )
        ).first()
        
        if not application:
            raise ValueError(f"Application {application_id} not found")
        
        # Update status
        application.status = status
        application.updated_at = datetime.utcnow()
        
        # Update interview info
        if interview_date:
            application.interview_date = interview_date
        
        if notes:
            existing_notes = application.interview_notes or ""
            timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
            application.interview_notes = f"{existing_notes}\n\n[{timestamp}] {notes}" if existing_notes else notes
        
        # Update offer details
        if offer_details:
            application.offer_salary = offer_details.get("salary")
            application.offer_status = offer_details.get("status", "pending")
        
        # Set rejection reason if status is rejected
        if status == "rejected" and notes:
            application.rejection_reason = notes
        
        db.commit()
        db.refresh(application)
        
        logger.info(f"Updated application {application_id} status to {status}")
        return application

    def get_user_applications(
        self,
        db: Session,
        user_id: str,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict:
        """Get all applications for a user with optional status filter"""
        
        query = db.query(JobApplication, Job).join(
            Job, JobApplication.job_id == Job.id
        ).filter(JobApplication.user_id == user_id)
        
        # Filter by status
        if status:
            query = query.filter(JobApplication.status == status)
        
        # Get total count
        total = query.count()
        
        # Get paginated results
        applications = query.order_by(
            JobApplication.updated_at.desc()
        ).offset(offset).limit(limit).all()
        
        result = []
        for app, job in applications:
            result.append({
                "application": {
                    "id": str(app.id),
                    "status": app.status,
                    "match_score": app.match_score,
                    "applied_at": app.applied_at.isoformat() if app.applied_at else None,
                    "updated_at": app.updated_at.isoformat() if app.updated_at else None,
                    "interview_date": app.interview_date.isoformat() if app.interview_date else None,
                    "interview_notes": app.interview_notes,
                    "offer_salary": app.offer_salary,
                    "offer_status": app.offer_status,
                    "rejection_reason": app.rejection_reason,
                },
                "job": {
                    "id": str(job.id),
                    "title": job.title,
                    "company": job.company_id,
                    "location": job.location,
                    "location_type": job.location_type,
                    "salary_min": job.salary_min,
                    "salary_max": job.salary_max,
                    "external_url": job.external_url,
                    "apply_url": job.apply_url,
                }
            })
        
        return {
            "applications": result,
            "total": total,
            "offset": offset,
            "limit": limit
        }

    def get_application_by_id(
        self,
        db: Session,
        application_id: str,
        user_id: str
    ) -> Optional[Dict]:
        """Get detailed application information"""
        
        result = db.query(JobApplication, Job).join(
            Job, JobApplication.job_id == Job.id
        ).filter(
            and_(
                JobApplication.id == application_id,
                JobApplication.user_id == user_id
            )
        ).first()
        
        if not result:
            return None
        
        app, job = result
        
        return {
            "application": {
                "id": str(app.id),
                "status": app.status,
                "match_score": app.match_score,
                "skill_gaps": app.skill_gaps,
                "recommended_prep": app.recommended_prep,
                "applied_at": app.applied_at.isoformat() if app.applied_at else None,
                "updated_at": app.updated_at.isoformat() if app.updated_at else None,
                "interview_date": app.interview_date.isoformat() if app.interview_date else None,
                "interview_notes": app.interview_notes,
                "offer_salary": app.offer_salary,
                "offer_status": app.offer_status,
                "rejection_reason": app.rejection_reason,
            },
            "job": {
                "id": str(job.id),
                "title": job.title,
                "description": job.description,
                "company": job.company_id,
                "location": job.location,
                "location_type": job.location_type,
                "remote_policy": job.remote_policy,
                "employment_type": job.employment_type,
                "seniority": job.seniority,
                "salary_min": job.salary_min,
                "salary_max": job.salary_max,
                "salary_currency": job.salary_currency,
                "required_skills": job.required_skills,
                "benefits": job.benefits,
                "requirements": job.requirements,
                "responsibilities": job.responsibilities,
                "external_url": job.external_url,
                "apply_url": job.apply_url,
                "posted_at": job.posted_at.isoformat() if job.posted_at else None,
            }
        }

    def get_application_stats(
        self,
        db: Session,
        user_id: str
    ) -> Dict:
        """Get application statistics for dashboard"""
        
        # Total applications
        total = db.query(JobApplication).filter(
            JobApplication.user_id == user_id
        ).count()
        
        # Count by status
        status_counts = {}
        for status in self.APPLICATION_STATUSES:
            count = db.query(JobApplication).filter(
                and_(
                    JobApplication.user_id == user_id,
                    JobApplication.status == status
                )
            ).count()
            status_counts[status] = count
        
        # Active applications (not rejected/withdrawn/accepted)
        active_count = db.query(JobApplication).filter(
            and_(
                JobApplication.user_id == user_id,
                JobApplication.status.in_(["applied", "screening", "interview", "assessment", "offer"])
            )
        ).count()
        
        # Upcoming interviews
        upcoming_interviews = db.query(JobApplication, Job).join(
            Job, JobApplication.job_id == Job.id
        ).filter(
            and_(
                JobApplication.user_id == user_id,
                JobApplication.interview_date >= datetime.utcnow(),
                JobApplication.interview_date <= datetime.utcnow() + timedelta(days=14)
            )
        ).order_by(JobApplication.interview_date.asc()).all()
        
        interview_list = []
        for app, job in upcoming_interviews:
            interview_list.append({
                "application_id": str(app.id),
                "job_title": job.title,
                "company": job.company_id,
                "interview_date": app.interview_date.isoformat(),
                "status": app.status
            })
        
        # Recent activity (last 7 days)
        recent_activity = db.query(JobApplication).filter(
            and_(
                JobApplication.user_id == user_id,
                JobApplication.updated_at >= datetime.utcnow() - timedelta(days=7)
            )
        ).count()
        
        # Response rate (applications that moved past "applied" status)
        moved_forward = db.query(JobApplication).filter(
            and_(
                JobApplication.user_id == user_id,
                JobApplication.status.in_(["screening", "interview", "assessment", "offer", "accepted"])
            )
        ).count()
        
        response_rate = (moved_forward / total * 100) if total > 0 else 0
        
        return {
            "total_applications": total,
            "active_applications": active_count,
            "status_breakdown": status_counts,
            "upcoming_interviews": interview_list,
            "recent_activity_count": recent_activity,
            "response_rate": round(response_rate, 1)
        }

    def delete_application(
        self,
        db: Session,
        application_id: str,
        user_id: str
    ) -> bool:
        """Delete an application"""
        
        application = db.query(JobApplication).filter(
            and_(
                JobApplication.id == application_id,
                JobApplication.user_id == user_id
            )
        ).first()
        
        if not application:
            return False
        
        db.delete(application)
        db.commit()
        
        logger.info(f"Deleted application {application_id}")
        return True
