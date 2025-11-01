"""
Profile Agent - Memory & Identity Manager
Maintains and retrieves the User Profile (single source of truth)
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from loguru import logger

from app.models.user_profile import (
    UserProfile, ProfileUpdate, WorkHistoryEntry, Skill,
    UserPreference, CareerGoal, RiskFactor, MotivationSignal,
    DevelopmentNeed
)
from app.services.supabase_client import SupabaseClient


class ProfileAgent:
    """
    Profile Agent - The memory keeper
    
    Responsibilities:
    - Retrieve the current User Profile
    - Update profile with new information
    - Calculate profile completeness
    - Answer: "Who is this person and what do they actually want?"
    """
    
    def __init__(self):
        self.supabase_client_wrapper = SupabaseClient()
        self.supabase = self.supabase_client_wrapper.get_client()
    
    async def get_profile(self, user_id: str) -> Optional[UserProfile]:
        """
        Retrieve the complete User Profile
        This is the single source of truth
        """
        try:
            response = self.supabase.table("user_profiles").select("*").eq("user_id", user_id).execute()
            
            if response.data and len(response.data) > 0:
                profile_data = response.data[0]
                
                # Convert JSON to UserProfile
                profile = UserProfile(**profile_data)
                
                # Update profile completeness
                profile.profile_completeness = self._calculate_completeness(profile)
                
                logger.info(f"Profile retrieved for user {user_id}: {profile.profile_completeness}% complete")
                
                return profile
            else:
                logger.warning(f"No profile found for user {user_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving profile for user {user_id}: {e}")
            return None
    
    async def create_profile(self, user_id: str, email: Optional[str] = None) -> UserProfile:
        """
        Create a new empty User Profile
        """
        try:
            profile = UserProfile(
                user_id=user_id,
                email=email,
                created_at=datetime.utcnow(),
                last_updated=datetime.utcnow()
            )
            
            # Store in Supabase
            profile_dict = profile.model_dump()
            
            response = self.supabase.table("user_profiles").insert(profile_dict).execute()
            
            logger.info(f"Created new profile for user {user_id}")
            
            return profile
            
        except Exception as e:
            logger.error(f"Error creating profile for user {user_id}: {e}")
            raise
    
    async def update_profile(self, user_id: str, profile_update: ProfileUpdate) -> UserProfile:
        """
        Apply a ProfileUpdate to the existing profile
        This is how the system learns and evolves the user model
        """
        try:
            # Get current profile
            profile = await self.get_profile(user_id)
            
            if not profile:
                logger.warning(f"No profile to update for user {user_id}, creating new one")
                profile = await self.create_profile(user_id)
            
            # Merge new skills
            for new_skill in profile_update.new_skills_detected:
                if not any(s.name == new_skill.name for s in profile.skills):
                    profile.skills.append(new_skill)
                    logger.info(f"Added new skill: {new_skill.name}")
            
            # Merge new preferences
            for new_pref in profile_update.new_preferences_detected:
                if not any(
                    p.category == new_pref.category and p.preference == new_pref.preference
                    for p in profile.preferences
                ):
                    profile.preferences.append(new_pref)
                    logger.info(f"Added new preference: {new_pref.preference}")
            
            # Merge new goals
            for new_goal in profile_update.new_goals_detected:
                if not any(
                    g.timeframe == new_goal.timeframe and g.description == new_goal.description
                    for g in profile.career_goals
                ):
                    profile.career_goals.append(new_goal)
                    logger.info(f"Added new goal: {new_goal.description}")
            
            # Merge risk signals
            for risk in profile_update.risk_signals_detected:
                profile.risk_factors.append(risk)
                logger.info(f"Added risk signal: {risk.description}")
            
            # Merge motivation signals
            for signal in profile_update.motivation_signals_detected:
                profile.motivation_signals.append(signal)
                logger.info(f"Added motivation signal: {signal.description}")
            
            # Merge development needs
            for need in profile_update.development_needs_detected:
                if not any(
                    n.skill_or_experience == need.skill_or_experience
                    for n in profile.development_needs
                ):
                    profile.development_needs.append(need)
                    logger.info(f"Added development need: {need.skill_or_experience}")
            
            # Update behavioral data
            if profile_update.job_interaction:
                job_id = profile_update.job_interaction.get("job_id")
                action = profile_update.job_interaction.get("action")
                
                if action == "viewed" and job_id not in profile.jobs_viewed:
                    profile.jobs_viewed.append(job_id)
                elif action == "saved" and job_id not in profile.jobs_saved:
                    profile.jobs_saved.append(job_id)
                elif action == "applied" and job_id not in profile.jobs_applied:
                    profile.jobs_applied.append(job_id)
                elif action == "rejected":
                    if job_id not in profile.jobs_rejected:
                        profile.jobs_rejected.append(job_id)
                    reason = profile_update.job_interaction.get("reason")
                    if reason:
                        profile.rejection_reasons[job_id] = reason
            
            # Update sentiment scores
            if profile_update.burnout_level_update is not None:
                profile.burnout_level = profile_update.burnout_level_update
            
            if profile_update.confidence_level_update is not None:
                profile.confidence_level = profile_update.confidence_level_update
            
            # Update metadata
            profile.last_updated = datetime.utcnow()
            profile.total_interactions += 1
            profile.last_interaction_at = datetime.utcnow()
            profile.profile_completeness = self._calculate_completeness(profile)
            
            # Save to database
            profile_dict = profile.model_dump()
            
            self.supabase.table("user_profiles").update(profile_dict).eq("user_id", user_id).execute()
            
            logger.info(f"Profile updated for user {user_id}: {profile.profile_completeness}% complete")
            
            return profile
            
        except Exception as e:
            logger.error(f"Error updating profile for user {user_id}: {e}")
            raise
    
    def _calculate_completeness(self, profile: UserProfile) -> int:
        """
        Calculate how complete the profile is (0-100%)
        Used to determine confidence in recommendations
        """
        total_fields = 0
        filled_fields = 0
        
        # Core identity (weight: 2)
        total_fields += 2
        if profile.email:
            filled_fields += 1
        if profile.location:
            filled_fields += 1
        
        # Work history (weight: 3)
        total_fields += 3
        if profile.current_role:
            filled_fields += 1
        if profile.work_history:
            filled_fields += 1
        if profile.years_total_experience:
            filled_fields += 1
        
        # Skills (weight: 3)
        total_fields += 3
        if profile.skills:
            filled_fields += 1
        if profile.core_competencies:
            filled_fields += 1
        if profile.transferable_skills:
            filled_fields += 1
        
        # Preferences (weight: 2)
        total_fields += 2
        if profile.preferences:
            filled_fields += 1
        if profile.remote_preference:
            filled_fields += 1
        
        # Career goals (weight: 2)
        total_fields += 2
        if profile.career_goals:
            filled_fields += 1
        if profile.desired_roles:
            filled_fields += 1
        
        # Motivation & sentiment (weight: 2)
        total_fields += 2
        if profile.motivation_signals:
            filled_fields += 1
        if profile.burnout_level is not None:
            filled_fields += 1
        
        # Salary expectations (weight: 1)
        total_fields += 1
        if profile.salary_expectations:
            filled_fields += 1
        
        completeness = int((filled_fields / total_fields) * 100)
        
        return completeness
    
    async def get_missing_critical_fields(self, user_id: str) -> List[str]:
        """
        Identify which critical profile fields are missing
        Returns field names that should be populated
        """
        profile = await self.get_profile(user_id)
        
        if not profile:
            return ["entire_profile"]
        
        missing = []
        
        if not profile.current_role:
            missing.append("current_role")
        
        if not profile.skills or len(profile.skills) == 0:
            missing.append("skills")
        
        if not profile.preferences or len(profile.preferences) == 0:
            missing.append("preferences")
        
        if not profile.career_goals or len(profile.career_goals) == 0:
            missing.append("career_goals")
        
        if profile.burnout_level is None:
            missing.append("burnout_level")
        
        if not profile.salary_expectations:
            missing.append("salary_expectations")
        
        if not profile.remote_preference:
            missing.append("remote_preference")
        
        return missing
