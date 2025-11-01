"""
Supabase Database Client
Handles all database operations for users, verification codes, and password resets
"""

from supabase import create_client, Client
from app.core.config import settings
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from loguru import logger
import json


_supabase_client_instance = None


class SupabaseClient:
    """Supabase database client for NEXT Career Intelligence"""

    def __new__(cls):
        global _supabase_client_instance
        if _supabase_client_instance is None:
            _supabase_client_instance = super(SupabaseClient, cls).__new__(cls)
            _supabase_client_instance._initialized = False
        return _supabase_client_instance

    def __init__(self):
        """Initialize Supabase client"""
        if self._initialized:
            return
        try:
            if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
                raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")

            self.client: Client = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_SERVICE_KEY
            )
            logger.info("✅ Supabase client initialized")
            self._initialized = True
        except Exception as e:
            logger.error(f"❌ Failed to initialize Supabase client: {str(e)}")
            # Do not raise here to allow app to start, but log critical error
            self.client = None
            self._initialized = False

    def get_client(self) -> Optional[Client]:
        """Returns the Supabase client if initialized, otherwise None."""
        if not self._initialized or self.client is None:
            logger.warning("Supabase client not initialized. Trying to re-initialize.")
            self.__init__() # Attempt to re-initialize
        return self.client

    # ==================== USER OPERATIONS ====================
    
    async def create_user(self, 
                         email: str, 
                         full_name: str, 
                         password_hash: str,
                         is_verified: bool = False) -> Dict[str, Any]:
        """
        Create a new user record
        
        Args:
            email: User's email address
            full_name: User's full name
            password_hash: Hashed password
            is_verified: Whether email is pre-verified
            
        Returns:
            Created user record with user_id
            
        Raises:
            Exception if user already exists or database error
        """
        try:
            data = {
                "email": email,
                "full_name": full_name,
                "password_hash": password_hash,
                "is_verified": is_verified,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "last_login": None,
                "profile_complete": False
            }
            
            response = self.client.table("users").insert(data).execute()
            
            if response.data:
                logger.info(f"✅ User created: {email} (ID: {response.data[0]['id']})")
                return response.data[0]
            else:
                raise Exception("No data returned from insert")
                
        except Exception as e:
            if "duplicate key" in str(e).lower() or "unique" in str(e).lower():
                logger.warning(f"⚠️ User already exists: {email}")
                raise Exception(f"Email already registered: {email}")
            logger.error(f"❌ Error creating user: {str(e)}")
            raise
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve user by email
        
        Args:
            email: User's email address
            
        Returns:
            User record or None if not found
        """
        try:
            response = self.client.table("users").select("*").eq("email", email).execute()
            
            if response.data and len(response.data) > 0:
                logger.info(f"✅ User found: {email}")
                return response.data[0]
            else:
                logger.info(f"ℹ️ User not found: {email}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error fetching user: {str(e)}")
            raise
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve user by ID
        
        Args:
            user_id: User's unique ID
            
        Returns:
            User record or None if not found
        """
        try:
            response = self.client.table("users").select("*").eq("id", user_id).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            else:
                logger.warning(f"⚠️ User not found with ID: {user_id}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error fetching user by ID: {str(e)}")
            raise
    
    async def update_user(self, user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update user record
        
        Args:
            user_id: User's unique ID
            updates: Dictionary of fields to update
            
        Returns:
            Updated user record
        """
        try:
            updates["updated_at"] = datetime.utcnow().isoformat()
            
            response = self.client.table("users").update(updates).eq("id", user_id).execute()
            
            if response.data:
                logger.info(f"✅ User updated: {user_id}")
                return response.data[0]
            else:
                raise Exception("No data returned from update")
                
        except Exception as e:
            logger.error(f"❌ Error updating user: {str(e)}")
            raise
    
    async def verify_email(self, user_id: str) -> bool:
        """
        Mark user's email as verified
        
        Args:
            user_id: User's unique ID
            
        Returns:
            True if successful
        """
        try:
            response = self.client.table("users").update({
                "is_verified": True,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", user_id).execute()
            
            if response.data:
                logger.info(f"✅ Email verified for user: {user_id}")
                return True
            else:
                raise Exception("No data returned from update")
                
        except Exception as e:
            logger.error(f"❌ Error verifying email: {str(e)}")
            raise
    
    async def update_password(self, user_id: str, password_hash: str) -> bool:
        """
        Update user's password hash
        
        Args:
            user_id: User's unique ID
            password_hash: New hashed password
            
        Returns:
            True if successful
        """
        try:
            response = self.client.table("users").update({
                "password_hash": password_hash,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", user_id).execute()
            
            if response.data:
                logger.info(f"✅ Password updated for user: {user_id}")
                return True
            else:
                raise Exception("No data returned from update")
                
        except Exception as e:
            logger.error(f"❌ Error updating password: {str(e)}")
            raise
    
    # ==================== VERIFICATION CODE OPERATIONS ====================
    
    async def create_verification_code(self, 
                                      user_id: str, 
                                      email: str, 
                                      code: str) -> Dict[str, Any]:
        """
        Create verification code record
        
        Args:
            user_id: User's unique ID
            email: User's email
            code: 6-digit verification code
            
        Returns:
            Created verification code record
        """
        try:
            data = {
                "user_id": user_id,
                "email": email,
                "code": code,
                "is_used": False,
                "created_at": datetime.utcnow().isoformat(),
                "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat()
            }
            
            response = self.client.table("verification_codes").insert(data).execute()
            
            if response.data:
                logger.info(f"✅ Verification code created for user: {user_id}")
                return response.data[0]
            else:
                raise Exception("No data returned from insert")
                
        except Exception as e:
            logger.error(f"❌ Error creating verification code: {str(e)}")
            raise
    
    async def verify_code(self, email: str, code: str) -> Optional[Dict[str, Any]]:
        """
        Verify email verification code
        
        Args:
            email: User's email
            code: Verification code to check
            
        Returns:
            Verification record if valid, None otherwise
        """
        try:
            response = self.client.table("verification_codes").select("*").eq(
                "email", email
            ).eq("code", code).eq("is_used", False).execute()
            
            if response.data and len(response.data) > 0:
                record = response.data[0]
                
                # Check if code expired
                expires_at = datetime.fromisoformat(record['expires_at'])
                if datetime.utcnow() > expires_at:
                    logger.warning(f"⚠️ Verification code expired for: {email}")
                    return None
                
                logger.info(f"✅ Verification code valid for: {email}")
                return record
            else:
                logger.warning(f"⚠️ No valid verification code found for: {email}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error verifying code: {str(e)}")
            raise
    
    async def mark_code_used(self, code_id: str) -> bool:
        """
        Mark verification code as used
        
        Args:
            code_id: ID of verification code record
            
        Returns:
            True if successful
        """
        try:
            response = self.client.table("verification_codes").update({
                "is_used": True
            }).eq("id", code_id).execute()
            
            if response.data:
                logger.info(f"✅ Verification code marked as used: {code_id}")
                return True
            else:
                raise Exception("No data returned from update")
                
        except Exception as e:
            logger.error(f"❌ Error marking code as used: {str(e)}")
            raise
    
    # ==================== PASSWORD RESET OPERATIONS ====================
    
    async def create_reset_code(self, 
                               user_id: str, 
                               email: str, 
                               code: str) -> Dict[str, Any]:
        """
        Create password reset code
        
        Args:
            user_id: User's unique ID
            email: User's email
            code: Secure reset code
            
        Returns:
            Created reset code record
        """
        try:
            data = {
                "user_id": user_id,
                "email": email,
                "code": code,
                "is_used": False,
                "created_at": datetime.utcnow().isoformat(),
                "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat()
            }
            
            response = self.client.table("password_resets").insert(data).execute()
            
            if response.data:
                logger.info(f"✅ Password reset code created for user: {user_id}")
                return response.data[0]
            else:
                raise Exception("No data returned from insert")
                
        except Exception as e:
            logger.error(f"❌ Error creating reset code: {str(e)}")
            raise
    
    async def verify_reset_code(self, email: str, code: str) -> Optional[Dict[str, Any]]:
        """
        Verify password reset code
        
        Args:
            email: User's email
            code: Reset code to verify
            
        Returns:
            Reset code record if valid, None otherwise
        """
        try:
            response = self.client.table("password_resets").select("*").eq(
                "email", email
            ).eq("code", code).eq("is_used", False).execute()
            
            if response.data and len(response.data) > 0:
                record = response.data[0]
                
                # Check if code expired
                expires_at = datetime.fromisoformat(record['expires_at'])
                if datetime.utcnow() > expires_at:
                    logger.warning(f"⚠️ Password reset code expired for: {email}")
                    return None
                
                logger.info(f"✅ Password reset code valid for: {email}")
                return record
            else:
                logger.warning(f"⚠️ No valid password reset code found for: {email}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error verifying reset code: {str(e)}")
            raise
    
    async def mark_reset_code_used(self, code_id: str) -> bool:
        """
        Mark password reset code as used
        
        Args:
            code_id: ID of password reset record
            
        Returns:
            True if successful
        """
        try:
            response = self.client.table("password_resets").update({
                "is_used": True
            }).eq("id", code_id).execute()
            
            if response.data:
                logger.info(f"✅ Password reset code marked as used: {code_id}")
                return True
            else:
                raise Exception("No data returned from update")
                
        except Exception as e:
            logger.error(f"❌ Error marking reset code as used: {str(e)}")
            raise
    
    # ==================== ONBOARDING OPERATIONS ====================
    
    async def save_onboarding_data(self, 
                                   user_id: str, 
                                   onboarding_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save or update user onboarding data
        
        Args:
            user_id: User's unique ID
            onboarding_data: Complete onboarding information
            
        Returns:
            Saved onboarding record
        """
        try:
            data = {
                "user_id": user_id,
                "current_role": onboarding_data.get("current_role"),
                "industry": onboarding_data.get("industry"),
                "years_experience": onboarding_data.get("years_experience"),
                "skills": onboarding_data.get("skills", []),
                "goals": onboarding_data.get("goals", []),
                "learning_style": onboarding_data.get("learning_style"),
                "is_complete": True,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Try to update first (if record exists)
            response = self.client.table("onboarding").update(data).eq(
                "user_id", user_id
            ).execute()
            
            # If no records updated, insert new
            if not response.data:
                response = self.client.table("onboarding").insert(data).execute()
            
            if response.data:
                logger.info(f"✅ Onboarding data saved for user: {user_id}")
                return response.data[0]
            else:
                raise Exception("No data returned from operation")
                
        except Exception as e:
            logger.error(f"❌ Error saving onboarding data: {str(e)}")
            raise
    
    async def get_onboarding_progress(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user's onboarding progress
        
        Args:
            user_id: User's unique ID
            
        Returns:
            Onboarding progress record or None if not found
        """
        try:
            response = self.client.table("onboarding").select("*").eq(
                "user_id", user_id
            ).execute()
            
            if response.data and len(response.data) > 0:
                logger.info(f"✅ Onboarding progress retrieved for user: {user_id}")
                return response.data[0]
            else:
                logger.info(f"ℹ️ No onboarding data found for user: {user_id}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error retrieving onboarding progress: {str(e)}")
            raise


# Create singleton instance
db_client = None


def get_db_client() -> SupabaseClient:
    """
    Get or create Supabase client instance
    
    Returns:
        SupabaseClient instance
    """
    global db_client
    if db_client is None:
        db_client = SupabaseClient()
    return db_client
