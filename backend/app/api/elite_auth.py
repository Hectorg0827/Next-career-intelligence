"""
Elite/Admin authentication endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from loguru import logger
import hashlib
import os

from app.models.database import User
from app.db.database import get_db

router = APIRouter()

# Elite credentials - stored securely
ELITE_USERNAME = "elite_admin"
ELITE_PASSWORD_HASH = hashlib.sha256("NextElite2025!".encode()).hexdigest()
ELITE_EMAIL = "elite@nextci.net"

class EliteLoginRequest(BaseModel):
    username: str
    password: str

class EliteLoginResponse(BaseModel):
    success: bool
    message: str
    user_id: str
    firebase_uid: str
    email: str
    role: str
    subscription_status: str

@router.post("/elite/login", response_model=EliteLoginResponse)
async def elite_login(
    credentials: EliteLoginRequest,
    db: Session = Depends(get_db)
):
    """
    Elite/Admin login endpoint
    Username: elite_admin
    Password: NextElite2025!
    """
    
    try:
        # Verify credentials
        password_hash = hashlib.sha256(credentials.password.encode()).hexdigest()
        
        if credentials.username != ELITE_USERNAME or password_hash != ELITE_PASSWORD_HASH:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid elite credentials"
            )
        
        # Find or create elite user
        elite_user = db.query(User).filter(User.email == ELITE_EMAIL).first()
        
        if not elite_user:
            # Create elite user
            elite_user = User(
                email=ELITE_EMAIL,
                firebase_uid=f"elite_{hashlib.md5(ELITE_EMAIL.encode()).hexdigest()}",
                name="Elite Admin",
                role="admin",
                subscription_status="elite"
            )
            db.add(elite_user)
            db.commit()
            db.refresh(elite_user)
            logger.info(f"Elite admin user created: {elite_user.email}")
        else:
            # Update to ensure admin privileges
            elite_user.role = "admin"
            elite_user.subscription_status = "elite"
            db.commit()
            db.refresh(elite_user)
            logger.info(f"Elite admin user logged in: {elite_user.email}")
        
        return EliteLoginResponse(
            success=True,
            message="Elite login successful",
            user_id=elite_user.id,
            firebase_uid=elite_user.firebase_uid,
            email=elite_user.email,
            role=elite_user.role,
            subscription_status=elite_user.subscription_status
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Elite login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Elite login failed"
        )


@router.get("/elite/status")
async def elite_status(
    firebase_uid: str,
    db: Session = Depends(get_db)
):
    """
    Check if a user has elite/admin privileges
    """
    
    try:
        user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
        
        if not user:
            return {
                "is_elite": False,
                "is_admin": False,
                "role": "none",
                "subscription_status": "none"
            }
        
        return {
            "is_elite": user.role in ["elite", "admin"],
            "is_admin": user.role == "admin",
            "role": user.role,
            "subscription_status": user.subscription_status
        }
        
    except Exception as e:
        logger.error(f"Failed to check elite status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check elite status"
        )
