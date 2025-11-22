"""
Real-time Job Recommendation Engine
Continuously matches users with new jobs and sends notifications
"""

from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from loguru import logger
from datetime import datetime, timedelta
import asyncio

from app.models.database import Job, User, SavedJob, JobApplication, JobAlertPreferences
from app.services.job_matcher_service import JobMatcherService
from app.services.email_notification_service import EmailNotificationService


class JobRecommendationEngine:
    """Service for real-time job recommendations and alerts"""

    def __init__(self):
        self.matcher = JobMatcherService()
        self.email_service = EmailNotificationService()

    async def get_user_preferences(
        self,
        db: Session,
        user_id: str
    ) -> Dict:
        """Get user's job alert preferences"""
        
        prefs = db.query(JobAlertPreferences).filter(
            JobAlertPreferences.user_id == user_id
        ).first()
        
        if not prefs:
            # Return default preferences
            return {
                "min_match_score": 50.0,
                "email_alerts_enabled": True,
                "alert_frequency": "daily",
                "job_title_keywords": [],
                "locations": [],
                "remote_types": ["remote"],
                "min_salary": None,
                "experience_levels": [],
                "required_skills": [],
                "excluded_keywords": []
            }
        
        return {
            "min_match_score": prefs.min_match_score or 50.0,
            "email_alerts_enabled": prefs.email_alerts_enabled == "true",
            "alert_frequency": prefs.alert_frequency or "daily",
            "job_title_keywords": prefs.job_title_keywords or [],
            "locations": prefs.locations or [],
            "remote_types": prefs.remote_types or [],
            "min_salary": prefs.min_salary,
            "experience_levels": prefs.experience_levels or [],
            "required_skills": prefs.required_skills or [],
            "excluded_keywords": prefs.excluded_keywords or []
        }

    async def filter_jobs_by_preferences(
        self,
        db: Session,
        jobs: List[Job],
        preferences: Dict
    ) -> List[Job]:
        """Filter jobs based on user preferences"""
        
        filtered = []
        
        for job in jobs:
            # Check excluded keywords
            excluded = preferences.get("excluded_keywords", [])
            if excluded:
                job_text = f"{job.title} {job.description}".lower()
                if any(keyword.lower() in job_text for keyword in excluded):
                    continue
            
            # Check job title keywords
            title_keywords = preferences.get("job_title_keywords", [])
            if title_keywords:
                if not any(keyword.lower() in job.title.lower() for keyword in title_keywords):
                    continue
            
            # Check location/remote type
            remote_types = preferences.get("remote_types", [])
            if remote_types:
                if job.location_type not in remote_types:
                    continue
            
            # Check salary
            min_salary = preferences.get("min_salary")
            if min_salary:
                if not job.salary_max or job.salary_max < min_salary:
                    continue
            
            filtered.append(job)
        
        return filtered

    async def get_new_job_recommendations(
        self,
        db: Session,
        user_id: str,
        hours_since: int = 24
    ) -> List[Dict]:
        """
        Get new job recommendations for a user
        
        Args:
            user_id: User ID
            hours_since: Check for jobs posted in last N hours
        
        Returns:
            List of job recommendations with match scores
        """
        logger.info(f"Getting new recommendations for user {user_id} (last {hours_since} hours)")
        
        # Get user preferences
        preferences = await self.get_user_preferences(db, user_id)
        
        # Get jobs posted in the last N hours
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_since)
        new_jobs = db.query(Job).filter(
            and_(
                Job.is_active == True,
                Job.posted_at >= cutoff_time
            )
        ).all()
        
        if not new_jobs:
            logger.info(f"No new jobs found in last {hours_since} hours")
            return []
        
        logger.info(f"Found {len(new_jobs)} new jobs to evaluate")
        
        # Filter by user preferences
        filtered_jobs = await self.filter_jobs_by_preferences(db, new_jobs, preferences)
        
        if not filtered_jobs:
            logger.info("No jobs matched user preferences")
            return []
        
        logger.info(f"After preference filtering: {len(filtered_jobs)} jobs")
        
        # Calculate match scores
        recommendations = []
        min_score = preferences.get("min_match_score", 50.0)
        
        for job in filtered_jobs:
            try:
                match_data = await self.matcher.calculate_match_score(db, user_id, job)
                
                if match_data["overall_score"] >= min_score:
                    recommendations.append({
                        "job": {
                            "id": str(job.id),
                            "title": job.title,
                            "company": job.company_id,
                            "location": job.location,
                            "location_type": job.location_type,
                            "salary_min": job.salary_min,
                            "salary_max": job.salary_max,
                            "posted_at": job.posted_at.isoformat() if job.posted_at else None,
                            "external_url": job.external_url,
                            "apply_url": job.apply_url,
                        },
                        "match": match_data,
                        "is_new": True,
                        "discovered_at": datetime.utcnow().isoformat()
                    })
            except Exception as e:
                logger.error(f"Error calculating match for job {job.id}: {e}")
                continue
        
        # Sort by match score
        recommendations.sort(key=lambda x: x["match"]["overall_score"], reverse=True)
        
        logger.info(f"Found {len(recommendations)} qualifying recommendations (>= {min_score}% match)")
        
        return recommendations

    async def send_job_alert_email(
        self,
        db: Session,
        user_id: str,
        recommendations: List[Dict]
    ) -> bool:
        """Send email notification about new job matches"""
        
        # Get user info
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.email:
            logger.warning(f"User {user_id} not found or has no email")
            return False
        
        # Get user preferences
        preferences = await self.get_user_preferences(db, user_id)
        if not preferences.get("email_alerts_enabled", True):
            logger.info(f"Email alerts disabled for user {user_id}")
            return False
        
        # Send email for top match
        if recommendations:
            top_match = recommendations[0]
            job = top_match["job"]
            match = top_match["match"]
            
            user_name = user.first_name or user.email.split("@")[0]
            
            success = self.email_service.send_job_match_notification(
                to_email=user.email,
                user_name=user_name,
                job_title=job["title"],
                company=job.get("company") or "Company",
                match_score=match["overall_score"],
                job_url=f"https://app.careercopilot.ai/jobs/{job['id']}"
            )
            
            return success
        
        return False

    async def process_user_recommendations(
        self,
        db: Session,
        user_id: str,
        send_email: bool = True
    ) -> Dict:
        """
        Process recommendations for a single user
        
        Returns:
            {
                "user_id": str,
                "new_recommendations": int,
                "email_sent": bool
            }
        """
        try:
            # Check user preferences for alert frequency
            preferences = await self.get_user_preferences(db, user_id)
            alert_frequency = preferences.get("alert_frequency", "daily")
            
            # Determine time window based on frequency
            hours_map = {
                "instant": 1,
                "daily": 24,
                "weekly": 168
            }
            hours_since = hours_map.get(alert_frequency, 24)
            
            # Get recommendations
            recommendations = await self.get_new_job_recommendations(
                db, user_id, hours_since=hours_since
            )
            
            email_sent = False
            if send_email and recommendations:
                email_sent = await self.send_job_alert_email(
                    db, user_id, recommendations
                )
            
            return {
                "user_id": user_id,
                "new_recommendations": len(recommendations),
                "email_sent": email_sent,
                "top_matches": recommendations[:5]  # Top 5
            }
            
        except Exception as e:
            logger.error(f"Error processing recommendations for user {user_id}: {e}")
            return {
                "user_id": user_id,
                "new_recommendations": 0,
                "email_sent": False,
                "error": str(e)
            }

    async def run_recommendation_batch(
        self,
        db: Session,
        user_ids: Optional[List[str]] = None,
        send_emails: bool = True
    ) -> Dict:
        """
        Run recommendation engine for multiple users
        
        Args:
            user_ids: List of user IDs to process (None = all active users)
            send_emails: Whether to send email notifications
        
        Returns:
            Summary statistics
        """
        logger.info("Starting recommendation batch processing")
        
        # Get users to process
        if not user_ids:
            users = db.query(User).filter(
                and_(
                    User.is_active == True,
                    User.email.isnot(None)
                )
            ).all()
            user_ids = [user.id for user in users]
        
        logger.info(f"Processing recommendations for {len(user_ids)} users")
        
        results = {
            "total_users": len(user_ids),
            "successful": 0,
            "failed": 0,
            "total_recommendations": 0,
            "emails_sent": 0,
            "users_with_matches": 0
        }
        
        for user_id in user_ids:
            try:
                result = await self.process_user_recommendations(
                    db, user_id, send_email=send_emails
                )
                
                results["successful"] += 1
                results["total_recommendations"] += result["new_recommendations"]
                
                if result["new_recommendations"] > 0:
                    results["users_with_matches"] += 1
                
                if result.get("email_sent"):
                    results["emails_sent"] += 1
                    
            except Exception as e:
                logger.error(f"Failed to process user {user_id}: {e}")
                results["failed"] += 1
        
        logger.info(f"Batch complete: {results}")
        return results

    async def update_user_preferences(
        self,
        db: Session,
        user_id: str,
        preferences: Dict
    ) -> JobAlertPreferences:
        """Update user's job alert preferences"""
        
        existing = db.query(JobAlertPreferences).filter(
            JobAlertPreferences.user_id == user_id
        ).first()
        
        if existing:
            # Update existing
            for key, value in preferences.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            existing.updated_at = datetime.utcnow()
        else:
            # Create new
            existing = JobAlertPreferences(
                id=user_id,
                user_id=user_id,
                **preferences,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(existing)
        
        db.commit()
        db.refresh(existing)
        
        logger.info(f"Updated preferences for user {user_id}")
        return existing
