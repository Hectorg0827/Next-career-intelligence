"""
NEXT | Adaptive Career Intelligence - Backend API
FastAPI application entry point
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import time
from contextlib import asynccontextmanager

from app.api import analyze, jobs, users, health, coach, interviewer, jobs_marketplace, subscriptions, roadmap, auth, onboarding, payments
try:
    from app.api import resume_studio
except ImportError:
    resume_studio = None
    logger.warning("Resume Studio module not available")
# from app.db.database import engine, Base  # REMOVED: Using Supabase instead
from app.core.config import settings

# Initialize database tables
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("🚀 Starting NEXT Career Intelligence API...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    
    # Database initialization - now using Supabase
    try:
        # Supabase handles its own schema, no need to create tables here
        logger.info("✅ Using Supabase database (tables created manually)")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
    
    yield
    
    logger.info("👋 Shutting down NEXT Career Intelligence API")


# Initialize FastAPI app
app = FastAPI(
    title="NEXT | Adaptive Career Intelligence API",
    description="Real-time AI-powered career resilience platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
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
    """Handle unexpected errors gracefully"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
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
app.include_router(auth.router, tags=["Authentication"])
app.include_router(onboarding.router, tags=["Onboarding"])
app.include_router(analyze.router, prefix="/api", tags=["Analysis"])
app.include_router(roadmap.router, prefix="/api", tags=["Career Roadmap"])
app.include_router(jobs.router, prefix="/api", tags=["Jobs"])
app.include_router(users.router, prefix="/api", tags=["Users"])
app.include_router(payments.router, prefix="/api", tags=["Payments"])

# Premium feature routers
if resume_studio:
    app.include_router(resume_studio.router, prefix="/api", tags=["Resume Studio - Premium"])
app.include_router(coach.router, prefix="/api", tags=["Career Coach - Premium"])
app.include_router(interviewer.router, prefix="/api", tags=["Interviewer AI - Premium"])
app.include_router(subscriptions.router, prefix="/api", tags=["Subscription Management"])

# Jobs Marketplace (360° Career Builder)
app.include_router(jobs_marketplace.router, prefix="/api", tags=["Jobs Marketplace - 360°"])


# Root endpoint
@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "NEXT | Adaptive Career Intelligence API",
        "version": "1.0.0",
        "status": "operational",
        "documentation": "/docs",
        "health_check": "/api/health"
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
