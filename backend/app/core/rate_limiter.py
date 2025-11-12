"""
Rate Limiting Middleware for NEXT Career Intelligence
Prevents API abuse and ensures fair resource usage
"""

from fastapi import Request, HTTPException
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from loguru import logger
from app.core.config import settings

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute", "1000/hour", "5000/day"],
    storage_uri=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/1" if settings.REDIS_HOST else "memory://",
    strategy="fixed-window",
)


def get_rate_limiter():
    """Get the rate limiter instance"""
    return limiter


# Custom rate limits for different endpoint types

# Authentication endpoints (more restrictive)
AUTH_RATE_LIMIT = "5/minute, 20/hour"

# AI endpoints (expensive operations)
AI_RATE_LIMIT = "10/minute, 100/hour"

# Search/query endpoints
SEARCH_RATE_LIMIT = "30/minute, 300/hour"

# Standard API endpoints
STANDARD_RATE_LIMIT = "50/minute, 500/hour"

# Premium user rate limits (higher limits)
PREMIUM_RATE_LIMIT = "200/minute, 2000/hour, 10000/day"


def get_user_tier(request: Request) -> str:
    """
    Determine user tier from request
    Returns: 'free', 'premium', or 'enterprise'
    """
    # Check for authentication token and subscription tier
    auth_header = request.headers.get("Authorization", "")

    # TODO: Implement proper tier detection from JWT token
    # For now, return 'free' by default

    if "premium" in auth_header.lower():
        return "premium"
    elif "enterprise" in auth_header.lower():
        return "enterprise"

    return "free"


def get_rate_limit_for_tier(tier: str, endpoint_type: str = "standard") -> str:
    """
    Get rate limit string based on user tier and endpoint type

    Args:
        tier: User tier ('free', 'premium', 'enterprise')
        endpoint_type: Type of endpoint ('auth', 'ai', 'search', 'standard')

    Returns:
        Rate limit string (e.g., "100/minute")
    """
    rate_limits = {
        "free": {
            "auth": "5/minute, 20/hour",
            "ai": "5/minute, 50/hour",
            "search": "20/minute, 200/hour",
            "standard": "50/minute, 500/hour",
        },
        "premium": {
            "auth": "20/minute, 100/hour",
            "ai": "30/minute, 300/hour",
            "search": "100/minute, 1000/hour",
            "standard": "200/minute, 2000/hour",
        },
        "enterprise": {
            "auth": "100/minute, 500/hour",
            "ai": "100/minute, 1000/hour",
            "search": "500/minute, 5000/hour",
            "standard": "1000/minute, 10000/hour",
        },
    }

    return rate_limits.get(tier, rate_limits["free"]).get(endpoint_type, STANDARD_RATE_LIMIT)


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """
    Custom handler for rate limit exceeded errors
    """
    logger.warning(f"Rate limit exceeded for {get_remote_address(request)}: {request.url.path}")

    return {
        "error": "rate_limit_exceeded",
        "message": "Too many requests. Please try again later.",
        "retry_after": exc.retry_after if hasattr(exc, "retry_after") else 60,
        "tier": get_user_tier(request),
        "upgrade_message": "Upgrade to Premium for higher rate limits",
    }


# Decorator for custom rate limiting on specific routes
def custom_rate_limit(limit: str):
    """
    Custom rate limit decorator

    Usage:
        @app.get("/expensive-operation")
        @custom_rate_limit("5/minute")
        async def expensive_operation():
            pass
    """

    def decorator(func):
        return limiter.limit(limit)(func)

    return decorator


# Rate limit monitoring
async def get_rate_limit_stats(ip_address: str) -> dict:
    """
    Get rate limit statistics for an IP address

    Args:
        ip_address: IP address to check

    Returns:
        Dictionary with rate limit stats
    """
    try:
        # TODO: Implement actual Redis-based stats retrieval
        return {"ip": ip_address, "requests_remaining": "N/A", "reset_time": "N/A", "status": "tracked"}
    except Exception as e:
        logger.error(f"Failed to get rate limit stats: {e}")
        return {"error": str(e)}


# Whitelist and blacklist management
WHITELISTED_IPS = set()
BLACKLISTED_IPS = set()


def add_to_whitelist(ip_address: str):
    """Add IP to whitelist (no rate limiting)"""
    WHITELISTED_IPS.add(ip_address)
    logger.info(f"IP added to whitelist: {ip_address}")


def add_to_blacklist(ip_address: str):
    """Add IP to blacklist (blocked)"""
    BLACKLISTED_IPS.add(ip_address)
    logger.warning(f"IP added to blacklist: {ip_address}")


def is_whitelisted(ip_address: str) -> bool:
    """Check if IP is whitelisted"""
    return ip_address in WHITELISTED_IPS


def is_blacklisted(ip_address: str) -> bool:
    """Check if IP is blacklisted"""
    return ip_address in BLACKLISTED_IPS


async def check_ip_access(request: Request) -> bool:
    """
    Check if IP should be allowed access

    Returns:
        True if allowed, raises HTTPException if blocked
    """
    ip = get_remote_address(request)

    if is_blacklisted(ip):
        logger.warning(f"Blocked request from blacklisted IP: {ip}")
        raise HTTPException(status_code=403, detail="Access denied. Your IP has been blocked.")

    return True
