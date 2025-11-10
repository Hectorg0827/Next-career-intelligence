"""
NEXT | Adaptive Career Intelligence - Backend API
FastAPI application entry point
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import time
from contextlib import asynccontextmanager

from app.api import analyze, jobs, users, health, coach, interviewer, jobs_marketplace, subscriptions, roadmap, auth, onboarding, marketplace, resume_studio, match, elite_auth, health_advanced, career_health, rft, talent_graph
try:
    from app.api import resume_studio
except ImportError:
    resume_studio = None
    logger.warning("Resume Studio module not available")

# Performance & Reliability imports
from app.core.config import settings
from app.core.cache import init_redis, cleanup_redis, get_cache_stats
from app.core.database_pool import init_supabase, get_db_stats
from app.core.rate_limiter import limiter, get_rate_limiter, rate_limit_exceeded_handler
from app.core.compression import CompressionMiddleware, RequestSizeLimitMiddleware
from app.core.monitoring import init_sentry, capture_exception
from app.core.scheduler import setup_scheduled_tasks, shutdown_scheduled_tasks, task_manager
from app.core.neo4j_client import neo4j_client
from slowapi.errors import RateLimitExceeded

# Initialize database tables
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events - Startup and Shutdown"""
    logger.info("🚀 Starting NEXT Career Intelligence API...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    
    # Initialize error monitoring
    try:
        sentry_initialized = init_sentry()
        if sentry_initialized:
            logger.info("✅ Sentry error monitoring initialized")
    except Exception as e:
        logger.warning(f"⚠️ Sentry initialization failed: {e}")
    
    # Initialize Redis cache
    try:
        redis_initialized = await init_redis()
        if redis_initialized:
            logger.info("✅ Redis cache initialized")
    except Exception as e:
        logger.warning(f"⚠️ Redis initialization failed: {e}")
    
    # Initialize Supabase connection pool
    try:
        init_supabase()
        logger.info("✅ Supabase connection pool initialized")
    except Exception as e:
        logger.error(f"❌ Supabase initialization failed: {e}")
        capture_exception(e, {"startup": {"service": "supabase"}})
    
    # Initialize Neo4j Talent Graph
    try:
        await neo4j_client.connect()
        logger.info("✅ Neo4j Talent Graph connected")
    except Exception as e:
        logger.warning(f"⚠️ Neo4j initialization failed: {e} - Talent Graph features will be disabled")

    # Initialize scheduled background tasks
    try:
        setup_scheduled_tasks()
        logger.info("✅ Scheduled background tasks initialized")
    except Exception as e:
        logger.warning(f"⚠️ Background tasks initialization failed: {e}")
    
    # Log startup complete
    logger.info("✅ All services initialized - API ready to accept requests")
    
    yield
    
    # Shutdown cleanup
    logger.info("👋 Shutting down NEXT Career Intelligence API...")
    
    # Shutdown scheduled tasks
    try:
        shutdown_scheduled_tasks()
        logger.info("✅ Background tasks stopped")
    except Exception as e:
        logger.error(f"❌ Background tasks shutdown failed: {e}")
    
    # Cleanup Neo4j connections
    try:
        await neo4j_client.close()
        logger.info("✅ Neo4j connections closed")
    except Exception as e:
        logger.error(f"❌ Neo4j cleanup failed: {e}")

    # Cleanup Redis connections
    try:
        await cleanup_redis()
        logger.info("✅ Redis connections closed")
    except Exception as e:
        logger.error(f"❌ Redis cleanup failed: {e}")

    logger.info("✅ Shutdown complete")


# Initialize FastAPI app
app = FastAPI(
    title="NEXT | Adaptive Career Intelligence API",
    description="Real-time AI-powered career resilience platform with performance optimizations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Add compression middleware (if enabled)
if settings.ENABLE_COMPRESSION:
    app.add_middleware(
        GZipMiddleware,
        minimum_size=settings.COMPRESSION_MIN_SIZE
    )
    logger.info(f"✅ Response compression enabled (min size: {settings.COMPRESSION_MIN_SIZE} bytes)")

# Add request size limit middleware
app.add_middleware(
    RequestSizeLimitMiddleware,
    max_size=settings.MAX_REQUEST_SIZE
)
logger.info(f"✅ Request size limit: {settings.MAX_REQUEST_SIZE / (1024*1024):.1f}MB")

# CORS middleware - Allow all origins in production for Cloud Run
# In production, frontend domain will be different, so we allow all origins
if settings.ENVIRONMENT == "production":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    # Development - only allow localhost
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests with timing"""
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = time.time() - start_time
    
    # Log request details
    logger.info(
        f"{request.method} {request.url.path} "
        f"- Status: {response.status_code} "
        f"- Duration: {duration:.3f}s"
    )
    
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors gracefully with monitoring"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    # Send to Sentry if configured
    try:
        capture_exception(exc, {
            "request": {
                "url": str(request.url),
                "method": request.method,
                "client_ip": request.client.host if request.client else "unknown"
            }
        })
    except Exception as e:
        logger.error(f"Failed to capture exception in Sentry: {e}")
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if settings.DEBUG else "An unexpected error occurred",
            "path": str(request.url)
        }
    )


# Include routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(health_advanced.router, prefix="/api", tags=["Health & Monitoring"])
app.include_router(auth.router, tags=["Authentication"])
app.include_router(elite_auth.router, prefix="/api", tags=["Elite Authentication"])
app.include_router(onboarding.router, tags=["Onboarding"])

# NEW: Multi-Agent Career Intelligence System
app.include_router(match.router, prefix="/api", tags=["Career Intelligence - Multi-Agent System"])

app.include_router(analyze.router, prefix="/api", tags=["Analysis"])
app.include_router(roadmap.router, prefix="/api", tags=["Career Roadmap"])
app.include_router(jobs.router, prefix="/api", tags=["Jobs"])
app.include_router(users.router, prefix="/api", tags=["Users"])
app.include_router(resume_studio.router, prefix="/api", tags=["Resume Studio"])

# Premium feature routers
if resume_studio:
    app.include_router(resume_studio.router, prefix="/api", tags=["Resume Studio - Premium"])
app.include_router(coach.router, prefix="/api", tags=["Career Coach - Premium"])
app.include_router(interviewer.router, prefix="/api", tags=["Interviewer AI - Premium"])
app.include_router(subscriptions.router, prefix="/api", tags=["Subscription Management"])

# Jobs Marketplace (360° Career Builder)
app.include_router(jobs_marketplace.router, prefix="/api", tags=["Jobs Marketplace - 360°"])

# Jobs Marketplace v2 (New Endpoints)
app.include_router(marketplace.router, tags=["Job Marketplace - Search & Apply"])

# Career Health Score
app.include_router(career_health.router, tags=["Career Health Score"])

# RFT (Reinforcement Fine-Tuning) System
app.include_router(rft.router, tags=["RFT Feedback"])

# Talent Graph (Neo4j)
app.include_router(talent_graph.router, tags=["Talent Graph - Neo4j"])


# Performance monitoring endpoint
@app.get("/api/performance")
async def performance_stats():
    """Get performance and caching statistics"""
    try:
        return {
            "cache": get_cache_stats(),
            "database": get_db_stats(),
            "background_tasks": task_manager.get_task_stats(),
            "rate_limiting": {
                "enabled": True,
                "storage": "redis" if settings.REDIS_HOST else "memory"
            },
            "compression": {
                "enabled": settings.ENABLE_COMPRESSION,
                "min_size_bytes": settings.COMPRESSION_MIN_SIZE
            },
            "monitoring": {
                "sentry_enabled": bool(settings.SENTRY_DSN),
                "environment": settings.SENTRY_ENVIRONMENT
            }
        }
    except Exception as e:
        logger.error(f"Failed to get performance stats: {e}")
        return {
            "error": str(e),
            "message": "Failed to retrieve performance statistics"
        }


# Root endpoint
@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "NEXT | Adaptive Career Intelligence API",
        "version": "1.0.0",
        "status": "operational",
        "documentation": "/docs",
        "health_check": "/api/health",
        "detailed_health": "/api/health/detailed",
        "performance_stats": "/api/performance",
        "features": {
            "caching": "enabled" if settings.REDIS_HOST else "disabled",
            "rate_limiting": "enabled",
            "compression": "enabled" if settings.ENABLE_COMPRESSION else "disabled",
            "error_monitoring": "enabled" if settings.SENTRY_DSN else "disabled"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )
