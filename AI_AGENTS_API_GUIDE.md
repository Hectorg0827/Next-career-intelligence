# AI Agents API - Quick Reference Guide

**Quick access to Phase 2 AI capabilities**

---

## 🚀 Quick Start

### Get Complete AI Intelligence (Dashboard)
```typescript
// One call to get everything
const response = await fetch('/api/ai/intelligence', {
  headers: { 'Authorization': `Bearer ${token}` }
});

const { intelligence } = await response.json();
console.log(intelligence);
// {
//   memory: { memory_count: 15, ai_ready: true },
//   recommendations: { count: 10, top_matches: [...] },
//   guidance: { count: 3, high_priority: [...] },
//   predictions: { churn_risk: "low", success_probability: 0.75 },
//   profile: { completeness: 0.65, level: "good" }
// }
```

---

## 📋 Common Use Cases

### 1. Show Job Recommendations
```typescript
// Get AI-powered job recommendations
const recs = await fetch('/api/jobs-marketplace/ai-recommendations?limit=10&include_stretch=true', {
  headers: { 'Authorization': `Bearer ${token}` }
});

const { recommendations } = await recs.json();

recommendations.forEach(rec => {
  console.log(`${rec.job.title} - Score: ${rec.ai_score}`);
  console.log(`Why: ${rec.match_reasons.join(', ')}`);
});
```

### 2. Display Proactive Guidance
```typescript
// Get guidance messages for dashboard
const guidance = await fetch('/api/ai/guidance', {
  headers: { 'Authorization': `Bearer ${token}` }
});

const { messages } = await guidance.json();

// Filter by priority
const critical = messages.filter(m => m.priority === 1);
const high = messages.filter(m => m.priority === 2);

// Show critical messages as alerts
critical.forEach(msg => {
  showAlert({
    type: 'error',
    title: msg.guidance_type,
    message: msg.content,
    actions: msg.action_items
  });
});
```

### 3. Profile Completeness Widget
```typescript
// Analyze profile
const analysis = await fetch('/api/ai/profile/analysis', {
  headers: { 'Authorization': `Bearer ${token}` }
});

const { analysis: profile } = await analysis.json();

// Show progress bar
<ProgressBar 
  value={profile.completeness_score * 100}
  label={`${Math.round(profile.completeness_score * 100)}% Complete`}
  level={profile.completeness_level}
/>

// Show top suggestions
<SuggestionsList>
  {profile.suggestions_count > 0 && (
    <Alert>
      You have {profile.suggestions_count} ways to improve your profile
    </Alert>
  )}
</SuggestionsList>
```

### 4. Quick Fill Profile Data
```typescript
// Infer missing data
const inferred = await fetch('/api/ai/profile/infer', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` }
});

const { inferred_data } = await inferred.json();

// Show quick fill modal
<QuickFillModal
  data={inferred_data}
  onApply={async (fields) => {
    await updateProfile(fields);
    toast.success('Profile updated with AI-inferred data');
  }}
/>
```

### 5. Generate Professional Summary
```typescript
// Generate AI summary
const summary = await fetch('/api/ai/profile/generate-summary', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` }
});

const { summary: text } = await summary.json();

// Show in profile editor
<SummaryField
  value={text}
  label="AI-Generated Summary"
  editable={true}
  onSave={saveSummary}
/>
```

### 6. Churn Risk Monitoring (Admin)
```typescript
// Get churn prediction
const churn = await fetch('/api/ai/predictions/churn', {
  headers: { 'Authorization': `Bearer ${token}` }
});

const { prediction } = await churn.json();

if (prediction.risk_level === 'high' || prediction.risk_level === 'critical') {
  // Send re-engagement campaign
  await sendRetentionEmail(userId, {
    risk_factors: prediction.risk_factors,
    recommended_actions: prediction.recommended_actions
  });
}
```

---

## 🎨 UI Component Examples

### Guidance Panel Component
```tsx
import { useEffect, useState } from 'react';

function GuidancePanel() {
  const [guidance, setGuidance] = useState([]);

  useEffect(() => {
    fetch('/api/ai/guidance', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(data => setGuidance(data.messages));
  }, []);

  const priorityColors = {
    1: 'bg-red-100 border-red-500',
    2: 'bg-yellow-100 border-yellow-500',
    3: 'bg-blue-100 border-blue-500',
    4: 'bg-gray-100 border-gray-500'
  };

  return (
    <div className="space-y-4">
      {guidance.map((msg, i) => (
        <div 
          key={i} 
          className={`p-4 border-l-4 rounded ${priorityColors[msg.priority]}`}
        >
          <h4 className="font-semibold">{msg.guidance_type}</h4>
          <p className="mt-2">{msg.content}</p>
          {msg.action_items.length > 0 && (
            <div className="mt-3 flex gap-2">
              {msg.action_items.map((action, j) => (
                <button 
                  key={j}
                  className="px-3 py-1 bg-blue-600 text-white rounded text-sm"
                >
                  {action}
                </button>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
```

### Profile Completeness Widget
```tsx
function ProfileCompletenessWidget() {
  const [analysis, setAnalysis] = useState(null);

  useEffect(() => {
    fetch('/api/ai/profile/analysis', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(data => setAnalysis(data.analysis));
  }, []);

  if (!analysis) return <div>Loading...</div>;

  const percentage = Math.round(analysis.completeness_score * 100);
  
  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h3 className="text-lg font-semibold mb-4">Profile Strength</h3>
      
      {/* Progress Bar */}
      <div className="mb-4">
        <div className="flex justify-between mb-1">
          <span className="text-sm font-medium">{percentage}%</span>
          <span className="text-sm text-gray-500">{analysis.completeness_level}</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-green-600 h-2 rounded-full"
            style={{ width: `${percentage}%` }}
          />
        </div>
      </div>

      {/* Strengths */}
      {analysis.strengths.length > 0 && (
        <div className="mb-4">
          <h4 className="text-sm font-semibold text-green-700 mb-2">✓ Strengths</h4>
          <ul className="text-sm text-gray-600 space-y-1">
            {analysis.strengths.map((s, i) => (
              <li key={i}>• {s}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Suggestions */}
      {analysis.suggestions_count > 0 && (
        <button className="w-full mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
          View {analysis.suggestions_count} Improvement Suggestions
        </button>
      )}
    </div>
  );
}
```

### AI Recommendations Feed
```tsx
function AIJobRecommendations() {
  const [recs, setRecs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/jobs-marketplace/ai-recommendations?limit=10', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(data => {
        setRecs(data.recommendations);
        setLoading(false);
      });
  }, []);

  return (
    <div>
      <div className="flex items-center gap-2 mb-4">
        <h2 className="text-2xl font-bold">AI Recommendations</h2>
        <span className="px-2 py-1 bg-purple-100 text-purple-700 text-xs rounded">
          Powered by AI
        </span>
      </div>

      {loading ? (
        <div>Loading recommendations...</div>
      ) : (
        <div className="space-y-4">
          {recs.map(rec => (
            <div key={rec.job.id} className="border rounded-lg p-4 hover:shadow-md">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-semibold text-lg">{rec.job.title}</h3>
                  <p className="text-gray-600">{rec.job.company}</p>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-green-600">
                    {Math.round(rec.ai_score)}%
                  </div>
                  <div className="text-xs text-gray-500">Match Score</div>
                </div>
              </div>

              {/* Match Reasons */}
              <div className="mt-3 flex flex-wrap gap-2">
                {rec.match_reasons.map((reason, i) => (
                  <span 
                    key={i}
                    className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded"
                  >
                    {reason}
                  </span>
                ))}
              </div>

              {/* Stretch Badge */}
              {rec.is_stretch && (
                <div className="mt-2">
                  <span className="px-2 py-1 bg-yellow-100 text-yellow-700 text-xs rounded">
                    🚀 Stretch Role - Growth Opportunity
                  </span>
                </div>
              )}

              {/* Growth Potential */}
              {rec.growth_potential && (
                <p className="mt-3 text-sm text-gray-700">
                  💡 {rec.growth_potential}
                </p>
              )}

              <button className="mt-4 w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
                View Details
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

---

## 🔧 Error Handling

All endpoints return consistent error responses:

```typescript
try {
  const response = await fetch('/api/ai/guidance', {
    headers: { 'Authorization': `Bearer ${token}` }
  });

  if (!response.ok) {
    const error = await response.json();
    // { detail: "Error message" }
    throw new Error(error.detail);
  }

  const data = await response.json();
  // { success: true, ... }
  
} catch (error) {
  console.error('AI request failed:', error);
  // Show user-friendly error message
  toast.error('Unable to fetch AI insights. Please try again.');
}
```

---

## 🎯 Best Practices

### 1. Cache AI Results
```typescript
// Cache for 5 minutes
const cacheKey = `ai-intelligence-${userId}`;
const cached = localStorage.getItem(cacheKey);

if (cached) {
  const { data, timestamp } = JSON.parse(cached);
  if (Date.now() - timestamp < 5 * 60 * 1000) {
    return data; // Use cached data
  }
}

// Fetch fresh data
const data = await fetchAIIntelligence();
localStorage.setItem(cacheKey, JSON.stringify({
  data,
  timestamp: Date.now()
}));
```

### 2. Show Loading States
```typescript
const [loading, setLoading] = useState(true);
const [data, setData] = useState(null);

useEffect(() => {
  setLoading(true);
  fetch('/api/ai/intelligence')
    .then(res => res.json())
    .then(data => {
      setData(data);
      setLoading(false);
    });
}, []);

return loading ? <Skeleton /> : <Dashboard data={data} />;
```

### 3. Handle Partial Failures
```typescript
// Some AI features may fail, but show what works
const intelligence = await fetchIntelligence();

return (
  <Dashboard>
    {intelligence.guidance && <GuidancePanel data={intelligence.guidance} />}
    {intelligence.recommendations && <RecsWidget data={intelligence.recommendations} />}
    {intelligence.profile && <ProfileWidget data={intelligence.profile} />}
    {/* Gracefully skip missing sections */}
  </Dashboard>
);
```

---

## 📊 Response Schemas

### GET /api/ai/intelligence
```json
{
  "success": true,
  "intelligence": {
    "memory": {
      "memory_count": 15,
      "ai_ready": true
    },
    "recommendations": {
      "count": 10,
      "top_matches": [
        { "job_id": "uuid", "score": 95.5 }
      ]
    },
    "guidance": {
      "count": 3,
      "high_priority": [
        "Complete your profile to get 3x more matches"
      ]
    },
    "predictions": {
      "churn_risk": "low",
      "churn_probability": 0.15,
      "success_probability": 0.75
    },
    "profile": {
      "completeness": 0.65,
      "level": "good",
      "suggestions_count": 5
    }
  }
}
```

### GET /api/ai/guidance
```json
{
  "success": true,
  "count": 3,
  "messages": [
    {
      "guidance_type": "profile_completion",
      "priority": 1,
      "content": "Your profile is only 45% complete...",
      "action_items": [
        "Add 5 more skills",
        "Complete work experience"
      ],
      "impact_description": "Increases matches by 3x"
    }
  ]
}
```

### GET /api/ai/profile/analysis
```json
{
  "success": true,
  "analysis": {
    "completeness_level": "good",
    "completeness_score": 0.65,
    "missing_fields": ["summary", "education"],
    "incomplete_fields": ["skills"],
    "suggestions_count": 5,
    "inferred_skills": ["Python", "SQL", "Data Analysis"],
    "strengths": ["10 skills listed", "3 positions with descriptions"],
    "weaknesses": ["Summary needs expansion"]
  }
}
```

---

## 🚀 Ready to Use!

All endpoints are:
- ✅ Authenticated (requires Bearer token)
- ✅ Documented in Swagger UI (`/docs`)
- ✅ Error-handled with fallbacks
- ✅ Type-safe with Pydantic models
- ✅ Production-ready

**API Base URL:** `https://your-domain.com/api`  
**Swagger Docs:** `https://your-domain.com/docs`
