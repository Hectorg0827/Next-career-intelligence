"""
Career Health Scoring Service

Calculates a comprehensive 0-100 score representing overall career health.
This becomes the user's primary engagement metric - like a "credit score" for careers.

Components:
1. Skill Relevance (30%) - How in-demand are user's skills?
2. Experience Trajectory (20%) - Is user progressing or stagnating?
3. Market Positioning (20%) - How competitive vs. peers?
4. Learning Velocity (15%) - How fast is user upskilling?
5. Automation Resilience (15%) - How AI-proof is the role?

Performance: <5 seconds per full calculation
Update Frequency: Daily (background job)
"""
import numpy as np
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging

from ..core.config import CAREER_HEALTH_WEIGHTS
from ..models.types import (
    CareerHealthComponents,
    CareerHealthResult,
    Skill
)

logger = logging.getLogger(__name__)


@dataclass
class WorkHistoryEntry:
    """Single job in work history"""
    title: str
    company: str
    start_date: datetime
    end_date: Optional[datetime]
    skills_gained: List[str] = None


@dataclass
class LearningActivity:
    """Learning activity in last period"""
    skills_added: int = 0
    courses_completed: int = 0
    certifications_earned: int = 0
    practice_sessions: int = 0


class CareerHealthService:
    """
    Calculate comprehensive career health score
    This becomes the user's primary metric for career vitality
    """

    def __init__(self):
        self.weights = CAREER_HEALTH_WEIGHTS

    def calculate_career_health(
        self,
        user_skills: List[Skill],
        work_history: List[WorkHistoryEntry],
        learning_activity: LearningActivity,
        current_role: str,
        years_experience: int,
        peer_data: Optional[Dict] = None,
    ) -> CareerHealthResult:
        """
        Calculate comprehensive career health score

        Args:
            user_skills: User's current skills
            work_history: Job history
            learning_activity: Learning activity (last 12 months)
            current_role: Current job title
            years_experience: Total years of experience
            peer_data: Optional comparison data

        Returns:
            CareerHealthResult with score, components, insights, actions
        """

        logger.info(f"Calculating career health for role: {current_role}")

        # Calculate each component
        components = CareerHealthComponents(
            skill_relevance=self._calculate_skill_relevance(user_skills),
            experience_trajectory=self._calculate_experience_trajectory(work_history),
            market_positioning=self._calculate_market_positioning(
                user_skills, years_experience, peer_data
            ),
            learning_velocity=self._calculate_learning_velocity(learning_activity),
            automation_resilience=self._calculate_automation_resilience(
                current_role, user_skills
            )
        )

        # Calculate weighted total
        total_score = (
            components.skill_relevance * self.weights['skill_relevance'] +
            components.experience_trajectory * self.weights['experience_trajectory'] +
            components.market_positioning * self.weights['market_positioning'] +
            components.learning_velocity * self.weights['learning_velocity'] +
            components.automation_resilience * self.weights['automation_resilience']
        )

        # Assign grade
        grade = self._score_to_grade(total_score)

        # Generate insights
        insights = self._generate_insights(components, None)

        # Generate action items
        action_items = self._generate_action_items(components)

        # Assess risk level
        risk_level = self._assess_risk_level(total_score, None)

        logger.info(f"Career health calculated: {total_score:.1f} ({grade})")

        return CareerHealthResult(
            score=round(total_score, 1),
            grade=grade,
            components=components,
            trend_7d=None,  # Would come from historical data
            trend_30d=None,  # Would come from historical data
            insights=insights,
            action_items=action_items,
            risk_level=risk_level
        )

    def _calculate_skill_relevance(self, user_skills: List[Skill]) -> float:
        """
        Component 1: How relevant are user's skills in current market?

        Factors:
        - Market demand for each skill
        - Growth trend (skills becoming more/less popular)
        - Recency (skills used recently are worth more)
        """
        if not user_skills:
            return 50.0

        skill_scores = []

        for skill in user_skills:
            # Market demand (mocked for now - would come from real market data)
            demand = self._get_skill_demand(skill.name)

            # Growth trend (mocked for now)
            growth = self._get_skill_growth(skill.name)

            # Recency score
            months_since_used = 0  # Would calculate from skill.last_used
            recency_score = max(0, 100 - (months_since_used * 5))

            # Combined score for this skill
            skill_score = (
                demand * 0.50 +
                (50 + growth * 500) * 0.30 +  # Convert growth rate to 0-100
                recency_score * 0.20
            )

            # Weight by proficiency
            weighted = skill_score * skill.proficiency
            skill_scores.append(weighted)

        return float(np.mean(skill_scores))

    def _calculate_experience_trajectory(
        self,
        work_history: List[WorkHistoryEntry]
    ) -> float:
        """
        Component 2: Is user progressing or stagnating?

        Factors:
        - Title progression over time
        - Job tenure patterns (too short = job hopping, too long = stagnation)
        - Skill accumulation rate
        """
        if len(work_history) < 2:
            return 50.0  # Neutral for early career

        # 1. Analyze title progression
        seniority_scores = [
            self._title_to_seniority_score(job.title)
            for job in work_history
        ]

        if len(seniority_scores) > 1:
            # Fit linear trend
            trend = np.polyfit(range(len(seniority_scores)), seniority_scores, 1)[0]

            if trend > 0.5:
                progression_score = 100.0
            elif trend > 0.2:
                progression_score = 85.0
            elif trend > 0:
                progression_score = 70.0
            elif trend == 0:
                progression_score = 50.0
            else:
                progression_score = 30.0
        else:
            progression_score = 50.0

        # 2. Tenure pattern analysis
        tenures = []
        for job in work_history:
            if job.end_date:
                tenure = (job.end_date - job.start_date).days / 365.25
                tenures.append(tenure)

        if tenures:
            avg_tenure = np.mean(tenures)

            # Optimal: 2-4 years per job
            if 2 <= avg_tenure <= 4:
                tenure_score = 100.0
            elif 1.5 <= avg_tenure <= 5:
                tenure_score = 85.0
            elif avg_tenure < 1:
                tenure_score = 50.0  # Job hopping
            elif avg_tenure > 7:
                tenure_score = 60.0  # Stagnation risk
            else:
                tenure_score = 70.0
        else:
            tenure_score = 50.0

        # 3. Skill accumulation rate
        skills_per_job = [
            len(job.skills_gained) if job.skills_gained else 0
            for job in work_history
        ]

        if skills_per_job:
            avg_skills = np.mean(skills_per_job)

            if avg_skills >= 5:
                learning_score = 100.0
            elif avg_skills >= 3:
                learning_score = 80.0
            elif avg_skills >= 1:
                learning_score = 60.0
            else:
                learning_score = 40.0
        else:
            learning_score = 50.0

        # Weighted combination
        return (
            progression_score * 0.50 +
            tenure_score * 0.30 +
            learning_score * 0.20
        )

    def _calculate_market_positioning(
        self,
        user_skills: List[Skill],
        years_experience: int,
        peer_data: Optional[Dict]
    ) -> float:
        """
        Component 3: How does user compare to peers?

        Factors:
        - Skill breadth vs. peers
        - Experience level vs. peers
        - Company tier (if applicable)
        """
        if not peer_data:
            # Without peer data, use skill count as proxy
            skill_count = len(user_skills)

            if skill_count >= 15:
                return 90.0
            elif skill_count >= 10:
                return 80.0
            elif skill_count >= 6:
                return 70.0
            elif skill_count >= 3:
                return 60.0
            else:
                return 50.0

        scores = {}

        # Skill breadth comparison
        if 'avg_skill_count' in peer_data:
            user_skill_count = len(user_skills)
            avg_peer_skills = peer_data['avg_skill_count']

            if user_skill_count >= avg_peer_skills * 1.2:
                scores['skills'] = 100.0
            elif user_skill_count >= avg_peer_skills:
                scores['skills'] = 85.0
            elif user_skill_count >= avg_peer_skills * 0.8:
                scores['skills'] = 70.0
            else:
                scores['skills'] = 50.0

        # Experience comparison
        if 'avg_years_experience' in peer_data:
            avg_peer_years = peer_data['avg_years_experience']

            if years_experience >= avg_peer_years:
                scores['experience'] = 85.0
            else:
                scores['experience'] = 70.0

        return float(np.mean(list(scores.values()))) if scores else 75.0

    def _calculate_learning_velocity(self, learning_activity: LearningActivity) -> float:
        """
        Component 4: How fast is user adapting and learning?

        Factors:
        - Skills added recently
        - Courses completed
        - Certifications earned
        - Practice/application frequency
        """

        # Skills added in last 12 months
        skill_score = min(100.0, learning_activity.skills_added * 10)

        # Courses completed
        course_score = min(100.0, learning_activity.courses_completed * 20)

        # Certifications earned
        cert_score = min(100.0, learning_activity.certifications_earned * 33)

        # Practice sessions
        practice_score = min(100.0, learning_activity.practice_sessions * 5)

        return (
            skill_score * 0.30 +
            course_score * 0.30 +
            cert_score * 0.25 +
            practice_score * 0.15
        )

    def _calculate_automation_resilience(
        self,
        current_role: str,
        user_skills: List[Skill]
    ) -> float:
        """
        Component 5: How resistant to AI/automation?

        Factors:
        - Base automation risk for role (from O*NET or similar)
        - Human-centric skills (leadership, creativity, etc.)
        - Technical adaptability (AI/ML skills)
        """

        # Base automation risk (would come from O*NET API)
        base_risk = self._get_role_automation_risk(current_role)

        # Count human-centric skills
        human_skills = [
            'leadership', 'management', 'negotiation', 'communication',
            'creativity', 'empathy', 'strategic thinking', 'mentoring',
            'teaching', 'coaching'
        ]

        user_skill_names = [s.name.lower() for s in user_skills]
        human_skill_count = sum(
            1 for h_skill in human_skills
            if any(h_skill in u_skill for u_skill in user_skill_names)
        )

        # Each human skill reduces automation risk by 3%
        risk_reduction = human_skill_count * 3

        # Check for AI/ML skills (increases resilience)
        ai_skills = ['machine learning', 'ai', 'artificial intelligence', 'deep learning']
        has_ai_skills = any(
            ai_skill in u_skill
            for ai_skill in ai_skills
            for u_skill in user_skill_names
        )

        if has_ai_skills:
            risk_reduction += 10

        # Adjusted risk
        adjusted_risk = max(5.0, min(95.0, base_risk - risk_reduction))

        # Return resilience (inverse of risk)
        return 100.0 - adjusted_risk

    def _generate_insights(
        self,
        components: CareerHealthComponents,
        trend: Optional[float]
    ) -> List[str]:
        """Generate actionable insights based on components and trends"""
        insights = []

        # Trend-based insights
        if trend is not None:
            if trend < -5:
                insights.append(
                    f"⚠️ Your career health dropped {abs(trend):.1f} points recently. Take action now."
                )
            elif trend > 5:
                insights.append(
                    f"✅ Your career health improved {trend:.1f} points! Keep up the momentum."
                )

        # Component-based insights
        component_dict = {
            'skill_relevance': components.skill_relevance,
            'experience_trajectory': components.experience_trajectory,
            'market_positioning': components.market_positioning,
            'learning_velocity': components.learning_velocity,
            'automation_resilience': components.automation_resilience
        }

        weakest = min(component_dict, key=component_dict.get)
        weakest_score = component_dict[weakest]

        if weakest_score < 60:
            insight_map = {
                'skill_relevance': "⚠️ Your skills are becoming less relevant. Consider upskilling in emerging technologies.",
                'experience_trajectory': "⚠️ Your career progression has slowed. Consider targeting more senior roles.",
                'market_positioning': "⚠️ You're falling behind your peers. Focus on differentiation.",
                'learning_velocity': "⚠️ You haven't added new skills recently. Set aside time for learning this quarter.",
                'automation_resilience': "⚠️ Your role has high automation risk. Focus on building uniquely human skills."
            }
            insights.append(insight_map[weakest])

        # Positive reinforcement
        strongest = max(component_dict, key=component_dict.get)
        if component_dict[strongest] > 85:
            insights.append(
                f"✅ Your {strongest.replace('_', ' ')} is excellent! This is a key strength."
            )

        return insights

    def _generate_action_items(self, components: CareerHealthComponents) -> List[Dict]:
        """Generate specific action items with impact estimates"""
        actions = []

        component_dict = {
            'skill_relevance': components.skill_relevance,
            'experience_trajectory': components.experience_trajectory,
            'market_positioning': components.market_positioning,
            'learning_velocity': components.learning_velocity,
            'automation_resilience': components.automation_resilience
        }

        # Sort by score (lowest first = highest priority)
        sorted_components = sorted(component_dict.items(), key=lambda x: x[1])

        for component_name, score in sorted_components[:3]:  # Top 3 priorities
            if score < 70:
                if component_name == 'skill_relevance':
                    actions.append({
                        'priority': 'high',
                        'title': 'Update your technical skills',
                        'description': 'Add 2-3 in-demand skills relevant to your role',
                        'estimated_time': '3 months',
                        'estimated_impact': '+15-20 points'
                    })

                elif component_name == 'learning_velocity':
                    actions.append({
                        'priority': 'medium',
                        'title': 'Complete a professional certification',
                        'description': 'Earn a recognized certification in your field',
                        'estimated_time': '1-2 months',
                        'estimated_impact': '+10-15 points'
                    })

                elif component_name == 'experience_trajectory':
                    actions.append({
                        'priority': 'high',
                        'title': 'Target a promotion or role change',
                        'description': 'Explore senior positions that match your skills',
                        'estimated_time': '3-6 months',
                        'estimated_impact': '+20-25 points'
                    })

                elif component_name == 'automation_resilience':
                    actions.append({
                        'priority': 'high',
                        'title': 'Build AI-resistant skills',
                        'description': 'Focus on leadership, creativity, and strategic thinking',
                        'estimated_time': '6 months',
                        'estimated_impact': '+15-20 points'
                    })

        return actions

    def _assess_risk_level(self, score: float, trend_30d: Optional[float]) -> str:
        """Determine overall risk level"""
        if score >= 80:
            return 'low'
        elif score >= 60:
            if trend_30d and trend_30d < -10:
                return 'high'  # Declining rapidly
            return 'medium'
        else:
            return 'high'

    def _score_to_grade(self, score: float) -> str:
        """Convert numeric score to letter grade"""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'

    # Helper methods (would integrate with real data sources)

    def _get_skill_demand(self, skill_name: str) -> float:
        """Get market demand for skill (0-100)"""
        # Mock implementation - would query real market data
        high_demand_skills = [
            'python', 'javascript', 'react', 'aws', 'kubernetes', 'docker',
            'machine learning', 'ai', 'typescript', 'node.js', 'sql'
        ]

        skill_lower = skill_name.lower()
        if any(hd in skill_lower for hd in high_demand_skills):
            return 85.0
        return 65.0

    def _get_skill_growth(self, skill_name: str) -> float:
        """Get skill growth rate (-1 to +1, where 0.1 = 10% growth)"""
        # Mock implementation - would query real trend data
        growing_skills = [
            'machine learning', 'ai', 'kubernetes', 'typescript', 'rust'
        ]
        declining_skills = ['jquery', 'angular.js', 'flash']

        skill_lower = skill_name.lower()
        if any(g in skill_lower for g in growing_skills):
            return 0.15  # 15% growth
        elif any(d in skill_lower for d in declining_skills):
            return -0.10  # 10% decline
        return 0.05  # Stable/slight growth

    def _get_role_automation_risk(self, role: str) -> float:
        """Get automation risk for role (0-100)"""
        # Mock implementation - would query O*NET API
        high_risk_roles = ['data entry', 'telemarketer', 'cashier']
        low_risk_roles = ['ceo', 'cto', 'manager', 'director', 'architect']

        role_lower = role.lower()
        if any(lr in role_lower for lr in low_risk_roles):
            return 20.0
        elif any(hr in role_lower for hr in high_risk_roles):
            return 80.0
        return 45.0  # Medium risk

    def _title_to_seniority_score(self, title: str) -> int:
        """Convert title to numeric seniority score"""
        title_lower = title.lower()

        if any(word in title_lower for word in ['ceo', 'cto', 'cfo', 'chief']):
            return 9
        elif any(word in title_lower for word in ['vp', 'vice president']):
            return 8
        elif any(word in title_lower for word in ['director', 'head']):
            return 7
        elif 'principal' in title_lower:
            return 6
        elif 'staff' in title_lower:
            return 5
        elif any(word in title_lower for word in ['lead', 'tech lead']):
            return 4
        elif any(word in title_lower for word in ['senior', 'sr']):
            return 3
        elif any(word in title_lower for word in ['junior', 'jr', 'entry']):
            return 1
        elif 'intern' in title_lower:
            return 0
        else:
            return 2  # Default mid-level


# Singleton instance
_career_health_instance: Optional[CareerHealthService] = None


def get_career_health_service() -> CareerHealthService:
    """Get or create singleton instance of career health service"""
    global _career_health_instance

    if _career_health_instance is None:
        _career_health_instance = CareerHealthService()

    return _career_health_instance
