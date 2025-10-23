-- Migration 008: Add firebase_uid column to users table
-- Purpose: Add Firebase authentication support
-- Run this after migration 001

-- Add firebase_uid column
ALTER TABLE public.users 
ADD COLUMN IF NOT EXISTS firebase_uid VARCHAR(255) UNIQUE;

-- Create index for performance
CREATE INDEX IF NOT EXISTS idx_users_firebase_uid ON public.users(firebase_uid);

-- Update existing users to have a placeholder firebase_uid (if any exist)
-- You'll need to update these manually or through your application
UPDATE public.users 
SET firebase_uid = 'legacy_' || id::text 
WHERE firebase_uid IS NULL;

-- Now make it NOT NULL after setting default values
ALTER TABLE public.users 
ALTER COLUMN firebase_uid SET NOT NULL;

-- Add comment for documentation
COMMENT ON COLUMN public.users.firebase_uid IS 'Firebase Authentication UID - unique identifier from Firebase Auth';
