"""
Sentry Error Monitoring Integration
Provides error tracking, performance monitoring, and alerting

Features:
- Custom error grouping and fingerprinting
- User context tracking
- Performance transaction monitoring
- Breadcrumb trails for debugging
- Custom error handlers for AI, DB, and external API errors
"""

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
import logging
from loguru import logger
from typing import Optional, Dict, Any
import traceback
import sys

from app.core.config import settings


def before_send(event: Dict[str, Any], hint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Filter and modify events before sending to Sentry

    Use cases:
    - Filter out noisy errors
    - Add custom fingerprinting for error grouping
    - Scrub sensitive data
    - Enhance context
    """

    # Get exception info
    exc_info = hint.get("exc_info")
    if exc_info:
        exc_type, exc_value, exc_tb = exc_info
        error_message = str(exc_value)
        error_type = exc_type.__name__ if exc_type else "Unknown"

        # Custom fingerprinting for better error grouping
        custom_fingerprint = []

        # Group by error type + message pattern
        if "database" in error_message.lower() or "postgresql" in error_message.lower():
            custom_fingerprint = ["database-error", error_type]
        elif "gemini" in error_message.lower() or "api" in error_message.lower():
            custom_fingerprint = ["ai-service-error", error_type]
        elif "redis" in error_message.lower():
            custom_fingerprint = ["cache-error", error_type]
        elif "stripe" in error_message.lower() or "payment" in error_message.lower():
            custom_fingerprint = ["payment-error", error_type]
        elif "rate limit" in error_message.lower():
            custom_fingerprint = ["rate-limit-exceeded"]
        elif "authentication" in error_message.lower() or "unauthorized" in error_message.lower():
            custom_fingerprint = ["auth-error", error_type]

        if custom_fingerprint:
            event["fingerprint"] = custom_fingerprint

        # Filter out noisy errors
        if error_type in ["KeyboardInterrupt", "SystemExit"]:
            return None  # Don't send to Sentry

        # Filter health check errors
        if event.get("request", {}).get("url", "").endswith("/health"):
            return None

    # Scrub sensitive data from event
    if "request" in event:
        headers = event["request"].get("headers", {})
        # Remove auth tokens
        if "Authorization" in headers:
            headers["Authorization"] = "[Filtered]"
        if "Cookie" in headers:
            headers["Cookie"] = "[Filtered]"

    # Add deployment info
    event.setdefault("tags", {})
    event["tags"]["deployment"] = settings.ENVIRONMENT
    event["tags"]["version"] = settings.VERSION

    return event


def init_sentry():
    """
    Initialize Sentry error monitoring with production-ready configuration

    Features:
    - Custom error grouping
    - Performance monitoring (APM)
    - User context tracking
    - Breadcrumb trails
    - Integration with FastAPI, Redis, SQLAlchemy
    """

    if not settings.SENTRY_DSN:
        logger.info("Sentry monitoring not configured (SENTRY_DSN missing)")
        return False

    try:
        # Configure logging integration
        logging_integration = LoggingIntegration(
            level=logging.INFO, event_level=logging.ERROR  # Capture info and above  # Send errors as events
        )

        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.SENTRY_ENVIRONMENT,
            traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
            # Integrations
            integrations=[
                FastApiIntegration(transaction_style="endpoint"),
                StarletteIntegration(transaction_style="endpoint"),
                RedisIntegration(),
                SqlalchemyIntegration(),
                logging_integration,
            ],
            # Performance monitoring
            enable_tracing=True,
            profiles_sample_rate=0.1,  # Profile 10% of transactions
            # Error sampling
            sample_rate=1.0,  # Capture 100% of errors
            # Release tracking (for source maps and deploy tracking)
            release=f"{settings.APP_NAME}@{settings.VERSION}",
            # Additional context
            attach_stacktrace=True,
            send_default_pii=False,  # Don't send PII (GDPR compliance)
            # Custom event processor
            before_send=before_send,
            # Max breadcrumbs (for debugging context)
            max_breadcrumbs=50,
            # Request bodies (size limit)
            max_request_body_size="medium",  # small/medium/large
            # Automatically track sessions
            auto_session_tracking=True,
        )

        logger.info(
            f"✅ Sentry monitoring initialized: "
            f"env={settings.SENTRY_ENVIRONMENT}, "
            f"traces={settings.SENTRY_TRACES_SAMPLE_RATE * 100}%, "
            f"release={settings.APP_NAME}@{settings.VERSION}"
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
        sentry_sdk.set_user({"id": user_id, "email": email, "username": username})


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
        sentry_sdk.add_breadcrumb(message=message, category=category, level=level, data=data or {})


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
    context = {"database": {"error_type": type(error).__name__, "query": query or "N/A"}}
    capture_exception(error, context)


def handle_ai_error(error: Exception, prompt: str = None, model: str = "gemini-1.5-flash"):
    """Handle AI service errors"""
    context = {
        "ai_service": {
            "model": model,
            "error_type": type(error).__name__,
            "prompt_length": len(prompt) if prompt else 0,
        }
    }
    capture_exception(error, context)


def handle_external_api_error(error: Exception, service: str, endpoint: str = None):
    """Handle external API errors"""
    context = {"external_api": {"service": service, "endpoint": endpoint or "N/A", "error_type": type(error).__name__}}
    capture_exception(error, context)


def handle_payment_error(error: Exception, amount: float = None, currency: str = "USD", user_id: str = None):
    """Handle payment-related errors"""
    context = {
        "payment": {
            "error_type": type(error).__name__,
            "amount": amount,
            "currency": currency,
            "user_id": user_id or "unknown",
        }
    }
    capture_exception(error, context)


# Performance monitoring decorators


def monitor_performance(operation_name: str):
    """
    Decorator to monitor function performance in Sentry

    Usage:
        @monitor_performance("analyze_resume")
        async def analyze_resume(resume_text: str):
            # ... expensive operation
            return result
    """

    def decorator(func):
        async def wrapper(*args, **kwargs):
            with start_transaction(name=operation_name, op="function"):
                return await func(*args, **kwargs)

        return wrapper

    return decorator


# Alert severity helpers


def alert_critical(message: str, context: Dict[str, Any] = None):
    """
    Send critical alert to Sentry (highest priority)

    Use for: Payment failures, data corruption, security breaches
    """
    capture_message(message, level="fatal", context=context)
    logger.critical(f"🚨 CRITICAL: {message}")


def alert_error(message: str, context: Dict[str, Any] = None):
    """
    Send error alert to Sentry

    Use for: AI failures, database errors, external API failures
    """
    capture_message(message, level="error", context=context)
    logger.error(f"❌ ERROR: {message}")


def alert_warning(message: str, context: Dict[str, Any] = None):
    """
    Send warning alert to Sentry

    Use for: Rate limit approaching, cache misses, slow queries
    """
    capture_message(message, level="warning", context=context)
    logger.warning(f"⚠️ WARNING: {message}")


def alert_info(message: str, context: Dict[str, Any] = None):
    """
    Send info message to Sentry

    Use for: Deployment events, feature usage, business metrics
    """
    capture_message(message, level="info", context=context)
    logger.info(f"ℹ️ INFO: {message}")


# Business metrics tracking


def track_user_signup(user_id: str, plan: str = "free"):
    """Track successful user signup"""
    add_breadcrumb(
        message=f"User signed up: {user_id} (plan: {plan})",
        category="user.signup",
        level="info",
        data={"user_id": user_id, "plan": plan},
    )


def track_subscription_change(user_id: str, old_plan: str, new_plan: str):
    """Track subscription upgrade/downgrade"""
    add_breadcrumb(
        message=f"Subscription changed: {old_plan} → {new_plan}",
        category="subscription.change",
        level="info",
        data={"user_id": user_id, "old_plan": old_plan, "new_plan": new_plan},
    )


def track_ai_usage(user_id: str, feature: str, tokens_used: int = 0):
    """Track AI feature usage for billing/analytics"""
    add_breadcrumb(
        message=f"AI feature used: {feature}",
        category="ai.usage",
        level="info",
        data={"user_id": user_id, "feature": feature, "tokens_used": tokens_used},
    )


def track_payment_success(user_id: str, amount: float, currency: str = "USD"):
    """Track successful payment"""
    add_breadcrumb(
        message=f"Payment successful: ${amount} {currency}",
        category="payment.success",
        level="info",
        data={"user_id": user_id, "amount": amount, "currency": currency},
    )


# Health check and status monitoring


def check_sentry_health() -> Dict[str, Any]:
    """
    Check if Sentry is properly configured and sending data

    Returns:
        Dict with status, DSN presence, environment
    """
    return {
        "enabled": bool(settings.SENTRY_DSN),
        "environment": settings.SENTRY_ENVIRONMENT,
        "traces_sample_rate": settings.SENTRY_TRACES_SAMPLE_RATE,
        "release": f"{settings.APP_NAME}@{settings.VERSION}",
    }
