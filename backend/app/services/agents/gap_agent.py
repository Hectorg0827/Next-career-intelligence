"""
Gap Agent - Growth & Training Analysis
Identifies missing skills and creates actionable development plans
"""

from typing import Dict, Any, List
from loguru import logger
import google.generativeai as genai

from app.core.config import settings
from app.models.user_profile import UserProfile
from app.models.orchestrator_schemas import JobOpportunity, SkillGap, GapSeverity


class GapAgent:
    """
    Gap Agent - The growth strategist
    
    Responsibilities:
    - Identify missing skills or experience
    - Label gap severity (minor, medium, critical)
    - Generate positioning advice (how to sell yourself anyway)
    - Create actionable next steps
    - Answer: "What's missing and how do we fix it?"
    """
    
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    async def analyze_gaps(
        self,
        user_profile: UserProfile,
        job: JobOpportunity
    ) -> Dict[str, Any]:
        """
        Analyze skill and experience gaps
        
        Returns:
        - skill_gaps_for_job: List of SkillGap objects
        - next_steps_for_user: Concrete actions to take
        """
        
        # Identify missing skills
        gaps = self._identify_skill_gaps(user_profile, job)
        
        # Use AI to enrich gaps with positioning advice and next steps
        enriched_gaps, next_steps = await self._enrich_with_ai(
            user_profile, job, gaps
        )
        
        logger.info(f"Identified {len(enriched_gaps)} gaps for {job.title}")
        
        return {
            "skill_gaps_for_job": enriched_gaps,
            "next_steps_for_user": next_steps
        }
    
    def _identify_skill_gaps(
        self,
        user_profile: UserProfile,
        job: JobOpportunity
    ) -> List[Dict[str, Any]]:
        """
        Identify which required skills the user doesn't have
        """
        
        if not job.required_skills:
            return []
        
        user_skill_names = [s.name.lower() for s in user_profile.skills]
        user_competencies = [c.lower() for c in user_profile.core_competencies]
        user_all_skills = set(user_skill_names + user_competencies)
        
        gaps = []
        
        for required_skill in job.required_skills:
            required_lower = required_skill.lower()
            
            # Check if user has this skill (exact or partial match)
            has_skill = False
            
            if required_lower in user_all_skills:
                has_skill = True
            else:
                # Check for partial matches
                for user_skill in user_all_skills:
                    if required_lower in user_skill or user_skill in required_lower:
                        has_skill = True
                        break
            
            if not has_skill:
                # Determine severity heuristically
                severity = self._determine_gap_severity(required_skill, job, user_profile)
                
                gaps.append({
                    "skill_or_experience": required_skill,
                    "severity": severity
                })
        
        return gaps
    
    def _determine_gap_severity(
        self,
        missing_skill: str,
        job: JobOpportunity,
        user_profile: UserProfile
    ) -> GapSeverity:
        """
        Determine if a gap is minor, medium, or critical
        """
        
        skill_lower = missing_skill.lower()
        
        # Critical gaps: certifications, licenses, years of specific experience
        critical_keywords = ["certified", "license", "clearance", "degree", "phd", "md"]
        if any(keyword in skill_lower for keyword in critical_keywords):
            return GapSeverity.CRITICAL
        
        # Minor gaps: tools, software, processes that can be learned quickly
        minor_keywords = ["software", "platform", "tool", "system", "basic", "familiarity"]
        if any(keyword in skill_lower for keyword in minor_keywords):
            return GapSeverity.MINOR
        
        # Default to medium
        return GapSeverity.MEDIUM
    
    async def _enrich_with_ai(
        self,
        user_profile: UserProfile,
        job: JobOpportunity,
        gaps: List[Dict[str, Any]]
    ) -> tuple[List[SkillGap], List[str]]:
        """
        Use AI to add positioning advice and next steps
        """
        
        try:
            prompt = self._build_gap_analysis_prompt(user_profile, job, gaps)
            
            response = self.model.generate_content(prompt)
            
            enriched_gaps, next_steps = self._parse_gap_response(response.text, gaps)
            
            return enriched_gaps, next_steps
            
        except Exception as e:
            logger.error(f"Error enriching gaps with AI: {e}")
            
            # Fallback: create basic gaps without AI enrichment
            return self._create_fallback_gaps(gaps), self._create_fallback_next_steps(user_profile, job)
    
    def _build_gap_analysis_prompt(
        self,
        user_profile: UserProfile,
        job: JobOpportunity,
        gaps: List[Dict[str, Any]]
    ) -> str:
        """Build prompt for AI gap analysis"""
        
        user_skills = [s.name for s in user_profile.skills[:10]]
        gap_list = [g["skill_or_experience"] for g in gaps]
        
        prompt = f"""You are a career coach. Help this person position themselves for a job despite skill gaps.

User Profile:
- Current Role: {user_profile.current_role or 'Not specified'}
- Years Experience: {user_profile.years_total_experience or 'Not specified'}
- Skills: {', '.join(user_skills)}

Target Job:
- Title: {job.title}
- Required Skills: {', '.join(job.required_skills) if job.required_skills else 'Not specified'}

Missing Skills (gaps):
{', '.join(gap_list) if gap_list else 'None identified'}

For each gap, provide:
1. How long to close it (e.g., "2 weeks", "3 months", "requires certification")
2. Positioning advice: How the user can sell themselves despite this gap

Also provide 3-5 concrete next steps the user should take immediately to prepare for this role.

Return ONLY a JSON object with this structure:
{{
  "gaps": [
    {{
      "skill": "skill name",
      "time_to_close": "2 weeks",
      "positioning_advice": "Say: 'I'm familiar with similar systems and can learn this quickly.'"
    }}
  ],
  "next_steps": [
    "Position yourself as X, not just Y.",
    "Collect 1-2 success stories demonstrating Z.",
    "Get basic familiarity with tool X."
  ]
}}

Be practical, specific, and actionable. Output ONLY valid JSON."""

        return prompt
    
    def _parse_gap_response(
        self,
        response_text: str,
        original_gaps: List[Dict[str, Any]]
    ) -> tuple[List[SkillGap], List[str]]:
        """Parse AI response into SkillGap objects and next steps"""
        
        import json
        import re
        
        try:
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            
            if json_match:
                data = json.loads(json_match.group())
                
                # Parse gaps
                skill_gaps = []
                for gap_data in data.get("gaps", []):
                    # Find original severity
                    skill_name = gap_data.get("skill", "")
                    severity = GapSeverity.MEDIUM
                    
                    for orig_gap in original_gaps:
                        if orig_gap["skill_or_experience"].lower() in skill_name.lower():
                            severity = orig_gap["severity"]
                            break
                    
                    skill_gaps.append(SkillGap(
                        skill_or_experience=skill_name,
                        severity=severity,
                        time_to_close=gap_data.get("time_to_close", "Unknown"),
                        positioning_advice=gap_data.get("positioning_advice")
                    ))
                
                # Parse next steps
                next_steps = data.get("next_steps", [])
                
                return skill_gaps, next_steps
            else:
                raise ValueError("No JSON found")
                
        except Exception as e:
            logger.error(f"Error parsing gap response: {e}")
            return self._create_fallback_gaps(original_gaps), []
    
    def _create_fallback_gaps(self, gaps: List[Dict[str, Any]]) -> List[SkillGap]:
        """Create basic SkillGap objects without AI enrichment"""
        
        skill_gaps = []
        
        for gap in gaps:
            severity = gap.get("severity", GapSeverity.MEDIUM)
            
            # Simple time estimates
            if severity == GapSeverity.MINOR:
                time_to_close = "1-2 weeks"
            elif severity == GapSeverity.MEDIUM:
                time_to_close = "1-3 months"
            else:
                time_to_close = "3+ months or requires certification"
            
            skill_gaps.append(SkillGap(
                skill_or_experience=gap["skill_or_experience"],
                severity=severity,
                time_to_close=time_to_close,
                positioning_advice=None
            ))
        
        return skill_gaps
    
    def _create_fallback_next_steps(
        self,
        user_profile: UserProfile,
        job: JobOpportunity
    ) -> List[str]:
        """Create basic next steps when AI fails"""
        
        next_steps = []
        
        # Generic but useful advice
        if user_profile.current_role:
            next_steps.append(
                f"Position yourself as someone who brings {user_profile.current_role} experience "
                f"to {job.title}, highlighting transferable skills."
            )
        
        next_steps.append(
            "Review the job description and prepare 2-3 specific examples "
            "from your experience that match their requirements."
        )
        
        if job.company:
            next_steps.append(
                f"Research {job.company}'s mission and values to show alignment in your application."
            )
        
        return next_steps
