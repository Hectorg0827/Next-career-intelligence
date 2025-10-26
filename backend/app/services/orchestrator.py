"""
Career Intelligence Orchestrator
The multi-agent brain that coordinates all analysis
"""

from typing import Dict, Any, List, Optional
from loguru import logger

from app.models.user_profile import UserProfile, ProfileUpdate
from app.models.orchestrator_schemas import (
    OrchestratorOutput,
    JobOpportunity,
    AIDisplacementRiskOutput
)
from app.services.agents.profile_agent import ProfileAgent
from app.services.agents.risk_agent import RiskAgent
from app.services.agents.match_agent import MatchAgent
from app.services.agents.gap_agent import GapAgent
from app.services.agents.sentiment_agent import SentimentAgent


class CareerOrchestrator:
    """
    The Backend Orchestrator for Next Career Intelligence
    
    Mission: Protect the user's career, grow it, and guide it forever.
    
    Coordinates:
    - Profile Agent (memory/identity)
    - Risk Agent (survival/stability)
    - Match Agent (fit/compatibility)
    - Gap Agent (growth/training)
    - Sentiment Agent (motivation/emotion)
    
    Returns standardized OrchestratorOutput for every analysis.
    """
    
    def __init__(self):
        self.profile_agent = ProfileAgent()
        self.risk_agent = RiskAgent()
        self.match_agent = MatchAgent()
        self.gap_agent = GapAgent()
        self.sentiment_agent = SentimentAgent()
        
        logger.info("Career Orchestrator initialized with multi-agent system")
    
    async def analyze_job_match(
        self,
        user_id: str,
        job: JobOpportunity,
        recent_conversation: Optional[str] = None
    ) -> OrchestratorOutput:
        """
        Full career intelligence analysis for a job opportunity
        
        Workflow:
        1. Get user profile (source of truth)
        2. Assess displacement risk
        3. Calculate compatibility
        4. Identify gaps
        5. Generate next steps
        6. Extract learnings for profile update
        7. Generate coach questions
        
        Returns complete OrchestratorOutput
        """
        
        logger.info(f"🧠 Orchestrating analysis for user {user_id} vs job: {job.title}")
        
        # Step 1: Get User Profile (source of truth)
        user_profile = await self.profile_agent.get_profile(user_id)
        
        if not user_profile:
            logger.warning(f"No profile found for user {user_id}, creating new one")
            user_profile = await self.profile_agent.create_profile(user_id)
        
        logger.info(f"Profile loaded: {user_profile.profile_completeness}% complete")
        
        # Step 2: Risk Assessment
        displacement_risk = await self.risk_agent.assess_displacement_risk(job, user_profile)
        
        logger.info(f"Risk assessed: {displacement_risk.level.value}")
        
        # Step 3: Compatibility Scoring
        match_result = await self.match_agent.calculate_compatibility(user_profile, job)
        
        compatibility_score = match_result["compatibility_score"]
        match_highlights = match_result["match_highlights"]
        
        logger.info(f"Compatibility: {compatibility_score}/100")
        
        # Step 4: Gap Analysis
        gap_result = await self.gap_agent.analyze_gaps(user_profile, job)
        
        skill_gaps = gap_result["skill_gaps_for_job"]
        next_steps = gap_result["next_steps_for_user"]
        
        logger.info(f"Identified {len(skill_gaps)} gaps, {len(next_steps)} next steps")
        
        # Step 5: Profile Updates & Learning
        profile_update = await self._generate_profile_update(
            user_profile, job, recent_conversation
        )
        
        # Step 6: Info Requests for Coach
        info_requests = await self._generate_info_requests(user_profile)
        
        # Step 7: Warnings & Flags
        warnings = self._generate_warnings(
            user_profile, job, displacement_risk, compatibility_score
        )
        
        # Step 8: Internal Scores (for ranking)
        internal_scores = self._calculate_internal_scores(
            user_profile, job, compatibility_score, displacement_risk
        )
        
        # Assemble final output
        output = OrchestratorOutput(
            ai_displacement_risk=displacement_risk,
            compatibility_score=compatibility_score,
            match_highlights=match_highlights,
            skill_gaps_for_job=skill_gaps,
            next_steps_for_user=next_steps,
            profile_update=profile_update.model_dump(),
            info_request_for_coach=info_requests,
            warnings=warnings,
            internal_scores=internal_scores
        )
        
        # Step 9: Update the user profile with learnings
        await self.profile_agent.update_profile(user_id, profile_update)
        
        logger.info(f"✅ Orchestration complete for {job.title}")
        
        return output
    
    async def _generate_profile_update(
        self,
        user_profile: UserProfile,
        job: JobOpportunity,
        recent_conversation: Optional[str]
    ) -> ProfileUpdate:
        """
        Generate profile updates based on this interaction
        """
        
        profile_update = ProfileUpdate()
        
        # If there's a recent conversation, extract sentiment
        if recent_conversation:
            sentiment_insights = await self.sentiment_agent.analyze_conversation(
                user_profile, recent_conversation
            )
            
            profile_update.motivation_signals_detected = sentiment_insights.get("motivation_signals", [])
            profile_update.new_preferences_detected = sentiment_insights.get("preferences", [])
            profile_update.new_goals_detected = sentiment_insights.get("goals", [])
            profile_update.risk_signals_detected = sentiment_insights.get("risk_signals", [])
            
            if sentiment_insights.get("burnout_level") is not None:
                profile_update.burnout_level_update = sentiment_insights["burnout_level"]
            
            if sentiment_insights.get("confidence_level") is not None:
                profile_update.confidence_level_update = sentiment_insights["confidence_level"]
        
        # Record job interaction
        profile_update.job_interaction = {
            "job_id": job.job_id or f"{job.company}_{job.title}",
            "action": "viewed",
            "timestamp": "now"
        }
        
        return profile_update
    
    async def _generate_info_requests(self, user_profile: UserProfile) -> List[str]:
        """
        Generate questions the coach should ask to fill missing profile data
        """
        
        missing_fields = await self.profile_agent.get_missing_critical_fields(user_profile.user_id)
        
        questions = []
        
        field_to_question = {
            "salary_expectations": "What salary range feels fair for you right now?",
            "remote_preference": "Do you prefer remote, hybrid, or on-site work?",
            "career_goals": "What are you hoping to achieve in your career in the next 1-3 years?",
            "burnout_level": "On a scale of 1-10, how energized vs drained do you feel in your current work?",
            "preferences": "What aspects of work are most important to you (e.g., flexibility, growth, impact)?",
            "skills": "What are your top 5 skills or areas of expertise?",
            "current_role": "What's your current job title and what do you do day-to-day?"
        }
        
        for field in missing_fields[:3]:  # Limit to 3 questions at a time
            if field in field_to_question:
                questions.append(field_to_question[field])
        
        return questions
    
    def _generate_warnings(
        self,
        user_profile: UserProfile,
        job: JobOpportunity,
        displacement_risk: AIDisplacementRiskOutput,
        compatibility_score: int
    ) -> List[str]:
        """
        Generate warnings or red flags about this opportunity
        """
        
        warnings = []
        
        # High displacement risk warning
        if displacement_risk.level.value in ["High", "Medium"]:
            if compatibility_score >= 70:
                warnings.append(
                    f"⚠️ High compatibility ({compatibility_score}/100) BUT {displacement_risk.level.value.lower()} "
                    f"automation risk. Consider this as a short-term bridge only."
                )
        
        # Burnout warning
        if user_profile.burnout_level and user_profile.burnout_level >= 7:
            # Check if job might repeat burnout factors
            user_hates = [
                s.description.lower()
                for s in user_profile.motivation_signals
                if s.signal_type == "hate"
            ]
            
            job_text = f"{job.title} {job.description or ''}".lower()
            
            if any(hate_keyword in job_text for hate_keyword in user_hates):
                warnings.append(
                    "⚠️ You're experiencing high burnout, and this role may contain elements "
                    "you've identified as draining. Proceed with caution."
                )
        
        # Preference violation warning
        dealbreakers = [p for p in user_profile.preferences if p.is_dealbreaker]
        
        for dealbreaker in dealbreakers:
            if "remote" in dealbreaker.preference.lower() and not job.is_remote:
                warnings.append(
                    f"⚠️ This role is not remote, which conflicts with your stated dealbreaker preference."
                )
        
        # Low compatibility warning
        if compatibility_score < 50:
            warnings.append(
                f"⚠️ Low compatibility score ({compatibility_score}/100). "
                f"Significant skill gaps or preference misalignment detected."
            )
        
        return warnings
    
    def _calculate_internal_scores(
        self,
        user_profile: UserProfile,
        job: JobOpportunity,
        compatibility_score: int,
        displacement_risk: AIDisplacementRiskOutput
    ) -> Dict[str, int]:
        """
        Calculate internal scores for ranking/sorting
        These aren't shown to user but used for recommendations
        """
        
        # Stability Score (0-100): How safe is this job long-term?
        risk_to_stability = {
            "Very Low": 95,
            "Low": 80,
            "Medium": 60,
            "High": 30
        }
        
        stability_score = risk_to_stability.get(displacement_risk.level.value, 60)
        
        # Trajectory Score (0-100): Does this help user long-term?
        trajectory_score = 70  # Default
        
        # Boost if job aligns with stated goals
        if user_profile.career_goals:
            for goal in user_profile.career_goals:
                if goal.timeframe in ["short-term", "mid-term"]:
                    goal_keywords = goal.description.lower().split()
                    job_text = f"{job.title} {job.description or ''}".lower()
                    
                    if any(keyword in job_text for keyword in goal_keywords if len(keyword) > 4):
                        trajectory_score += 15
        
        # Penalize if it's a step backward in seniority
        if user_profile.years_total_experience and user_profile.years_total_experience > 5:
            if job.seniority_level and job.seniority_level.lower() == "entry":
                trajectory_score -= 20
        
        trajectory_score = max(min(trajectory_score, 100), 0)
        
        # Overall Recommendation Score (weighted combination)
        recommendation_score = int(
            0.4 * compatibility_score +
            0.3 * stability_score +
            0.3 * trajectory_score
        )
        
        return {
            "stability_score": stability_score,
            "trajectory_score": trajectory_score,
            "recommendation_score": recommendation_score
        }
    
    async def rank_jobs(
        self,
        user_id: str,
        jobs: List[JobOpportunity]
    ) -> List[Dict[str, Any]]:
        """
        Rank multiple jobs by overall recommendation score
        
        Returns sorted list with scores and metadata
        """
        
        logger.info(f"Ranking {len(jobs)} jobs for user {user_id}")
        
        results = []
        
        for job in jobs:
            analysis = await self.analyze_job_match(user_id, job)
            
            recommendation_score = analysis.internal_scores.get("recommendation_score", 0)
            
            results.append({
                "job": job,
                "analysis": analysis,
                "recommendation_score": recommendation_score,
                "compatibility_score": analysis.compatibility_score,
                "displacement_risk": analysis.ai_displacement_risk.level.value
            })
        
        # Sort by recommendation score (descending)
        results.sort(key=lambda x: x["recommendation_score"], reverse=True)
        
        logger.info(f"✅ Ranked {len(results)} jobs")
        
        return results
