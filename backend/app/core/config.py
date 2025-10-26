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
    
    # Google Cloud Platform
    GCP_PROJECT_ID: str = ""
    GCP_DEPLOYMENT_URL: str = ""
    GCP_OAUTH_CLIENT_ID: str = ""
    
    # O*NET API
    ONET_USERNAME: str = ""
    ONET_PASSWORD: str = ""
    ONET_BASE_URL: str = "https://services.onetcenter.org/ws"
    
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
    
    # Stripe Payment Processing
    STRIPE_SECRET_KEY: str = ""
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
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://your-production-domain.com"
    ]
    CORS_ALLOW_ALL_ORIGINS: bool = False  # Set to True in production if needed
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
