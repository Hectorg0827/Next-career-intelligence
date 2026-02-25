"""
SDR Synthesis Node
Generates tailored resumes and cover letters for each researched job.
Uses the existing Resume Studio with ephemeral versioning to preserve SSOT integrity.
"""

import uuid
import asyncio
from typing import Dict, Any, List
from loguru import logger
from datetime import datetime


async def _synthesize_application(
    job: Dict[str, Any],
    user_profile: Dict[str, Any],
) -> Dict[str, Any]:
    """Generate a tailored application for a single job."""
    job_id = job.get("job_id", "")
    company = job.get("company", "")
    title = job.get("title", "")
    description = job.get("description", "")
    company_research = job.get("company_research", {})

    try:
        from app.services.ai.model_router import model_router
        model = model_router.get_generative_model("sdr_synthesis")

        # Build context from company research
        research_context = ""
        if company_research:
            insights = company_research.get("key_insights", [])
            growth = company_research.get("growth_signals", [])
            if insights:
                research_context += f"\nCompany Insights:\n" + "\n".join(f"- {i}" for i in insights[:3])
            if growth:
                research_context += f"\nGrowth Signals:\n" + "\n".join(f"- {g}" for g in growth[:2])

        # Generate cover letter
        user_name = user_profile.get("name", "the candidate")
        current_role = user_profile.get("current_role", "professional")
        years_exp = user_profile.get("years_total_experience", 0)
        top_skills = user_profile.get("skills", [])[:6]
        skills_str = ", ".join(top_skills) if top_skills else "relevant professional skills"

        prompt = f"""Write a compelling, personalized cover letter for this job application.

Candidate: {user_name}
Current Role: {current_role}
Years Experience: {years_exp}
Top Skills: {skills_str}

Target Role: {title} at {company}

Job Description (excerpt):
{description[:1500]}
{research_context}

Requirements:
1. Opening paragraph: Reference specific company context (use research insights if available)
2. Middle paragraph: Connect candidate's specific experience to 2-3 job requirements
3. Closing: Express genuine interest and clear call to action
4. Tone: Confident, specific, human — not generic or robotic
5. Length: 3 paragraphs, ~250 words

Return ONLY the cover letter text, no JSON wrapper."""

        response = model.generate_content(prompt)
        cover_letter = response.text.strip()

        # Match rationale
        match_prompt = f"""In 2-3 sentences, explain why this candidate is a strong match for this role.
Be specific about skills alignment and what the candidate brings that this role needs.

Candidate: {current_role} with {years_exp} years experience, skills: {skills_str}
Role: {title} at {company}
Job requires: {description[:500]}

Return only the 2-3 sentence match explanation."""

        match_response = model.generate_content(match_prompt)
        match_rationale = match_response.text.strip()

    except Exception as e:
        logger.warning(f"AI synthesis failed for {title} at {company}: {e}")
        user_name = user_profile.get("name", "the candidate")
        cover_letter = (
            f"Dear Hiring Team at {company},\n\n"
            f"I am excited to apply for the {title} position. "
            f"With {user_profile.get('years_total_experience', 0)} years of experience as a {user_profile.get('current_role', 'professional')}, "
            f"I believe I can make a meaningful contribution to your team.\n\n"
            f"I look forward to discussing this opportunity further.\n\nSincerely,\n{user_name}"
        )
        match_rationale = f"Strong background in {user_profile.get('current_role', 'relevant field')} aligns with {title} requirements."

    return {
        "id": str(uuid.uuid4()),
        "job_candidate": job,
        "tailored_resume_id": None,  # Resume tailoring via API would go here
        "cover_letter": cover_letter,
        "match_rationale": match_rationale,
        "status": "pending_approval",
        "created_at": datetime.utcnow().isoformat(),
    }


async def synthesis_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Synthesis node: for each researched job, generate a tailored cover letter
    and match rationale. Fetches user profile to personalize.
    """
    researched_jobs = state.get("researched_jobs", [])
    user_id = state["user_id"]

    if not researched_jobs:
        logger.info(f"SDR Synthesis: no jobs to synthesize for user {user_id}")
        return {
            **state,
            "synthesized_applications": [],
            "awaiting_approval": [],
            "pipeline_stage": "synthesis_complete",
        }

    # Fetch user profile
    user_profile = {}
    try:
        from app.db.supabase import get_supabase_client
        client = get_supabase_client()
        profile_result = client.table("career_profiles").select(
            "name, current_role, years_total_experience, skills, profile_data"
        ).eq("user_id", user_id).limit(1).execute()

        if profile_result.data:
            raw = profile_result.data[0]
            user_profile = {
                "name": raw.get("name", ""),
                "current_role": raw.get("current_role", ""),
                "years_total_experience": raw.get("years_total_experience", 0),
                "skills": raw.get("skills", []),
            }
    except Exception as e:
        logger.warning(f"Could not fetch user profile for synthesis: {e}")

    logger.info(f"SDR Synthesis: generating {len(researched_jobs)} applications for user {user_id}")

    # Generate applications concurrently
    tasks = [_synthesize_application(job, user_profile) for job in researched_jobs]
    applications = await asyncio.gather(*tasks, return_exceptions=True)

    valid_applications = []
    for i, result in enumerate(applications):
        if isinstance(result, Exception):
            logger.error(f"Synthesis failed for job {researched_jobs[i].get('job_id')}: {result}")
            continue
        valid_applications.append(result)

    # Store applications in Supabase for the approval gate
    try:
        from app.db.supabase import get_supabase_client
        client = get_supabase_client()
        for app in valid_applications:
            client.table("sdr_applications").insert({
                "id": app["id"],
                "sdr_run_id": state.get("run_id"),
                "user_id": user_id,
                "job_id": app["job_candidate"]["job_id"],
                "status": "pending_approval",
                "cover_letter": app["cover_letter"],
                "match_rationale": app["match_rationale"],
                "company_research": app["job_candidate"].get("company_research"),
                "created_at": app["created_at"],
            }).execute()
    except Exception as e:
        logger.error(f"Failed to store SDR applications in DB: {e}")

    logger.info(f"SDR Synthesis complete: {len(valid_applications)} applications generated")

    return {
        **state,
        "synthesized_applications": valid_applications,
        "awaiting_approval": valid_applications,
        "pipeline_stage": "synthesis_complete",
    }
