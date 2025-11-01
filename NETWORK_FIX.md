# Network Connection Fix - Frontend to Backend

## Problem Identified
The frontend at `https://nextci.net` reports "network not connected" error when trying to reach the backend API.

## Root Cause
The frontend environment variables were updated locally, but **Vercel needs to rebuild the frontend** to pick up the new `NEXT_PUBLIC_API_URL` environment variable.

## Solution

### Step 1: Verify Environment Variable is Set on Vercel
1. Go to https://vercel.com/dashboard
2. Select your "next-career-intelligence" project
3. Go to **Settings** → **Environment Variables**
4. Ensure `NEXT_PUBLIC_API_URL` is set to:
   ```
   https://next-career-backend-795538981829.us-central1.run.app
   ```

### Step 2: Trigger a Vercel Rebuild
Choose ONE of these options:

**Option A: Vercel Dashboard Redeploy**
1. Go to Vercel Dashboard
2. Select "next-career-intelligence" project
3. Click **Deployments** tab
4. Find the latest deployment
5. Click **Redeploy** button

**Option B: Push a Commit (Automatic)**
1. Make a small commit to trigger a redeploy:
   ```bash
   cd /Users/hectorgarcia/Desktop/Next-career-intelligence/frontend
   git add .
   git commit -m "chore: Trigger Vercel rebuild for environment variables"
   git push origin main
   ```

**Option C: Using Vercel CLI**
1. Install Vercel CLI: `npm i -g vercel`
2. Run: `vercel --prod --force`

### Step 3: Verify the Fix
After Vercel deploys, test:
1. Visit https://nextci.net
2. Enter career profile data
3. Click "Analyze"
4. Should see full AI analysis (NOT "network not connected" error)

## Backend Verification
The backend is confirmed working:
- ✅ Health endpoint: `/api/health` → Returns 200 OK
- ✅ Analyze endpoint: `/api/analyze` → Returns 201 with full analysis
- ✅ CORS headers: Correctly set for `https://nextci.net`

## API Testing (Verified Working)
```bash
curl -X POST https://next-career-backend-795538981829.us-central1.run.app/api/analyze \
  -H "Content-Type: application/json" \
  -H "Origin: https://nextci.net" \
  -d '{
    "experience": 5,
    "skills": ["Python", "FastAPI"],
    "job_title": "Backend Developer",
    "location": "San Francisco"
  }'
```

Response: Full career analysis with displacement risk, benchmarks, etc.

## Troubleshooting

**If still getting "network not connected" after Vercel redeploy:**
1. Clear browser cache (Ctrl+Shift+Delete or Cmd+Shift+Delete)
2. Try incognito/private window
3. Check browser DevTools → Network tab to see:
   - What URL is being called
   - What error response is returned
4. Run this test:
   ```bash
   curl -H "Origin: https://nextci.net" \
     https://next-career-backend-795538981829.us-central1.run.app/api/health
   ```

## CORS Headers Confirmed ✅
```
access-control-allow-origin: https://nextci.net
access-control-allow-methods: DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT
access-control-allow-credentials: true
access-control-max-age: 600
```

All CORS headers are properly configured on the backend.
