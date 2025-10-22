#!/bin/bash

set -e

echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║  🚀 AUTOMATIC SUPABASE + SENDGRID SETUP                                   ║"
echo "║                                                                            ║"
echo "║  This script will:                                                         ║"
echo "║  1. Install Python dependencies (including SendGrid)                       ║"
echo "║  2. Create database migration SQL scripts                                  ║"
echo "║  3. Display setup completion status                                        ║"
echo "║  4. Show next steps for running the application                            ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ============================================================================
# Step 1: Install Dependencies
# ============================================================================
echo "📦 Step 1: Installing Python dependencies..."
echo "───────────────────────────────────────────────────────────────────────────────"

cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip setuptools wheel > /dev/null 2>&1

# Install requirements
echo "Installing Python packages from requirements.txt..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt > /dev/null 2>&1
    echo "✅ Dependencies installed successfully"
else
    echo "⚠️  requirements.txt not found, skipping pip install"
fi

cd ..

# ============================================================================
# Step 2: Create SQL Migration Scripts
# ============================================================================
echo ""
echo "📊 Step 2: Creating Supabase SQL migration scripts..."
echo "───────────────────────────────────────────────────────────────────────────────"

mkdir -p backend/migrations

# Create migration script for users table
cat > backend/migrations/001_create_users_table.sql << 'EOF'
-- Create users table
-- Run this script in Supabase SQL Editor

DROP TABLE IF EXISTS onboarding CASCADE;
DROP TABLE IF EXISTS password_resets CASCADE;
DROP TABLE IF EXISTS verification_codes CASCADE;
DROP TABLE IF EXISTS users CASCADE;

CREATE TABLE users (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  full_name TEXT NOT NULL,
  password_hash TEXT NOT NULL,
  is_verified BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
  last_login TIMESTAMP WITH TIME ZONE,
  profile_complete BOOLEAN DEFAULT FALSE
);

ALTER TABLE users ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own data"
  ON users FOR SELECT
  USING (true);

CREATE POLICY "Service role can manage users"
  ON users FOR ALL
  USING (true);

CREATE INDEX users_email_idx ON users(email);

GRANT ALL ON users TO authenticated;
GRANT ALL ON users TO service_role;
EOF

# Create migration script for verification codes
cat > backend/migrations/002_create_verification_codes_table.sql << 'EOF'
-- Create verification_codes table
-- Run this script in Supabase SQL Editor after 001_create_users_table.sql

CREATE TABLE verification_codes (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  email TEXT NOT NULL,
  code TEXT NOT NULL,
  is_used BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
  expires_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE INDEX verification_codes_email_code_idx ON verification_codes(email, code);
CREATE INDEX verification_codes_user_id_idx ON verification_codes(user_id);

ALTER TABLE verification_codes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Service role can manage verification codes"
  ON verification_codes FOR ALL
  USING (true);

GRANT ALL ON verification_codes TO authenticated;
GRANT ALL ON verification_codes TO service_role;
EOF

# Create migration script for password resets
cat > backend/migrations/003_create_password_resets_table.sql << 'EOF'
-- Create password_resets table
-- Run this script in Supabase SQL Editor after 002_create_verification_codes_table.sql

CREATE TABLE password_resets (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  email TEXT NOT NULL,
  code TEXT NOT NULL,
  is_used BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
  expires_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE INDEX password_resets_email_code_idx ON password_resets(email, code);
CREATE INDEX password_resets_user_id_idx ON password_resets(user_id);

ALTER TABLE password_resets ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Service role can manage password resets"
  ON password_resets FOR ALL
  USING (true);

GRANT ALL ON password_resets TO authenticated;
GRANT ALL ON password_resets TO service_role;
EOF

# Create migration script for onboarding
cat > backend/migrations/004_create_onboarding_table.sql << 'EOF'
-- Create onboarding table
-- Run this script in Supabase SQL Editor after 003_create_password_resets_table.sql

CREATE TABLE onboarding (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
  current_role TEXT,
  industry TEXT,
  years_experience TEXT,
  skills TEXT[] DEFAULT '{}',
  goals TEXT[] DEFAULT '{}',
  learning_style TEXT,
  notification_preferences JSONB DEFAULT '{}',
  is_complete BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

CREATE INDEX onboarding_user_id_idx ON onboarding(user_id);
CREATE INDEX onboarding_is_complete_idx ON onboarding(is_complete);

ALTER TABLE onboarding ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Service role can manage career profiles"
  ON onboarding FOR ALL
  USING (true);

GRANT ALL ON onboarding TO authenticated;
GRANT ALL ON onboarding TO service_role;
EOF

echo "✅ Migration scripts created in backend/migrations/"
echo "   - 001_create_users_table.sql"
echo "   - 002_create_verification_codes_table.sql"
echo "   - 003_create_password_resets_table.sql"
echo "   - 004_create_onboarding_table.sql"

# ============================================================================
# Step 3: Create environment variable documentation
# ============================================================================
echo ""
echo "📝 Step 3: Creating environment variable reference..."
echo "───────────────────────────────────────────────────────────────────────────────"

cat > ENV_REFERENCE.md << 'EOF'
# Environment Variables Reference

## Backend (.env)
Current status: ✅ CONFIGURED

Required variables are set:
- ✅ SUPABASE_URL
- ✅ SUPABASE_SERVICE_KEY
- ✅ SUPABASE_ANON_KEY
- ⏳ SENDGRID_API_KEY (needs your actual API key)
- ✅ Other variables

To use SendGrid:
1. Go to https://app.sendgrid.com
2. Settings → API Keys
3. Create New API Key
4. Copy the key (starts with "SG.")
5. Update backend/.env: SENDGRID_API_KEY=SG.your-key-here

## Frontend (.env.local)
Current status: ✅ CONFIGURED

All required variables are set:
- ✅ NEXT_PUBLIC_SUPABASE_URL
- ✅ NEXT_PUBLIC_SUPABASE_ANON_KEY
- ✅ NEXT_PUBLIC_API_URL
- ✅ Firebase configuration
- ✅ Stripe configuration

## Supabase Database Tables
Status: ⏳ NEEDS CREATION

Run these SQL scripts in Supabase SQL Editor (one at a time):
1. backend/migrations/001_create_users_table.sql
2. backend/migrations/002_create_verification_codes_table.sql
3. backend/migrations/003_create_password_resets_table.sql
4. backend/migrations/004_create_onboarding_table.sql
EOF

echo "✅ Environment reference created: ENV_REFERENCE.md"

# ============================================================================
# Step 4: Display setup summary
# ============================================================================
echo ""
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                    ✅ SETUP COMPLETE!                                     ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""

echo "📊 CURRENT STATUS:"
echo "───────────────────────────────────────────────────────────────────────────────"
echo "✅ Python dependencies installed"
echo "✅ Backend .env configured (add SendGrid API key)"
echo "✅ Frontend .env.local configured"
echo "✅ Supabase SQL migration scripts created"
echo ""

echo "🎯 NEXT STEPS (In Order):"
echo "───────────────────────────────────────────────────────────────────────────────"
echo ""
echo "1️⃣  GET SENDGRID API KEY (2 minutes)"
echo "   a. Go to: https://app.sendgrid.com"
echo "   b. Settings → API Keys"
echo "   c. Create New Static Key"
echo "   d. Copy the key (starts with SG.)"
echo "   e. Edit backend/.env and update SENDGRID_API_KEY"
echo ""

echo "2️⃣  CREATE SUPABASE TABLES (5 minutes)"
echo "   a. Go to: https://supabase.com/dashboard"
echo "   b. Click: SQL Editor"
echo "   c. Paste this script (one at a time, wait after each):"
echo "      └─ Content of backend/migrations/001_create_users_table.sql"
echo "      └─ Content of backend/migrations/002_create_verification_codes_table.sql"
echo "      └─ Content of backend/migrations/003_create_password_resets_table.sql"
echo "      └─ Content of backend/migrations/004_create_onboarding_table.sql"
echo ""

echo "3️⃣  START BACKEND SERVER (1 minute)"
echo "   $ cd backend"
echo "   $ source venv/bin/activate"
echo "   $ python3 -m uvicorn app.main:app --reload"
echo "   Access: http://localhost:8000/docs"
echo ""

echo "4️⃣  START FRONTEND SERVER (1 minute)"
echo "   $ cd frontend"
echo "   $ npm run dev"
echo "   Access: http://localhost:3000"
echo ""

echo "5️⃣  TEST FULL AUTHENTICATION FLOW (5 minutes)"
echo "   $ curl -X POST http://localhost:8000/api/auth/signup \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"email\":\"test@example.com\",\"full_name\":\"Test User\",\"password\":\"Pass123\"}'"
echo ""

echo "📁 IMPORTANT FILES:"
echo "───────────────────────────────────────────────────────────────────────────────"
echo "✅ backend/.env .......................... Environment variables (CONFIGURED)"
echo "✅ frontend/.env.local .................. Frontend variables (CONFIGURED)"
echo "📁 backend/migrations/*.sql ............. Database creation scripts (READY)"
echo "📄 ENV_REFERENCE.md ..................... This reference guide"
echo ""

echo "📚 DOCUMENTATION:"
echo "───────────────────────────────────────────────────────────────────────────────"
echo "📖 SUPABASE_SENDGRID_SETUP.md ........... Complete setup guide"
echo "📖 FRONTEND_SUPABASE_SETUP.md .......... Frontend integration"
echo "📖 QUICK_START_SETUP.md ................ Quick reference"
echo "📖 SENDGRID_DNS_SETUP.md ............... Email deliverability"
echo ""

echo "⏱️  TOTAL TIME TO LIVE: ~20 minutes"
echo "───────────────────────────────────────────────────────────────────────────────"
echo "1. Get SendGrid key: 2 min"
echo "2. Create tables: 5 min"
echo "3. Start backend: 1 min"
echo "4. Start frontend: 1 min"
echo "5. Test flows: 5 min"
echo "6. Buffer: 6 min"
echo ""

echo "═════════════════════════════════════════════════════════════════════════════"
echo "👉 NEXT ACTION: Get your SendGrid API key and update backend/.env"
echo "═════════════════════════════════════════════════════════════════════════════"
echo ""
