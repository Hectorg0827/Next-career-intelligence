# Quick Reference: Supabase & SendGrid Setup

## 🚀 5-Step Quick Start

### Step 1: Backend Credentials (10 min)
```bash
# Navigate to Supabase and create project
# Get from: Settings → API
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_SERVICE_KEY="eyJhbGc..."

# Navigate to SendGrid and create API key
# Get from: Settings → API Keys
export SENDGRID_API_KEY="SG.your-key-here"

# Create backend/.env
cd backend
cat > .env << 'EOF'
SUPABASE_URL=$SUPABASE_URL
SUPABASE_SERVICE_KEY=$SUPABASE_SERVICE_KEY
SENDGRID_API_KEY=$SENDGRID_API_KEY
SENDGRID_FROM_EMAIL=noreply@nextcareer.ai
APP_URL=http://localhost:3000
API_URL=http://localhost:8000
EOF
```

### Step 2: Database Setup (5 min)
```sql
-- In Supabase SQL Editor, run the 4 scripts from:
-- SUPABASE_SENDGRID_SETUP.md → Section "5. Create Supabase Tables"

-- Run ONE AT A TIME and wait after each:
-- 1. Users Table (drops old tables first)
-- 2. Verification Codes Table
-- 3. Password Resets Table
-- 4. Onboarding Table
```

### Step 3: Frontend Credentials (5 min)
```bash
# Create frontend/.env.local
cd ../frontend
cat > .env.local << 'EOF'
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGc...
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF
```

### Step 4: Start Services (5 min)
```bash
# Terminal 1: Backend
cd backend
python3 -m uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev

# Access:
# Backend API: http://localhost:8000
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

### Step 5: DNS Setup (15 min - mostly waiting)
```bash
# Add these 6 records to your domain registrar:
# (See SENDGRID_DNS_SETUP.md for exact values)

# 5 CNAME records
url1859.nextci.com → sendgrid.net
56863448.nextci.com → sendgrid.net
em1249.nextci.com → u56863448.wl199.sendgrid.net
s1._domainkey.nextci.com → s1.domainkey.u56863448.wl199.sendgrid.net
s2._domainkey.nextci.com → s2.domainkey.u56863448.wl199.sendgrid.net

# 1 TXT record
_dmarc.nextci.com → v=DMARC1; p=none;

# Wait 15-30 minutes for DNS propagation
# Verify in SendGrid Dashboard → Settings → Sender Authentication
```

---

## 🔑 Credential Reference

### Backend .env
```bash
# Supabase (get from Settings → API)
SUPABASE_URL=https://your-project.supabase.co          # Project URL
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1Ni...            # Service role key

# SendGrid (get from Settings → API Keys)
SENDGRID_API_KEY=SG.your-api-key-here                  # API key

# URLs
APP_URL=http://localhost:3000                          # Frontend
API_URL=http://localhost:8000                          # Backend
```

### Frontend .env.local
```bash
# Supabase (get from Settings → API)
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co     # Project URL
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1Ni...           # Anon key

# Backend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

⚠️ **KEY DIFFERENCE**:
- Backend uses `SUPABASE_SERVICE_KEY` (admin access)
- Frontend uses `NEXT_PUBLIC_SUPABASE_ANON_KEY` (restricted access)

---

## 🧪 Testing Checklist

### Test 1: Backend API
```bash
# Health check
curl http://localhost:8000/api/health

# Expected: {"status": "healthy", ...}
```

### Test 2: Signup
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "full_name": "Test User",
    "password": "TestPass123"
  }'

# Expected: {"success": true, "user_id": "...", ...}
# Check email inbox for 6-digit verification code
```

### Test 3: Verify Email
```bash
curl -X POST http://localhost:8000/api/auth/verify-email \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "verification_code": "123456"
  }'

# Expected: {"success": true, ...}
# Check email inbox for welcome email
```

### Test 4: Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123"
  }'

# Expected: {"success": true, "access_token": "...", ...}
```

### Test 5: Onboarding
```bash
curl -X POST http://localhost:8000/api/onboarding/complete \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer USER_ID" \
  -d '{
    "current_role": "Software Engineer",
    "industry": "tech",
    "years_experience": "5-10",
    "skills": ["Python", "React"],
    "goals": ["Become CTO"],
    "learning_style": "videos"
  }'

# Expected: {"success": true, "learning_path_id": "...", ...}
```

### Test 6: Verify in Supabase
1. Go to Supabase Dashboard
2. Click Table Editor
3. Should see:
   - New user in `users` table
   - Verification code in `verification_codes` table (is_used = true)
   - Onboarding data in `onboarding` table

---

## 📚 Documentation Files

| File | Purpose | Read Time |
|------|---------|-----------|
| SUPABASE_SENDGRID_SETUP.md | Complete backend setup | 30 min |
| FRONTEND_SUPABASE_SETUP.md | Frontend integration | 15 min |
| SENDGRID_DNS_SETUP.md | Email deliverability | 15 min |
| SUPABASE_FIX_EXISTING_SETUP.md | Troubleshooting errors | 10 min |

---

## 🆘 Common Errors & Fixes

### Error: "NEXT_PUBLIC_SUPABASE_ANON_KEY is not set"
**Fix**: Create `frontend/.env.local` with the variable

### Error: "policy already exists"
**Fix**: See SUPABASE_FIX_EXISTING_SETUP.md → Run DROP TABLE IF EXISTS

### Error: "Connection refused" on localhost:8000
**Fix**: Backend not running. Start with: `python3 -m uvicorn app.main:app --reload`

### Error: "Email not sent"
**Fix**: DNS not verified yet. Wait 15-30 min or check SENDGRID_DNS_SETUP.md

### Error: "Invalid API key"
**Fix**: Wrong key type:
- ✅ Backend: Use `SERVICE_KEY` (not anon key)
- ✅ Frontend: Use `ANON_KEY` (not service key)

---

## ⚡ Quick Commands

```bash
# Install dependencies
pip install -r backend/requirements.txt  # Python
npm install                              # Node (in frontend/)

# Start services
python3 -m uvicorn app.main:app --reload      # Backend
npm run dev                                    # Frontend
docker-compose up                              # All services

# Check if running
curl http://localhost:8000/api/health  # Backend
curl http://localhost:3000             # Frontend

# View logs
ps aux | grep uvicorn   # Check backend process
ps aux | grep node      # Check frontend process

# Kill services
lsof -ti:8000 | xargs kill -9   # Kill backend
lsof -ti:3000 | xargs kill -9   # Kill frontend
```

---

## 📊 Architecture Overview

```
Frontend (Next.js)              Backend (FastAPI)           Database (PostgreSQL)
┌──────────────────┐           ┌────────────────────┐      ┌──────────────────┐
│  Auth Component  │           │  /api/auth/signup  │      │  users table     │
│  Onboarding Flow │──POST────→│  /api/auth/login   │─────→│  ver_codes table │
│  Dashboard       │           │  /api/onboarding/* │      │  pass_resets table
│ .env.local       │           │  /api/analyze      │      │  onboarding table
│ (anon_key)       │           │ .env (service_key) │      │                   │
└──────────────────┘           └────────────────────┘      └──────────────────┘
        │                               │                            │
        │                               │                            │
        └───────────────────────────────┴────────────────────────────┘
                      HTTP/REST & Supabase SDK
```

---

## ✅ Final Checklist

Before calling it done:

- [ ] Backend .env created with Supabase + SendGrid credentials
- [ ] Frontend .env.local created with Supabase ANON_KEY
- [ ] 4 Supabase tables created and visible in dashboard
- [ ] Backend server running (port 8000)
- [ ] Frontend dev server running (port 3000)
- [ ] DNS records added to domain registrar (6 records)
- [ ] DNS propagation verified
- [ ] Signup → Verify → Login flow tested
- [ ] Onboarding flow tested
- [ ] Email verification code received
- [ ] Welcome email received
- [ ] Data visible in Supabase dashboard

---

## 🚀 You're Ready!

All code is production-ready. Just need to:
1. Add credentials
2. Create database tables
3. Verify DNS
4. Test the flows

**Estimated time: 75 minutes**

After that: Full-stack authentication, email, and onboarding system ready! 🎉
