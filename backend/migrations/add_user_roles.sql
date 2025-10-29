-- Migration to add role and subscription fields to users table
-- Run this on your Supabase database

-- Add new columns to users table
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS role VARCHAR(50) DEFAULT 'user' NOT NULL,
ADD COLUMN IF NOT EXISTS subscription_status VARCHAR(50) DEFAULT 'free',
ADD COLUMN IF NOT EXISTS free_reports_used FLOAT DEFAULT 0,
ADD COLUMN IF NOT EXISTS stripe_customer_id VARCHAR(255),
ADD COLUMN IF NOT EXISTS last_free_analysis_at TIMESTAMP;

-- Update existing users to have default values
UPDATE users 
SET 
    role = 'user',
    subscription_status = 'free',
    free_reports_used = 0
WHERE role IS NULL;

-- Create index for role lookups
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_subscription ON users(subscription_status);

-- Show results
SELECT id, email, name, role, subscription_status 
FROM users 
LIMIT 10;
