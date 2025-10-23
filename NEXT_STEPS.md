# 🚀 NEXT STEPS - Complete Setup Guide

## Current Status ✅

### Completed
- ✅ **AI Coach Backend** - `ai_coach_service.py` (470 lines, ChatGPT-style)
- ✅ **AI Coach API** - `coach.py` (3 endpoints: start, message, history)
- ✅ **AI Coach Frontend** - `/coach/chat` page with real-time messaging
- ✅ **Landing Page** - Redesigned with single "Is Your Job AI-Proof?" input
- ✅ **Subscription System** - Backend gating, frontend hooks, Stripe webhooks
- ✅ **Migration Files** - 7 SQL files ready to run

### Pending
- ⏳ **Database Setup** - Run migrations in Supabase (15 minutes)
- ⏳ **Testing** - Verify full system works

---

## 📋 Action Plan

### Step 1: Run Database Migrations (15 minutes) 🎯

**Open this file for full guide:**
```
backend/migrations/MIGRATION_GUIDE.md
```

**Quick version:**

1. **Go to Supabase Dashboard**
   - URL: https://supabase.com/dashboard/project/whxbxjpymksgvixudnjh
   - Click "SQL Editor" → "New Query"

2. **Run migrations in order (copy/paste each file):**
   ```
   001_create_users_table.sql          ← Foundation
   002_create_verification_codes_table.sql
   003_create_password_resets_table.sql
   004_create_onboarding_table.sql
   005_add_subscription_fields.sql     ← Freemium model
   006_create_pro_features_tables.sql  ← AI Coach messages
   007_create_marketplace_tables.sql   ← Job marketplace
   ```

3. **Verify migrations worked:**
   - Run `backend/migrations/CHECK_STATUS.sql`
   - Should see 15 tables including `coach_messages`

---

### Step 2: Test Backend (5 minutes)

1. **Start backend server:**
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload
   ```

2. **Run test script:**
   ```bash
   python test_backend.py
   ```
   
   Expected output:
   ```
   ✅ Health check passed
   ✅ API docs accessible
   ✅ Coach endpoint exists
   ✅ Payments endpoint exists
   ```

3. **Open API docs:**
   - http://localhost:8000/docs
   - Verify `/coach/conversations/start` endpoint exists

---

### Step 3: Test Frontend (5 minutes)

1. **Start frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

2. **Test landing page:**
   - Go to http://localhost:3000
   - See new "Is Your Job AI-Proof?" design
   - Enter job title → Should redirect to `/analyze?job=...`

3. **Test AI Coach (Pro users only):**
   - First, set yourself as Pro in database:
   ```sql
   UPDATE users 
   SET subscription_status = 'pro' 
   WHERE email = 'your-email@example.com';
   ```
   
   - Go to http://localhost:3000/coach/chat
   - Should see AI greeting message
   - Type message → Should get AI response

---

### Step 4: Test Subscription Gating (5 minutes)

1. **Test free user limit:**
   - Set user to free:
   ```sql
   UPDATE users 
   SET subscription_status = 'free',
       free_reports_used = 0
   WHERE email = 'your-email@example.com';
   ```
   
   - Go to landing page
   - Enter job title → Should work (1st time)
   - Try again → Should show "Upgrade to Pro" (402 error)

2. **Test AI Coach gating:**
   - As free user, go to `/coach/chat`
   - Should see "Upgrade to Pro" paywall
   - Switch to Pro → Should access chat

---

## 🎯 Feature Checklist

### AI Coach ✅
- [x] Backend service (Gemini AI)
- [x] API endpoints (start, message, history)
- [x] Frontend chat UI
- [x] Pro subscription gating
- [ ] Database tables created (pending migration)
- [ ] End-to-end test

### Subscription System ✅
- [x] Database schema (subscription_status, free_reports_used)
- [x] Backend gating (analyze.py checks limits)
- [x] Frontend hooks (useAuth, useSubscription)
- [x] Stripe webhooks (payments.py)
- [ ] Stripe keys in .env
- [ ] Payment flow test

### Landing Page ✅
- [x] Redesigned (single input focus)
- [x] Beautiful gradient design
- [x] Trust indicators
- [x] Social proof stats
- [x] Redirects to /analyze

---

## 🔧 Environment Variables Needed

### Backend (.env)
```bash
# Already configured:
SUPABASE_URL=https://whxbxjpymksgvixudnjh.supabase.co
SUPABASE_KEY=<your-key>
SENDGRID_API_KEY=SG.bD1yvViYS-G7Fv1DhTiTQQ...
GEMINI_API_KEY=<your-key>

# Need to add:
STRIPE_SECRET_KEY=sk_test_...        # Get from Stripe dashboard
STRIPE_WEBHOOK_SECRET=whsec_...      # Get from Stripe webhooks
STRIPE_PRO_PRICE_ID=price_...        # Create Pro price in Stripe
```

### Frontend (.env.local)
```bash
# Already configured:
NEXT_PUBLIC_FIREBASE_API_KEY=...
NEXT_PUBLIC_SUPABASE_URL=...
NEXT_PUBLIC_SUPABASE_ANON_KEY=...
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 📊 Database Schema Overview

```
users (foundation)
├── id (UUID)
├── email, password_hash
├── subscription_status ← 'free', 'pro', 'enterprise'
├── stripe_customer_id
├── free_reports_used ← Max 1 for free tier
└── last_free_analysis_at

coach_messages (AI Coach conversations)
├── id (UUID)
├── user_id → users
├── role ← 'user' or 'assistant'
├── content ← Message text
├── session_id ← Group conversations
└── created_at

user_progress (Track learning)
├── id (UUID)
├── user_id → users
├── target_role, current_role
├── item_name ← Skill/course name
├── status ← 'not_started', 'in_progress', 'completed'
└── priority (1-10)

companies, jobs, user_job_applications (Marketplace)
└── For job matching and hiring feedback loop
```

---

## 🚨 Common Issues & Solutions

### Issue: Backend won't start
**Error:** `ModuleNotFoundError: No module named 'fastapi'`
**Solution:**
```bash
cd backend
pip install -r requirements.txt
```

### Issue: Frontend won't start
**Error:** `Cannot find module 'lucide-react'`
**Solution:**
```bash
cd frontend
npm install
```

### Issue: AI Coach returns 402 error
**Cause:** User not set to Pro subscription
**Solution:**
```sql
UPDATE users SET subscription_status = 'pro' WHERE email = 'your-email';
```

### Issue: Coach messages not saving
**Cause:** `coach_messages` table doesn't exist
**Solution:** Run migration `006_create_pro_features_tables.sql`

### Issue: Free analysis limit not working
**Cause:** Migration 005 not run (subscription fields missing)
**Solution:** Run `005_add_subscription_fields.sql`

---

## 📈 Success Metrics

After completing setup, you should have:

- ✅ **15 database tables** created in Supabase
- ✅ **Backend running** on http://localhost:8000
- ✅ **Frontend running** on http://localhost:3000
- ✅ **API docs** accessible at /docs
- ✅ **Landing page** showing new design
- ✅ **AI Coach** working for Pro users
- ✅ **Free tier limit** enforcing 1 analysis
- ✅ **Subscription gating** working

---

## 🎉 What You've Built

You now have a complete **Career Co-pilot** platform with:

### Free Tier
- 1 free career analysis
- Landing page with AI risk assessment
- Job title analysis

### Pro Tier ($10-20/month)
- Unlimited career analyses
- **AI Career Coach** (ChatGPT-style conversations)
- Personalized learning roadmap
- Progress tracking
- AI Interview practice (framework ready)
- Community cohorts (framework ready)

### Enterprise Tier (Future)
- Team management
- Job marketplace
- Hiring feedback loop
- Custom branding

---

## 📚 Documentation Files Created

1. **MIGRATION_GUIDE.md** - Complete database setup guide
2. **CHECK_STATUS.sql** - Verify migrations worked
3. **test_backend.py** - Automated backend testing
4. **NEXT_STEPS.md** - This file

---

## 🎯 After Setup is Complete

### Immediate Next Steps:
1. Add Stripe API keys to enable payments
2. Create test users with different subscription tiers
3. Test full user flow: signup → free analysis → upgrade → AI Coach
4. Deploy to production (Vercel + Railway/Render)

### Future Enhancements:
1. Email notifications (SendGrid already configured)
2. AI Interviewer full implementation
3. Job marketplace activation
4. Mobile app (React Native)
5. API rate limiting
6. Analytics dashboard

---

## 🆘 Need Help?

### Check Logs
```bash
# Backend logs
tail -f backend/logs/app.log

# Frontend logs (in terminal where npm run dev is running)
```

### Verify Database
```bash
# Run in Supabase SQL Editor
SELECT * FROM users LIMIT 5;
SELECT * FROM coach_messages LIMIT 5;
```

### Test Endpoints
```bash
# Health check
curl http://localhost:8000/health

# API docs
open http://localhost:8000/docs
```

---

## ✅ Final Checklist

Before considering setup complete:

- [ ] All 7 migrations run successfully
- [ ] `CHECK_STATUS.sql` shows 15 tables
- [ ] Backend test script passes (4/4 tests)
- [ ] Landing page loads with new design
- [ ] Can enter job title and see redirect
- [ ] AI Coach accessible (with Pro user)
- [ ] AI Coach sends/receives messages
- [ ] Free tier limit enforced (402 error on 2nd analysis)
- [ ] Stripe keys added (optional, for payments)

---

**You're ready to go! 🚀**

Run the migrations, start the servers, and you'll have a fully functional AI-powered career platform!
