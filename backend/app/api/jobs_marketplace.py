"""
Jobs Marketplace API
Real jobs with AI matching, auto-tailor resume, auto-generate cover letter
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from loguru import logger
import json

from app.db.supabase import get_supabase_client
from app.services.job_matcher import job_matcher
from app.services.gemini_analyzer import gemini_analyzer
from app.services.prompts import get_prompt_set
from app.core.auth import get_current_user, require_premium
from app.core.cache import cache, cached

router = APIRouter(prefix="/jobs", tags=["Jobs Marketplace - Premium"])


# ========================================
# PYDANTIC MODELS
# ========================================

from pydantic import BaseModel

class JobSearchRequest(BaseModel):
    query: Optional[str] = None
    location: Optional[str] = None
    remote_only: bool = False
    salary_min: Optional[int] = None
    seniority: Optional[List[str]] = None
    limit: int = 20
    offset: int = 0


class JobApplicationRequest(BaseModel):
    user_id: str
    job_id: str
    auto_tailor: bool = True  # Auto-generate tailored resume
    auto_cover_letter: bool = True  # Auto-generate cover letter


class UpdatePreferencesRequest(BaseModel):
    desired_titles: Optional[List[str]] = None
    desired_industries: Optional[List[str]] = None
    desired_locations: Optional[List[str]] = None
    remote_only: Optional[bool] = None
    salary_min: Optional[int] = None
    auto_apply_enabled: Optional[bool] = None


# ========================================
# HELPER FUNCTIONS
# ========================================

async def get_user_profile(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user's career profile"""
    try:
        client = get_supabase_client()
        if not client:
            return None

        # Check cache first
        cached_profile = await cache.get("profile", user_id)
        if cached_profile:
            return cached_profile

        response = client.table('career_profiles')\
            .select('*')\
            .eq('user_id', user_id)\
            .single()\
            .execute()

        profile = response.data if response.data else None

        if profile:
            await cache.set("profile", user_id, profile, ttl=3600)

        return profile

    except Exception as e:
        logger.error(f"Get profile error: {e}")
        return None


async def get_user_preferences(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user's job preferences"""
    try:
        client = get_supabase_client()
        if not client:
            return None

        response = client.table('user_job_preferences')\
            .select('*')\
            .eq('user_id', user_id)\
            .single()\
            .execute()

        return response.data if response.data else None

    except Exception as e:
        logger.error(f"Get preferences error: {e}")
        return None


# ========================================
# ENDPOINTS
# ========================================

@router.get("/search")
async def search_jobs(
    query: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    remote_only: bool = Query(False),
    salary_min: Optional[int] = Query(None),
    limit: int = Query(20, le=100),
    offset: int = Query(0),
    current_user: Dict = Depends(get_current_user)
):
    """
    Search for jobs with filters
    Public search (no matching/ranking)
    """
    try:
        client = get_supabase_client()
        if not client:
            raise HTTPException(503, "Database unavailable")

        # Build query
        query_builder = client.table('jobs')\
            .select('*, employers(name, logo_url, domain)')\
            .eq('status', 'active')\
            .eq('is_spam', False)

        # Apply filters
        if remote_only:
            query_builder = query_builder.eq('location_type', 'remote')

        if location:
            query_builder = query_builder.or_(
                f"location_city.ilike.%{location}%,"
                f"location_state.ilike.%{location}%,"
                f"location_country.ilike.%{location}%"
            )

        if salary_min:
            query_builder = query_builder.gte('salary_max', salary_min)

        # Text search if query provided
        if query:
            query_builder = query_builder.or_(
                f"title.ilike.%{query}%,"
                f"description.ilike.%{query}%"
            )

        # Execute with pagination
        response = query_builder\
            .order('posted_at', desc=True)\
            .range(offset, offset + limit - 1)\
            .execute()

        jobs = response.data if response.data else []

        return {
            "jobs": jobs,
            "total": len(jobs),
            "offset": offset,
            "limit": limit
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Job search error: {e}")
        raise HTTPException(500, f"Search failed: {str(e)}")


@router.get("/recommendations")
async def get_recommendations(
    user_id: Optional[str] = Query(None),
    refresh: bool = Query(False),
    limit: int = Query(20, le=100),
    min_skill_match: float = Query(30.0, ge=0, le=100, description="Minimum skill match % (default 30%)"),
    max_distance_km: Optional[float] = Query(None, ge=0, description="Maximum distance in km (None = no limit)"),
    expand_search: bool = Query(False, description="Expand search beyond strict filters"),
    current_user: Dict = Depends(require_premium)
):
    """
    Get AI-matched job recommendations with intelligent filtering

    Premium feature - uses multi-objective matching with:
    1. Goals alignment - Jobs that help achieve career goals
    2. Skill match - Minimum skill overlap threshold
    3. Distance filter - Location-based filtering (if not remote)
    4. AI Displacement Risk - Shows % risk for each job

    Set expand_search=true to see more jobs beyond strict filters
    """
    try:
        user_id = user_id or current_user['user_id']

        # Get profile and preferences
        profile = await get_user_profile(user_id)
        if not profile:
            raise HTTPException(404, "Profile not found. Please create profile first.")

        preferences = await get_user_preferences(user_id)

        client = get_supabase_client()
        if not client:
            raise HTTPException(503, "Database unavailable")

        # Check for cached recommendations (if not refreshing and no custom filters)
        if not refresh and not max_distance_km and min_skill_match == 30.0 and not expand_search:
            cached_recs = await cache.get("recommendations", user_id)
            if cached_recs:
                return cached_recs

        # Get user's active goals
        try:
            goals_response = client.table('career_goals')\
                .select('*')\
                .eq('user_id', user_id)\
                .eq('status', 'active')\
                .execute()
            user_goals = goals_response.data if goals_response.data else []
        except Exception as e:
            logger.warning(f"Failed to fetch goals: {e}")
            user_goals = []

        # Get user location from profile or preferences
        user_lat = None
        user_lon = None
        if preferences:
            user_lat = preferences.get('home_latitude')
            user_lon = preferences.get('home_longitude')

        # If not in preferences, try profile
        if not user_lat or not user_lon:
            profile_data = profile.get('profile_data', {})
            user_lat = profile_data.get('latitude')
            user_lon = profile_data.get('longitude')

        # Get active jobs (larger pool for filtering)
        jobs_response = client.table('jobs')\
            .select('*')\
            .eq('status', 'active')\
            .eq('is_spam', False)\
            .limit(200)\
            .execute()

        jobs = jobs_response.data if jobs_response.data else []

        logger.info(f"🔍 Filtering {len(jobs)} jobs for user {user_id}")
        logger.info(f"   Filters: skill_match≥{min_skill_match}%, distance≤{max_distance_km}km, goals={len(user_goals)}")

        # Apply intelligent filtering
        if expand_search:
            # Expanded search - loosen filters
            filtered_jobs = await job_matcher.filter_jobs_by_criteria(
                jobs=jobs,
                user_profile=profile,
                user_goals=user_goals,
                user_preferences=preferences,
                min_skill_match=max(10.0, min_skill_match - 20),  # Lower threshold
                max_distance_km=max_distance_km * 2 if max_distance_km else None,  # Double distance
                user_lat=user_lat,
                user_lon=user_lon
            )
        else:
            # Strict filtering
            filtered_jobs = await job_matcher.filter_jobs_by_criteria(
                jobs=jobs,
                user_profile=profile,
                user_goals=user_goals,
                user_preferences=preferences,
                min_skill_match=min_skill_match,
                max_distance_km=max_distance_km,
                user_lat=user_lat,
                user_lon=user_lon
            )

        logger.info(f"✅ {len(filtered_jobs)} jobs matched filters")

        # Take top N
        top_recommendations = filtered_jobs[:limit]

        # Save recommendations to database
        for idx, job_rec in enumerate(top_recommendations):
            try:
                client.table('job_recommendations').upsert({
                    'user_id': user_id,
                    'job_id': job_rec['id'],
                    'overall_score': job_rec['match_score'],
                    'skill_fit_score': job_rec['match_details'].get('skill_fit_score'),
                    'trajectory_fit_score': job_rec['match_details'].get('trajectory_fit_score'),
                    'value_match_score': job_rec['match_details'].get('value_match_score'),
                    'logistics_fit_score': job_rec['match_details'].get('logistics_fit_score'),
                    'growth_potential_score': job_rec['match_details'].get('growth_potential_score'),
                    'match_highlights': job_rec['match_details'].get('match_highlights', []),
                    'skill_gaps': job_rec['match_details'].get('skill_gaps', []),
                    'why_matched': job_rec['match_details'].get('why_matched'),
                    'displacement_risk_improvement': job_rec['match_details'].get('displacement_risk_improvement'),
                    'rank_position': idx + 1,
                    'status': 'pending'
                }).execute()
            except Exception as e:
                logger.error(f"Failed to save recommendation: {e}")

        result = {
            "recommendations": top_recommendations,
            "total": len(top_recommendations),
            "total_before_filtering": len(jobs),
            "filters_applied": {
                "min_skill_match": min_skill_match,
                "max_distance_km": max_distance_km,
                "goals_count": len(user_goals),
                "expand_search": expand_search
            },
            "user_goals": [{"id": g.get('id'), "title": g.get('title')} for g in user_goals],
            "profile_id": profile['id']
        }

        # Cache for 1 hour (only if default filters)
        if not max_distance_km and min_skill_match == 30.0 and not expand_search:
            await cache.set("recommendations", user_id, result, ttl=3600)

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Recommendations error: {e}")
        raise HTTPException(500, f"Failed to generate recommendations: {str(e)}")


@router.get("/jobs/{job_id}")
async def get_job_details(
    job_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Get detailed job information"""
    try:
        client = get_supabase_client()
        if not client:
            raise HTTPException(503, "Database unavailable")

        response = client.table('jobs')\
            .select('*, employers(name, logo_url, domain, description, website)')\
            .eq('id', job_id)\
            .single()\
            .execute()

        if not response.data:
            raise HTTPException(404, "Job not found")

        return response.data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get job error: {e}")
        raise HTTPException(500, str(e))


@router.post("/apply")
async def apply_to_job(
    request: JobApplicationRequest,
    current_user: Dict = Depends(require_premium)
):
    """
    Apply to job with auto-tailored resume and cover letter
    Premium feature - automatically customizes application materials
    """
    try:
        client = get_supabase_client()
        if not client:
            raise HTTPException(503, "Database unavailable")

        # Get job details
        job_response = client.table('jobs')\
            .select('*, employers(*)')\
            .eq('id', request.job_id)\
            .single()\
            .execute()

        if not job_response.data:
            raise HTTPException(404, "Job not found")

        job = job_response.data

        # Get user profile
        profile = await get_user_profile(request.user_id)
        if not profile:
            raise HTTPException(404, "Profile not found")

        tailored_resume = None
        cover_letter = None

        # Auto-tailor resume if requested
        if request.auto_tailor:
            logger.info(f"Auto-tailoring resume for job {job['title']}")

            # Get Resume Studio prompts
            resume_prompts = get_prompt_set('resume_studio', 'tailor_resume')

            # Build JD JSON
            jd_json = {
                "title": job['title'],
                "seniority": job.get('seniority', 'mid'),
                "company": job['employers']['name'],
                "location": f"{job.get('location_city', '')} {job.get('location_country', '')}".strip(),
                "must_haves": job.get('skills_extracted', [])[:5] if job.get('skills_extracted') else [],
                "keywords": job.get('skills_extracted', []) if job.get('skills_extracted') else [],
                "industry": job.get('industry', job['employers'].get('industry', '')),
                "region": "US"
            }

            task_prompt = resume_prompts['task'].format(
                career_profile_json=json.dumps(profile.get('profile_data', {}), indent=2),
                job_description_json=json.dumps(jd_json, indent=2)
            )

            # Call Gemini
            tailor_response = await gemini_analyzer.analyze_with_prompts(
                system_prompt=resume_prompts['system'],
                developer_prompt=resume_prompts['developer'],
                task_prompt=task_prompt
            )

            tailored_resume = tailor_response.get('parsed_data', {})

        # Auto-generate cover letter if requested
        if request.auto_cover_letter:
            logger.info(f"Auto-generating cover letter for {job['title']}")

            cover_prompts = get_prompt_set('resume_studio', 'tailor_cover_letter')

            jd_json = {
                "title": job['title'],
                "company": job['employers']['name'],
                "description": job.get('description', '')[:500]  # First 500 chars
            }

            task_prompt = cover_prompts['task'].format(
                career_profile_json=json.dumps(profile.get('profile_data', {}), indent=2),
                tailored_resume_json=json.dumps(tailored_resume, indent=2) if tailored_resume else "{}",
                job_description_json=json.dumps(jd_json, indent=2)
            )

            cover_response = await gemini_analyzer.analyze_with_prompts(
                system_prompt=cover_prompts['system'],
                developer_prompt=cover_prompts['developer'],
                task_prompt=task_prompt
            )

            cover_letter = cover_response.get('parsed_data', {})

        # Save application
        application_data = {
            'user_id': request.user_id,
            'job_id': request.job_id,
            'employer_id': job['employer_id'],
            'tailored_resume_text': json.dumps(tailored_resume) if tailored_resume else None,
            'cover_letter_text': json.dumps(cover_letter) if cover_letter else None,
            'applied_via': 'auto' if request.auto_tailor else 'manual',
            'apply_url': job.get('apply_url'),
            'status': 'submitted',
            'submitted_at': datetime.utcnow().isoformat()
        }

        app_response = client.table('job_applications')\
            .insert(application_data)\
            .execute()

        application = app_response.data[0] if app_response.data else None

        # Update recommendation status
        client.table('job_recommendations')\
            .update({'status': 'applied'})\
            .eq('user_id', request.user_id)\
            .eq('job_id', request.job_id)\
            .execute()

        logger.info(f"✅ Application submitted for user {request.user_id} to job {job['title']}")

        return {
            "success": True,
            "application_id": application['id'] if application else None,
            "job_title": job['title'],
            "company": job['employers']['name'],
            "tailored_resume": tailored_resume,
            "cover_letter": cover_letter,
            "apply_url": job.get('apply_url'),
            "message": "Application submitted successfully with tailored materials"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        raise HTTPException(500, f"Application failed: {str(e)}")


@router.get("/applications/my")
async def get_my_applications(
    status: Optional[str] = Query(None),
    limit: int = Query(20, le=100),
    offset: int = Query(0),
    current_user: Dict = Depends(get_current_user)
):
    """Get user's job applications"""
    try:
        client = get_supabase_client()
        if not client:
            raise HTTPException(503, "Database unavailable")

        query_builder = client.table('job_applications')\
            .select('*, jobs(title, employers(name, logo_url)), employer_id')\
            .eq('user_id', current_user['user_id'])

        if status:
            query_builder = query_builder.eq('status', status)

        response = query_builder\
            .order('submitted_at', desc=True)\
            .range(offset, offset + limit - 1)\
            .execute()

        return {
            "applications": response.data if response.data else [],
            "total": len(response.data) if response.data else 0
        }

    except Exception as e:
        logger.error(f"Get applications error: {e}")
        raise HTTPException(500, str(e))


@router.put("/preferences")
async def update_preferences(
    request: UpdatePreferencesRequest,
    current_user: Dict = Depends(get_current_user)
):
    """Update job search preferences"""
    try:
        client = get_supabase_client()
        if not client:
            raise HTTPException(503, "Database unavailable")

        # Build update data
        update_data = {
            key: value
            for key, value in request.dict().items()
            if value is not None
        }
        update_data['updated_at'] = datetime.utcnow().isoformat()

        # Upsert preferences
        response = client.table('user_job_preferences').upsert({
            'user_id': current_user['user_id'],
            **update_data
        }).execute()

        # Invalidate recommendations cache
        await cache.delete("recommendations", current_user['user_id'])

        return {
            "success": True,
            "message": "Preferences updated successfully"
        }

    except Exception as e:
        logger.error(f"Update preferences error: {e}")
        raise HTTPException(500, str(e))


@router.get("/preferences")
async def get_preferences(
    current_user: Dict = Depends(get_current_user)
):
    """Get user's job preferences"""
    try:
        preferences = await get_user_preferences(current_user['user_id'])
        return preferences or {"message": "No preferences set"}

    except Exception as e:
        logger.error(f"Get preferences error: {e}")
        raise HTTPException(500, str(e))


@router.get("/health")
async def health_check():
    """Health check"""
    return {
        "status": "operational",
        "service": "Jobs Marketplace",
        "features": ["search", "ai_matching", "auto_tailor", "auto_apply"],
        "timestamp": datetime.utcnow().isoformat()
    }
