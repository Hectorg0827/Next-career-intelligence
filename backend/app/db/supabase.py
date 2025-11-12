"""
Supabase Client Configuration
Handles both database and authentication for NEXT Careers
"""

import os
from supabase import create_client, Client
from loguru import logger

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# Initialize Supabase client
supabase: Client = None


def get_supabase_client() -> Client:
    """
    Get Supabase client singleton
    """
    global supabase

    if supabase is None:
        if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
            logger.warning("Supabase credentials not configured - running without database")
            return None

        try:
            supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
            logger.info("✅ Supabase client initialized")
        except Exception as e:
            logger.error(f"❌ Supabase initialization failed: {e}")
            return None

    return supabase


async def test_supabase_connection():
    """
    Test Supabase connection
    """
    try:
        client = get_supabase_client()
        if not client:
            logger.warning("Supabase not configured")
            return False

        # Test query - just check if we can connect
        response = client.table("users").select("count", count="exact").limit(0).execute()
        logger.info(f"✅ Supabase connection successful")
        return True
    except Exception as e:
        logger.warning(f"⚠️ Supabase connection test failed (this is OK if tables don't exist yet): {e}")
        return False


# Database helper functions
class SupabaseDB:
    """Helper class for database operations"""

    @staticmethod
    async def save_analysis(user_id: str, analysis_data: dict):
        """Save career analysis to database"""
        try:
            client = get_supabase_client()
            if not client:
                return None

            response = (
                client.table("analyses")
                .insert(
                    {
                        "user_id": user_id,
                        "job_title": analysis_data.get("job_title"),
                        "risk_score": analysis_data.get("ai_displacement_risk", {}).get("score"),
                        "risk_level": analysis_data.get("ai_displacement_risk", {}).get("level"),
                        "analysis_data": analysis_data,
                    }
                )
                .execute()
            )

            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Failed to save analysis: {e}")
            return None

    @staticmethod
    async def get_user_analyses(user_id: str):
        """Get all analyses for a user"""
        try:
            client = get_supabase_client()
            if not client:
                return []

            response = (
                client.table("analyses").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
            )

            return response.data
        except Exception as e:
            logger.error(f"Failed to get analyses: {e}")
            return []

    @staticmethod
    async def save_roadmap(user_id: str, analysis_id: str, roadmap_data: dict):
        """Save career roadmap to database"""
        try:
            client = get_supabase_client()
            if not client:
                return None

            response = (
                client.table("career_roadmaps")
                .insert(
                    {
                        "user_id": user_id,
                        "analysis_id": analysis_id,
                        "roadmap_data": roadmap_data,
                    }
                )
                .execute()
            )

            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Failed to save roadmap: {e}")
            return None


# Export
db = SupabaseDB()
