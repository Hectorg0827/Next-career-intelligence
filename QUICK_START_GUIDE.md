# 🚀 NEXT Career Intelligence - Quick Start Guide

**Last Updated:** 2025-01-10
**Purpose:** Get you from 0 to implementing core features in < 1 hour

---

## 📋 What You Have Now

✅ **48K+ lines of production code**
✅ **10 AI agents working**
✅ **38 API endpoints functional**
✅ **Jobs marketplace with AI matching**
✅ **Resume Studio, Career Coach, Interviewer AI**
✅ **Stripe subscriptions**
✅ **Complete roadmap (see IMPLEMENTATION_ROADMAP.md)**

---

## ⚡ Phase 1 Quick Wins (Do These First)

### 1. Apply Database Migrations (15 minutes)

#### A. Jobs Marketplace Schema
```bash
# 1. Open Supabase SQL Editor: https://app.supabase.com/project/YOUR_PROJECT/sql
# 2. Copy contents of APPLY_THIS_SQL.sql
# 3. Execute in SQL Editor
# 4. Verify: SELECT COUNT(*) FROM jobs;
```

#### B. RFT System Tables
```bash
# 1. In Supabase SQL Editor
# 2. Copy contents of backend/migrations/create_rft_tables.sql
# 3. Execute
# 4. Verify: SELECT * FROM rft_model_versions;
```

**Expected Result:** 3 tables created (rft_feedback, rft_model_versions, rft_training_jobs)

---

### 2. Start Neo4j Talent Graph (10 minutes)

```bash
# Start Neo4j + Redis
docker-compose -f docker-compose.neo4j.yml up -d

# Wait 30 seconds for startup
sleep 30

# Open Neo4j Browser
open http://localhost:7474

# Login: neo4j / next-career-password-2024

# In Neo4j Browser, paste contents of backend/neo4j/schema.cypher
# Execute each section (or all at once)

# Verify:
MATCH (n) RETURN labels(n) AS type, count(n) AS count;
# Should show: Skill (15), Role (5), Company (2)
```

**Expected Result:** Graph database with 22 nodes, ~30 relationships

---

### 3. Test Jobs Seeding (5 minutes)

```bash
# Start backend (if not running)
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn app.main:app --reload --port 8000

# In another terminal, test seeding
curl -X POST "http://localhost:8000/api/jobs/seed?count=10"

# Verify jobs created
curl "http://localhost:8000/api/jobs/search?limit=10" | jq '.jobs | length'
# Should return: 10
```

**Expected Result:** 10 jobs seeded successfully

---

## 🧠 Phase 2: Implement RFT System (2-3 hours)

### Step 1: Backend RFT API (30 minutes)

Create file: `backend/app/api/rft.py`

```python
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.core.supabase_client import supabase
from app.services.auth import get_current_user

router = APIRouter(prefix="/api/rft", tags=["rft"])

class RFTFeedbackCreate(BaseModel):
    event_type: str
    agent_name: str
    prompt: str
    model_output: str
    preferred_output: str | None = None
    user_rating: int | None = None
    user_accepted: bool | None = None
    context_data: dict = {}

@router.post("/feedback")
async def record_feedback(
    feedback: RFTFeedbackCreate,
    current_user = Depends(get_current_user)
):
    """Record user feedback for RFT training"""

    feedback_record = {
        "user_id": current_user.id,
        **feedback.dict()
    }

    response = supabase.table("rft_feedback").insert(feedback_record).execute()

    return {
        "status": "recorded",
        "feedback_id": response.data[0]["id"]
    }
```

Register in `backend/app/main.py`:
```python
from app.api import rft
app.include_router(rft.router)
```

---

### Step 2: Frontend RFT Tracker (30 minutes)

Create file: `frontend/src/lib/rft-tracker.ts`

```typescript
import { api } from './api'

export class RFTTracker {
  static async trackResumeBulletAccepted(data: {
    originalBullet: string
    aiRewrittenBullet: string
    jobDescription: string
  }) {
    await api.post('/api/rft/feedback', {
      event_type: 'resume_bullet_accepted',
      agent_name: 'resume_studio',
      prompt: `Job Description:\n${data.jobDescription}\n\nOriginal:\n${data.originalBullet}`,
      model_output: data.aiRewrittenBullet,
      preferred_output: data.aiRewrittenBullet,
      user_accepted: true,
      context_data: { job_description: data.jobDescription }
    })
  }

  static async trackResumeBulletRejected(data: {
    originalBullet: string
    aiRewrittenBullet: string
    userFinalEdit: string
    jobDescription: string
  }) {
    await api.post('/api/rft/feedback', {
      event_type: 'resume_bullet_rejected',
      agent_name: 'resume_studio',
      prompt: `Job Description:\n${data.jobDescription}\n\nOriginal:\n${data.originalBullet}`,
      model_output: data.aiRewrittenBullet,
      preferred_output: data.userFinalEdit,
      user_accepted: false,
      context_data: { job_description: data.jobDescription }
    })
  }

  static async trackInterviewAnswerRated(data: {
    question: string
    userAnswer: string
    aiFeedback: string
    userRating: 1 | 2 | 3 | 4 | 5
  }) {
    await api.post('/api/rft/feedback', {
      event_type: 'interview_answer_rated',
      agent_name: 'interviewer_ai',
      prompt: `Question:\n${data.question}\n\nAnswer:\n${data.userAnswer}`,
      model_output: data.aiFeedback,
      user_rating: data.userRating,
      context_data: {}
    })
  }
}
```

---

### Step 3: Integrate with Resume Studio (30 minutes)

Edit: `frontend/src/components/resume-studio/SuggestionsInbox.tsx`

```typescript
import { RFTTracker } from '@/lib/rft-tracker'

function SuggestionCard({ suggestion }: { suggestion: Suggestion }) {
  const handleAccept = async () => {
    // Apply the suggestion
    await applyBulletSuggestion(suggestion.id)

    // Track RFT feedback
    await RFTTracker.trackResumeBulletAccepted({
      originalBullet: suggestion.original,
      aiRewrittenBullet: suggestion.suggested,
      jobDescription: suggestion.jobDescription
    })

    toast.success("Suggestion applied!")
  }

  const handleReject = () => {
    // User rejected - do nothing
    toast.info("Suggestion dismissed")
  }

  const handleEdit = async (finalEdit: string) => {
    // User manually edited
    await RFTTracker.trackResumeBulletRejected({
      originalBullet: suggestion.original,
      aiRewrittenBullet: suggestion.suggested,
      userFinalEdit: finalEdit,
      jobDescription: suggestion.jobDescription
    })

    toast.success("Manual edit saved!")
  }

  return (
    <Card>
      {/* UI code */}
      <Button onClick={handleAccept}>Accept</Button>
      <Button onClick={handleReject}>Reject</Button>
    </Card>
  )
}
```

**Test:**
```bash
# 1. Go to Resume Studio
# 2. Upload resume
# 3. Paste job description
# 4. Click "Tailor Resume"
# 5. Accept or reject suggestions
# 6. Check database:

# In Supabase SQL Editor:
SELECT * FROM rft_feedback ORDER BY created_at DESC LIMIT 5;
```

**Expected Result:** Feedback events appear in `rft_feedback` table

---

## 🕸️ Phase 3: Neo4j Integration (2 hours)

### Step 1: Python Neo4j Client (30 minutes)

Already created! File: `backend/app/core/neo4j_client.py`

Copy this code:

```python
from neo4j import AsyncGraphDatabase
import os

class Neo4jClient:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "next-career-password-2024")
        self.driver = None

    async def connect(self):
        self.driver = AsyncGraphDatabase.driver(
            self.uri,
            auth=(self.user, self.password)
        )
        await self.driver.verify_connectivity()

    async def close(self):
        if self.driver:
            await self.driver.close()

    async def get_skill_gaps(self, user_id: str, target_role: str):
        async with self.driver.session() as session:
            result = await session.run(
                """
                MATCH (u:User {user_id: $user_id})
                MATCH (target:Role {title: $target_role})
                MATCH (target)-[req:REQUIRES_SKILL]->(s:Skill)
                WHERE NOT (u)-[:HAS_SKILL]->(s)
                RETURN s.name AS skill,
                       req.importance AS importance,
                       req.proficiency AS required_level
                ORDER BY req.importance DESC
                """,
                user_id=user_id,
                target_role=target_role
            )

            gaps = []
            async for record in result:
                gaps.append({
                    "skill": record["skill"],
                    "importance": record["importance"],
                    "required_level": record["required_level"]
                })

            return gaps

neo4j_client = Neo4jClient()
```

Add to `.env`:
```bash
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=next-career-password-2024
```

Register in `backend/app/main.py`:
```python
from app.core.neo4j_client import neo4j_client

@app.on_event("startup")
async def startup():
    await neo4j_client.connect()

@app.on_event("shutdown")
async def shutdown():
    await neo4j_client.close()
```

---

### Step 2: Talent Graph API (30 minutes)

Create file: `backend/app/api/talent_graph.py`

```python
from fastapi import APIRouter, Depends
from app.core.neo4j_client import neo4j_client
from app.services.auth import get_current_user

router = APIRouter(prefix="/api/talent-graph", tags=["talent_graph"])

@router.get("/users/me/skill-gap")
async def get_my_skill_gap(
    target_role: str,
    current_user = Depends(get_current_user)
):
    """Get skills user needs for target role"""

    # Get user's current skills from profile
    profile = await get_user_profile(current_user.id)

    # Create user node in Neo4j if not exists
    async with neo4j_client.driver.session() as session:
        await session.run(
            """
            MERGE (u:User {user_id: $user_id})
            SET u.current_role = $current_role
            """,
            user_id=current_user.id,
            current_role=profile.get("current_role")
        )

        # Link user's skills
        for skill in profile.get("skills", []):
            await session.run(
                """
                MATCH (u:User {user_id: $user_id})
                MERGE (s:Skill {name: $skill_name})
                MERGE (u)-[:HAS_SKILL]->(s)
                """,
                user_id=current_user.id,
                skill_name=skill
            )

    # Get skill gaps
    gaps = await neo4j_client.get_skill_gaps(current_user.id, target_role)

    return {
        "target_role": target_role,
        "skill_gaps": gaps,
        "total_gaps": len(gaps)
    }
```

Register in `backend/app/main.py`:
```python
from app.api import talent_graph
app.include_router(talent_graph.router)
```

**Test:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/talent-graph/users/me/skill-gap?target_role=Senior%20Software%20Engineer"
```

**Expected Result:**
```json
{
  "target_role": "Senior Software Engineer",
  "skill_gaps": [
    {"skill": "Leadership", "importance": 0.8, "required_level": "intermediate"},
    {"skill": "AWS", "importance": 0.8, "required_level": "intermediate"}
  ],
  "total_gaps": 2
}
```

---

### Step 3: Frontend Visualization (1 hour)

Create file: `frontend/src/components/talent-graph/SkillGapChart.tsx`

```typescript
import { useQuery } from '@tanstack/react-query'
import { RadarChart, Radar, PolarGrid, PolarAngleAxis } from 'recharts'

export function SkillGapChart({ targetRole }: { targetRole: string }) {
  const { data, isLoading } = useQuery({
    queryKey: ['skill-gap', targetRole],
    queryFn: () => api.get(`/talent-graph/users/me/skill-gap?target_role=${targetRole}`)
  })

  if (isLoading) return <Skeleton />

  const chartData = data.skill_gaps.map(gap => ({
    skill: gap.skill,
    importance: gap.importance * 100
  }))

  return (
    <Card className="p-6">
      <h3 className="text-lg font-semibold mb-4">
        Skills Needed for {targetRole}
      </h3>

      <RadarChart width={400} height={400} data={chartData}>
        <PolarGrid />
        <PolarAngleAxis dataKey="skill" />
        <Radar name="Importance" dataKey="importance" stroke="#8884d8" fill="#8884d8" fillOpacity={0.6} />
      </RadarChart>

      <div className="mt-4 space-y-2">
        {data.skill_gaps.map(gap => (
          <div key={gap.skill} className="flex justify-between">
            <span>{gap.skill}</span>
            <Badge>{gap.required_level}</Badge>
          </div>
        ))}
      </div>
    </Card>
  )
}
```

Add to dashboard: `frontend/src/app/dashboard/page.tsx`

```typescript
import { SkillGapChart } from '@/components/talent-graph/SkillGapChart'

export default function Dashboard() {
  return (
    <div className="grid grid-cols-2 gap-6">
      {/* Existing widgets */}

      <SkillGapChart targetRole="Senior Software Engineer" />
    </div>
  )
}
```

---

## 🎯 Phase 4: Deploy to Production (1 day)

### Backend: Google Cloud Run

```bash
# 1. Install Google Cloud SDK
brew install --cask google-cloud-sdk  # macOS
# or: https://cloud.google.com/sdk/docs/install

# 2. Login and set project
gcloud auth login
gcloud config set project next-career-intelligence

# 3. Build and push Docker image
cd backend
gcloud builds submit --tag gcr.io/next-career-intelligence/backend

# 4. Deploy to Cloud Run
gcloud run deploy next-backend \
  --image gcr.io/next-career-intelligence/backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="ENVIRONMENT=production" \
  --memory 2Gi \
  --cpu 2 \
  --max-instances 10

# 5. Get service URL
gcloud run services describe next-backend --region us-central1 --format 'value(status.url)'
```

---

### Frontend: Vercel

```bash
# 1. Install Vercel CLI
npm i -g vercel

# 2. Login
vercel login

# 3. Deploy from frontend directory
cd frontend
vercel

# Follow prompts:
# - Set up and deploy? Yes
# - Which scope? Your account
# - Link to existing project? No
# - Project name: next-career-intelligence
# - Directory: ./
# - Override settings? No

# 4. Set environment variables in Vercel dashboard
# https://vercel.com/your-project/settings/environment-variables

NEXT_PUBLIC_API_URL=https://YOUR-CLOUD-RUN-URL
NEXT_PUBLIC_FIREBASE_API_KEY=...
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=...

# 5. Redeploy with env vars
vercel --prod
```

---

## ✅ Success Checklist

After completing Quick Start, you should have:

- ✅ Jobs marketplace working with real schema
- ✅ RFT system collecting feedback data
- ✅ Neo4j Talent Graph running locally
- ✅ Skill gap analysis functional
- ✅ (Optional) Production deployment live

---

## 🆘 Troubleshooting

### Problem: Neo4j won't start
```bash
# Check Docker logs
docker-compose -f docker-compose.neo4j.yml logs neo4j

# Common fix: Clean volumes and restart
docker-compose -f docker-compose.neo4j.yml down -v
docker-compose -f docker-compose.neo4j.yml up -d
```

### Problem: RFT feedback not saving
```bash
# Check if table exists
# In Supabase SQL Editor:
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'rft_feedback';

# If empty, re-run migration
```

### Problem: Frontend can't reach backend
```bash
# Check NEXT_PUBLIC_API_URL in .env.local
# Should be: http://localhost:8000 (development)
# or: https://your-cloud-run-url (production)
```

### Problem: Type errors in frontend
```bash
# Regenerate API types
cd backend && uvicorn app.main:app --port 8000 &
sleep 5
curl http://localhost:8000/openapi.json > /tmp/openapi.json
cd ../frontend
npx openapi-typescript /tmp/openapi.json --output src/types/api.ts
```

---

## 📚 Next Steps

After Quick Start, continue with:

1. **Week 1-2:** Complete Phase 1 tasks in IMPLEMENTATION_ROADMAP.md
2. **Week 3-4:** Build job scrapers for real data
3. **Week 5-6:** Email notifications + goal automation
4. **Week 7-8:** Production hardening + testing

---

## 🎉 You're Ready to Build!

You now have:
- ✅ Complete understanding of the codebase
- ✅ Strategic roadmap for 8 weeks
- ✅ RFT and Neo4j infrastructure ready
- ✅ Clear path to production launch

**Questions?** Refer to:
- `IMPLEMENTATION_ROADMAP.md` - Detailed 8-week plan
- `EXECUTION_SUMMARY.md` - Current status & recommendations
- `APPLY_THIS_SQL.sql` - Database schema
- `backend/neo4j/schema.cypher` - Graph database schema

**Let's ship V2.0!** 🚀
