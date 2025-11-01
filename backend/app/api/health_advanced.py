"""
Comprehensive Health Check System for NEXT Career Intelligence
Monitors all critical services and dependencies
"""

from fastapi import APIRouter, Response
from typing import Dict, Any
from datetime import datetime
from loguru import logger
import httpx
import asyncio

from app.core.config import settings
from app.core.cache import get_redis_client
from app.core.database_pool import get_supabase, db_pool

router = APIRouter()


async def check_database() -> Dict[str, Any]:
    """Check Supabase database connectivity and performance"""
    try:
        start_time = datetime.now()
        db = get_supabase()
        
        # Perform a simple query to test connection
        result = db.table('users').select('id').limit(1).execute()
        
        duration = (datetime.now() - start_time).total_seconds()
        
        return {
            "status": "healthy",
            "response_time_ms": round(duration * 1000, 2),
            "pool_stats": db_pool.get_stats()
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


async def check_redis() -> Dict[str, Any]:
    """Check Redis connectivity and performance"""
    try:
        redis_client = get_redis_client()
        
        if not redis_client:
            return {
                "status": "disabled",
                "message": "Redis not configured"
            }
        
        start_time = datetime.now()
        redis_client.ping()
        duration = (datetime.now() - start_time).total_seconds()
        
        # Get Redis info
        info = redis_client.info()
        
        return {
            "status": "healthy",
            "response_time_ms": round(duration * 1000, 2),
            "connected_clients": info.get('connected_clients', 0),
            "used_memory": info.get('used_memory_human', 'N/A'),
            "total_keys": redis_client.dbsize()
        }
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


async def check_gemini_ai() -> Dict[str, Any]:
    """Check Google Gemini AI service availability"""
    try:
        # Test with a simple prompt
        import google.generativeai as genai
        
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model_name = settings.GEMINI_MODEL if hasattr(settings, 'GEMINI_MODEL') else 'gemini-1.5-flash'
        model = genai.GenerativeModel(model_name)
        
        start_time = datetime.now()
        response = model.generate_content("Hello")
        duration = (datetime.now() - start_time).total_seconds()
        
        return {
            "status": "healthy",
            "response_time_ms": round(duration * 1000, 2),
            "model": model_name,
            "api_configured": bool(settings.GEMINI_API_KEY)
        }
    except Exception as e:
        logger.error(f"Gemini AI health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "api_configured": bool(settings.GEMINI_API_KEY)
        }


async def check_external_services() -> Dict[str, Any]:
    """Check external service dependencies"""
    services = {}
    
    # Check Stripe (if configured)
    if settings.STRIPE_API_KEY:
        try:
            import stripe
            stripe.api_key = settings.STRIPE_API_KEY
            
            start_time = datetime.now()
            stripe.Account.retrieve()
            duration = (datetime.now() - start_time).total_seconds()
            
            services['stripe'] = {
                "status": "healthy",
                "response_time_ms": round(duration * 1000, 2)
            }
        except Exception as e:
            services['stripe'] = {
                "status": "unhealthy",
                "error": str(e)
            }
    else:
        services['stripe'] = {"status": "not_configured"}
    
    # Check SendGrid (if configured)
    if settings.SENDGRID_API_KEY:
        services['sendgrid'] = {
            "status": "configured",
            "api_key_present": True
        }
    else:
        services['sendgrid'] = {"status": "not_configured"}
    
    return services


@router.get("/health")
async def health_check():
    """
    Basic health check endpoint
    Returns 200 if service is running
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "NEXT Career Intelligence API",
        "version": "1.0.0"
    }


@router.get("/health/detailed")
async def detailed_health_check():
    """
    Detailed health check with all service dependencies
    Checks: Database, Redis, AI services, External APIs
    """
    start_time = datetime.now()
    
    # Run all health checks concurrently
    database_status, redis_status, ai_status, external_services = await asyncio.gather(
        check_database(),
        check_redis(),
        check_gemini_ai(),
        check_external_services(),
        return_exceptions=True
    )
    
    total_duration = (datetime.now() - start_time).total_seconds()
    
    # Determine overall health
    critical_services = [database_status, redis_status]
    is_healthy = all(
        isinstance(svc, dict) and svc.get("status") in ["healthy", "disabled"]
        for svc in critical_services
    )
    
    return {
        "status": "healthy" if is_healthy else "degraded",
        "timestamp": datetime.now().isoformat(),
        "total_check_time_ms": round(total_duration * 1000, 2),
        "services": {
            "database": database_status if not isinstance(database_status, Exception) else {"status": "error", "error": str(database_status)},
            "redis": redis_status if not isinstance(redis_status, Exception) else {"status": "error", "error": str(redis_status)},
            "gemini_ai": ai_status if not isinstance(ai_status, Exception) else {"status": "error", "error": str(ai_status)},
            "external": external_services if not isinstance(external_services, Exception) else {"status": "error", "error": str(external_services)}
        },
        "environment": settings.ENVIRONMENT
    }


@router.get("/health/live")
async def liveness_probe():
    """
    Kubernetes liveness probe
    Returns 200 if application is alive
    """
    return Response(status_code=200, content="OK")


@router.get("/health/ready")
async def readiness_probe():
    """
    Kubernetes readiness probe
    Returns 200 only if all critical services are ready
    """
    try:
        # Check critical services
        db_status = await check_database()
        
        if db_status.get("status") == "healthy":
            return Response(status_code=200, content="READY")
        else:
            return Response(status_code=503, content="NOT READY")
    except Exception as e:
        logger.error(f"Readiness probe failed: {e}")
        return Response(status_code=503, content="NOT READY")


@router.get("/health/metrics")
async def health_metrics():
    """
    Prometheus-style metrics endpoint
    Returns metrics in a format suitable for monitoring systems
    """
    try:
        db_status = await check_database()
        redis_status = await check_redis()
        
        metrics = {
            "database_response_time_ms": db_status.get("response_time_ms", 0),
            "database_pool_utilization": db_status.get("pool_stats", {}).get("utilization", 0),
            "database_active_connections": db_status.get("pool_stats", {}).get("active_connections", 0),
            "redis_response_time_ms": redis_status.get("response_time_ms", 0),
            "redis_total_keys": redis_status.get("total_keys", 0),
            "redis_connected_clients": redis_status.get("connected_clients", 0),
            "timestamp": datetime.now().isoformat()
        }
        
        return metrics
    except Exception as e:
        logger.error(f"Failed to generate metrics: {e}")
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
