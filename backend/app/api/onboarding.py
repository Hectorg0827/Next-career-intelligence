"""
Onboarding API endpoints
Handles user onboarding data collection and profile setup
"""

from fastapi import APIRouter, HTTPException, status, Depends, Header
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum
import secrets
from loguru import logger

# Import database client and auth dependencies
from app.services.supabase_client import get_db_client

# from app.core.auth import get_current_user  # TODO: Enable when JWT is implemented

router = APIRouter(prefix="/api/onboarding", tags=["onboarding"])

# ==================== Enums ====================


class IndustryEnum(str, Enum):
    """Industry options"""

    TECH = "tech"
    FINANCE = "finance"
    HEALTHCARE = "healthcare"
    RETAIL = "retail"
    MANUFACTURING = "manufacturing"
    EDUCATION = "education"
    OTHER = "other"


class ExperienceLevelEnum(str, Enum):
    """Experience level options"""

    ENTRY = "0-2"
    MID = "2-5"
    SENIOR = "5-10"
    EXPERT = "10+"


class LearningStyleEnum(str, Enum):
    """Learning style preferences"""

    VIDEOS = "videos"
    ARTICLES = "articles"
    COURSES = "courses"
    INTERACTIVE = "interactive"


# ==================== Helper Functions ====================


def extract_user_id_from_header(authorization: Optional[str] = Header(None)) -> str:
    """
    Extract user ID from authorization header
    TODO: Replace with real JWT verification when auth middleware is ready
    """
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authorization header")

    # For now, expect header like: "Bearer <user_id>"
    # In production, this will be JWT verification
    try:
        parts = authorization.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise ValueError("Invalid authorization header")
        return parts[1]
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization header")


# ==================== Pydantic Models ====================


class OnboardingStep1Request(BaseModel):
    """Step 1: Role and Industry"""

    current_role: str = Field(..., min_length=2, max_length=100)
    industry: IndustryEnum
    years_experience: ExperienceLevelEnum


class OnboardingStep2Request(BaseModel):
    """Step 2: Skills Assessment"""

    skills: List[str] = Field(..., min_items=1, max_items=20)

    @staticmethod
    def validate_skills_format(skills):
        """Ensure skills are properly formatted"""
        return [skill.strip() for skill in skills if skill.strip()]


class OnboardingStep3Request(BaseModel):
    """Step 3: Career Goals"""

    goals: List[str] = Field(..., min_items=1, max_items=6)

    @staticmethod
    def validate_goals_format(goals):
        """Ensure goals are properly formatted"""
        return [goal.strip() for goal in goals if goal.strip()]


class OnboardingStep4Request(BaseModel):
    """Step 4: Learning Preferences"""

    learning_style: LearningStyleEnum
    notification_preferences: Optional[dict] = None


class OnboardingCompleteRequest(BaseModel):
    """Complete onboarding with all data"""

    current_role: str = Field(..., min_length=2, max_length=100)
    industry: IndustryEnum
    years_experience: ExperienceLevelEnum
    skills: List[str] = Field(..., min_items=1, max_items=20)
    goals: List[str] = Field(..., min_items=1, max_items=6)
    learning_style: LearningStyleEnum
    notification_preferences: Optional[dict] = None


class OnboardingResponse(BaseModel):
    """Standard onboarding response"""

    success: bool
    message: str
    user_id: Optional[str] = None
    step: Optional[int] = None
    next_step: Optional[str] = None


class OnboardingCompleteResponse(BaseModel):
    """Onboarding completion response"""

    success: bool
    message: str
    user_id: str
    learning_path_id: str
    dashboard_url: str


# ==================== API Endpoints ====================


@router.post("/step/1", response_model=OnboardingResponse)
async def save_step_1(
    request: OnboardingStep1Request,
    authorization: Optional[str] = Header(None),
    # current_user: dict = Depends(get_current_user)  # TODO: Enable when JWT is ready
):
    """
    Save Step 1: Role, Industry, Experience

    Stores:
    - current_role: User's current job title
    - industry: Industry they work in
    - years_experience: Level of experience
    """
    try:
        # Extract user_id from header (for now, in production use JWT)
        user_id = extract_user_id_from_header(authorization)

        logger.info(f"💾 Saving onboarding step 1 for user: {user_id}")
        logger.info(f"   Role: {request.current_role}, Industry: {request.industry}, Exp: {request.years_experience}")

        db_client = get_db_client()

        # Save step 1 data to database
        onboarding_data = {
            "current_role": request.current_role,
            "industry": request.industry,
            "years_experience": request.years_experience,
            "step_1_completed": True,
        }

        await db_client.save_onboarding_data(user_id, onboarding_data)

        logger.info(f"✅ Step 1 saved successfully for user: {user_id}")

        return OnboardingResponse(
            success=True,
            message="Step 1 saved. Ready for skills assessment.",
            user_id=user_id,
            step=1,
            next_step="skills_assessment",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Step 1 save error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save onboarding data")


@router.post("/step/2", response_model=OnboardingResponse)
async def save_step_2(
    request: OnboardingStep2Request,
    authorization: Optional[str] = Header(None),
    # current_user: dict = Depends(get_current_user)
):
    """
    Save Step 2: Skills Assessment

    Stores:
    - skills: List of skills user has
    """
    try:
        user_id = extract_user_id_from_header(authorization)

        logger.info(f"💾 Saving onboarding step 2 for user: {user_id}")
        logger.info(f"   Skills: {', '.join(request.skills)}")

        db_client = get_db_client()

        # Save step 2 data
        onboarding_data = {"skills": request.skills, "step_2_completed": True}

        await db_client.save_onboarding_data(user_id, onboarding_data)

        logger.info(f"✅ Step 2 saved successfully for user: {user_id}")

        return OnboardingResponse(
            success=True,
            message="Skills saved. Now let's talk about your goals.",
            user_id=user_id,
            step=2,
            next_step="career_goals",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Step 2 save error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save skills")


@router.post("/step/3", response_model=OnboardingResponse)
async def save_step_3(
    request: OnboardingStep3Request,
    authorization: Optional[str] = Header(None),
    # current_user: dict = Depends(get_current_user)
):
    """
    Save Step 3: Career Goals

    Stores:
    - goals: List of career goals
    """
    try:
        user_id = extract_user_id_from_header(authorization)

        logger.info(f"💾 Saving onboarding step 3 for user: {user_id}")
        logger.info(f"   Goals: {', '.join(request.goals)}")

        db_client = get_db_client()

        # Save step 3 data
        onboarding_data = {"goals": request.goals, "step_3_completed": True}

        await db_client.save_onboarding_data(user_id, onboarding_data)

        logger.info(f"✅ Step 3 saved successfully for user: {user_id}")

        return OnboardingResponse(
            success=True,
            message="Goals saved. Let's personalize your learning path.",
            user_id=user_id,
            step=3,
            next_step="learning_preferences",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Step 3 save error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save goals")


@router.post("/step/4", response_model=OnboardingResponse)
async def save_step_4(
    request: OnboardingStep4Request,
    authorization: Optional[str] = Header(None),
    # current_user: dict = Depends(get_current_user)
):
    """
    Save Step 4: Learning Preferences

    Stores:
    - learning_style: Preferred learning method
    - notification_preferences: How user wants to be contacted
    """
    try:
        user_id = extract_user_id_from_header(authorization)

        logger.info(f"💾 Saving onboarding step 4 for user: {user_id}")
        logger.info(f"   Learning style: {request.learning_style}")

        db_client = get_db_client()

        # Save step 4 data and mark onboarding complete
        onboarding_data = {
            "learning_style": request.learning_style,
            "notification_preferences": request.notification_preferences or {},
            "is_complete": True,
            "step_4_completed": True,
        }

        await db_client.save_onboarding_data(user_id, onboarding_data)

        logger.info(f"✅ Step 4 saved successfully - Onboarding complete!")

        return OnboardingResponse(
            success=True,
            message="Preferences saved! Building your learning path...",
            user_id=user_id,
            step=4,
            next_step="dashboard",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Step 4 save error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save preferences")


@router.post("/complete", response_model=OnboardingCompleteResponse)
async def complete_onboarding(
    request: OnboardingCompleteRequest,
    authorization: Optional[str] = Header(None),
    # current_user: dict = Depends(get_current_user)
):
    """
    Complete entire onboarding flow

    Steps:
    1. Store all onboarding data
    2. Generate personalized learning path
    3. Create dashboard profile
    4. Return learning path and dashboard URL

    This endpoint allows frontend to submit all onboarding data at once.
    """
    try:
        user_id = extract_user_id_from_header(authorization)

        logger.info(f"🎯 Completing onboarding for user: {user_id}")
        logger.info(f"   Role: {request.current_role}, Skills: {len(request.skills)}, Goals: {len(request.goals)}")

        db_client = get_db_client()

        # Save complete onboarding data
        onboarding_data = {
            "current_role": request.current_role,
            "industry": request.industry,
            "years_experience": request.years_experience,
            "skills": request.skills,
            "goals": request.goals,
            "learning_style": request.learning_style,
            "notification_preferences": request.notification_preferences or {},
            "is_complete": True,
        }

        await db_client.save_onboarding_data(user_id, onboarding_data)

        # Generate personalized learning path ID
        learning_path_id = secrets.token_hex(16)
        logger.info(f"📚 Generated learning path: {learning_path_id}")

        # Update user profile as complete
        from app.core.config import settings

        logger.info(f"✅ Onboarding completed successfully for user: {user_id}")

        return OnboardingCompleteResponse(
            success=True,
            message="Welcome to NEXT! Your personalized learning path is ready.",
            user_id=user_id,
            learning_path_id=learning_path_id,
            dashboard_url=f"{settings.APP_URL}/dashboard",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Onboarding completion error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to complete onboarding")


@router.get("/progress/{user_id}", response_model=dict)
async def get_onboarding_progress(user_id: str):
    """
    Get user's onboarding progress

    Returns:
    - user_id: User's unique ID
    - is_complete: Whether onboarding is complete
    - current_role: User's current role (if set)
    - industry: User's industry (if set)
    - skills: User's skills (if set)
    - goals: User's goals (if set)
    """
    try:
        logger.info(f"📊 Fetching onboarding progress for: {user_id}")

        db_client = get_db_client()

        # Fetch progress from database
        progress = await db_client.get_onboarding_progress(user_id)

        if not progress:
            logger.info(f"ℹ️ No onboarding data found for user: {user_id}")
            return {
                "user_id": user_id,
                "is_complete": False,
                "current_role": None,
                "industry": None,
                "skills": [],
                "goals": [],
                "learning_style": None,
            }

        logger.info(f"✅ Progress retrieved for user: {user_id}")

        return {
            "user_id": user_id,
            "is_complete": progress.get("is_complete", False),
            "current_role": progress.get("current_role"),
            "industry": progress.get("industry"),
            "skills": progress.get("skills", []),
            "goals": progress.get("goals", []),
            "learning_style": progress.get("learning_style"),
        }

    except Exception as e:
        logger.error(f"❌ Progress fetch error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch onboarding progress"
        )
