# Premium Features Setup Guide

## Quick Start

This guide will help you set up and test the premium features: **Resume Studio**, **Career Coach**, and **Interviewer AI**.

---

## Prerequisites

1. **Python 3.11+**
2. **Google Gemini API Key**
3. **Supabase Account** (or use local PostgreSQL)

---

## Step 1: Environment Setup

### 1.1 Update `.env` File

Create or update `backend/.env`:

```env
# Google Gemini API (Required)
GEMINI_API_KEY=your_gemini_api_key_here

# Supabase (Required for premium features)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key

# App Config
ENVIRONMENT=development
DEBUG=True

# CORS
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:3001"]
```

### 1.2 Get Gemini API Key

1. Go to https://makersuite.google.com/app/apikey
2. Create new API key
3. Copy to `.env` file

### 1.3 Setup Supabase

1. Create account at https://supabase.com
2. Create new project
3. Go to Project Settings → API
4. Copy URL and keys to `.env`

---

## Step 2: Database Setup

### 2.1 Run Schema in Supabase

1. Open Supabase SQL Editor
2. Copy entire content from `database_schema.sql`
3. Execute the SQL
4. Verify tables were created:
   - `users`
   - `career_profiles`
   - `resume_artifacts`
   - `profile_suggestions`
   - `career_goals`
   - `interview_sessions`
   - `coach_conversations`
   - `subscriptions`

### 2.2 Create Test User

```sql
INSERT INTO public.users (email, firebase_uid, name)
VALUES ('test@example.com', 'test_uid_123', 'Test User');
```

---

## Step 3: Start Backend Server

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn app.main:app --reload --port 8000
```

You should see:
```
🚀 Starting NEXT Career Intelligence API...
Environment: development
✅ Using Supabase database
INFO:     Uvicorn running on http://127.0.0.1:8000
```

---

## Step 4: Test API Endpoints

### 4.1 Check Health

```bash
# Overall health
curl http://localhost:8000/api/health

# Resume Studio health
curl http://localhost:8000/api/resume-studio/health

# Career Coach health
curl http://localhost:8000/api/coach/health

# Interviewer AI health
curl http://localhost:8000/api/interviewer/health
```

### 4.2 Test Resume Studio

**Test 1: Ingest Resume**

```bash
curl -X POST http://localhost:8000/api/resume-studio/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "text": "JOHN DOE\nSenior Product Manager\n\nEXPERIENCE\n\nAcme Corp | Product Manager | Jan 2020 - Present\n- Led product strategy for B2B platform serving 500+ clients\n- Increased user engagement by 40% through data-driven feature prioritization\n- Managed cross-functional team of 12 (Engineering, Design, Marketing)\n\nPrevious Company | Associate PM | Jun 2018 - Dec 2019\n- Launched MVP in 8 weeks, achieving 10k users in first month\n- Conducted 50+ user interviews to inform product roadmap\n\nEDUCATION\nUniversity of State | BS Computer Science | 2018\n\nSKILLS\nProduct Management, Agile, JIRA, SQL, Data Analysis, Stakeholder Management",
    "user_id": "test_uid_123"
  }'
```

**Test 2: Tailor Resume**

```bash
curl -X POST http://localhost:8000/api/resume-studio/tailor \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_uid_123",
    "job_description": {
      "title": "Senior Product Manager",
      "company": "Tech Startup",
      "seniority": "Senior",
      "location": "Remote",
      "must_haves": ["Product strategy", "B2B SaaS", "Cross-functional leadership"],
      "nice_to_haves": ["Data analysis", "User research"],
      "keywords": ["roadmap", "OKRs", "user engagement", "stakeholder management"],
      "industry": "B2B SaaS",
      "region": "US"
    }
  }'
```

### 4.3 Test Career Coach

```bash
curl -X POST http://localhost:8000/api/coach/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_uid_123",
    "message": "I want to transition from product management to data science. What skills should I focus on?",
    "conversation_type": "skill_discovery"
  }'
```

### 4.4 Test Interviewer AI

**Start Interview:**
```bash
curl -X POST http://localhost:8000/api/interviewer/start \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_uid_123",
    "role_title": "Senior Product Manager",
    "company_name": "Tech Startup",
    "interview_type": "behavioral"
  }'
```

**Submit Answer (use session_id from above):**
```bash
curl -X POST http://localhost:8000/api/interviewer/answer \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "YOUR_SESSION_ID_HERE",
    "user_id": "test_uid_123",
    "question_index": 0,
    "answer": "At Acme Corp, I had to manage conflicting priorities between Engineering who wanted to delay for quality, and Sales who needed to meet a client deadline. I facilitated a meeting where we identified a minimum viable scope that satisfied both teams. We shipped on time with core features, then followed up with enhancements in the next sprint. The client was happy with 95% satisfaction score, and we maintained code quality with zero critical bugs."
  }'
```

---

## Step 5: Access API Documentation

Open in browser:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

You'll see all 30+ endpoints organized by tags:
- Health
- Analysis (existing)
- Jobs (existing)
- Users (existing)
- Resume Studio - Premium
- Career Coach - Premium
- Interviewer AI - Premium

---

## Step 6: Common Issues & Fixes

### Issue: "Gemini API error"

**Fix:**
1. Verify `GEMINI_API_KEY` in `.env`
2. Check API key is valid at https://makersuite.google.com/app/apikey
3. Ensure API key has proper permissions

### Issue: "Database unavailable"

**Fix:**
1. Check Supabase credentials in `.env`
2. Verify project is not paused in Supabase dashboard
3. Test connection:
   ```bash
   python3 -c "from app.db.supabase import test_supabase_connection; import asyncio; asyncio.run(test_supabase_connection())"
   ```

### Issue: "Profile not found"

**Fix:**
1. Create career profile first:
   ```sql
   INSERT INTO public.career_profiles (user_id, profile_data)
   VALUES ('test_uid_123', '{
     "basics": {},
     "work_history": [],
     "education": [],
     "skills": {"hard": [], "soft": [], "domains": []}
   }'::jsonb);
   ```

### Issue: Import errors

**Fix:**
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Verify imports
python3 -c "from app.services.prompts import get_prompt_set; print('OK')"
python3 -c "from app.models.premium_schemas import CoachRequest; print('OK')"
```

---

## Step 7: Architecture Overview

### Data Flow

```
1. Resume Studio (SSOT)
   ├─ Ingest: Parse resume → career_profile
   ├─ Tailor: JD → tailored resume
   └─ Apply: User confirms suggestion → update profile

2. Career Coach (Read-Only)
   ├─ Read: career_profile
   ├─ Chat: Generate coaching advice
   └─ Suggest: Create profile_suggestions (not applied)

3. Interviewer AI (Read-Only)
   ├─ Read: career_profile
   ├─ Interview: STAR questions → extract evidence
   └─ Suggest: Create profile_suggestions (not applied)

4. User Approval Flow
   User reviews suggestions → approves → Resume Studio applies
```

### Key Files

```
backend/
├── app/
│   ├── api/
│   │   ├── resume_studio.py     # Resume Studio endpoints
│   │   ├── coach.py              # Career Coach endpoints
│   │   └── interviewer.py        # Interviewer AI endpoints
│   ├── models/
│   │   ├── premium_schemas.py    # Pydantic schemas
│   │   └── resume_studio.py      # SQLAlchemy models (legacy)
│   ├── services/
│   │   ├── prompts.py            # System/Developer/Task prompts
│   │   └── gemini_analyzer.py    # Gemini API wrapper
│   ├── db/
│   │   └── supabase.py           # Supabase client
│   └── main.py                   # FastAPI app
├── requirements.txt
└── .env

database_schema.sql              # Full database schema
PREMIUM_API_DOCS.md             # Complete API documentation
PREMIUM_SETUP_GUIDE.md          # This file
```

---

## Step 8: Next Steps

### For Development

1. **Add Authentication**
   - Implement Firebase Auth middleware
   - Protect premium endpoints
   - Add user ID extraction from JWT

2. **Add Subscription Management**
   - Integrate Stripe
   - Create subscription middleware
   - Gate premium features by tier

3. **Improve Error Handling**
   - Add custom exception handlers
   - Implement retry logic
   - Add request logging

### For Production

1. **Security Hardening**
   - Enable HTTPS
   - Add rate limiting (Redis)
   - Implement CORS properly
   - Add input validation

2. **Performance Optimization**
   - Add caching (Redis)
   - Implement connection pooling
   - Optimize database queries
   - Add CDN for static assets

3. **Monitoring & Logging**
   - Set up Sentry for error tracking
   - Add structured logging
   - Implement metrics (Prometheus)
   - Set up health checks

---

## Testing Checklist

- [ ] Backend server starts without errors
- [ ] All health endpoints return 200
- [ ] Gemini API connection works
- [ ] Supabase connection works
- [ ] Resume ingestion works
- [ ] Resume tailoring works
- [ ] Cover letter generation works
- [ ] Career Coach chat works
- [ ] Interview session creation works
- [ ] Interview answer submission works
- [ ] Suggestions are saved to database
- [ ] Goals can be created and retrieved

---

## Support

For issues:
1. Check logs in terminal
2. Verify environment variables
3. Test database connection
4. Check Gemini API quota
5. Review PREMIUM_API_DOCS.md
6. Open GitHub issue

---

**Congratulations!** 🎉

You now have a fully functional premium career intelligence platform with:
- ✅ Resume Studio (AI-powered resume parsing & tailoring)
- ✅ Career Coach (Conversational AI coaching)
- ✅ Interviewer AI (STAR interview practice)
- ✅ Supabase database
- ✅ Google Gemini integration
- ✅ Safety & privacy guardrails

Ready to help users build AI-resilient careers!
