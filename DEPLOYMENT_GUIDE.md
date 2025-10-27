# 🚀 Complete Deployment Guide
## NEXT | Career Intelligence Platform

This guide covers deploying the full stack:
- **Backend**: Google Cloud Run
- **Database**: Supabase (PostgreSQL)
- **Frontend**: Vercel

---

## 📋 Pre-Deployment Checklist

- [ ] Google Cloud account with billing enabled
- [ ] Supabase account (already configured)
- [ ] Vercel account
- [ ] GitHub repository access
- [ ] Firebase project configured
- [ ] Environment variables documented

---

## 1️⃣ Backend Deployment to Google Cloud Run

### Prerequisites

```bash
# Install Google Cloud SDK
brew install --cask google-cloud-sdk

# Login to Google Cloud
gcloud auth login

# Set your project
gcloud config set project next-fc055
```

### Deploy Backend

```bash
cd backend

# Build and deploy to Cloud Run
gcloud run deploy next-backend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --max-instances 10 \
  --min-instances 0 \
  --port 8080 \
  --set-env-vars="$(cat .env.production | tr '\n' ',' | sed 's/,$//')"

# Get the deployed URL
gcloud run services describe next-backend --region us-central1 --format='value(status.url)'
```

### Set Environment Variables in Cloud Run

Go to Cloud Run Console or use:

```bash
gcloud run services update next-backend --region us-central1 \
  --set-env-vars="SUPABASE_URL=https://whxbxjpymksgvixudnjh.supabase.co" \
  --set-env-vars="SUPABASE_KEY=your-supabase-service-key" \
  --set-env-vars="GOOGLE_GEMINI_API_KEY=your-gemini-key" \
  --set-env-vars="FIREBASE_PROJECT_ID=next-fc055" \
  --set-env-vars="STRIPE_SECRET_KEY=your-stripe-secret"
```

---

## 2️⃣ Supabase Configuration (Already Set Up)

Your Supabase is already configured:
- **URL**: `https://whxbxjpymksgvixudnjh.supabase.co`
- **Database**: PostgreSQL hosted on Supabase

### Verify Database Tables

```bash
# Check tables exist
psql "postgresql://postgres.[password]@db.whxbxjpymksgvixudnjh.supabase.co:5432/postgres"

# List tables
\dt
```

### Create Missing Tables (if needed)

The backend will auto-create tables, but you can also run migrations:

```sql
-- Users table
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  firebase_uid TEXT UNIQUE NOT NULL,
  email TEXT UNIQUE NOT NULL,
  name TEXT,
  subscription_tier TEXT DEFAULT 'free',
  created_at TIMESTAMP DEFAULT NOW()
);

-- User profiles table (for multi-agent system)
CREATE TABLE IF NOT EXISTS user_profiles (
  user_id TEXT PRIMARY KEY,
  profile_data JSONB,
  updated_at TIMESTAMP DEFAULT NOW()
);
```

---

## 3️⃣ Frontend Deployment to Vercel

### Option A: Deploy via Vercel Dashboard (Recommended)

1. **Go to**: https://vercel.com/new
2. **Import Git Repository**: Connect your GitHub repo
3. **Configure Project**:
   - Framework Preset: **Next.js**
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `.next`
4. **Add Environment Variables** (see below)
5. **Click Deploy**

### Option B: Deploy via Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Navigate to frontend
cd frontend

# Login to Vercel
vercel login

# Deploy
vercel --prod
```

### Environment Variables for Vercel

Add these in **Vercel Dashboard → Project Settings → Environment Variables**:

```bash
# Backend API (Update with your Cloud Run URL)
NEXT_PUBLIC_API_URL=https://next-backend-XXXXX-uc.a.run.app

# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://whxbxjpymksgvixudnjh.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndoeGJ4anB5bWtzZ3ZpeHVkbmpoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA4NjAzNDksImV4cCI6MjA3NjQzNjM0OX0.8ykQi5mPIe48aA8E3J82acqqPlhEtS7VICduXOui0zc

# Firebase
NEXT_PUBLIC_FIREBASE_API_KEY=AIzaSyDIQ68KTtgSu0716r1X9p8XGGHJivdXY4Q
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=next-fc055.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=next-fc055
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=next-fc055.firebasestorage.app
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=438736067565
NEXT_PUBLIC_FIREBASE_APP_ID=1:438736067565:web:5ec706d253893954a0e5e4
NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID=G-HQLTL9GQ5Y

# Google OAuth
NEXT_PUBLIC_GOOGLE_CLIENT_ID=795538981829-0c05b330697k523h6aehtabvbik8d9oe.apps.googleusercontent.com

# Stripe
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_51SKRgLHwn1oJmJZkyS2T6xTbuwl538mqRESS38j0diGssBPAdX5gap5aHpepFh6XrUW9ZbqMqFqd4dRX9UQP18ft000CV1p0et
```

---

## 4️⃣ Post-Deployment Configuration

### Update Frontend to Use New Backend URL

After deploying backend, update the frontend's API URL:

```bash
# In Vercel Dashboard
# Environment Variables → NEXT_PUBLIC_API_URL
# Set to your Cloud Run URL
```

### Configure CORS in Backend

Update `backend/app/core/middleware.py`:

```python
origins = [
    "https://your-vercel-app.vercel.app",
    "https://your-custom-domain.com",
    "http://localhost:3000"  # Keep for local dev
]
```

### Update Firebase Authorized Domains

1. Go to Firebase Console → Authentication → Settings
2. Add your Vercel domain to **Authorized domains**:
   - `your-app.vercel.app`
   - `your-custom-domain.com`

### Update Google OAuth Redirect URIs

1. Go to Google Cloud Console → APIs & Services → Credentials
2. Edit your OAuth 2.0 Client ID
3. Add to **Authorized redirect URIs**:
   - `https://your-app.vercel.app`
   - `https://next-fc055.firebaseapp.com/__/auth/handler`

---

## 5️⃣ Verification Checklist

### Backend Health Check
```bash
curl https://your-backend-url.run.app/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "version": "1.0.0"
}
```

### Frontend Access
- Visit: `https://your-app.vercel.app`
- Test login/signup
- Test job analysis
- Verify multi-agent system works

### Database Connection
```bash
# Test from backend
curl https://your-backend-url.run.app/api/users
```

---

## 6️⃣ Custom Domain Setup (Optional)

### For Frontend (Vercel)
1. Go to Vercel Dashboard → Domains
2. Add your custom domain
3. Configure DNS records as instructed

### For Backend (Cloud Run)
```bash
gcloud run domain-mappings create \
  --service next-backend \
  --domain api.your-domain.com \
  --region us-central1
```

---

## 7️⃣ Monitoring & Logs

### View Cloud Run Logs
```bash
gcloud run services logs read next-backend --region us-central1 --limit 50
```

### View Vercel Logs
- Go to Vercel Dashboard → Your Project → Deployments → View Logs

### Monitor Supabase
- Go to Supabase Dashboard → Database → Logs
- Monitor queries and performance

---

## 🔧 Troubleshooting

### Backend Not Responding
```bash
# Check Cloud Run status
gcloud run services describe next-backend --region us-central1

# View recent logs
gcloud run services logs read next-backend --region us-central1
```

### Frontend Build Failures
- Check Vercel deployment logs
- Verify all environment variables are set
- Check for TypeScript errors

### Database Connection Issues
- Verify Supabase credentials
- Check IP allowlisting (Supabase allows all by default)
- Test connection from Cloud Run

---

## 📊 Deployment URLs

After deployment, you should have:

- **Frontend**: `https://your-app.vercel.app`
- **Backend**: `https://next-backend-XXXXX-uc.a.run.app`
- **Database**: `https://whxbxjpymksgvixudnjh.supabase.co`

---

## 🎉 Success Criteria

- ✅ Backend responds to health check
- ✅ Frontend loads and shows homepage
- ✅ User signup/login works
- ✅ Job analysis triggers multi-agent system
- ✅ Database stores user data
- ✅ Stripe payments work (if enabled)

---

## 📞 Support

If you encounter issues:
- Check logs in Cloud Run and Vercel
- Verify environment variables
- Test database connection
- Review CORS configuration
