"""
Match Agent - Fit & Compatibility Scoring
Compares User Profile to job opportunities
"""

from typing import Dict, Any, List, Tuple
from loguru import logger
import google.generativeai as genai

from app.core.config import settings
from app.models.user_profile import UserProfile, Skill, UserPreference
from app.models.orchestrator_schemas import JobOpportunity


class MatchAgent:
    """
    Match Agent - The compatibility analyzer
    
    Responsibilities:
    - Score compatibility between user and job (0-100)
    - Generate match highlights
    - Consider skills, experience, preferences, and values
    - Answer: "How good of a fit is this job for this person?"
    """
    
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    async def calculate_compatibility(
        self,
        user_profile: UserProfile,
        job: JobOpportunity
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive compatibility score and highlights
        
        Returns:
        - compatibility_score (0-100)
        - match_highlights (list of reasons)
        - sub_scores (breakdown)
        """
        
        # Calculate sub-scores
        skill_match = self._calculate_skill_match(user_profile, job)
        experience_alignment = self._calculate_experience_alignment(user_profile, job)
        preference_alignment = self._calculate_preference_alignment(user_profile, job)
        burnout_alignment = self._calculate_burnout_alignment(user_profile, job)
        
        # Weighted final score
        compatibility_score = int(
            0.4 * skill_match +
            0.3 * experience_alignment +
            0.2 * preference_alignment +
            0.1 * burnout_alignment
        )
        
        # Generate highlights using AI
        highlights = await self._generate_match_highlights(
            user_profile, job, compatibility_score
        )
        
        logger.info(
            f"Compatibility score for {job.title}: {compatibility_score}/100 "
            f"(skills={skill_match}, exp={experience_alignment}, "
            f"prefs={preference_alignment}, burnout={burnout_alignment})"
        )
        
        return {
            "compatibility_score": compatibility_score,
            "match_highlights": highlights,
            "sub_scores": {
                "skill_match": skill_match,
                "experience_alignment": experience_alignment,
                "preference_alignment": preference_alignment,
                "burnout_alignment": burnout_alignment
            }
        }
    
    def _calculate_skill_match(self, user_profile: UserProfile, job: JobOpportunity) -> int:
        """
        Calculate skill match percentage (0-100)
        % of required skills user already has
        """
        
        if not job.required_skills or len(job.required_skills) == 0:
            return 70  # Default if no skills specified
        
        user_skill_names = [s.name.lower() for s in user_profile.skills]
        user_competencies = [c.lower() for c in user_profile.core_competencies]
        user_all_skills = set(user_skill_names + user_competencies)
        
        required_skills_lower = [s.lower() for s in job.required_skills]
        
        # Count matches
        matches = 0
        for required_skill in required_skills_lower:
            # Exact match
            if required_skill in user_all_skills:
                matches += 1
                continue
            
            # Partial match (fuzzy)
            for user_skill in user_all_skills:
                if required_skill in user_skill or user_skill in required_skill:
                    matches += 0.5
                    break
        
        skill_match_percentage = int((matches / len(required_skills_lower)) * 100)
        
        return min(skill_match_percentage, 100)
    
    def _calculate_experience_alignment(self, user_profile: UserProfile, job: JobOpportunity) -> int:
        """
        Calculate experience alignment (0-100)
        How close is user's seniority/scope to what job expects
        """
        
        if not job.seniority_level:
            return 75  # Default if not specified
        
        # Map years of experience to seniority
        years = user_profile.years_total_experience or 0
        
        user_seniority = self._map_experience_to_seniority(years)
        
        job_seniority = job.seniority_level.lower()
        
        # Alignment scoring
        seniority_levels = ["entry", "mid", "senior", "lead", "executive"]
        
        if user_seniority not in seniority_levels or job_seniority not in seniority_levels:
            return 70
        
        user_level_idx = seniority_levels.index(user_seniority)
        job_level_idx = seniority_levels.index(job_seniority)
        
        # Perfect match
        if user_level_idx == job_level_idx:
            return 100
        
        # One level off
        if abs(user_level_idx - job_level_idx) == 1:
            return 85
        
        # Two levels off
        if abs(user_level_idx - job_level_idx) == 2:
            return 60
        
        # More than two levels off
        return 40
    
    def _map_experience_to_seniority(self, years: float) -> str:
        """Map years of experience to seniority level"""
        
        if years < 2:
            return "entry"
        elif years < 5:
            return "mid"
        elif years < 10:
            return "senior"
        elif years < 15:
            return "lead"
        else:
            return "executive"
    
    def _calculate_preference_alignment(self, user_profile: UserProfile, job: JobOpportunity) -> int:
        """
        Calculate preference alignment (0-100)
        Remote/on-site, location, work style, etc.
        """
        
        alignment_score = 100
        
        # Remote preference
        if user_profile.remote_preference:
            if user_profile.remote_preference == "remote_only" and not job.is_remote:
                alignment_score -= 40
            elif user_profile.remote_preference == "on_site" and job.is_remote:
                alignment_score -= 20
        
        # Check dealbreakers in preferences
        dealbreaker_violations = 0
        for pref in user_profile.preferences:
            if pref.is_dealbreaker:
                # Check if job violates this dealbreaker
                if self._violates_preference(pref, job):
                    dealbreaker_violations += 1
        
        if dealbreaker_violations > 0:
            alignment_score -= (dealbreaker_violations * 30)
        
        # Location preference
        if user_profile.location and job.location:
            if not user_profile.relocation_willing:
                if user_profile.location.lower() not in job.location.lower():
                    if not job.is_remote:
                        alignment_score -= 25
        
        return max(alignment_score, 0)
    
    def _violates_preference(self, preference: UserPreference, job: JobOpportunity) -> bool:
        """
        Check if job violates a user preference
        Simple keyword matching for now
        """
        
        pref_text = preference.preference.lower()
        job_title = job.title.lower()
        job_desc = (job.description or "").lower()
        
        # Simple violation checks
        if "no sales" in pref_text and ("sales" in job_title or "sales" in job_desc):
            return True
        
        if "no management" in pref_text and ("manager" in job_title or "management" in job_desc):
            return True
        
        return False
    
    def _calculate_burnout_alignment(self, user_profile: UserProfile, job: JobOpportunity) -> int:
        """
        Calculate burnout alignment (0-100)
        Does this job eliminate or repeat the things user hates?
        """
        
        # If no burnout data, return neutral
        if not user_profile.motivation_signals:
            return 75
        
        alignment_score = 75  # Start neutral
        
        # Check what user hates
        hates = [
            signal for signal in user_profile.motivation_signals
            if signal.signal_type == "hate"
        ]
        
        # Check what user enjoys
        enjoys = [
            signal for signal in user_profile.motivation_signals
            if signal.signal_type == "enjoy"
        ]
        
        job_text = f"{job.title} {job.description or ''} {' '.join(job.responsibilities)}".lower()
        
        # Penalize if job contains things user hates
        for hate_signal in hates:
            hate_keywords = hate_signal.description.lower().split()
            if any(keyword in job_text for keyword in hate_keywords if len(keyword) > 4):
                penalty = hate_signal.intensity * 5
                alignment_score -= penalty
        
        # Boost if job contains things user enjoys
        for enjoy_signal in enjoys:
            enjoy_keywords = enjoy_signal.description.lower().split()
            if any(keyword in job_text for keyword in enjoy_keywords if len(keyword) > 4):
                boost = enjoy_signal.intensity * 3
                alignment_score += boost
        
        return max(min(alignment_score, 100), 0)
    
    async def _generate_match_highlights(
        self,
        user_profile: UserProfile,
        job: JobOpportunity,
        compatibility_score: int
    ) -> List[str]:
        """
        Use AI to generate human-readable match highlights
        """
        
        try:
            prompt = self._build_highlights_prompt(user_profile, job, compatibility_score)
            
            response = self.model.generate_content(prompt)
            
            highlights = self._parse_highlights(response.text)
            
            return highlights
            
        except Exception as e:
            logger.error(f"Error generating match highlights: {e}")
            
            # Fallback highlights
            return self._generate_fallback_highlights(user_profile, job, compatibility_score)
    
    def _build_highlights_prompt(
        self,
        user_profile: UserProfile,
        job: JobOpportunity,
        compatibility_score: int
    ) -> str:
        """Build prompt for AI to generate match highlights"""
        
        user_skills = [s.name for s in user_profile.skills[:10]]
        user_enjoys = [s.description for s in user_profile.motivation_signals if s.signal_type == "enjoy"][:3]
        user_hates = [s.description for s in user_profile.motivation_signals if s.signal_type == "hate"][:3]
        
        prompt = f"""Generate 2-4 match highlights for this job-candidate fit.

User Profile:
- Current Role: {user_profile.current_role or 'Not specified'}
- Years Experience: {user_profile.years_total_experience or 'Not specified'}
- Top Skills: {', '.join(user_skills)}
- Enjoys: {', '.join(user_enjoys) if user_enjoys else 'Not specified'}
- Dislikes: {', '.join(user_hates) if user_hates else 'Not specified'}

Job:
- Title: {job.title}
- Company: {job.company}
- Required Skills: {', '.join(job.required_skills) if job.required_skills else 'Not specified'}
- Remote: {job.is_remote}

Compatibility Score: {compatibility_score}/100

Return ONLY a JSON array of 2-4 short, specific highlights explaining why this is a good (or not good) match.
Each highlight should be one sentence, concrete, and reference specific skills or preferences.

Example format:
["Your 8 years in special education directly aligns with this behavior intervention role.", "Remote flexibility matches your stated preference for work-life balance."]

Output ONLY valid JSON array."""

        return prompt
    
    def _parse_highlights(self, response_text: str) -> List[str]:
        """Parse AI response into list of highlights"""
        
        import json
        import re
        
        try:
            # Extract JSON array
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            
            if json_match:
                highlights = json.loads(json_match.group())
                return highlights
            else:
                raise ValueError("No JSON array found")
                
        except Exception as e:
            logger.error(f"Error parsing highlights: {e}")
            return []
    
    def _generate_fallback_highlights(
        self,
        user_profile: UserProfile,
        job: JobOpportunity,
        compatibility_score: int
    ) -> List[str]:
        """Generate simple highlights when AI fails"""
        
        highlights = []
        
        if compatibility_score >= 80:
            highlights.append(f"Strong overall compatibility ({compatibility_score}/100) based on skills and experience.")
        elif compatibility_score >= 60:
            highlights.append(f"Good fit ({compatibility_score}/100) with some gaps to address.")
        else:
            highlights.append(f"Moderate fit ({compatibility_score}/100) - may require significant skill development.")
        
        # Add skill highlight
        if user_profile.skills:
            top_skills = [s.name for s in user_profile.skills[:3]]
            highlights.append(f"Your skills in {', '.join(top_skills)} are relevant to this role.")
        
        # Add remote highlight if applicable
        if job.is_remote and user_profile.remote_preference == "remote_only":
            highlights.append("Remote position matches your preference for flexible work.")
        
        return highlights
