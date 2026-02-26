"""
Application configuration settings
"""

from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings"""

    # App config
    APP_NAME: str = "NEXT Career Intelligence"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/next_career_db"

    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_KEY: str = ""

    # Google Gemini API (Replaces OpenAI)
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"  # Default model

    # Google Cloud Platform
    GCP_PROJECT_ID: str = ""
    GCP_DEPLOYMENT_URL: str = ""
    GCP_OAUTH_CLIENT_ID: str = ""

    # O*NET API
    ONET_USERNAME: str = ""
    ONET_PASSWORD: str = ""
    ONET_BASE_URL: str = "https://services.onetcenter.org/ws"

    # Apify (Levels.fyi scraper for real salary data)
    APIFY_API_TOKEN: str = ""

    # BLS (Bureau of Labor Statistics OES API — free, register at bls.gov)
    BLS_API_KEY: str = ""

    # Adzuna Jobs API (free tier: 250 req/day — demand trends & job volume)
    ADZUNA_APP_ID: str = ""
    ADZUNA_API_KEY: str = ""

    # TheirStack (technology stack by company — $99/mo)
    THEIRSTACK_API_KEY: str = ""

    # Lightcast / EMSI (enterprise labor market data — $500+/mo)
    LIGHTCAST_CLIENT_ID: str = ""
    LIGHTCAST_CLIENT_SECRET: str = ""

    # NewsAPI (company research for SDR — free tier: 100 req/day)
    NEWS_API_KEY: str = ""

    # OpenAI (fallback provider when Gemini is rate-limited)
    OPENAI_API_KEY: str = ""

    # Salary data cache TTL (seconds)
    SALARY_CACHE_TTL: int = 86400  # 24 hours

    # Active labor market data provider (adzuna | onet | lightcast)
    ACTIVE_LABOR_PROVIDER: str = "adzuna"

    # SDR Configuration
    SDR_MAX_APPLICATIONS_PER_WEEK: int = 10  # Hard cap across all users
    SDR_DEFAULT_WEEKLY_QUOTA: int = 5        # Default per-user quota

    # Coursera API
    COURSERA_API_KEY: str = ""
    COURSERA_BASE_URL: str = "https://api.coursera.org/api"

    # LinkedIn API (optional)
    LINKEDIN_CLIENT_ID: str = ""
    LINKEDIN_CLIENT_SECRET: str = ""

    # SendGrid Email Service
    SENDGRID_API_KEY: str = ""
    SENDGRID_FROM_EMAIL: str = "noreply@nextcareer.ai"
    SENDGRID_FROM_NAME: str = "NEXT Career Intelligence"

    # Application URLs
    APP_URL: str = "http://localhost:3000"
    API_URL: str = "http://localhost:8000"

    # CORS Settings
    ALLOWED_ORIGINS: str = "http://localhost:3000,https://localhost:3000"

    @property
    def allowed_origins_list(self) -> list:
        """Convert ALLOWED_ORIGINS string to list"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    # Stripe Payment Processing
    STRIPE_SECRET_KEY: str = ""
    STRIPE_API_KEY: str = ""  # Alias for STRIPE_SECRET_KEY, used by health check
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_PRICE_ID_PRO_MONTHLY: str = ""
    STRIPE_PRICE_ID_PRO_YEARLY: str = ""
    STRIPE_PRICE_ID_ENTERPRISE: str = ""

    # Neo4j (optional - Phase 2)
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "password"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Redis Configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0
    REDIS_URL: str = ""  # Alternative: redis://user:pass@host:port/db
    REDIS_ENABLED: bool = True  # Phase 4

    # Cache Configuration (Phase 4)
    CACHE_TTL: int = 3600  # Cache time-to-live in seconds
    CACHE_ENABLED: bool = True

    # CORS (defined above at line 68)
    # ALLOWED_ORIGINS is defined as a string above
    CORS_ALLOW_ALL_ORIGINS: bool = False  # Set to True in production if needed

    # Logging
    LOG_LEVEL: str = "INFO"

    # Rate limiting (Phase 4 Enhanced)
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_HOUR: int = 1000

    # Performance & Monitoring (Phase 4 Enhanced)
    ENABLE_COMPRESSION: bool = True
    COMPRESSION_MIN_SIZE: int = 1024  # Minimum response size to compress (bytes)
    COMPRESSION_LEVEL: int = 6  # Gzip compression level (1-9)
    MAX_REQUEST_SIZE: int = 10 * 1024 * 1024  # 10MB max request size
    MAX_WORKERS: int = 4  # Number of worker processes

    # AI Service Configuration (Phase 4)
    AI_REQUEST_TIMEOUT: int = 30  # Timeout for AI API calls in seconds
    AI_MAX_RETRIES: int = 3  # Maximum retries for failed AI requests
    AI_CIRCUIT_BREAKER_THRESHOLD: int = 5  # Failures before circuit opens
    AI_CIRCUIT_BREAKER_TIMEOUT: int = 60  # Seconds before circuit half-opens

    # Database Pooling (Phase 4)
    DB_POOL_SIZE: int = 20  # Connection pool size
    DB_MAX_OVERFLOW: int = 10  # Max connections beyond pool_size
    DB_POOL_TIMEOUT: int = 30  # Timeout for getting connection from pool

    # Sentry Error Monitoring (optional)
    SENTRY_DSN: str = ""
    SENTRY_ENVIRONMENT: str = "development"
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1  # 10% of transactions
    SENTRY_ENABLED: bool = False  # Phase 4

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Allow extra fields from .env for Phase 4


settings = Settings()
