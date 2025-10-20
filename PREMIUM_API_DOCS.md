# NEXT Career Intelligence - Premium API Documentation

## Overview

This document describes the premium features added to the NEXT Career Intelligence platform:

1. **Resume Studio** - Single source of truth for career profiles
2. **Career Coach** - AI coaching with read-only profile access
3. **Interviewer AI** - STAR interview practice with evidence extraction

All premium features use **Google Gemini API** as the LLM backend and **Supabase** for data storage.

---

## Architecture

### Data Flow

```
Resume Studio (SSOT - Authoritative)
     ↓ (read-only)
Career Coach → generates suggestions → user approves → Resume Studio applies
     ↓ (read-only)
Interviewer AI → generates suggestions → user approves → Resume Studio applies
```

### Key Principles

1. **Resume Studio** is the **single source of truth** for career profiles
2. **Coach** and **Interviewer** have **READ-ONLY** access to profiles
3. All profile changes require **explicit user approval**
4. Privacy and safety guardrails are built into every endpoint

---

## API Endpoints

### Resume Studio API (`/api/resume-studio`)

#### POST `/api/resume-studio/ingest`
**Purpose:** Parse resume/LinkedIn text into normalized career profile

**Request:**
```json
{
  "text": "Resume text or LinkedIn profile content",
  "file_id": null,
  "linkedin_url": null,
  "user_id": "user_123",
  "privacy_consent": {
    "store_profile": true,
    "ai_processing": true,
    "data_retention": true
  },
  "user_region": "US"
}
```

**Response:**
```json
{
  "validation_summary": "Parsed 3 roles (2019–Present). No conflicts found.",
  "profile_patch_json": {
    "basics": { "full_name": "Jane Doe", ... },
    "work_history": [...],
    "education": [...],
    "skills": {"hard": [...], "soft": [...]}
  },
  "open_questions": [
    "What was the end date for Role X?",
    "Can you add a metric for the project?"
  ],
  "conflicts": [],
  "privacy_summary": { ... },
  "safety_flags": []
}
```

**Key Features:**
- Parses text into ATS-normalized structure
- Detects conflicts (date overlaps, missing info)
- Returns `open_questions` for user clarification
- Privacy filtering (redacts PII based on region)
- Safety checks (blocks harmful content)

---

#### POST `/api/resume-studio/tailor`
**Purpose:** Tailor resume for specific job description

**Request:**
```json
{
  "user_id": "user_123",
  "job_description": {
    "title": "Senior Product Manager",
    "company": "Acme Corp",
    "seniority": "Senior",
    "location": "Remote",
    "must_haves": ["Product strategy", "Stakeholder management"],
    "nice_to_haves": ["B2B SaaS experience"],
    "keywords": ["roadmap", "OKRs", "user research"],
    "industry": "B2B SaaS",
    "region": "US"
  }
}
```

**Response:**
```json
{
  "resume": {
    "summary": "2-4 line summary aligned to JD",
    "core_skills": {
      "business": ["Product Strategy", "Roadmap Planning"],
      "leadership": ["Stakeholder Management"],
      "tools": ["JIRA", "Amplitude"]
    },
    "experience": [
      {
        "company": "Previous Company",
        "title": "Product Manager",
        "dates": "Jan 2020 - Present",
        "bullets": [
          "Led product strategy for B2B platform serving 500+ enterprise clients",
          "Aligned cross-functional teams (Engineering, Design, Sales) on quarterly OKRs"
        ]
      }
    ]
  },
  "ats_notes": ["dates normalized", "US spelling", "no tables"],
  "risk_flags": ["gap: specific tool X"],
  "keyword_coverage": {
    "matched": ["product strategy", "stakeholder management", "B2B SaaS"],
    "missing": ["user research metrics"],
    "coverage_percentage": 85
  },
  "placeholders": ["confirm exact user count for platform"]
}
```

---

#### POST `/api/resume-studio/cover-letter/tailor`
**Purpose:** Generate tailored cover letter

**Request:**
```json
{
  "user_id": "user_123",
  "job_description": { ... }
}
```

**Response:**
```json
{
  "cover_letter": {
    "salutation": "Hiring Manager",
    "opening": "Hook with quantified win aligned to must-have",
    "body": [
      "Relevance paragraph",
      "Proof paragraph (STAR mini-story)",
      "Values/fit paragraph"
    ],
    "closing": "CTA + availability",
    "signature_block": "Name | Phone | Email | LinkedIn"
  },
  "word_count": 275,
  "tone": "professional"
}
```

---

### Career Coach API (`/api/coach`)

#### POST `/api/coach/chat`
**Purpose:** Chat with Career Coach AI (read-only to profile)

**Request:**
```json
{
  "user_id": "user_123",
  "message": "How can I improve my resume to transition into data science?",
  "conversation_id": null,
  "conversation_type": "skill_discovery"
}
```

**Response:**
```json
{
  "conversation_id": "conv_456",
  "reply": "Based on your background in business analytics, you already have strong foundations in Excel and SQL. Here's how you can bridge the gap to data science...",
  "profile_patch_suggestions": [
    {
      "source": "coach",
      "suggestion_type": "skill",
      "proposed_patch": {
        "path": "skills.hard",
        "operation": "add",
        "value": "Data Storytelling"
      },
      "evidence": "User mentioned creating executive dashboards",
      "confidence_score": 0.85,
      "reasoning": "This implicit skill should be explicitly listed"
    }
  ],
  "goal_updates": [
    {
      "goal_title": "Learn Python for data analysis",
      "specific": "Complete 3 data projects using pandas",
      "measurable": "3 documented projects",
      "time_bound": "3 months"
    }
  ],
  "next_actions": [
    "Add 'Data Storytelling' to LinkedIn (5 min)",
    "Draft bullet about dashboard project (10 min)",
    "Research Python courses (15 min)"
  ]
}
```

**Key Features:**
- Conversational coaching
- Generates non-authoritative suggestions
- Suggests SMART goals
- Provides 1-3 doable next actions (≤15 minutes)
- Does NOT modify profile directly

---

#### POST `/api/coach/goals`
**Purpose:** Create a new career goal

**Request:**
```json
{
  "user_id": "user_123",
  "goal": {
    "goal_title": "Become proficient in Python for data analysis",
    "goal_type": "skill_acquisition",
    "specific": "Complete 3 data analysis projects using pandas and matplotlib",
    "measurable": "3 completed projects with documented code",
    "achievable": "Build on existing Excel skills",
    "relevant": "Aligns with data analyst transition goal",
    "time_bound": "3 months",
    "status": "active",
    "progress_percentage": 0,
    "milestones": [
      {
        "title": "Complete Python fundamentals course",
        "completed": false
      }
    ]
  }
}
```

**Response:**
```json
{
  "id": "goal_789",
  "user_id": "user_123",
  "goal_data": { ... },
  "created_at": "2025-10-20T10:00:00Z",
  "updated_at": "2025-10-20T10:00:00Z"
}
```

---

#### GET `/api/coach/goals/{user_id}`
**Purpose:** Get all career goals for a user

**Response:**
```json
{
  "goals": [ ... ],
  "active_count": 3,
  "completed_count": 1
}
```

---

### Interviewer AI API (`/api/interviewer`)

#### POST `/api/interviewer/start`
**Purpose:** Start a new interview session

**Request:**
```json
{
  "user_id": "user_123",
  "role_title": "Product Manager",
  "company_name": "Acme Corp",
  "job_description": { ... },
  "interview_type": "behavioral"
}
```

**Response:**
```json
{
  "session_id": "session_abc",
  "role_title": "Product Manager",
  "company_name": "Acme Corp",
  "interview_type": "behavioral",
  "questions": [
    {
      "question": "Tell me about a time when you had to manage conflicting stakeholder priorities.",
      "user_response": null
    },
    {
      "question": "Describe a product launch that didn't go as planned. What did you do?",
      "user_response": null
    }
  ],
  "evidence_summaries": [],
  "generated_suggestions": [],
  "status": "in_progress",
  "created_at": "2025-10-20T10:00:00Z"
}
```

---

#### POST `/api/interviewer/answer`
**Purpose:** Submit answer to interview question

**Request:**
```json
{
  "session_id": "session_abc",
  "user_id": "user_123",
  "question_index": 0,
  "answer": "At my previous company, I led a product launch where Engineering wanted to delay for quality, while Sales needed to meet a client deadline. I facilitated a meeting where we identified a minimum viable scope that satisfied both teams. We shipped on time with core features, then followed up with enhancements in the next sprint. The client was happy, and we maintained code quality."
}
```

**Response:**
```json
{
  "success": true,
  "evidence_extracted": true,
  "follow_up_question": "Can you quantify the impact? How many clients or users were affected?",
  "star_breakdown": {
    "situation": "Conflicting priorities between Engineering (quality) and Sales (deadline)",
    "task": "Need to ship product on time while maintaining quality",
    "action": "Facilitated meeting, identified MVP scope, coordinated phased rollout",
    "result": "Shipped on time, client satisfied, quality maintained"
  }
}
```

---

#### POST `/api/interviewer/complete`
**Purpose:** Complete interview and generate resume bullet suggestions

**Request:**
```json
{
  "session_id": "session_abc",
  "user_id": "user_123"
}
```

**Response:**
```json
{
  "session_id": "session_abc",
  "role_title": "Product Manager",
  "interview_type": "behavioral",
  "questions": [ ... ],
  "evidence_summaries": [
    {
      "summary": "Led cross-functional team to deliver MVP on time while managing conflicting stakeholder priorities",
      "metric": "on-time delivery, satisfied client",
      "confidence": 0.9,
      "source_question_index": 0
    }
  ],
  "generated_suggestions": [
    {
      "source": "interviewer",
      "suggestion_type": "bullet",
      "proposed_patch": {
        "path": "work_history[0].bullets",
        "operation": "add",
        "value": "Led cross-functional team (Engineering, Sales) to deliver product MVP on time, resolving competing priorities through facilitated scope definition and phased rollout"
      },
      "evidence": "From Q1 response about stakeholder management",
      "confidence_score": 0.9,
      "reasoning": "Strong example aligned to JD requirement for stakeholder management"
    }
  ],
  "status": "completed",
  "created_at": "2025-10-20T10:00:00Z",
  "completed_at": "2025-10-20T10:30:00Z"
}
```

---

## Database Schema

### Premium Tables (Supabase)

1. **career_profiles** - Single source of truth for user career data
2. **resume_artifacts** - Tailored resumes and cover letters
3. **profile_suggestions** - Suggestions from Coach/Interviewer (require approval)
4. **career_goals** - User's SMART goals
5. **interview_sessions** - Interview practice sessions
6. **coach_conversations** - Coaching conversation history
7. **subscriptions** - User subscription tiers (free/premium/enterprise)

See [database_schema.sql](./database_schema.sql) for full DDL.

---

## Subscription Tiers

### Free Tier
- Basic career analysis
- Job search
- Limited AI features

### Premium Tier (Paid)
- ✅ **Resume Studio** - Unlimited profile parsing and tailoring
- ✅ **Career Coach** - Unlimited coaching conversations
- ✅ **Interviewer AI** - Interview practice with STAR extraction
- ✅ **Career Goals** - Goal tracking and management
- ✅ **Profile Suggestions** - AI-powered improvement suggestions

### Enterprise Tier
- All Premium features
- Priority support
- Team management
- Custom integrations

---

## Safety & Privacy

### Built-in Guardrails

1. **Scope Enforcement** - Agents only handle career-related content
2. **PII Protection** - Auto-redacts sensitive data based on region (GDPR, CCPA, PDPA, etc.)
3. **Content Filtering** - Blocks harmful, discriminatory, or illegal content
4. **Fake Credentials Prevention** - Rejects requests for false information
5. **Consent Management** - Explicit user consent required for data processing

### Regional Compliance

- **GDPR (EU/EEA)** - Right to erasure, data minimization, 30-day breach notification
- **CCPA (California)** - Opt-out rights, deletion requests
- **PDPA (Singapore)** - Consent, purpose limitation
- **APPI (Japan)** - Proper acquisition, security measures
- **PIPL (China)** - Explicit consent, data localization

---

## Usage Examples

### Example 1: Complete Resume Studio Flow

```bash
# 1. Ingest resume
curl -X POST http://localhost:8000/api/resume-studio/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "text": "John Doe\nProduct Manager with 5 years experience...",
    "user_id": "user_123"
  }'

# 2. Tailor for job
curl -X POST http://localhost:8000/api/resume-studio/tailor \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "job_description": {
      "title": "Senior PM",
      "company": "Acme",
      "must_haves": ["Product strategy"],
      "region": "US"
    }
  }'

# 3. Generate cover letter
curl -X POST http://localhost:8000/api/resume-studio/cover-letter/tailor \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "job_description": { ... }
  }'
```

### Example 2: Career Coach Flow

```bash
# 1. Chat with coach
curl -X POST http://localhost:8000/api/coach/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "message": "How can I transition into data science?",
    "conversation_type": "skill_discovery"
  }'

# 2. Create goal from coaching session
curl -X POST http://localhost:8000/api/coach/goals \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "goal": {
      "goal_title": "Learn Python",
      "goal_type": "skill_acquisition",
      "time_bound": "3 months"
    }
  }'
```

### Example 3: Interviewer AI Flow

```bash
# 1. Start interview
curl -X POST http://localhost:8000/api/interviewer/start \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "role_title": "Product Manager",
    "interview_type": "behavioral"
  }'

# 2. Answer questions
curl -X POST http://localhost:8000/api/interviewer/answer \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session_abc",
    "user_id": "user_123",
    "question_index": 0,
    "answer": "At my previous company..."
  }'

# 3. Complete and get suggestions
curl -X POST http://localhost:8000/api/interviewer/complete \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session_abc",
    "user_id": "user_123"
  }'
```

---

## Testing

### Run Server
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### Access API Docs
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Health Checks
- Resume Studio: http://localhost:8000/api/resume-studio/health
- Career Coach: http://localhost:8000/api/coach/health
- Interviewer AI: http://localhost:8000/api/interviewer/health

---

## Next Steps

### Frontend Integration
1. Create profile intake wizard in Next.js
2. Build suggestions inbox component
3. Implement coaching chat interface
4. Add interview practice simulator
5. Create goal tracking dashboard

### Backend Enhancements
1. Add user authentication (Firebase Auth)
2. Implement subscription management (Stripe)
3. Add file upload handling (PDF/DOCX parsing)
4. Implement caching (Redis) for performance
5. Add comprehensive logging and monitoring

---

## Support

For issues or questions:
- GitHub Issues: https://github.com/your-repo/issues
- Documentation: https://docs.yourplatform.com
- Email: support@yourplatform.com

---

**Built with:**
- FastAPI
- Google Gemini API
- Supabase
- Python 3.11+
