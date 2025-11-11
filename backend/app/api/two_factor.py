"""
Two-Factor Authentication API Endpoints
Handles 2FA setup, verification, and recovery
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from typing import List, Optional
from app.core.auth import get_current_user
from app.services.two_factor_auth import get_tfa_service
from app.services.supabase_client import get_supabase
from loguru import logger
from datetime import datetime

router = APIRouter(prefix="/api/2fa", tags=["Two-Factor Authentication"])

# Pydantic models
class Enable2FAResponse(BaseModel):
    secret: str
    qr_code: str  # Base64 data URL
    manual_entry_code: str  # Formatted for manual entry
    backup_codes: List[str]

class Verify2FARequest(BaseModel):
    token: str = Field(..., min_length=6, max_length=6, description="6-digit TOTP code")

class Verify2FASetupRequest(BaseModel):
    secret: str
    token: str = Field(..., min_length=6, max_length=6)

class Disable2FARequest(BaseModel):
    password: str
    token: Optional[str] = None  # Required if 2FA currently enabled

class RegenerateBackupCodesRequest(BaseModel):
    password: str

class Use2FABackupCodeRequest(BaseModel):
    backup_code: str = Field(..., min_length=8, max_length=8)


@router.post("/enable/initialize", response_model=Enable2FAResponse)
async def initialize_2fa_setup(current_user=Depends(get_current_user)):
    """
    Initialize 2FA setup (step 1)

    Returns:
    - TOTP secret
    - QR code for scanning
    - Manual entry code
    - 10 backup codes

    Next step: User scans QR code, then calls /enable/verify to confirm
    """
    try:
        tfa_service = get_tfa_service()
        supabase = get_supabase()

        # Check if 2FA already enabled
        result = await supabase.table("users").select("two_factor_enabled").eq("id", current_user["user_id"]).execute()
        if result.data and result.data[0].get("two_factor_enabled"):
            raise HTTPException(400, "2FA is already enabled for this account")

        # Generate secret and QR code
        secret = tfa_service.generate_secret()
        qr_code = tfa_service.generate_qr_code(
            secret=secret,
            user_email=current_user["email"]
        )
        manual_code = tfa_service.format_secret_for_manual_entry(secret)

        # Generate backup codes
        backup_codes = tfa_service.generate_backup_codes(count=10)

        logger.info(f"2FA initialization started for user {current_user['user_id']}")

        return {
            "secret": secret,
            "qr_code": qr_code,
            "manual_entry_code": manual_code,
            "backup_codes": backup_codes
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error initializing 2FA: {e}")
        raise HTTPException(500, "Failed to initialize 2FA")


@router.post("/enable/verify")
async def verify_and_enable_2fa(
    request: Verify2FASetupRequest,
    current_user=Depends(get_current_user)
):
    """
    Verify TOTP token and enable 2FA (step 2)

    User must provide:
    - secret (from /enable/initialize)
    - token (6-digit code from authenticator app)

    If valid, enables 2FA for the account
    """
    try:
        tfa_service = get_tfa_service()
        supabase = get_supabase()

        # Verify token
        is_valid = tfa_service.verify_totp(request.secret, request.token)
        if not is_valid:
            raise HTTPException(400, "Invalid 2FA token. Please try again.")

        # Hash backup codes (from previous step - frontend should send them)
        # For now, generate new ones (frontend should store from step 1)
        backup_codes = tfa_service.generate_backup_codes(count=10)
        hashed_codes = [tfa_service.hash_backup_code(code) for code in backup_codes]

        # Enable 2FA in database
        await supabase.table("users").update({
            "two_factor_enabled": True,
            "two_factor_secret": request.secret,  # TODO: Encrypt at rest
            "two_factor_backup_codes": hashed_codes,
            "two_factor_enabled_at": datetime.utcnow().isoformat(),
            "two_factor_method": "totp"
        }).eq("id", current_user["user_id"]).execute()

        logger.info(f"✅ 2FA enabled for user {current_user['user_id']}")

        return {
            "message": "2FA successfully enabled",
            "enabled": True,
            "backup_codes": backup_codes  # Show once, user must save
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error enabling 2FA: {e}")
        raise HTTPException(500, "Failed to enable 2FA")


@router.post("/verify")
async def verify_2fa_token(
    request: Verify2FARequest,
    current_user=Depends(get_current_user)
):
    """
    Verify 2FA token during login

    Called after username/password auth succeeds
    """
    try:
        tfa_service = get_tfa_service()
        supabase = get_supabase()

        # Get user's 2FA secret
        result = await supabase.table("users").select(
            "two_factor_enabled, two_factor_secret"
        ).eq("id", current_user["user_id"]).execute()

        if not result.data:
            raise HTTPException(404, "User not found")

        user_data = result.data[0]
        if not user_data.get("two_factor_enabled"):
            raise HTTPException(400, "2FA is not enabled for this account")

        secret = user_data.get("two_factor_secret")
        if not secret:
            raise HTTPException(500, "2FA secret not found")

        # Verify token
        is_valid = tfa_service.verify_totp(secret, request.token)
        if not is_valid:
            # Record failed attempt
            await supabase.rpc("record_failed_login", {
                "user_id_param": current_user["user_id"],
                "max_attempts": 5,
                "lockout_duration_minutes": 30
            }).execute()

            raise HTTPException(401, "Invalid 2FA token")

        # Reset failed attempts on success
        await supabase.rpc("reset_failed_logins", {
            "user_id_param": current_user["user_id"]
        }).execute()

        logger.info(f"✅ 2FA verification successful for user {current_user['user_id']}")

        return {"verified": True, "message": "2FA token verified"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying 2FA token: {e}")
        raise HTTPException(500, "Failed to verify 2FA token")


@router.post("/verify-backup-code")
async def verify_backup_code(
    request: Use2FABackupCodeRequest,
    current_user=Depends(get_current_user)
):
    """
    Verify backup code (recovery method)

    Use when user lost access to authenticator app
    Backup code can only be used once
    """
    try:
        tfa_service = get_tfa_service()
        supabase = get_supabase()

        # Get user's backup codes
        result = await supabase.table("users").select(
            "two_factor_backup_codes"
        ).eq("id", current_user["user_id"]).execute()

        if not result.data:
            raise HTTPException(404, "User not found")

        backup_codes = result.data[0].get("two_factor_backup_codes", [])
        if not backup_codes:
            raise HTTPException(400, "No backup codes available")

        # Check if code matches any stored hash
        code_upper = request.backup_code.upper()
        is_valid = False
        for hashed_code in backup_codes:
            if tfa_service.verify_backup_code(code_upper, hashed_code):
                is_valid = True
                # Remove used code
                backup_codes.remove(hashed_code)
                break

        if not is_valid:
            raise HTTPException(401, "Invalid backup code")

        # Update backup codes (remove used one)
        await supabase.table("users").update({
            "two_factor_backup_codes": backup_codes
        }).eq("id", current_user["user_id"]).execute()

        # Reset failed attempts
        await supabase.rpc("reset_failed_logins", {
            "user_id_param": current_user["user_id"]
        }).execute()

        remaining_codes = len(backup_codes)
        logger.info(f"✅ Backup code used for user {current_user['user_id']} ({remaining_codes} remaining)")

        return {
            "verified": True,
            "message": "Backup code verified",
            "remaining_codes": remaining_codes
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying backup code: {e}")
        raise HTTPException(500, "Failed to verify backup code")


@router.post("/disable")
async def disable_2fa(
    request: Disable2FARequest,
    current_user=Depends(get_current_user)
):
    """
    Disable 2FA for account

    Requires:
    - Password verification
    - 2FA token (if currently enabled)
    """
    try:
        supabase = get_supabase()

        # TODO: Verify password (implement password verification)
        # For now, just check if password is provided
        if not request.password:
            raise HTTPException(400, "Password is required")

        # If 2FA enabled, verify token
        result = await supabase.table("users").select(
            "two_factor_enabled, two_factor_secret"
        ).eq("id", current_user["user_id"]).execute()

        if result.data and result.data[0].get("two_factor_enabled"):
            if not request.token:
                raise HTTPException(400, "2FA token required to disable 2FA")

            tfa_service = get_tfa_service()
            secret = result.data[0].get("two_factor_secret")
            if not tfa_service.verify_totp(secret, request.token):
                raise HTTPException(401, "Invalid 2FA token")

        # Disable 2FA
        await supabase.table("users").update({
            "two_factor_enabled": False,
            "two_factor_secret": None,
            "two_factor_backup_codes": None
        }).eq("id", current_user["user_id"]).execute()

        logger.info(f"2FA disabled for user {current_user['user_id']}")

        return {"message": "2FA successfully disabled", "enabled": False}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error disabling 2FA: {e}")
        raise HTTPException(500, "Failed to disable 2FA")


@router.post("/regenerate-backup-codes", response_model=dict)
async def regenerate_backup_codes(
    request: RegenerateBackupCodesRequest,
    current_user=Depends(get_current_user)
):
    """
    Regenerate backup codes

    Use when user used all backup codes or lost them
    Old codes are invalidated
    """
    try:
        tfa_service = get_tfa_service()
        supabase = get_supabase()

        # TODO: Verify password
        if not request.password:
            raise HTTPException(400, "Password is required")

        # Check if 2FA enabled
        result = await supabase.table("users").select(
            "two_factor_enabled"
        ).eq("id", current_user["user_id"]).execute()

        if not result.data or not result.data[0].get("two_factor_enabled"):
            raise HTTPException(400, "2FA is not enabled")

        # Generate new backup codes
        backup_codes = tfa_service.generate_backup_codes(count=10)
        hashed_codes = [tfa_service.hash_backup_code(code) for code in backup_codes]

        # Update database
        await supabase.table("users").update({
            "two_factor_backup_codes": hashed_codes
        }).eq("id", current_user["user_id"]).execute()

        logger.info(f"Backup codes regenerated for user {current_user['user_id']}")

        return {
            "message": "Backup codes regenerated",
            "backup_codes": backup_codes  # Show once, user must save
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error regenerating backup codes: {e}")
        raise HTTPException(500, "Failed to regenerate backup codes")


@router.get("/status")
async def get_2fa_status(current_user=Depends(get_current_user)):
    """
    Get 2FA status for current user

    Returns:
    - enabled: Whether 2FA is enabled
    - method: 'totp' or 'sms'
    - enabled_at: When 2FA was enabled
    - backup_codes_remaining: Number of unused backup codes
    """
    try:
        supabase = get_supabase()

        result = await supabase.table("users").select(
            "two_factor_enabled, two_factor_method, two_factor_enabled_at, two_factor_backup_codes"
        ).eq("id", current_user["user_id"]).execute()

        if not result.data:
            raise HTTPException(404, "User not found")

        user_data = result.data[0]
        backup_codes = user_data.get("two_factor_backup_codes", [])

        return {
            "enabled": user_data.get("two_factor_enabled", False),
            "method": user_data.get("two_factor_method", "totp"),
            "enabled_at": user_data.get("two_factor_enabled_at"),
            "backup_codes_remaining": len(backup_codes)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting 2FA status: {e}")
        raise HTTPException(500, "Failed to get 2FA status")
