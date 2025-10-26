# Enhanced Intelligence API Documentation

## Overview

The Enhanced Intelligence API provides advanced predictive analytics, market intelligence, and career benchmarking capabilities through a suite of specialized AI agents.

## Base URL

```
/api/intelligence
```

## Authentication

All endpoints require authentication via Bearer token:

```
Authorization: Bearer <firebase_jwt_token>
```

---

## Endpoints

### 1. Career Forecast

Get AI-powered career trajectory predictions over 3-5 year horizon.

**Endpoint:** `GET /api/intelligence/career-forecast`

**Query Parameters:**
- `time_horizon` (optional, default: 3): Number of years to forecast (1-5)

**Response:**
```json
{
  "success": true,
  "forecast": {
    "predicted_roles": [
      {
        "title": "Senior Software Engineer",
        "year": 1,
        "probability": 75,
        "salary_range": "$130,000 - $160,000",
        "requirements": ["Advanced Python", "System Design", "Leadership"]
      }
    ],
    "skill_evolution": {
      "year_1": ["Cloud Architecture", "Kubernetes"],
      "year_2": ["Team Leadership", "Strategic Planning"],
      "year_3": ["Executive Communication"]
    },
    "key_milestones": [
      "Lead major project",
      "Mentor junior developers",
      "Contribute to open source"
    ],
    "alternative_paths": [
      "Technical Lead",
      "Engineering Manager"
    ]
  },
  "generated_for": "Software Engineer"
}
```

---

### 2. Market Snapshot

Get real-time market intelligence for a specific role.

**Endpoint:** `GET /api/intelligence/market-snapshot/{role}`

**Path Parameters:**
- `role` (required): Job title to analyze (URL encoded)

**Query Parameters:**
- `location` (optional): Geographic location for localized data

**Response:**
```json
{
  "success": true,
  "snapshot": {
    "demand_level": "high",
    "salary_trend": "increasing (5-8% growth)",
    "competition_level": "moderate",
    "hot_skills": ["Python", "AWS", "React", "Docker", "Kubernetes"],
    "market_insights": [
      "Strong demand for cloud expertise",
      "Remote positions increasing"
    ],
    "timestamp": "2025-10-26T10:30:00Z",
    "confidence_score": 0.85
  },
  "role": "Software Engineer"
}
```

---

### 3. Salary Trends

Analyze salary trends and compensation data for a role.

**Endpoint:** `GET /api/intelligence/salary-trends/{role}`

**Path Parameters:**
- `role` (required): Job title to analyze

**Query Parameters:**
- `location` (optional): Geographic location
- `years_experience` (optional): Years of experience level

**Response:**
```json
{
  "success": true,
  "salary_data": {
    "current_range": {
      "min": 80000,
      "max": 150000,
      "median": 115000
    },
    "trend_direction": "increasing (5% annually)",
    "percentile_breakdown": {
      "25th": 95000,
      "50th": 115000,
      "75th": 135000,
      "90th": 150000
    },
    "factors_affecting": [
      "Experience level",
      "Location and cost of living",
      "Company size and funding"
    ]
  },
  "role": "Software Engineer"
}
```

---

### 4. Risk Scan

Comprehensive career risk assessment and threat detection.

**Endpoint:** `GET /api/intelligence/risk-scan`

**Response:**
```json
{
  "success": true,
  "risk_report": {
    "overall_risk_score": 45,
    "risk_level": "medium",
    "threat_count": 3,
    "threats_by_severity": {
      "critical": 0,
      "high": 1,
      "medium": 2,
      "low": 0
    },
    "threats": [
      {
        "type": "skill_obsolescence",
        "severity": "high",
        "title": "Skill Risk: jQuery",
        "description": "This skill may be declining in relevance",
        "impact": "Replacement: Modern frameworks (React, Vue)",
        "recommendations": [
          "Learn React or Vue.js",
          "Start transition within 6-12 months"
        ],
        "urgency": "high",
        "detected_at": "2025-10-26T10:30:00Z"
      }
    ],
    "top_priority_actions": [
      "Learn modern JavaScript frameworks",
      "Build cloud expertise",
      "Develop leadership skills"
    ],
    "generated_at": "2025-10-26T10:30:00Z"
  }
}
```

---

### 5. Analyze Job Offer

Comprehensive job offer analysis with negotiation intelligence.

**Endpoint:** `POST /api/intelligence/analyze-offer`

**Request Body:**
```json
{
  "job_title": "Senior Software Engineer",
  "job_location": "San Francisco, CA",
  "offer_details": {
    "base_salary": 150000,
    "bonus": 20000,
    "equity": {
      "type": "rsu",
      "value": 100000,
      "vesting_years": 4
    },
    "benefits": ["health_insurance", "401k_match"],
    "pto_days": 25,
    "remote_policy": "hybrid"
  }
}
```

**Response:**
```json
{
  "success": true,
  "analysis": {
    "offer_summary": {
      "base_salary": 150000,
      "total_comp_year_1": 195000,
      "total_comp_4_year": 780000,
      "components_breakdown": {
        "base_salary": 150000,
        "annual_bonus": 20000,
        "equity_annual": 25000,
        "equity_total": 100000
      }
    },
    "market_comparison": {
      "market_median": 160000,
      "percentile": 60,
      "vs_market": 35000
    },
    "negotiation_strategy": {
      "leverage": "medium",
      "key_points": [
        "Market rate alignment",
        "Skill level match",
        "Experience value"
      ],
      "tradeoffs": ["Equity", "Bonus structure", "PTO"],
      "red_flags": []
    },
    "recommendation": "Fair offer - at market rate. Room for negotiation to reach 75th percentile."
  }
}
```

---

### 6. Peer Benchmark

Compare career progress against industry peers.

**Endpoint:** `GET /api/intelligence/peer-benchmark`

**Response:**
```json
{
  "success": true,
  "benchmark": {
    "peer_cohort": {
      "role": "Software Engineer",
      "seniority": "mid",
      "industry": "Technology",
      "location": "United States",
      "years_experience": "3-5"
    },
    "overall_percentile": 65,
    "overall_rating": "above_average",
    "salary_comparison": {
      "user_salary": 120000,
      "peer_median": 115000,
      "percentile": 60,
      "vs_median": 5000,
      "assessment": "Market rate - competitive compensation"
    },
    "skills_comparison": {
      "skill_count": 15,
      "peer_median_count": 12,
      "percentile": 70,
      "assessment": "Competitive skill set - on par with peers"
    },
    "strengths": [
      "Compensation above peer average",
      "Strong skill set breadth"
    ],
    "improvement_areas": [
      "Consider expanding into emerging technologies"
    ],
    "generated_at": "2025-10-26T10:30:00Z"
  }
}
```

---

### 7. Emerging Skills

Identify rapidly growing skills in an industry.

**Endpoint:** `GET /api/intelligence/emerging-skills/{industry}`

**Path Parameters:**
- `industry` (required): Industry to analyze

**Query Parameters:**
- `lookback_months` (optional, default: 6): Analysis window in months

**Response:**
```json
{
  "success": true,
  "industry": "Technology",
  "emerging_skills": [
    {
      "skill_name": "Large Language Models",
      "growth_rate": 85.0,
      "adoption_stage": "growing",
      "related_roles": ["ML Engineer", "AI Researcher", "Data Scientist"]
    },
    {
      "skill_name": "Kubernetes",
      "growth_rate": 45.0,
      "adoption_stage": "mainstream",
      "related_roles": ["DevOps Engineer", "Platform Engineer"]
    }
  ]
}
```

---

### 8. Market Disruptions

Detect major disruptions affecting an industry.

**Endpoint:** `GET /api/intelligence/market-disruptions/{industry}`

**Path Parameters:**
- `industry` (required): Industry to analyze

**Response:**
```json
{
  "success": true,
  "industry": "Technology",
  "disruptions": [
    {
      "type": "ai_automation",
      "title": "AI and Automation Acceleration",
      "impact_level": "high",
      "description": "Rapid AI adoption is changing skill requirements",
      "affected_roles": ["Data Entry", "Customer Service", "Content Writing"],
      "recommendations": [
        "Develop AI literacy",
        "Focus on uniquely human capabilities"
      ],
      "urgency": "ongoing"
    }
  ]
}
```

---

### 9. Progression Timing

Analyze optimal timing for career advancement.

**Endpoint:** `GET /api/intelligence/progression-timing/{target_role}`

**Path Parameters:**
- `target_role` (required): Desired role to progress to

**Response:**
```json
{
  "success": true,
  "target_role": "Senior Software Engineer",
  "timing_analysis": {
    "readiness_score": 65,
    "timeline_months": 9,
    "critical_gaps": [
      "Leadership experience",
      "System design expertise"
    ],
    "quick_wins": [
      "Lead a team project",
      "Get AWS certification"
    ]
  }
}
```

---

## Error Responses

All endpoints return standard error responses:

**404 Not Found:**
```json
{
  "detail": "User profile not found"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Failed to generate career forecast"
}
```

---

## Rate Limiting

- Free tier: 20 requests per day
- Pro tier: 300 requests per hour (sufficient for active job searches)
- Elite tier: 1000 requests per hour
- Enterprise: Unlimited

**Note:** Rate limits are per user, not per endpoint. Bulk operations count as single requests.

---

## Agent Architecture

The Enhanced Intelligence system uses 10 specialized AI agents:

### Core Agents (Existing)
1. **Profile Agent** - User identity and memory
2. **Risk Agent** - AI displacement assessment
3. **Match Agent** - Job compatibility scoring
4. **Gap Agent** - Skill gap analysis
5. **Sentiment Agent** - Motivation detection

### Enhanced Agents (New)
6. **Trajectory Agent** - Career path forecasting
7. **Market Intel Agent** - Real-time market data
8. **Early Warning Agent** - Threat detection
9. **Negotiation Agent** - Offer analysis
10. **Peer Benchmarking Agent** - Comparative analytics

---

## Best Practices

1. **Caching**: 
   - Market data: Cached for 6 hours (invalidated on major market events)
   - Career forecasts: Cached for 1 week (invalidated on profile changes)
   - Risk scans: Cached for 24 hours (invalidated on new threat detection)
   - Salary data: Cached for 24 hours
   
   **Cache Invalidation Triggers:**
   - User profile updates (skills, experience, goals)
   - Major market disruptions in user's industry
   - Significant role/location changes
   - Manual refresh requests (Pro/Elite)

2. **Polling**: Don't poll frequently - data updates occur:
   - Market data: Every 6 hours
   - Risk scans: Daily at midnight UTC
   - Forecasts: Weekly on Sundays
   
3. **Error Handling**: Always check `success` field in responses
4. **Profile Completeness**: More complete profiles yield better predictions (aim for 80%+ completeness)

---

## Support

For API support, contact: api-support@nextcareer.ai
