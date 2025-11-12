"""
Early Warning Agent - Proactive Career Threat Detection
Monitors for career risks and opportunities before they become critical
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from loguru import logger

from app.models.user_profile import UserProfile, RiskFactor
from app.services.agents.market_intel_agent import MarketIntelAgent
from app.services.agents.risk_agent import RiskAgent


class CareerAlert(Dict):
    """A proactive career alert"""

    pass


class EarlyWarningAgent:
    """
    Early Warning Agent - The threat detector

    Responsibilities:
    - Monitor for automation threats
    - Detect skill obsolescence
    - Flag layoff risks
    - Identify opportunity windows
    - Answer: "What should this person know BEFORE it's urgent?"
    """

    def __init__(self):
        self.market_intel = MarketIntelAgent()
        self.risk_agent = RiskAgent()

    async def scan_for_threats(self, user_profile: UserProfile) -> List[Dict[str, Any]]:
        """
        Proactive scan for career threats

        Returns list of alerts:
        [
            {
                "alert_type": "skill_obsolescence" | "automation_threat" | "market_decline" | "layoff_risk",
                "severity": "critical" | "high" | "medium" | "low",
                "message": "...",
                "recommended_actions": [...],
                "urgency_days": 90
            }
        ]
        """

        alerts = []

        # Check automation risk for current role
        if user_profile.current_role:
            automation_alert = await self._check_automation_threat(user_profile)
            if automation_alert:
                alerts.append(automation_alert)

        # Check skill demand trends
        skill_alerts = await self._check_skill_obsolescence(user_profile)
        alerts.extend(skill_alerts)

        # Check market demand for user's role
        if user_profile.current_role:
            market_alert = await self._check_market_decline(user_profile)
            if market_alert:
                alerts.append(market_alert)

        # Check burnout risk
        burnout_alert = self._check_burnout_risk(user_profile)
        if burnout_alert:
            alerts.append(burnout_alert)

        # Check confidence decay
        confidence_alert = self._check_confidence_decay(user_profile)
        if confidence_alert:
            alerts.append(confidence_alert)

        # Sort by severity
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        alerts.sort(key=lambda x: severity_order.get(x["severity"], 4))

        logger.info(f"Generated {len(alerts)} early warning alerts for user {user_profile.user_id}")

        return alerts

    async def _check_automation_threat(self, user_profile: UserProfile) -> Optional[Dict[str, Any]]:
        """Check if user's current job has increasing automation risk"""

        try:
            current_job_risk = await self.risk_agent.assess_current_job_risk(user_profile)

            risk_level = current_job_risk.get("risk_level", "Unknown")

            if risk_level in ["High", "Medium"]:
                return {
                    "alert_type": "automation_threat",
                    "severity": "high" if risk_level == "High" else "medium",
                    "message": f"Your current role ({user_profile.current_role}) has {risk_level.lower()} AI displacement risk. Consider preparing a transition plan.",
                    "recommended_actions": [
                        "Identify roles with lower automation risk that match your skills",
                        "Develop human-centric skills (leadership, empathy, creativity)",
                        "Start building your next career narrative now, not when displaced",
                    ],
                    "urgency_days": 180 if risk_level == "Medium" else 90,
                }

            return None

        except Exception as e:
            logger.error(f"Error checking automation threat: {e}")
            return None

    async def _check_skill_obsolescence(self, user_profile: UserProfile) -> List[Dict[str, Any]]:
        """Check if user's skills are declining in market demand"""

        alerts = []

        if not user_profile.skills:
            return alerts

        # Get market intel for user's top skills
        top_skills = [s.name for s in user_profile.skills[:5]]

        try:
            market_data = await self.market_intel.get_market_intelligence(top_skills)

            demand_change = market_data.get("demand_change_90d", 0)

            if demand_change < -10:  # 10%+ decline
                alerts.append(
                    {
                        "alert_type": "skill_obsolescence",
                        "severity": "high",
                        "message": f"Demand for your core skills dropped {abs(demand_change):.1f}% in the last 90 days. Time to pivot or upskill.",
                        "recommended_actions": [
                            "Explore emerging skills in your field",
                            "Consider adjacent roles with growing demand",
                            f"Skills to add: {', '.join(market_data.get('emerging_skills', [])[:3])}",
                        ],
                        "urgency_days": 120,
                    }
                )

        except Exception as e:
            logger.error(f"Error checking skill obsolescence: {e}")

        return alerts

    async def _check_market_decline(self, user_profile: UserProfile) -> Optional[Dict[str, Any]]:
        """Check if user's industry/role is in decline"""

        try:
            role_keywords = [user_profile.current_role] if user_profile.current_role else []

            market_data = await self.market_intel.get_market_intelligence(role_keywords)

            trend = market_data.get("demand_trend", "stable")

            if trend == "declining":
                return {
                    "alert_type": "market_decline",
                    "severity": "high",
                    "message": f"The market for {user_profile.current_role} is declining. Consider transitioning to a growth area.",
                    "recommended_actions": [
                        "Identify transferable skills for growing roles",
                        "Network in adjacent industries",
                        "Start building your pivot narrative",
                    ],
                    "urgency_days": 90,
                }

            return None

        except Exception as e:
            logger.error(f"Error checking market decline: {e}")
            return None

    def _check_burnout_risk(self, user_profile: UserProfile) -> Optional[Dict[str, Any]]:
        """Check if user is at risk of burnout"""

        if user_profile.burnout_level is None:
            return None

        if user_profile.burnout_level >= 8:
            return {
                "alert_type": "burnout_risk",
                "severity": "critical",
                "message": "Your burnout level is critically high. Your career and health are at risk if you don't take action soon.",
                "recommended_actions": [
                    "Consider taking a break or sabbatical if possible",
                    "Explore roles with better work-life balance",
                    "Talk to a career coach or therapist",
                    "Set boundaries and reduce non-essential commitments",
                ],
                "urgency_days": 30,
            }
        elif user_profile.burnout_level >= 6:
            return {
                "alert_type": "burnout_risk",
                "severity": "medium",
                "message": "Your burnout level is elevated. Address this before it becomes critical.",
                "recommended_actions": [
                    "Identify what specifically drains you and create a plan to reduce it",
                    "Explore roles that eliminate your top stressors",
                    "Build recovery time into your schedule",
                ],
                "urgency_days": 60,
            }

        return None

    def _check_confidence_decay(self, user_profile: UserProfile) -> Optional[Dict[str, Any]]:
        """Check if user's confidence is declining"""

        if user_profile.confidence_level is None:
            return None

        if user_profile.confidence_level <= 3:
            return {
                "alert_type": "confidence_decay",
                "severity": "medium",
                "message": "Your confidence level is low. This can hold you back from opportunities.",
                "recommended_actions": [
                    "Document recent wins and achievements",
                    "Get skill validation through certifications or projects",
                    "Talk to a mentor or coach",
                    "Apply for stretch opportunities to rebuild momentum",
                ],
                "urgency_days": 90,
            }

        return None

    async def scan_for_opportunities(self, user_profile: UserProfile) -> List[Dict[str, Any]]:
        """
        Proactive scan for career opportunities
        """

        opportunities = []

        # Check for emerging roles matching user's skills
        if user_profile.skills:
            market_data = await self.market_intel.get_market_intelligence([s.name for s in user_profile.skills[:5]])

            if market_data.get("demand_trend") == "growing":
                opportunities.append(
                    {
                        "opportunity_type": "market_growth",
                        "message": f"Demand for your skills is growing. Now is a good time to explore new opportunities.",
                        "recommended_actions": [
                            "Update your resume and LinkedIn",
                            "Reach out to recruiters in growing companies",
                            "Consider asking for a raise if you're underpaid",
                        ],
                    }
                )

        return opportunities
