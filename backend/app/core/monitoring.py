"""
Sentry Error Monitoring Integration
Provides error tracking, performance monitoring, and alerting
"""

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from loguru import logger

from app.core.config import settings


def init_sentry():
    """
    Initialize Sentry error monitoring
    Only initializes if SENTRY_DSN is configured
    """
    
    if not settings.SENTRY_DSN:
        logger.info("Sentry monitoring not configured (SENTRY_DSN missing)")
        return False
    
    try:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.SENTRY_ENVIRONMENT,
            traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
            
            # Integrations
            integrations=[
                FastApiIntegration(transaction_style="endpoint"),
                StarletteIntegration(transaction_style="endpoint"),
                RedisIntegration(),
            ],
            
            # Performance monitoring
            enable_tracing=True,
            
            # Error sampling
            sample_rate=1.0,  # Capture 100% of errors
            
            # Release tracking
            release=f"{settings.APP_NAME}@{settings.VERSION}",
            
            # Additional context
            attach_stacktrace=True,
            send_default_pii=False,  # Don't send personally identifiable information
        )
        
        logger.info(
            f"✅ Sentry monitoring initialized: "
            f"env={settings.SENTRY_ENVIRONMENT}, "
            f"traces={settings.SENTRY_TRACES_SAMPLE_RATE * 100}%"
        )
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize Sentry: {e}")
        return False


def capture_exception(error: Exception, context: dict = None):
    """
    Manually capture an exception to Sentry
    
    Args:
        error: Exception to capture
        context: Additional context data
    """
    if settings.SENTRY_DSN:
        with sentry_sdk.push_scope() as scope:
            if context:
                for key, value in context.items():
                    scope.set_context(key, value)
            
            sentry_sdk.capture_exception(error)


def capture_message(message: str, level: str = "info", context: dict = None):
    """
    Capture a message to Sentry
    
    Args:
        message: Message to capture
        level: Message level (debug, info, warning, error, fatal)
        context: Additional context data
    """
    if settings.SENTRY_DSN:
        with sentry_sdk.push_scope() as scope:
            if context:
                for key, value in context.items():
                    scope.set_context(key, value)
            
            sentry_sdk.capture_message(message, level=level)


def set_user_context(user_id: str, email: str = None, username: str = None):
    """
    Set user context for error tracking
    
    Args:
        user_id: User ID
        email: User email (optional)
        username: Username (optional)
    """
    if settings.SENTRY_DSN:
        sentry_sdk.set_user({
            "id": user_id,
            "email": email,
            "username": username
        })


def add_breadcrumb(message: str, category: str = "default", level: str = "info", data: dict = None):
    """
    Add a breadcrumb for debugging context
    
    Args:
        message: Breadcrumb message
        category: Breadcrumb category
        level: Breadcrumb level
        data: Additional data
    """
    if settings.SENTRY_DSN:
        sentry_sdk.add_breadcrumb(
            message=message,
            category=category,
            level=level,
            data=data or {}
        )


def start_transaction(name: str, op: str = "http.server") -> object:
    """
    Start a performance monitoring transaction
    
    Args:
        name: Transaction name
        op: Operation type
    
    Returns:
        Transaction object (use as context manager)
    """
    if settings.SENTRY_DSN:
        return sentry_sdk.start_transaction(name=name, op=op)
    
    # Return a dummy context manager if Sentry is not configured
    class DummyTransaction:
        def __enter__(self):
            return self
        
        def __exit__(self, *args):
            pass
    
    return DummyTransaction()


# Custom error handlers for common scenarios

def handle_database_error(error: Exception, query: str = None):
    """Handle database-related errors"""
    context = {
        "database": {
            "error_type": type(error).__name__,
            "query": query or "N/A"
        }
    }
    capture_exception(error, context)


def handle_ai_error(error: Exception, prompt: str = None, model: str = "gemini-1.5-flash"):
    """Handle AI service errors"""
    context = {
        "ai_service": {
            "model": model,
            "error_type": type(error).__name__,
            "prompt_length": len(prompt) if prompt else 0
        }
    }
    capture_exception(error, context)


def handle_external_api_error(error: Exception, service: str, endpoint: str = None):
    """Handle external API errors"""
    context = {
        "external_api": {
            "service": service,
            "endpoint": endpoint or "N/A",
            "error_type": type(error).__name__
        }
    }
    capture_exception(error, context)
