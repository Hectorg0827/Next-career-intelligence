"""
Health check endpoint
"""

from fastapi import APIRouter
from datetime import datetime
from app.models.schemas import HealthResponse
from app.core.config import settings
from app.db.supabase import get_supabase_client

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    Returns API status and service availability
    """
    services = {
        "api": "operational",
        "database": "unknown",
        "nextai": "configured" if settings.GEMINI_API_KEY else "not_configured",
        "onet": "configured" if (settings.ONET_USERNAME and settings.ONET_PASSWORD) else "not_configured",
    }

    # Check Supabase database connection
    try:
        client = get_supabase_client()
        if client:
            # Test connection by checking if we can access a table
            result = client.table("users").select("count", count="exact").limit(0).execute()
            services["database"] = "operational"
        else:
            services["database"] = "error"
    except Exception:
        services["database"] = "error"

    return HealthResponse(
        status="healthy" if services["database"] == "operational" else "degraded",
        version=settings.VERSION,
        timestamp=datetime.utcnow(),
        services=services,
    )
