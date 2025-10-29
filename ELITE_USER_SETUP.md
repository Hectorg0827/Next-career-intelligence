# Elite User Setup Guide

## Overview
This guide will help you set up an elite/admin user account for testing all premium features.

## Step 1: Run Database Migration

First, you need to add the new columns to your Supabase database:

1. Go to Supabase Dashboard: https://supabase.com/dashboard
2. Select your project: `whxbxjpymksgvixudnjh`
3. Click **SQL Editor** in the left sidebar
4. Click **New Query**
5. Copy and paste the contents of `backend/migrations/add_user_roles.sql`
6. Click **Run** (or press Cmd/Ctrl + Enter)

This will add these fields to the users table:
- `role` - 'user', 'elite', or 'admin'
- `subscription_status` - 'free', 'pro', or 'elite'
- `free_reports_used` - Track free usage
- `stripe_customer_id` - For billing
- `last_free_analysis_at` - Rate limiting

## Step 2: Deploy Backend with New Changes

The backend needs to be redeployed with the updated User model:

```bash
cd backend
gcloud builds submit --tag gcr.io/next-475619/next-backend
gcloud run deploy next-backend \
  --image gcr.io/next-475619/next-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## Step 3: Get Your Firebase UID

To find your Firebase UID:

### Option A: From Firebase Console
1. Go to Firebase Console: https://console.firebase.google.com/project/next-fc055
2. Click **Authentication** in left sidebar
3. Find your user account
4. Copy the **User UID** column

### Option B: From Browser Console (when logged in)
1. Log in to https://www.nextci.net
2. Open browser Developer Tools (F12)
3. Go to Console tab
4. Type: `auth.currentUser.uid`
5. Copy the UID that appears

### Option C: From localStorage
1. Log in to https://www.nextci.net
2. Open Developer Tools (F12)
3. Go to Application/Storage tab → Local Storage
4. Look for Firebase auth data with your UID

## Step 4: Set Your Account as Elite

Once you have your Firebase UID, run the script:

```bash
cd /Users/hectorgarcia/Desktop/Next-career-intelligence/backend/scripts
python3 set_elite_user.py YOUR_FIREBASE_UID_HERE elite elite
```

For example:
```bash
python3 set_elite_user.py abc123xyz456 elite elite
```

### Alternative: Use curl

If the Python script doesn't work, use curl directly:

```bash
curl -X POST "https://next-backend-795538981829.us-central1.run.app/api/users/YOUR_FIREBASE_UID/set-role?role=elite&subscription_status=elite"
```

## Step 5: Verify Elite Status

Check that your account was updated:

```bash
# Using the backend API
curl "https://next-backend-795538981829.us-central1.run.app/api/users/subscription?firebase_uid=YOUR_FIREBASE_UID"
```

You should see:
```json
{
  "subscription_status": "elite",
  "free_reports_used": 0,
  "stripe_customer_id": null,
  "last_free_analysis_at": null
}
```

## Elite Privileges

With elite/admin status, you get:
- ✅ **Unlimited career analyses** (no rate limits)
- ✅ **Full access to all AI features**
- ✅ **Access to job marketplace**
- ✅ **Resume builder and optimization**
- ✅ **AI career coach**
- ✅ **Interview simulator**
- ✅ **Priority support**
- ✅ **No paywalls**

## Testing Different Roles

You can test different privilege levels:

### Admin (Full Access)
```bash
python3 set_elite_user.py YOUR_UID admin elite
```

### Elite User (Premium)
```bash
python3 set_elite_user.py YOUR_UID elite elite
```

### Pro User (Paid)
```bash
python3 set_elite_user.py YOUR_UID user pro
```

### Free User (Limited)
```bash
python3 set_elite_user.py YOUR_UID user free
```

## Troubleshooting

### Error: User not found
- Make sure you've signed up at least once at https://www.nextci.net/auth/signup
- Verify your Firebase UID is correct

### Error: Connection refused
- Check that backend is deployed and running
- Test health: `curl https://next-backend-795538981829.us-central1.run.app/api/health`

### Database error
- Make sure you ran the migration SQL in Step 1
- Check Supabase logs for any errors

## Next Steps

After setting up your elite account:
1. Log out and log back in to refresh your session
2. Try creating career analyses
3. Test the job marketplace
4. Use the AI coach
5. Build and optimize resumes
6. Practice with interview simulator

Enjoy testing all the premium features! 🚀
