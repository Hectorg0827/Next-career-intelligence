# Fix: Policy Already Exists Error

If you see this error:
```
policy "Service role can manage career profiles" for table "career_profiles" already exists
```

This means the tables were already created. Here's how to fix it:

## Quick Fix (30 seconds)

### Option 1: Clean Slate (Recommended - Start Fresh)

**In Supabase SQL Editor**, run this ONCE:

```sql
-- Drop all tables to start fresh
DROP TABLE IF EXISTS onboarding CASCADE;
DROP TABLE IF EXISTS password_resets CASCADE;
DROP TABLE IF EXISTS verification_codes CASCADE;
DROP TABLE IF EXISTS users CASCADE;
```

Then go back to `SUPABASE_SENDGRID_SETUP.md` and run each of the 4 table creation scripts again, ONE AT A TIME.

### Option 2: Drop & Recreate Only Problematic Table

If you want to keep existing data, you can recreate just one table:

```sql
-- Drop just the onboarding table
DROP TABLE IF EXISTS onboarding CASCADE;

-- Then run this:
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

ALTER TABLE onboarding ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Service role can manage career profiles"
  ON onboarding FOR ALL
  USING (true);
```

## Why This Happens

When you run SQL scripts multiple times:
1. ✅ First time: Tables and policies are created
2. ❌ Second time: Error - table/policy already exists

The updated `SUPABASE_SENDGRID_SETUP.md` now includes `DROP TABLE IF EXISTS` at the beginning of the users table script, which fixes this automatically.

## Next Steps

After running the fix:

1. Verify tables were created:
   ```
   Supabase Dashboard → Table Editor
   ```
   You should see: `users`, `verification_codes`, `password_resets`, `onboarding`

2. Test the API:
   ```bash
   curl -X POST http://localhost:8000/api/auth/signup \
     -H "Content-Type: application/json" \
     -d '{
       "full_name": "Test User",
       "email": "test@example.com",
       "password": "TestPass123"
     }'
   ```

3. Check for new user in Supabase:
   ```
   Supabase Dashboard → Table Editor → users
   ```
   Should show your test user record

## Still Having Issues?

Check these:

1. **Are you running scripts ONE AT A TIME?**
   - ❌ Wrong: Copy all 4 scripts, paste together, run
   - ✅ Right: Copy script 1, run, wait, copy script 2, run, wait...

2. **Did you use the right credentials?**
   - Double-check `.env` file has correct SUPABASE_SERVICE_KEY
   - Should start with `eyJhbG...` (not the anon key)

3. **Is backend running?**
   ```bash
   ps aux | grep uvicorn
   ```
   Should show the server running on port 8000

4. **Check API logs:**
   Look at terminal where backend is running for error messages
