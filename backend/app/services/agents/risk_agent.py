"""
Risk Agent - Survival & Stability Analysis
Calculates AI displacement/automation risk for jobs
"""

from typing import Dict, Any, List, Optional
from loguru import logger
import google.generativeai as genai

from app.core.config import settings
from app.models.orchestrator_schemas import DisplacementRiskLevel, AIDisplacementRiskOutput
from app.models.user_profile import UserProfile
from app.models.orchestrator_schemas import JobOpportunity


class RiskAgent:
    """
    Risk Agent - The survival analyst

    Responsibilities:
    - Calculate AI displacement/automation risk for target jobs
    - Flag industry-level threats (outsourcing, AI replacement)
    - Predict job stability 12-24 months out
    - Answer: "Will this role still be safe in 12-24 months?"
    """

    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    async def assess_displacement_risk(
        self, job: JobOpportunity, user_profile: Optional[UserProfile] = None
    ) -> AIDisplacementRiskOutput:
        """
        Assess AI displacement risk for a specific job

        Returns structured risk assessment with level and justification
        """
        try:
            prompt = self._build_risk_assessment_prompt(job, user_profile)

            response = self.model.generate_content(prompt)

            # Parse response
            risk_data = self._parse_risk_response(response.text, job)

            logger.info(f"Risk assessment for {job.title}: {risk_data.level}")

            return risk_data

        except Exception as e:
            logger.error(f"Error assessing displacement risk: {e}")

            # Fallback risk assessment
            return AIDisplacementRiskOutput(
                level=DisplacementRiskLevel.MEDIUM,
                justification=f"Unable to perform full risk analysis. {job.title} should be evaluated based on how much of the role requires human judgment, trust, and in-person interaction.",
            )

    def _build_risk_assessment_prompt(self, job: JobOpportunity, user_profile: Optional[UserProfile]) -> str:
        """Build the prompt for Gemini risk analysis"""

        current_context = ""
        if user_profile and user_profile.current_role:
            current_context = f"\nUser's current role: {user_profile.current_role}"

        prompt = f"""You are a career risk analyst. Assess the AI displacement risk for this job.

Job Title: {job.title}
Company: {job.company}
Location: {job.location or 'Not specified'}
Remote: {job.is_remote}
Required Skills: {', '.join(job.required_skills) if job.required_skills else 'Not specified'}
Responsibilities: {', '.join(job.responsibilities) if job.responsibilities else 'Not specified'}
{current_context}

Analyze this role's AI displacement risk for the next 12-24 months.

Consider:
1. Core tasks - can AI reasonably do 70%+ of this job's daily tasks?
2. Human factors - does this require trust, judgment, physical presence, relational skills?
3. Market trends - is this role expanding or shrinking?
4. Automation potential - are the core functions repeatable/digital or situational/human?

Return ONLY a JSON object with this exact structure:
{{
  "level": "Very Low" | "Low" | "Medium" | "High",
  "justification": "One clear sentence explaining why, focusing on core tasks and human skills required."
}}

Guidelines for risk levels:
- Very Low: Requires high-trust human interaction, physical presence, situational judgment
- Low: Requires human skills but has some automatable components
- Medium: Mix of human and automatable tasks
- High: Primarily digital, repeatable, or easily outsourced work

Be realistic and data-driven. Output ONLY valid JSON."""

        return prompt

    def _parse_risk_response(self, response_text: str, job: JobOpportunity) -> AIDisplacementRiskOutput:
        """Parse Gemini response into structured risk output"""

        import json
        import re

        try:
            # Extract JSON from response
            json_match = re.search(r"\{.*\}", response_text, re.DOTALL)

            if json_match:
                risk_data = json.loads(json_match.group())

                level_str = risk_data.get("level", "Medium")
                justification = risk_data.get("justification", "Risk analysis completed.")

                # Map to enum
                level_mapping = {
                    "Very Low": DisplacementRiskLevel.VERY_LOW,
                    "Low": DisplacementRiskLevel.LOW,
                    "Medium": DisplacementRiskLevel.MEDIUM,
                    "High": DisplacementRiskLevel.HIGH,
                }

                level = level_mapping.get(level_str, DisplacementRiskLevel.MEDIUM)

                return AIDisplacementRiskOutput(level=level, justification=justification)
            else:
                raise ValueError("No JSON found in response")

        except Exception as e:
            logger.error(f"Error parsing risk response: {e}")

            # Fallback based on job characteristics
            return self._fallback_risk_assessment(job)

    def _fallback_risk_assessment(self, job: JobOpportunity) -> AIDisplacementRiskOutput:
        """
        Fallback risk assessment when AI call fails
        Uses heuristics based on job characteristics
        """

        # Keywords indicating low automation risk
        low_risk_keywords = [
            "coach",
            "mentor",
            "counsel",
            "therapist",
            "nurse",
            "teacher",
            "trainer",
            "facilitator",
            "mediator",
            "manager",
            "leader",
            "director",
            "supervisor",
            "field",
            "on-site",
            "in-person",
            "physical",
        ]

        # Keywords indicating high automation risk
        high_risk_keywords = [
            "data entry",
            "transcription",
            "basic",
            "routine",
            "clerical",
            "administrative assistant",
            "receptionist",
        ]

        title_lower = job.title.lower()
        responsibilities_text = " ".join(job.responsibilities).lower() if job.responsibilities else ""

        combined_text = f"{title_lower} {responsibilities_text}"

        # Check for low risk indicators
        if any(keyword in combined_text for keyword in low_risk_keywords):
            return AIDisplacementRiskOutput(
                level=DisplacementRiskLevel.LOW,
                justification=f"This role appears to require human-centric skills like coaching, leadership, or in-person interaction, which are difficult to automate.",
            )

        # Check for high risk indicators
        if any(keyword in combined_text for keyword in high_risk_keywords):
            return AIDisplacementRiskOutput(
                level=DisplacementRiskLevel.HIGH,
                justification=f"This role involves primarily routine, digital tasks that may be susceptible to automation.",
            )

        # Default to medium
        return AIDisplacementRiskOutput(
            level=DisplacementRiskLevel.MEDIUM,
            justification=f"{job.title} likely has a mix of human and automatable tasks. Evaluate based on specific responsibilities.",
        )

    async def assess_current_job_risk(self, user_profile: UserProfile) -> Dict[str, Any]:
        """
        Assess displacement risk for user's CURRENT job
        This helps identify if they need to move urgently
        """

        if not user_profile.current_role:
            return {"risk_level": "Unknown", "justification": "No current role specified in profile."}

        # Create a pseudo job object from current role
        current_job = JobOpportunity(
            title=user_profile.current_role,
            company=user_profile.current_company or "Current employer",
            required_skills=[s.name for s in user_profile.skills[:10]],
            is_remote=user_profile.remote_preference == "remote_only" if user_profile.remote_preference else False,
        )

        risk = await self.assess_displacement_risk(current_job, user_profile)

        return {
            "risk_level": risk.level.value,
            "justification": risk.justification,
            "should_consider_transition": risk.level in [DisplacementRiskLevel.HIGH, DisplacementRiskLevel.MEDIUM],
        }
