"""
Firebase Authentication Middleware
Handles JWT token verification and user extraction
"""

from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
from loguru import logger
import firebase_admin
from firebase_admin import auth, credentials
import os
from functools import lru_cache

# Initialize Firebase Admin SDK
_firebase_app = None

def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    global _firebase_app

    if _firebase_app is not None:
        return _firebase_app

    try:
        # Check if running in Google Cloud (uses Application Default Credentials)
        if os.getenv("GOOGLE_CLOUD_PROJECT"):
            _firebase_app = firebase_admin.initialize_app()
            logger.info("✅ Firebase initialized with Application Default Credentials")
        else:
            # Local development - use service account key
            cred_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
            if cred_path and os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                _firebase_app = firebase_admin.initialize_app(cred)
                logger.info("✅ Firebase initialized with service account")
            else:
                logger.warning("⚠️ Firebase not configured - auth disabled for development")
                return None
    except Exception as e:
        logger.error(f"❌ Firebase initialization failed: {e}")
        return None

    return _firebase_app

# Initialize on module load
initialize_firebase()

# Security scheme
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
) -> Dict[str, Any]:
    """
    Extract and verify user from Firebase JWT token

    Returns user dict with:
    - user_id: Firebase UID
    - email: User email
    - email_verified: Boolean
    - firebase_token: Original token
    """
    # Development mode - allow bypass if Firebase not configured
    if _firebase_app is None:
        logger.warning("⚠️ Auth bypass - Firebase not configured")
        return {
            "user_id": "dev_user_123",
            "email": "dev@example.com",
            "email_verified": True,
            "dev_mode": True
        }

    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    try:
        # Verify the Firebase ID token
        decoded_token = auth.verify_id_token(credentials.credentials)

        return {
            "user_id": decoded_token["uid"],
            "email": decoded_token.get("email"),
            "email_verified": decoded_token.get("email_verified", False),
            "firebase_token": decoded_token
        }

    except auth.ExpiredIdTokenError:
        raise HTTPException(
            status_code=401,
            detail="Token has expired. Please login again.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except auth.RevokedIdTokenError:
        raise HTTPException(
            status_code=401,
            detail="Token has been revoked. Please login again.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except auth.InvalidIdTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=401,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"}
        )


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
) -> Optional[Dict[str, Any]]:
    """
    Optional authentication - returns None if no token provided
    Useful for endpoints that work both authenticated and unauthenticated
    """
    if not credentials:
        return None

    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


async def require_premium(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Require premium subscription
    Checks user's subscription tier from database
    """
    from app.db.supabase import get_supabase_client

    # Development mode bypass
    if current_user.get("dev_mode"):
        logger.warning("⚠️ Premium check bypass - dev mode")
        current_user["subscription_tier"] = "premium"
        return current_user

    try:
        client = get_supabase_client()
        if not client:
            # If database unavailable, allow access in development
            logger.warning("⚠️ Database unavailable - allowing premium access")
            current_user["subscription_tier"] = "premium"
            return current_user

        # Check subscription
        response = client.table('subscriptions')\
            .select('tier, status')\
            .eq('user_id', current_user['user_id'])\
            .eq('status', 'active')\
            .single()\
            .execute()

        if response.data:
            tier = response.data.get('tier', 'free')
            current_user["subscription_tier"] = tier

            if tier in ['premium', 'enterprise']:
                return current_user
            else:
                raise HTTPException(
                    status_code=403,
                    detail="Premium subscription required. Please upgrade your plan."
                )
        else:
            # No active subscription - default to free
            raise HTTPException(
                status_code=403,
                detail="Premium subscription required. Please upgrade your plan."
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Subscription check error: {e}")
        # In case of error, allow access but log it
        logger.warning("⚠️ Subscription check failed - allowing access")
        current_user["subscription_tier"] = "free"
        return current_user


async def require_enterprise(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Require enterprise subscription
    """
    current_user = await require_premium(current_user)

    if current_user.get("subscription_tier") != "enterprise":
        raise HTTPException(
            status_code=403,
            detail="Enterprise subscription required"
        )

    return current_user


# Helper function to get user from Supabase or create
async def get_or_create_user(firebase_user: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get user from Supabase database or create if doesn't exist
    """
    from app.db.supabase import get_supabase_client

    client = get_supabase_client()
    if not client:
        return firebase_user

    try:
        # Try to get existing user
        response = client.table('users')\
            .select('*')\
            .eq('firebase_uid', firebase_user['user_id'])\
            .single()\
            .execute()

        if response.data:
            return {**firebase_user, **response.data}

        # Create new user
        new_user = client.table('users')\
            .insert({
                'firebase_uid': firebase_user['user_id'],
                'email': firebase_user['email'],
                'name': firebase_user.get('name')
            })\
            .execute()

        if new_user.data:
            logger.info(f"✅ Created new user: {firebase_user['email']}")
            return {**firebase_user, **new_user.data[0]}

        return firebase_user

    except Exception as e:
        logger.error(f"Get or create user error: {e}")
        return firebase_user
