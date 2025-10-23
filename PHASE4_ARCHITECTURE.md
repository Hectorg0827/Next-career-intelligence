# 🚀 PHASE 4: JOB MARKETPLACE ARCHITECTURE

**Phase Status:** Ready to Start
**Estimated Duration:** 3-5 days
**Dependency:** Phase 1-3 Complete ✅

---

## 📊 Phase 4 Overview

Transform NEXT from a Career Coaching platform into a **complete AI-powered Career Intelligence Platform** with intelligent job matching, applications tracking, and AI-driven recommendations.

### Core Feature: AI-Powered Job Marketplace
- **Intelligent Job Matching**: Users get job recommendations based on their career goals and AI analysis
- **Job Search Interface**: Powerful search with filters (salary, location, experience level, skills)
- **Application Tracking**: Track applications, interviews, and outcomes
- **AI Interview Prep**: Practice interviewing for specific roles
- **Salary Intelligence**: Real-time salary data integrated with O*NET
- **Career Path Visualization**: See how specific jobs fit into user's career roadmap

---

## 🏗️ ARCHITECTURE

### Database Schema (New Tables)

#### 1. `Job` Table
```sql
CREATE TABLE jobs (
    id UUID PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    company VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    requirements TEXT,
    
    -- Location & Type
    location VARCHAR(255),
    remote_type VARCHAR(50), -- on_site, hybrid, remote
    job_type VARCHAR(50), -- full_time, part_time, contract
    
    -- Compensation
    salary_min DECIMAL(10, 2),
    salary_max DECIMAL(10, 2),
    salary_currency VARCHAR(3),
    
    -- Skills & Requirements
    required_skills JSON, -- ["Python", "FastAPI", "PostgreSQL"]
    nice_to_have_skills JSON,
    years_experience_min INTEGER,
    years_experience_max INTEGER,
    
    -- Source & Links
    source_url VARCHAR(512),
    source_platform VARCHAR(100), -- linkedin, indeed, builtin, etc
    external_id VARCHAR(255), -- Job ID from source platform
    
    -- Career Level
    career_level VARCHAR(50), -- entry, junior, mid, senior, lead, executive
    
    -- Metadata
    posted_date TIMESTAMP,
    last_updated TIMESTAMP,
    is_active BOOLEAN,
    ai_relevance_score DECIMAL(3, 2), -- 0.0-1.0
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### 2. `JobApplication` Table
```sql
CREATE TABLE job_applications (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    job_id UUID NOT NULL REFERENCES jobs(id),
    
    -- Application Status
    status VARCHAR(50), -- saved, applied, interviewing, rejected, offered, accepted
    
    -- Interview Tracking
    interview_stage VARCHAR(50), -- phone_screen, technical, behavioral, final
    interview_date TIMESTAMP,
    interview_notes TEXT,
    
    -- AI Analysis
    match_score DECIMAL(3, 2), -- 0.0-1.0 (AI calculated relevance)
    skill_gaps JSON, -- ["Docker", "Kubernetes"]
    recommended_prep JSON, -- Interview tips specific to role
    
    -- Outcomes
    rejection_reason VARCHAR(255),
    rejection_date TIMESTAMP,
    offer_date TIMESTAMP,
    offer_salary DECIMAL(10, 2),
    accepted_date TIMESTAMP,
    
    -- Metadata
    applied_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(user_id, job_id)
);
```

#### 3. `SavedJob` Table
```sql
CREATE TABLE saved_jobs (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    job_id UUID NOT NULL REFERENCES jobs(id),
    
    -- Metadata
    saved_at TIMESTAMP DEFAULT NOW(),
    notes VARCHAR(500), -- Why user saved this job
    
    UNIQUE(user_id, job_id)
);
```

#### 4. `JobAlertPreference` Table
```sql
CREATE TABLE job_alert_preferences (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Search Criteria
    job_titles JSON, -- ["Software Engineer", "Senior Developer"]
    locations JSON, -- ["San Francisco", "New York"]
    remote_preference VARCHAR(50),
    job_types JSON, -- ["full_time", "contract"]
    
    -- Compensation Range
    salary_min DECIMAL(10, 2),
    salary_max DECIMAL(10, 2),
    
    -- Skills
    required_skills JSON,
    nice_to_have_skills JSON,
    
    -- Experience
    years_experience_min INTEGER,
    years_experience_max INTEGER,
    
    -- Frequency
    alert_frequency VARCHAR(50), -- daily, weekly, never
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### 5. `JobRecommendation` Table
```sql
CREATE TABLE job_recommendations (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    job_id UUID NOT NULL REFERENCES jobs(id),
    
    -- AI Analysis
    match_score DECIMAL(3, 2), -- 0.0-1.0
    match_reason TEXT, -- "Your backend skills align well with this role"
    skill_alignment JSON,
    growth_opportunity DECIMAL(3, 2), -- 0.0-1.0 (career growth potential)
    
    -- Metadata
    recommended_at TIMESTAMP DEFAULT NOW(),
    user_viewed BOOLEAN DEFAULT FALSE,
    viewed_at TIMESTAMP,
    user_saved BOOLEAN DEFAULT FALSE,
    user_applied BOOLEAN DEFAULT FALSE,
    
    is_active BOOLEAN DEFAULT TRUE
);
```

### Modify `Conversation` Table
Add field to support job-related conversations:
```sql
ALTER TABLE conversations ADD COLUMN context_type VARCHAR(50); -- 'career', 'job_preparation', 'salary_negotiation'
ALTER TABLE conversations ADD COLUMN related_job_id UUID REFERENCES jobs(id);
```

---

## 🤖 AI MATCHING ALGORITHM

### Core Algorithm: Vector-Based Job Matching

```python
class JobMatcher:
    """
    AI-powered job matching using embeddings and semantic similarity
    """
    
    def calculate_match_score(self, user_profile, job) -> float:
        """
        Returns match score 0.0 to 1.0
        """
        scores = {
            'skill_match': self.skill_similarity(user_profile.skills, job.required_skills),
            'experience_match': self.experience_compatibility(user_profile.experience, job.years_experience),
            'salary_match': self.salary_alignment(user_profile.salary_expectations, job.salary_range),
            'location_match': self.location_preference(user_profile.location_preference, job.location),
            'career_path_match': self.career_goal_alignment(user_profile.career_goals, job),
            'growth_potential': self.learning_opportunity(user_profile.skill_gaps, job.required_skills),
        }
        
        # Weighted average
        weights = {
            'skill_match': 0.30,
            'experience_match': 0.20,
            'salary_match': 0.15,
            'location_match': 0.10,
            'career_path_match': 0.15,
            'growth_potential': 0.10,
        }
        
        score = sum(scores[key] * weights[key] for key in scores)
        return min(max(score, 0.0), 1.0)  # Clamp to 0.0-1.0
    
    def skill_similarity(self, user_skills, required_skills) -> float:
        """Using Gemini embeddings for semantic similarity"""
        user_embedding = embed_skills(user_skills)
        job_embedding = embed_skills(required_skills)
        return cosine_similarity(user_embedding, job_embedding)
    
    def experience_compatibility(self, years, required_years) -> float:
        """Flexibility around years of experience"""
        if not required_years:
            return 1.0
        
        min_req, max_req = required_years
        if years < min_req * 0.8:  # 20% below minimum
            return max(0.0, (years / (min_req * 0.8)))
        elif years > max_req * 1.5:  # 50% above maximum
            return 0.7 + 0.3 * (1 / (1 + (years - max_req) / max_req))
        else:
            return 1.0
```

### Key Matching Components:

1. **Skill-Based Matching**
   - Semantic similarity using Gemini embeddings
   - Identifies transferable skills
   - Calculates skill gaps for learning

2. **Experience Matching**
   - Flexible experience level checking
   - Accounts for overqualification
   - Considers transferable experience

3. **Salary Alignment**
   - Matches user salary expectations with job range
   - Considers cost of living by location
   - Flags significant mismatches

4. **Career Path Integration**
   - Uses user's career goals from AI Coach
   - Evaluates how job fits into roadmap
   - Identifies growth opportunities

5. **Location Intelligence**
   - Remote work preferences
   - Geographic constraints
   - Cost of living considerations

---

## 📱 FRONTEND COMPONENTS (NEW)

### Page Structure:
```
/app/jobs/
├── page.tsx                 # Job search/browse interface
├── [jobId]/
│   └── page.tsx            # Individual job detail page
├── recommendations/
│   └── page.tsx            # AI-recommended jobs for user
├── applications/
│   └── page.tsx            # Job applications tracking
└── alerts/
    └── page.tsx            # Job alert preferences

/app/coach/
└── interview-prep/
    └── [jobId]/
        └── page.tsx        # AI interview practice for specific job
```

### Component Architecture:

**1. Job Search Component** (`jobs/page.tsx`)
```typescript
- Search bar with autocomplete
- Filter sidebar
  - Location (with map view option)
  - Salary range slider
  - Job type checkboxes
  - Remote preference
  - Skills filter
  - Experience level
- Job cards with quick apply
- Saved jobs button
- View application status
```

**2. Job Detail Component** (`jobs/[jobId]/page.tsx`)
```typescript
- Full job description
- Company information card
- AI Match Score badge
  - Skill alignment visualization
  - Career fit assessment
  - Skill gaps list
  - Recommended interview prep
- Apply button
- Save button
- Share button
- AI Coach "Ask about this job" button
```

**3. Job Recommendations Component** (`jobs/recommendations/page.tsx`)
```typescript
- Personalized AI job matches
- Filter by match score
- Sort by (newest, best match, salary, growth)
- Quick apply
- "Why this match?" explanation
- Save/unsave
- Apply status tracking
```

**4. Applications Tracking Component** (`jobs/applications/page.tsx`)
```typescript
- Kanban board view (Saved → Applied → Interviewing → Offered → Accepted)
- Application cards with:
  - Job title & company
  - Application status
  - Last update date
  - Interview stage
  - AI prep recommendations
- Interview date calendar
- Offer details view
- Rejection notes
```

**5. Job Alerts Component** (`jobs/alerts/page.tsx`)
```typescript
- Create/edit alert preferences
- Set search criteria
- Notification frequency
- Alert history
- Enable/disable alerts
```

**6. Interview Prep Component** (`coach/interview-prep/[jobId]/page.tsx`)
```typescript
- Role-specific interview questions
- AI practice chat
- Common interview patterns for role
- Salary negotiation tips
- Company research highlights
- Follow-up questions practice
```

---

## 🔌 BACKEND API ENDPOINTS (NEW)

### Job Management Endpoints
```python
# Job Search & Discovery
GET    /api/jobs/search?title=&location=&skills=
GET    /api/jobs/{job_id}
GET    /api/jobs/recommendations
GET    /api/jobs/recommended?limit=10
POST   /api/jobs/search/advanced  # Advanced filtering

# Job Applications
POST   /api/jobs/{job_id}/apply
GET    /api/jobs/applications
GET    /api/jobs/applications/{app_id}
PUT    /api/jobs/applications/{app_id}  # Update status
DELETE /api/jobs/applications/{app_id}

# Saved Jobs
POST   /api/jobs/{job_id}/save
DELETE /api/jobs/{job_id}/save
GET    /api/jobs/saved

# Job Alerts
POST   /api/jobs/alerts
GET    /api/jobs/alerts
PUT    /api/jobs/alerts/{alert_id}
DELETE /api/jobs/alerts/{alert_id}

# AI Analysis
POST   /api/jobs/{job_id}/analyze      # Get AI analysis for a job
GET    /api/jobs/{job_id}/match-score  # User's match score
GET    /api/jobs/{job_id}/interview-tips

# Admin Endpoints
POST   /api/admin/jobs/import          # Bulk import jobs
POST   /api/admin/jobs/update-from-source  # Sync with job platforms
```

### Models & Schemas
```python
# schemas.py additions

class JobBase(BaseModel):
    title: str
    company: str
    description: str
    location: str
    salary_min: Optional[float]
    salary_max: Optional[float]
    required_skills: List[str]

class JobResponse(JobBase):
    id: UUID
    match_score: Optional[float]  # For user-specific responses
    created_at: datetime

class JobApplicationRequest(BaseModel):
    job_id: UUID

class JobApplicationResponse(BaseModel):
    id: UUID
    user_id: UUID
    job_id: UUID
    status: str
    match_score: float
    applied_at: datetime

class JobRecommendation(BaseModel):
    job_id: UUID
    match_score: float
    match_reason: str
    skill_alignment: Dict[str, float]
```

---

## 🔄 DATA FLOW ARCHITECTURE

### Job Recommendation Flow
```
1. User Profile Updated
   ↓
2. Trigger Job Re-Matching Service
   ↓
3. Calculate Match Scores
   - Skill matching (Gemini embeddings)
   - Experience compatibility
   - Salary alignment
   - Location preferences
   - Career path fit
   ↓
4. Update job_recommendations table
   ↓
5. Send email alerts (if job_alert_preferences.alert_frequency = daily/weekly)
   ↓
6. Display recommendations in UI
```

### Application Tracking Flow
```
1. User Clicks "Apply" on Job
   ↓
2. Create job_application record (status: applied)
   ↓
3. Optionally trigger email to user (confirmation)
   ↓
4. User can update application status (interviewing, rejected, offered)
   ↓
5. AI Coach can prepare interview questions for specific job
   ↓
6. Track outcomes (accepted, rejected)
   ↓
7. Generate career insights (success rate, pattern analysis)
```

---

## 📊 DATA SOURCES FOR JOBS

### Integration Options:

1. **LinkedIn Jobs API**
   - Real-time job data
   - Company info
   - Salary data (premium)

2. **Indeed API**
   - Large job database
   - Structured data
   - Location-based search

3. **BuildIn.com API**
   - Tech jobs specifically
   - Company culture
   - Remote-first jobs

4. **O*NET Integration** (Already configured!)
   - Career path information
   - Skill requirements
   - Salary data by location
   - Career transitions

5. **Manual Seeding**
   - Test data during development
   - Premium job board partnerships

---

## 🎯 IMPLEMENTATION ROADMAP

### Week 1 (Days 1-2): Backend Foundation
- [ ] Create database schema (5 new tables)
- [ ] Implement Job model & schemas
- [ ] Build job search endpoints
- [ ] Create AI matching algorithm
- [ ] Write unit tests

### Week 1 (Day 3): Frontend Part 1
- [ ] Create job search page
- [ ] Build job detail page
- [ ] Create job recommendation page
- [ ] Implement filters & search

### Week 1 (Day 4): Frontend Part 2 + Integration
- [ ] Build application tracking page
- [ ] Create job alerts page
- [ ] Integrate with backend API
- [ ] End-to-end testing

### Week 2 (Day 5+): Polish & Advanced Features
- [ ] AI interview prep integration
- [ ] Email notifications
- [ ] Analytics dashboard
- [ ] Performance optimization
- [ ] Production deployment

---

## 🧪 TESTING STRATEGY

### Unit Tests
- AI matching algorithm accuracy
- Filter logic
- Data validation

### Integration Tests
- API endpoints with database
- Search functionality
- Application flow

### E2E Tests
- Complete job search flow
- Apply to job flow
- Recommendations display
- Application tracking

### Performance Tests
- Job search with 100k+ jobs
- Real-time recommendations
- Match score calculations

---

## 📈 PHASE 4 SUCCESS CRITERIA

- ✅ Users can search and filter 10,000+ jobs
- ✅ AI matching algorithm achieves 85%+ accuracy
- ✅ Job recommendations delivered within 2 seconds
- ✅ Full application tracking workflow
- ✅ Interview prep for specific jobs
- ✅ Email alerts working
- ✅ 0 critical bugs
- ✅ All tests passing (>85% coverage)

---

## 🚀 LAUNCH READINESS

**Phase 4 Completion** = **NEXT Career Intelligence v1.0**

Complete AI-powered career platform:
1. ✅ Phase 1: Premium Subscriptions (Payments)
2. ✅ Phase 2: User Management & Auth
3. ✅ Phase 3: AI Career Coach with Persistence
4. ✅ **Phase 4: Job Marketplace with AI Matching**

**Ready for:**
- Production deployment
- Major user acquisition
- Media launch
- B2B partnerships

---

## 💡 FUTURE ENHANCEMENTS (Post-v1.0)

- AI salary negotiation coach
- LinkedIn profile optimization
- Resume feedback with AI
- Networking recommendations
- Career transition planning
- Skill marketplace (users can hire other users for practice)
- Company reviews and culture analysis
- Equity calculator for startup jobs
- Interview scheduling integration

---

**Phase 4 Status:** 🎯 Ready to Build
**Estimated Start:** Immediately after Stripe completion
**Expected Completion:** 3-5 days of active development
