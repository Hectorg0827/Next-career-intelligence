# 🔒 Supabase RLS Configuration Guide

## Step 1: Access Supabase SQL Editor

1. Go to: https://whxbxjpymksgvixudnjh.supabase.co
2. Log in with your Supabase account
3. Navigate to **SQL Editor** in the left sidebar
4. Click **"+ New Query"**

## Step 2: Run RLS Setup Script

Copy the entire contents of `SUPABASE_RLS_SETUP.sql` and paste into the SQL Editor, then click **"Run"**.

This will:
- ✅ Create RLS policies for all 10 tables
- ✅ Allow service_role (backend) full access
- ✅ Allow authenticated users to access their own data
- ✅ Enable Row Level Security on all tables

## Step 3: Verify Configuration

Run this verification query:

```sql
SELECT 
  schemaname,
  tablename,
  policyname,
  roles
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename;
```

You should see policies for:
- users (2 policies)
- career_profiles (2 policies)
- analyses (2 policies)
- career_roadmaps (2 policies)
- interview_sessions (2 policies)
- interview_answers (2 policies)
- coach_conversations (2 policies)
- career_goals (2 policies)
- job_applications (2 policies)
- subscriptions (2 policies)

## Step 4: Test Backend Connection

After applying policies, restart the backend and test:

```bash
curl http://localhost:8000/api/health | python3 -m json.tool
```

Expected result:
```json
{
  "status": "operational",
  "services": {
    "api": "operational",
    "database": "operational",  // ✅ Should now be operational
    "gemini": "configured"
  }
}
```

## Troubleshooting

### If database still shows "error":

1. **Check service_role key**: Verify `SUPABASE_SERVICE_KEY` in backend/.env is correct
2. **Check connection**: Run in Supabase SQL Editor:
   ```sql
   SELECT count(*) FROM users;
   ```
   Should return count without error.

3. **Check backend logs**:
   ```bash
   cd backend
   tail -f backend.log
   ```

### If policies not working:

1. **Verify RLS is enabled**:
   ```sql
   SELECT tablename, rowsecurity 
   FROM pg_tables 
   WHERE schemaname = 'public';
   ```
   All tables should show `rowsecurity = true`

2. **Check policy syntax**:
   ```sql
   SELECT * FROM pg_policies WHERE schemaname = 'public' AND tablename = 'users';
   ```

## Next Steps

Once RLS is configured:
1. ✅ Backend can write to database
2. ✅ Analyses will persist
3. ✅ User data is secure
4. Move to Task 2: Firebase Authentication
