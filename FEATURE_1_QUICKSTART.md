# 🚀 Quick Start Guide - Feature 1: Skill Inference Engine

## Installation (5 minutes)

### 1. Backend Setup
```bash
cd backend

# Install new ML dependencies
pip install numpy pandas scikit-learn

# Verify installation
python -c "import numpy, pandas, sklearn; print('✅ Dependencies installed')"

# Start server
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup
```bash
cd frontend

# Install animation dependencies
npm install framer-motion react-vis d3
npm install -D @types/d3 @types/react-vis

# Start dev server
npm run dev
```

---

## Test the API (2 minutes)

```bash
# Test skill inference endpoint
curl -X POST http://localhost:8000/api/analyze/career \
  -H "Content-Type: application/json" \
  -d '{
    "job_title": "Software Engineer",
    "skills": ["Python", "JavaScript", "React"],
    "years_experience": 3,
    "location": "Remote"
  }' | jq '.skill_insights'
```

**Expected Output:**
- ✅ `skill_clusters`: 3-4 categories
- ✅ `transferable_skills`: 10 suggestions with confidence scores
- ✅ `hidden_skills`: 5-10 AI-detected skills
- ✅ `skill_gaps_for_growth`: 5-15 prioritized gaps
- ✅ `skill_strength_score`: Overall score 0-100

---

## Integrate into Your UI (5 minutes)

### Option 1: Add to Existing Analysis Page

```typescript
// In your analysis results component
import { SkillInsightsPanel } from '@/components/SkillInsights';

export default function AnalysisPage() {
  const { data } = useAnalysis(); // Your existing hook
  
  return (
    <div className="space-y-8">
      {/* Your existing components */}
      <RiskAnalysisCard data={data.risk} />
      <CompatibilityCard data={data.compatibility} />
      
      {/* NEW: Add Skill Insights */}
      {data.skill_insights && (
        <SkillInsightsPanel 
          skillInsights={data.skill_insights}
          jobTitle={data.job_title}
        />
      )}
      
      <TrainingRecommendations data={data.training} />
    </div>
  );
}
```

### Option 2: Standalone Skills Page

```typescript
// Create new route: /app/skills/page.tsx
import { SkillInsightsPanel } from '@/components/SkillInsights';

export default async function SkillsPage() {
  const analysisData = await fetchLatestAnalysis();
  
  return (
    <main className="container mx-auto py-8">
      <SkillInsightsPanel 
        skillInsights={analysisData.skill_insights}
        jobTitle={analysisData.job_title}
      />
    </main>
  );
}
```

---

## Component Usage Examples

### 1. Full Panel (Recommended)
```tsx
<SkillInsightsPanel 
  skillInsights={data.skill_insights}
  jobTitle="Data Scientist"
/>
```

### 2. Individual Components
```tsx
import { 
  SkillStrengthMeter,
  SkillClustersCard,
  TransferableSkillsCard,
  HiddenSkillsBadge,
  SkillGapsRoadmap
} from '@/components/SkillInsights';

// Use individually
<SkillStrengthMeter skillStrength={data.skill_strength_score} />
<TransferableSkillsCard transferableSkills={data.transferable_skills} />
```

---

## Configuration (Optional)

### Customize Skill Taxonomy

Edit `/backend/app/services/skill_inference.py`:

```python
# Add your domain-specific skills
self.skill_taxonomy['Domain Expertise'] = {
    'Your Industry': [
        'Custom Skill 1',
        'Custom Skill 2',
        # ...
    ]
}
```

### Customize Animations

Edit component files:

```typescript
// Adjust animation timings
const containerVariants = {
  visible: {
    transition: {
      staggerChildren: 0.2,  // Change from 0.1
      delayChildren: 0.5     // Change from 0.2
    }
  }
};
```

---

## Troubleshooting

### Backend Issues

**Error: "Module 'numpy' not found"**
```bash
pip install numpy pandas scikit-learn
```

**Error: "OpenAI API key not set"**
```bash
# Add to .env
OPENAI_API_KEY=your_key_here
```

**Slow response times (>5s)**
- Check OpenAI API rate limits
- Consider caching skill inference results

### Frontend Issues

**Error: "Cannot find module 'framer-motion'"**
```bash
npm install framer-motion
```

**TypeScript errors**
```bash
npm install -D @types/d3 @types/react-vis
```

**Components not rendering**
- Check browser console for errors
- Verify `skill_insights` exists in API response
- Check Tailwind CSS is configured

---

## Performance Tips

### Backend Optimization
```python
# Cache skill inference for 1 hour
from cachetools import TTLCache
cache = TTLCache(maxsize=100, ttl=3600)

@cached(cache)
async def infer_adjacent_skills(...):
    # ...
```

### Frontend Optimization
```typescript
// Lazy load heavy components
const SkillInsightsPanel = dynamic(
  () => import('@/components/SkillInsights/SkillInsightsPanel'),
  { loading: () => <LoadingSpinner /> }
);
```

---

## What's Next?

### Immediate Enhancements
1. ✅ **Feature 1 Complete** - Skill Inference Engine
2. ⏳ **Add Explainable AI** - "Why?" buttons on all suggestions
3. ⏳ **Multi-Year Roadmaps** - 3/5/10 year career paths

### Phase 2
- User feedback on skill suggestions
- ML-based skill relationship learning
- Integration with LinkedIn profiles
- Resume builder with hidden skills

---

## Need Help?

**Documentation:**
- Full technical spec: `FEATURE_1_SKILL_INFERENCE_COMPLETE.md`
- Implementation roadmap: `IMPLEMENTATION_WEEK_1.md`
- Quick reference: `QUICK_REFERENCE.md`

**Code Locations:**
- Backend: `/backend/app/services/skill_inference.py`
- Frontend: `/frontend/src/components/SkillInsights/`
- API: `/backend/app/api/analyze.py`

---

## Success Checklist

- [ ] Backend dependencies installed (numpy, pandas, scikit-learn)
- [ ] Frontend dependencies installed (framer-motion, react-vis, d3)
- [ ] API returns `skill_insights` field
- [ ] Components render without errors
- [ ] Animations are smooth (60fps)
- [ ] Mobile responsive (test on phone)
- [ ] Accessible (keyboard navigation works)

---

**🎉 You're ready to go! Open http://localhost:3000 and test Feature 1! 🎉**
