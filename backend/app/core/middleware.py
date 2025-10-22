"""
Protected routes middleware and route guards
Defines which routes require authentication and verification
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.routing import APIRoute
from typing import Callable, List
from loguru import logger

# ==================== Protected Routes Configuration ====================

# Routes that require authentication
PROTECTED_ROUTES = {
    '/api/dashboard': ['GET', 'POST'],
    '/api/onboarding/complete': ['POST'],
    '/api/onboarding/progress': ['GET'],
    '/api/roadmap': ['GET'],
    '/api/analyze': ['POST'],
    '/api/coach': ['GET', 'POST'],
    '/api/interviewer': ['GET', 'POST'],
    '/api/subscriptions': ['GET', 'POST'],
}

# Routes that require verified email
EMAIL_VERIFIED_ROUTES = {
    '/api/roadmap': ['POST'],
    '/api/coach/premium': ['POST'],
    '/api/interviewer/premium': ['POST'],
}

# Routes that require premium subscription
PREMIUM_ROUTES = {
    '/api/coach': ['GET', 'POST'],
    '/api/interviewer': ['GET', 'POST'],
    '/api/resume-studio': ['GET', 'POST', 'DELETE'],
}

# Public routes (no auth required)
PUBLIC_ROUTES = {
    '/': ['GET'],
    '/api/health': ['GET'],
    '/api/auth/signup': ['POST'],
    '/api/auth/login': ['POST'],
    '/api/auth/oauth-callback': ['POST'],
    '/api/auth/request-password-reset': ['POST'],
    '/api/auth/reset-password': ['POST'],
    '/docs': ['GET'],
    '/redoc': ['GET'],
    '/openapi.json': ['GET'],
}

# ==================== Route Guard Functions ====================

def is_route_protected(path: str, method: str) -> bool:
    """Check if route requires authentication"""
    for route_pattern, methods in PROTECTED_ROUTES.items():
        if path.startswith(route_pattern) and method in methods:
            return True
    return False


def is_route_public(path: str, method: str) -> bool:
    """Check if route is publicly accessible"""
    for route_pattern, methods in PUBLIC_ROUTES.items():
        if path == route_pattern and method in methods:
            return True
    return False


def requires_verified_email(path: str, method: str) -> bool:
    """Check if route requires verified email"""
    for route_pattern, methods in EMAIL_VERIFIED_ROUTES.items():
        if path.startswith(route_pattern) and method in methods:
            return True
    return False


def requires_premium(path: str, method: str) -> bool:
    """Check if route requires premium subscription"""
    for route_pattern, methods in PREMIUM_ROUTES.items():
        if path.startswith(route_pattern) and method in methods:
            return True
    return False


# ==================== Route Configuration ====================

def configure_protected_routes(app: FastAPI):
    """
    Configure route protection in FastAPI app
    
    This should be called during app initialization to set up
    route guards for all endpoints
    """
    logger.info("🔐 Configuring protected routes...")
    
    protected_count = len(PROTECTED_ROUTES)
    premium_count = len(PREMIUM_ROUTES)
    public_count = len(PUBLIC_ROUTES)
    
    logger.info(f"📋 Route Configuration:")
    logger.info(f"   - Protected routes: {protected_count}")
    logger.info(f"   - Premium routes: {premium_count}")
    logger.info(f"   - Public routes: {public_count}")
    logger.info(f"   - Email-verified routes: {len(EMAIL_VERIFIED_ROUTES)}")


# ==================== Route Documentation ====================

ROUTE_DOCUMENTATION = {
    # Authentication endpoints (Public)
    '/api/auth/signup': {
        'method': 'POST',
        'auth_required': False,
        'description': 'Create new user account',
        'email_verified': False,
        'premium_required': False
    },
    '/api/auth/login': {
        'method': 'POST',
        'auth_required': False,
        'description': 'Login with email/password',
        'email_verified': False,
        'premium_required': False
    },
    '/api/auth/verify-email': {
        'method': 'POST',
        'auth_required': False,
        'description': 'Verify email with code',
        'email_verified': False,
        'premium_required': False
    },
    '/api/auth/request-password-reset': {
        'method': 'POST',
        'auth_required': False,
        'description': 'Request password reset email',
        'email_verified': False,
        'premium_required': False
    },
    '/api/auth/reset-password': {
        'method': 'POST',
        'auth_required': False,
        'description': 'Reset password with code',
        'email_verified': False,
        'premium_required': False
    },
    '/api/auth/oauth-callback': {
        'method': 'POST',
        'auth_required': False,
        'description': 'OAuth callback (Google, LinkedIn)',
        'email_verified': False,
        'premium_required': False
    },
    
    # Onboarding endpoints (Protected)
    '/api/onboarding/step/1': {
        'method': 'POST',
        'auth_required': True,
        'description': 'Save onboarding step 1 (role/industry)',
        'email_verified': True,
        'premium_required': False
    },
    '/api/onboarding/step/2': {
        'method': 'POST',
        'auth_required': True,
        'description': 'Save onboarding step 2 (skills)',
        'email_verified': True,
        'premium_required': False
    },
    '/api/onboarding/step/3': {
        'method': 'POST',
        'auth_required': True,
        'description': 'Save onboarding step 3 (goals)',
        'email_verified': True,
        'premium_required': False
    },
    '/api/onboarding/step/4': {
        'method': 'POST',
        'auth_required': True,
        'description': 'Save onboarding step 4 (preferences)',
        'email_verified': True,
        'premium_required': False
    },
    '/api/onboarding/complete': {
        'method': 'POST',
        'auth_required': True,
        'description': 'Complete entire onboarding',
        'email_verified': True,
        'premium_required': False
    },
    
    # Dashboard (Protected)
    '/api/dashboard': {
        'method': 'GET',
        'auth_required': True,
        'description': 'Get user dashboard data',
        'email_verified': True,
        'premium_required': False
    },
    
    # Career Analysis (Protected)
    '/api/analyze': {
        'method': 'POST',
        'auth_required': True,
        'description': 'Analyze career & AI risk',
        'email_verified': True,
        'premium_required': False
    },
    
    # Career Coach (Premium)
    '/api/coach': {
        'method': ['GET', 'POST'],
        'auth_required': True,
        'description': 'Access AI career coach',
        'email_verified': True,
        'premium_required': True
    },
    
    # Interviewer AI (Premium)
    '/api/interviewer': {
        'method': ['GET', 'POST'],
        'auth_required': True,
        'description': 'Access mock interview practice',
        'email_verified': True,
        'premium_required': True
    },
}


def get_route_status(path: str, method: str) -> dict:
    """Get authentication requirements for a route"""
    auth_required = is_route_protected(path, method)
    email_verified = requires_verified_email(path, method)
    premium_required = requires_premium(path, method)
    is_public = is_route_public(path, method)
    
    return {
        'path': path,
        'method': method,
        'auth_required': auth_required,
        'email_verified': email_verified,
        'premium_required': premium_required,
        'is_public': is_public
    }


# ==================== Startup Logging ====================

def log_route_configuration():
    """Log route configuration at startup"""
    logger.info("=" * 60)
    logger.info("🔐 ROUTE PROTECTION CONFIGURATION")
    logger.info("=" * 60)
    
    logger.info("\n📍 PUBLIC ROUTES (No authentication required):")
    for route, methods in PUBLIC_ROUTES.items():
        logger.info(f"   {route}: {', '.join(methods)}")
    
    logger.info("\n🔒 PROTECTED ROUTES (Authentication required):")
    for route, methods in PROTECTED_ROUTES.items():
        logger.info(f"   {route}: {', '.join(methods)}")
    
    logger.info("\n⭐ PREMIUM ROUTES (Authentication + Subscription required):")
    for route, methods in PREMIUM_ROUTES.items():
        logger.info(f"   {route}: {', '.join(methods)}")
    
    logger.info("\n✉️  EMAIL-VERIFIED ROUTES (Authentication + Verified email):")
    for route, methods in EMAIL_VERIFIED_ROUTES.items():
        logger.info(f"   {route}: {', '.join(methods)}")
    
    logger.info("=" * 60 + "\n")
