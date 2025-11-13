# Production Deployment Guide - NEXT Career Intelligence

**Status:** Production Ready  
**Last Updated:** November 13, 2025  
**Version:** 2.0.0 - Career Operating System

---

## Executive Summary

Your NEXT Career Intelligence platform is production-ready with a complete Career Operating System transformation. This guide provides step-by-step deployment instructions for launching to market.

**Deployment Stack:**
- **Frontend:** Next.js 14 on Vercel (auto-scaling, global CDN)
- **Backend:** FastAPI on Google Cloud Run (serverless, pay-per-use)
- **Database:** Supabase PostgreSQL (managed, auto-backups)
- **AI:** Google Gemini API (career intelligence)

---

## Quick Start (30 Minutes to Production)

```bash
# 1. Deploy Backend to Cloud Run
cd backend
gcloud run deploy next-career-backend --source . --region us-central1

# 2. Deploy Frontend to Vercel
cd ../frontend
vercel --prod

# 3. Update frontend with backend URL
vercel env add NEXT_PUBLIC_API_URL production
# Enter the Cloud Run URL from step 1

# 4. Redeploy frontend
vercel --prod
```

**Done!** Your platform is live at your Vercel URL.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Backend Deployment](#backend-deployment)
4. [Frontend Deployment](#frontend-deployment)
5. [Database Configuration](#database-configuration)
6. [Post-Deployment Checklist](#post-deployment-checklist)
7. [Monitoring & Maintenance](#monitoring--maintenance)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Accounts

| Service | Purpose | Cost | Sign Up |
|---------|---------|------|---------|
| **Google Cloud** | Backend hosting | $0-50/month | [cloud.google.com](https://cloud.google.com) |
| **Vercel** | Frontend hosting | Free-$20/month | [vercel.com](https://vercel.com) |
| **Supabase** | Database + Auth | Free-$25/month | [supabase.com](https://supabase.com) |
| **Gemini API** | AI analysis | Pay-per-use | [ai.google.dev](https://ai.google.dev) |

### Local Tools

```bash
# Install required tools
brew install google-cloud-sdk  # macOS
npm install -g vercel

# Verify installations
gcloud --version
vercel --version
node --version  # Should be >= 18
python3 --version  # Should be >= 3.12
```

---

## Environment Setup

### Backend Environment Variables

Create `/backend/.env`:

```bash
# Core Configuration
ENVIRONMENT=production

# Supabase (REQUIRED)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key
SUPABASE_JWT_SECRET=your-jwt-secret

# Google Gemini AI (REQUIRED)
GEMINI_API_KEY=your-gemini-api-key

# Security
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=https://yourdomain.com

# Optional Services
REDIS_HOST=your-redis-host
SENTRY_DSN=your-sentry-dsn
```

**Get Your Keys:**
- **Supabase:** Project Settings > API > URL and service_role key
- **Gemini:** [Google AI Studio](https://aistudio.google.com/apikey)
- **Secret Key:** `openssl rand -hex 32`

### Frontend Environment Variables

Create `/frontend/.env.production`:

```bash
# API Configuration (will update after backend deployment)
NEXT_PUBLIC_API_URL=https://your-backend.run.app

# Supabase Public Keys
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-public-key
```

---

## Backend Deployment

### Google Cloud Run (5 minutes)

1. **Authenticate:**

```bash
gcloud auth login
gcloud config set project your-project-id
```

2. **Enable Required APIs:**

```bash
gcloud services enable run.googleapis.com cloudbuild.googleapis.com
```

3. **Deploy:**

```bash
cd backend

gcloud run deploy next-career-backend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --max-instances 100 \
  --min-instances 0 \
  --timeout 300
```

4. **Add Environment Variables:**

```bash
gcloud run services update next-career-backend \
  --set-env-vars="ENVIRONMENT=production,SUPABASE_URL=https://your-project.supabase.co" \
  --set-env-vars="GEMINI_API_KEY=your-key"
# Add all other environment variables
```

5. **Get Deployed URL:**

```bash
gcloud run services describe next-career-backend \
  --format="value(status.url)"
```

**Save this URL** - you'll need it for the frontend configuration.

### Alternative: Railway (Simpler Option)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy
cd backend
railway up

# Add environment variables in Railway dashboard
```

---

## Frontend Deployment

### Vercel (3 minutes)

1. **Login:**

```bash
cd frontend
vercel login
```

2. **First Deployment:**

```bash
vercel

# Follow prompts:
# - Link to existing project? No
# - Project name: next-career-intelligence
# - Directory: ./
```

3. **Add Environment Variables:**

```bash
# Add backend URL (from previous step)
vercel env add NEXT_PUBLIC_API_URL production
# Paste: https://your-backend.run.app

# Add Supabase credentials
vercel env add NEXT_PUBLIC_SUPABASE_URL production
# Paste: https://your-project.supabase.co

vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY production
# Paste: your-anon-key
```

4. **Deploy to Production:**

```bash
vercel --prod
```

5. **Custom Domain (Optional):**

In Vercel Dashboard:
- Go to Project Settings > Domains
- Add `yourdomain.com`
- Update DNS records at your registrar

---

## Database Configuration

### Supabase Setup

1. **Create Project:**
   - Go to [supabase.com/dashboard](https://supabase.com/dashboard)
   - Click "New Project"
   - Choose region closest to users
   - Save your database password

2. **Note Your Credentials:**
   - Project URL: `https://xxx.supabase.co`
   - Anon/Public Key: For frontend
   - Service Role Key: For backend (keep secret!)
   - JWT Secret: For backend auth

3. **Database is auto-created** by backend on first run (if tables don't exist)

4. **Enable Row Level Security:**

```sql
-- In Supabase SQL Editor
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE career_health_history ENABLE ROW LEVEL SECURITY;

-- Users can only access their own data
CREATE POLICY "Users access own data" ON profiles
  FOR ALL USING (auth.uid() = user_id);
```

---

## Post-Deployment Checklist

### Verification Steps

1. **Backend Health Check:**

```bash
curl https://your-backend.run.app/api/health
# Expected: {"status":"healthy"}
```

2. **Frontend Loading:**

Visit `https://your-domain.vercel.app`
- Homepage loads ✓
- Navigation works ✓
- Login page accessible ✓

3. **End-to-End Test:**

- Register new account
- Verify email (if configured)
- Login successfully
- Navigate to `/dashboard`
- Verify Career Health Score displays
- Check job recommendations load

4. **Mobile Test:**

- Open on mobile device
- Verify bottom navigation appears
- Test touch interactions
- Check responsiveness

### Security Checklist

- [ ] HTTPS enabled (automatic on Vercel & Cloud Run)
- [ ] CORS configured correctly
- [ ] Environment variables secured
- [ ] Row Level Security enabled on database
- [ ] API rate limiting active
- [ ] No secrets in Git repository

---

## Monitoring & Maintenance

### Set Up Monitoring

1. **Sentry (Error Tracking):**

```bash
# Sign up at sentry.io
# Add SENTRY_DSN to backend environment variables
gcloud run services update next-career-backend \
  --set-env-vars="SENTRY_DSN=https://your-sentry-dsn"
```

2. **View Logs:**

```bash
# Backend logs
gcloud logging read "resource.type=cloud_run_revision" --limit 50

# Frontend logs (Vercel Dashboard > Logs)
```

3. **Performance Monitoring:**

- Vercel Analytics: Built-in (Dashboard > Analytics)
- Cloud Run Metrics: Console > Cloud Run > Metrics

### Regular Maintenance

**Weekly:**
- Check error rates in Sentry
- Review Cloud Run costs
- Monitor database size

**Monthly:**
- Update dependencies
- Review security advisories
- Test backup restoration

---

## Troubleshooting

### Common Issues

**Issue: Frontend can't reach backend (CORS error)**

```bash
# Solution: Update CORS_ORIGINS in backend
gcloud run services update next-career-backend \
  --set-env-vars="CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com"
```

**Issue: "Authentication service unavailable"**

```bash
# Solution: Verify Supabase credentials in backend
gcloud run services update next-career-backend \
  --set-env-vars="SUPABASE_URL=https://your-project.supabase.co,SUPABASE_KEY=your-key"
```

**Issue: Dashboard shows empty states**

1. Check if user is logged in
2. Verify backend is receiving requests (check logs)
3. Confirm database has user profile data

**Issue: Build fails on Vercel**

```bash
# Clear cache and rebuild
vercel --force

# Check build logs in Vercel Dashboard
```

---

## Cost Optimization

### Expected Monthly Costs

| Tier | Users | Backend | Frontend | Database | Total |
|------|-------|---------|----------|----------|-------|
| **Starter** | < 100 | Free | Free | Free | $0 |
| **Growth** | < 1000 | $25 | Free | $25 | $50 |
| **Scale** | < 10k | $100 | $20 | $25 | $145 |

### Reduce Costs

- Use Vercel Hobby plan (free for personal projects)
- Set Cloud Run `--min-instances=0` (no idle costs)
- Enable Supabase connection pooling
- Use Redis caching (reduces database queries)

---

## Rollback Procedures

### Backend Rollback

```bash
# List revisions
gcloud run revisions list --service next-career-backend

# Rollback to previous
gcloud run services update-traffic next-career-backend \
  --to-revisions=REVISION_NAME=100
```

### Frontend Rollback

```bash
# Via CLI
vercel rollback

# Or in Vercel Dashboard > Deployments > Promote to Production
```

---

## Next Steps

Now that you're deployed:

1. **Set up custom domain**
2. **Configure email provider** (SendGrid)
3. **Enable analytics** (Google Analytics)
4. **Add monitoring** (Sentry)
5. **Create backup schedule**

---

## Support Resources

- **Backend Issues:** `gcloud logging read` + Cloud Run logs
- **Frontend Issues:** Vercel Dashboard > Logs
- **Database Issues:** Supabase Dashboard > Logs
- **Community:** GitHub Issues

---

## Conclusion

Your NEXT Career Intelligence platform is now live! 

**What You've Deployed:**
✅ Production-ready backend on Google Cloud Run  
✅ Lightning-fast frontend on Vercel CDN  
✅ Secure authentication with Supabase  
✅ AI-powered career intelligence with Gemini  
✅ Mobile-first design with responsive UI  

**Status:** 🟢 **PRODUCTION READY - GO TO MARKET**

---

*Deployment Guide v2.0.0*  
*Last Updated: November 13, 2025*  
*Platform: Career Operating System*
