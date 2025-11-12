"""
AI Job Matching Engine
Multi-objective scoring: SkillFit + TrajectoryFit + ValueMatch + LogisticsFit + GrowthPotential
"""

from typing import Dict, Any, List, Optional, Tuple
from loguru import logger
import numpy as np
from datetime import datetime
import json
import math


class JobMatcher:
    """
    World-class AI matching engine for jobs

    Final Score = w1·SkillFit + w2·TrajectoryFit + w3·ValueMatch + w4·LogisticsFit + w5·GrowthPotential - Penalties
    """

    # Default weights (can be tuned per user or via ML)
    DEFAULT_WEIGHTS = {
        "skill_fit": 0.35,
        "trajectory_fit": 0.25,
        "value_match": 0.15,
        "logistics_fit": 0.15,
        "growth_potential": 0.10,
    }

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.weights = weights or self.DEFAULT_WEIGHTS

    async def calculate_match_score(
        self, user_profile: Dict[str, Any], job: Dict[str, Any], user_preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive match score

        Args:
            user_profile: Career profile with skills, experience, goals
            job: Job posting with requirements, description, location
            user_preferences: Optional user preferences (salary, location, etc.)

        Returns:
            Dict with overall_score and component breakdowns
        """
        try:
            # Component scores
            skill_fit = await self._calculate_skill_fit(user_profile, job)
            trajectory_fit = await self._calculate_trajectory_fit(user_profile, job)
            value_match = await self._calculate_value_match(user_profile, job, user_preferences)
            logistics_fit = await self._calculate_logistics_fit(user_profile, job, user_preferences)
            growth_potential = await self._calculate_growth_potential(user_profile, job)

            # Penalties
            penalties = await self._calculate_penalties(user_profile, job)

            # Weighted sum
            overall_score = (
                self.weights["skill_fit"] * skill_fit
                + self.weights["trajectory_fit"] * trajectory_fit
                + self.weights["value_match"] * value_match
                + self.weights["logistics_fit"] * logistics_fit
                + self.weights["growth_potential"] * growth_potential
            ) - penalties

            # Clamp to 0-100
            overall_score = max(0, min(100, overall_score))

            # Generate explanations
            match_highlights, skill_gaps = await self._generate_explanations(
                user_profile, job, skill_fit, trajectory_fit, growth_potential
            )

            # Displacement risk improvement
            current_risk = user_profile.get("ai_displacement_risk", {}).get("score", 50)
            job_risk = await self._estimate_job_risk(job)
            risk_improvement = max(0, current_risk - job_risk)

            return {
                "overall_score": round(overall_score, 2),
                "skill_fit_score": round(skill_fit, 2),
                "trajectory_fit_score": round(trajectory_fit, 2),
                "value_match_score": round(value_match, 2),
                "logistics_fit_score": round(logistics_fit, 2),
                "growth_potential_score": round(growth_potential, 2),
                "penalties": round(penalties, 2),
                "match_highlights": match_highlights,
                "skill_gaps": skill_gaps,
                "displacement_risk_improvement": round(risk_improvement, 2),
                "why_matched": await self._generate_why_matched(overall_score, match_highlights, skill_gaps),
            }

        except Exception as e:
            logger.error(f"Match scoring error: {e}")
            return {"overall_score": 0, "error": str(e)}

    async def _calculate_skill_fit(self, user_profile: Dict[str, Any], job: Dict[str, Any]) -> float:
        """
        SkillFit: Semantic overlap between user skills and job requirements
        Range: 0-100
        """
        # Extract user skills
        profile_data = user_profile.get("profile_data", {})
        user_skills = set()

        # Hard skills
        hard_skills = profile_data.get("skills", {}).get("hard", [])
        user_skills.update([s.lower() for s in hard_skills])

        # Skills from work history
        for work in profile_data.get("work_history", []):
            tech_stack = work.get("tech_stack", [])
            user_skills.update([s.lower() for s in tech_stack])

        # Extract job skills
        job_skills = set()
        if job.get("skills_extracted"):
            if isinstance(job["skills_extracted"], list):
                job_skills = set([s.lower() for s in job["skills_extracted"]])
            elif isinstance(job["skills_extracted"], dict):
                # pgvector JSONB format
                job_skills = set([s.lower() for s in json.loads(job["skills_extracted"])])

        if not job_skills:
            return 50  # Neutral if no skills specified

        # Calculate overlap
        overlap = user_skills.intersection(job_skills)
        overlap_count = len(overlap)
        total_required = len(job_skills)

        # Basic score
        if total_required == 0:
            base_score = 50
        else:
            base_score = (overlap_count / total_required) * 100

        # Bonus for extra relevant skills
        extra_skills = user_skills - job_skills
        bonus = min(10, len(extra_skills) * 2)

        return min(100, base_score + bonus)

    async def _calculate_trajectory_fit(self, user_profile: Dict[str, Any], job: Dict[str, Any]) -> float:
        """
        TrajectoryFit: Likelihood of career move from current → target role
        Range: 0-100
        """
        profile_data = user_profile.get("profile_data", {})

        # Get current role (most recent work)
        work_history = profile_data.get("work_history", [])
        if not work_history:
            return 50  # Neutral for entry-level

        current_role = work_history[0]  # Assuming sorted by recency
        current_title = current_role.get("title", "").lower()
        current_seniority = self._extract_seniority(current_title)

        # Target role
        target_title = job.get("title", "").lower()
        target_seniority = job.get("seniority", self._extract_seniority(target_title))

        # Calculate seniority progression
        seniority_order = ["entry", "mid", "senior", "lead", "director", "vp", "executive"]
        try:
            current_idx = seniority_order.index(current_seniority)
            target_idx = seniority_order.index(target_seniority)
            seniority_delta = target_idx - current_idx
        except:
            seniority_delta = 0

        # Scoring logic
        if seniority_delta == 0:
            # Lateral move - good
            base_score = 85
        elif seniority_delta == 1:
            # One level up - excellent
            base_score = 95
        elif seniority_delta == 2:
            # Two levels up - ambitious but possible
            base_score = 70
        elif seniority_delta > 2:
            # Too big a jump - unlikely
            base_score = 40
        elif seniority_delta == -1:
            # One level down - acceptable (lifestyle, pivot)
            base_score = 75
        else:
            # Significant step down - red flag
            base_score = 30

        # Check role similarity (e.g., "data analyst" → "senior data analyst")
        current_keywords = set(current_title.split())
        target_keywords = set(target_title.split())
        role_overlap = len(current_keywords.intersection(target_keywords)) / max(len(target_keywords), 1)

        # Adjust based on role similarity
        if role_overlap > 0.5:
            base_score += 10  # Similar role family

        return min(100, base_score)

    async def _calculate_value_match(
        self, user_profile: Dict[str, Any], job: Dict[str, Any], user_preferences: Optional[Dict[str, Any]]
    ) -> float:
        """
        ValueMatch: Alignment on mission, industry, work style
        Range: 0-100
        """
        if not user_preferences:
            return 70  # Neutral default

        score = 70  # Start neutral

        # Industry match
        desired_industries = user_preferences.get("desired_industries", [])
        if desired_industries:
            job_industry = job.get("industry", "").lower()
            if any(ind.lower() in job_industry for ind in desired_industries):
                score += 15

        # Company size preference
        company_size_pref = user_preferences.get("company_size_preference", [])
        if company_size_pref:
            # Would need employer data to match
            score += 5  # Placeholder

        # Work arrangement
        preferred_arrangement = user_preferences.get("work_arrangement")
        job_location_type = job.get("location_type", "").lower()

        if preferred_arrangement == "remote" and "remote" in job_location_type:
            score += 10
        elif preferred_arrangement == "hybrid" and "hybrid" in job_location_type:
            score += 10
        elif preferred_arrangement == "flexible":
            score += 5  # Any arrangement acceptable

        return min(100, score)

    async def _calculate_logistics_fit(
        self, user_profile: Dict[str, Any], job: Dict[str, Any], user_preferences: Optional[Dict[str, Any]]
    ) -> float:
        """
        LogisticsFit: Compensation, location, visa, practical constraints
        Range: 0-100
        """
        score = 70  # Start neutral

        if not user_preferences:
            return score

        # Salary fit
        desired_min_salary = user_preferences.get("salary_min", 0)
        job_salary_max = job.get("salary_max", 0)

        if desired_min_salary > 0 and job_salary_max > 0:
            if job_salary_max >= desired_min_salary:
                score += 15  # Meets minimum
            else:
                score -= 20  # Below minimum - penalty

        # Location fit
        remote_only = user_preferences.get("remote_only", False)
        job_location_type = job.get("location_type", "").lower()

        if remote_only:
            if "remote" in job_location_type:
                score += 10
            else:
                score -= 30  # Deal-breaker
        else:
            # Check location match
            desired_locations = user_preferences.get("desired_locations", [])
            job_location = f"{job.get('location_city', '')} {job.get('location_state', '')} {job.get('location_country', '')}".lower()

            if desired_locations:
                if any(loc.lower() in job_location for loc in desired_locations):
                    score += 10

        # Visa requirement
        visa_required = user_preferences.get("visa_required", False)
        visa_sponsorship = job.get("visa_sponsorship", False)

        if visa_required and not visa_sponsorship:
            score -= 50  # Critical constraint
        elif visa_required and visa_sponsorship:
            score += 10

        return max(0, min(100, score))

    async def _calculate_growth_potential(self, user_profile: Dict[str, Any], job: Dict[str, Any]) -> float:
        """
        GrowthPotential: How much this role advances user's goals
        Range: 0-100
        """
        # Check if job aligns with user goals
        user_goals = user_profile.get("goals", [])
        if not user_goals:
            return 60  # Neutral if no goals set

        score = 60
        job_title = job.get("title", "").lower()
        job_skills = set()
        if job.get("skills_extracted"):
            if isinstance(job["skills_extracted"], list):
                job_skills = set([s.lower() for s in job["skills_extracted"]])

        for goal in user_goals:
            if goal.get("status") != "active":
                continue

            goal_title = goal.get("goal_title", "").lower()

            # Check if job title matches goal
            goal_keywords = set(goal_title.split())
            title_keywords = set(job_title.split())

            if goal_keywords.intersection(title_keywords):
                score += 20
                break

            # Check if job teaches goal skills
            goal_text = f"{goal_title} {goal.get('specific', '')}".lower()
            for skill in job_skills:
                if skill in goal_text:
                    score += 10
                    break

        # Check seniority progression
        job_seniority = job.get("seniority", "mid")
        if job_seniority in ["senior", "lead", "director"]:
            score += 10  # Leadership growth

        return min(100, score)

    async def _calculate_penalties(self, user_profile: Dict[str, Any], job: Dict[str, Any]) -> float:
        """
        Penalties: Red flags that reduce match score
        Range: 0-50
        """
        penalty = 0

        # Missing critical skills (hard requirements)
        # This would need to parse job requirements more sophisticatedly

        # Check experience requirements
        job_min_exp = job.get("experience_years_min", 0)

        profile_data = user_profile.get("profile_data", {})
        work_history = profile_data.get("work_history", [])

        # Calculate total years of experience
        total_exp = 0
        for work in work_history:
            start = work.get("start_date", "")
            end = work.get("end_date", "Present")

            # Rough calculation (would be more accurate with proper date parsing)
            if end == "Present":
                total_exp += 1  # At least 1 year
            else:
                total_exp += 1  # Simplified

        if job_min_exp > 0 and total_exp < job_min_exp:
            exp_gap = job_min_exp - total_exp
            penalty += min(20, exp_gap * 5)  # Up to 20 point penalty

        # Spam/low quality job
        if job.get("is_spam", False) or job.get("spam_score", 0) > 0.5:
            penalty += 30

        return min(50, penalty)

    async def _generate_explanations(
        self,
        user_profile: Dict[str, Any],
        job: Dict[str, Any],
        skill_fit: float,
        trajectory_fit: float,
        growth_potential: float,
    ) -> Tuple[List[str], List[str]]:
        """Generate match highlights and skill gaps"""
        highlights = []
        gaps = []

        # Skill highlights
        if skill_fit > 80:
            highlights.append("Strong skill alignment with job requirements")
        elif skill_fit > 60:
            highlights.append("Good skill match with room to grow")

        # Trajectory highlights
        if trajectory_fit > 85:
            highlights.append("Natural career progression from your current role")

        # Growth highlights
        if growth_potential > 75:
            highlights.append("Aligns well with your career goals")

        # Identify specific gaps
        profile_data = user_profile.get("profile_data", {})
        user_skills = set()
        hard_skills = profile_data.get("skills", {}).get("hard", [])
        user_skills.update([s.lower() for s in hard_skills])

        job_skills = set()
        if job.get("skills_extracted"):
            if isinstance(job["skills_extracted"], list):
                job_skills = set([s.lower() for s in job["skills_extracted"]])

        missing_skills = job_skills - user_skills
        if missing_skills:
            # Highlight top 3 gaps
            for skill in list(missing_skills)[:3]:
                gaps.append(skill.title())

        if not highlights:
            highlights.append("Potential fit worth exploring")

        return highlights, gaps

    async def _generate_why_matched(self, overall_score: float, highlights: List[str], gaps: List[str]) -> str:
        """Generate human-readable explanation"""
        if overall_score >= 80:
            intro = "Excellent match!"
        elif overall_score >= 60:
            intro = "Good match."
        else:
            intro = "Potential fit."

        explanation = f"{intro} {' '.join(highlights[:2])}"

        if gaps:
            explanation += f" Consider upskilling in: {', '.join(gaps[:2])}."

        return explanation

    def _extract_seniority(self, title: str) -> str:
        """Extract seniority level from job title"""
        title_lower = title.lower()

        if any(word in title_lower for word in ["vp", "vice president", "cxo", "chief"]):
            return "executive"
        elif any(word in title_lower for word in ["director", "head of"]):
            return "director"
        elif any(word in title_lower for word in ["lead", "principal", "staff"]):
            return "lead"
        elif any(word in title_lower for word in ["senior", "sr"]):
            return "senior"
        elif any(word in title_lower for word in ["junior", "jr", "associate", "entry"]):
            return "entry"
        else:
            return "mid"

    async def _estimate_job_risk(self, job: Dict[str, Any]) -> float:
        """
        Estimate AI displacement risk for this job (0-100%)

        Based on:
        - Routine vs creative work
        - Human interaction requirements
        - Technical complexity
        - Strategic/leadership components

        Returns: Risk percentage (0 = safe, 100 = high risk)
        """
        job_title = job.get("title", "").lower()
        job_description = job.get("description", "").lower()
        seniority = job.get("seniority", "mid").lower()

        risk_score = 50  # Start at medium risk

        # ===== VERY HIGH RISK (70-90%) =====
        # Repetitive, routine, data-processing roles
        very_high_risk_keywords = [
            "data entry",
            "clerk",
            "operator",
            "transcription",
            "routine",
            "repetitive",
            "administrative assistant",
            "call center",
            "telemarketer",
            "cashier",
        ]
        if any(kw in job_title or kw in job_description for kw in very_high_risk_keywords):
            risk_score = 80

        # ===== HIGH RISK (50-70%) =====
        # Standardized analysis, basic technical work
        high_risk_keywords = [
            "junior",
            "associate",
            "analyst",
            "coordinator",
            "specialist",
            "technical support",
            "quality assurance",
            "bookkeeping",
            "payroll",
        ]
        if any(kw in job_title for kw in high_risk_keywords):
            risk_score = max(risk_score, 60)

        # ===== MEDIUM RISK (30-50%) =====
        # Mix of routine and creative/strategic work
        medium_risk_keywords = [
            "developer",
            "engineer",
            "designer",
            "researcher",
            "consultant",
            "account manager",
            "project manager",
        ]
        if any(kw in job_title for kw in medium_risk_keywords):
            risk_score = 45

        # ===== LOW RISK (15-30%) =====
        # Leadership, creative, strategic, high human interaction
        low_risk_keywords = [
            "senior",
            "lead",
            "principal",
            "staff",
            "manager",
            "director",
            "vp",
            "chief",
            "head of",
            "creative",
            "strategy",
            "business development",
            "sales",
            "client success",
            "relationship manager",
            "therapist",
            "nurse",
            "teacher",
            "coach",
        ]
        if any(kw in job_title for kw in low_risk_keywords):
            risk_score = 25

        # ===== VERY LOW RISK (5-15%) =====
        # C-suite, founder, highly strategic/creative
        very_low_risk_keywords = [
            "ceo",
            "cto",
            "cfo",
            "coo",
            "founder",
            "executive",
            "vp of",
            "svp",
            "president",
            "artist",
            "musician",
            "psychiatrist",
        ]
        if any(kw in job_title for kw in very_low_risk_keywords):
            risk_score = 10

        # Seniority adjustment (senior roles = lower risk)
        if seniority in ["senior", "lead", "principal", "staff"]:
            risk_score -= 10
        elif seniority in ["director", "vp", "executive"]:
            risk_score -= 20
        elif seniority in ["entry", "junior"]:
            risk_score += 10

        # Human interaction bonus (reduces risk)
        human_keywords = [
            "client",
            "customer",
            "team",
            "collaboration",
            "leadership",
            "management",
            "presentation",
            "communication",
        ]
        if any(kw in job_description for kw in human_keywords):
            risk_score -= 5

        # Technical complexity bonus (reduces risk for now)
        tech_keywords = [
            "architecture",
            "design",
            "strategy",
            "research",
            "innovation",
            "optimization",
            "problem solving",
        ]
        if any(kw in job_description for kw in tech_keywords):
            risk_score -= 5

        # Clamp to 0-100
        return max(5, min(95, risk_score))

    @staticmethod
    def calculate_distance(
        lat1: Optional[float], lon1: Optional[float], lat2: Optional[float], lon2: Optional[float]
    ) -> float:
        """
        Calculate distance between two geographic points in kilometers
        Using Haversine formula

        Returns: Distance in km, or None if coordinates missing
        """
        if not all([lat1, lon1, lat2, lon2]):
            return None

        # Convert to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))

        # Radius of Earth in km
        r = 6371

        return r * c

    async def filter_jobs_by_criteria(
        self,
        jobs: List[Dict[str, Any]],
        user_profile: Dict[str, Any],
        user_goals: List[Dict[str, Any]],
        user_preferences: Optional[Dict[str, Any]] = None,
        min_skill_match: float = 30.0,
        max_distance_km: Optional[float] = None,
        user_lat: Optional[float] = None,
        user_lon: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """
        Filter jobs based on:
        1. Goals alignment
        2. Skill match threshold
        3. Distance from user location

        Args:
            jobs: List of job postings
            user_profile: User's career profile
            user_goals: User's active goals
            user_preferences: User preferences (salary, remote, etc.)
            min_skill_match: Minimum skill match % (default 30%)
            max_distance_km: Maximum distance in km (None = no limit)
            user_lat: User's latitude
            user_lon: User's longitude

        Returns:
            Filtered and scored list of jobs
        """
        filtered_jobs = []

        for job in jobs:
            try:
                # Calculate full match score
                match_result = await self.calculate_match_score(
                    user_profile=user_profile, job=job, user_preferences=user_preferences
                )

                # Filter 1: Skill match threshold
                if match_result["skill_fit_score"] < min_skill_match:
                    continue

                # Filter 2: Distance threshold (if not remote)
                job_location_type = job.get("location_type", "").lower()
                if max_distance_km and "remote" not in job_location_type:
                    job_lat = job.get("latitude")
                    job_lon = job.get("longitude")

                    if user_lat and user_lon and job_lat and job_lon:
                        distance = self.calculate_distance(user_lat, user_lon, job_lat, job_lon)
                        if distance and distance > max_distance_km:
                            continue
                    else:
                        # Missing coordinates - keep if distance filter requested
                        distance = None
                else:
                    distance = None

                # Filter 3: Goals alignment scoring
                goal_relevance_score = 0
                relevant_goals = []

                if user_goals:
                    for goal in user_goals:
                        if goal.get("status") != "active":
                            continue

                        goal_title = goal.get("title", "").lower()
                        goal_desc = goal.get("description", "").lower()
                        job_title = job.get("title", "").lower()
                        job_desc = job.get("description", "").lower()

                        # Check if job helps achieve goal
                        goal_keywords = set(goal_title.split() + goal_desc.split())
                        job_keywords = set(job_title.split() + job_desc.split())

                        # Remove common words
                        common_words = {"the", "a", "an", "in", "on", "at", "to", "for", "of", "and", "or"}
                        goal_keywords -= common_words
                        job_keywords -= common_words

                        overlap = len(goal_keywords & job_keywords)
                        if overlap > 0:
                            goal_relevance_score += 20
                            relevant_goals.append(
                                {
                                    "goal_id": goal.get("id"),
                                    "goal_title": goal.get("title"),
                                    "overlap_keywords": list(goal_keywords & job_keywords),
                                }
                            )

                # Calculate AI displacement risk for job
                job_risk = await self._estimate_job_risk(job)

                # Add enriched job data
                filtered_jobs.append(
                    {
                        **job,
                        "match_score": match_result["overall_score"],
                        "match_details": match_result,
                        "ai_displacement_risk": job_risk,
                        "distance_km": distance,
                        "goal_relevance_score": min(100, goal_relevance_score),
                        "relevant_goals": relevant_goals,
                    }
                )

            except Exception as e:
                logger.error(f"Error filtering job {job.get('id')}: {e}")
                continue

        # Sort by match score (highest first)
        filtered_jobs.sort(key=lambda x: x["match_score"], reverse=True)

        return filtered_jobs


# Global instance
job_matcher = JobMatcher()
