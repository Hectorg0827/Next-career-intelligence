"""
Career Health Score (CHS) Calculator

Calculates a comprehensive 1-100 score measuring career vitality.
Higher scores indicate stronger career positioning.

Formula:
- Profile Completeness: 25%
- Skill Currency: 25%
- Market Activity: 20%
- Goal Progress: 20%
- Network Strength: 10%
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pydantic import BaseModel
from app.db.supabase import get_supabase_client
from loguru import logger
import re


class CareerHealthScore(BaseModel):
    """Career Health Score output model"""
    overall_score: int  # 1-100
    grade: str  # A, B, C, D, F
    breakdown: Dict[str, float]
    recommendations: List[str]
    trend: Optional[str] = None  # 'improving', 'stable', 'declining'


class CareerHealthScoreCalculator:
    """Calculates Career Health Score for users"""

    def __init__(self):
        self.weights = {
            "profile_completeness": 0.25,
            "skill_currency": 0.25,
            "market_activity": 0.20,
            "goal_progress": 0.20,
            "network_strength": 0.10
        }

    async def calculate(self, user_id: str) -> CareerHealthScore:
        """
        Calculate comprehensive Career Health Score

        Args:
            user_id: User UUID

        Returns:
            CareerHealthScore with breakdown and recommendations
        """
        logger.info(f"Calculating Career Health Score for user {user_id}")

        try:
            # Fetch all required data
            user_data = await self._fetch_user_data(user_id)

            # Calculate each component
            profile_score = self._calculate_profile_completeness(user_data)
            skill_score = await self._calculate_skill_currency(user_data)
            activity_score = await self._calculate_market_activity(user_data)
            goal_score = await self._calculate_goal_progress(user_data)
            network_score = self._calculate_network_strength(user_data)

            # Weighted sum
            overall_score = int(
                profile_score * self.weights["profile_completeness"] +
                skill_score * self.weights["skill_currency"] +
                activity_score * self.weights["market_activity"] +
                goal_score * self.weights["goal_progress"] +
                network_score * self.weights["network_strength"]
            )

            # Generate recommendations
            recommendations = self._generate_recommendations(
                profile_score, skill_score, activity_score, goal_score, network_score
            )

            # Calculate trend (if historical data exists)
            trend = await self._calculate_trend(user_id, overall_score)

            return CareerHealthScore(
                overall_score=overall_score,
                grade=self._score_to_grade(overall_score),
                breakdown={
                    "profile_completeness": profile_score,
                    "skill_currency": skill_score,
                    "market_activity": activity_score,
                    "goal_progress": goal_score,
                    "network_strength": network_score
                },
                recommendations=recommendations,
                trend=trend
            )

        except Exception as e:
            logger.error(f"Failed to calculate CHS for user {user_id}: {e}")
            raise

    async def _fetch_user_data(self, user_id: str) -> Dict:
        """Fetch all user data needed for CHS calculation"""
        
        supabase = get_supabase_client()
        if not supabase:
            raise Exception("Database unavailable")

        # User profile
        user_response = supabase.table("users").select("*").eq("id", user_id).execute()
        user = user_response.data[0] if user_response.data else {}

        # Career profile from resume studio
        profile_response = supabase.table("career_profiles").select("*").eq("user_id", user_id).execute()
        profile = profile_response.data[0] if profile_response.data else {}

        # Recent applications
        apps_response = supabase.table("job_applications") \
            .select("*") \
            .eq("user_id", user_id) \
            .order("applied_at", desc=True) \
            .limit(50) \
            .execute()
        applications = apps_response.data if apps_response.data else []

        # Active goals
        goals_response = supabase.table("user_goals") \
            .select("*") \
            .eq("user_id", user_id) \
            .eq("status", "active") \
            .execute()
        goals = goals_response.data if goals_response.data else []

        # Interview sessions
        sessions_response = supabase.table("interview_sessions") \
            .select("*") \
            .eq("user_id", user_id) \
            .execute()
        interview_sessions = sessions_response.data if sessions_response.data else []

        return {
            "user": user,
            "profile": profile,
            "applications": applications,
            "goals": goals,
            "interview_sessions": interview_sessions
        }

    def _calculate_profile_completeness(self, user_data: Dict) -> float:
        """
        Calculate profile completeness (0-100)

        Checks for:
        - Resume uploaded
        - Skills added (at least 5)
        - Experience entries
        - Education entries
        - Certifications (optional, bonus)
        """
        profile = user_data.get("profile", {})

        score = 0.0
        max_points = 5

        # Resume uploaded (20 points)
        if profile.get("resume_text") or profile.get("original_resume_url"):
            score += 20

        # Skills (20 points)
        skills = profile.get("skills", [])
        if isinstance(skills, list):
            skill_count = len(skills)
            if skill_count >= 10:
                score += 20
            elif skill_count >= 5:
                score += 15
            elif skill_count >= 3:
                score += 10

        # Experience (20 points)
        experience = profile.get("experience", [])
        if isinstance(experience, list):
            exp_count = len(experience)
            if exp_count >= 3:
                score += 20
            elif exp_count >= 2:
                score += 15
            elif exp_count >= 1:
                score += 10

        # Education (20 points)
        education = profile.get("education", [])
        if isinstance(education, list) and len(education) >= 1:
            score += 20

        # Certifications (20 points bonus)
        certifications = profile.get("certifications", [])
        if isinstance(certifications, list) and len(certifications) >= 1:
            score += 20

        return min(100, score)

    async def _calculate_skill_currency(self, user_data: Dict) -> float:
        """
        Calculate skill currency (0-100)

        Measures how up-to-date and in-demand user's skills are:
        - Skills match current market trends
        - Recent skills added (learning activity)
        - Skills have high demand scores
        """
        profile = user_data.get("profile", {})
        skills = profile.get("skills", [])

        if not skills:
            return 0.0

        score = 0.0

        # High-demand skills (50 points)
        high_demand_skills = [
            "Python", "JavaScript", "TypeScript", "React", "AWS",
            "Machine Learning", "AI", "LLM", "Cloud", "Kubernetes",
            "Next.js", "FastAPI", "PostgreSQL", "Docker", "Go"
        ]

        user_skill_names = [s if isinstance(s, str) else s.get("name", "") for s in skills]
        matches = sum(1 for skill in user_skill_names if any(hd.lower() in skill.lower() for hd in high_demand_skills))

        demand_score = min(50, (matches / 5) * 50)  # 5+ matches = full points
        score += demand_score

        # Skill diversity (25 points)
        # Check for breadth across categories
        categories = {
            "frontend": ["React", "Vue", "Angular", "Next.js", "TypeScript", "JavaScript"],
            "backend": ["Python", "Java", "Go", "Node", "FastAPI", "Django"],
            "data": ["SQL", "PostgreSQL", "MongoDB", "Redis"],
            "cloud": ["AWS", "Azure", "GCP", "Cloud"],
            "ai": ["Machine Learning", "AI", "LLM", "NLP"]
        }

        category_coverage = 0
        for category, category_skills in categories.items():
            if any(cs.lower() in str(user_skill_names).lower() for cs in category_skills):
                category_coverage += 1

        diversity_score = (category_coverage / len(categories)) * 25
        score += diversity_score

        # Recent learning activity (25 points)
        # Check if user has added skills recently
        updated_at = profile.get("updated_at")
        if updated_at:
            try:
                updated_date = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                days_since_update = (datetime.now() - updated_date).days

                if days_since_update <= 7:
                    score += 25
                elif days_since_update <= 30:
                    score += 20
                elif days_since_update <= 90:
                    score += 15
            except:
                pass

        return min(100, score)

    async def _calculate_market_activity(self, user_data: Dict) -> float:
        """
        Calculate market activity (0-100)

        Measures how actively user is engaging with job market:
        - Recent applications
        - Interview activity
        - Profile updates
        - Resume tailoring
        """
        applications = user_data.get("applications", [])
        interview_sessions = user_data.get("interview_sessions", [])

        score = 0.0

        # Recent applications (50 points)
        now = datetime.now()
        recent_apps = [
            app for app in applications
            if (now - datetime.fromisoformat(app.get("applied_at", "").replace('Z', '+00:00'))).days <= 30
        ]

        if len(recent_apps) >= 10:
            score += 50
        elif len(recent_apps) >= 5:
            score += 40
        elif len(recent_apps) >= 3:
            score += 30
        elif len(recent_apps) >= 1:
            score += 20

        # Interview activity (30 points)
        recent_interviews = [
            session for session in interview_sessions
            if (now - datetime.fromisoformat(session.get("created_at", "").replace('Z', '+00:00'))).days <= 30
        ]

        if len(recent_interviews) >= 5:
            score += 30
        elif len(recent_interviews) >= 3:
            score += 25
        elif len(recent_interviews) >= 1:
            score += 20

        # Application success rate (20 points)
        if len(applications) > 0:
            interviews = len([app for app in applications if app.get("status") in ["interview", "offer"]])
            success_rate = interviews / len(applications)

            if success_rate >= 0.2:  # 20%+ interview rate
                score += 20
            elif success_rate >= 0.1:
                score += 15
            elif success_rate >= 0.05:
                score += 10

        return min(100, score)

    async def _calculate_goal_progress(self, user_data: Dict) -> float:
        """
        Calculate goal progress (0-100)

        Measures progress toward career goals:
        - Goals set and tracked
        - Goal completion rate
        - Recent goal activity
        """
        goals = user_data.get("goals", [])

        if not goals:
            return 0.0  # No goals = no score

        score = 0.0

        # Has active goals (30 points)
        if len(goals) >= 3:
            score += 30
        elif len(goals) >= 2:
            score += 25
        elif len(goals) >= 1:
            score += 20

        # Goal progress (40 points)
        total_progress = sum(goal.get("progress", 0) for goal in goals)
        avg_progress = total_progress / len(goals) if goals else 0
        score += (avg_progress / 100) * 40

        # Recent goal activity (30 points)
        now = datetime.now()
        recent_activity = [
            goal for goal in goals
            if (now - datetime.fromisoformat(goal.get("updated_at", "").replace('Z', '+00:00'))).days <= 14
        ]

        if len(recent_activity) >= 2:
            score += 30
        elif len(recent_activity) >= 1:
            score += 20

        return min(100, score)

    def _calculate_network_strength(self, user_data: Dict) -> float:
        """
        Calculate network strength (0-100)

        Currently simplified - can be enhanced with:
        - LinkedIn connections
        - Referrals received
        - Professional group memberships
        """
        user = user_data.get("user", {})
        profile = user_data.get("profile", {})

        score = 0.0

        # Has LinkedIn profile linked (30 points)
        if profile.get("linkedin_url"):
            score += 30

        # Email verified (30 points)
        if user.get("email_verified", False):
            score += 30

        # Has professional summary (20 points)
        if profile.get("summary") and len(profile.get("summary", "")) > 100:
            score += 20

        # Has portfolio/website (20 points)
        if profile.get("portfolio_url") or profile.get("github_url"):
            score += 20

        return min(100, score)

    def _generate_recommendations(
        self,
        profile_score: float,
        skill_score: float,
        activity_score: float,
        goal_score: float,
        network_score: float
    ) -> List[str]:
        """Generate actionable recommendations based on scores"""

        recommendations = []

        # Profile recommendations
        if profile_score < 70:
            recommendations.append("📝 Complete your profile: Add missing experience, education, or certifications")

        # Skill recommendations
        if skill_score < 70:
            recommendations.append("🎯 Update your skills: Learn in-demand technologies like AI, Cloud, or Modern Web Frameworks")

        # Activity recommendations
        if activity_score < 50:
            recommendations.append("💼 Increase job search activity: Apply to 3-5 jobs per week")
        elif activity_score < 70:
            recommendations.append("🚀 Keep up the momentum: Continue applying and interviewing regularly")

        # Goal recommendations
        if goal_score < 50:
            recommendations.append("🎯 Set career goals: Define what you want to achieve in the next 3-6 months")
        elif goal_score < 70:
            recommendations.append("📈 Focus on goal progress: Take action on your active goals")

        # Network recommendations
        if network_score < 60:
            recommendations.append("🤝 Strengthen your network: Connect your LinkedIn and add professional links")

        # If all scores are good
        if not recommendations:
            recommendations.append("⭐ Excellent! Keep maintaining your career health with consistent activity")

        return recommendations

    async def _calculate_trend(self, user_id: str, current_score: int) -> Optional[str]:
        """
        Calculate CHS trend by comparing to historical scores

        Returns: 'improving', 'stable', or 'declining'
        """
        try:
            supabase = get_supabase_client()
            if not supabase:
                return None
                
            # Fetch historical CHS records
            history_response = supabase.table("career_health_history") \
                .select("score, created_at") \
                .eq("user_id", user_id) \
                .order("created_at", desc=True) \
                .limit(2) \
                .execute()

            history = history_response.data if history_response.data else []

            if len(history) < 1:
                # No history yet - save current score
                await self._save_score_history(user_id, current_score)
                return None

            previous_score = history[0].get("score", current_score)
            diff = current_score - previous_score

            # Save current score to history
            await self._save_score_history(user_id, current_score)

            if diff >= 5:
                return "improving"
            elif diff <= -5:
                return "declining"
            else:
                return "stable"

        except Exception as e:
            logger.warning(f"Could not calculate trend: {e}")
            return None

    async def _save_score_history(self, user_id: str, score: int):
        """Save CHS score to history table"""
        try:
            supabase = get_supabase_client()
            if not supabase:
                return
                
            supabase.table("career_health_history").insert({
                "user_id": user_id,
                "score": score,
                "created_at": datetime.utcnow().isoformat()
            }).execute()
        except Exception as e:
            logger.warning(f"Could not save score history: {e}")

    def _score_to_grade(self, score: int) -> str:
        """Convert numeric score to letter grade"""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"


# Global instance
chs_calculator = CareerHealthScoreCalculator()
