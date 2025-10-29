# Backend Database Configuration Fix

## Problem
The backend shows `"database":"error"` because it can't connect to PostgreSQL.

## Solution: Use Supabase PostgreSQL

### Step 1: Get Supabase Database URL

1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Select your project: `whxbxjpymksgvixudnjh`
3. Go to **Settings** → **Database**
4. Scroll to **Connection String**
5. Select **Connection Pooling** tab
6. Copy the **Connection string** (it looks like):
   ```
   postgresql://postgres.whxbxjpymksgvixudnjh:[YOUR-PASSWORD]@aws-0-us-west-1.pooler.supabase.com:6543/postgres
   ```
7. Replace `[YOUR-PASSWORD]` with your actual database password

### Step 2: Add to GRC Environment Variables

In your Google Cloud Run backend deployment, add this environment variable:

```
DATABASE_URL=postgresql://postgres.whxbxjpymksgvixudnjh:[YOUR-PASSWORD]@aws-0-us-west-1.pooler.supabase.com:6543/postgres
```

### Step 3: Redeploy Backend

After adding the `DATABASE_URL` environment variable, redeploy your backend to GRC.

## Alternative: Use Supabase SDK Instead of PostgreSQL

If you prefer to use Supabase's SDK instead of direct PostgreSQL connection, we can refactor the backend to use Supabase client library.

---

## Quick Test After Fix

Once deployed, test with:
```bash
curl https://next-backend-jxs4smo7nq-uc.a.run.app/api/health
```

Should show: `"database":"operational"`

---

## Current Status

- ✅ Frontend deployed to Vercel
- ✅ Firebase authentication working (fixed)
- ✅ Backend deployed to GRC
- ⚠️ Backend database not connected → **Fix this**
- ⏳ After database fix, user registration will work
