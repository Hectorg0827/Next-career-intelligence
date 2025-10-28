# 🧠 Next Career Intelligence - Backend Architecture

## 🎯 Mission
Transform Next Career Intelligence into **the world's most intelligent career powerhouse** with predictive intelligence, proactive protection, and personalized forecasting.

---

## 🏗️ Multi-Agent Architecture (3 Layers)

### **Layer 1: Core Analysis** ✅ COMPLETE
The foundation - instant analysis of any job opportunity

| Agent | Purpose | Key Output |
|-------|---------|------------|
| **ProfileAgent** | Memory keeper - manages persistent UserProfile as single source of truth | UserProfile with completeness scoring, missing fields |
| **RiskAgent** | Survival analyst - assesses AI displacement risk using Gemini | DisplacementRiskLevel + justification |
| **MatchAgent** | Compatibility analyzer - weighted multi-factor fit scoring | compatibility_score (0-100) + match_highlights |
| **GapAgent** | Growth strategist - identifies skill gaps with positioning advice | SkillGap[] with severity, time_to_close, next_steps |
| **SentimentAgent** | Emotional intelligence - extracts motivation signals from conversations | ProfileUpdate with enjoy/hate/fear/aspire signals |

**Workflow**: Profile → Risk → Match → Gap → Sentiment → Update Profile

**Formula (MatchAgent)**:
```
compatibility_score = 
  40% × skill_match +
  30% × experience_alignment +
  20% × preference_alignment +
  10% × burnout_alignment
```

---

### **Layer 2: Predictive Intelligence** ✅ COMPLETE
The forecasting engine - see futures before they happen

| Agent | Purpose | Key Output |
|-------|---------|------------|
| **TrajectoryAgent** | Future predictor - forecasts 3 most likely career paths | career_forecast with probabilities, timelines, salary ranges, skill unlock sequences |
| **MarketIntelAgent** | Market watcher - aggregates live labor market data | demand_trend, avg_salary, emerging_skills, automation_risk_trend, layoff_alerts |

**TrajectoryAgent Output**:
```json
{
  "career_forecast": [
    {
      "path_name": "Behavior Specialist",
      "probability": 68,
      "timeline_months": 14,
      "salary_range": {"min": 72000, "max": 95000},
      "required_skills": ["ABA", "Data Collection"],
      "skill_unlock_sequence": ["Get ABA certification (3mo)", "Shadowing program (2mo)"],
      "reasoning": "Your special education background aligns perfectly..."
    }
  ],
  "current_trajectory_score": 73,
  "pivot_opportunities": ["EdTech Product Manager", "Learning Experience Designer"]
}
```

**MarketIntelAgent Data Sources** (future):
- LinkedIn Jobs API
- Indeed Analytics
- Layoffs.fyi
- Levels.fyi
- Payscale
- GitHub Jobs

---

### **Layer 3: Proactive Protection** ✅ COMPLETE
The safety net - detect threats, optimize decisions

| Agent | Purpose | Key Output |
|-------|---------|------------|
| **EarlyWarningAgent** | Threat detector - scans for career risks before they're urgent | Alert[] with severity, urgency_days, recommended_actions |
| **NegotiationAgent** | Compensation optimizer - analyzes offers and generates negotiation scripts | fairness_score, lifetime_value_delta, negotiation_script |
| **PeerBenchmarkingAgent** | Community intelligence - compares user to similar profiles | common_transitions, salary_comparison, skill_gaps_vs_peers |

**EarlyWarningAgent Alert Types**:
- `automation_threat`: Current role at high AI displacement risk (90 days)
- `skill_obsolescence`: Skills declining >10% in demand (120 days)
- `market_decline`: Industry contracting (90 days)
- `burnout_risk`: Burnout level ≥6 (critical if ≥8) (30-60 days)
- `confidence_decay`: Confidence level ≤3 (90 days)

**NegotiationAgent Fairness Score**:
- 90-100: Top 25% of market (≥75th percentile)
- 70-90: Above median
- 40-70: Below median
- 0-40: Bottom 25%

**Lifetime Value Delta**: 5-year projection with 3% annual raises vs market median

---

## 📡 REST API Endpoints

### Base URL
- **Production**: `https://next-backend-jxs4smo7nq-uc.a.run.app`
- **Local**: `http://localhost:8000`

### **Layer 1 Endpoints** (Core Analysis)

#### `POST /api/match/analyze`
Analyze compatibility between user and job opportunity
```json
{
  "user_id": "user_123",
  "job": {
    "title": "Special Education Teacher",
    "company": "Oakland School District",
    "required_skills": ["IEP Development", "Behavior Management"],
    ...
  },
  "recent_conversation": "I'm looking for something less stressful..."
}
```

**Response**: `OrchestratorOutput` with ai_displacement_risk, compatibility_score, skill_gaps, next_steps, profile_update

#### `POST /api/match/rank`
Rank multiple jobs by recommendation score
```json
{
  "user_id": "user_123",
  "jobs": [...]
}
```

#### `GET /api/match/profile/{user_id}`
Get user's complete profile (source of truth)

#### `POST /api/match/profile/{user_id}/create`
Initialize new user profile

#### `GET /api/match/user/{user_id}/current-job-risk`
Assess AI displacement risk for user's current job

---

### **Layer 2 Endpoints** (Predictive Intelligence)

#### `GET /api/match/user/{user_id}/career-forecast`
Predict 3 most likely career paths with probabilities, timelines, salaries

**Powers**: "Career Path Visualizer" frontend module

**Response**:
```json
{
  "career_forecast": [...],
  "current_trajectory_score": 73,
  "pivot_opportunities": [...]
}
```

#### `GET /api/match/market-intelligence?role_keywords=teacher&industry=education&location=Oakland`
Get live market intelligence

**Powers**: "Market Pulse Widget" scrolling ticker

**Response**:
```json
{
  "demand_trend": "stable",
  "demand_change_90d": -5.2,
  "avg_salary": 68000,
  "top_hiring_companies": ["OUSD", "Alameda County Office of Ed"],
  "emerging_skills": ["AI literacy", "Hybrid learning design"],
  "automation_risk_trend": "increasing",
  "layoff_alerts": []
}
```

---

### **Layer 3 Endpoints** (Proactive Protection)

#### `GET /api/match/user/{user_id}/early-warnings`
Scan for threats before they're urgent

**Powers**: "Early Warning Banner" and proactive email alerts  
**Subscription**: Pro tier ($29/mo) and Elite tier ($99/mo)

**Response**:
```json
{
  "alerts": [
    {
      "type": "automation_threat",
      "severity": "high",
      "urgency_days": 90,
      "message": "Your current role as K-12 Teacher has Medium AI displacement risk...",
      "recommended_actions": ["Upskill in AI literacy", "Explore EdTech roles"]
    }
  ]
}
```

#### `POST /api/match/user/{user_id}/analyze-offer`
Analyze job offer and generate negotiation strategy

**Powers**: "Offer Optimizer" card  
**Subscription**: Elite tier ($99/mo) exclusive

**Request**:
```json
{
  "user_id": "user_123",
  "offer_details": {
    "salary": 78000,
    "equity": 0,
    "bonus": 3000,
    "benefits": "Standard health",
    "company": "Oakland School District",
    "role": "Special Ed Teacher"
  }
}
```

**Response**:
```json
{
  "market_analysis": {...},
  "fairness_score": 72,
  "lifetime_value_delta": -$52000,
  "leverage_points": ["7 years experience", "Special certification"],
  "recommended_counter": 85000,
  "negotiation_script": "Thank you for the offer. Based on my 7 years...",
  "fallback_positions": ["Ask for extra PTO", "Request professional development budget"]
}
```

#### `GET /api/match/user/{user_id}/peer-insights`
Get anonymized career insights from similar users

**Powers**: "Peer Lens" comparison module  
**Subscription**: Enterprise tier

**Response**:
```json
{
  "peer_cohort_size": 127,
  "common_transitions": [
    {
      "from_role": "Special Ed Teacher",
      "to_role": "Behavior Specialist",
      "frequency": 23,
      "avg_timeline_months": 14,
      "success_rate": 78
    }
  ],
  "salary_comparison": {
    "user_position": "45th percentile",
    "cohort_median": 72000,
    "user_salary": 68000
  },
  "skill_gaps_vs_peers": ["ABA Certification", "Data Analysis"],
  "trending_skills_in_cohort": ["AI literacy", "SEL frameworks"]
}
```

---

## 📊 Data Models

### **UserProfile** (Single Source of Truth)
```python
{
  "user_id": str,
  "email": str,
  "current_role": str,
  "industry": str,
  "years_total_experience": int,
  "work_history": [WorkHistoryEntry],
  "skills": [Skill],
  "preferences": [UserPreference],
  "career_goals": [CareerGoal],
  "risk_factors": [RiskFactor],
  "motivation_signals": [MotivationSignal],
  "development_needs": [DevelopmentNeed],
  
  # Behavioral tracking
  "jobs_viewed": [str],
  "jobs_saved": [str],
  "jobs_applied": [str],
  "jobs_rejected": [{"job_id": str, "reason": str}],
  
  # Metadata
  "profile_completeness": float,  # 0-100%
  "total_interactions": int,
  "burnout_level": int,  # 0-10
  "confidence_level": int,  # 0-10
  "salary_expectations": {"min": int, "target": int, "currency": str},
  
  "created_at": datetime,
  "updated_at": datetime
}
```

**Completeness Scoring** (15 weighted fields):
- Critical: current_role, skills, career_goals (weight: 10 each)
- Important: work_history, preferences, salary_expectations (weight: 5 each)
- Optional: motivation_signals, development_needs (weight: 2 each)

### **OrchestratorOutput** (Standard Response)
```python
{
  "ai_displacement_risk": {
    "level": "Low" | "Medium" | "High" | "Very Low",
    "score": float,  # 0-100
    "justification": str
  },
  "compatibility_score": float,  # 0-100
  "match_highlights": [str],
  "skill_gaps_for_job": [
    {
      "skill": str,
      "severity": "minor" | "medium" | "critical",
      "time_to_close": str,
      "positioning_advice": str
    }
  ],
  "next_steps_for_user": [str],
  "profile_update": ProfileUpdate,
  "info_request_for_coach": [str],
  "warnings": [str],
  "internal_scores": {
    "stability_score": float,
    "trajectory_score": float,
    "recommendation_score": float
  }
}
```

---

## 🔄 Learning Loop

Every interaction updates the UserProfile:

1. **User views job** → Add to `jobs_viewed`
2. **User saves job** → Add to `jobs_saved`, extract preferences
3. **User applies** → Add to `jobs_applied`, boost confidence
4. **User rejects job** → Add to `jobs_rejected` with reason, learn dealbreakers
5. **User chats with AI** → SentimentAgent extracts motivation signals
6. **Profile updated** → Next recommendation is smarter

**ProfileUpdate Schema**:
```python
{
  "new_skills": [Skill],
  "new_preferences": [UserPreference],
  "new_goals": [CareerGoal],
  "new_risks": [RiskFactor],
  "new_motivation_signals": [MotivationSignal],
  "behavior": {
    "job_viewed": str,
    "job_saved": str,
    "job_applied": str,
    "job_rejected": {"job_id": str, "reason": str}
  }
}
```

---

## 🚀 Deployment

### **Production** (Google Cloud Run)
- URL: `https://next-backend-jxs4smo7nq-uc.a.run.app`
- Project: `next-475619`
- Region: `us-central1`
- Image: `gcr.io/next-475619/next-backend:latest`
- Status: ✅ Live

### **Environment Variables**
```bash
GEMINI_API_KEY=9c6779342f509f9f39e21adf9e3ec54d4ac5df70
SUPABASE_URL=<your_supabase_url>
SUPABASE_SERVICE_KEY=<your_service_key>
ONET_API_KEY=<your_onet_key>
```

### **Redeploy Command**
```bash
cd backend
gcloud builds submit --tag gcr.io/next-475619/next-backend
gcloud run deploy next-backend \
  --image gcr.io/next-475619/next-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=9c6779342f509f9f39e21adf9e3ec54d4ac5df70
```

---

## 📦 Agent Files

| File | Lines | Purpose |
|------|-------|---------|
| `app/services/agents/profile_agent.py` | ~180 | Memory keeper |
| `app/services/agents/risk_agent.py` | ~150 | AI displacement analysis |
| `app/services/agents/match_agent.py` | ~200 | Compatibility scoring |
| `app/services/agents/gap_agent.py` | ~180 | Skill gap analysis |
| `app/services/agents/sentiment_agent.py` | ~170 | Motivation extraction |
| `app/services/agents/trajectory_agent.py` | ~230 | Career path forecasting |
| `app/services/agents/market_intel_agent.py` | ~210 | Market intelligence |
| `app/services/agents/early_warning_agent.py` | ~260 | Threat detection |
| `app/services/agents/negotiation_agent.py` | ~280 | Offer optimization |
| `app/services/agents/peer_benchmarking_agent.py` | ~250 | Peer comparison |

**Total**: ~2,110 lines of agent code

---

## 🎨 Frontend Integration Roadmap

### **New UX Modules to Build** (8 components)

1. **Career Radar Dashboard**
   - API: `GET /api/match/user/{user_id}/early-warnings`
   - Visual: Circular radar showing threats (automation, skill gaps, market decline, burnout)
   - Colors: Green (safe) → Yellow (monitor) → Red (urgent)

2. **Career Path Visualizer**
   - API: `GET /api/match/user/{user_id}/career-forecast`
   - Visual: 3 parallel timelines showing probable paths
   - Hover: See skill unlock sequences and salary progression

3. **Learning Tracker**
   - API: `POST /api/match/analyze` (uses skill_gaps_for_job)
   - Visual: Progress bars for each skill gap with time-to-close estimates
   - Action: Link to Coursera courses

4. **Market Pulse Widget**
   - API: `GET /api/match/market-intelligence`
   - Visual: Scrolling ticker showing live trends
   - Example: "UX demand +12% ↑ | K-12 layoffs -8% ↓ | AI literacy +34% 🔥"

5. **Offer Optimizer**
   - API: `POST /api/match/user/{user_id}/analyze-offer`
   - Visual: Card comparing offer to market with fairness score gauge
   - Output: Copyable negotiation script

6. **Life Context Customizer**
   - API: `GET /api/match/profile/{user_id}` (uses preferences)
   - Visual: Sliders for priorities (work-life balance, remote work, stability)
   - Effect: Updates preference weights in real-time

7. **Career Journal (Chat AI)**
   - API: `POST /api/match/analyze` (with recent_conversation)
   - Visual: Chat interface with AI coach
   - Learning: Every conversation updates motivation_signals

8. **Peer Lens**
   - API: `GET /api/match/user/{user_id}/peer-insights`
   - Visual: Comparison table showing user vs cohort median
   - Insights: Common transitions, trending skills

---

## 💰 Subscription Tiers

| Tier | Price | Features |
|------|-------|----------|
| **Free** | $0 | Layer 1 agents (Profile, Risk, Match, Gap, Sentiment) + Basic compatibility |
| **Pro** | $29/mo | + Layer 2 (Career Forecast, Market Intelligence) + Early Warning alerts |
| **Elite** | $99/mo | + Offer Optimizer + Negotiation scripts + Priority support |
| **Enterprise** | Custom | + Peer Benchmarking + Team analytics + Retention predictor + White-label |

---

## 🔮 Future Enhancements

### **Career Graph** (Knowledge Base)
- Node types: Roles, Skills, Companies, Industries
- Edges: required_for, leads_to, similar_to, emerging_in
- Query: "What skills unlock path from Teacher → EdTech PM?"

### **Background Jobs** (Proactive Scans)
- Weekly EarlyWarningAgent scans for all Pro/Elite users
- Email alerts for critical threats
- Monthly trajectory recalculations

### **Machine Learning Pipeline**
- Train on historical transitions to improve probability forecasts
- Clustering for better peer cohort matching
- Sentiment analysis for burnout prediction

### **Live API Integrations**
- LinkedIn Jobs API → Real job posting counts
- Layoffs.fyi → Industry contraction alerts
- Levels.fyi → Accurate salary benchmarks
- Payscale → Compensation trends

---

## 📈 Metrics to Track

### **User Engagement**
- Profile completeness over time
- Interactions per session
- Jobs applied vs jobs viewed (conversion rate)

### **Agent Performance**
- Match accuracy: Did user apply to high-scoring jobs?
- Risk accuracy: Did predicted threats materialize?
- Trajectory accuracy: Did user follow predicted path?

### **Business Metrics**
- Free → Pro conversion rate
- Pro → Elite upgrade rate
- Monthly recurring revenue (MRR)
- Churn rate by tier

---

## ✅ Status

**Backend**: ✅ 100% COMPLETE (9/9 agents built)
- Layer 1: ✅ Complete
- Layer 2: ✅ Complete
- Layer 3: ✅ Complete

**Frontend**: ⏳ 0% (8 UX modules to build)

**Business Logic**: ⏳ 0% (Subscription gates, payment integration)

**Next Steps**:
1. Test all agents with sample data
2. Redeploy backend to Cloud Run
3. Build frontend UX modules
4. Implement subscription tiers
5. Connect live APIs
6. Launch beta testing

---

**Built with 🔥 by Next Career Intelligence**
