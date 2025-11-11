"""
Security Middleware
Adds security headers to all HTTP responses

Headers implemented:
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: 1; mode=block
- Strict-Transport-Security: max-age=31536000
- Content-Security-Policy: Comprehensive CSP
- Referrer-Policy: strict-origin-when-cross-origin
- Permissions-Policy: Restrict browser features
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from typing import Callable
from loguru import logger


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Add security headers to response

        Reference: OWASP Secure Headers Project
        https://owasp.org/www-project-secure-headers/
        """
        response = await call_next(request)

        # Prevent MIME type sniffing
        # Stops browsers from trying to guess content type
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Clickjacking protection
        # Prevents site from being embedded in iframe
        response.headers["X-Frame-Options"] = "DENY"

        # XSS filter (legacy, but still useful for old browsers)
        # Enables browser's XSS filtering
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Force HTTPS (only add in production)
        # Tells browsers to only access site via HTTPS
        # max-age=31536000 = 1 year
        # includeSubDomains = apply to all subdomains
        if not request.url.hostname in ["localhost", "127.0.0.1"]:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"

        # Content Security Policy (CSP)
        # Prevents XSS, code injection, clickjacking
        csp_directives = [
            "default-src 'self'",  # Only load resources from same origin
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://www.googletagmanager.com",  # Allow scripts from self + CDNs
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",  # Allow styles from self + Google Fonts
            "font-src 'self' https://fonts.gstatic.com data:",  # Allow fonts from self + Google Fonts
            "img-src 'self' data: https: blob:",  # Allow images from anywhere (for user uploads)
            "connect-src 'self' https://api.nextcareer.ai https://*.supabase.co https://o123456.ingest.sentry.io",  # API endpoints
            "frame-ancestors 'none'",  # Don't allow embedding (same as X-Frame-Options)
            "base-uri 'self'",  # Restrict <base> tag
            "form-action 'self'",  # Only submit forms to same origin
            "upgrade-insecure-requests",  # Upgrade HTTP to HTTPS
        ]
        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)

        # Referrer policy
        # Controls how much referrer information is sent
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions Policy (formerly Feature-Policy)
        # Restricts browser features
        permissions_directives = [
            "geolocation=()",  # Disable geolocation
            "microphone=()",  # Disable microphone
            "camera=()",  # Disable camera
            "payment=(self)",  # Allow payment API on same origin
            "usb=()",  # Disable USB
            "magnetometer=()",  # Disable magnetometer
            "gyroscope=()",  # Disable gyroscope
            "accelerometer=()",  # Disable accelerometer
        ]
        response.headers["Permissions-Policy"] = ", ".join(permissions_directives)

        # Remove server information (security through obscurity)
        # Don't advertise what framework/server we're using
        response.headers.pop("Server", None)
        response.headers["Server"] = "NEXT"

        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple rate limiting middleware

    Note: For production, use Redis-based rate limiting (already implemented in cache.py)
    This is a fallback/additional layer
    """

    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.request_counts = {}  # In-memory store (not suitable for multi-instance)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Track request count per IP

        WARNING: This is a simple implementation for single-instance deployments.
        For production with multiple instances, use Redis rate limiting.
        """
        client_ip = request.client.host

        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/api/health"]:
            return await call_next(request)

        # TODO: Implement sliding window with Redis
        # For now, just pass through
        # Real implementation in app/core/cache.py (RateLimiter class)

        response = await call_next(request)
        return response


class AccountLockoutMiddleware(BaseHTTPMiddleware):
    """
    Check if account is locked before processing request

    Works with database function: is_account_locked()
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Check if user account is locked

        If locked, return 403 Forbidden with lock expiry time
        """
        # Skip for non-authenticated endpoints
        if not request.url.path.startswith("/api"):
            return await call_next(request)

        # Skip for auth endpoints (login, signup)
        if request.url.path in ["/api/auth/login", "/api/auth/signup", "/api/health"]:
            return await call_next(request)

        # Check if Authorization header present
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return await call_next(request)

        # Extract user_id from JWT (if available)
        # This check happens AFTER JWT verification in get_current_user()
        # So we'll let the auth middleware handle extraction
        # Just pass through for now

        response = await call_next(request)
        return response
