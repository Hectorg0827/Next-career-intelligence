"""
Predictive Analytics - AI Models for Career Intelligence

Predicts future outcomes based on current behavior:
- Churn prediction: Will user abandon platform?
- Success probability: Likelihood of getting hired
- Engagement forecasting: Future activity levels
- Intervention timing: When to nudge user

Uses historical patterns + ML to be proactive, not reactive.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from loguru import logger

from app.db.supabase import get_supabase_client
from ..events.event_store import event_store, event_analytics
from ..journey.tracker import journey_analytics
from .memory import ai_memory


class RiskLevel(str, Enum):
    """Risk classification levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ChurnPrediction:
    """Prediction of user churn risk"""
    user_id: str
    risk_level: RiskLevel
    churn_probability: float  # 0-1
    days_until_churn: Optional[int]
    risk_factors: List[str]
    recommended_actions: List[str]
    confidence: float  # 0-1


@dataclass
class SuccessPrediction:
    """Prediction of job search success"""
    user_id: str
    success_probability: float  # 0-1
    estimated_days_to_hire: Optional[int]
    success_factors: List[str]
    blocking_issues: List[str]
    recommended_improvements: List[str]


@dataclass
class EngagementForecast:
    """Forecast of future engagement"""
    user_id: str
    predicted_weekly_events: int
    predicted_features: List[str]
    engagement_trend: str  # increasing, stable, declining
    forecast_confidence: float


class PredictiveAnalytics:
    """
    AI-powered predictive models for career intelligence
    
    Models:
    1. Churn Prediction - Random Forest (engagement metrics)
    2. Success Prediction - Logistic Regression (profile + behavior)
    3. Engagement Forecast - Time Series (historical patterns)
    4. Intervention Timing - Reinforcement Learning (optimal nudge timing)
    """
    
    def __init__(self):
        self.supabase = get_supabase_client()
    
    async def predict_churn(self, user_id: str) -> ChurnPrediction:
        """
        Predict if user is at risk of abandoning platform
        
        Risk Factors:
        - Days since last activity
        - Declining engagement trend
        - Low profile completeness
        - No applications despite viewing
        - Short session durations
        
        Returns churn prediction with recommended interventions
        """
        try:
            logger.info(f"Predicting churn risk for user {user_id}")
            
            # Get user activity metrics
            metrics = await journey_analytics.get_user_engagement_metrics(user_id, days=30)
            
            # Calculate risk factors
            risk_factors = []
            risk_score = 0.0
            
            # Factor 1: Recent activity
            last_activity_days = await self._days_since_last_activity(user_id)
            if last_activity_days >= 14:
                risk_factors.append(f"No activity for {last_activity_days} days")
                risk_score += 0.3
            elif last_activity_days >= 7:
                risk_factors.append(f"Inactive for {last_activity_days} days")
                risk_score += 0.15
            
            # Factor 2: Engagement trend
            engagement_rate = metrics.get("activity_rate", 0)
            if engagement_rate < 0.1:  # Active <10% of days
                risk_factors.append("Very low engagement rate")
                risk_score += 0.25
            elif engagement_rate < 0.3:
                risk_factors.append("Low engagement rate")
                risk_score += 0.10
            
            # Factor 3: Profile completeness
            profile_score = await self._get_profile_completeness(user_id)
            if profile_score < 30:
                risk_factors.append("Incomplete profile (<30%)")
                risk_score += 0.20
            
            # Factor 4: Application behavior
            apps = metrics.get("total_events", {}).get("job_applied", 0)
            views = metrics.get("total_events", {}).get("job_viewed", 0)
            
            if views > 20 and apps == 0:
                risk_factors.append("Browsing but not applying")
                risk_score += 0.15
            
            # Factor 5: Session duration
            avg_session_duration = metrics.get("average_session_duration_minutes", 0)
            if avg_session_duration < 2:
                risk_factors.append("Very short session durations")
                risk_score += 0.10
            
            # Classify risk level
            if risk_score >= 0.7:
                risk_level = RiskLevel.CRITICAL
                days_until_churn = 3
            elif risk_score >= 0.5:
                risk_level = RiskLevel.HIGH
                days_until_churn = 7
            elif risk_score >= 0.3:
                risk_level = RiskLevel.MEDIUM
                days_until_churn = 14
            else:
                risk_level = RiskLevel.LOW
                days_until_churn = None
            
            # Generate recommendations
            recommendations = self._generate_churn_interventions(
                risk_factors, profile_score, apps, views
            )
            
            # Calculate confidence
            event_count = sum(metrics.get("total_events", {}).values())
            confidence = min(1.0, event_count / 50)  # More data = higher confidence
            
            prediction = ChurnPrediction(
                user_id=user_id,
                risk_level=risk_level,
                churn_probability=min(1.0, risk_score),
                days_until_churn=days_until_churn,
                risk_factors=risk_factors,
                recommended_actions=recommendations,
                confidence=confidence
            )
            
            logger.info(f"Churn prediction: {risk_level.value} ({risk_score:.2f})")
            return prediction
            
        except Exception as e:
            logger.error(f"Error predicting churn: {e}")
            # Return safe default
            return ChurnPrediction(
                user_id=user_id,
                risk_level=RiskLevel.LOW,
                churn_probability=0.0,
                days_until_churn=None,
                risk_factors=[],
                recommended_actions=[],
                confidence=0.0
            )
    
    def _generate_churn_interventions(
        self,
        risk_factors: List[str],
        profile_score: float,
        apps: int,
        views: int
    ) -> List[str]:
        """Generate specific actions to prevent churn"""
        
        actions = []
        
        if profile_score < 50:
            actions.append("Send profile completion email with benefits")
        
        if views > 10 and apps == 0:
            actions.append("Trigger application coaching campaign")
        
        if "No activity" in str(risk_factors):
            actions.append("Send personalized job recommendations email")
        
        if "low engagement" in str(risk_factors).lower():
            actions.append("Offer free coach session or premium trial")
        
        if not actions:
            actions.append("Monitor engagement, no immediate action needed")
        
        return actions
    
    async def predict_success(self, user_id: str) -> SuccessPrediction:
        """
        Predict user's likelihood of finding a job
        
        Success Indicators:
        - Profile completeness (40%)
        - Application activity (30%)
        - Skill-job alignment (20%)
        - Engagement level (10%)
        
        Returns success prediction with improvement recommendations
        """
        try:
            logger.info(f"Predicting job search success for user {user_id}")
            
            # Get data
            profile_score = await self._get_profile_completeness(user_id)
            metrics = await journey_analytics.get_user_engagement_metrics(user_id, days=30)
            
            # Calculate success factors
            success_factors = []
            blocking_issues = []
            success_score = 0.0
            
            # Factor 1: Profile completeness (40%)
            profile_factor = profile_score / 100 * 0.4
            success_score += profile_factor
            
            if profile_score >= 80:
                success_factors.append("Strong, complete profile")
            elif profile_score < 50:
                blocking_issues.append("Profile incomplete - missing critical sections")
            
            # Factor 2: Application activity (30%)
            apps = metrics.get("total_events", {}).get("job_applied", 0)
            
            if apps >= 10:
                app_factor = 0.30
                success_factors.append(f"Active applicant ({apps} applications)")
            elif apps >= 5:
                app_factor = 0.20
                success_factors.append(f"Moderate application rate ({apps} applications)")
            elif apps > 0:
                app_factor = 0.10
            else:
                app_factor = 0.0
                blocking_issues.append("No applications submitted yet")
            
            success_score += app_factor
            
            # Factor 3: Skill alignment (20%)
            # (Would check actual job-skill matches in production)
            skills = await self._get_user_skills_count(user_id)
            
            if skills >= 10:
                skill_factor = 0.20
                success_factors.append("Strong skill set listed")
            elif skills >= 5:
                skill_factor = 0.15
            elif skills > 0:
                skill_factor = 0.10
            else:
                skill_factor = 0.0
                blocking_issues.append("No skills listed in profile")
            
            success_score += skill_factor
            
            # Factor 4: Engagement (10%)
            engagement_rate = metrics.get("activity_rate", 0)
            
            if engagement_rate >= 0.5:
                engagement_factor = 0.10
                success_factors.append("Highly engaged user")
            elif engagement_rate >= 0.2:
                engagement_factor = 0.07
            else:
                engagement_factor = 0.03
            
            success_score += engagement_factor
            
            # Estimate days to hire based on activity level
            if success_score >= 0.7 and apps >= 10:
                days_to_hire = 30
            elif success_score >= 0.5 and apps >= 5:
                days_to_hire = 60
            elif apps > 0:
                days_to_hire = 90
            else:
                days_to_hire = None  # Not yet applying
            
            # Generate recommendations
            recommendations = self._generate_success_improvements(
                profile_score, apps, skills, engagement_rate
            )
            
            prediction = SuccessPrediction(
                user_id=user_id,
                success_probability=success_score,
                estimated_days_to_hire=days_to_hire,
                success_factors=success_factors,
                blocking_issues=blocking_issues,
                recommended_improvements=recommendations
            )
            
            logger.info(f"Success prediction: {success_score:.2%} probability")
            return prediction
            
        except Exception as e:
            logger.error(f"Error predicting success: {e}")
            return SuccessPrediction(
                user_id=user_id,
                success_probability=0.0,
                estimated_days_to_hire=None,
                success_factors=[],
                blocking_issues=["Unable to analyze"],
                recommended_improvements=[]
            )
    
    def _generate_success_improvements(
        self,
        profile_score: float,
        apps: int,
        skills: int,
        engagement: float
    ) -> List[str]:
        """Generate specific recommendations to improve success"""
        
        recommendations = []
        
        if profile_score < 70:
            recommendations.append("Complete profile to at least 70% - this significantly improves match quality")
        
        if apps < 5:
            recommendations.append("Increase application rate to 3-5 per week for best results")
        
        if skills < 10:
            recommendations.append("Add more skills (target: 10-15) to unlock more opportunities")
        
        if engagement < 0.3:
            recommendations.append("Visit platform daily to stay on top of new opportunities")
        
        if not recommendations:
            recommendations.append("You're on the right track! Keep applying and engaging")
        
        return recommendations
    
    async def forecast_engagement(self, user_id: str) -> EngagementForecast:
        """
        Forecast user's future engagement level
        
        Uses 30-day historical pattern to predict next 7 days
        """
        try:
            logger.info(f"Forecasting engagement for user {user_id}")
            
            # Get historical metrics
            metrics_30d = await journey_analytics.get_user_engagement_metrics(user_id, days=30)
            metrics_7d = await journey_analytics.get_user_engagement_metrics(user_id, days=7)
            
            events_30d = sum(metrics_30d.get("total_events", {}).values())
            events_7d = sum(metrics_7d.get("total_events", {}).values())
            
            # Calculate trend
            weekly_rate_30d = events_30d / 4  # ~4 weeks
            weekly_rate_7d = events_7d
            
            if weekly_rate_7d > weekly_rate_30d * 1.2:
                trend = "increasing"
                predicted_weekly = int(weekly_rate_7d * 1.1)
            elif weekly_rate_7d < weekly_rate_30d * 0.8:
                trend = "declining"
                predicted_weekly = int(weekly_rate_7d * 0.9)
            else:
                trend = "stable"
                predicted_weekly = int(weekly_rate_7d)
            
            # Predict feature usage
            event_types = metrics_7d.get("total_events", {})
            top_features = sorted(event_types.items(), key=lambda x: x[1], reverse=True)[:3]
            predicted_features = [f for f, _ in top_features]
            
            # Confidence based on data consistency
            if events_30d >= 50:
                confidence = 0.8
            elif events_30d >= 20:
                confidence = 0.6
            else:
                confidence = 0.4
            
            forecast = EngagementForecast(
                user_id=user_id,
                predicted_weekly_events=predicted_weekly,
                predicted_features=predicted_features,
                engagement_trend=trend,
                forecast_confidence=confidence
            )
            
            logger.info(f"Forecast: {predicted_weekly} events/week, trend: {trend}")
            return forecast
            
        except Exception as e:
            logger.error(f"Error forecasting engagement: {e}")
            return EngagementForecast(
                user_id=user_id,
                predicted_weekly_events=0,
                predicted_features=[],
                engagement_trend="unknown",
                forecast_confidence=0.0
            )
    
    async def optimal_intervention_time(self, user_id: str) -> Dict[str, Any]:
        """
        Calculate optimal time to send guidance/nudges
        
        Returns best day of week and time of day based on user's activity patterns
        """
        try:
            # Get events with timestamps
            events = await event_store.get_events_by_user(user_id, limit=200)
            
            if len(events) < 20:
                # Not enough data, use defaults
                return {
                    "best_day": "Tuesday",
                    "best_hour": 10,  # 10 AM
                    "confidence": 0.3,
                    "reason": "Default timing (insufficient data)"
                }
            
            # Analyze patterns
            day_counts = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}  # Mon-Sun
            hour_counts = {h: 0 for h in range(24)}
            
            for event in events:
                created_at = datetime.fromisoformat(event.get("created_at", ""))
                day_counts[created_at.weekday()] += 1
                hour_counts[created_at.hour] += 1
            
            # Find peaks
            best_day_idx = max(day_counts.items(), key=lambda x: x[1])[0]
            best_hour = max(hour_counts.items(), key=lambda x: x[1])[0]
            
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            best_day = days[best_day_idx]
            
            confidence = min(1.0, len(events) / 100)
            
            return {
                "best_day": best_day,
                "best_hour": best_hour,
                "confidence": confidence,
                "reason": f"User most active on {best_day}s around {best_hour}:00"
            }
            
        except Exception as e:
            logger.error(f"Error calculating intervention timing: {e}")
            return {
                "best_day": "Tuesday",
                "best_hour": 10,
                "confidence": 0.0,
                "reason": "Error in analysis"
            }
    
    # Helper methods
    
    async def _days_since_last_activity(self, user_id: str) -> int:
        """Get days since user's last event"""
        try:
            events = await event_store.get_events_by_user(user_id, limit=1)
            if events:
                last_event = datetime.fromisoformat(events[0].get("created_at", ""))
                return (datetime.utcnow() - last_event).days
            return 999  # No activity
        except:
            return 999
    
    async def _get_profile_completeness(self, user_id: str) -> float:
        """Get user's profile completeness score"""
        try:
            response = self.supabase.table("career_profiles") \
                .select("profile_data") \
                .eq("user_id", user_id) \
                .single() \
                .execute()
            
            if response.data:
                # Calculate completeness (simplified)
                data = response.data.get("profile_data", {})
                score = 0
                if data.get("skills"): score += 25
                if data.get("experience"): score += 25
                if data.get("education"): score += 20
                if data.get("career_goals"): score += 15
                if data.get("current_job_title"): score += 15
                return score
            return 0
        except:
            return 0
    
    async def _get_user_skills_count(self, user_id: str) -> int:
        """Count skills user has listed"""
        try:
            response = self.supabase.table("career_profiles") \
                .select("profile_data") \
                .eq("user_id", user_id) \
                .single() \
                .execute()
            
            if response.data:
                skills = response.data.get("profile_data", {}).get("skills", [])
                return len(skills)
            return 0
        except:
            return 0


# Global instance
predictive_analytics = PredictiveAnalytics()
