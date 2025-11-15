"""
Smart Profile Assistant - AI-Powered Profile Completion

Helps users build complete, compelling profiles by:
- Inferring missing information from context
- Suggesting skills based on job history
- Writing professional summaries from bullet points
- Optimizing profiles for ATS and recruiters
- Detecting inconsistencies and gaps

Makes profile building effortless and intelligent.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum

import google.generativeai as genai
from loguru import logger

from app.db.supabase import get_supabase_client
from app.core.config import settings
from ..profile.unified_profile import unified_profile_manager
from .memory import ai_memory


class ProfileCompletenessLevel(str, Enum):
    """Profile completion levels"""
    MINIMAL = "minimal"  # < 30%
    BASIC = "basic"      # 30-50%
    GOOD = "good"        # 50-75%
    EXCELLENT = "excellent"  # 75-90%
    PERFECT = "perfect"  # > 90%


@dataclass
class ProfileSuggestion:
    """Suggestion for improving profile"""
    field: str
    suggestion_type: str  # 'missing', 'incomplete', 'inconsistent', 'optimization'
    current_value: Optional[Any]
    suggested_value: Any
    reasoning: str
    priority: int  # 1=critical, 2=high, 3=medium, 4=low
    impact_score: float  # 0-1, how much this improves profile


@dataclass
class ProfileAnalysis:
    """Complete profile analysis"""
    user_id: str
    completeness_level: ProfileCompletenessLevel
    completeness_score: float  # 0-1
    missing_fields: List[str]
    incomplete_fields: List[str]
    suggestions: List[ProfileSuggestion]
    inferred_skills: List[str]
    strengths: List[str]
    weaknesses: List[str]


class SmartProfileAssistant:
    """
    AI Assistant for Profile Completion
    
    Features:
    - Analyze profile completeness
    - Infer missing skills from experience
    - Generate professional summaries
    - Suggest improvements
    - Optimize for ATS
    """
    
    def __init__(self):
        self.supabase = get_supabase_client()
        
        # Initialize Gemini
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-pro')
            logger.info("Smart Profile Assistant initialized with Gemini")
        except Exception as e:
            logger.warning(f"Gemini not configured: {e}")
            self.model = None
    
    
    async def analyze_profile(self, user_id: str) -> ProfileAnalysis:
        """
        Complete profile analysis with suggestions
        
        Returns:
            ProfileAnalysis with completeness score and suggestions
        """
        try:
            # Get unified profile
            profile = await unified_profile_manager.get_unified_profile(user_id)
            if not profile:
                logger.warning(f"No profile found for user {user_id}")
                return self._empty_analysis(user_id)
            
            # Calculate completeness
            completeness = self._calculate_completeness(profile)
            
            # Find missing/incomplete fields
            missing = self._find_missing_fields(profile)
            incomplete = self._find_incomplete_fields(profile)
            
            # Generate suggestions
            suggestions = await self._generate_suggestions(profile, missing, incomplete)
            
            # Infer skills from experience
            inferred_skills = await self._infer_skills_from_experience(profile)
            
            # Identify strengths and weaknesses
            strengths, weaknesses = self._analyze_strengths_weaknesses(profile, completeness)
            
            # Determine level
            level = self._get_completeness_level(completeness)
            
            return ProfileAnalysis(
                user_id=user_id,
                completeness_level=level,
                completeness_score=completeness,
                missing_fields=missing,
                incomplete_fields=incomplete,
                suggestions=suggestions,
                inferred_skills=inferred_skills,
                strengths=strengths,
                weaknesses=weaknesses
            )
            
        except Exception as e:
            logger.error(f"Error analyzing profile for {user_id}: {e}")
            return self._empty_analysis(user_id)
    
    
    async def infer_missing_data(self, user_id: str) -> Dict[str, Any]:
        """
        Infer missing profile data from available context
        
        Returns:
            Dictionary of inferred values
        """
        try:
            # Get profile and context
            profile = await unified_profile_manager.get_unified_profile(user_id)
            context = await ai_memory.get_user_context(user_id)
            
            inferred = {}
            
            # Infer location from job preferences or history
            if not profile.get('location'):
                inferred['location'] = self._infer_location(profile, context)
            
            # Infer seniority from experience years
            if not profile.get('seniority_level'):
                inferred['seniority_level'] = self._infer_seniority(profile)
            
            # Infer desired salary from experience and location
            if not profile.get('desired_salary'):
                inferred['desired_salary'] = self._infer_salary(profile)
            
            # Infer skills from job titles and descriptions
            if not profile.get('skills') or len(profile['skills']) < 5:
                inferred['skills'] = await self._infer_skills_from_experience(profile)
            
            # Infer job preferences from behavior
            if not profile.get('preferences'):
                inferred['preferences'] = self._infer_preferences(context)
            
            logger.info(f"Inferred {len(inferred)} fields for user {user_id}")
            return inferred
            
        except Exception as e:
            logger.error(f"Error inferring data for {user_id}: {e}")
            return {}
    
    
    async def generate_summary(self, user_id: str) -> Optional[str]:
        """
        Generate professional profile summary using AI
        
        Returns:
            Professional summary text
        """
        if not self.model:
            return None
        
        try:
            # Get profile
            profile = await unified_profile_manager.get_unified_profile(user_id)
            if not profile:
                return None
            
            # Build context for AI
            context_parts = []
            
            if profile.get('experience'):
                context_parts.append(f"Experience: {len(profile['experience'])} positions")
                for exp in profile['experience'][:3]:  # Latest 3
                    context_parts.append(f"- {exp.get('title', 'Unknown')} at {exp.get('company', 'Unknown')}")
            
            if profile.get('skills'):
                context_parts.append(f"Skills: {', '.join(profile['skills'][:10])}")
            
            if profile.get('education'):
                context_parts.append(f"Education: {profile['education'][0].get('degree', 'Degree')} from {profile['education'][0].get('institution', 'University')}")
            
            context = "\n".join(context_parts)
            
            # Generate summary with AI
            prompt = f"""Generate a professional profile summary (2-3 sentences) for this person:

{context}

Write in first person, be concise and impactful. Focus on expertise and value proposition."""
            
            response = self.model.generate_content(prompt)
            summary = response.text.strip()
            
            logger.info(f"Generated summary for user {user_id}")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary for {user_id}: {e}")
            return None
    
    
    async def optimize_for_ats(self, user_id: str, job_description: str) -> List[str]:
        """
        Optimize profile for Applicant Tracking Systems
        
        Args:
            user_id: User identifier
            job_description: Target job description
            
        Returns:
            List of optimization suggestions
        """
        if not self.model:
            return ["Enable AI features to get ATS optimization suggestions"]
        
        try:
            # Get profile
            profile = await unified_profile_manager.get_unified_profile(user_id)
            if not profile:
                return []
            
            # Extract keywords from job description
            prompt = f"""Analyze this job description and extract key skills, technologies, and qualifications:

{job_description[:1000]}

Return only the comma-separated list of keywords."""
            
            response = self.model.generate_content(prompt)
            job_keywords = set(response.text.strip().lower().split(', '))
            
            # Compare with profile
            profile_keywords = set()
            if profile.get('skills'):
                profile_keywords.update([s.lower() for s in profile['skills']])
            if profile.get('summary'):
                profile_keywords.update(profile['summary'].lower().split())
            
            # Find missing keywords
            missing_keywords = job_keywords - profile_keywords
            
            suggestions = []
            
            if missing_keywords:
                suggestions.append(f"Add these keywords to your profile: {', '.join(list(missing_keywords)[:10])}")
            
            # Check for quantifiable achievements
            has_numbers = False
            if profile.get('experience'):
                for exp in profile['experience']:
                    desc = exp.get('description', '')
                    if any(char.isdigit() for char in desc):
                        has_numbers = True
                        break
            
            if not has_numbers:
                suggestions.append("Add quantifiable achievements (numbers, percentages, metrics) to stand out")
            
            # Check for action verbs
            weak_verbs = ['responsible for', 'worked on', 'helped with']
            strong_verbs = ['led', 'implemented', 'achieved', 'drove', 'increased']
            
            if profile.get('experience'):
                experience_text = ' '.join([exp.get('description', '') for exp in profile['experience']]).lower()
                if any(verb in experience_text for verb in weak_verbs):
                    suggestions.append(f"Use strong action verbs: {', '.join(strong_verbs)}")
            
            logger.info(f"Generated {len(suggestions)} ATS suggestions for user {user_id}")
            return suggestions
            
        except Exception as e:
            logger.error(f"Error optimizing for ATS: {e}")
            return []
    
    
    async def suggest_next_steps(self, user_id: str) -> List[ProfileSuggestion]:
        """
        Suggest prioritized next steps to improve profile
        
        Returns:
            Top 3-5 suggestions ordered by priority
        """
        try:
            # Get profile analysis
            analysis = await self.analyze_profile(user_id)
            
            # Sort suggestions by priority and impact
            sorted_suggestions = sorted(
                analysis.suggestions,
                key=lambda s: (s.priority, -s.impact_score)
            )
            
            # Return top 5
            return sorted_suggestions[:5]
            
        except Exception as e:
            logger.error(f"Error suggesting next steps for {user_id}: {e}")
            return []
    
    
    # === Helper Methods ===
    
    def _calculate_completeness(self, profile: Dict[str, Any]) -> float:
        """Calculate profile completeness score (0-1)"""
        required_fields = {
            'full_name': 0.05,
            'email': 0.05,
            'phone': 0.05,
            'location': 0.05,
            'summary': 0.15,
            'skills': 0.20,
            'experience': 0.25,
            'education': 0.10,
            'preferences': 0.10
        }
        
        score = 0.0
        
        for field, weight in required_fields.items():
            value = profile.get(field)
            if value:
                if isinstance(value, list) and len(value) > 0:
                    score += weight
                elif isinstance(value, str) and len(value) > 0:
                    score += weight
                elif isinstance(value, dict) and len(value) > 0:
                    score += weight
        
        return min(score, 1.0)
    
    
    def _find_missing_fields(self, profile: Dict[str, Any]) -> List[str]:
        """Find completely missing fields"""
        required = ['full_name', 'email', 'phone', 'location', 'summary', 'skills', 'experience', 'education']
        missing = []
        
        for field in required:
            value = profile.get(field)
            if not value or (isinstance(value, list) and len(value) == 0):
                missing.append(field)
        
        return missing
    
    
    def _find_incomplete_fields(self, profile: Dict[str, Any]) -> List[str]:
        """Find fields that exist but are incomplete"""
        incomplete = []
        
        # Summary too short
        if profile.get('summary') and len(profile['summary']) < 50:
            incomplete.append('summary')
        
        # Too few skills
        if profile.get('skills') and len(profile['skills']) < 5:
            incomplete.append('skills')
        
        # Experience missing descriptions
        if profile.get('experience'):
            for exp in profile['experience']:
                if not exp.get('description') or len(exp['description']) < 20:
                    incomplete.append('experience_descriptions')
                    break
        
        return list(set(incomplete))
    
    
    async def _generate_suggestions(
        self,
        profile: Dict[str, Any],
        missing: List[str],
        incomplete: List[str]
    ) -> List[ProfileSuggestion]:
        """Generate actionable suggestions"""
        suggestions = []
        
        # Missing field suggestions
        for field in missing:
            suggestions.append(ProfileSuggestion(
                field=field,
                suggestion_type='missing',
                current_value=None,
                suggested_value=f"Add your {field.replace('_', ' ')}",
                reasoning=f"Required field for complete profile",
                priority=1 if field in ['email', 'full_name'] else 2,
                impact_score=0.8
            ))
        
        # Incomplete field suggestions
        for field in incomplete:
            if field == 'summary':
                suggestions.append(ProfileSuggestion(
                    field='summary',
                    suggestion_type='incomplete',
                    current_value=profile.get('summary'),
                    suggested_value="Expand your summary to 2-3 paragraphs highlighting your expertise and goals",
                    reasoning="Strong summaries are 100-200 words",
                    priority=2,
                    impact_score=0.7
                ))
            elif field == 'skills':
                inferred = await self._infer_skills_from_experience(profile)
                suggestions.append(ProfileSuggestion(
                    field='skills',
                    suggestion_type='incomplete',
                    current_value=profile.get('skills', []),
                    suggested_value=inferred,
                    reasoning="Add more skills to match your experience",
                    priority=2,
                    impact_score=0.75
                ))
        
        return suggestions
    
    
    async def _infer_skills_from_experience(self, profile: Dict[str, Any]) -> List[str]:
        """Infer skills from job titles and descriptions"""
        if not self.model:
            return []
        
        try:
            # Build experience context
            experience_text = []
            if profile.get('experience'):
                for exp in profile['experience'][:3]:  # Latest 3
                    title = exp.get('title', '')
                    desc = exp.get('description', '')
                    experience_text.append(f"{title}: {desc}")
            
            if not experience_text:
                return []
            
            context = "\n\n".join(experience_text)
            
            # Ask AI to extract skills
            prompt = f"""Based on this work experience, list 10-15 technical and professional skills this person likely has:

{context[:1000]}

Return only comma-separated skills, no explanation."""
            
            response = self.model.generate_content(prompt)
            skills = [s.strip() for s in response.text.split(',')]
            
            return skills[:15]
            
        except Exception as e:
            logger.error(f"Error inferring skills: {e}")
            return []
    
    
    def _analyze_strengths_weaknesses(
        self,
        profile: Dict[str, Any],
        completeness: float
    ) -> Tuple[List[str], List[str]]:
        """Identify profile strengths and weaknesses"""
        strengths = []
        weaknesses = []
        
        # Strengths
        if completeness > 0.8:
            strengths.append("Highly complete profile")
        
        if profile.get('experience') and len(profile['experience']) >= 3:
            strengths.append(f"{len(profile['experience'])} positions listed")
        
        if profile.get('skills') and len(profile['skills']) >= 10:
            strengths.append(f"{len(profile['skills'])} skills listed")
        
        if profile.get('summary') and len(profile['summary']) > 100:
            strengths.append("Detailed professional summary")
        
        # Weaknesses
        if completeness < 0.5:
            weaknesses.append("Profile needs more information")
        
        if not profile.get('summary') or len(profile['summary']) < 50:
            weaknesses.append("Summary needs expansion")
        
        if not profile.get('skills') or len(profile['skills']) < 5:
            weaknesses.append("Add more skills")
        
        if profile.get('experience'):
            has_descriptions = all(exp.get('description') for exp in profile['experience'])
            if not has_descriptions:
                weaknesses.append("Some positions missing descriptions")
        
        return strengths, weaknesses
    
    
    def _get_completeness_level(self, score: float) -> ProfileCompletenessLevel:
        """Convert score to level"""
        if score >= 0.9:
            return ProfileCompletenessLevel.PERFECT
        elif score >= 0.75:
            return ProfileCompletenessLevel.EXCELLENT
        elif score >= 0.5:
            return ProfileCompletenessLevel.GOOD
        elif score >= 0.3:
            return ProfileCompletenessLevel.BASIC
        else:
            return ProfileCompletenessLevel.MINIMAL
    
    
    def _infer_location(self, profile: Dict[str, Any], context: Dict[str, Any]) -> Optional[str]:
        """Infer location from job preferences or history"""
        # Check job preferences
        if context.get('recent_goals'):
            for goal in context['recent_goals']:
                if 'location' in goal.lower():
                    # Extract location from goal text
                    # Simple heuristic - this could be improved with NLP
                    return "Remote"  # Default fallback
        
        # Check experience locations
        if profile.get('experience'):
            locations = [exp.get('location') for exp in profile['experience'] if exp.get('location')]
            if locations:
                return locations[0]  # Most recent
        
        return None
    
    
    def _infer_seniority(self, profile: Dict[str, Any]) -> Optional[str]:
        """Infer seniority level from experience"""
        if not profile.get('experience'):
            return "Entry Level"
        
        years = 0
        for exp in profile['experience']:
            if exp.get('start_date') and exp.get('end_date'):
                # Calculate years (simplified)
                years += 1  # Rough approximation
        
        if years >= 10:
            return "Senior"
        elif years >= 5:
            return "Mid-Level"
        elif years >= 2:
            return "Junior"
        else:
            return "Entry Level"
    
    
    def _infer_salary(self, profile: Dict[str, Any]) -> Optional[Dict[str, int]]:
        """Infer desired salary from seniority and skills"""
        seniority = self._infer_seniority(profile)
        
        # Very rough salary ranges (in USD)
        ranges = {
            "Entry Level": {"min": 50000, "max": 70000},
            "Junior": {"min": 60000, "max": 85000},
            "Mid-Level": {"min": 80000, "max": 120000},
            "Senior": {"min": 120000, "max": 180000}
        }
        
        return ranges.get(seniority)
    
    
    def _infer_preferences(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Infer job preferences from behavior"""
        preferences = {
            "remote": True,  # Default to remote preference
            "full_time": True,
            "part_time": False,
            "contract": False
        }
        
        # Could be enhanced by analyzing browsing patterns
        # For now, return safe defaults
        return preferences
    
    
    def _empty_analysis(self, user_id: str) -> ProfileAnalysis:
        """Return empty analysis for errors"""
        return ProfileAnalysis(
            user_id=user_id,
            completeness_level=ProfileCompletenessLevel.MINIMAL,
            completeness_score=0.0,
            missing_fields=[],
            incomplete_fields=[],
            suggestions=[],
            inferred_skills=[],
            strengths=[],
            weaknesses=[]
        )


# Global instance
profile_assistant = SmartProfileAssistant()
