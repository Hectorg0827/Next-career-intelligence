"""
AI Job Matching Service
Calculates match scores between user profiles and jobs using AI intelligence
"""

import asyncio
import json
import logging
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_

import google.generativeai as genai

from app.core.config import settings
from app.models.database import Job, User, JobApplication, UserSkill, Skill
from app.models.job_schemas import JobApplicationResponse
from app.services.skill_service import SkillService

logger = logging.getLogger(__name__)


class AIMatchingService:
    """Service for AI-powered job matching"""

    def __init__(self):
        """Initialize Gemini client"""
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model_name = getattr(settings, "GEMINI_MODEL", "gemini-1.5-flash")
            self.model = genai.GenerativeModel(model_name)
        else:
            logger.warning("GEMINI_API_KEY not set - using fallback matching")
            self.model = None

    async def calculate_match_score(self, user_profile: Dict[str, Any], job: Job, db: Session) -> Dict[str, Any]:
        """
        Calculate match score between user and job using AI

        Args:
            user_profile: User's career profile data
            job: Job record from database
            db: Database session

        Returns:
            Dict with match_score (0-100), skill_gaps, recommended_prep
        """
        try:
            # Extract key user data
            user_skills = user_profile.get("skills", [])
            user_experience = user_profile.get("years_of_experience", 0)
            user_level = user_profile.get("experience_level", "mid")
            user_goals = user_profile.get("career_goals", [])
            user_title = user_profile.get("current_job_title", "")

            # Extract job data
            job_skills = job.required_skills or []
            job_level = job.seniority or "mid"
            job_salary_min = job.salary_min or 0
            job_salary_max = job.salary_max or 0
            job_location = job.location or ""
            job_remote = job.remote_policy or "on_site"

            if self.model:
                # Use AI for intelligent matching
                result = await self._ai_match(
                    user_skills=user_skills,
                    job_skills=job_skills,
                    user_experience=user_experience,
                    job_level=job_level,
                    user_level=user_level,
                    user_goals=user_goals,
                    user_title=user_title,
                    job_title=job.title,
                    job_description=job.description,
                )
            else:
                # Use fallback rule-based matching
                result = self._rule_based_match(
                    user_skills=user_skills,
                    job_skills=job_skills,
                    user_experience=user_experience,
                    job_level=job_level,
                    user_level=user_level,
                )

            return result

        except Exception as e:
            logger.error(f"Error calculating match score: {str(e)}")
            # Return minimal match score on error
            return {
                "match_score": 50.0,
                "skill_gaps": [],
                "recommended_prep": "Unable to calculate recommendations. Please try again.",
                "reasoning": str(e),
            }

    async def _ai_match(
        self,
        user_skills: List[str],
        job_skills: List[str],
        user_experience: float,
        job_level: str,
        user_level: str,
        user_goals: List[str],
        user_title: str,
        job_title: str,
        job_description: str,
    ) -> Dict[str, Any]:
        """
        Use Gemini AI to calculate intelligent match score
        """
        prompt = f"""You are an expert career coach and job matching specialist. 
        
Analyze the following user profile and job posting to calculate a match score.

USER PROFILE:
- Current Job Title: {user_title or 'Not specified'}
- Experience Level: {user_level}
- Years of Experience: {user_experience}
- Skills: {', '.join(user_skills) or 'Not specified'}
- Career Goals: {', '.join(user_goals) or 'Not specified'}

JOB POSTING:
- Job Title: {job_title}
- Required Level: {job_level}
- Required Skills: {', '.join(job_skills) or 'Not specified'}
- Description: {job_description[:500] or 'Not specified'}

Please provide your analysis in the following JSON format:
{{
    "match_score": <0-100 as integer>,
    "skill_gaps": [<list of skills user needs to develop>],
    "skill_matches": [<list of skills user already has that match job>],
    "experience_fit": "<explain how experience level matches>",
    "recommended_prep": "<specific 2-3 sentence recommendation for the user>",
    "strengths": [<2-3 key strengths user brings to this role>],
    "opportunities": [<2-3 growth opportunities this role offers>],
    "career_alignment": "<how well does this align with stated career goals>"
}}

Be fair but realistic. Consider:
- Exact skill matches are best, related skills are good, missing skills can be learned
- Experience level should be within 1 level (entry/mid/senior) ideally
- Strong career goal alignment increases score
- Demonstrated growth potential can compensate for some gaps

Return ONLY valid JSON, no other text."""

        try:
            response = await asyncio.to_thread(self.model.generate_content, prompt)

            # Parse response
            response_text = response.text.strip()

            # Handle markdown code blocks
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            result = json.loads(response_text.strip())

            # Validate and normalize score
            match_score = float(result.get("match_score", 50))
            match_score = max(0, min(100, match_score))  # Clamp 0-100

            return {
                "match_score": match_score,
                "skill_gaps": result.get("skill_gaps", []),
                "skill_matches": result.get("skill_matches", []),
                "recommended_prep": result.get("recommended_prep", ""),
                "experience_fit": result.get("experience_fit", ""),
                "strengths": result.get("strengths", []),
                "opportunities": result.get("opportunities", []),
                "career_alignment": result.get("career_alignment", ""),
                "reasoning": "AI-powered analysis",
            }

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response: {str(e)}")
            # Fall back to rule-based
            return self._rule_based_match(
                user_skills=user_skills,
                job_skills=job_skills,
                user_experience=user_experience,
                job_level=job_level,
                user_level=user_level,
            )
        except Exception as e:
            logger.error(f"AI matching error: {str(e)}")
            return self._rule_based_match(
                user_skills=user_skills,
                job_skills=job_skills,
                user_experience=user_experience,
                job_level=job_level,
                user_level=user_level,
            )

    def _rule_based_match(
        self,
        user_skills: List[str],
        job_skills: List[str],
        user_experience: float,
        job_level: str,
        user_level: str,
    ) -> Dict[str, Any]:
        """
        Fallback rule-based matching algorithm
        """
        # Normalize skill strings for comparison
        user_skills_lower = [s.lower().strip() for s in (user_skills or [])]
        job_skills_lower = [s.lower().strip() for s in (job_skills or [])]

        # Calculate skill match
        matched_skills = []
        missing_skills = []

        for skill in job_skills_lower:
            if any(skill in us or us in skill for us in user_skills_lower):
                matched_skills.append(skill)
            else:
                missing_skills.append(skill)

        skill_match_ratio = len(matched_skills) / max(len(job_skills_lower), 1)
        skill_score = skill_match_ratio * 100

        # Calculate experience level match
        level_mapping = {"entry": 0, "mid": 1, "senior": 2}
        user_level_val = level_mapping.get(user_level.lower(), 1)
        job_level_val = level_mapping.get(job_level.lower(), 1)

        # Experience level should ideally match or exceed job requirement
        level_diff = abs(user_level_val - job_level_val)
        if level_diff == 0:
            level_score = 100
        elif level_diff == 1:
            # One level off is acceptable if user exceeds requirement
            level_score = 80 if user_level_val >= job_level_val else 60
        else:
            level_score = 40

        # Calculate years of experience score
        # Rough estimate: entry (0-2), mid (2-7), senior (7+)
        if job_level_val == 0:  # entry
            exp_score = min(100, user_experience * 25)
        elif job_level_val == 1:  # mid
            exp_score = 100 if 2 <= user_experience <= 10 else max(0, 100 - abs(user_experience - 5) * 10)
        else:  # senior
            exp_score = 100 if user_experience >= 7 else max(0, user_experience * 14.3)

        # Combine scores
        match_score = skill_score * 0.6 + level_score * 0.25 + exp_score * 0.15
        match_score = max(0, min(100, match_score))

        # Generate recommendation
        if skill_match_ratio < 0.3:
            recommendation = "Consider this a stretch role. Focus on learning the missing skills through online courses and side projects."
        elif skill_match_ratio < 0.6:
            recommendation = (
                "Good opportunity to grow. You have foundational skills; focus on the missing areas before applying."
            )
        elif skill_match_ratio < 0.85:
            recommendation = "Strong fit! You have most skills. Polish the missing areas and apply with confidence."
        else:
            recommendation = "Excellent fit! Your skills align well with this role. Apply immediately."

        return {
            "match_score": round(match_score, 1),
            "skill_gaps": missing_skills,
            "skill_matches": matched_skills,
            "recommended_prep": recommendation,
            "reasoning": "Rule-based matching (AI unavailable)",
        }

    async def calculate_all_matches_for_user(self, user_id: str, db: Session, limit: int = 50) -> int:
        """
        Calculate match scores for all active jobs for a user

        Args:
            user_id: User ID
            db: Database session
            limit: Max number of jobs to process

        Returns:
            Number of matches calculated
        """
        try:
            # Get user skills using SkillService
            skill_service = SkillService()
            user_skills_response = skill_service.get_user_skills(db, user_id)
            
            # Get user details
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                logger.warning(f"User {user_id} not found")
                return 0

            # Construct profile data
            # TODO: Fetch experience and goals from user_metadata or separate table
            user_meta = user.user_metadata or {}
            
            profile_data = {
                "skills": [s.name for s in user_skills_response.skills],
                "years_of_experience": user_meta.get("years_of_experience", 5),
                "experience_level": user_meta.get("experience_level", "mid"),
                "career_goals": user_meta.get("career_goals", []),
                "current_job_title": user_meta.get("current_job_title", "")
            }

            # Get all active jobs without match scores
            jobs = (
                db.query(Job)
                .filter(
                    and_(
                        Job.is_active == True,
                    )
                )
                .limit(limit)
                .all()
            )

            matches_calculated = 0

            for job in jobs:
                try:
                    # Get existing application or create new one
                    application = (
                        db.query(JobApplication)
                        .filter(and_(JobApplication.user_id == user_id, JobApplication.job_id == job.id))
                        .first()
                    )

                    if not application:
                        # Calculate match score
                        match_data = await self.calculate_match_score(user_profile=profile_data, job=job, db=db)

                        # Create application record with match data
                        application = JobApplication(
                            user_id=user_id,
                            job_id=job.id,
                            status="matched",
                            match_score=match_data.get("match_score", 50),
                            skill_gaps=json.dumps(match_data.get("skill_gaps", [])),
                            recommended_prep=match_data.get("recommended_prep", ""),
                        )

                        db.add(application)
                        matches_calculated += 1

                except Exception as e:
                    logger.error(f"Error matching job {job.id} for user {user_id}: {str(e)}")
                    continue

            # Commit all changes
            if matches_calculated > 0:
                db.commit()

            return matches_calculated

        except Exception as e:
            logger.error(f"Error calculating matches for user {user_id}: {str(e)}")
            db.rollback()
            return 0

    async def get_top_matched_jobs(
        self, user_id: str, db: Session, limit: int = 10, min_score: float = 60.0
    ) -> List[Dict[str, Any]]:
        """
        Get top matched jobs for a user

        Args:
            user_id: User ID
            db: Database session
            limit: Max results
            min_score: Minimum match score threshold

        Returns:
            List of matched jobs with scores
        """
        try:
            # Query applications with match scores
            applications = (
                db.query(JobApplication)
                .filter(and_(JobApplication.user_id == user_id, JobApplication.match_score >= min_score))
                .order_by(JobApplication.match_score.desc())
                .limit(limit)
                .all()
            )

            results = []
            for app in applications:
                job = db.query(Job).filter(Job.id == app.job_id).first()
                if job:
                    results.append(
                        {
                            "job_id": job.id,
                            "title": job.title,
                            "company": job.company,
                            "location": job.location,
                            "match_score": app.match_score,
                            "skill_gaps": json.loads(app.skill_gaps) if app.skill_gaps else [],
                            "recommended_prep": app.recommended_prep,
                            "salary_range": (
                                f"${job.salary_min:,} - ${job.salary_max:,}"
                                if job.salary_min and job.salary_max
                                else "Not specified"
                            ),
                        }
                    )

            return results

        except Exception as e:
            logger.error(f"Error getting top matches for user {user_id}: {str(e)}")
            return []

    async def refresh_job_match(self, user_id: str, job_id: str, db: Session) -> Optional[Dict[str, Any]]:
        """
        Recalculate match score for specific job

        Args:
            user_id: User ID
            job_id: Job ID
            db: Database session

        Returns:
            Updated match data or None
        """
        try:
            # Get user skills using SkillService
            skill_service = SkillService()
            user_skills_response = skill_service.get_user_skills(db, user_id)
            
            # Get user details
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                logger.warning(f"User {user_id} not found")
                return None

            # Construct profile data
            user_meta = user.user_metadata or {}
            
            profile_data = {
                "skills": [s.name for s in user_skills_response.skills],
                "years_of_experience": user_meta.get("years_of_experience", 5),
                "experience_level": user_meta.get("experience_level", "mid"),
                "career_goals": user_meta.get("career_goals", []),
                "current_job_title": user_meta.get("current_job_title", "")
            }

            # Get job
            job = db.query(Job).filter(Job.id == job_id).first()
            if not job:
                logger.warning(f"Job {job_id} not found")
                return None

            # Calculate match score
            match_data = await self.calculate_match_score(user_profile=profile_data, job=job, db=db)

            # Update or create application
            application = (
                db.query(JobApplication)
                .filter(and_(JobApplication.user_id == user_id, JobApplication.job_id == job_id))
                .first()
            )

            if application:
                application.match_score = match_data.get("match_score", 50)
                application.skill_gaps = json.dumps(match_data.get("skill_gaps", []))
                application.recommended_prep = match_data.get("recommended_prep", "")
            else:
                application = JobApplication(
                    user_id=user_id,
                    job_id=job_id,
                    status="matched",
                    match_score=match_data.get("match_score", 50),
                    skill_gaps=json.dumps(match_data.get("skill_gaps", [])),
                    recommended_prep=match_data.get("recommended_prep", ""),
                )
                db.add(application)

            db.commit()

            return {
                "job_id": job_id,
                "match_score": application.match_score,
                "skill_gaps": json.loads(application.skill_gaps) if application.skill_gaps else [],
                "recommended_prep": application.recommended_prep,
            }

        except Exception as e:
            logger.error(f"Error refreshing match for user {user_id}, job {job_id}: {str(e)}")
            db.rollback()
            return None


# Create singleton instance
ai_matching_service = AIMatchingService()
