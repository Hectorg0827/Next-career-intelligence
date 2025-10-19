"""
Health check endpoint
"""

from fastapi import APIRouter
from datetime import datetime
from app.models.schemas import HealthResponse
from app.core.config import settings
from app.db.database import engine

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
        "openai": "configured" if settings.OPENAI_API_KEY else "not_configured",
        "onet": "configured" if settings.ONET_API_KEY else "not_configured"
    }
    
    # Check database connection
    try:
        engine.connect()
        services["database"] = "operational"
    except Exception:
        services["database"] = "error"
    
    return HealthResponse(
        status="healthy" if services["database"] == "operational" else "degraded",
        version=settings.VERSION,
        timestamp=datetime.utcnow(),
        services=services
    )
