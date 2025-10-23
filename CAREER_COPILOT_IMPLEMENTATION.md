# 🚀 Career Co-pilot Implementation Guide

## Overview
This guide will help you implement the full "Career Co-pilot" vision - a lifelong career platform from college to retirement.

---

## 📊 Database Migrations (DO THIS FIRST!)

You have **3 new migration files** to run in Supabase:

### Step 1: Go to Supabase Dashboard
1. Open: https://supabase.com/dashboard
2. Select project: "Next Career Intelligence"
3. Click: **SQL Editor** (left sidebar)

### Step 2: Run Migrations in Order

**Migration 5: Subscription Management**
- File: `backend/migrations/005_add_subscription_fields.sql`
- Purpose: Adds subscription_status, stripe_customer_id, free_reports_used to users table
- Action: Copy entire file → Paste in SQL Editor → Click "Run"

**Migration 6: Pro Features Tables**
- File: `backend/migrations/006_create_pro_features_tables.sql`
- Purpose: Creates tables for AI Coach, AI Interviewer, Portfolio Projects
- Tables Created: user_progress, coach_messages, cohorts, interview_sessions, portfolio_projects
- Action: Copy entire file → Paste in SQL Editor → Click "Run"

**Migration 7: Marketplace Tables**
- File: `backend/migrations/007_create_marketplace_tables.sql`
- Purpose: Creates job board and recruiter portal tables
- Tables Created: companies, jobs, user_job_applications, hiring_feedback, recruiter_searches
- Action: Copy entire file → Paste in SQL Editor → Click "Run"

---

## 🏗️ Architecture Overview

### The 3 Tiers

**Tier 1: Free (The Hook)**
```
User Journey:
1. Landing page (app/page.tsx) → Single input: "Enter job title"
2. Teaser report (app/results/[jobTitle]/page.tsx) → Partial report with signup CTA
3. Sign up → Get 1 full report free
4. Paywall → "Upgrade to Pro" to analyze more jobs
```

**Tier 2: Pro Subscription ($10-20/month)**
```
Pro Features:
- Unlimited career analyses
- AI Coach (app/coach/page.tsx) with community cohorts
- AI Interviewer (app/interview/page.tsx) with audio feedback
- Portfolio Projects (app/projects/page.tsx) with AI grading
- Job Hub (app/jobs/page.tsx) with readiness scores
```

**Tier 3: Marketplace (B2B)**
```
Recruiter Portal:
- Search verified talent pool
- See user's verified skills from portfolio/interview scores
- Pay $100s-$1000s/month for access
```

---

## 📋 Implementation Checklist

### Phase 1: Freemium Foundation (Week 1-2)

**Backend:**
- [ ] Run migrations 005, 006, 007 in Supabase ⭐ START HERE
- [ ] Update `backend/app/services/supabase_client.py`:
  - Add methods: `check_subscription_status()`, `increment_free_reports()`
  - Add method: `get_user_with_subscription()`
- [ ] Create `backend/app/api/payments.py`:
  - Add Stripe webhook endpoint
  - Update subscription_status on payment
- [ ] Update `backend/app/api/analyze.py`:
  - Add `/api/analyze/teaser` (public, no auth, cached)
  - Update `/api/analyze` to check subscription and enforce limits

**Frontend:**
- [ ] Redesign `frontend/src/app/page.tsx`:
  - Remove all content
  - Add single input: "Enter your job title to see its AI risk"
  - Make it beautiful and minimal
- [ ] Create `frontend/src/app/results/[jobTitle]/page.tsx`:
  - Show partial report (risk score visible, rest blurred)
  - Add "Sign up to unlock" CTA
- [ ] Create `frontend/src/hooks/useAuth.ts`:
  - Manage Firebase auth state
  - Fetch user subscription status from backend
- [ ] Create `frontend/src/hooks/useSubscription.ts`:
  - Check if user is 'free' or 'pro'
  - Return helper: `canAccessFeature(feature: string)`
- [ ] Update `frontend/src/app/dashboard/page.tsx`:
  - Add paywall for free users
  - Lock "analyze" button after 1 free report
- [ ] Create `frontend/src/app/account/page.tsx`:
  - Subscription management
  - Link to Stripe checkout

### Phase 2: Pro Features (Week 3-5)

**AI Coach:**
- [ ] Backend: Create `backend/app/services/ai_coach_service.py`
  - Method: `create_progress_plan(user_id, roadmap)` → populate user_progress table
  - Method: `get_progress_checklist(user_id)` → fetch all items
  - Method: `chat(user_id, message)` → GPT-4 with user context
- [ ] Backend: Create `backend/app/api/coach.py`
  - `POST /coach/plan` → Create plan from roadmap
  - `GET /coach/progress` → Get checklist
  - `PUT /coach/progress/{item_id}` → Update item status
  - `POST /coach/chat` → Chat with AI Coach
- [ ] Frontend: Create `frontend/src/app/coach/page.tsx`
  - Chat interface (use npm package like `react-chat-widget`)
  - Progress checklist component
  - Community cohort section

**AI Interviewer:**
- [ ] Backend: Install dependencies: `pip install openai beautifulsoup4`
- [ ] Backend: Create `backend/app/services/ai_interviewer_service.py`
  - Method: `create_session(user_id, job_url)` → scrape job, create session
  - Method: `generate_question(session_id)` → GPT-4 creates interview question
  - Method: `grade_answer(session_id, audio_file)` → Whisper transcribe → GPT-4 analyze
- [ ] Backend: Create `backend/app/api/interviewer.py`
  - `POST /interviewer/sessions` → Start interview session
  - `POST /interviewer/sessions/{id}/respond` → Submit audio answer
  - `GET /interviewer/sessions/{id}` → Get session history
- [ ] Frontend: Create `frontend/src/app/interview/page.tsx`
  - Job description input
  - Audio recording UI (use MediaRecorder API)
  - Real-time feedback display

**Portfolio Projects:**
- [ ] Backend: Create `backend/app/services/portfolio_service.py`
  - Method: `generate_project_brief(user_id, skill)` → GPT-4 creates project
  - Method: `grade_submission(project_id, submission_url)` → AI grades work
- [ ] Backend: Create `backend/app/api/projects.py`
  - `GET /projects/generate` → Generate new project
  - `GET /projects` → Get user's projects
  - `POST /projects/{id}/submit` → Submit work
- [ ] Frontend: Create `frontend/src/app/projects/page.tsx`
  - Project briefs display
  - Submission interface
  - Grading results

### Phase 3: Marketplace (Week 6-8)

**Job Hub (B2C):**
- [ ] Backend: Install `pip install beautifulsoup4 httpx apscheduler`
- [ ] Backend: Create `backend/app/services/job_scraper_service.py`
  - Method: `scrape_company_jobs(company_url)` → scrape jobs
  - Method: `extract_skills(job_description)` → AI extracts required skills
  - Scheduler: Run nightly to populate jobs table
- [ ] Backend: Create `backend/app/api/jobs.py`
  - `GET /jobs` → Match jobs to user's target role
  - `GET /jobs/{id}/match` → Calculate readiness score
  - `POST /jobs/{id}/apply` → Track application
- [ ] Frontend: Create `frontend/src/app/jobs/page.tsx`
  - Job cards with readiness scores
  - Skill breakdown: ✅ Have / ⏳ Learning / ❌ Missing
  - "Add to Coach" button for missing skills

**Recruiter Portal (B2B):**
- [ ] Backend: Create `backend/app/api/recruiter.py`
  - `GET /talent-pool/search` → Search verified users
  - `POST /talent-pool/shortlist` → Save candidate
  - `GET /talent-pool/candidate/{id}` → View full profile (verified skills)
- [ ] Frontend: Create `frontend/src/app/recruiters/page.tsx`
  - B2B marketing page
  - "Request Demo" form
  - Pricing tiers

**Feedback Flywheel:**
- [ ] Backend: Create `backend/app/api/feedback.py`
  - `POST /feedback/hiring` → User reports "I got the job!"
  - Collect: important_skills, interview_topics, preparation_time
- [ ] Frontend: Add "I got the job!" button to job applications
  - Modal to collect feedback
  - Celebrate their success!

---

## 🎯 Quick Start (Next 30 Minutes)

### Immediate Actions:

1. **Run the 3 SQL migrations** ⭐ (10 min)
   - Go to Supabase SQL Editor
   - Run migrations 005, 006, 007

2. **Update Backend Dependencies** (5 min)
   ```bash
   cd backend
   source venv/bin/activate
   pip install openai beautifulsoup4 httpx stripe apscheduler
   pip freeze > requirements.txt
   ```

3. **Test Database Changes** (5 min)
   ```bash
   # In Supabase SQL Editor, run:
   SELECT * FROM users LIMIT 1;
   -- You should now see subscription_status column
   
   SELECT * FROM user_progress LIMIT 1;
   -- Should return empty table (no error)
   ```

4. **Update Your Todo List** (10 min)
   - Review the checklist above
   - Pick ONE feature to build first (I recommend: AI Coach)
   - Break it into smaller tasks

---

## 🧭 Recommended Build Order

**Week 1:** Freemium foundation (paywall, teaser page)
**Week 2:** AI Coach (highest retention value)
**Week 3:** Job Hub (close the loop - users find jobs)
**Week 4:** AI Interviewer (helps users get hired)
**Week 5:** Portfolio Projects (builds credibility)
**Week 6:** Feedback Flywheel (data moat begins)
**Week 7:** Recruiter Portal (B2B revenue)
**Week 8:** Polish, marketing, launch! 🚀

---

## 💡 Key Success Metrics

**Acquisition (Tier 1):**
- Landing page conversions: Target 5-10%
- Free → Pro conversion: Target 2-5%

**Retention (Tier 2):**
- Monthly churn: Target <5%
- AI Coach daily active users: Target 30%+
- Jobs applied to per user: Target 5+/month

**Revenue (Tier 3):**
- Pro MRR: $10-20 x subscribers
- Recruiter MRR: $100-1000 x companies
- Target: 70% Pro revenue, 30% recruiter revenue

---

## 🆘 Need Help?

**Database Issues:**
- Check: Supabase Dashboard → Database → Connection Pooler
- Verify: All migrations ran without errors
- Test: Run `SELECT tablename FROM pg_tables WHERE schemaname='public';`

**Backend Issues:**
- Check: `python -m uvicorn app.main:app --reload`
- Verify: http://localhost:8000/docs loads
- Test: `curl http://localhost:8000/api/health`

**Frontend Issues:**
- Check: `npm run dev`
- Verify: http://localhost:3000 loads
- Test: Open browser console for errors

---

## 🎉 You're Ready!

Your database is now ready for the full Career Co-pilot vision. Start with Phase 1 (Freemium) and build from there.

**Next Step:** Run the 3 SQL migrations in Supabase! 🚀
