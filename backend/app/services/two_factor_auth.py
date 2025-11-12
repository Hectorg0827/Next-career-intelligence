"""
Two-Factor Authentication (2FA) Service
Implements TOTP (Time-based One-Time Password) authentication

Features:
- QR code generation for authenticator apps
- TOTP verification
- Backup codes generation
- 2FA recovery flow
"""

import pyotp
import qrcode
import io
import base64
from typing import List, Tuple, Optional
from loguru import logger
from datetime import datetime
import secrets
import hashlib


class TwoFactorAuthService:
    """Handle 2FA setup, verification, and recovery"""

    @staticmethod
    def generate_secret() -> str:
        """
        Generate a random secret for TOTP

        Returns:
            Base32-encoded secret (e.g., 'JBSWY3DPEHPK3PXP')
        """
        return pyotp.random_base32()

    @staticmethod
    def generate_qr_code(secret: str, user_email: str, issuer_name: str = "NEXT Career Intelligence") -> str:
        """
        Generate QR code for TOTP secret

        Args:
            secret: Base32-encoded TOTP secret
            user_email: User's email address
            issuer_name: App name shown in authenticator

        Returns:
            Base64-encoded PNG image data URL

        Usage in frontend:
            <img src={qr_code_data_url} alt="Scan this QR code" />
        """
        try:
            # Create TOTP URI
            totp = pyotp.TOTP(secret)
            provisioning_uri = totp.provisioning_uri(name=user_email, issuer_name=issuer_name)

            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(provisioning_uri)
            qr.make(fit=True)

            # Create image
            img = qr.make_image(fill_color="black", back_color="white")

            # Convert to base64 data URL
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            img_str = base64.b64encode(buffer.getvalue()).decode()
            data_url = f"data:image/png;base64,{img_str}"

            return data_url

        except Exception as e:
            logger.error(f"Error generating QR code: {e}")
            raise

    @staticmethod
    def verify_totp(secret: str, token: str, window: int = 1) -> bool:
        """
        Verify TOTP token

        Args:
            secret: User's TOTP secret
            token: 6-digit code from authenticator app
            window: Number of time windows to check (default: 1)
                    window=1 allows ±30 seconds drift

        Returns:
            True if token is valid

        Example:
            valid = TwoFactorAuthService.verify_totp(
                secret="JBSWY3DPEHPK3PXP",
                token="123456"
            )
        """
        try:
            totp = pyotp.TOTP(secret)
            is_valid = totp.verify(token, valid_window=window)

            if is_valid:
                logger.info(f"✅ 2FA token verified successfully")
            else:
                logger.warning(f"⚠️ 2FA token verification failed")

            return is_valid

        except Exception as e:
            logger.error(f"Error verifying TOTP: {e}")
            return False

    @staticmethod
    def generate_backup_codes(count: int = 10) -> List[str]:
        """
        Generate backup recovery codes

        Args:
            count: Number of backup codes to generate (default: 10)

        Returns:
            List of 8-character alphanumeric codes

        Example:
            ['A1B2C3D4', 'E5F6G7H8', ...]
        """
        backup_codes = []
        for _ in range(count):
            # Generate 4 random bytes = 8 hex characters
            code = secrets.token_hex(4).upper()
            backup_codes.append(code)

        return backup_codes

    @staticmethod
    def hash_backup_code(code: str) -> str:
        """
        Hash backup code before storing in database

        Args:
            code: Plain text backup code

        Returns:
            SHA-256 hash of the code

        Note: Store hashed codes in DB, never plain text
        """
        return hashlib.sha256(code.encode()).hexdigest()

    @staticmethod
    def verify_backup_code(code: str, hashed_code: str) -> bool:
        """
        Verify backup code against stored hash

        Args:
            code: User-provided backup code
            hashed_code: Stored hash from database

        Returns:
            True if code matches
        """
        code_hash = TwoFactorAuthService.hash_backup_code(code)
        return code_hash == hashed_code

    @staticmethod
    def format_secret_for_manual_entry(secret: str) -> str:
        """
        Format secret for manual entry in authenticator app

        Args:
            secret: Base32-encoded secret

        Returns:
            Formatted secret (e.g., 'JBSW Y3DP EHPK 3PXP')

        Usage:
            "Can't scan QR code? Enter this manually: JBSW Y3DP EHPK 3PXP"
        """
        # Insert space every 4 characters
        return " ".join([secret[i : i + 4] for i in range(0, len(secret), 4)])

    @staticmethod
    def get_current_totp(secret: str) -> str:
        """
        Get current TOTP token (for testing only!)

        Args:
            secret: TOTP secret

        Returns:
            Current 6-digit TOTP token

        WARNING: Only use for testing/debugging. Never expose in production API.
        """
        totp = pyotp.TOTP(secret)
        return totp.now()


# Singleton instance
_tfa_service = None


def get_tfa_service() -> TwoFactorAuthService:
    """Get or create 2FA service instance"""
    global _tfa_service
    if _tfa_service is None:
        _tfa_service = TwoFactorAuthService()
    return _tfa_service
