"""
Analytics Service
Track user engagement, job search metrics, and platform usage
"""

from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from loguru import logger
from datetime import datetime, timedelta
import json

from app.models.database import (
    Job, User, JobApplication, SavedJob, 
    Conversation, CoachMessage, UserSkill
)


class AnalyticsService:
    """Service for tracking and analyzing platform metrics"""

    def get_user_activity_summary(
        self,
        db: Session,
        user_id: str,
        days: int = 30
    ) -> Dict:
        """
        Get comprehensive user activity summary
        
        Returns metrics for dashboard overview
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Job search activity
        total_applications = db.query(JobApplication).filter(
            JobApplication.user_id == user_id
        ).count()
        
        recent_applications = db.query(JobApplication).filter(
            and_(
                JobApplication.user_id == user_id,
                JobApplication.applied_at >= cutoff_date
            )
        ).count()
        
        saved_jobs_count = db.query(SavedJob).filter(
            SavedJob.user_id == user_id
        ).count()
        
        # Application status breakdown
        status_breakdown = {}
        statuses = ["applied", "screening", "interview", "offer", "rejected", "accepted"]
        for status in statuses:
            count = db.query(JobApplication).filter(
                and_(
                    JobApplication.user_id == user_id,
                    JobApplication.status == status
                )
            ).count()
            status_breakdown[status] = count
        
        # AI Coach usage
        conversations_count = db.query(Conversation).filter(
            Conversation.user_id == user_id
        ).count()
        
        messages_count = db.query(CoachMessage).join(
            Conversation
        ).filter(
            Conversation.user_id == user_id
        ).count()
        
        recent_messages = db.query(CoachMessage).join(
            Conversation
        ).filter(
            and_(
                Conversation.user_id == user_id,
                CoachMessage.created_at >= cutoff_date
            )
        ).count()
        
        # Skills profile
        skills_count = db.query(UserSkill).filter(
            UserSkill.user_id == user_id
        ).count()
        
        # Calculate response rate
        responded_applications = status_breakdown.get("screening", 0) + \
                                status_breakdown.get("interview", 0) + \
                                status_breakdown.get("offer", 0) + \
                                status_breakdown.get("accepted", 0)
        
        response_rate = (responded_applications / total_applications * 100) if total_applications > 0 else 0
        
        # Calculate interview rate
        interview_rate = ((status_breakdown.get("interview", 0) + status_breakdown.get("offer", 0) + status_breakdown.get("accepted", 0)) / total_applications * 100) if total_applications > 0 else 0
        
        return {
            "period_days": days,
            "job_search": {
                "total_applications": total_applications,
                "recent_applications": recent_applications,
                "saved_jobs": saved_jobs_count,
                "status_breakdown": status_breakdown,
                "response_rate": round(response_rate, 1),
                "interview_rate": round(interview_rate, 1)
            },
            "ai_coach": {
                "total_conversations": conversations_count,
                "total_messages": messages_count,
                "recent_messages": recent_messages,
                "avg_messages_per_conversation": round(messages_count / conversations_count, 1) if conversations_count > 0 else 0
            },
            "profile": {
                "skills_count": skills_count
            }
        }

    def get_application_timeline(
        self,
        db: Session,
        user_id: str,
        days: int = 90
    ) -> List[Dict]:
        """
        Get application activity over time
        
        Returns daily/weekly breakdown for charts
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        applications = db.query(
            func.date(JobApplication.applied_at).label('date'),
            func.count(JobApplication.id).label('count')
        ).filter(
            and_(
                JobApplication.user_id == user_id,
                JobApplication.applied_at >= cutoff_date
            )
        ).group_by(
            func.date(JobApplication.applied_at)
        ).order_by(
            func.date(JobApplication.applied_at)
        ).all()
        
        timeline = []
        for date, count in applications:
            timeline.append({
                "date": date.isoformat() if date else None,
                "applications": count
            })
        
        return timeline

    def get_top_job_categories(
        self,
        db: Session,
        user_id: str,
        limit: int = 10
    ) -> List[Dict]:
        """Get most applied-to job categories/titles"""
        
        results = db.query(
            Job.title,
            func.count(JobApplication.id).label('application_count')
        ).join(
            JobApplication, JobApplication.job_id == Job.id
        ).filter(
            JobApplication.user_id == user_id
        ).group_by(
            Job.title
        ).order_by(
            desc('application_count')
        ).limit(limit).all()
        
        categories = []
        for title, count in results:
            categories.append({
                "title": title,
                "count": count
            })
        
        return categories

    def get_success_metrics(
        self,
        db: Session,
        user_id: str
    ) -> Dict:
        """Calculate success rates and conversion metrics"""
        
        total_apps = db.query(JobApplication).filter(
            JobApplication.user_id == user_id
        ).count()
        
        if total_apps == 0:
            return {
                "total_applications": 0,
                "response_rate": 0,
                "interview_rate": 0,
                "offer_rate": 0,
                "acceptance_rate": 0,
                "avg_time_to_response": None
            }
        
        # Count by status
        screened = db.query(JobApplication).filter(
            and_(
                JobApplication.user_id == user_id,
                JobApplication.status.in_(["screening", "interview", "offer", "accepted"])
            )
        ).count()
        
        interviews = db.query(JobApplication).filter(
            and_(
                JobApplication.user_id == user_id,
                JobApplication.status.in_(["interview", "offer", "accepted"])
            )
        ).count()
        
        offers = db.query(JobApplication).filter(
            and_(
                JobApplication.user_id == user_id,
                JobApplication.status.in_(["offer", "accepted"])
            )
        ).count()
        
        accepted = db.query(JobApplication).filter(
            and_(
                JobApplication.user_id == user_id,
                JobApplication.status == "accepted"
            )
        ).count()
        
        # Calculate rates
        response_rate = (screened / total_apps) * 100
        interview_rate = (interviews / total_apps) * 100
        offer_rate = (offers / total_apps) * 100
        acceptance_rate = (accepted / offers * 100) if offers > 0 else 0
        
        # Average time to response
        apps_with_updates = db.query(JobApplication).filter(
            and_(
                JobApplication.user_id == user_id,
                JobApplication.applied_at.isnot(None),
                JobApplication.updated_at.isnot(None),
                JobApplication.status != "applied"
            )
        ).all()
        
        avg_time = None
        if apps_with_updates:
            time_diffs = [
                (app.updated_at - app.applied_at).days 
                for app in apps_with_updates
            ]
            avg_time = sum(time_diffs) / len(time_diffs)
        
        return {
            "total_applications": total_apps,
            "response_rate": round(response_rate, 1),
            "interview_rate": round(interview_rate, 1),
            "offer_rate": round(offer_rate, 1),
            "acceptance_rate": round(acceptance_rate, 1),
            "avg_time_to_response": round(avg_time, 1) if avg_time else None
        }

    def get_skill_gap_insights(
        self,
        db: Session,
        user_id: str
    ) -> Dict:
        """Analyze skill gaps across applications"""
        
        applications = db.query(JobApplication).filter(
            JobApplication.user_id == user_id
        ).all()
        
        if not applications:
            return {
                "total_applications_analyzed": 0,
                "common_missing_skills": [],
                "avg_match_score": None
            }
        
        # Collect all skill gaps
        all_gaps = []
        match_scores = []
        
        for app in applications:
            if app.skill_gaps:
                gaps = app.skill_gaps if isinstance(app.skill_gaps, list) else app.skill_gaps.get("missing_skills", [])
                all_gaps.extend(gaps)
            
            if app.match_score:
                match_scores.append(app.match_score)
        
        # Count skill frequency
        skill_frequency = {}
        for skill in all_gaps:
            skill_name = skill if isinstance(skill, str) else skill.get("name", "")
            skill_frequency[skill_name] = skill_frequency.get(skill_name, 0) + 1
        
        # Sort by frequency
        common_gaps = sorted(
            [{"skill": k, "frequency": v} for k, v in skill_frequency.items()],
            key=lambda x: x["frequency"],
            reverse=True
        )[:10]
        
        avg_match = sum(match_scores) / len(match_scores) if match_scores else None
        
        return {
            "total_applications_analyzed": len(applications),
            "common_missing_skills": common_gaps,
            "avg_match_score": round(avg_match, 1) if avg_match else None,
            "skills_to_prioritize": [s["skill"] for s in common_gaps[:5]]
        }

    def get_platform_usage_stats(
        self,
        db: Session,
        user_id: str,
        days: int = 30
    ) -> Dict:
        """Track platform feature usage"""
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # AI Coach usage
        coach_sessions = db.query(Conversation).filter(
            and_(
                Conversation.user_id == user_id,
                Conversation.created_at >= cutoff_date
            )
        ).count()
        
        # Job searches (approximated by saved jobs activity)
        job_searches = db.query(SavedJob).filter(
            and_(
                SavedJob.user_id == user_id,
                SavedJob.saved_at >= cutoff_date
            )
        ).count()
        
        # Application activity
        app_activity = db.query(JobApplication).filter(
            and_(
                JobApplication.user_id == user_id,
                JobApplication.updated_at >= cutoff_date
            )
        ).count()
        
        # Calculate engagement score (0-100)
        engagement_score = min(100, (
            coach_sessions * 10 +
            job_searches * 5 +
            app_activity * 8
        ))
        
        return {
            "period_days": days,
            "ai_coach_sessions": coach_sessions,
            "job_searches": job_searches,
            "application_updates": app_activity,
            "engagement_score": engagement_score,
            "engagement_level": self._get_engagement_level(engagement_score)
        }

    def _get_engagement_level(self, score: float) -> str:
        """Convert engagement score to level"""
        if score >= 80:
            return "Very Active"
        elif score >= 60:
            return "Active"
        elif score >= 40:
            return "Moderate"
        elif score >= 20:
            return "Low"
        else:
            return "Inactive"

    def get_recommendations_performance(
        self,
        db: Session,
        user_id: str
    ) -> Dict:
        """Analyze how well recommendations perform"""
        
        # Get applications with match scores
        apps_with_scores = db.query(JobApplication).filter(
            and_(
                JobApplication.user_id == user_id,
                JobApplication.match_score.isnot(None)
            )
        ).all()
        
        if not apps_with_scores:
            return {
                "total_recommendations_applied": 0,
                "avg_match_score": None,
                "high_match_success_rate": None
            }
        
        # Calculate average match score
        avg_score = sum(app.match_score for app in apps_with_scores) / len(apps_with_scores)
        
        # High match applications (>= 70%)
        high_match_apps = [app for app in apps_with_scores if app.match_score >= 70]
        high_match_success = len([
            app for app in high_match_apps 
            if app.status in ["interview", "offer", "accepted"]
        ])
        
        high_match_rate = (high_match_success / len(high_match_apps) * 100) if high_match_apps else None
        
        return {
            "total_recommendations_applied": len(apps_with_scores),
            "avg_match_score": round(avg_score, 1),
            "high_match_applications": len(high_match_apps),
            "high_match_success_rate": round(high_match_rate, 1) if high_match_rate else None,
            "recommendation_quality": "Excellent" if avg_score >= 75 else "Good" if avg_score >= 60 else "Fair"
        }
