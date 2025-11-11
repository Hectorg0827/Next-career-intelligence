"""
Talent Graph API

Endpoints for Neo4j-powered career intelligence:
- Skill gap analysis
- Career pathway discovery
- Skill recommendations
- Market intelligence
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from app.core.neo4j_client import neo4j_client
from app.services.auth import get_current_user
from app.db.supabase import get_supabase_client
from loguru import logger
from typing import List, Optional

router = APIRouter(prefix="/api/talent-graph", tags=["talent_graph"])


async def get_user_profile(user_id: str):
    """Helper to fetch user profile"""
    response = supabase.table("career_profiles").select("*").eq("user_id", user_id).execute()
    if response.data:
        return response.data[0]
    return {}


@router.get("/skill-gaps")
async def get_skill_gaps(
    target_role: str = Query(..., description="Target job title (e.g., 'Software Engineer')"),
    target_seniority: str = Query("mid", description="Target seniority: entry/mid/senior/staff"),
    current_user = Depends(get_current_user)
):
    """
    Get skill gaps for target role

    This endpoint uses the Neo4j Talent Graph to find skills that:
    1. The target role requires
    2. The user doesn't currently have

    Returns prioritized list with learning recommendations.
    """
    try:
        # Check Neo4j health
        is_healthy = await neo4j_client.health_check()
        if not is_healthy:
            raise HTTPException(
                status_code=503,
                detail="Talent Graph is currently unavailable. Please try again later."
            )

        # Get user profile
        profile = await get_user_profile(current_user.id)
        user_skills = profile.get("skills", [])

        # Ensure user node exists in graph
        await neo4j_client.create_user_node(current_user.id, profile)

        # Link user's skills
        if user_skills:
            await neo4j_client.link_user_skills(current_user.id, user_skills)

        # Get skill gaps
        gaps = await neo4j_client.get_skill_gaps(
            user_id=current_user.id,
            target_role=target_role,
            target_seniority=target_seniority
        )

        # Enrich with learning recommendations
        for gap in gaps:
            gap["learning_time_estimate"] = _estimate_learning_time(gap.get("learning_curve", "moderate"))
            gap["priority"] = _calculate_priority(gap)

        return {
            "user_id": current_user.id,
            "current_skills": user_skills,
            "target_role": target_role,
            "target_seniority": target_seniority,
            "skill_gaps": gaps,
            "total_gaps": len(gaps),
            "high_priority_gaps": [g for g in gaps if g["priority"] == "high"],
            "estimated_learning_time": sum(gap["learning_time_estimate"] for gap in gaps[:5])
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get skill gaps: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze skill gaps")


@router.get("/career-pathways")
async def get_career_pathways(
    target_role: str = Query(..., description="Target job title"),
    target_seniority: str = Query("senior", description="Target seniority level"),
    current_user = Depends(get_current_user)
):
    """
    Get possible career pathways from current role to target

    Returns multiple pathways with:
    - Steps (intermediate roles)
    - Time estimates
    - Success rates
    - Required skill acquisitions per step
    """
    try:
        is_healthy = await neo4j_client.health_check()
        if not is_healthy:
            raise HTTPException(status_code=503, detail="Talent Graph unavailable")

        # Get user's current role
        profile = await get_user_profile(current_user.id)
        current_role = profile.get("current_role", "Software Engineer")
        current_seniority = _infer_seniority(profile.get("experience_years", 0))

        # Get pathways
        pathways = await neo4j_client.get_career_pathways(
            current_role=current_role,
            current_seniority=current_seniority,
            target_role=target_role,
            target_seniority=target_seniority
        )

        # Enrich pathways with skill requirements
        for pathway in pathways:
            pathway["steps_detail"] = []
            for i in range(len(pathway["roles"]) - 1):
                from_role = pathway["roles"][i]
                to_role = pathway["roles"][i + 1]

                # Get skills needed for next step
                # (simplified - in production, query graph for each step)
                pathway["steps_detail"].append({
                    "from": from_role,
                    "to": to_role,
                    "years": pathway["years_per_step"][i] if i < len(pathway["years_per_step"]) else 0,
                    "skills_to_acquire": []  # TODO: Query graph for skill requirements
                })

        return {
            "user_id": current_user.id,
            "current_role": f"{current_role} ({current_seniority})",
            "target_role": f"{target_role} ({target_seniority})",
            "pathways": pathways,
            "recommended_pathway": pathways[0] if pathways else None
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get career pathways: {e}")
        raise HTTPException(status_code=500, detail="Failed to find career pathways")


@router.get("/skills/{skill_name}/related")
async def get_related_skills(
    skill_name: str,
    limit: int = Query(10, ge=1, le=50)
):
    """
    Get skills commonly learned together with given skill

    Useful for:
    - Skill recommendations
    - Learning pathway suggestions
    - Curriculum planning
    """
    try:
        is_healthy = await neo4j_client.health_check()
        if not is_healthy:
            raise HTTPException(status_code=503, detail="Talent Graph unavailable")

        related = await neo4j_client.get_related_skills(skill_name, radius=2, limit=limit)

        return {
            "skill": skill_name,
            "related_skills": related,
            "count": len(related),
            "recommendation": _generate_skill_recommendation(skill_name, related)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get related skills: {e}")
        raise HTTPException(status_code=500, detail="Failed to find related skills")


@router.get("/skills/{skill_name}/market-data")
async def get_skill_market_data(skill_name: str):
    """
    Get market intelligence for a skill

    Returns:
    - Demand score
    - Growth rate
    - Salary premium
    - Automation risk
    - Learning difficulty
    - Number of roles requiring skill
    """
    try:
        is_healthy = await neo4j_client.health_check()
        if not is_healthy:
            raise HTTPException(status_code=503, detail="Talent Graph unavailable")

        market_data = await neo4j_client.get_skill_market_data(skill_name)

        if not market_data:
            raise HTTPException(status_code=404, detail=f"Skill '{skill_name}' not found in graph")

        # Add insights
        market_data["insights"] = _generate_skill_insights(market_data)

        return market_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get skill market data: {e}")
        raise HTTPException(status_code=500, detail="Failed to get market data")


@router.post("/users/me/sync-profile")
async def sync_user_profile(current_user = Depends(get_current_user)):
    """
    Sync user profile to Talent Graph

    Creates/updates user node and skill relationships in Neo4j.
    Should be called after profile updates.
    """
    try:
        is_healthy = await neo4j_client.health_check()
        if not is_healthy:
            raise HTTPException(status_code=503, detail="Talent Graph unavailable")

        # Get user profile
        profile = await get_user_profile(current_user.id)

        # Create user node
        await neo4j_client.create_user_node(current_user.id, profile)

        # Link skills
        skills = profile.get("skills", [])
        if skills:
            linked_count = await neo4j_client.link_user_skills(current_user.id, skills)
        else:
            linked_count = 0

        return {
            "status": "synced",
            "user_id": current_user.id,
            "skills_linked": linked_count,
            "message": "Profile synced to Talent Graph successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to sync user profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to sync profile")


@router.get("/stats")
async def get_graph_stats():
    """
    Get Talent Graph statistics

    Returns:
    - Node counts by type
    - Relationship counts
    - Graph size
    """
    try:
        is_healthy = await neo4j_client.health_check()
        if not is_healthy:
            return {
                "status": "unhealthy",
                "message": "Talent Graph is currently unavailable"
            }

        stats = await neo4j_client.get_graph_stats()

        return {
            "status": "healthy",
            **stats
        }

    except Exception as e:
        logger.error(f"Failed to get graph stats: {e}")
        return {
            "status": "error",
            "message": str(e)
        }


# ========================================
# Helper Functions
# ========================================

def _estimate_learning_time(learning_curve: str) -> int:
    """Estimate learning time in weeks"""
    mapping = {
        "easy": 2,
        "moderate": 4,
        "steep": 8,
        "lifelong": 52
    }
    return mapping.get(learning_curve, 4)


def _calculate_priority(gap: Dict) -> str:
    """Calculate priority level for skill gap"""
    importance = gap.get("importance", 0.5)
    demand = gap.get("demand_score", 50)

    score = (importance * 0.6) + (demand / 100 * 0.4)

    if score >= 0.8:
        return "high"
    elif score >= 0.6:
        return "medium"
    else:
        return "low"


def _infer_seniority(years: int) -> str:
    """Infer seniority from years of experience"""
    if years <= 2:
        return "entry"
    elif years <= 5:
        return "mid"
    elif years <= 10:
        return "senior"
    else:
        return "staff"


def _generate_skill_recommendation(skill: str, related: List[Dict]) -> str:
    """Generate human-readable skill recommendation"""
    if not related:
        return f"No related skills found for {skill}"

    top_3 = [s["skill"] for s in related[:3]]
    return f"Professionals with {skill} often also learn: {', '.join(top_3)}"


def _generate_skill_insights(market_data: Dict) -> List[str]:
    """Generate insights from market data"""
    insights = []

    # Demand insight
    demand = market_data.get("demand_score", 0)
    if demand >= 90:
        insights.append("🔥 Extremely high demand - top 10% of skills")
    elif demand >= 75:
        insights.append("⭐ High demand - actively sought by employers")
    elif demand < 50:
        insights.append("⚠️ Lower demand - consider pairing with in-demand skills")

    # Growth insight
    growth = market_data.get("growth_rate", 0)
    if growth >= 0.3:
        insights.append("📈 Rapidly growing - future-proof skill")
    elif growth <= 0:
        insights.append("📉 Declining - may be becoming less relevant")

    # Salary insight
    salary_premium = market_data.get("salary_premium", 0)
    if salary_premium >= 20000:
        insights.append(f"💰 High salary premium: +${salary_premium:,}/year on average")

    # Automation risk
    auto_risk = market_data.get("automation_risk", 0)
    if auto_risk <= 0.2:
        insights.append("🛡️ Low automation risk - human advantage")
    elif auto_risk >= 0.5:
        insights.append("⚠️ Higher automation risk - focus on creative/strategic aspects")

    return insights
