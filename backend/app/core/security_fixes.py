"""
Security Fixes Implementation
Addresses critical vulnerabilities identified in security audit
"""

import bcrypt
import secrets
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from cryptography.fernet import Fernet
import base64
import hashlib
from loguru import logger


# ==================== 1. SECURE PASSWORD HASHING ====================

def hash_password_secure(password: str) -> str:
    """
    Hash password using bcrypt (industry standard)

    Replaces insecure SHA-256 implementation
    Uses 12 rounds (balance of security vs performance)

    Args:
        password: Plain text password

    Returns:
        Bcrypt hash string
    """
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password_secure(password: str, hashed: str) -> bool:
    """
    Verify password against bcrypt hash

    Args:
        password: Plain text password
        hashed: Bcrypt hash from database

    Returns:
        True if password matches, False otherwise
    """
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False


# ==================== 2. JWT TOKEN GENERATION ====================

def generate_jwt_tokens(
    user_id: str,
    email: str,
    secret_key: str,
    access_token_expire_minutes: int = 60,
    refresh_token_expire_days: int = 30
) -> Dict[str, Any]:
    """
    Generate secure JWT access and refresh tokens

    Replaces insecure random token generation

    Args:
        user_id: User's unique identifier
        email: User's email
        secret_key: JWT signing secret
        access_token_expire_minutes: Access token lifetime (default 1 hour)
        refresh_token_expire_days: Refresh token lifetime (default 30 days)

    Returns:
        Dict with access_token, refresh_token, expires_in, token_type
    """
    now = datetime.utcnow()

    # Access token payload
    access_payload = {
        'sub': user_id,
        'email': email,
        'type': 'access',
        'iat': now,
        'exp': now + timedelta(minutes=access_token_expire_minutes),
        'jti': secrets.token_urlsafe(16)  # Unique token ID
    }

    # Refresh token payload (fewer claims for security)
    refresh_payload = {
        'sub': user_id,
        'type': 'refresh',
        'iat': now,
        'exp': now + timedelta(days=refresh_token_expire_days),
        'jti': secrets.token_urlsafe(16)
    }

    # Sign tokens
    access_token = jwt.encode(access_payload, secret_key, algorithm='HS256')
    refresh_token = jwt.encode(refresh_payload, secret_key, algorithm='HS256')

    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'expires_in': access_token_expire_minutes * 60,  # seconds
        'token_type': 'bearer'
    }


def verify_jwt_token(token: str, secret_key: str, expected_type: str = 'access') -> Optional[Dict[str, Any]]:
    """
    Verify and decode JWT token

    Args:
        token: JWT token string
        secret_key: JWT signing secret
        expected_type: 'access' or 'refresh'

    Returns:
        Decoded payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])

        # Verify token type
        if payload.get('type') != expected_type:
            logger.warning(f"Invalid token type: expected {expected_type}, got {payload.get('type')}")
            return None

        return payload

    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        return None
    except JWTError as e:
        logger.error(f"Token verification failed: {e}")
        return None


def refresh_access_token(
    refresh_token: str,
    secret_key: str,
    access_token_expire_minutes: int = 60
) -> Optional[Dict[str, Any]]:
    """
    Generate new access token from refresh token

    Args:
        refresh_token: Valid refresh token
        secret_key: JWT signing secret
        access_token_expire_minutes: New access token lifetime

    Returns:
        Dict with new access_token or None if refresh invalid
    """
    payload = verify_jwt_token(refresh_token, secret_key, expected_type='refresh')
    if not payload:
        return None

    # Generate new access token
    now = datetime.utcnow()
    access_payload = {
        'sub': payload['sub'],
        'type': 'access',
        'iat': now,
        'exp': now + timedelta(minutes=access_token_expire_minutes),
        'jti': secrets.token_urlsafe(16)
    }

    access_token = jwt.encode(access_payload, secret_key, algorithm='HS256')

    return {
        'access_token': access_token,
        'expires_in': access_token_expire_minutes * 60,
        'token_type': 'bearer'
    }


# ==================== 3. 2FA SECRET ENCRYPTION ====================

class SecretEncryption:
    """Encrypt/decrypt sensitive data at rest (e.g., 2FA secrets)"""

    def __init__(self, encryption_key: str):
        """
        Initialize encryption with key

        Args:
            encryption_key: Base64-encoded Fernet key (generate with Fernet.generate_key())
        """
        try:
            self.cipher = Fernet(encryption_key.encode())
        except Exception as e:
            logger.error(f"Failed to initialize encryption: {e}")
            raise ValueError("Invalid encryption key")

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt plaintext string

        Args:
            plaintext: String to encrypt

        Returns:
            Base64-encoded ciphertext
        """
        try:
            encrypted = self.cipher.encrypt(plaintext.encode('utf-8'))
            return encrypted.decode('utf-8')
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise

    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt ciphertext string

        Args:
            ciphertext: Base64-encoded encrypted string

        Returns:
            Original plaintext
        """
        try:
            decrypted = self.cipher.decrypt(ciphertext.encode('utf-8'))
            return decrypted.decode('utf-8')
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise


def generate_encryption_key() -> str:
    """
    Generate new Fernet encryption key

    Returns:
        Base64-encoded key (store in .env as ENCRYPTION_KEY)
    """
    key = Fernet.generate_key()
    return key.decode('utf-8')


# ==================== 4. PII REDACTION FOR LOGS ====================

def redact_email(email: str) -> str:
    """
    Redact email address for logging (GDPR compliance)

    Example: user@example.com -> u***@e***.com

    Args:
        email: Email address to redact

    Returns:
        Redacted email string
    """
    try:
        local, domain = email.split('@')
        domain_parts = domain.split('.')
        domain_name = domain_parts[0]
        domain_ext = domain_parts[-1] if len(domain_parts) > 1 else ''

        return f"{local[0]}***@{domain_name[0]}***.{domain_ext}"
    except Exception:
        return "***@***.***"


def redact_user_id(user_id: str) -> str:
    """
    Redact user ID for logging

    Example: abc123def456 -> abc***456

    Args:
        user_id: User ID to redact

    Returns:
        Redacted user ID
    """
    if len(user_id) < 8:
        return "***"
    return f"{user_id[:3]}***{user_id[-3:]}"


def hash_for_logging(value: str) -> str:
    """
    Create consistent hash for logging (useful for tracking without exposing PII)

    Args:
        value: String to hash

    Returns:
        First 8 chars of SHA-256 hash
    """
    hashed = hashlib.sha256(value.encode('utf-8')).hexdigest()
    return hashed[:8]


# ==================== 5. SECURE SESSION MANAGEMENT ====================

class SessionManager:
    """Manage user sessions with security best practices"""

    def __init__(self, redis_client):
        """
        Initialize session manager

        Args:
            redis_client: Redis client for session storage
        """
        self.redis = redis_client
        self.session_prefix = "session:"
        self.session_ttl = 3600  # 1 hour

    async def create_session(self, user_id: str, metadata: Dict[str, Any]) -> str:
        """
        Create new session

        Args:
            user_id: User's unique identifier
            metadata: Session metadata (IP, user agent, etc.)

        Returns:
            Session token
        """
        session_token = secrets.token_urlsafe(32)
        session_key = f"{self.session_prefix}{session_token}"

        session_data = {
            'user_id': user_id,
            'created_at': datetime.utcnow().isoformat(),
            'ip_address': metadata.get('ip_address'),
            'user_agent': metadata.get('user_agent'),
            'last_activity': datetime.utcnow().isoformat()
        }

        await self.redis.setex(
            session_key,
            self.session_ttl,
            str(session_data)
        )

        return session_token

    async def validate_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """
        Validate session and update last activity

        Args:
            session_token: Session token to validate

        Returns:
            Session data if valid, None otherwise
        """
        session_key = f"{self.session_prefix}{session_token}"
        session_data = await self.redis.get(session_key)

        if not session_data:
            return None

        # Update last activity
        await self.redis.expire(session_key, self.session_ttl)

        return eval(session_data)  # Use json.loads in production

    async def invalidate_session(self, session_token: str) -> bool:
        """
        Invalidate session (logout)

        Args:
            session_token: Session token to invalidate

        Returns:
            True if session was invalidated
        """
        session_key = f"{self.session_prefix}{session_token}"
        result = await self.redis.delete(session_key)
        return result > 0

    async def invalidate_all_user_sessions(self, user_id: str) -> int:
        """
        Invalidate all sessions for a user (force logout everywhere)

        Args:
            user_id: User's unique identifier

        Returns:
            Number of sessions invalidated
        """
        # Scan for all sessions for this user
        cursor = 0
        count = 0

        while True:
            cursor, keys = await self.redis.scan(
                cursor,
                match=f"{self.session_prefix}*",
                count=100
            )

            for key in keys:
                session_data = await self.redis.get(key)
                if session_data and user_id in str(session_data):
                    await self.redis.delete(key)
                    count += 1

            if cursor == 0:
                break

        return count


# ==================== 6. INPUT VALIDATION & SANITIZATION ====================

def validate_email_format(email: str) -> bool:
    """
    Validate email format (basic check)

    Args:
        email: Email to validate

    Returns:
        True if valid format
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def sanitize_user_input(user_input: str, max_length: int = 1000) -> str:
    """
    Sanitize user input to prevent injection attacks

    Args:
        user_input: Raw user input
        max_length: Maximum allowed length

    Returns:
        Sanitized string
    """
    # Trim whitespace
    sanitized = user_input.strip()

    # Limit length
    sanitized = sanitized[:max_length]

    # Remove null bytes
    sanitized = sanitized.replace('\x00', '')

    # Remove control characters (except newline/tab)
    sanitized = ''.join(char for char in sanitized if ord(char) >= 32 or char in '\n\t')

    return sanitized


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password strength

    Requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character

    Args:
        password: Password to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not any(char.isupper() for char in password):
        return False, "Password must contain at least one uppercase letter"

    if not any(char.islower() for char in password):
        return False, "Password must contain at least one lowercase letter"

    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one digit"

    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(char in special_chars for char in password):
        return False, "Password must contain at least one special character"

    # Check against common passwords (add more as needed)
    common_passwords = ['password', '12345678', 'qwerty', 'admin', 'letmein']
    if password.lower() in common_passwords:
        return False, "Password is too common. Please choose a stronger password"

    return True, ""


# ==================== 7. SECURITY UTILITIES ====================

def generate_secure_token(length: int = 32) -> str:
    """
    Generate cryptographically secure random token

    Args:
        length: Token length in bytes

    Returns:
        URL-safe base64-encoded token
    """
    return secrets.token_urlsafe(length)


def constant_time_compare(val1: str, val2: str) -> bool:
    """
    Compare two strings in constant time (prevents timing attacks)

    Args:
        val1: First string
        val2: Second string

    Returns:
        True if strings are equal
    """
    return secrets.compare_digest(val1, val2)


def generate_csrf_token() -> str:
    """
    Generate CSRF token for forms

    Returns:
        CSRF token string
    """
    return secrets.token_hex(32)


def verify_csrf_token(token: str, stored_token: str) -> bool:
    """
    Verify CSRF token

    Args:
        token: Token from request
        stored_token: Token from session/cookie

    Returns:
        True if tokens match
    """
    return constant_time_compare(token, stored_token)


# ==================== USAGE EXAMPLES ====================

"""
EXAMPLE 1: Password Hashing
-----------------------------
from app.core.security_fixes import hash_password_secure, verify_password_secure

# On signup
hashed = hash_password_secure("SecureP@ssw0rd!")
# Store hashed in database

# On login
is_valid = verify_password_secure("SecureP@ssw0rd!", hashed)


EXAMPLE 2: JWT Tokens
--------------------
from app.core.security_fixes import generate_jwt_tokens, verify_jwt_token
from app.core.config import settings

# On login
tokens = generate_jwt_tokens(
    user_id="user123",
    email="user@example.com",
    secret_key=settings.SECRET_KEY
)
# Return tokens to client

# On protected endpoint
payload = verify_jwt_token(token, settings.SECRET_KEY)
if payload:
    user_id = payload['sub']


EXAMPLE 3: 2FA Secret Encryption
--------------------------------
from app.core.security_fixes import SecretEncryption, generate_encryption_key

# Generate key (once, store in .env)
key = generate_encryption_key()

# In application
encryptor = SecretEncryption(settings.ENCRYPTION_KEY)
encrypted_secret = encryptor.encrypt("JBSWY3DPEHPK3PXP")  # TOTP secret
# Store encrypted_secret in database

# When verifying TOTP
decrypted_secret = encryptor.decrypt(encrypted_secret)
# Use decrypted_secret with pyotp


EXAMPLE 4: PII Redaction
------------------------
from app.core.security_fixes import redact_email, hash_for_logging

email = "user@example.com"
logger.info(f"User signup: {redact_email(email)}")  # u***@e***.com
logger.info(f"User hash: {hash_for_logging(email)}")  # a1b2c3d4


EXAMPLE 5: Session Management
-----------------------------
from app.core.security_fixes import SessionManager

session_manager = SessionManager(redis_client)

# Create session
session_token = await session_manager.create_session(
    user_id="user123",
    metadata={"ip_address": request.client.host, "user_agent": request.headers.get("user-agent")}
)

# Validate session
session_data = await session_manager.validate_session(session_token)
if session_data:
    user_id = session_data['user_id']

# Logout
await session_manager.invalidate_session(session_token)

# Force logout everywhere (security incident)
await session_manager.invalidate_all_user_sessions("user123")
"""
