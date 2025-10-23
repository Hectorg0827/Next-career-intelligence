# 🚀 Database Migration Guide for NEXT Career Intelligence

## Overview
This guide will help you set up all database tables in Supabase for the full Career Co-pilot platform.

## Prerequisites
- Supabase account
- Access to project: `whxbxjpymksgvixudnjh`
- URL: https://whxbxjpymksgvixudnjh.supabase.co

## Migration Files (Run in Order)

### 1️⃣ **001_create_users_table.sql** - Core Users Table
**What it creates:**
- `users` table with authentication fields
- Firebase UID support
- OAuth provider columns (Google, Microsoft, GitHub)
- Email verification tracking
- Row Level Security (RLS) policies

**Run this first** - All other tables depend on this.

### 2️⃣ **002_create_verification_codes_table.sql** - Email Verification
**What it creates:**
- `verification_codes` table
- Supports email verification flow
- Time-based expiration

### 3️⃣ **003_create_password_resets_table.sql** - Password Reset
**What it creates:**
- `password_resets` table
- Secure token generation
- Expiration tracking

### 4️⃣ **004_create_onboarding_table.sql** - User Onboarding
**What it creates:**
- `onboarding_data` table
- Stores career goals, current role, desired skills
- Used for personalized recommendations

### 5️⃣ **005_add_subscription_fields.sql** - Subscription System ⭐
**What it creates:**
- Adds subscription fields to `users` table:
  - `subscription_status` (free/pro/enterprise)
  - `stripe_customer_id`
  - `stripe_subscription_id`
  - `free_reports_used` (limit 1 for free tier)
  - `last_free_analysis_at`

**Critical for:** Freemium model, AI Coach gating

### 6️⃣ **006_create_pro_features_tables.sql** - Pro Features 🎯
**What it creates:**
- `user_progress` - Track learning progress, skills, courses
- `coach_messages` - **AI Coach conversation history** 💬
- `cohorts` & `cohort_members` - Community groups
- `interview_sessions` & `interview_turns` - AI Interviewer data
- `portfolio_projects` - Project briefs and submissions

**Critical for:** AI Coach, AI Interviewer, Progress tracking

### 7️⃣ **007_create_marketplace_tables.sql** - Job Marketplace 🏢
**What it creates:**
- `companies` - Recruiter/company profiles
- `jobs` - Job listings with skills matching
- `user_job_applications` - Track applications
- `hiring_feedback` - Feedback loop from successful hires

**Critical for:** Job matching, marketplace features

---

## 📋 Step-by-Step Instructions

### Option A: Run in Supabase Dashboard (Recommended)

1. **Open Supabase Dashboard**
   ```
   https://supabase.com/dashboard/project/whxbxjpymksgvixudnjh
   ```

2. **Navigate to SQL Editor**
   - Click "SQL Editor" in left sidebar
   - Click "New Query"

3. **Run Each Migration**
   For each file (001 → 007):
   
   a. Open the migration file in VS Code
   b. Copy the entire SQL content
   c. Paste into Supabase SQL Editor
   d. Click "Run" button
   e. ✅ Check for success message (green checkmark)
   f. ❌ If error, read error message and fix before continuing
   
4. **Verify Tables Created**
   After running all migrations, verify:
   ```sql
   SELECT table_name 
   FROM information_schema.tables 
   WHERE table_schema = 'public' 
   ORDER BY table_name;
   ```
   
   You should see:
   - `users`
   - `verification_codes`
   - `password_resets`
   - `onboarding_data`
   - `user_progress`
   - `coach_messages` ← **Critical for AI Coach**
   - `cohorts`, `cohort_members`
   - `interview_sessions`, `interview_turns`
   - `portfolio_projects`
   - `companies`, `jobs`
   - `user_job_applications`
   - `hiring_feedback`

### Option B: Run via Supabase CLI (Advanced)

```bash
# Install Supabase CLI
npm install -g supabase

# Login
supabase login

# Link to project
supabase link --project-ref whxbxjpymksgvixudnjh

# Run migrations
supabase db push

# Or run individual files
psql -h db.whxbxjpymksgvixudnjh.supabase.co -U postgres -d postgres -f backend/migrations/001_create_users_table.sql
```

---

## 🔍 Verification Checklist

After running all migrations, verify:

- [ ] **Users table exists** with subscription fields
  ```sql
  SELECT column_name, data_type 
  FROM information_schema.columns 
  WHERE table_name = 'users' 
  AND column_name IN ('subscription_status', 'stripe_customer_id', 'free_reports_used');
  ```

- [ ] **Coach messages table exists**
  ```sql
  SELECT COUNT(*) FROM coach_messages;
  -- Should return 0 (empty but accessible)
  ```

- [ ] **All indexes created**
  ```sql
  SELECT indexname 
  FROM pg_indexes 
  WHERE schemaname = 'public';
  ```

- [ ] **RLS policies active**
  ```sql
  SELECT tablename, policyname 
  FROM pg_policies 
  WHERE schemaname = 'public';
  ```

---

## ⚠️ Troubleshooting

### Error: "relation already exists"
**Solution:** Table already created. Skip this migration or drop table first:
```sql
DROP TABLE IF EXISTS table_name CASCADE;
```

### Error: "permission denied"
**Solution:** Make sure you're using the service_role key, not anon key.

### Error: "column already exists"
**Solution:** Migration 005 trying to add columns that exist. Safe to skip.

### Error: "foreign key constraint fails"
**Solution:** Run migrations in order. Parent tables must exist before child tables.

---

## 🎯 What Happens After Migrations?

### ✅ AI Coach Will Work
- Conversations saved to `coach_messages`
- Progress tracking in `user_progress`
- Pro subscription gating enforced

### ✅ Subscription System Active
- Free users: 1 analysis limit
- Pro users: Unlimited access
- Stripe webhooks update `subscription_status`

### ✅ Job Marketplace Ready
- Companies can post jobs
- Users can apply
- Feedback loop tracks what works

---

## 🚀 Next Steps After Migrations

1. **Start Backend**
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload
   ```

2. **Start Frontend**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Test AI Coach**
   - Go to http://localhost:3000/coach/chat
   - Need Pro subscription (set manually in DB for testing):
   ```sql
   UPDATE users 
   SET subscription_status = 'pro' 
   WHERE email = 'your-test-email@example.com';
   ```

4. **Test Free Analysis Limit**
   - Go to http://localhost:3000
   - Enter job title → Should work once
   - Try again → Should show upgrade prompt

---

## 📊 Database Schema Diagram

```
users (core)
├── verification_codes
├── password_resets
├── onboarding_data
├── user_progress (Pro)
├── coach_messages (Pro) ← AI Coach
├── cohort_members → cohorts
├── interview_sessions (Pro) → interview_turns
├── portfolio_projects (Pro)
└── user_job_applications → jobs → companies
                                    └── hiring_feedback
```

---

## 🆘 Need Help?

### Check Migration Status
```sql
-- See all tables
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';

-- Count rows in each table
SELECT 'users' as table_name, COUNT(*) as row_count FROM users
UNION ALL
SELECT 'coach_messages', COUNT(*) FROM coach_messages
UNION ALL
SELECT 'user_progress', COUNT(*) FROM user_progress;
```

### Reset Everything (DESTRUCTIVE)
```sql
-- ⚠️ WARNING: This deletes ALL data
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO public;

-- Then re-run all migrations 001-007
```

---

## 📝 Summary

**Total Tables:** 13
**Total Migrations:** 7
**Estimated Time:** 10-15 minutes
**Order Matters:** Yes! Run 001 → 007 in sequence

**Most Critical:**
1. `001_create_users_table.sql` - Foundation
2. `005_add_subscription_fields.sql` - Freemium model
3. `006_create_pro_features_tables.sql` - AI Coach messages

**After completion, your Career Co-pilot platform is fully database-ready! 🎉**
