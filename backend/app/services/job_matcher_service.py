"""
AI Job Matching Service
Matches users with jobs based on skills, experience, and preferences
"""

from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from loguru import logger
from datetime import datetime
import os
import json

from app.models.database import Job, User, UserSkill, Skill, SavedJob
from app.services.skill_service import SkillService
from app.services.skill_gap_analyzer import SkillGapAnalyzerService

try:
    import google.generativeai as genai
except ImportError:
    logger.warning("google.generativeai not installed")
    genai = None


class JobMatcherService:
    """Service for matching users with relevant job opportunities"""

    def __init__(self):
        self.skill_service = SkillService()
        self.gap_analyzer = SkillGapAnalyzerService()
        
        if genai:
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
            self.model = genai.GenerativeModel(
                model_name,
                generation_config={"response_mime_type": "application/json"}
            )
        else:
            self.model = None

    def calculate_skill_match_score(
        self,
        user_skills: List[Dict],
        job_skills: List[str]
    ) -> Tuple[float, Dict]:
        """
        Calculate skill match percentage between user and job
        
        Returns:
            Tuple of (match_score, details_dict)
        """
        if not job_skills or not user_skills:
            return 0.0, {"matched_skills": [], "missing_skills": job_skills or []}
        
        # Normalize skill names
        user_skill_map = {
            self.skill_service.normalize_skill_name(s["name"]): s
            for s in user_skills
        }
        
        normalized_job_skills = [
            self.skill_service.normalize_skill_name(skill) 
            for skill in job_skills
        ]
        
        # Calculate matches
        matched_skills = []
        missing_skills = []
        
        for job_skill in normalized_job_skills:
            if job_skill in user_skill_map:
                matched_skills.append({
                    "name": job_skill,
                    "proficiency": user_skill_map[job_skill].get("proficiency_level", 5)
                })
            else:
                missing_skills.append(job_skill)
        
        # Calculate weighted score
        if not normalized_job_skills:
            return 0.0, {"matched_skills": [], "missing_skills": []}
        
        base_match = len(matched_skills) / len(normalized_job_skills)
        
        # Bonus for proficiency levels
        proficiency_bonus = 0
        if matched_skills:
            avg_proficiency = sum(s["proficiency"] for s in matched_skills) / len(matched_skills)
            proficiency_bonus = (avg_proficiency / 10) * 0.2  # Up to 20% bonus
        
        final_score = min(100.0, (base_match + proficiency_bonus) * 100)
        
        return final_score, {
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "matched_count": len(matched_skills),
            "total_required": len(normalized_job_skills)
        }

    def calculate_experience_match(
        self,
        user_years_experience: int,
        job_required_years: Optional[int]
    ) -> float:
        """Calculate experience level match (0-100)"""
        if not job_required_years:
            return 100.0  # No requirement = perfect match
        
        if user_years_experience >= job_required_years:
            return 100.0
        
        # Partial credit if close
        ratio = user_years_experience / job_required_years
        if ratio >= 0.8:
            return 90.0
        elif ratio >= 0.6:
            return 75.0
        elif ratio >= 0.4:
            return 50.0
        else:
            return 25.0

    def calculate_location_match(
        self,
        user_preferences: Dict,
        job: Job
    ) -> float:
        """Calculate location preference match (0-100)"""
        
        # Remote preferences
        user_wants_remote = user_preferences.get("remote_only", False)
        job_is_remote = job.location_type == "remote" or job.remote_policy in ["full_remote", "remote"]
        
        if user_wants_remote:
            return 100.0 if job_is_remote else 20.0
        
        # Location matching (if not remote-only)
        user_locations = user_preferences.get("preferred_locations", [])
        if not user_locations:
            return 80.0  # No preference = good match
        
        # Check if job location matches any preferred location
        job_location = (job.location or "").lower()
        for pref_loc in user_locations:
            if pref_loc.lower() in job_location or job_location in pref_loc.lower():
                return 100.0
        
        # Partial credit if remote option available
        if job_is_remote:
            return 70.0
        
        return 30.0

    def calculate_salary_match(
        self,
        user_salary_expectation: Optional[int],
        job_salary_min: Optional[int],
        job_salary_max: Optional[int]
    ) -> float:
        """Calculate salary expectation match (0-100)"""
        if not user_salary_expectation:
            return 100.0  # No expectation = perfect match
        
        if not job_salary_min and not job_salary_max:
            return 80.0  # No salary info = good default match
        
        # Use max salary if available, otherwise min
        job_salary = job_salary_max or job_salary_min
        
        if not job_salary:
            return 80.0
        
        if job_salary >= user_salary_expectation:
            return 100.0
        
        # Partial credit if close
        ratio = job_salary / user_salary_expectation
        if ratio >= 0.9:
            return 90.0
        elif ratio >= 0.8:
            return 75.0
        elif ratio >= 0.7:
            return 60.0
        else:
            return 40.0

    async def calculate_match_score(
        self,
        db: Session,
        user_id: str,
        job: Job,
        user_preferences: Optional[Dict] = None
    ) -> Dict:
        """
        Calculate comprehensive match score between user and job
        
        Returns:
            {
                "overall_score": float,
                "skill_match": {...},
                "experience_match": float,
                "location_match": float,
                "salary_match": float,
                "recommendation": str,
                "gap_analysis": {...}
            }
        """
        logger.info(f"Calculating match score for user {user_id} and job {job.id}")
        
        # Get user profile
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # Get user skills
        user_skill_response = self.skill_service.get_user_skills(db, user_id)
        user_skills = [
            {
                "name": s.name,
                "proficiency_level": s.proficiency_level
            }
            for s in user_skill_response.skills
        ]
        
        # Get job skills
        job_skills = []
        if job.required_skills:
            if isinstance(job.required_skills, list):
                job_skills = job.required_skills
            elif isinstance(job.required_skills, dict):
                job_skills = job.required_skills.get("skills", [])
        
        if job.skills_extracted:
            if isinstance(job.skills_extracted, list):
                job_skills.extend(job.skills_extracted)
            elif isinstance(job.skills_extracted, dict):
                job_skills.extend(job.skills_extracted.get("skills", []))
        
        # Remove duplicates
        job_skills = list(set(job_skills))
        
        # Calculate individual scores
        skill_score, skill_details = self.calculate_skill_match_score(user_skills, job_skills)
        
        # Experience match
        user_years_exp = user.user_metadata.get("years_experience", 0) if user.user_metadata else 0
        experience_score = self.calculate_experience_match(
            user_years_exp,
            job.required_years_experience
        )
        
        # Location match
        user_prefs = user_preferences or (user.user_metadata.get("preferences", {}) if user.user_metadata else {})
        location_score = self.calculate_location_match(user_prefs, job)
        
        # Salary match
        user_salary_exp = user_prefs.get("salary_expectation")
        salary_score = self.calculate_salary_match(
            user_salary_exp,
            job.salary_min,
            job.salary_max
        )
        
        # Weighted overall score
        weights = {
            "skills": 0.50,      # 50% - Most important
            "experience": 0.20,  # 20%
            "location": 0.15,    # 15%
            "salary": 0.15       # 15%
        }
        
        overall_score = (
            skill_score * weights["skills"] +
            experience_score * weights["experience"] +
            location_score * weights["location"] +
            salary_score * weights["salary"]
        )
        
        # Generate recommendation
        if overall_score >= 80:
            recommendation = "Excellent Match"
            reason = "You're highly qualified for this role."
        elif overall_score >= 65:
            recommendation = "Good Match"
            reason = "You meet most of the requirements."
        elif overall_score >= 50:
            recommendation = "Fair Match"
            reason = "You have some relevant qualifications."
        else:
            recommendation = "Low Match"
            reason = "This role may require additional skills or experience."
        
        return {
            "overall_score": round(overall_score, 1),
            "skill_match": {
                "score": round(skill_score, 1),
                "details": skill_details
            },
            "experience_match": round(experience_score, 1),
            "location_match": round(location_score, 1),
            "salary_match": round(salary_score, 1),
            "recommendation": recommendation,
            "reason": reason,
            "weights": weights
        }

    async def get_recommended_jobs(
        self,
        db: Session,
        user_id: str,
        limit: int = 20,
        min_score: float = 50.0,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Get top recommended jobs for a user
        
        Args:
            user_id: User ID
            limit: Maximum number of jobs to return
            min_score: Minimum match score threshold
            filters: Additional filters (location, salary, etc.)
        
        Returns:
            List of jobs with match scores, sorted by relevance
        """
        logger.info(f"Getting recommended jobs for user {user_id}")
        
        # Build base query
        query = db.query(Job).filter(Job.is_active == True)
        
        # Apply filters if provided
        if filters:
            if filters.get("location_type"):
                query = query.filter(Job.location_type == filters["location_type"])
            
            if filters.get("seniority"):
                query = query.filter(Job.seniority.in_(filters["seniority"]))
            
            if filters.get("salary_min"):
                query = query.filter(
                    or_(
                        Job.salary_max >= filters["salary_min"],
                        Job.salary_min >= filters["salary_min"]
                    )
                )
        
        # Get jobs
        jobs = query.order_by(Job.posted_at.desc()).limit(limit * 2).all()  # Get more to filter
        
        # Calculate match scores
        job_matches = []
        for job in jobs:
            try:
                match_data = await self.calculate_match_score(db, user_id, job)
                
                if match_data["overall_score"] >= min_score:
                    job_matches.append({
                        "job": {
                            "id": str(job.id),
                            "title": job.title,
                            "company": job.company_id,
                            "location": job.location,
                            "location_type": job.location_type,
                            "remote_policy": job.remote_policy,
                            "salary_min": job.salary_min,
                            "salary_max": job.salary_max,
                            "salary_currency": job.salary_currency,
                            "seniority": job.seniority,
                            "employment_type": job.employment_type,
                            "posted_at": job.posted_at.isoformat() if job.posted_at else None,
                            "external_url": job.external_url,
                            "apply_url": job.apply_url,
                        },
                        "match": match_data
                    })
            except Exception as e:
                logger.error(f"Error calculating match for job {job.id}: {e}")
                continue
        
        # Sort by match score
        job_matches.sort(key=lambda x: x["match"]["overall_score"], reverse=True)
        
        return job_matches[:limit]

    async def explain_match(
        self,
        db: Session,
        user_id: str,
        job_id: str
    ) -> Dict:
        """
        Use AI to generate detailed explanation of job match
        
        Returns:
            {
                "match_score": float,
                "explanation": str,
                "strengths": List[str],
                "gaps": List[str],
                "recommendations": List[str]
            }
        """
        if not self.model:
            raise ValueError("Gemini AI not configured")
        
        # Get job
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        # Calculate match
        match_data = await self.calculate_match_score(db, user_id, job)
        
        # Generate AI explanation
        prompt = f"""
You are a career advisor. Analyze this job match and provide detailed explanation.

Job Title: {job.title}
Job Description: {job.description[:500]}
Required Skills: {match_data['skill_match']['details']['missing_skills']}

User's Matched Skills: {match_data['skill_match']['details']['matched_skills']}
Overall Match Score: {match_data['overall_score']}%

Provide a comprehensive analysis in JSON format:
{{
    "explanation": "2-3 sentence overview of the match",
    "strengths": ["List 3-5 key strengths that make the user qualified"],
    "gaps": ["List 2-4 skill or experience gaps"],
    "recommendations": ["List 3-4 specific actions to improve candidacy"]
}}
"""
        
        try:
            response = self.model.generate_content(prompt)
            ai_analysis = json.loads(response.text)
            
            return {
                "match_score": match_data["overall_score"],
                "match_breakdown": match_data,
                **ai_analysis
            }
        except Exception as e:
            logger.error(f"Error generating AI explanation: {e}")
            return {
                "match_score": match_data["overall_score"],
                "match_breakdown": match_data,
                "explanation": f"You have a {match_data['recommendation'].lower()} with this role.",
                "strengths": [f"Matched {match_data['skill_match']['details']['matched_count']} required skills"],
                "gaps": match_data['skill_match']['details']['missing_skills'][:3],
                "recommendations": ["Review job requirements", "Build missing skills", "Tailor your resume"]
            }
