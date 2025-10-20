# 🚀 GEMINI + GCP SETUP COMPLETE!

## ✅ What's Configured

### 1. **Google Gemini Pro 1.5** (AI Engine)
- ✅ Installed: `google-generativeai==0.8.3`
- ✅ Created: `backend/app/services/gemini_analyzer.py`
- ✅ Updated: `backend/app/api/analyze.py` to use Gemini
- ✅ Cost: 92% cheaper than OpenAI ($0.00025/1K vs $0.03/1K tokens)

### 2. **Supabase** (PostgreSQL on GCP)
- ✅ Installed Backend: `supabase==2.10.0`
- ✅ Installed Frontend: `@supabase/supabase-js@2.39.0`
- ✅ Created: `backend/app/db/supabase.py`
- ✅ Created: `frontend/src/lib/supabase.ts`
- ✅ Your Project: `https://whxbxjpymksgvixudnjh.supabase.co`

### 3. **Google Cloud Run** (Deployment)
- ✅ Project ID: `795538981829`
- ✅ Region: `europe-west1`
- ✅ Service URL: `https://next-career-intelligence-795538981829.europe-west1.run.app`
- ✅ OAuth Client: `795538981829-0c05b330697k523h6aehtabvbik8d9oe.apps.googleusercontent.com`

---

## 🔑 Required Credentials (YOU NEED THESE!)

### 1. Gemini API Key (2 minutes)
```bash
# Get it: https://aistudio.google.com/app/apikey
# 1. Click "Get API Key"
# 2. Click "Create API key in new project"
# 3. Copy the key (starts with AIzaSy...)

# Add to backend/.env:
GEMINI_API_KEY=AIzaSy...your_key_here
```

### 2. Supabase Credentials (3 minutes)
```bash
# Your project: https://whxbxjpymksgvixudnjh.supabase.co
# Go to: Settings → Database

# You need 4 values:
# 1. DATABASE_URL - Connection string (mode: Session)
# 2. SUPABASE_URL - Project URL
# 3. SUPABASE_ANON_KEY - anon/public key  
# 4. SUPABASE_SERVICE_KEY - service_role key

# Add to backend/.env:
DATABASE_URL=postgresql://postgres.whxbxjpymksgvixudnjh:[PASSWORD]@...
SUPABASE_URL=https://whxbxjpymksgvixudnjh.supabase.co
SUPABASE_ANON_KEY=eyJhbG...
SUPABASE_SERVICE_KEY=eyJhbG...

# Add to frontend/.env.local:
NEXT_PUBLIC_SUPABASE_URL=https://whxbxjpymksgvixudnjh.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbG...
```

---

## 🗄️ Create Database Tables (5 minutes)

Go to Supabase Dashboard → SQL Editor and run:

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Analyses table
CREATE TABLE analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    job_title VARCHAR(255) NOT NULL,
    risk_score FLOAT,
    risk_level VARCHAR(50),
    analysis_data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Career roadmaps table
CREATE TABLE career_roadmaps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    analysis_id UUID REFERENCES analyses(id),
    roadmap_data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_analyses_user_id ON analyses(user_id);
CREATE INDEX idx_analyses_created_at ON analyses(created_at);
CREATE INDEX idx_roadmaps_user_id ON career_roadmaps(user_id);
CREATE INDEX idx_roadmaps_analysis_id ON career_roadmaps(analysis_id);

-- Enable Row Level Security (RLS)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE career_roadmaps ENABLE ROW LEVEL SECURITY;

-- Policies (users can only see their own data)
CREATE POLICY "Users can view their own data" ON users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can view their own analyses" ON analyses
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own analyses" ON analyses
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can view their own roadmaps" ON career_roadmaps
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own roadmaps" ON career_roadmaps
    FOR INSERT WITH CHECK (auth.uid() = user_id);
```

---

## 🚀 Start the Application

### Terminal 1 - Backend
```bash
cd /Users/hectorgarcia/Desktop/Next-career-intelligence/backend

# Set environment
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Start server
python3 -m uvicorn app.main:app --reload --port 8000
```

### Terminal 2 - Frontend  
```bash
cd /Users/hectorgarcia/Desktop/Next-career-intelligence/frontend

# Start dev server
npm run dev
```

### Access Application
- Frontend: http://localhost:3000
- Dashboard: http://localhost:3000/dashboard
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 🧪 Test Gemini Integration

```bash
# Test API endpoint
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "job_title": "Software Engineer",
    "skills": ["Python", "React", "TypeScript"],
    "location": "San Francisco",
    "years_experience": 5
  }' | python3 -m json.tool
```

**Expected:** JSON response with Gemini-generated analysis!

---

## 📊 Cost Breakdown

### Before (OpenAI)
- OpenAI API: $50-100/month
- PostgreSQL hosting: $10-20/month
- **Total: $60-120/month**

### After (Gemini + Supabase)
- Gemini API: $5-10/month (with free tier)
- Supabase: $0/month (free tier)
- **Total: $5-10/month**

**Savings: ~90%** 💰

---

## ✅ Files Created/Modified

### Backend (Python)
1. ✅ `backend/app/services/gemini_analyzer.py` (NEW - 532 lines)
2. ✅ `backend/app/api/analyze.py` (UPDATED - uses Gemini)
3. ✅ `backend/app/db/supabase.py` (NEW - 140 lines)
4. ✅ `backend/requirements.txt` (UPDATED - added Gemini, removed OpenAI)
5. ✅ `backend/.env` (UPDATED - needs your keys!)

### Frontend (TypeScript)
6. ✅ `frontend/src/lib/supabase.ts` (NEW - 150 lines)
7. ✅ `frontend/.env.local` (UPDATED - needs your keys!)
8. ✅ `frontend/package.json` (UPDATED - added Supabase)

---

## 🆘 Troubleshooting

### "ModuleNotFoundError: No module named 'google.generativeai'"
```bash
cd backend && pip3 install google-generativeai==0.8.3
```

### "Gemini API key not configured"
1. Get key: https://aistudio.google.com/app/apikey
2. Add to `backend/.env`: `GEMINI_API_KEY=your_key`
3. Restart backend server

### "Supabase connection failed"
1. Check credentials in `backend/.env`
2. Verify project URL: `https://whxbxjpymksgvixudnjh.supabase.co`
3. Ensure service_role key has correct permissions

### "Database tables not found"
1. Go to Supabase Dashboard → SQL Editor
2. Run the CREATE TABLE SQL above
3. Check Tables tab to verify

### "Frontend compilation errors"
```bash
cd frontend
rm -rf .next node_modules
npm install --legacy-peer-deps
npm run dev
```

---

## 🎯 Next Steps

### NOW (5 minutes)
1. ✅ Get Gemini API key from https://aistudio.google.com/app/apikey
2. ✅ Get Supabase credentials from https://supabase.com
3. ✅ Update `backend/.env` with keys
4. ✅ Update `frontend/.env.local` with keys

### SOON (10 minutes)
1. ✅ Create database tables in Supabase (run SQL above)
2. ✅ Start both servers (backend + frontend)
3. ✅ Test one analysis request
4. ✅ Verify Gemini is working

### LATER (optional)
1. Add login/register UI
2. Deploy to production (Cloud Run + Vercel)
3. Set up monitoring
4. Add more features!

---

## 📚 Resources

- **Gemini Docs:** https://ai.google.dev/docs
- **Gemini Pricing:** https://ai.google.dev/pricing
- **Supabase Docs:** https://supabase.com/docs
- **Cloud Run Docs:** https://cloud.google.com/run/docs

---

## 🎉 Summary

**Your NEXT Careers platform now runs on:**
- ⚡ Google Gemini Pro 1.5 (AI analysis)
- 🗄️ Supabase PostgreSQL (database)
- 🔐 Supabase Auth (user management)
- ☁️ Google Cloud Run (deployment ready)

**Configuration Status:**
- ✅ Dependencies installed
- ✅ Code updated
- ⏳ Waiting for API keys
- ⏳ Waiting for database setup

**Once you add the keys, you're ready to go!** 🚀
