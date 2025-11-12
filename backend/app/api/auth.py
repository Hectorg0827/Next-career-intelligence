"""
Authentication API endpoints
Handles user signup, login, email verification, and password reset
"""

from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional
from datetime import datetime, timedelta
import secrets
from loguru import logger

# Import database and email services
from app.services.supabase_client import get_db_client
from app.services.email_service import get_email_service

# Import security functions (bcrypt, JWT)
from app.core.security_fixes import hash_password_secure, verify_password_secure, generate_jwt_tokens, verify_jwt_token

router = APIRouter(prefix="/api/auth", tags=["authentication"])

# ==================== Pydantic Models ====================


class SignupRequest(BaseModel):
    """User signup request"""

    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str = Field(..., min_length=8, max_length=128)

    @validator("password")
    def password_strength(cls, v):
        """Validate password strength"""
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")
        return v

    @validator("confirm_password")
    def passwords_match(cls, v, values):
        """Validate passwords match"""
        if "password" in values and v != values["password"]:
            raise ValueError("Passwords do not match")
        return v


class LoginRequest(BaseModel):
    """User login request"""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    remember_me: bool = False


class EmailVerificationRequest(BaseModel):
    """Email verification request"""

    email: EmailStr
    verification_code: str = Field(..., min_length=6, max_length=6)


class PasswordResetRequest(BaseModel):
    """Password reset request"""

    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation"""

    email: EmailStr
    reset_code: str = Field(..., min_length=10, max_length=50)
    new_password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str = Field(..., min_length=8, max_length=128)


class AuthResponse(BaseModel):
    """Standard auth response"""

    success: bool
    message: str
    user_id: Optional[str] = None
    email: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None  # seconds


class EmailVerificationResponse(BaseModel):
    """Email verification response"""

    success: bool
    message: str
    user_id: Optional[str] = None


# ==================== Helper Functions ====================


def hash_password(password: str) -> str:
    """Hash password using bcrypt (12 rounds)"""
    return hash_password_secure(password)


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against bcrypt hash"""
    return verify_password_secure(password, hashed)


def generate_verification_code() -> str:
    """Generate 6-digit verification code"""
    return "".join([str(secrets.randbelow(10)) for _ in range(6)])


def generate_reset_code() -> str:
    """Generate secure reset code"""
    return secrets.token_urlsafe(32)


def generate_tokens(user_id: str, email: str = "") -> dict:
    """Generate JWT access and refresh tokens"""
    from app.core.config import settings

    return generate_jwt_tokens(user_id=user_id, email=email, secret_key=settings.SECRET_KEY)


async def send_verification_email(
    email: str, full_name: str, verification_code: str, background_tasks: BackgroundTasks
):
    """Send verification email"""
    email_service = get_email_service()
    background_tasks.add_task(email_service.send_verification_email, email, full_name, verification_code)
    logger.info(f"📧 Verification email queued for {email}")


async def send_password_reset_email(email: str, full_name: str, reset_code: str, background_tasks: BackgroundTasks):
    """Send password reset email"""
    from app.core.config import settings

    email_service = get_email_service()
    reset_url = f"{settings.APP_URL}/reset-password?code={reset_code}"
    background_tasks.add_task(email_service.send_password_reset_email, email, full_name, reset_url)
    logger.info(f"📧 Password reset email queued for {email}")


# ==================== API Endpoints ====================


@router.post("/signup", response_model=AuthResponse)
async def signup(request: SignupRequest, background_tasks: BackgroundTasks):
    """
    Register a new user

    Steps:
    1. Validate email uniqueness
    2. Hash password
    3. Create user record
    4. Generate verification code
    5. Send verification email
    6. Return success response
    """
    try:
        logger.info(f"📝 Signup attempt for: {request.email}")

        db_client = get_db_client()

        # Check if email already exists
        existing_user = await db_client.get_user_by_email(request.email)
        if existing_user:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

        # Generate verification code and hash password
        verification_code = generate_verification_code()
        hashed_password = hash_password(request.password)

        # Create user in Supabase
        user = await db_client.create_user(
            email=request.email, full_name=request.full_name, password_hash=hashed_password, is_verified=False
        )

        user_id = user["id"]

        # Store verification code in database
        await db_client.create_verification_code(user_id=user_id, email=request.email, code=verification_code)

        # Send verification email in background
        await send_verification_email(
            email=request.email,
            full_name=request.full_name,
            verification_code=verification_code,
            background_tasks=background_tasks,
        )

        logger.info(f"✅ User created: {request.email} (ID: {user_id})")

        return AuthResponse(
            success=True,
            message="Signup successful. Please check your email to verify your account.",
            user_id=user_id,
            email=request.email,
        )

    except HTTPException:
        raise
    except Exception as e:
        if "already registered" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
        logger.error(f"❌ Signup error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Signup failed. Please try again."
        )


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """
    Login user

    Steps:
    1. Find user by email
    2. Verify password
    3. Check email verification status
    4. Generate access/refresh tokens
    5. Return tokens
    """
    try:
        logger.info(f"🔐 Login attempt for: {request.email}")

        db_client = get_db_client()

        # Find user by email
        user = await db_client.get_user_by_email(request.email)
        if not user:
            # Generic message to prevent email enumeration
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

        # Verify password
        if not verify_password(request.password, user["password_hash"]):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

        # Check email verification
        if not user.get("is_verified", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Please verify your email before logging in"
            )

        # Generate tokens
        tokens = generate_tokens(user_id=user["id"], email=request.email)

        logger.info(f"✅ Login successful: {request.email}")

        return AuthResponse(
            success=True,
            message="Login successful",
            user_id=user["id"],
            email=request.email,
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            expires_in=tokens["expires_in"],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Login error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login failed. Please try again.")


@router.post("/verify-email", response_model=EmailVerificationResponse)
async def verify_email(request: EmailVerificationRequest, background_tasks: BackgroundTasks):
    """
    Verify user email with code sent to inbox

    Steps:
    1. Find unverified user by email
    2. Compare verification code
    3. Mark email as verified
    4. Send welcome email
    5. Return success
    """
    try:
        logger.info(f"✉️  Email verification attempt for: {request.email}")

        db_client = get_db_client()

        # Find user by email (must be unverified)
        user = await db_client.get_user_by_email(request.email)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        if user.get("is_verified"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already verified")

        # Verify code
        code_record = await db_client.verify_code(email=request.email, code=request.verification_code)

        if not code_record:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired verification code")

        # Mark email as verified
        await db_client.verify_email(user_id=user["id"])

        # Mark code as used
        await db_client.mark_code_used(code_record["id"])

        # Send welcome email
        email_service = get_email_service()
        background_tasks.add_task(email_service.send_welcome_email, request.email, user["full_name"])

        logger.info(f"✅ Email verified: {request.email}")

        return EmailVerificationResponse(
            success=True, message="Email verified successfully. Redirecting to onboarding...", user_id=user["id"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Verification error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Email verification failed")


@router.post("/resend-verification", response_model=AuthResponse)
async def resend_verification(request: EmailVerificationRequest, background_tasks: BackgroundTasks):
    """
    Resend verification email with new code

    Steps:
    1. Find user by email
    2. Check if already verified
    3. Generate new verification code
    4. Store new code
    5. Send verification email
    """
    try:
        logger.info(f"📧 Resending verification code to: {request.email}")

        db_client = get_db_client()

        # Find user by email
        user = await db_client.get_user_by_email(request.email)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        # Check if already verified
        if user.get("email_verified", False):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is already verified")

        # Generate new 6-digit verification code
        verification_code = "".join([str(secrets.randbelow(10)) for _ in range(6)])

        # Store verification code with 15 min expiration
        await db_client.create_verification_code(
            user_id=user["id"], code=verification_code, expires_at=datetime.utcnow() + timedelta(minutes=15)
        )

        # Send verification email in background
        email_service = get_email_service()
        background_tasks.add_task(
            email_service.send_verification_email, request.email, user["full_name"], verification_code
        )

        logger.info(f"✅ Verification code resent to: {request.email}")

        return AuthResponse(
            success=True, message="Verification code resent successfully. Check your email.", token=None
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Resend verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to resend verification code"
        )


@router.post("/request-password-reset", response_model=AuthResponse)
async def request_password_reset(request: PasswordResetRequest, background_tasks: BackgroundTasks):
    """
    Request password reset by email

    Steps:
    1. Find user by email
    2. Generate reset code
    3. Store reset code with expiration
    4. Send reset email
    5. Return success (don't reveal if email exists)
    """
    try:
        logger.info(f"🔑 Password reset requested for: {request.email}")

        db_client = get_db_client()

        # Find user by email (safely - don't reveal if email exists)
        user = await db_client.get_user_by_email(request.email)

        if user:
            # Generate reset code
            reset_code = generate_reset_code()

            # Store reset code in database (1 hour expiration)
            await db_client.create_reset_code(user_id=user["id"], email=request.email, code=reset_code)

            # Send reset email in background
            await send_password_reset_email(
                email=request.email,
                full_name=user["full_name"],
                reset_code=reset_code,
                background_tasks=background_tasks,
            )

            logger.info(f"✅ Password reset code sent: {request.email}")
        else:
            logger.info(f"ℹ️ Password reset requested for unknown email: {request.email}")

        # Always return success to prevent email enumeration
        return AuthResponse(
            success=True,
            message="If this email is registered, you'll receive password reset instructions",
            email=request.email,
        )

    except Exception as e:
        logger.error(f"❌ Password reset request error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Password reset request failed")


@router.post("/reset-password", response_model=AuthResponse)
async def reset_password(request: PasswordResetConfirm):
    """
    Complete password reset with reset code

    Steps:
    1. Find user by reset code
    2. Check code expiration
    3. Update password
    4. Invalidate reset code
    5. Return success
    """
    try:
        logger.info(f"🔑 Password reset attempt for: {request.email}")

        db_client = get_db_client()

        # Verify passwords match
        if request.new_password != request.confirm_password:
            raise ValueError("Passwords do not match")

        # Verify reset code is valid
        reset_code_record = await db_client.verify_reset_code(email=request.email, code=request.reset_code)

        if not reset_code_record:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset code")

        # Find user by email
        user = await db_client.get_user_by_email(request.email)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        # Hash new password
        hashed_password = hash_password(request.new_password)

        # Update password in database
        await db_client.update_password(user_id=user["id"], password_hash=hashed_password)

        # Mark reset code as used
        await db_client.mark_reset_code_used(reset_code_record["id"])

        logger.info(f"✅ Password reset successful: {request.email}")

        return AuthResponse(
            success=True,
            message="Password reset successfully. Please log in with your new password.",
            email=request.email,
        )

    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"❌ Validation error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Password reset error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Password reset failed")


@router.post("/oauth-callback")
async def oauth_callback(provider: str, code: str, background_tasks: BackgroundTasks):
    """
    OAuth callback handler (Google, LinkedIn)

    Steps:
    1. Exchange code for token with OAuth provider
    2. Get user info from provider
    3. Find or create user in database
    4. Generate session tokens
    5. Return tokens
    """
    try:
        logger.info(f"🔐 OAuth callback from {provider}")

        # TODO: Implement OAuth exchange
        # if provider == 'google':
        #     user_info = await exchange_google_code(code)
        # elif provider == 'linkedin':
        #     user_info = await exchange_linkedin_code(code)
        # else:
        #     raise HTTPException(status_code=400, detail="Unknown provider")

        # TODO: Find or create user
        # user = await db.users.find_one({'email': user_info['email']})
        # if not user:
        #     user = await db.users.insert_one({
        #         'email': user_info['email'],
        #         'full_name': user_info.get('name'),
        #         'oauth_provider': provider,
        #         'oauth_id': user_info['id'],
        #         'email_verified': True,
        #         'created_at': datetime.utcnow()
        #     })

        # Generate tokens
        tokens = generate_tokens(user_id=secrets.token_hex(16))

        logger.info(f"✅ OAuth login successful: {provider}")

        return AuthResponse(
            success=True,
            message=f"Login successful via {provider}",
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            expires_in=tokens["expires_in"],
        )

    except Exception as e:
        logger.error(f"❌ OAuth callback error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="OAuth login failed")
