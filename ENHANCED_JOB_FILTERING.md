# Enhanced Job Filtering System

**Date:** October 20, 2025
**Status:** ✅ Implemented
**Version:** 2.0

---

## 🎯 Overview

The jobs marketplace now features **intelligent filtering** based on user requirements:

1. **Goals Alignment** - Match jobs to career goals
2. **Skill Match Threshold** - Filter by minimum skill overlap
3. **Distance-Based Filtering** - Location proximity for non-remote jobs
4. **AI Displacement Risk** - Show % probability of automation for each job
5. **Expand Search Option** - Loosen filters to see more opportunities

---

## 🔍 Filtering Criteria

### 1. Goals Alignment

**How it works:**
- System fetches user's active career goals from database
- For each job, calculates keyword overlap with goal titles/descriptions
- Scores job based on relevance to achieving goals
- Shows which goals each job helps achieve

**Example:**

**User Goal:** "Become a Technical Lead managing a team of 5+ engineers"

**Job Match:** "Senior Software Engineer - Team Lead"
- **Goal Relevance Score:** 60/100
- **Relevant Goals:** ["Become a Technical Lead"]
- **Overlap Keywords:** ["technical", "lead", "team", "engineers"]

**Job Match:** "Junior Developer"
- **Goal Relevance Score:** 0/100
- **Relevant Goals:** []
- **Overlap Keywords:** []

**Algorithm:**
```python
for goal in user_active_goals:
    goal_keywords = set(goal.title.split() + goal.description.split())
    job_keywords = set(job.title.split() + job.description.split())

    # Remove common words
    goal_keywords -= {'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'and', 'or'}
    job_keywords -= common_words

    overlap = len(goal_keywords & job_keywords)
    if overlap > 0:
        goal_relevance_score += 20  # Per matching goal
```

**Score Range:** 0-100 (capped)

---

### 2. Skill Match Threshold

**How it works:**
- Extracts user's skills from career profile
- Extracts required skills from job posting
- Calculates overlap percentage
- Filters out jobs below threshold

**Parameters:**
- `min_skill_match` (default: 30%)
  - 0-20%: Very loose, shows many jobs
  - 30-50%: Balanced, shows relevant jobs
  - 50-70%: Strict, highly qualified
  - 70-100%: Very strict, perfect matches only

**Example:**

**User Skills:**
```json
["Python", "React", "AWS", "Docker", "PostgreSQL", "REST APIs", "Git"]
```

**Job Requirements:**
```json
["Python", "Django", "AWS", "Docker", "PostgreSQL", "CI/CD"]
```

**Calculation:**
```python
user_skills = {"Python", "React", "AWS", "Docker", "PostgreSQL", "REST APIs", "Git"}
job_skills = {"Python", "Django", "AWS", "Docker", "PostgreSQL", "CI/CD"}

overlap = user_skills & job_skills  # {"Python", "AWS", "Docker", "PostgreSQL"}
skill_fit_score = (len(overlap) / len(job_skills)) * 100
# Result: (4 / 6) * 100 = 66.67%
```

**Skill Gaps Identified:**
- Django (required, user doesn't have)
- CI/CD (required, user doesn't have)

**Action:** If `min_skill_match=30`, this job passes. If `min_skill_match=70`, it's filtered out.

---

### 3. Distance-Based Filtering

**How it works:**
- Uses Haversine formula to calculate great-circle distance
- Filters non-remote jobs by maximum distance
- Remote jobs always pass distance filter

**Parameters:**
- `max_distance_km` (default: None = no limit)
  - 10 km: Same city only
  - 50 km: Nearby cities
  - 100 km: Regional
  - None: No distance restriction

**Haversine Formula:**
```python
def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points on Earth"""
    # Convert to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))

    # Earth radius in km
    r = 6371

    return r * c
```

**Example:**

**User Location:** San Francisco, CA (37.7749°N, 122.4194°W)

**Job 1:** Remote position at Seattle company
- **Distance:** N/A (remote)
- **Result:** ✅ Pass (remote jobs always pass)

**Job 2:** On-site in Palo Alto, CA (37.4419°N, 122.1430°W)
- **Distance:** ~35 km
- **Result:**
  - ✅ Pass if `max_distance_km=50`
  - ❌ Filtered if `max_distance_km=20`

**Job 3:** On-site in Los Angeles, CA (34.0522°N, 118.2437°W)
- **Distance:** ~559 km
- **Result:** ❌ Filtered if `max_distance_km=100`

**Location Data Sources:**
1. User preferences (`home_latitude`, `home_longitude`)
2. Career profile (`profile_data.latitude`, `profile_data.longitude`)
3. If missing, distance filter not applied

---

### 4. AI Displacement Risk

**How it works:**
- Analyzes job title, description, and seniority
- Scores automation risk from 5% (very safe) to 95% (high risk)
- Based on routine vs creative work, human interaction, technical complexity

**Risk Categories:**

**VERY HIGH RISK (70-90%)**
- Repetitive tasks
- Data entry, clerical work
- Call center operations
- Examples: "Data Entry Clerk", "Telemarketer"

**HIGH RISK (50-70%)**
- Standardized analysis
- Junior/entry-level roles
- Examples: "Junior Analyst", "QA Tester", "Bookkeeper"

**MEDIUM RISK (30-50%)**
- Mix of routine and creative
- Mid-level technical roles
- Examples: "Software Developer", "Designer", "Project Manager"

**LOW RISK (15-30%)**
- Leadership, strategy
- High human interaction
- Examples: "Senior Manager", "Sales Director", "Consultant"

**VERY LOW RISK (5-15%)**
- C-suite, executive
- Highly creative/strategic
- Examples: "CTO", "VP of Product", "Creative Director"

**Modifiers:**
- Seniority: Senior/Lead (-10%), Director/VP (-20%), Entry/Junior (+10%)
- Human interaction: Client-facing, team leadership (-5%)
- Technical complexity: Architecture, research, strategy (-5%)

**Algorithm:**
```python
def estimate_job_risk(job):
    risk_score = 50  # Start at medium

    title = job.title.lower()
    description = job.description.lower()

    # Check risk keywords
    if 'data entry' in title:
        risk_score = 80
    elif 'manager' in title or 'director' in title:
        risk_score = 25
    elif 'developer' in title:
        risk_score = 45

    # Adjust for seniority
    if job.seniority == 'senior':
        risk_score -= 10
    elif job.seniority == 'director':
        risk_score -= 20

    # Adjust for human interaction
    if 'client' in description or 'team' in description:
        risk_score -= 5

    return max(5, min(95, risk_score))
```

**Example Output:**

| Job Title | Seniority | AI Risk | Explanation |
|-----------|-----------|---------|-------------|
| Senior Software Engineer | Senior | 35% | Technical work with leadership, lower risk |
| Data Entry Specialist | Entry | 85% | Highly repetitive, high automation risk |
| Director of Engineering | Director | 15% | Strategic leadership, very low risk |
| Marketing Analyst | Mid | 55% | Standardized analysis, moderate risk |
| Sales Manager | Senior | 20% | High human interaction, low risk |

---

### 5. Expand Search Option

**How it works:**
- When `expand_search=true`, loosens filtering criteria
- Skill match threshold reduced by 20% (min 10%)
- Distance doubled (if applicable)
- Shows more opportunities beyond strict matches

**Example:**

**Strict Filters:**
```
min_skill_match = 50%
max_distance_km = 30 km
→ Result: 12 jobs
```

**Expanded Search:**
```
min_skill_match = 30%  (50% - 20%)
max_distance_km = 60 km  (30 km * 2)
→ Result: 47 jobs
```

**Use Cases:**
- Not enough matches with strict filters
- Exploring adjacent roles
- Open to stretch positions
- Considering relocation

---

## 📡 API Endpoint

### GET /api/jobs/recommendations

**Enhanced Parameters:**

```
GET /api/jobs/recommendations?
    min_skill_match=40.0&
    max_distance_km=50&
    expand_search=false&
    limit=20&
    refresh=false
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `user_id` | string | current user | Override user (admin only) |
| `refresh` | boolean | false | Force refresh, bypass cache |
| `limit` | integer | 20 | Max results (1-100) |
| `min_skill_match` | float | 30.0 | Minimum skill match % (0-100) |
| `max_distance_km` | float | None | Max distance in km (None = no limit) |
| `expand_search` | boolean | false | Loosen filters for more results |

**Response:**

```json
{
  "recommendations": [
    {
      "id": "job_uuid_123",
      "title": "Senior Software Engineer",
      "company": "TechCorp Inc",
      "location_city": "San Francisco",
      "location_type": "hybrid",
      "salary_min": 140000,
      "salary_max": 180000,
      "description": "...",
      "skills_extracted": ["Python", "AWS", "Docker"],

      "match_score": 87.5,
      "match_details": {
        "overall_score": 87.5,
        "skill_fit_score": 92.0,
        "trajectory_fit_score": 100.0,
        "value_match_score": 75.0,
        "logistics_fit_score": 90.0,
        "growth_potential_score": 80.0,
        "match_highlights": [
          "Strong technical skill match",
          "Perfect seniority progression",
          "Hybrid setup matches preference"
        ],
        "skill_gaps": ["Kubernetes", "GraphQL"],
        "why_matched": "This role aligns perfectly with your skillset and goals..."
      },

      "ai_displacement_risk": 35.0,
      "distance_km": 12.5,
      "goal_relevance_score": 60.0,
      "relevant_goals": [
        {
          "goal_id": "goal_uuid_456",
          "goal_title": "Become a Technical Lead",
          "overlap_keywords": ["senior", "engineer", "team", "lead"]
        }
      ]
    }
  ],

  "total": 15,
  "total_before_filtering": 200,

  "filters_applied": {
    "min_skill_match": 40.0,
    "max_distance_km": 50.0,
    "goals_count": 3,
    "expand_search": false
  },

  "user_goals": [
    {"id": "goal_1", "title": "Become a Technical Lead"},
    {"id": "goal_2", "title": "Master cloud architecture"},
    {"id": "goal_3", "title": "Contribute to open source"}
  ],

  "profile_id": "profile_uuid_789"
}
```

---

## 🎨 Frontend UI Recommendations

### Jobs List View

```
┌─────────────────────────────────────────────────────────────┐
│  🔍 Job Recommendations for You                   [Filters] │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Showing 15 jobs matching your goals and skills             │
│  Your Goals: Become Technical Lead | Master Cloud | OSS     │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Senior Software Engineer - Team Lead        87% ⭐  │   │
│  │ TechCorp Inc • San Francisco, CA • Hybrid           │   │
│  │                                                      │   │
│  │ Match: 87% | 🎯 Goals: 1 | 📍 12 km | 🤖 Risk: 35% │   │
│  │                                                      │   │
│  │ ✅ Python, AWS, Docker                              │   │
│  │ ❌ Kubernetes, GraphQL                              │   │
│  │                                                      │   │
│  │ 💡 Helps achieve: "Become a Technical Lead"        │   │
│  │                                                      │   │
│  │ [View Details]  [Apply with Auto-Tailor]           │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Cloud Architect                             82% ⭐  │   │
│  │ CloudCo • Remote                                    │   │
│  │                                                      │   │
│  │ Match: 82% | 🎯 Goals: 1 | 📍 Remote | 🤖 Risk: 25%│   │
│  │                                                      │   │
│  │ ✅ AWS, Kubernetes, Docker, Terraform              │   │
│  │ ❌ GCP                                               │   │
│  │                                                      │   │
│  │ 💡 Helps achieve: "Master cloud architecture"      │   │
│  │                                                      │   │
│  │ [View Details]  [Apply with Auto-Tailor]           │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  Not finding what you're looking for?                       │
│  [🔍 Expand Search] to see 32 more jobs                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Filter Panel

```
┌──────────────────────────────────┐
│ 🎯 Filter Jobs                   │
├──────────────────────────────────┤
│                                  │
│ Skill Match Threshold            │
│ ▓▓▓▓▓▓░░░░ 40%                  │
│ Only show jobs with 40%+ match   │
│                                  │
│ Distance                         │
│ (○) Any distance                 │
│ (●) Within 50 km                 │
│                                  │
│ Goals Alignment                  │
│ [✓] Become Technical Lead        │
│ [✓] Master cloud architecture    │
│ [✓] Contribute to open source    │
│                                  │
│ AI Displacement Risk             │
│ (○) All jobs                     │
│ (●) Low risk only (< 40%)        │
│                                  │
│ [Apply Filters]  [Reset]         │
│                                  │
└──────────────────────────────────┘
```

### Job Detail Card

```
┌─────────────────────────────────────────────────────────────┐
│  Senior Software Engineer - Team Lead                       │
│  TechCorp Inc                                               │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  📍 San Francisco, CA (12 km from you)                      │
│  💼 Hybrid • 3 days in office                               │
│  💰 $140k - $180k                                           │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 🎯 Match Score: 87%                          🤖 35%  │  │
│  │                                                       │  │
│  │ Components:                                          │  │
│  │ • Skill Fit:        ████████████████████   92%       │  │
│  │ • Trajectory:       ████████████████████  100%       │  │
│  │ • Values:           ███████████████░░░░░   75%       │  │
│  │ • Logistics:        ███████████████████░   90%       │  │
│  │ • Growth Potential: ████████████████░░░░   80%       │  │
│  │                                                       │  │
│  │ AI Displacement Risk: 35% (Low-Medium)               │  │
│  │ This role has low automation risk due to             │  │
│  │ leadership and strategic components.                 │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ✅ Your Matching Skills:                                   │
│  Python • AWS • Docker • React • PostgreSQL                 │
│                                                              │
│  ❌ Skills to Learn:                                        │
│  Kubernetes • GraphQL                                       │
│                                                              │
│  💡 Helps You Achieve:                                      │
│  🎯 "Become a Technical Lead"                               │
│     Overlap: technical, lead, team, engineers               │
│                                                              │
│  📄 Description:                                            │
│  We're looking for a Senior Engineer to lead our backend    │
│  team of 5 developers...                                    │
│                                                              │
│  [🚀 Apply with Auto-Tailored Resume]                      │
│  [📋 Save for Later]                                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Example Use Cases

### Use Case 1: Local Job Search

**User Profile:**
- Location: Austin, TX (30.2672°N, 97.7431°W)
- Goals: "Transition to DevOps role"
- Skills: Python, Docker, AWS

**Query:**
```
GET /api/jobs/recommendations?
    min_skill_match=40&
    max_distance_km=50&
    limit=10
```

**Result:**
- Filters to jobs within 50 km of Austin
- Requires 40%+ skill match
- Shows jobs aligned with DevOps goal
- Each job shows distance (e.g., "15 km")
- Each job shows AI displacement risk

**Sample Output:**
1. "DevOps Engineer" at LocalCo - 18 km, 78% match, 🤖 40% risk
2. "Site Reliability Engineer" at TechHub - 23 km, 72% match, 🤖 35% risk
3. "Cloud Engineer" at StartupX - 45 km, 68% match, 🤖 30% risk

---

### Use Case 2: Remote Job Search

**User Profile:**
- Location: Rural Montana
- Goals: "Work remotely", "Master React"
- Skills: JavaScript, React, Node.js

**Query:**
```
GET /api/jobs/recommendations?
    min_skill_match=50&
    max_distance_km=null  (no distance filter for remote)
```

**Result:**
- Shows remote jobs only (via preferences: remote_only=true)
- Distance filter not applied (remote jobs always pass)
- 50%+ skill match required
- Prioritizes React-heavy roles

**Sample Output:**
1. "Senior Frontend Engineer (Remote)" - Remote, 85% match, 🤖 40% risk
2. "React Developer (Anywhere)" - Remote, 82% match, 🤖 45% risk

---

### Use Case 3: Career Pivot with Expanded Search

**User Profile:**
- Current: "Marketing Manager"
- Goal: "Transition to Product Management"
- Skills: Marketing, Analytics, some SQL

**Initial Query:**
```
GET /api/jobs/recommendations?
    min_skill_match=40&
    limit=20
```

**Result:** 3 jobs (very few matches)

**Expanded Query:**
```
GET /api/jobs/recommendations?
    min_skill_match=40&
    expand_search=true&
    limit=20
```

**Result:** 18 jobs
- Skill threshold lowered to 20% (40% - 20%)
- Shows adjacent roles: Associate PM, Product Analyst
- More opportunities for career transition

---

## 🧪 Testing

### Test Distance Calculation

```python
from app.services.job_matcher import JobMatcher

# San Francisco to Palo Alto
distance = JobMatcher.calculate_distance(
    37.7749, -122.4194,  # SF
    37.4419, -122.1430   # Palo Alto
)
print(f"Distance: {distance:.2f} km")  # ~35 km

# San Francisco to Los Angeles
distance = JobMatcher.calculate_distance(
    37.7749, -122.4194,  # SF
    34.0522, -118.2437   # LA
)
print(f"Distance: {distance:.2f} km")  # ~559 km
```

### Test Risk Estimation

```python
job1 = {
    'title': 'Data Entry Clerk',
    'description': 'Routine data entry tasks',
    'seniority': 'entry'
}
risk1 = await job_matcher._estimate_job_risk(job1)
print(f"Risk: {risk1}%")  # Expected: 80-85%

job2 = {
    'title': 'VP of Engineering',
    'description': 'Strategic leadership and team management',
    'seniority': 'director'
}
risk2 = await job_matcher._estimate_job_risk(job2)
print(f"Risk: {risk2}%")  # Expected: 5-15%
```

### Test Filtering

```python
from app.services.job_matcher import job_matcher

# Mock data
profile = {
    'profile_data': {
        'skills': ['Python', 'React', 'AWS']
    }
}

goals = [
    {
        'id': 'goal_1',
        'title': 'Become a Senior Engineer',
        'status': 'active'
    }
]

jobs = [
    {
        'id': 'job_1',
        'title': 'Senior Software Engineer',
        'description': 'Python backend development',
        'skills_extracted': ['Python', 'Django', 'AWS'],
        'location_type': 'remote'
    },
    {
        'id': 'job_2',
        'title': 'Data Entry Specialist',
        'description': 'Manual data entry',
        'skills_extracted': ['Excel', 'Typing'],
        'location_type': 'onsite',
        'latitude': 37.4419,
        'longitude': -122.1430
    }
]

# Apply filters
filtered = await job_matcher.filter_jobs_by_criteria(
    jobs=jobs,
    user_profile=profile,
    user_goals=goals,
    user_preferences=None,
    min_skill_match=40.0,
    max_distance_km=50.0,
    user_lat=37.7749,
    user_lon=-122.4194
)

print(f"Original: {len(jobs)} jobs")
print(f"Filtered: {len(filtered)} jobs")
# Expected: job_1 passes (high skill match, remote)
#           job_2 filtered (low skill match, high risk)
```

---

## 🚀 Performance Considerations

### Caching Strategy

**Cache Key:** `recommendations:{user_id}`
**TTL:** 1 hour
**Invalidation:** When user updates profile, goals, or preferences

**Bypass Cache When:**
- `refresh=true`
- Custom filters applied (`max_distance_km`, `min_skill_match ≠ 30`, `expand_search=true`)

### Database Optimization

**Indexes Required:**
```sql
CREATE INDEX idx_jobs_active ON jobs(status, is_spam);
CREATE INDEX idx_jobs_location ON jobs(latitude, longitude) WHERE location_type != 'remote';
CREATE INDEX idx_career_goals_user_active ON career_goals(user_id, status);
```

### Scaling

**Current:** Filter 200 jobs in ~2-5 seconds
**Target:** Handle 10,000+ jobs with sub-second response

**Future Optimizations:**
1. Pre-compute skill vectors (embeddings)
2. Use vector similarity search (pgvector)
3. Cache pre-filtered job pools by region
4. Async batch processing for large job sets

---

## 📈 Metrics to Track

### Filtering Effectiveness
- **Pass Rate:** % of jobs passing each filter
- **Avg Match Score:** Before vs after filtering
- **Filter Usage:** Which filters users apply most

### User Engagement
- **Expand Search Rate:** % of users clicking "Expand Search"
- **Application Rate:** % of recommended jobs applied to
- **Filter Adjustment:** How users tune skill/distance thresholds

### Goal Alignment
- **Goal Hit Rate:** % of jobs matching at least one goal
- **Multi-Goal Matches:** Jobs matching 2+ goals
- **Goal Achievement:** Do applied jobs correlate with goal completion?

### Risk Awareness
- **Risk Distribution:** % of jobs in each risk category
- **Risk Preference:** Do users apply to lower-risk jobs?
- **Risk Improvement:** Average displacement risk reduction

---

## ✅ Implementation Complete

**Files Modified:**
1. `backend/app/services/job_matcher.py`
   - Enhanced `_estimate_job_risk()` with comprehensive algorithm
   - Added `calculate_distance()` static method
   - Added `filter_jobs_by_criteria()` comprehensive filtering

2. `backend/app/api/jobs_marketplace.py`
   - Updated `/recommendations` endpoint with new parameters
   - Integrated goals fetching
   - Integrated location-based filtering
   - Added expand_search logic

**New Capabilities:**
- ✅ Filter by career goals alignment
- ✅ Filter by skill match threshold (customizable)
- ✅ Filter by distance from user location
- ✅ Display AI displacement risk % for each job
- ✅ Expand search option for more results
- ✅ Detailed filtering metadata in response

**API Enhancements:**
- 5 new query parameters
- Enhanced response with filtering stats
- Goal relevance scoring per job
- Distance calculation per job
- Risk estimation per job

---

## 🎓 User Education

### Dashboard Message

```
🎯 Smart Job Filtering

We've matched 15 jobs to your goals and skills:

• 3 jobs help you "Become a Technical Lead"
• 8 jobs are within 50 km of San Francisco
• All jobs have 40%+ skill match
• Average AI displacement risk: 38% (Medium)

Want more options? Click "Expand Search" to see 32 additional jobs.
```

### Tooltips

**Skill Match Threshold:**
"Higher values show only jobs you're highly qualified for. Lower values show more opportunities including stretch roles."

**Distance Filter:**
"Remote jobs are always included. Distance only applies to on-site and hybrid positions."

**AI Displacement Risk:**
"Estimated probability that this job could be automated by AI in the next 5-10 years. Based on routine tasks, human interaction, and strategic complexity."

**Expand Search:**
"Loosens filters to show more opportunities. Skill threshold decreases by 20%, distance doubles."

---

**Generated:** October 20, 2025
**Version:** 2.0
**Status:** ✅ Production Ready
