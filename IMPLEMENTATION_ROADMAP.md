# 🚀 NEXT Career Intelligence - Implementation Roadmap

**Document Version:** 2.0
**Last Updated:** 2025-01-10
**Status:** Active Development

---

## 📋 Executive Summary

This roadmap bridges the gap between your **current implementation** (48K+ lines, 10 AI agents, working jobs marketplace) and the **V2.0 "Career Command Center" specification** with strategic moats (Neo4j Talent Graph + RFT System).

**Timeline Overview:**
- **Phase 1 (Weeks 1-2):** Fix Current Issues & Quick Wins
- **Phase 2 (Weeks 3-4):** Core Moat Features (RFT + Neo4j)
- **Phase 3 (Weeks 5-6):** Data Pipeline & Automation
- **Phase 4 (Weeks 7-8):** Production Readiness
- **Total Estimated Time:** 8 weeks to full V2.0 launch

---

## 🎯 Strategic Priorities

### Moat Features (Competitive Advantage)
1. **Neo4j Talent Graph** - Proprietary skills relationship data
2. **RFT Agent System** - Self-improving AI that learns from user success
3. **Career Health Score** - Persistent metric for retention

### Growth Features (User Acquisition & Retention)
4. **Real Job Data** - Scrapers for Greenhouse, Lever, Indeed
5. **Goal-Based Automation** - Intelligent job filtering
6. **Email Notifications** - Re-engagement system

### Foundation (Technical Excellence)
7. **Type Safety Pipeline** - Eliminate FE/BE integration errors
8. **Production Deployment** - Cloud Run + Vercel
9. **Monitoring & Observability** - Full telemetry

---

## 📦 Phase 1: Fix & Stabilize (Weeks 1-2)

**Goal:** Clean up current issues, complete half-finished features, ensure solid foundation.

### Week 1: Critical Fixes

#### 1.1 Jobs Marketplace Cleanup ✅
**Status:** In Progress (modified files in git)
**Files:** `jobs_marketplace.py`, `job_seeder.py`

**Tasks:**
- [x] Remove SQL query accidentally added to Python file
- [ ] Apply schema changes from `APPLY_THIS_SQL.sql` to Supabase
- [ ] Test job seeding without employers table dependency
- [ ] Verify all 6 job endpoints work correctly
- [ ] Add error handling for missing salary data

**Acceptance Criteria:**
- `POST /api/jobs/seed?count=50` successfully creates 50 jobs
- No database constraint errors
- All jobs have required fields populated

**Estimated Time:** 4 hours

---

#### 1.2 Type Safety Enforcement
**Priority:** High (prevents integration bugs)

**Current State:**
- `openapi-typescript` is installed but not enforced
- FE/BE type mismatches are possible

**Implementation:**
```bash
# backend/scripts/generate-types.sh
#!/bin/bash
set -e

echo "🔄 Starting FastAPI server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
SERVER_PID=$!

# Wait for server to be ready
sleep 5

echo "📥 Fetching OpenAPI schema..."
curl http://localhost:8000/openapi.json > /tmp/openapi.json

echo "🔨 Generating TypeScript types..."
npx openapi-typescript /tmp/openapi.json --output ../frontend/src/types/api.ts

echo "🛑 Stopping server..."
kill $SERVER_PID

echo "✅ Types generated successfully!"
```

**CI/CD Integration:**
```yaml
# .github/workflows/type-safety.yml
name: Type Safety Check

on: [pull_request]

jobs:
  check-types:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node
        uses: actions/setup-node@v3
      - name: Setup Python
        uses: actions/setup-python@v4
      - name: Generate Types
        run: |
          cd backend && pip install -r requirements.txt
          cd .. && bash backend/scripts/generate-types.sh
      - name: Check for Type Changes
        run: |
          if git diff --exit-code frontend/src/types/api.ts; then
            echo "✅ Types are in sync"
          else
            echo "❌ Type mismatch detected!"
            git diff frontend/src/types/api.ts
            exit 1
          fi
```

**Update Frontend API Client:**
```typescript
// frontend/src/lib/api.ts
import type { paths } from '@/types/api'
import createClient from 'openapi-fetch'

const client = createClient<paths>({ baseUrl: process.env.NEXT_PUBLIC_API_URL })

// Now all API calls are type-safe!
export async function getJobRecommendations(userId: string) {
  const { data, error } = await client.GET('/api/jobs/recommendations', {
    params: { query: { user_id: userId } }
  })
  // TypeScript knows the exact shape of data!
  return data
}
```

**Acceptance Criteria:**
- Type generation script runs successfully
- GitHub Action fails on type mismatch
- Frontend uses generated types for all API calls
- No manual type definitions for API responses

**Estimated Time:** 6 hours

---

#### 1.3 Empty State Handling
**Priority:** Medium (prevents churn)

**Issue:** New users may see blank dashboards after signup.

**Implementation:**

1. **Onboarding Completion Hook:**
```python
# backend/app/api/onboarding.py
@router.post("/complete")
async def complete_onboarding(user_id: str, onboarding_data: OnboardingComplete):
    # Save onboarding data
    await save_user_onboarding(user_id, onboarding_data)

    # Generate initial Action Plan
    initial_actions = await generate_initial_action_plan(
        target_role=onboarding_data.target_role,
        experience_level=onboarding_data.experience_level,
        top_goal=onboarding_data.top_goal
    )

    # Create initial Career Health Score
    initial_chs = calculate_initial_chs(onboarding_data)

    return {
        "onboarding_complete": True,
        "initial_action_plan": initial_actions,
        "career_health_score": initial_chs
    }
```

2. **Dashboard Empty State Component:**
```typescript
// frontend/src/components/dashboard/EmptyState.tsx
export function DashboardEmptyState({ user }: { user: User }) {
  const hasCompletedOnboarding = user.onboarding_completed

  if (!hasCompletedOnboarding) {
    return <OnboardingPrompt />
  }

  return (
    <div className="text-center py-12">
      <Sparkles className="w-16 h-16 mx-auto text-purple-500 mb-4" />
      <h2 className="text-2xl font-bold mb-2">Welcome to Your Career Command Center!</h2>
      <p className="text-gray-600 mb-6">Let's get started with your first action</p>
      <div className="grid grid-cols-3 gap-4 max-w-2xl mx-auto">
        <QuickAction icon={FileText} title="Upload Resume" href="/resume-studio/upload" />
        <QuickAction icon={Target} title="Set Goals" href="/coach/goals" />
        <QuickAction icon={Briefcase} title="Find Jobs" href="/jobs/recommendations" />
      </div>
    </div>
  )
}
```

**Acceptance Criteria:**
- New user never sees completely blank dashboard
- Onboarding data populates initial CHS and action plan
- Clear CTAs guide user to first valuable action

**Estimated Time:** 4 hours

---

### Week 2: Quick Wins

#### 1.4 Career Health Score (CHS) Implementation
**Priority:** High (core retention metric)

**Formula:**
```python
def calculate_career_health_score(user: User, profile: CareerProfile) -> int:
    """
    Career Health Score (1-100)

    Weights:
    - Profile Completeness: 25%
    - Skill Currency: 25%
    - Market Activity: 20%
    - Goal Progress: 20%
    - Network Strength: 10%
    """
    score = 0

    # 1. Profile Completeness (25 points)
    profile_fields = ['resume', 'skills', 'experience', 'education', 'certifications']
    filled_fields = sum(1 for field in profile_fields if getattr(profile, field))
    score += (filled_fields / len(profile_fields)) * 25

    # 2. Skill Currency (25 points)
    # Check if skills match current market demand
    skill_recency_score = await check_skill_market_demand(profile.skills)
    score += skill_recency_score * 25

    # 3. Market Activity (20 points)
    # Recent applications, interviews, networking
    days_since_last_activity = (datetime.now() - profile.last_activity).days
    activity_score = max(0, 1 - (days_since_last_activity / 30))  # Decay over 30 days
    score += activity_score * 20

    # 4. Goal Progress (20 points)
    goals = await get_user_goals(user.id)
    if goals:
        completed = sum(1 for g in goals if g.status == 'completed')
        score += (completed / len(goals)) * 20

    # 5. Network Strength (10 points)
    # LinkedIn connections, referrals, etc.
    network_score = min(1.0, profile.linkedin_connections / 500)
    score += network_score * 10

    return int(score)
```

**Backend API:**
```python
@router.get("/users/me/career-health-score")
async def get_career_health_score(current_user: User = Depends(get_current_user)):
    profile = await get_user_profile(current_user.id)
    chs = await calculate_career_health_score(current_user, profile)

    # Get breakdown for UI
    breakdown = {
        "overall_score": chs,
        "profile_completeness": calculate_profile_completeness(profile),
        "skill_currency": await calculate_skill_currency(profile),
        "market_activity": calculate_market_activity(profile),
        "goal_progress": await calculate_goal_progress(current_user.id),
        "recommendations": generate_chs_recommendations(chs, profile)
    }

    return breakdown
```

**Frontend Widget:**
```typescript
// frontend/src/components/dashboard/CareerHealthScore.tsx
export function CareerHealthScoreWidget() {
  const { data: chs } = useQuery({
    queryKey: ['career-health-score'],
    queryFn: () => api.get('/users/me/career-health-score')
  })

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Career Health Score</h3>
        <Badge variant={getScoreVariant(chs.overall_score)}>
          {getScoreLabel(chs.overall_score)}
        </Badge>
      </div>

      <div className="relative h-40 mb-6">
        <CircularProgress value={chs.overall_score} />
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <div className="text-4xl font-bold">{chs.overall_score}</div>
            <div className="text-sm text-gray-500">out of 100</div>
          </div>
        </div>
      </div>

      <div className="space-y-2">
        {Object.entries(chs.breakdown).map(([key, value]) => (
          <div key={key} className="flex items-center justify-between">
            <span className="text-sm">{formatLabel(key)}</span>
            <div className="flex items-center gap-2">
              <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-purple-500 to-blue-500"
                  style={{ width: `${value}%` }}
                />
              </div>
              <span className="text-sm font-medium">{value}%</span>
            </div>
          </div>
        ))}
      </div>

      <Button className="w-full mt-4" onClick={() => router.push('/improve-score')}>
        Improve Score
      </Button>
    </Card>
  )
}
```

**Acceptance Criteria:**
- CHS visible on dashboard for all users
- Score updates in real-time based on user actions
- Breakdown shows which areas need improvement
- Recommendations are actionable and specific

**Estimated Time:** 8 hours

---

#### 1.5 Goal-Based Job Filtering
**Priority:** High (improves retention)

**Implementation:**

1. **Backend Goal-Job Matching:**
```python
# backend/app/services/goal_matcher.py
class GoalMatcher:
    async def filter_jobs_by_goals(
        self,
        user_id: str,
        jobs: List[Job]
    ) -> List[JobWithGoalMatch]:
        """Filter and rank jobs based on user's active goals"""

        goals = await get_active_goals(user_id)
        if not goals:
            return jobs  # No filtering if no goals

        scored_jobs = []
        for job in jobs:
            goal_scores = []

            for goal in goals:
                score = self._score_job_for_goal(job, goal)
                goal_scores.append({
                    "goal_id": goal.id,
                    "goal_title": goal.title,
                    "match_score": score,
                    "match_reasons": self._explain_match(job, goal)
                })

            # Average goal match score
            avg_score = sum(s["match_score"] for s in goal_scores) / len(goal_scores)

            scored_jobs.append({
                **job.dict(),
                "goal_alignment_score": avg_score,
                "goal_matches": goal_scores
            })

        # Sort by goal alignment
        scored_jobs.sort(key=lambda x: x["goal_alignment_score"], reverse=True)

        return scored_jobs

    def _score_job_for_goal(self, job: Job, goal: Goal) -> float:
        """Score 0-100 how well a job aligns with a goal"""

        score = 0.0

        # Goal type: "get_job"
        if goal.goal_type == "get_job":
            if goal.target_role and goal.target_role.lower() in job.title.lower():
                score += 50
            if goal.target_company and goal.target_company.lower() in job.company.lower():
                score += 30
            if goal.target_salary and job.salary_max >= goal.target_salary:
                score += 20

        # Goal type: "learn_skill"
        elif goal.goal_type == "learn_skill":
            if goal.target_skill in job.skills_extracted:
                score += 60  # Job uses the skill they want to learn

        # Goal type: "get_promotion"
        elif goal.goal_type == "get_promotion":
            current_seniority = goal.current_seniority or "mid"
            if self._is_promotion(current_seniority, job.seniority):
                score += 70

        # Goal type: "switch_industry"
        elif goal.goal_type == "switch_industry":
            if goal.target_industry and goal.target_industry in job.description:
                score += 60

        return min(100, score)
```

2. **Update Recommendations Endpoint:**
```python
@router.get("/jobs/recommendations")
async def get_job_recommendations(
    user_id: str,
    filter_by_goals: bool = True,
    limit: int = 20
):
    # Get AI-matched jobs (existing logic)
    matched_jobs = await job_matcher.get_recommendations(user_id, limit=limit*2)

    # Apply goal-based filtering
    if filter_by_goals:
        goal_matcher = GoalMatcher()
        matched_jobs = await goal_matcher.filter_jobs_by_goals(user_id, matched_jobs)

    return matched_jobs[:limit]
```

3. **Track Goal Progress on Application:**
```python
@router.post("/jobs/apply")
async def apply_to_job(application: JobApplication):
    # Create application record
    app_id = await create_application(application)

    # Check if job aligns with any goals
    goals = await get_active_goals(application.user_id)
    for goal in goals:
        if goal_aligns_with_job(goal, application.job_id):
            await increment_goal_progress(goal.id, progress=10)
            await create_notification(
                user_id=application.user_id,
                message=f"Great! This application moves you closer to: {goal.title}",
                type="goal_progress"
            )

    return {"application_id": app_id}
```

**Acceptance Criteria:**
- Jobs are ranked by goal alignment
- UI shows why a job matches user's goals
- Applying to aligned jobs increments goal progress
- Users can filter recommendations by specific goals

**Estimated Time:** 6 hours

---

## 🧠 Phase 2: Core Moat Features (Weeks 3-4)

**Goal:** Implement the two strategic moats from the spec.

### Week 3: RFT (Reinforcement Fine-Tuning) System

#### 2.1 RFT Infrastructure Setup
**Priority:** Critical (core competitive advantage)

**Architecture:**
```
User Action → Frontend Event → Backend Queue → RFT Feedback Table → Weekly Batch Job → Fine-Tuned Model
```

**Database Schema:**
```sql
-- backend/migrations/add_rft_tables.sql

-- RFT Feedback Events
CREATE TABLE IF NOT EXISTS rft_feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),

    -- Event metadata
    event_type VARCHAR(50) NOT NULL,  -- 'resume_bullet_accepted', 'interview_answer_rated', 'application_status_updated'
    agent_name VARCHAR(50) NOT NULL,  -- 'resume_studio', 'interviewer_ai', etc.

    -- Input/Output pairs for training
    prompt TEXT NOT NULL,
    model_output TEXT NOT NULL,
    preferred_output TEXT,  -- NULL if user accepted model output

    -- Feedback signal
    user_rating INTEGER CHECK (user_rating >= 1 AND user_rating <= 5),
    user_accepted BOOLEAN,

    -- Context
    context_data JSONB,  -- Job description, user profile snapshot, etc.

    -- Success metrics (for ultimate reward signal)
    led_to_interview BOOLEAN DEFAULT false,
    led_to_offer BOOLEAN DEFAULT false,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_rft_feedback_event_type ON rft_feedback(event_type);
CREATE INDEX idx_rft_feedback_agent_name ON rft_feedback(agent_name);
CREATE INDEX idx_rft_feedback_created_at ON rft_feedback(created_at DESC);

-- RFT Model Versions
CREATE TABLE IF NOT EXISTS rft_model_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_name VARCHAR(50) NOT NULL,
    model_name VARCHAR(100) NOT NULL,  -- e.g., 'gemini-1.5-pro-RFT-v1'

    -- Training metadata
    trained_on_feedback_count INTEGER NOT NULL,
    training_start_date DATE NOT NULL,
    training_end_date DATE NOT NULL,

    -- Performance metrics
    validation_accuracy FLOAT,
    user_acceptance_rate FLOAT,

    -- Deployment
    is_active BOOLEAN DEFAULT false,
    deployed_at TIMESTAMP WITH TIME ZONE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Frontend Event Tracking:**
```typescript
// frontend/src/lib/rft-tracker.ts
import { api } from './api'

export class RFTTracker {
  /**
   * Track when user accepts an AI-generated resume bullet
   */
  static async trackResumeBulletAccepted(data: {
    bulletId: string
    originalBullet: string
    aiRewrittenBullet: string
    jobDescription: string
  }) {
    await api.post('/api/rft/feedback', {
      event_type: 'resume_bullet_accepted',
      agent_name: 'resume_studio',
      prompt: `Job Description:\n${data.jobDescription}\n\nOriginal Bullet:\n${data.originalBullet}`,
      model_output: data.aiRewrittenBullet,
      preferred_output: data.aiRewrittenBullet,  // User accepted it
      user_accepted: true,
      context_data: {
        bullet_id: data.bulletId,
        job_description: data.jobDescription
      }
    })
  }

  /**
   * Track when user rejects and manually edits
   */
  static async trackResumeBulletRejected(data: {
    bulletId: string
    originalBullet: string
    aiRewrittenBullet: string
    userFinalEdit: string
    jobDescription: string
  }) {
    await api.post('/api/rft/feedback', {
      event_type: 'resume_bullet_rejected',
      agent_name: 'resume_studio',
      prompt: `Job Description:\n${data.jobDescription}\n\nOriginal Bullet:\n${data.originalBullet}`,
      model_output: data.aiRewrittenBullet,
      preferred_output: data.userFinalEdit,  // What user actually wanted
      user_accepted: false,
      context_data: {
        bullet_id: data.bulletId,
        job_description: data.jobDescription
      }
    })
  }

  /**
   * Track interview answer quality ratings
   */
  static async trackInterviewAnswerRated(data: {
    sessionId: string
    question: string
    userAnswer: string
    aiFeedback: string
    userRating: 1 | 2 | 3 | 4 | 5
  }) {
    await api.post('/api/rft/feedback', {
      event_type: 'interview_answer_rated',
      agent_name: 'interviewer_ai',
      prompt: `Question:\n${data.question}\n\nUser Answer:\n${data.userAnswer}`,
      model_output: data.aiFeedback,
      user_rating: data.userRating,
      context_data: {
        session_id: data.sessionId
      }
    })
  }

  /**
   * ULTIMATE REWARD SIGNAL: User got an interview/offer
   */
  static async trackApplicationSuccess(data: {
    applicationId: string
    jobId: string
    status: 'interview' | 'offer'
  }) {
    // Find all RFT feedback related to this application
    const relatedFeedback = await api.get(`/api/rft/feedback/for-application/${data.applicationId}`)

    // Update feedback with success signal
    for (const feedback of relatedFeedback) {
      await api.patch(`/api/rft/feedback/${feedback.id}`, {
        led_to_interview: data.status === 'interview',
        led_to_offer: data.status === 'offer'
      })
    }
  }
}
```

**Backend RFT API:**
```python
# backend/app/api/rft_feedback.py
from fastapi import APIRouter, Depends
from app.models.rft import RFTFeedback, RFTFeedbackCreate
from app.services.auth import get_current_user

router = APIRouter(prefix="/api/rft", tags=["rft"])

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

    # Store in PostgreSQL
    response = supabase.table("rft_feedback").insert(feedback_record).execute()

    # Also push to Redis queue for real-time processing
    await redis_client.lpush("rft_feedback_queue", json.dumps(feedback_record))

    logger.info(f"RFT Feedback recorded: {feedback.event_type} for {feedback.agent_name}")

    return {"status": "recorded", "feedback_id": response.data[0]["id"]}

@router.get("/feedback/for-application/{application_id}")
async def get_feedback_for_application(application_id: str):
    """Get all RFT feedback related to an application"""

    # Get application details
    app = await get_application(application_id)

    # Find feedback created around the same time
    # (resume tailoring, cover letter generation)
    feedback = supabase.table("rft_feedback") \
        .select("*") \
        .eq("user_id", app.user_id) \
        .gte("created_at", app.created_at - timedelta(hours=1)) \
        .lte("created_at", app.created_at + timedelta(hours=1)) \
        .execute()

    return feedback.data
```

**Acceptance Criteria:**
- All user "Accept" actions are tracked
- Feedback stored in PostgreSQL + Redis queue
- Application success retroactively updates feedback
- Dashboard shows RFT data collection stats

**Estimated Time:** 12 hours

---

#### 2.2 RFT Grader Functions
**Priority:** Critical

**Resume Bullet Grader:**
```python
# backend/app/services/rft_graders.py
from typing import List, Dict
import re

class ResumeBulletGrader:
    """Deterministic grading function for resume bullets"""

    # Action verbs from O*NET taxonomy
    STRONG_ACTION_VERBS = [
        "achieved", "improved", "reduced", "increased", "launched",
        "built", "designed", "led", "managed", "optimized",
        "delivered", "created", "implemented", "established", "spearheaded"
    ]

    def score_bullet(self, bullet: str, job_description: str = None) -> Dict:
        """
        Score a resume bullet (0-100)

        Returns:
            {
                "overall_score": int,
                "breakdown": {
                    "action_verb": int,
                    "quantifiable": int,
                    "keyword_match": int,
                    "star_structure": int,
                    "length": int
                },
                "suggestions": List[str]
            }
        """
        scores = {}
        suggestions = []

        # 1. Action Verb Check (20 points)
        first_word = bullet.split()[0].lower() if bullet else ""
        if first_word in self.STRONG_ACTION_VERBS:
            scores["action_verb"] = 20
        else:
            scores["action_verb"] = 0
            suggestions.append(f"Start with a strong action verb (e.g., {random.choice(self.STRONG_ACTION_VERBS)})")

        # 2. Quantifiable Metrics (30 points)
        has_numbers = bool(re.search(r'\d+', bullet))
        has_percentage = bool(re.search(r'\d+%', bullet))
        has_currency = bool(re.search(r'\$[\d,]+', bullet))

        metric_score = 0
        if has_numbers: metric_score += 10
        if has_percentage: metric_score += 10
        if has_currency: metric_score += 10
        scores["quantifiable"] = metric_score

        if metric_score < 30:
            suggestions.append("Add quantifiable metrics (numbers, %, $) to show impact")

        # 3. Keyword Match (25 points) - if job description provided
        if job_description:
            jd_keywords = self._extract_keywords(job_description)
            bullet_keywords = set(bullet.lower().split())
            matches = bullet_keywords.intersection(jd_keywords)

            keyword_score = min(25, len(matches) * 5)
            scores["keyword_match"] = keyword_score

            if keyword_score < 15:
                missing_keywords = list(jd_keywords - bullet_keywords)[:3]
                suggestions.append(f"Include key skills from job description: {', '.join(missing_keywords)}")
        else:
            scores["keyword_match"] = 0

        # 4. STAR Structure (15 points)
        # Situation/Task, Action, Result
        has_context = any(word in bullet.lower() for word in ["to", "by", "for", "across"])
        has_action = first_word in self.STRONG_ACTION_VERBS
        has_result = has_numbers or "resulting in" in bullet.lower()

        star_score = 0
        if has_context: star_score += 5
        if has_action: star_score += 5
        if has_result: star_score += 5
        scores["star_structure"] = star_score

        if star_score < 10:
            suggestions.append("Use STAR format: Situation → Action → Result")

        # 5. Length Check (10 points)
        word_count = len(bullet.split())
        if 10 <= word_count <= 25:
            scores["length"] = 10
        elif word_count < 10:
            scores["length"] = 5
            suggestions.append("Bullet is too short - add more detail")
        else:
            scores["length"] = 5
            suggestions.append("Bullet is too long - be more concise")

        overall_score = sum(scores.values())

        return {
            "overall_score": overall_score,
            "breakdown": scores,
            "suggestions": suggestions,
            "grade": self._score_to_grade(overall_score)
        }

    def _extract_keywords(self, text: str) -> set:
        """Extract important keywords from text"""
        # Simple keyword extraction (could be replaced with TF-IDF or KeyBERT)
        stopwords = {"the", "a", "an", "in", "to", "for", "of", "and", "or", "is", "are"}
        words = re.findall(r'\b\w+\b', text.lower())
        return set(w for w in words if w not in stopwords and len(w) > 3)

    def _score_to_grade(self, score: int) -> str:
        if score >= 80: return "A"
        elif score >= 70: return "B"
        elif score >= 60: return "C"
        elif score >= 50: return "D"
        else: return "F"


class InterviewAnswerGrader:
    """Deterministic grading function for interview answers"""

    def score_answer(self, question: str, answer: str) -> Dict:
        """
        Score an interview answer (0-100)

        Focuses on:
        - STAR structure
        - Specificity
        - Confidence markers
        - Filler words (negative signal)
        """
        scores = {}
        suggestions = []

        # 1. STAR Structure (40 points)
        situation_markers = ["when i", "at my previous", "while working", "during my time"]
        task_markers = ["needed to", "responsible for", "tasked with"]
        action_markers = ["i decided", "i implemented", "i created", "i led"]
        result_markers = ["which resulted", "leading to", "achieved", "improved by"]

        has_situation = any(marker in answer.lower() for marker in situation_markers)
        has_task = any(marker in answer.lower() for marker in task_markers)
        has_action = any(marker in answer.lower() for marker in action_markers)
        has_result = any(marker in answer.lower() for marker in result_markers)

        star_score = (has_situation * 10) + (has_task * 10) + (has_action * 10) + (has_result * 10)
        scores["star_structure"] = star_score

        if star_score < 30:
            suggestions.append("Use STAR method: Situation → Task → Action → Result")

        # 2. Specificity (30 points)
        has_numbers = bool(re.search(r'\d+', answer))
        has_specific_tools = bool(re.search(r'(Python|Java|React|AWS|SQL)', answer, re.I))
        word_count = len(answer.split())

        specificity_score = 0
        if has_numbers: specificity_score += 10
        if has_specific_tools: specificity_score += 10
        if word_count > 50: specificity_score += 10  # Detailed answer
        scores["specificity"] = specificity_score

        if not has_numbers:
            suggestions.append("Add specific metrics to quantify your impact")

        # 3. Confidence Markers (20 points)
        weak_phrases = ["i think", "maybe", "sort of", "kind of", "i guess"]
        weak_count = sum(answer.lower().count(phrase) for phrase in weak_phrases)
        confidence_score = max(0, 20 - (weak_count * 5))
        scores["confidence"] = confidence_score

        if weak_count > 2:
            suggestions.append("Reduce hedging language - be more confident!")

        # 4. Filler Words (10 points penalty)
        fillers = ["um", "uh", "like", "you know", "basically"]
        filler_count = sum(answer.lower().count(filler) for filler in fillers)
        filler_penalty = min(10, filler_count * 2)
        scores["filler_penalty"] = -filler_penalty

        if filler_count > 3:
            suggestions.append(f"Reduce filler words (found {filler_count})")

        overall_score = max(0, sum(scores.values()))

        return {
            "overall_score": overall_score,
            "breakdown": scores,
            "suggestions": suggestions,
            "grade": self._score_to_grade(overall_score)
        }

    def _score_to_grade(self, score: int) -> str:
        if score >= 80: return "A"
        elif score >= 70: return "B"
        elif score >= 60: return "C"
        elif score >= 50: return "D"
        else: return "F"
```

**Integration with Agents:**
```python
# backend/app/agents/resume_agent.py
from app.services.rft_graders import ResumeBulletGrader

class ResumeStudioAgent:
    def __init__(self):
        self.grader = ResumeBulletGrader()

    async def tailor_resume_bullet(self, bullet: str, job_description: str) -> Dict:
        # 1. Get AI rewrite
        ai_rewrite = await self.gemini_rewrite(bullet, job_description)

        # 2. Score original vs AI rewrite
        original_score = self.grader.score_bullet(bullet, job_description)
        ai_score = self.grader.score_bullet(ai_rewrite, job_description)

        # 3. Only suggest if AI version is better
        if ai_score["overall_score"] > original_score["overall_score"]:
            return {
                "original": bullet,
                "suggested": ai_rewrite,
                "original_score": original_score,
                "ai_score": ai_score,
                "improvement": ai_score["overall_score"] - original_score["overall_score"]
            }
        else:
            return {
                "original": bullet,
                "suggested": bullet,  # Don't change it
                "message": "Your original bullet is already strong!"
            }
```

**Acceptance Criteria:**
- Grader functions are deterministic (same input = same output)
- All scores have explanations
- Agents use graders before returning suggestions
- Frontend shows score breakdowns to users

**Estimated Time:** 10 hours

---

### Week 4: Neo4j Talent Graph

#### 2.3 Neo4j Setup & Schema
**Priority:** High (strategic moat)

**Docker Compose Update:**
```yaml
# docker-compose.yml
services:
  neo4j:
    image: neo4j:5.15.0
    ports:
      - "7474:7474"  # HTTP
      - "7687:7687"  # Bolt
    environment:
      NEO4J_AUTH: neo4j/password
      NEO4J_PLUGINS: '["apoc", "graph-data-science"]'
      NEO4J_dbms_memory_heap_max__size: 2G
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs

volumes:
  neo4j_data:
  neo4j_logs:
```

**Graph Schema:**
```cypher
// backend/neo4j/schema.cypher

// Node Types
CREATE CONSTRAINT user_id IF NOT EXISTS FOR (u:User) REQUIRE u.user_id IS UNIQUE;
CREATE CONSTRAINT skill_name IF NOT EXISTS FOR (s:Skill) REQUIRE s.name IS UNIQUE;
CREATE CONSTRAINT role_title IF NOT EXISTS FOR (r:Role) REQUIRE r.title IS UNIQUE;
CREATE CONSTRAINT company_name IF NOT EXISTS FOR (c:Company) REQUIRE c.name IS UNIQUE;
CREATE CONSTRAINT course_id IF NOT EXISTS FOR (co:Course) REQUIRE co.course_id IS UNIQUE;

// Indexes for performance
CREATE INDEX user_created_at IF NOT EXISTS FOR (u:User) ON (u.created_at);
CREATE INDEX skill_category IF NOT EXISTS FOR (s:Skill) ON (s.category);
CREATE INDEX role_seniority IF NOT EXISTS FOR (r:Role) ON (r.seniority);

// Example Nodes
CREATE (python:Skill {
  name: "Python",
  category: "Programming Language",
  demand_score: 95,
  growth_rate: 0.15,
  automation_risk: 0.2
});

CREATE (se:Role {
  title: "Software Engineer",
  seniority: "mid",
  avg_salary: 120000,
  demand_score: 90
});

CREATE (senior_se:Role {
  title: "Senior Software Engineer",
  seniority: "senior",
  avg_salary: 160000,
  demand_score: 95
});

CREATE (google:Company {
  name: "Google",
  size: "enterprise",
  hiring_velocity: 0.8
});

// Relationships
CREATE (se)-[:REQUIRES_SKILL {proficiency: "intermediate", importance: 0.9}]->(python);
CREATE (senior_se)-[:REQUIRES_SKILL {proficiency: "expert", importance: 0.95}]->(python);
CREATE (se)-[:PATHWAY_TO {typical_years: 3, success_rate: 0.7}]->(senior_se);
CREATE (google)-[:HIRES_FOR]->(se);
CREATE (google)-[:HIRES_FOR]->(senior_se);
```

**Python Neo4j Client:**
```python
# backend/app/core/neo4j_client.py
from neo4j import AsyncGraphDatabase
from typing import List, Dict
import os

class Neo4jClient:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "password")
        self.driver = None

    async def connect(self):
        self.driver = AsyncGraphDatabase.driver(
            self.uri,
            auth=(self.user, self.password)
        )
        # Verify connection
        await self.driver.verify_connectivity()
        logger.info("✅ Connected to Neo4j")

    async def close(self):
        if self.driver:
            await self.driver.close()

    async def create_user_node(self, user_id: str, profile: Dict):
        """Create or update user node in graph"""
        async with self.driver.session() as session:
            await session.run(
                """
                MERGE (u:User {user_id: $user_id})
                SET u.current_role = $current_role,
                    u.experience_years = $experience_years,
                    u.updated_at = datetime()
                """,
                user_id=user_id,
                current_role=profile.get("current_role"),
                experience_years=profile.get("experience_years")
            )

    async def link_user_skills(self, user_id: str, skills: List[str]):
        """Create HAS_SKILL relationships"""
        async with self.driver.session() as session:
            for skill in skills:
                await session.run(
                    """
                    MATCH (u:User {user_id: $user_id})
                    MERGE (s:Skill {name: $skill_name})
                    MERGE (u)-[r:HAS_SKILL]->(s)
                    SET r.acquired_at = datetime()
                    """,
                    user_id=user_id,
                    skill_name=skill
                )

    async def get_skill_gaps(self, user_id: str, target_role: str) -> List[Dict]:
        """Find skills user needs for target role"""
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

    async def get_career_pathways(
        self,
        current_role: str,
        target_role: str
    ) -> List[Dict]:
        """Find possible career pathways"""
        async with self.driver.session() as session:
            result = await session.run(
                """
                MATCH path = shortestPath(
                    (start:Role {title: $current_role})-[:PATHWAY_TO*..4]->(end:Role {title: $target_role})
                )
                RETURN [node in nodes(path) | node.title] AS pathway,
                       [rel in relationships(path) | rel.typical_years] AS years,
                       reduce(rate = 1.0, rel in relationships(path) | rate * rel.success_rate) AS success_rate
                ORDER BY success_rate DESC
                LIMIT 5
                """,
                current_role=current_role,
                target_role=target_role
            )

            pathways = []
            async for record in result:
                pathways.append({
                    "roles": record["pathway"],
                    "estimated_years": sum(record["years"]),
                    "success_rate": record["success_rate"]
                })

            return pathways

    async def get_skill_neighbors(self, skill: str, radius: int = 2) -> List[Dict]:
        """Find related skills (for recommendations)"""
        async with self.driver.session() as session:
            result = await session.run(
                """
                MATCH (s:Skill {name: $skill})-[:OFTEN_PAIRED_WITH*..2]-(related:Skill)
                RETURN DISTINCT related.name AS skill,
                       related.demand_score AS demand,
                       related.growth_rate AS growth
                ORDER BY demand DESC
                LIMIT 10
                """,
                skill=skill
            )

            related = []
            async for record in result:
                related.append({
                    "skill": record["skill"],
                    "demand_score": record["demand"],
                    "growth_rate": record["growth"]
                })

            return related

# Global instance
neo4j_client = Neo4jClient()
```

**Startup/Shutdown Hooks:**
```python
# backend/app/main.py
@app.on_event("startup")
async def startup():
    await neo4j_client.connect()
    logger.info("🚀 Neo4j Talent Graph connected")

@app.on_event("shutdown")
async def shutdown():
    await neo4j_client.close()
    logger.info("👋 Neo4j Talent Graph disconnected")
```

**Acceptance Criteria:**
- Neo4j runs in Docker with APOC plugin
- Schema created with constraints and indexes
- Python client can CRUD nodes and relationships
- Startup/shutdown hooks work

**Estimated Time:** 8 hours

---

#### 2.4 Talent Graph API Endpoints
**Priority:** High

```python
# backend/app/api/talent_graph.py
from fastapi import APIRouter, Depends
from app.core.neo4j_client import neo4j_client
from app.services.auth import get_current_user

router = APIRouter(prefix="/api/talent-graph", tags=["talent_graph"])

@router.get("/users/me/skill-gap")
async def get_my_skill_gap(
    target_role: str,
    current_user = Depends(get_current_user)
):
    """Get skills user needs to acquire for target role"""

    # Ensure user exists in graph
    profile = await get_user_profile(current_user.id)
    await neo4j_client.create_user_node(current_user.id, profile)
    await neo4j_client.link_user_skills(current_user.id, profile["skills"])

    # Get gaps
    gaps = await neo4j_client.get_skill_gaps(current_user.id, target_role)

    # Enrich with training resources
    for gap in gaps:
        gap["courses"] = await find_courses_for_skill(gap["skill"])
        gap["estimated_learning_time"] = estimate_learning_time(gap["required_level"])

    return {
        "target_role": target_role,
        "skill_gaps": gaps,
        "total_gaps": len(gaps),
        "high_priority_gaps": [g for g in gaps if g["importance"] > 0.7]
    }

@router.get("/users/me/career-pathways")
async def get_career_pathways(
    target_role: str,
    current_user = Depends(get_current_user)
):
    """Get possible career pathways from current role to target"""

    profile = await get_user_profile(current_user.id)
    current_role = profile.get("current_role", "Software Engineer")

    pathways = await neo4j_client.get_career_pathways(current_role, target_role)

    # Enrich with skill requirements for each step
    for pathway in pathways:
        pathway["steps"] = []
        for i in range(len(pathway["roles"]) - 1):
            from_role = pathway["roles"][i]
            to_role = pathway["roles"][i + 1]

            # Get skills needed for transition
            skills_needed = await neo4j_client.get_skill_gaps(current_user.id, to_role)

            pathway["steps"].append({
                "from": from_role,
                "to": to_role,
                "skills_needed": skills_needed,
                "estimated_time": pathway["years"][i] if i < len(pathway["years"]) else 0
            })

    return {
        "current_role": current_role,
        "target_role": target_role,
        "pathways": pathways,
        "recommended_pathway": pathways[0] if pathways else None
    }

@router.get("/skills/{skill_name}/related")
async def get_related_skills(skill_name: str):
    """Get skills often learned together with this skill"""

    related = await neo4j_client.get_skill_neighbors(skill_name, radius=2)

    return {
        "skill": skill_name,
        "related_skills": related,
        "recommendation": f"Professionals with {skill_name} often also learn: {', '.join([s['skill'] for s in related[:3]])}"
    }

@router.post("/admin/seed-graph")
async def seed_talent_graph():
    """Admin endpoint to seed graph with O*NET data"""
    # This would import O*NET occupational data into Neo4j
    # For now, placeholder
    return {"message": "Seeding not yet implemented"}
```

**Frontend Visualization:**
```typescript
// frontend/src/components/talent-graph/SkillGapVisualization.tsx
import { useQuery } from '@tanstack/react-query'
import { RadarChart, Radar, PolarGrid, PolarAngleAxis } from 'recharts'

export function SkillGapVisualization({ targetRole }: { targetRole: string }) {
  const { data } = useQuery({
    queryKey: ['skill-gap', targetRole],
    queryFn: () => api.get(`/talent-graph/users/me/skill-gap?target_role=${targetRole}`)
  })

  if (!data) return <Skeleton />

  // Transform for radar chart
  const chartData = data.skill_gaps.map(gap => ({
    skill: gap.skill,
    current: 0, // User doesn't have it
    required: gap.importance * 100
  }))

  return (
    <Card className="p-6">
      <h3 className="text-lg font-semibold mb-4">
        Skill Gaps for {targetRole}
      </h3>

      <RadarChart width={400} height={400} data={chartData}>
        <PolarGrid />
        <PolarAngleAxis dataKey="skill" />
        <Radar name="Your Level" dataKey="current" stroke="#8884d8" fill="#8884d8" fillOpacity={0.6} />
        <Radar name="Required" dataKey="required" stroke="#82ca9d" fill="#82ca9d" fillOpacity={0.6} />
      </RadarChart>

      <div className="mt-6 space-y-4">
        <h4 className="font-semibold">High Priority Skills</h4>
        {data.high_priority_gaps.map(gap => (
          <div key={gap.skill} className="flex items-center justify-between p-3 bg-gray-50 rounded">
            <div>
              <div className="font-medium">{gap.skill}</div>
              <div className="text-sm text-gray-500">
                {gap.estimated_learning_time} to reach {gap.required_level}
              </div>
            </div>
            <Button size="sm" onClick={() => router.push(`/learn/${gap.skill}`)}>
              Start Learning
            </Button>
          </div>
        ))}
      </div>
    </Card>
  )
}
```

**Acceptance Criteria:**
- `/talent-graph/users/me/skill-gap` returns accurate gaps
- `/talent-graph/users/me/career-pathways` finds shortest path
- Frontend visualizes gaps with radar chart
- Each gap shows learning resources

**Estimated Time:** 10 hours

---

## 🔄 Phase 3: Data Pipeline & Automation (Weeks 5-6)

### Week 5: Real Job Scrapers

#### 3.1 Job Scraper Architecture
**Priority:** Critical (can't launch without real jobs)

**Scraper Strategy:**
```
Option A: API-First (Preferred)
- Greenhouse API (official)
- Lever API (official)
- Indeed API (restricted - needs partner account)

Option B: Scraping (Fallback)
- Puppeteer/Playwright for sites without APIs
- Respect robots.txt
- Rate limiting
```

**Implementation:**
```python
# backend/app/scrapers/greenhouse_scraper.py
import httpx
from typing import List, Dict
from datetime import datetime

class GreenhouseScraper:
    """
    Scraper for Greenhouse-powered career sites

    Greenhouse provides a public job board API:
    https://boards-api.greenhouse.io/v1/boards/{company}/jobs
    """

    BASE_URL = "https://boards-api.greenhouse.io/v1/boards"

    async def scrape_company(self, company_board_token: str) -> List[Dict]:
        """Scrape all jobs from a company's Greenhouse board"""

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/{company_board_token}/jobs",
                params={"content": "true"}  # Include full job description
            )
            response.raise_for_status()

            jobs_data = response.json()["jobs"]

            processed_jobs = []
            for job in jobs_data:
                processed = self._process_greenhouse_job(job, company_board_token)
                processed_jobs.append(processed)

            return processed_jobs

    def _process_greenhouse_job(self, raw_job: Dict, company: str) -> Dict:
        """Transform Greenhouse format to our schema"""

        # Extract location
        location = raw_job.get("location", {})
        is_remote = "remote" in location.get("name", "").lower()

        # Extract salary (if present in description)
        description = raw_job.get("content", "")
        salary_range = self._extract_salary(description)

        # Determine seniority from title
        title = raw_job.get("title", "")
        seniority = self._infer_seniority(title)

        return {
            "title": title,
            "seniority": seniority,
            "description": description,
            "requirements": self._extract_requirements(raw_job),
            "responsibilities": self._extract_responsibilities(raw_job),
            "benefits": None,  # Not usually in Greenhouse data
            "skills_extracted": self._extract_skills(description),
            "location_type": "remote" if is_remote else "onsite",
            "location_city": location.get("name") if not is_remote else None,
            "location_country": "USA",  # Default, could parse from location
            "salary_min": salary_range[0] if salary_range else None,
            "salary_max": salary_range[1] if salary_range else None,
            "salary_currency": "USD",
            "employment_type": "full_time",
            "apply_url": raw_job.get("absolute_url"),
            "source": f"greenhouse:{company}",
            "external_id": f"greenhouse_{raw_job['id']}",
            "posted_at": datetime.fromisoformat(raw_job.get("updated_at", "").replace("Z", "+00:00"))
        }

    def _extract_salary(self, text: str) -> tuple:
        """Extract salary range from text"""
        import re

        # Look for patterns like "$100k-$150k" or "$100,000 - $150,000"
        pattern = r'\$(\d{1,3}(?:,?\d{3})*)\s*(?:-|to)\s*\$(\d{1,3}(?:,?\d{3})*)'
        match = re.search(pattern, text)

        if match:
            min_sal = int(match.group(1).replace(',', ''))
            max_sal = int(match.group(2).replace(',', ''))
            return (min_sal, max_sal)

        return None

    def _infer_seniority(self, title: str) -> str:
        """Infer seniority level from job title"""
        title_lower = title.lower()

        if any(word in title_lower for word in ["senior", "sr.", "lead", "principal", "staff"]):
            return "senior"
        elif any(word in title_lower for word in ["junior", "jr.", "entry", "associate"]):
            return "entry"
        elif any(word in title_lower for word in ["manager", "director", "head", "vp"]):
            return "manager"
        else:
            return "mid"

    async def _extract_skills(self, text: str) -> List[str]:
        """Extract skills from job description"""
        # Use Gemini for skill extraction (or spaCy NER)
        from app.services.gemini_analyzer import GeminiAnalyzer

        analyzer = GeminiAnalyzer()
        skills = await analyzer.extract_skills_from_text(text)

        return skills


# backend/app/scrapers/lever_scraper.py
class LeverScraper:
    """
    Scraper for Lever-powered career sites

    Lever API: https://api.lever.co/v0/postings/{company}?mode=json
    """

    BASE_URL = "https://api.lever.co/v0/postings"

    async def scrape_company(self, company: str) -> List[Dict]:
        """Scrape all jobs from a company's Lever board"""
        # Similar to Greenhouse scraper
        pass


# backend/app/scrapers/indeed_scraper.py
class IndeedScraper:
    """
    Indeed scraper (requires Indeed Publisher API key)
    https://indeed.com/publisher
    """

    async def search_jobs(self, query: str, location: str = None) -> List[Dict]:
        """Search Indeed jobs"""
        # Requires API key from Indeed Publisher program
        pass


# backend/app/scrapers/orchestrator.py
class ScraperOrchestrator:
    """Manages all job scrapers"""

    def __init__(self):
        self.greenhouse = GreenhouseScraper()
        self.lever = LeverScraper()
        self.indeed = IndeedScraper()

        # Companies using Greenhouse
        self.greenhouse_companies = [
            "airbnb", "stripe", "gitlab", "coinbase", "notion",
            "figma", "databricks", "plaid", "ramp", "scale"
        ]

        # Companies using Lever
        self.lever_companies = [
            "netflix", "uber", "lyft", "reddit", "twitch"
        ]

    async def scrape_all(self) -> Dict:
        """Scrape all configured sources"""

        all_jobs = []
        stats = {"greenhouse": 0, "lever": 0, "indeed": 0, "errors": 0}

        # Scrape Greenhouse companies
        for company in self.greenhouse_companies:
            try:
                jobs = await self.greenhouse.scrape_company(company)
                all_jobs.extend(jobs)
                stats["greenhouse"] += len(jobs)
                logger.info(f"✅ Scraped {len(jobs)} jobs from {company} (Greenhouse)")
            except Exception as e:
                logger.error(f"❌ Failed to scrape {company}: {e}")
                stats["errors"] += 1

            # Rate limiting
            await asyncio.sleep(2)

        # Scrape Lever companies
        for company in self.lever_companies:
            try:
                jobs = await self.lever.scrape_company(company)
                all_jobs.extend(jobs)
                stats["lever"] += len(jobs)
                logger.info(f"✅ Scraped {len(jobs)} jobs from {company} (Lever)")
            except Exception as e:
                logger.error(f"❌ Failed to scrape {company}: {e}")
                stats["errors"] += 1

            await asyncio.sleep(2)

        # Deduplicate jobs
        unique_jobs = self._deduplicate(all_jobs)

        return {
            "jobs": unique_jobs,
            "stats": stats,
            "total_scraped": len(all_jobs),
            "total_unique": len(unique_jobs)
        }

    def _deduplicate(self, jobs: List[Dict]) -> List[Dict]:
        """Remove duplicate jobs based on title + company + location"""

        seen = set()
        unique = []

        for job in jobs:
            key = (job["title"], job.get("location_city", ""), job["source"])
            if key not in seen:
                seen.add(key)
                unique.append(job)

        return unique
```

**Scheduled Scraping:**
```python
# backend/app/core/scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.scrapers.orchestrator import ScraperOrchestrator

scheduler = AsyncIOScheduler()

async def daily_job_scrape():
    """Scrape jobs from all sources daily"""
    logger.info("🕐 Starting daily job scrape...")

    orchestrator = ScraperOrchestrator()
    result = await orchestrator.scrape_all()

    # Insert into database
    for job in result["jobs"]:
        try:
            # Check if job already exists
            existing = supabase.table("jobs") \
                .select("id") \
                .eq("external_id", job.get("external_id")) \
                .execute()

            if not existing.data:
                # New job - insert
                supabase.table("jobs").insert(job).execute()
            else:
                # Existing job - update
                supabase.table("jobs") \
                    .update(job) \
                    .eq("external_id", job.get("external_id")) \
                    .execute()
        except Exception as e:
            logger.error(f"Failed to insert job: {e}")

    logger.info(f"✅ Daily scrape complete: {result['stats']}")

# Schedule for 2 AM daily
scheduler.add_job(daily_job_scrape, 'cron', hour=2, minute=0)

@app.on_event("startup")
async def start_scheduler():
    scheduler.start()
    logger.info("📅 Job scraper scheduler started")
```

**Acceptance Criteria:**
- Greenhouse scraper works for 10+ companies
- Lever scraper works for 5+ companies
- Daily scraping runs automatically at 2 AM
- Duplicate jobs are detected and skipped
- Database has 500+ real jobs after first run

**Estimated Time:** 16 hours

---

### Week 6: Email Notifications & Automation

#### 3.2 SendGrid Email System
**Priority:** High (re-engagement)

**Email Templates:**
```python
# backend/app/services/email_service.py
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, DynamicTemplateData
import os

class EmailService:
    def __init__(self):
        self.client = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        self.from_email = "noreply@nextcareer.ai"

        # SendGrid Template IDs (create these in SendGrid UI)
        self.templates = {
            "job_alert": "d-xxx",
            "goal_progress": "d-yyy",
            "weekly_digest": "d-zzz",
            "interview_reminder": "d-aaa"
        }

    async def send_job_alert(self, user_email: str, jobs: List[Dict]):
        """Send email with new matching jobs"""

        message = Mail(
            from_email=self.from_email,
            to_emails=user_email
        )

        message.template_id = self.templates["job_alert"]
        message.dynamic_template_data = {
            "jobs": jobs[:5],  # Top 5 matches
            "job_count": len(jobs),
            "view_all_url": f"https://app.nextcareer.ai/jobs/recommendations"
        }

        try:
            response = self.client.send(message)
            logger.info(f"✅ Job alert sent to {user_email}: {response.status_code}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to send job alert: {e}")
            return False

    async def send_weekly_digest(self, user_email: str, digest_data: Dict):
        """Send weekly progress digest"""

        message = Mail(
            from_email=self.from_email,
            to_emails=user_email
        )

        message.template_id = self.templates["weekly_digest"]
        message.dynamic_template_data = {
            "career_health_score": digest_data["chs"],
            "chs_change": digest_data["chs_change"],
            "applications_this_week": digest_data["applications"],
            "goals_completed": digest_data["goals_completed"],
            "new_skills_added": digest_data["new_skills"],
            "top_recommendation": digest_data["top_action"]
        }

        try:
            response = self.client.send(message)
            logger.info(f"✅ Weekly digest sent to {user_email}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to send weekly digest: {e}")
            return False
```

**Scheduled Email Jobs:**
```python
# backend/app/core/scheduler.py

async def send_daily_job_alerts():
    """Send job alerts to users with alerts enabled"""

    # Get users with job alerts enabled
    users = supabase.table("users") \
        .select("id, email") \
        .eq("email_alerts_enabled", True) \
        .execute()

    email_service = EmailService()

    for user in users.data:
        # Get user's job preferences
        prefs = supabase.table("job_alert_preferences") \
            .select("*") \
            .eq("user_id", user["id"]) \
            .execute()

        if not prefs.data:
            continue

        # Find new jobs matching preferences
        new_jobs = await find_jobs_matching_preferences(prefs.data[0])

        if new_jobs:
            await email_service.send_job_alert(user["email"], new_jobs)

async def send_weekly_digests():
    """Send weekly progress digests"""

    users = supabase.table("users") \
        .select("id, email") \
        .eq("weekly_digest_enabled", True) \
        .execute()

    email_service = EmailService()

    for user in users.data:
        # Compile digest data
        digest = await compile_weekly_digest(user["id"])
        await email_service.send_weekly_digest(user["email"], digest)

# Schedule daily alerts at 9 AM
scheduler.add_job(send_daily_job_alerts, 'cron', hour=9, minute=0)

# Schedule weekly digests on Monday 8 AM
scheduler.add_job(send_weekly_digests, 'cron', day_of_week='mon', hour=8, minute=0)
```

**Acceptance Criteria:**
- SendGrid templates created in UI
- Job alerts sent daily at 9 AM
- Weekly digests sent Monday 8 AM
- Users can unsubscribe via link
- Email preferences saved in database

**Estimated Time:** 8 hours

---

## 🚀 Phase 4: Production Readiness (Weeks 7-8)

### Week 7: Deployment Setup

#### 4.1 Backend: Google Cloud Run
**Priority:** Critical

**Dockerfile:**
```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run migrations on startup (optional)
# RUN alembic upgrade head

# Expose port
EXPOSE 8000

# Start server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
```

**Cloud Build Config:**
```yaml
# backend/cloudbuild.yaml
steps:
  # Build the container image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/next-backend:$COMMIT_SHA', '.']

  # Push the container image to Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/next-backend:$COMMIT_SHA']

  # Deploy container image to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'next-backend'
      - '--image'
      - 'gcr.io/$PROJECT_ID/next-backend:$COMMIT_SHA'
      - '--region'
      - 'us-central1'
      - '--platform'
      - 'managed'
      - '--allow-unauthenticated'
      - '--set-env-vars'
      - 'ENVIRONMENT=production'
      - '--memory'
      - '2Gi'
      - '--cpu'
      - '2'
      - '--max-instances'
      - '10'

images:
  - 'gcr.io/$PROJECT_ID/next-backend:$COMMIT_SHA'
```

**Deploy Script:**
```bash
# backend/deploy.sh
#!/bin/bash
set -e

echo "🚀 Deploying NEXT Backend to Cloud Run..."

# Set project
gcloud config set project next-career-intelligence

# Submit build
gcloud builds submit --config=cloudbuild.yaml

echo "✅ Deployment complete!"
echo "🌐 Service URL: https://next-backend-xxxxx-uc.a.run.app"
```

**Acceptance Criteria:**
- Docker image builds successfully
- Cloud Run service deploys
- Health check endpoint returns 200
- API accessible via public URL
- Environment variables set correctly

**Estimated Time:** 6 hours

---

#### 4.2 Frontend: Vercel
**Priority:** Critical

**Vercel Configuration:**
```json
// frontend/vercel.json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "framework": "nextjs",
  "regions": ["iad1"],
  "env": {
    "NEXT_PUBLIC_API_URL": "https://api.nextcareer.ai",
    "NEXT_PUBLIC_FIREBASE_API_KEY": "@firebase-api-key",
    "NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY": "@stripe-publishable-key"
  },
  "functions": {
    "app/api/**": {
      "memory": 1024,
      "maxDuration": 10
    }
  },
  "redirects": [
    {
      "source": "/resume",
      "destination": "/resume-studio",
      "permanent": true
    }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        }
      ]
    }
  ]
}
```

**Deploy via GitHub Integration:**
1. Connect GitHub repo to Vercel
2. Configure environment variables in Vercel dashboard
3. Set production branch: `main`
4. Enable auto-deploy on push

**Acceptance Criteria:**
- Frontend deploys automatically on push to main
- Custom domain configured (nextcareer.ai)
- HTTPS enabled
- Environment variables work
- Build time < 3 minutes

**Estimated Time:** 4 hours

---

### Week 8: Monitoring & Final Testing

#### 4.3 Observability Stack
**Priority:** High

**Sentry Configuration:**
```python
# backend/app/core/monitoring.py (enhanced)
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    environment=os.getenv("ENVIRONMENT", "development"),
    integrations=[
        FastApiIntegration(),
        SqlalchemyIntegration()
    ],
    traces_sample_rate=0.1,  # 10% of transactions
    profiles_sample_rate=0.1,

    # Custom error handling
    before_send=lambda event, hint: event if should_send_error(event) else None
)

def track_custom_metric(metric_name: str, value: float, tags: Dict = None):
    """Track custom business metrics"""
    sentry_sdk.set_measurement(metric_name, value)
    if tags:
        for key, val in tags.items():
            sentry_sdk.set_tag(key, val)
```

**Performance Monitoring:**
```python
# Track key business metrics
@router.post("/jobs/apply")
async def apply_to_job(application: JobApplication):
    with sentry_sdk.start_span(op="job_application", description="Apply to job"):
        # Track time to tailor resume
        start = time.time()
        tailored = await tailor_resume(application)
        tailor_time = time.time() - start

        track_custom_metric("resume_tailor_time_ms", tailor_time * 1000, {
            "job_id": application.job_id,
            "user_tier": application.user_tier
        })

        # Rest of application logic...
```

**Health Dashboard:**
```python
# backend/app/api/admin/health_dashboard.py
@router.get("/admin/health/dashboard")
async def health_dashboard():
    """Comprehensive health dashboard for monitoring"""

    return {
        "system": {
            "uptime_seconds": time.time() - app_start_time,
            "environment": os.getenv("ENVIRONMENT"),
            "version": os.getenv("APP_VERSION", "unknown")
        },
        "database": {
            "postgres_healthy": await check_postgres(),
            "neo4j_healthy": await check_neo4j(),
            "redis_healthy": await check_redis()
        },
        "external_services": {
            "gemini_api": await check_gemini(),
            "stripe_api": await check_stripe(),
            "sendgrid_api": await check_sendgrid()
        },
        "performance": {
            "avg_response_time_ms": get_avg_response_time(),
            "cache_hit_rate": get_cache_hit_rate(),
            "error_rate": get_error_rate()
        },
        "business_metrics": {
            "total_users": await count_users(),
            "active_users_today": await count_active_users(),
            "applications_today": await count_applications_today(),
            "revenue_mrr": await calculate_mrr()
        },
        "rft_system": {
            "feedback_events_today": await count_rft_feedback_today(),
            "model_version": await get_active_rft_model_version()
        }
    }
```

**Acceptance Criteria:**
- Sentry captures errors and performance traces
- Health dashboard shows all system statuses
- Alerts configured for critical errors
- Custom business metrics tracked

**Estimated Time:** 6 hours

---

#### 4.4 End-to-End Testing
**Priority:** High

**Test Suite:**
```python
# backend/tests/test_e2e.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_complete_user_journey():
    """Test full user flow from signup to job application"""

    async with AsyncClient(base_url="http://localhost:8000") as client:
        # 1. Signup
        signup_response = await client.post("/api/auth/signup", json={
            "email": "test@example.com",
            "password": "Test123!",
            "name": "Test User"
        })
        assert signup_response.status_code == 201

        user_id = signup_response.json()["user_id"]
        token = signup_response.json()["token"]

        headers = {"Authorization": f"Bearer {token}"}

        # 2. Complete onboarding
        await client.post("/api/onboarding/complete", json={
            "target_role": "Software Engineer",
            "experience_level": "mid",
            "top_goal": "get_job"
        }, headers=headers)

        # 3. Upload resume
        with open("tests/fixtures/sample_resume.pdf", "rb") as f:
            resume_response = await client.post(
                "/api/resume-studio/ingest",
                files={"file": f},
                headers=headers
            )
        assert resume_response.status_code == 200

        # 4. Get job recommendations
        jobs_response = await client.get(
            "/api/jobs/recommendations",
            params={"user_id": user_id},
            headers=headers
        )
        assert jobs_response.status_code == 200
        assert len(jobs_response.json()) > 0

        # 5. Apply to job
        job_id = jobs_response.json()[0]["id"]
        apply_response = await client.post(
            "/api/jobs/apply",
            json={
                "user_id": user_id,
                "job_id": job_id,
                "tailor_resume": True,
                "generate_cover_letter": True
            },
            headers=headers
        )
        assert apply_response.status_code == 201

        # 6. Verify RFT feedback was recorded
        feedback_response = await client.get(
            f"/api/rft/feedback/for-application/{apply_response.json()['application_id']}",
            headers=headers
        )
        assert len(feedback_response.json()) > 0

        print("✅ Complete user journey test passed!")

@pytest.mark.asyncio
async def test_career_health_score_calculation():
    """Test CHS calculation"""
    # Test code...
    pass

@pytest.mark.asyncio
async def test_neo4j_skill_gap_analysis():
    """Test Neo4j talent graph queries"""
    # Test code...
    pass
```

**Run Tests:**
```bash
# Run full test suite
pytest backend/tests/ -v --cov=app --cov-report=html

# Generate coverage report
open htmlcov/index.html
```

**Acceptance Criteria:**
- E2E test passes without errors
- Test coverage > 70%
- All critical paths tested
- Integration tests pass

**Estimated Time:** 8 hours

---

## 📊 Phase Summary & Checklist

### Phase 1: Fix & Stabilize (Weeks 1-2) ✅
- [x] Jobs marketplace cleanup
- [ ] Type safety enforcement (CI/CD)
- [ ] Empty state handling
- [ ] Career Health Score implementation
- [ ] Goal-based job filtering

### Phase 2: Core Moats (Weeks 3-4)
- [ ] RFT infrastructure setup
- [ ] RFT grader functions
- [ ] Neo4j setup & schema
- [ ] Talent Graph API endpoints
- [ ] Frontend visualizations

### Phase 3: Data Pipeline (Weeks 5-6)
- [ ] Job scrapers (Greenhouse, Lever)
- [ ] Scheduled scraping
- [ ] Email notification system
- [ ] Weekly digest automation

### Phase 4: Production (Weeks 7-8)
- [ ] Backend deployment (Cloud Run)
- [ ] Frontend deployment (Vercel)
- [ ] Monitoring & observability
- [ ] End-to-end testing
- [ ] Load testing

---

## 🎯 Success Metrics

**Technical Metrics:**
- **Type Safety:** 0 FE/BE integration bugs in production
- **RFT Data Collection:** 100+ feedback events per day
- **Neo4j Performance:** Skill gap queries < 500ms
- **Job Data:** 1000+ real jobs in database
- **Uptime:** 99.9% availability
- **API Latency:** p99 < 2 seconds

**Business Metrics:**
- **User Retention:** 30-day retention > 40%
- **Career Health Score:** Average CHS > 60
- **Feature Adoption:**
  - Resume Studio: 70% of users
  - Job Recommendations: 50% of users
  - Interview AI: 30% of users
- **Conversion:** Free → Pro conversion > 5%

---

## 🚨 Risk Mitigation

### Risk 1: RFT System Doesn't Collect Enough Data
**Mitigation:**
- Lower friction for feedback (1-click accept)
- Gamify feedback (badges, points)
- Show users how feedback improves their experience

### Risk 2: Neo4j Performance Issues
**Mitigation:**
- Cache common queries in Redis
- Use APOC procedures for complex traversals
- Limit graph depth to 4 hops

### Risk 3: Job Scraping Gets Blocked
**Mitigation:**
- Use official APIs where possible
- Respect rate limits
- Rotate user agents for scraping
- Have fallback to manual job seeding

### Risk 4: Email Deliverability Issues
**Mitigation:**
- Warm up SendGrid domain
- Monitor spam scores
- Include unsubscribe link
- Segment email lists

---

## 📅 Timeline Visualization

```
Week 1-2: Foundation
├─ Jobs cleanup (4h)
├─ Type safety (6h)
├─ Empty states (4h)
├─ CHS implementation (8h)
└─ Goal filtering (6h)

Week 3-4: Moat Features
├─ RFT setup (12h)
├─ RFT graders (10h)
├─ Neo4j setup (8h)
└─ Talent Graph API (10h)

Week 5-6: Data Pipeline
├─ Job scrapers (16h)
└─ Email system (8h)

Week 7-8: Production
├─ Backend deploy (6h)
├─ Frontend deploy (4h)
├─ Monitoring (6h)
└─ Testing (8h)

Total: ~116 hours (~3 hours/day for 8 weeks)
```

---

## 🎉 Launch Readiness Checklist

Before going to production, verify:

- [ ] All Phase 1 tasks complete
- [ ] RFT system collecting feedback
- [ ] Neo4j graph populated with data
- [ ] 1000+ real jobs in database
- [ ] Email system tested
- [ ] Backend deployed to Cloud Run
- [ ] Frontend deployed to Vercel
- [ ] Custom domain configured
- [ ] SSL/HTTPS enabled
- [ ] Sentry monitoring active
- [ ] Database backups configured
- [ ] Rate limiting tested
- [ ] Load testing passed (500 concurrent users)
- [ ] Security scan passed (no critical vulnerabilities)
- [ ] GDPR compliance verified
- [ ] Terms of Service + Privacy Policy published
- [ ] Support email configured
- [ ] Analytics tracking enabled

---

**Document Status:** Ready for Execution
**Next Steps:** Begin Phase 1, Task 1.1 (Jobs Marketplace Cleanup)
